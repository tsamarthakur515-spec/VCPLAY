import math
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
from pyrogram.enums import ChatMemberStatus # Ye line sabse upar imports mein add kar dena
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
# global dictionaries for tracking (Add these near top of file)
playing_messages = {} # {chat_id: message_id}
current_playing = {} # {chat_id: {"title": ..., "duration": ..., "start_time": ...}}


#MUSIC PLAYING TIMER
def fmt_time(seconds):
    if seconds <= 0:
        return "00:00"
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours > 0:
        return f"{hours:02}:{minutes:02}:{seconds:02}"
    return f"{minutes:02}:{seconds:02}"
#MUSIC PROGRESS BAR

def gen_progressbar(total_sec, current_sec):
    if total_sec == 0:
        total_sec = 1 # ZeroDivisionError se bachne ke liye
    percentage = (current_sec / total_sec) * 100
    percentage = min(100, max(0, percentage)) # Percentage 0-100 ke beech rahe
    
    # Bar style (Total 10 blocks)
    bar_length = 10
    filled_blocks = math.floor(percentage / (100 / bar_length))
    
    # ▬▬▬▬▬▬▬ style bar
    bar = "▬" * filled_blocks + "▬" + "▬" * (bar_length - filled_blocks)
    
    current_str = fmt_time(current_sec)
    total_str = fmt_time(total_sec)
    
    return f"<code>{current_str}</code> {bar} <code>{total_str}</code>"


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
    # Pehle purana message delete karo (agar ho sake)
    try:
        await msg.delete() 
    except:
        pass

    # Bot knamfo ek hi baar fetch kar lete hain performance ke liye
    me = await bot.get_me()
    bot_name = me.first_name
    bot_username = me.username
    
    # ──────── ANIMATION START ────────
    # 1st Phase: HEY
    m = await bot.send_message(msg.chat.id, "<b>ʜᴇʏ...</b>")
    await asyncio.sleep(0.8) # Thoda wait
    
    # 2nd Phase: HOW ARE YOU
    await m.edit_text("<b>ʜᴏᴡ ᴀʀᴇ ʏᴏᴜ? ✨</b>")
    await asyncio.sleep(0.8)
    
    # 3rd Phase: I AM [BOTNAME] STARTING...
    bot_name = (await bot.get_me()).first_name
    await m.edit_text(f"<b>ɪ ᴀᴍ {bot_name} 🎵\nsᴛᴀʀᴛɪɴɢ.....</b>")
    await asyncio.sleep(1.0)
    
    # Animation khatam, ab message delete karke main menu bhejenge
    await m.delete()
    # ──────── ANIMATION END ────────

    START_IMG = "https://files.catbox.moe/uyum1c.jpg" 
    
    text = (
        "<b>╔══════════════════╗</b>\n"
        "<b>   🎵 ᴍᴜsɪᴄ ᴘʟᴀʏᴇʀ ʙᴏᴛ 🎵   </b>\n"
        "<b>╚══════════════════╝</b>\n\n"
        "<b>👋 ʜᴇʟʟᴏ! ɪ ᴀᴍ ᴀ ғᴀsᴛ & ᴘᴏᴡᴇʀғᴜʟ</b>\n"
        "<b>ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ᴍᴜsɪᴄ ᴘʟᴀʏᴇʀ ʙᴏᴛ.</b>\n\n"
        "✨ <b>ᴍᴀᴅᴇ ᴡɪᴛʜ ❤️ ʙʏ:</b> <a href='https://t.me/sxyaru'>sxyaru</a>"
    )

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
            InlineKeyboardButton("➕ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ", url=f"https://t.me/{(await bot.get_me()).username}?startgroup=true")
        ]
    ])

    await bot.send_photo(
        msg.chat.id,
        photo=START_IMG,
        caption=text,
        reply_markup=buttons
    )

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from pyrogram.enums import ChatMemberStatus # Ye line sabse upar imports mein add kar dena

@bot.on_message(filters.command("play"))
async def play_cmd(_, msg: Message):
    chat_id = msg.chat.id
    user_name = msg.from_user.first_name if msg.from_user else "User"

    # 1. Assistant Status & Admin Checks (Wahi purana solid logic)
    try:
        assistant_info = await assistant.get_me()
        ast_id = assistant_info.id
        ast_username = f"@{assistant_info.username}" if assistant_info.username else "Assistant"
        ast_member = await bot.get_chat_member(chat_id, ast_id)
        
        if ast_member.status == ChatMemberStatus.BANNED:
            return await msg.reply(f"❌ **Assistant is Banned!**\nPls unban: {ast_username}")
        if ast_member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return await msg.reply(f"❌ **Assistant is not Admin!**\nMake {ast_username} admin first.")
    except Exception as e:
        if "USER_NOT_PARTICIPANT" in str(e):
            try:
                invitelink = await bot.export_chat_invite_link(chat_id)
                await assistant.join_chat(invitelink)
                return await msg.reply(f"✅ **Assistant Joined!**\nAb admin banao aur play karo.")
            except: return await msg.reply("❌ Auto-invite failed!")
        pass

    # 2. Search Logic
    if len(msg.command) < 2:
        return await msg.reply("❌ **Song name toh do!**")

    query = msg.text.split(None, 1)[1].strip()
    m = await msg.reply("🔎 <b>Searching...</b>")

    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://jio-saa-van.vercel.app/result/?query={quote(query)}"
            async with session.get(url, timeout=12) as r:
                data = await r.json()
    except: return await m.edit("❌ API Error!")

    if not data or len(data) == 0:
        return await m.edit("❌ No results found.")

    track = data[0]
    title = track.get("song", "Unknown")
    duration = int(track.get("duration", 0))
    stream_url = track.get("media_url") or track.get("download_url")
    thumb = "https://files.catbox.moe/uyum1c.jpg" # Aapka diya hua image link

    # 3. Queue Logic
    song_data = {"title": title, "url": stream_url, "duration": duration, "by": user_name}
    queues.setdefault(chat_id, []).append(song_data)

    # 4. Progress Bar (Initial)
    # gen_progressbar(total, current) function use kar rahe hain
    prog_bar = gen_progressbar(duration, 0) 

    # 5. UI Layout (Exact Image Match)
    text = (
        f"<b>❍ Sᴛᴀʀᴛᴇᴅ Sᴛʀᴇᴀᴍɪɴɢ |</b>\n\n"
        f"<b>‣ Tɪᴛʟᴇ :</b> <a href='{stream_url}'>{title}</a>\n"
        f"<b>‣ Dᴜʀᴀᴛɪᴏɴ :</b> <code>{fmt_time(duration)} MINUTES</code>\n"
        f"<b>‣ Rᴇǫᴜᴇsᴛᴇᴅ ʙʏ :</b> —🌿❤️`{user_name}`— [7G]"
    )

    # 6. High-End Buttons (Exact Photo Style)
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("▷", callback_data="resume_cb"),
            InlineKeyboardButton("Ⅱ", callback_data="pause_cb"),
            InlineKeyboardButton("⏭", callback_data="skip_cb"),
            InlineKeyboardButton("▢", callback_data="stop_cb")
        ],
        [
            InlineKeyboardButton("⏮ -20s", callback_data="seek_back"),
            InlineKeyboardButton("↺", callback_data="replay_cb"),
            InlineKeyboardButton("+20s ⏭", callback_data="seek_forward")
        ],
        [
            InlineKeyboardButton("HELP ↗", callback_data="help_menu"),
            InlineKeyboardButton("SUPPORT ↗", url="https://t.me/your_channel")
        ]
    ])

    await m.delete()
    await bot.send_photo(
        chat_id, 
        photo=thumb, 
        caption=f"{text}\n\n{prog_bar}", 
        reply_markup=buttons
    )
    
    await play_next(chat_id)




async def play_next(chat_id: int):
    if chat_id not in queues or not queues[chat_id]:
        return
    
    song = queues[chat_id][0]
    url = song["url"]

    try:
        # Assistant join karne ki koshish karega
        try:
            await call.join_group_call(
                chat_id,
                AudioPiped(url, HighQualityAudio()),
                stream_type=StreamType().pulse_stream
            )
        except Exception:
            # Agar Assistant pehle se VC mein hai toh sirf gaana change hoga
            await call.change_stream(
                chat_id,
                AudioPiped(url, HighQualityAudio())
            )
            
    except Exception as e:
        print(f"Assistant Join Error: {e}")
        
        # Queue se gaana hatao taaki loop na bane
        if chat_id in queues:
            queues[chat_id].pop(0)
            
        # Sahi error message dikhane ke liye
        error_text = f"❌ **Assistant join nahi kar pa raha!**\n\n"
        if "CHAT_ADMIN_REQUIRED" in str(e):
            error_text += "💡 **Reason:** Assistant ke paas 'Manage Video Chats' permission nahi hai."
        else:
            error_text += f"💬 **Error:** `{e}`"
            
        await bot.send_message(chat_id, error_text)




# ───────────── CALLBACK HANDLER ─────────────

@bot.on_callback_query()
async def cb_handler(_, query):
    chat_id = query.message.chat.id
    data = query.data

    # --- Start & Help Menus ---
    if data == "help_menu":
        help_text = (
            "<b>📖 <u>ʙᴏᴛ ʜᴇʟᴘ ᴍᴇɴᴜ</u></b>\n\n"
            "🚀 <b>/play</b> [ꜱᴏɴɢ]  |  🛑 <b>/stop</b>\n"
            "⏭ <b>/skip</b>  |  ⏸ <b>/pause</b>\n"
            "▶️ <b>/resume</b>  |  📋 <b>/queue</b>\n"
            "📡 <b>/ping</b> - Stats check"
        )
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
        bot_me = await bot.get_me()
        text = (
        "<b>╔══════════════════╗</b>\n"
        "<b>   🎵 ᴍᴜsɪᴄ ᴘʟᴀʏᴇʀ ʙᴏᴛ 🎵   </b>\n"
        "<b>╚══════════════════╝</b>\n\n"
        "<b>👋 ʜᴇʟʟᴏ! ɪ ᴀᴍ ᴀ ғᴀsᴛ & ᴘᴏᴡᴇʀғᴜʟ</b>\n"
        "<b>ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ᴍᴜsɪᴄ ᴘʟᴀʏᴇʀ ʙᴏᴛ.</b>\n\n"
        "✨ <b>ᴍᴀᴅᴇ ᴡɪᴛʜ ❤️ ʙʏ:</b> <a href='https://t.me/sxyaru'>sxyaru</a>"
       )
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("❓ ʜᴇʟᴘ", callback_data="help_menu"), InlineKeyboardButton("📂 ʀᴇᴘᴏ", callback_data="repo_menu")],
            [InlineKeyboardButton("👤 ᴏᴡɴᴇʀ", url="https://t.me/sxyaru"), InlineKeyboardButton("📢 sᴜᴘᴘᴏʀᴛ", url="https://t.me/your_channel")],
            [InlineKeyboardButton("➕ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ", url=f"https://t.me/{bot_me.username}?startgroup=true")]
        ])
        await query.message.edit_caption(caption=text, reply_markup=buttons)

    # --- Play Music Controls (Photo Buttons) ---
    elif data == "pause_cb":
        try:
            await call.pause_stream(chat_id)
            await query.answer("Paused ⏸")
        except:
            await query.answer("Nothing playing!", show_alert=True)

    elif data == "resume_cb":
        try:
            await call.resume_stream(chat_id)
            await query.answer("Resumed ▶️")
        except:
            await query.answer("Nothing playing!", show_alert=True)

    elif data == "skip_cb":
        try:
            # Skip logic (Current song pop and play next)
            if chat_id in queues:
                queues[chat_id].pop(0)
            await play_next(chat_id)
            await query.answer("Skipped ⏭")
        except:
            await query.answer("Nothing to skip!", show_alert=True)

    elif data == "stop_cb":
        try:
            await call.leave_group_call(chat_id)
            queues.pop(chat_id, None)
            await query.message.delete()
            await query.answer("Stopped & Left VC ⏹")
        except:
            await query.answer("Assistant not in VC!", show_alert=True)

    # --- Advanced Controls (Seek & Replay) ---
    elif data == "seek_forward":
        await query.answer("Seeking +20s... ⏭")
        # Note: Seek requires proper frame support in PyTgCalls

    elif data == "seek_back":
        await query.answer("Seeking -20s... ⏮")

    elif data == "replay_cb":
        try:
            await play_next(chat_id)
            await query.answer("Replaying... ↺")
        except:
            await query.answer("Error replaying!", show_alert=True)





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
