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


@bot.on_message(filters.command("ping"))
async def ping_cmd(_, msg: Message):
    try:
        await message.delete()
    except:
        pass
    # 1. Sabse pehle loading message
    start_time = time.time()
    m = await msg.reply_text("📡 <code>Pinging...</code>")
    
    # Calculation start
    end_time = time.time()
    latency = round((end_time - start_time) * 1000, 2)
    
    # Uptime logic
    uptime_sec = (datetime.now() - BOT_START_TIME).total_seconds()
    uptime = str(timedelta(seconds=int(uptime_sec)))
    
    # System Stats
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent

    # 2. Thoda 'delay' feel dene ke liye (Optional, professional lagta hai)
    await asyncio.sleep(0.5)

    # 3. Final message edit
    text = (
        "<b>🏓 Pong!</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"🚀 <b>Latency:</b> <code>{latency} ms</code>\n"
        f"🆙 <b>Uptime:</b> <code>{uptime}</code>\n"
        f"💻 <b>CPU:</b> <code>{cpu}%</code>\n"
        f"📊 <b>RAM:</b> <code>{ram}%</code>\n"
        f"💾 <b>Disk:</b> <code>{disk}%</code>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "👤 <b>By:</b> <a href='https://t.me/sxyaru'>sxyaru</a>"
    )

    await m.edit_text(text, disable_web_page_preview=True)


# ───────────── START COMMAND ─────────────

@bot.on_message(filters.command("start"))
async def start_cmd(_, msg: Message):
    try:
        await msg.delete() 
    except:
        pass
        
    START_IMG = "https://files.catbox.moe/uyum1c.jpg" 
    
    text = (
        "<b>╔══════════════════╗</b>\n"
        "<b>   🎵 ᴍᴜsɪᴄ ᴘʟᴀʏᴇʀ ʙᴏᴛ 🎵   </b>\n"
        "<b>╚══════════════════╝</b>\n\n"
        "<b>👋 ʜᴇʟʟᴏ! ɪ ᴀᴍ ᴀ ғᴀsᴛ & ᴘᴏᴡᴇʀғᴜʟ</b>\n"
        "<b>ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ᴍᴜsɪᴄ ᴘʟᴀʏᴇʀ ʙᴏᴛ.</b>\n\n"
        "✨ <b>ᴍᴀᴅᴇ ᴡɪᴛʜ ❤️ ʙʏ:</b> <a href='https://t.me/sxyaru'>sxyaru</a>"
    )

    # Buttons ko compact karne ke liye ek hi row mein zyada buttons daale hain
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("❓ ʜᴇʟᴘ", callback_data="help_menu"),
            InlineKeyboardButton("📂 ʀᴇᴘᴏ", callback_data="repo_menu")
        ],
        [
            InlineKeyboardButton("👤 ᴏᴡɴᴇʀ", url="https://t.me/sxyaru"),
            InlineKeyboardButton("📢 sᴜᴘᴘᴏʀᴛ", url="https://t.me/your_channel")
        ],
        [
            InlineKeyboardButton("➕ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ", url=f"https://t.me/{bot.me.username}?startgroup=true")
        ]
    ])

    await bot.send_photo(
        msg.chat.id,
        photo=START_IMG,
        caption=text,
        reply_markup=buttons
    )
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

@bot.on_message(filters.command("play"))
async def play_cmd(_, msg: Message):
    try:
        await message.delete()
    except:
        pass
    if len(msg.command) < 2:
        return await msg.reply("❌ Give a song name.\nEx: <code>/play mann mera</code>")

    query = msg.text.split(None, 1)[1].strip()
    m = await msg.reply("🔎 <b>Searching...</b>")

    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://jio-saa-van.vercel.app/result/?query={quote(query)}"
            async with session.get(url, timeout=12) as r:
                data = await r.json()
    except Exception as ex:
        return await m.edit(f"❌ API error: {ex.__class__.__name__}")

    if not data or not isinstance(data, list) or len(data) == 0:
        return await m.edit("❌ No results found.")

    track = data[0]
    stream_url = track.get("media_url") or track.get("download_url")
    if not stream_url:
        return await m.edit("❌ No stream URL found.")

    # Details Extraction
    title = track.get("song", "Unknown")
    artist = track.get("primary_artists") or track.get("singers", "Unknown")
    duration = int(track.get("duration", 0))
    thumb = track.get("image") or "https://telegra.ph/file/default_music.jpg" # Default image agar na mile
    chat_id = msg.chat.id
    requester = msg.from_user.first_name

    # Queue Logic
    song_data = {
        "title": title, 
        "url": stream_url, 
        "duration": duration, 
        "by": requester,
        "thumb": thumb
    }
    queues.setdefault(chat_id, []).append(song_data)

    # Buttons Setup
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⏸ Pause", callback_data="pause_cb"),
            InlineKeyboardButton("▶️ Resume", callback_data="resume_cb"),
            InlineKeyboardButton("⏭ Skip", callback_data="skip_cb")
        ],
        [
            InlineKeyboardButton("📢 Channel", url="https://t.me/your_channel"), # Apna channel link dalein
            InlineKeyboardButton("👤 Owner", url="https://t.me/sxyaru")
        ]
    ])

    text = (
        f"🎵 <b>Now Playing</b>\n\n"
        f"📝 <b>Song:</b> <code>{title}</code>\n"
        f"👤 <b>Artist:</b> <code>{artist}</code>\n"
        f"⏳ <b>Duration:</b> <code>{fmt_time(duration)}</code>\n"
        f"🎧 <b>Requested by:</b> {requester}\n\n"
        f"<b>API By:</b> <a href='https://t.me/sxyaru'>sxyaru</a>"
    )

    if len(queues[chat_id]) > 1:
        # Agar queue mein add hua hai toh photo ke saath reply karega
        await m.delete()
        return await bot.send_photo(
            chat_id, 
            photo=thumb, 
            caption=f"✅ <b>Queued at #{len(queues[chat_id])}</b>\n\n{text}",
            reply_markup=buttons
        )

    # Play Next & Edit Message
    await m.delete() # 'Searching' message delete karke photo bhejega
    await bot.send_photo(
        chat_id, 
        photo=thumb, 
        caption=text,
        reply_markup=buttons
    )
    
    await play_next(chat_id)


async def play_next(chat_id: int):
    if chat_id not in queues or not queues[chat_id]:
        return
    
    song = queues[chat_id][0]
    url = song["url"]

    try:
        # Check if Assistant is already in call
        try:
            await call.join_group_call(
                chat_id,
                AudioPiped(url, HighQualityAudio()),
                stream_type=StreamType().pulse_stream
            )
        except Exception:
            # If already joined, just change the stream
            await call.change_stream(
                chat_id,
                AudioPiped(url, HighQualityAudio())
            )
            
    except Exception as e:
        print(f"Assistant Join Error: {e}")
        # Agar error aaye toh queue se hata do taki bot stuck na ho
        if chat_id in queues:
            queues[chat_id].pop(0)
        await bot.send_message(chat_id, f"❌ **Assistant join nahi kar pa raha!**\n`{e}`")




# ───────────── CALLBACK HANDLER ─────────────

@bot.on_callback_query()
async def cb_handler(_, query):
    chat_id = query.message.chat.id
    data = query.data

    if data == "help_menu":
        help_text = (
            "<b>📖 <u>ʙᴏᴛ ʜᴇʟᴘ ᴍᴇɴᴜ</u></b>\n\n"
            "🚀 <b>/play</b> [ꜱᴏɴɢ]  |  🛑 <b>/stop</b>\n"
            "⏭ <b>/skip</b>  |  ⏸ <b>/pause</b>\n"
            "▶️ <b>/resume</b>  |  📋 <b>/queue</b>\n"
            "📡 <b>/ping</b> - Stats check"
        )
        # Back button compact
        await query.message.edit_caption(
            caption=help_text,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ ʙᴀᴄᴋ", callback_data="back_to_start")]])
        )

    elif data == "repo_menu":
        repo_text = (
            "<b>📂 <u>ʀᴇᴘᴏsɪᴛᴏʀʏ ɪɴғᴏ</u></b>\n\n"
            "✨ <b>Owner:</b> <a href='https://t.me/sxyaru'>sxyaru</a>\n"
            "🛠 <b>Language:</b> Python\n\n"
            "Custom music player build by sxyaru."
        )
        await query.message.edit_caption(
            caption=repo_text,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ ʙᴀᴄᴋ", callback_data="back_to_start")]])
        )

    elif data == "back_to_start":
        text = (
            "<b>╔══════════════════╗</b>\n"
            "<b>   🎵 ᴍᴜsɪᴄ ᴘʟᴀʏᴇʀ ʙᴏᴛ 🎵   </b>\n"
            "<b>╚══════════════════╝</b>\n\n"
            "<b>👋 ʜᴇʟʟᴏ! ɪ ᴀᴍ ᴀ ғᴀsᴛ & ᴘᴏᴡᴇʀғᴜʟ</b>\n"
            "<b>ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ᴍᴜsɪᴄ ᴘʟᴀʏᴇʀ ʙᴏᴛ.</b>"
        )
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("❓ ʜᴇʟᴘ", callback_data="help_menu"), InlineKeyboardButton("📂 ʀᴇᴘᴏ", callback_data="repo_menu")],
            [InlineKeyboardButton("👤 ᴏᴡɴᴇʀ", url="https://t.me/sxyaru"), InlineKeyboardButton("📢 sᴜᴘᴘᴏʀᴛ", url="https://t.me/your_channel")],
            [InlineKeyboardButton("➕ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ", url=f"https://t.me/{bot.me.username}?startgroup=true")]
        ])
        await query.message.edit_caption(caption=text, reply_markup=buttons)

    # Music Player Buttons (Compact Row)
    # Jab /play karoge, tab ye buttons 1 hi line mein ayenge
    elif data == "pause_cb":
        try: await call.pause_stream(chat_id); await query.answer("Paused ⏸")
        except: await query.answer("Nothing playing!", show_alert=True)

    elif data == "resume_cb":
        try: await call.resume_stream(chat_id); await query.answer("Resumed ▶️")
        except: await query.answer("Nothing playing!", show_alert=True)




@bot.on_message(filters.command("stop"))
async def stop_cmd(_, msg: Message):
    try:
        await message.delete()
    except:
        pass
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
