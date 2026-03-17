import time
import psutil
from datetime import datetime, timedelta
import asyncio
import aiohttp
from urllib.parse import quote

from pyrogram import Client, filters, idle
from pyrogram.enums import ParseMode
from pyrogram.types import Message
from pyrogram.errors import PeerIdInvalid, ChannelInvalid

from pytgcalls import PyTgCalls, StreamType
from pytgcalls.types.input_stream import AudioPiped
from pytgcalls.types.input_stream.quality import HighQualityAudio

# ───────────── CONFIG ─────────────
API_ID = 33603336
API_HASH = "c9683a8ec3b886c18219f650fc8ed429"
BOT_TOKEN = "8411080834:AAE85QH-LpaiOpht-RSMpwYQPus1jHONnu4"
SESSION_STRING = "BQE-4i0ASxu8TXk4s870tFMn-D2Ijs-7DaTep8qcmRnZuowGYTiKDzzy9fKRT3pCc7aFI9oql0Rp5k1FkymDhRbewYPN11p5G7exMCs-z2bdMPuRoJCF60r7p_xq0TBjtLw5P1f-pXHHRxeXSAq0nKyNglv2pZ-GVCbYL4J-OwIkfck4wZyfiU0H58LZla5Il4VmVww-ewK3roa4mVjIxGKYoFva7LqYEf9Iti77jLz7HW7gCfuNessLDXqH1se4DuOSmoJzbacJxofENDQJChGjP4K7gbkMQQKwjCQfndvTmHLyDnc5jDqwfngZK1ogepmyiXZhhzHVebIieznK4DXTM1Q7pAAAAAHKarFXAA"

bot = Client("musicbot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
assistant = Client("assistant", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)
call = PyTgCalls(assistant)

BOT_START_TIME = datetime.now()
queues = {}

def fmt_time(seconds: int) -> str:
    if seconds <= 0: return "00:00"
    m, s = divmod(seconds, 60)
    return f"{m}:{s:02d}"

@bot.on_message(filters.command("start"))
async def start_cmd(_, msg: Message):
    await msg.reply_text("<b>🎶 Music Bot is Alive!</b>\nUse /play [song name] to start.")

@bot.on_message(filters.command("play"))
async def play_cmd(_, msg: Message):
    if len(msg.command) < 2:
        return await msg.reply("Usage: /play [song name]")

    chat_id = msg.chat.id
    query = msg.text.split(None, 1)[1]
    m = await msg.reply("🔎 Searching...")

    # Assistant Check
    try:
        await assistant.get_chat(chat_id)
    except Exception:
        return await m.edit("❌ **Assistant is not in this group!**\nPlease add the Assistant account to this group first.")

    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://jio-saa-van.vercel.app/result/?query={quote(query)}"
            async with session.get(url, timeout=10) as r:
                data = await r.json()
                if not data or not isinstance(data, list):
                    return await m.edit("No results found.")
                track = data[0]
    except Exception as e:
        return await m.edit(f"API Error: {e}")

    stream_url = track.get("media_url") or track.get("download_url")
    if not stream_url:
        return await m.edit("Could not find a playable link.")

    song_data = {
        "title": track.get("song", "Unknown"),
        "url": stream_url,
        "duration": int(track.get("duration", 0)),
        "by": msg.from_user.first_name
    }

    queues.setdefault(chat_id, []).append(song_data)

    if len(queues[chat_id]) > 1:
        return await m.edit(f"✅ Queued at #{len(queues[chat_id])}: {song_data['title']}")

    await play_next(chat_id, m)

async def play_next(chat_id: int, msg: Message = None):
    if chat_id not in queues or not queues[chat_id]:
        return
    
    song = queues[chat_id][0]
    try:
        # Pehle join karne ki koshish karein
        try:
            await call.join_group_call(
                chat_id,
                AudioPiped(song["url"], HighQualityAudio()),
                stream_type=StreamType().pulse_stream
            )
        except Exception:
            # Agar pehle se join hai, toh sirf stream change karein
            await call.change_stream(
                chat_id,
                AudioPiped(song["url"], HighQualityAudio())
            )
            
        text = f"🎵 **Now Playing:** {song['title']}\n👤 **Requested by:** {song['by']}"
        if msg: 
            await msg.edit(text)
        else: 
            await bot.send_message(chat_id, text)
            
    except Exception as e:
        print(f"Error details: {e}") # Terminal mein check karein
        if msg: 
            await msg.edit(f"❌ **Assistant join nahi kar pa raha!**\nError: `{e}`")
        else:
            await bot.send_message(chat_id, f"Error: {e}")


@bot.on_message(filters.command("stop"))
async def stop_cmd(_, msg: Message):
    try:
        await call.leave_group_call(msg.chat.id)
        queues.pop(msg.chat.id, None)
        await msg.reply("⏹ Stopped and cleared queue.")
    except Exception as e:
        await msg.reply(f"Error: {e}")

async def main():
    print("Starting clients...")
    await bot.start()
    await assistant.start()
    await call.start()
    print("--- BOT STARTED SUCCESSFULLY ---")
    await idle()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
