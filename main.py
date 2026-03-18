import math
import time
import random
import psutil
from datetime import datetime, timedelta
import asyncio
import aiohttp
from urllib.parse import quote
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from pyrogram.errors import FloodWait
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
# --- Random image links ---
WELCOME_IMAGES = [
    "https://files.catbox.moe/nacfzm.jpg",
    "https://files.catbox.moe/x4lzbx.jpg",
    "https://files.catbox.moe/g6cmb2.jpg",
    "https://files.catbox.moe/3hxb96.jpg",
    "https://files.catbox.moe/3h3vqz.jpg",
    "https://files.catbox.moe/yah7a9.jpg"
]
# --- Welcome message template ---
WELCOME_TEXT = """🌸✨ ──────────────────── ✨🌸  
🎊 <b>ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴏᴜʀ ɢʀᴏᴜᴘ</b> 🎊  
  
🌹 <b>ɴᴀᴍᴇ</b> ➤ {name}  
🆔 <b>ᴜsᴇʀ ɪᴅ</b> ➤ <code>{user_id}</code>  
🏠 <b>ɢʀᴏᴜᴘ</b> ➤ {chat_title}  
  
💕 <b>ᴡᴇ'ʀᴇ sᴏ ʜᴀᴘᴘʏ ᴛᴏ ʜᴀᴠᴇ ʏᴏᴜ ʜᴇʀᴇ!</b>  
✨ <b>ғᴇᴇʟ ғʀᴇᴇ ᴛᴏ sʜᴀʀᴇ ᴀɴᴅ ᴇɴᴊᴏʏ!</b>  
⚡ <b>ᴇɴᴊᴏʏ ʏᴏᴜʀ ᴇxᴘᴇʀɪᴇɴᴄᴇ ᴡɪᴛʜ ᴛʜɪs ʙᴏᴛ</b>  
  
💝 <b>ᴘᴏᴡᴇʀᴇᴅ ʙʏ ➤</b> <a href="https://t.me/sxyaru">˹ᴀʀᴜ × ᴀᴘɪ˼ × [ʙᴏᴛs]</a>  
🌸✨ ──────────────────── ✨🌸  
"""

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
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours > 0:
        return f"{hours:02}:{minutes:02}:{seconds:02}"
    return f"{minutes:02}:{seconds:02}"

def gen_btn_progressbar(total_sec, current_sec):
    # Pehle bar_length 12-15 thi, ab 6-8 karke dekho
    bar_length = 8 
    
    if total_sec == 0: total_sec = 1
    percentage = (current_sec / total_sec) * 100
    percentage = min(100, max(0, percentage))
    
    filled_blocks = int(percentage / (100 / bar_length))
    
    # Dot wala style (Image match)
    bar = "▬" * filled_blocks + "●" + "▬" * (bar_length - filled_blocks)
    
    return f"{fmt_time(current_sec)} {bar} {fmt_time(total_sec)}"


# TIMER LOOPER (Ye background mein chalega)
# Humein queues aur call variables yahan chahiye honge
async def update_timer(chat_id, message_id, duration):
    current_time = 0
    while current_time < duration:
        await asyncio.sleep(10) # 10 sec ka gap perfect hai
        
        # Check karo agar music stop ho gaya ya queue khali ho gayi
        if chat_id not in queues:
            break
            
        # Agar music paused hai, toh timer mat badhao
        # (Iske liye aapko ek 'is_paused' variable ya check chahiye hoga)
        # Abhi ke liye hum simple increment kar rahe hain:
        current_time += 10

        # Sabse bada FIX: Agar current_time duration se upar nikal jaye
        if current_time >= duration:
            current_time = duration # Full bar dikhao aur loop khatam karo

        new_prog = gen_btn_progressbar(duration, current_time)
        
        try:
            await bot.edit_message_reply_markup(
                chat_id,
                message_id,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(text=new_prog, callback_data="prog_update")],
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
                        InlineKeyboardButton("ᴏᴡɴᴇʀ↗", url="https://t.me/ll_PANDA_BBY_ll"),
                        InlineKeyboardButton("sᴜᴘᴘᴏʀᴛ ↗", url="https://t.me/sxyaru")
                    ]
                ])
            )
            # Agar gaana khatam ho gaya toh loop exit kar do
            if current_time >= duration:
                break
        except Exception:
            break



#BASE BOOST

# --- Global Level Variable ---

@bot.on_message(filters.command("level"))
async def set_boost_level(_, msg: Message):
    global UKHI_LEVEL
    if len(msg.command) < 2:
        return await msg.reply("❌ **Level do (1-20)!**")
    
    try:
        level = int(msg.command[1])
        if 1 <= level <= 20:
            UKHI_LEVEL = level
            await msg.reply(f"🔊 **Ukhi Boost Level set to:** `{level}`\n⚡ *Ab /boost_on karke dekho!*")
        else:
            await msg.reply("❌ 1-20 range rakho!")
    except:
        await msg.reply("❌ Number do Brahh!")

from pytgcalls.types.input_stream import AudioPiped, HighQualityAudio

@bot.on_message(filters.command("boost_on"))
async def start_boost(_, msg: Message):
    chat_id = msg.chat.id
    ukhi_filt = f"bass=g={UKHI_LEVEL*2},volume={UKHI_LEVEL},aecho=0.8:0.8:40:0.5"

    try:
        await msg.reply("🎤 **Assistant is now listening & boosting...**")
        
        # Sabse safe tareeka: Direct FFMPEG string pass karna
        await call.join_group_call(
            chat_id,
            AudioPiped(
                f"pulse", # Input source
                HighQualityAudio(),
                # Yahan hum 'additional_ffmpeg_parameters' try karenge
                additional_ffmpeg_parameters=f"-af {ukhi_filt}" 
            )
        )
    except Exception as e:
        # AGAR PHIR BHI ERROR AAYE, TOH YE TRY KARO (Final Boss):
        try:
             await call.join_group_call(
                chat_id,
                AudioPiped(
                    "pulse",
                    HighQualityAudio()
                    # Bina filters ke join karo pehle, check karne ke liye
                )
            )
             await msg.reply("⚠️ **Note:** Filters support nahi ho rahe, par Assistant join ho gaya hai.")
        except:
            await msg.reply(f"❌ Error: {e}")



@bot.on_message(filters.command("boost_off"))
async def stop_boost(_, msg: Message):
    try:
        await call.leave_group_call(msg.chat.id)
        await msg.reply("🔇 **Boost OFF!**")
    except:
        pass
#WELCOME FUNCTION FOR USER WHO JOIN GROUP
# --- Handler for new members ---
# --- Updated Welcome Handler ---
@bot.on_message(filters.new_chat_members & filters.group)
async def welcome_user(client, msg: Message):
    # Debug ke liye print (Check karo terminal mein ye print ho raha hai ya nahi)
    print(f"New member detected in: {msg.chat.title}")

    for user in msg.new_chat_members:
        # Agar bot khud join kare toh welcome na kare
        if user.is_self:
            continue
            
        try:
            name = user.first_name or "User"
            user_id = user.id
            chat_title = msg.chat.title
            
            photo = random.choice(WELCOME_IMAGES)
            
            caption = WELCOME_TEXT.format(
                name=name, 
                user_id=user_id, 
                chat_title=chat_title
            )

            buttons = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("• ᴄʜᴀɴɴᴇʟ •", url="https://t.me/sxyaru"),
                    InlineKeyboardButton("• ᴏᴡɴᴇʀ •", url="https://t.me/ll_PANDA_BBY_ll")
                ]
            ])

            wel_msg = await client.send_photo(
                chat_id=msg.chat.id,
                photo=photo,
                caption=caption,
                reply_markup=buttons
            )

            # 60 Seconds baad delete
            await asyncio.sleep(60)
            await wel_msg.delete()

        except Exception as e:
            print(f"[WELCOME ERROR] {e}")



@bot.on_message(filters.command("ping"))
async def ping_cmd(_, msg: Message):
    # User ka /ping command delete karne ki koshish
    try:
        await msg.delete()
    except:
        pass

    start_time = time.time()
    
    # Temporarily 'Pinging...' message (Optional, direct photo bhi bhej sakte ho)
    m = await msg.reply_text("<code>ᴘɪɴɢɪɴɢ..</code>")
    
    # Latency Calculation
    end_time = time.time()
    latency = round((end_time - start_time) * 1000, 2)
    
    # Uptime Logic
    uptime_sec = (datetime.now() - BOT_START_TIME).total_seconds()
    uptime = str(timedelta(seconds=int(uptime_sec)))
    
    # System Stats
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent

    # Final Text
    text = (
        "<b>🏓 ᴘᴏɴɢ! sᴛᴀᴛs ᴀʀᴇ ʜᴇʀᴇ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"🚀 <b>ʟᴀᴛᴇɴᴄʏ:</b> <code>{latency} ms</code>\n"
        f"🆙 <b>ᴜᴘᴛɪᴍᴇ:</b> <code>{uptime}</code>\n"
        f"💻 <b>ᴄᴘᴜ:</b> <code>{cpu}%</code>\n"
        f"📊 <b>ʀᴀᴍ:</b> <code>{ram}%</code>\n"
        f"💾 <b>ᴅɪsᴋ:</b> <code>{disk}%</code>\n"
        f"📡 <b>ᴘʏᴛɢᴄᴀʟʟs:</b> <code>2.2.11</code>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "👤 <b>ᴏᴡɴᴇʀ:</b> <a href='https://t.me/sxyaru'>ᴀʀᴜ × ᴀᴘɪ [ʙᴏᴛs]</a>"
    )

    # Buttons
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("sᴜᴘᴘᴏʀᴛ", url="https://t.me/sxyaru"),
            InlineKeyboardButton("ᴅᴇᴠᴇʟᴏᴘᴇʀ", url="https://t.me/ll_PANDA_BBY_ll")
        ]
    ])

    # 1. Pinging message delete karo
    await m.delete()

    # 2. Final Photo + Caption + Buttons bhejo
    # Yahan apni pasand ki image link daal dena
    PING_IMG = "https://files.catbox.moe/nacfzm.jpg" 
    
    await bot.send_photo(
        msg.chat.id,
        photo=PING_IMG,
        caption=text,
        reply_markup=buttons
    )


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


# --- Ye aapka Updated Play Command hai ---
@bot.on_message(filters.command("play"))
async def play_cmd(_, msg: Message):
    try:
        await msg.delete()
    except:
        pass
    chat_id = msg.chat.id
    user_name = msg.from_user.first_name if msg.from_user else "User"

    # 1. Assistant Status & Admin Checks
    try:
        assistant_info = await assistant.get_me()
        ast_id = assistant_info.id
        ast_username = f"@{assistant_info.username}" if assistant_info.username else "Assistant"
        
        try:
            ast_member = await bot.get_chat_member(chat_id, ast_id)
            if ast_member.status == ChatMemberStatus.BANNED:
                return await msg.reply(f"❌ **ᴀssɪsᴛᴀɴᴛ ɪs ʙᴀɴ!**\nᴘʟs ᴜɴʙᴀɴ {ast_username} (ɪᴅ: <code>{ast_id}</code>)")
            if ast_member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                return await msg.reply(f"❌ **ᴀssɪsᴛᴀɴᴛ ɪs ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ!**\nᴍᴀᴋᴇ {ast_username} ᴀs ᴀᴅᴍɪɴ ᴛᴏ ᴍᴀɴᴀɢᴇ ᴛʜᴇ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ")
        except Exception as e:
            if "USER_NOT_PARTICIPANT" in str(e):
                m = await msg.reply(f"🔄 **ɪɴᴠɪᴛɪɴɢ ᴀssɪsᴛᴀɴᴛ ᴛᴏ ɢʀᴏᴜᴘ...**")
                try:
                    invitelink = await bot.export_chat_invite_link(chat_id)
                    await assistant.join_chat(invitelink)
                    return await m.edit(f"✅ **ᴀssɪsᴛᴀɴᴛ ᴊᴏɪɴᴇᴅ ᴛʜᴇ ɢʀᴏᴜᴘ ᴍᴀᴋᴇ ᴀᴅᴍɪɴ ᴛʜᴇɴ /play**")
                except: return await m.edit("❌ ᴀᴜᴛᴏ ɪɴᴠɪᴛɪɴɢ ғᴀɪʟᴇᴅ ᴀᴅᴅ ᴛʜᴇ ᴀssɪsᴛᴀɴᴛ ᴍᴀɴᴜᴀʟʟʏ")
            pass
    except Exception as e:
        return await msg.reply(f"❌ Assistant Error: {e}")

    # 2. Search Logic
    if len(msg.command) < 2:
        return await msg.reply("❌ **ɢɪᴠᴇ ǫᴜᴇʀʏ!**")

    query = msg.text.split(None, 1)[1].strip()
    m = await msg.reply("🔎 <b>sᴇᴀʀᴄʜɪɴɢ...</b>")

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
    thumb = "https://files.catbox.moe/uyum1c.jpg"

    # 3. Queue Logic
    song_data = {"title": title, "url": stream_url, "duration": duration, "by": user_name}
    queues.setdefault(chat_id, []).append(song_data)

    # 4. 🔥 CRITICAL STEP: TRY JOINING FIRST 🔥
    # Pehle join karne ki koshish (True/False return)
    # Humein play_next variable mein return status capture karna hai
    try:
        join_status = await play_next(chat_id)
    except:
        join_status = False # play_next failed explicitly

    if not join_status:
        # Agar join fail hua, toh searching message delete karo aur menu mat bhejo
        await m.delete()
        return

    # 5. UI Layout (Buttons set to Small/Compact and Timer fix)
    # gen_btn_progressbar function upar paste kiya hai
    btn_prog = gen_btn_progressbar(duration, 0) 
    
    text = (
        f"<b>❍ Sᴛᴀʀᴛᴇᴅ Sᴛʀᴇᴀᴍɪɴɢ |</b>\n\n"
        f"<b>‣ Tɪᴛʟᴇ :</b> <a href='{stream_url}'>{title}</a>\n"
        f"<b>‣ Dᴜʀᴀᴛɪᴏɴ :</b> <code>{fmt_time(duration)} ᴍs</code>\n"
        f"<b>‣ Rᴇǫᴜᴇsᴛᴇᴅ ʙʏ :</b> `{user_name}`\n"
        f"<b>‣ ʙᴏᴛ ʙᴀsᴇᴅ ᴏɴ : ᴀʀᴜ x ᴊɪᴏsᴀᴠᴀɴ</b>\n"
        f"<b>‣ ᴀᴘɪ ʙʏ: <a href='https://t.me/sxyaru'>ᴀʀᴜ × ᴀᴘɪ [ʙᴏᴛs]</a></b>\n"
        f"<b>‣ ᴀᴘɪ ᴍᴀᴅᴇ ʙʏ: <a herf='href=https://t.me/ll_PANDA_BBY_ll'>ᴘᴀɴᴅᴀ-ʙᴀʙʏ</a></b>"
    )

    # Exact Photo Style (Row 2 mein 4 compact buttons)
    buttons = InlineKeyboardMarkup([
        [
            # Row 1: Progress Bar Button (10 blocks)
            InlineKeyboardButton(text=btn_prog, callback_data="prog_update")
        ],
        [
            # Row 2: 4 Buttons (Isse buttons baraber 'Small' dikhenge)
            InlineKeyboardButton("▷", callback_data="resume_cb"),
            InlineKeyboardButton("Ⅱ", callback_data="pause_cb"),
            InlineKeyboardButton("⏭", callback_data="skip_cb"),
            InlineKeyboardButton("▢", callback_data="stop_cb")
        ],
        [
            # Row 3: 3 Buttons
            InlineKeyboardButton("⏮ -20s", callback_data="seek_back"),
            InlineKeyboardButton("↺", callback_data="replay_cb"),
            InlineKeyboardButton("+20s ⏭", callback_data="seek_forward")
        ],
        [
            InlineKeyboardButton("ᴏᴡɴᴇʀ↗", url="https://t.me/ll_PANDA_BBY_ll"),
            InlineKeyboardButton("sᴜᴘᴘᴏʀᴛ ↗", url="https://t.me/sxyaru")
        ]
    ])

    await m.delete()
    
    # 6. SEND PHOTO AND START TIMER
    # Sent message ko pmp capture kiya hai ID timer ko dene ke liye
    pmp = await bot.send_photo(chat_id, photo=thumb, caption=text, reply_markup=buttons)
    
    # Ye line progress bar timer ko background mein start kar degi
    asyncio.create_task(update_timer(chat_id, pmp.id, duration))







async def play_next(chat_id: int):
    # 1. Check karo queue mein gaana hai ya nahi
    if chat_id not in queues or not queues[chat_id]:
        return False
    
    song = queues[chat_id][0]
    url = song["url"]

    try:
        # 2. Assistant ko join ya stream change karwana
        try:
            await call.join_group_call(
                chat_id,
                AudioPiped(url, HighQualityAudio()),
                stream_type=StreamType().pulse_stream
            )
        except Exception:
            # Agar pehle se VC mein hai toh sirf stream badlo
            await call.change_stream(
                chat_id,
                AudioPiped(url, HighQualityAudio())
            )
        
        # Agar yahan tak code pahuncha matlab SUCCESS!
        return True
            
    except Exception as e:
        print(f"Assistant Join Error: {e}")
        
        # Error aane par queue se gaana hata do
        if chat_id in queues:
            queues[chat_id].pop(0)
            
        # Error message format
        error_text = f"❌ **ᴘʟᴇᴀsᴇ ᴏɴ ᴛʜᴇ ᴠᴄ**\n\n"
        
        # Special check for VC not started
        if "CHAT_ADMIN_REQUIRED" in str(e):
            error_text += "💡 **Reason:** ᴀssɪsᴛᴀɴᴛ ʜᴀᴠᴇ ɴᴏ ᴘᴇʀᴍɪssɪᴏɴ ᴏғ ᴍᴀɴᴀɢᴇᴅ ᴠɪᴅᴇᴏ ᴄʜᴀᴛ."
        elif "not in a group call" in str(e).lower() or "GROUP_CALL_NOT_MODIFIED" in str(e):
            error_text += "💡 **Reason:** ғɪʀsᴛ sᴛᴀʀᴛ ᴛʜᴇ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ᴠᴄ!"
        else:
            error_text += f"💬 **Error:** <code>{e}</code>"
            
        await bot.send_message(chat_id, error_text)
        
        # Matlab FAILED!
        return False





# ───────────── CALLBACK HANDLER ─────────────

@bot.on_callback_query()
async def cb_handler(_, query):
    chat_id = query.message.chat.id
    data = query.data

    # --- Start & Help Menus ---
    if data == "help_menu":
        help_text = (
            "<b> ʙᴏᴛ ʜᴇʟᴘ ᴍᴇɴᴜ</b>\n\n"
            "<b>/play</b> [ꜱᴏɴɢ ɴᴀᴍᴇ]</b>\n"  
            "<b>/ping</b> - Stats check"
        )
        await query.message.edit_caption(
            caption=help_text,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="back_to_start")]])
        )

    elif data == "repo_menu":
        repo_text = (
            "<b> ʀᴇᴘᴏ ᴋʏᴀ ʟᴇɢᴀ ᴍᴀᴅᴀʀᴄʜᴏᴅ\nᴘᴀɴᴅᴀ ᴋᴀ ʟᴀɴᴅ ʟᴇʟᴇ ʙᴏʟ ʟᴇɢᴀ 😂🖕??</b>"
        )
        await query.message.edit_caption(
            caption=repo_text,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="back_to_start")]])
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
        await msg.delete()
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
