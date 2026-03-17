import time
import psutil
from datetime import datetime, timedelta
import asyncio
from asyncio import sleep
import aiohttp
from urllib.parse import quote

from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message

from pytgcalls import PyTgCalls, StreamType
from pytgcalls.types.input_stream import AudioPiped
from pytgcalls.types.input_stream.quality import HighQualityAudio

# ───────────── CONFIG ─────────────
API_ID = 33603336
API_HASH = "c9683a8ec3b886c18219f650fc8ed429"
BOT_TOKEN = "8411080834:AAGG87Dh82Lc5UFyhJJJYgj3UU-OIUw4iJY"
SESSION_STRING = "BQE-4i0ASxu8TXk4s870tFMn-D2Ijs-7DaTep8qcmRnZuowGYTiKDzzy9fKRT3pCc7aFI9oql0Rp5k1FkymDhRbewYPN11p5G7exMCs-z2bdMPuRoJCF60r7p_xq0TBjtLw5P1f-pXHHRxeXSAq0nKyNglv2pZ-GVCbYL4J-OwIkfck4wZyfiU0H58LZla5Il4VmVww-ewK3roa4mVjIxGKYoFva7LqYEf9Iti77jLz7HW7gCfuNessLDXqH1se4DuOSmoJzbacJxofENDQJChGjP4K7gbkMQQKwjCQfndvTmHLyDnc5jDqwfngZK1ogepmyiXZhhzHVebIieznK4DXTM1Q7pAAAAAHKarFXAA"

bot = Client("musicbot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
assistant = Client("assistant", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

call = PyTgCalls(assistant)

BOT_START_TIME = datetime.now()
# Simple queue: {chat_id: [{"title": "...", "url": "...", "duration": int}, ...]}
queues = {}  # type: dict[int, list[dict]]

# ───────────── HELPERS ─────────────
def fmt_time(seconds: int) -> str:
    if seconds < 0:
        return "Live"
    m, s = divmod(seconds, 60)
    return f"{m}:{s:02d}"

# ───────────── COMMANDS ─────────────

@bot.on_message(filters.command("start"))
async def start_cmd(_, msg: Message):
    txt = (
        "<b>👋 Hello there!</b>\n\n"
        "I'm a simple <b>Voice Chat Music Player</b>\n"
        "I can play songs in group voice chats.\n\n"
        "<b>Commands:</b>\n"
        "• /play <song name or youtube link>\n"
        "• /rfplay (reply to audio)\n"
        "• /stop  —  stop & leave VC\n"
        "• /skip  —  skip current song\n"
        "• /queue — show current queue\n"
        "• /ping\n\n"
        "Have fun 🎶"
    )
    await msg.reply_text(txt, disable_web_page_preview=True)


@bot.on_message(filters.command("ping"))
async def ping_cmd(_, msg: Message):
    start = time.time()
    sent = await msg.reply_text("Pinging...")
    end = time.time()

    uptime = str(timedelta(seconds=int((datetime.now() - BOT_START_TIME).total_seconds()))).split(".")[0]
    cpu = psutil.cpu_percent()

    try:
        vc = "Active" if await call.get_call(msg.chat.id) else "Not active"
    except:
        vc = "Unknown"

    text = f"""<b>🏓 Pong!</b>
• Latency: <code>{round((end - start) * 1000, 2)} ms</code>
• Uptime : <code>{uptime}</code>
• CPU    : <code>{cpu}%</code>
• VC     : {vc}"""

    await sent.edit_text(text)


@bot.on_message(filters.command("play"))
# etc.
async def play_cmd(_, msg: Message):
    if len(msg.command) < 2:
        return await msg.reply("Give a song name.\nEx: <code>/play mann mera</code>")

    query = msg.text.split(None, 1)[1].strip()
    m = await msg.reply("🔎 Searching...")

    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://jio-saa-van.vercel.app/result/?query={quote(query)}"
            async with session.get(url, timeout=12) as r:
                if r.status != 200:
                    return await m.edit("API returned bad status.")
                data = await r.json()
    except Exception as ex:
        return await m.edit(f"API error: {ex.__class__.__name__}")

    if not data or not isinstance(data, list) or len(data) == 0:
        return await m.edit("No results found.")

    track = data[0]
    url = track.get("media_url")
    if not url:
        return await m.edit("No stream URL found in result.")

    title = track.get("song", "Unknown")
    artist = track.get("primary_artists") or track.get("singers", "Unknown")
    dur = int(track.get("duration", 0))

    chat_id = msg.chat.id

    # Add to queue
    song = {"title": title, "url": url, "duration": dur, "by": msg.from_user.first_name}
    queues.setdefault(chat_id, []).append(song)

    if len(queues[chat_id]) > 1:
        # Already playing → just added to queue
        pos = len(queues[chat_id])
        await m.edit(
            f"🎶 <b>Queued at position #{pos}</b>\n"
            f"• {title}\n"
            f"• {artist}  •  {fmt_time(dur)}"
        )
        return

    # First song → play now
    await play_next(chat_id, m)


async def play_next(chat_id: int, msg: Message | None = None):
    if chat_id not in queues or not queues[chat_id]:
        if msg:
            await msg.edit("Queue empty.")
        return

    song = queues[chat_id][0]
    url = song["url"]
    title = song["title"]
    dur = song["duration"]

    try:
        # Try to change if already playing
        await call.change_stream(chat_id, AudioPiped(url, HighQualityAudio()))
    except Exception:
        try:
            await call.join_group_call(
                chat_id,
                AudioPiped(url, HighQualityAudio()),
                stream_type=StreamType().pulse_stream
            )
        except Exception as e:
            if msg:
                await msg.edit(f"Failed to join/play: {e}")
            return

    text = (
        f"🎵 <b>Now Playing:</b>\n"
        f"• {title}\n"
        f"• Duration: {fmt_time(dur)}\n"
        f"• Requested by: {song['by']}"
    )

    if msg:
        await msg.edit(text)
    else:
        await bot.send_message(chat_id, text)


@bot.on_message(filters.command("skip"))
async def skip_cmd(_, msg: Message):
    chat_id = msg.chat.id
    if chat_id not in queues or not queues[chat_id]:
        return await msg.reply("Nothing is playing.")

    queues[chat_id].pop(0)  # remove current
    await msg.reply("⏭ Skipped.")

    # Play next if any
    if queues[chat_id]:
        await play_next(chat_id)
    else:
        try:
            await call.leave_group_call(chat_id)
            await msg.reply("Queue finished → left VC.")
        except:
            pass


@bot.on_message(filters.command("queue"))
async def queue_cmd(_, msg: Message):
    chat_id = msg.chat.id
    if chat_id not in queues or not queues[chat_id]:
        return await msg.reply("Queue is empty.")

    txt = "<b>Current Queue:</b>\n"
    for i, s in enumerate(queues[chat_id], 1):
        txt += f"{i}. {s['title']} • {fmt_time(s['duration'])}\n"
    await msg.reply(txt)


@bot.on_message(filters.command("stop"))
async def stop_cmd(_, msg: Message):
    try:
        await call.leave_group_call(msg.chat.id)
        if msg.chat.id in queues:
            del queues[msg.chat.id]
        await msg.reply("⏹ Stopped and left voice chat.")
    except Exception as e:
        await msg.reply(f"Error: {e}")


# Your rfplay (reply audio) — kept almost same, just cleaned
@bot.on_message(filters.command("rfplay"))
async def rfplay_cmd(_, msg: Message):
    if not msg.reply_to_message or not (msg.reply_to_message.audio or msg.reply_to_message.voice):
        return await msg.reply("Reply to an audio/voice message.")

    file_path = await msg.reply_to_message.download()
    chat_id = msg.chat.id

    try:
        await call.change_stream(chat_id, AudioPiped(file_path, HighQualityAudio()))
    except:
        await call.join_group_call(chat_id, AudioPiped(file_path, HighQualityAudio()))

    await msg.reply("Playing replied audio file locally.")


# ───────────── START ─────────────
async def main():
    await assistant.start()
    await bot.start()
    await call.start()
    print("Voice Chat Music Bot Started")
    await asyncio.Event().wait()  # keep running


if __name__ == "__main__":
    asyncio.run(main())
