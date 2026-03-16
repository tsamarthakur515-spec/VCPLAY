
import time
import psutil
from urllib.parse import quote
from datetime import datetime, timedelta
import asyncio
from asyncio import create_task, sleep, CancelledError
import aiohttp
from pyrogram.enums import ParseMode
from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped
from pytgcalls.types.input_stream.quality import HighQualityAudio

# ------------------- CONFIG -------------------
API_ID = 33603336
API_HASH = "c9683a8ec3b886c18219f650fc8ed429"
BOT_TOKEN = "YOUR_BOT_TOKEN"
SESSION = "BQE-4i0ASxu8TXk4s870tFMn-D2Ijs-7DaTep8qcmRnZuowGYTiKDzzy9fKRT3pCc7aFI9oql0Rp5k1FkymDhRbewYPN11p5G7exMCs-z2bdMPuRoJCF60r7p_xq0TBjtLw5P1f-pXHHRxeXSAq0nKyNglv2pZ-GVCbYL4J-OwIkfck4wZyfiU0H58LZla5Il4VmVww-ewK3roa4mVjIxGKYoFva7LqYEf9Iti77jLz7HW7gCfuNessLDXqH1se4DuOSmoJzbacJxofENDQJChGjP4K7gbkMQQKwjCQfndvTmHLyDnc5jDqwfngZK1ogepmyiXZhhzHVebIieznK4DXTM1Q7pAAAAAHKarFXAA"
# ----------------------------------------------

bot = Client(
    "musicbot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

assistant = Client(
    "assistant",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION
)

call = PyTgCalls(assistant)
BOT_START_TIME = datetime.now()
# ----------------- COMMANDS ------------------

# VOICE COMMAND
@bot.on_message(filters.command("start"))
async def start(client, message):
    text = (
        "<b>👋 Hello!</b>\n\n"
        "🎧 I am a <b>Voice Chat Music Bot</b>.\n"
        "I can play songs in Telegram Voice Chat.\n\n"
        "<b>📌 Commands:</b>\n"
        "• /play <song name> - Play music in VC\n"
        "• /stop - Stop music\n"
        "• /ping - Check bot speed\n"
        "• /level 1-20 - Change volume\n"
        "• /rfplay - Reply audio to play\n\n"
        "⚡ Powered by Pyrogram & PyTgCalls"
    )

    await message.reply_text(
        text,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )
#PINH COMMAND

@bot.on_message(filters.command("ping"))
async def ping(client, message):

    try:
        await message.delete()
    except:
        pass

    start = time.monotonic()

    msg = await message.reply_text("鈿� Pinging...")

    frames = [
        "▰▱▱▱▱▱▱▱▱▱ 10%",
        "▰▰▱▱▱▱▱▱▱▱ 20%",
        "▰▰▰▱▱▱▱▱▱▱ 30%",
        "▰▰▰▰▱▱▱▱▱▱ 40%",
        "▰▰▰▰▰▱▱▱▱▱ 50%",
        "▰▰▰▰▰▰▱▱▱▱ 60%",
        "▰▰▰▰▰▰▰▱▱▱ 70%",
        "▰▰▰▰▰▰▰▰▱▱ 80%",
        "▰▰▰▰▰▰▰▰▰▱ 90%",
        "▰▰▰▰▰▰▰▰▰▰ 100%"
    ]

    for frame in frames:
        await asyncio.sleep(0.1)
        try:
            await msg.edit(f"鈿� Checking Bot Speed...\n\n{frame}")
        except:
            pass

    end = time.monotonic()
    ping = round((end - start) * 1000, 2)

    uptime_sec = int((datetime.now() - BOT_START_TIME).total_seconds())
    uptime = str(timedelta(seconds=uptime_sec)).split('.')[0]

    cpu = psutil.cpu_percent()

    try:
        vc_status = "馃煝 Active" if call.is_connected else "馃敶 Not Active"
    except:
        vc_status = "鈿狅笍 Unknown"

    me = await client.get_me()
    name = me.first_name

    text = (
    f"<blockquote>"
    f"鈺攢鉂� <b>{name} 蕶岽忈礇 s岽涐磤岽涐礈s</b>\n"
    f"鈹溾殹 <b>岽樕瓷�:</b> <code>{ping} ms</code>\n"
    f"鈹溾彵 <b>岽溼礃岽浬磵岽�:</b> <code>{uptime}</code>\n"
    f"鈹滒煉� <b>岽勧礃岽�:</b> <code>{cpu}%</code>\n"
    f"鈹滒煄� <b>岽犪磩:</b> {vc_status}\n"
    f"鈺梆煍� <b>岽�岽樕�:</b> <a href='https://t.me/sxyaru'>岽�蕗岽� 脳 岽�岽樕� [蕶岽忈礇s]</a>"
    f"</blockquote>"
)

    await msg.edit_text(
    text,
    parse_mode=ParseMode.HTML,
    disable_web_page_preview=True
)
# ----------------- PLAY COMMAND -----------------
def format_time(seconds: int):
    minutes, sec = divmod(seconds, 60)
    return f"{minutes}:{sec:02d}"

def create_progress_bar(current, total, length=12):
    """Return a progress bar like: 鈻戔枒鈻戰煍樷枒鈻戔枒"""
    if total == 0:
        total = 1
    pos = int(length * current / total)
    bar = "鈹�" * pos + "鈥�" + "鈹�" * (length - pos)
    return bar

#DURATION STOP

def format_time(seconds: int):
    minutes, sec = divmod(seconds, 60)
    return f"{minutes}:{sec:02d}"

@bot.on_message(filters.command("play"))
async def play(client, message):
    try:
        await message.delete()
    except:
        pass

    if len(message.command) < 2:
        return await message.reply(
            "散瑟岽犪磭 谦岽溼磭蕗蕪 岽涐磸 s岽囜磤蕗岽勈淺nExample: `.play mann mera`"
        )

    query = message.text.split(None, 1)[1]
    status_msg = await message.reply("`s岽囜磤蕗岽勈溕瓷� 蕪岽忈礈蕗 谦岽溼磭蕗蕪 馃捒`")

    # Fetch API
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://jio-saa-van.vercel.app/result/?query={query}"
            async with session.get(url) as resp:
                data = await resp.json()
    except Exception as e:
        return await status_msg.edit(f"鈿狅笍 Failed to fetch API: {e}")

    results = data
    if not results:
        return await status_msg.edit("鉂� 谦岽溼磭蕗蕪 纱岽忈礇 覔岽忈礈纱岽�")

    song = results[0]

    stream_url = song.get("media_url")
    if not stream_url:
        return await status_msg.edit("鉂� No playable link found!")

    title = song.get("song") or "Unknown"
    artist = song.get("primary_artists") or song.get("singers") or "Unknown"

    # Duration convert
    duration_sec = int(song.get("duration") or 0)
    duration_fmt = format_time(duration_sec)

    progress_bar = f"0:00 鈹�鈹�鈹�鈥⑩攢鈹�鈹�鈹� {duration_fmt}"

    # Join VC
    try:
        await call.join_group_call(
            message.chat.id,
            AudioPiped(stream_url, HighQualityAudio())
        )
    except Exception as e:
        if "isn't in a group call" in str(e):
            try:
                await call.leave_group_call(message.chat.id)
                await call.join_group_call(
                    message.chat.id,
                    AudioPiped(stream_url, HighQualityAudio())
                )
            except Exception as ee:
                return await status_msg.edit(f"鈿狅笍 Could not join VC: {ee}")
        else:
            try:
                await call.change_stream(
                    message.chat.id,
                    AudioPiped(stream_url, HighQualityAudio())
                )
            except Exception as ee:
                return await status_msg.edit(f"鈿狅笍 Could not play in VC: {ee}")

    await status_msg.edit(
        f"馃帶 **Streaming started!**\n\n"
        f"馃幍 **Title:** {title}\n"
        f"馃懁 **Artist:** {artist}\n"
        f"鈴� **Duration:** {progress_bar}\n\n"
        f"馃檵 **Requested by:** {message.from_user.first_name}\n"
        f"馃敆 **API:** @sxyaru"
    )


#VIDEO PLAYING FUNCTION



# ----------------- REPLY TO AUDIO FILE PLAY -----------------
@bot.on_message(filters.command("rfplay"))
async def rfplay_music(_, message):
    try:
        await message.delete()
    except:
        pass
    chat_id = message.chat.id

    # Check if replied to an audio/voice
    if message.reply_to_message:
        audio = message.reply_to_message.audio or message.reply_to_message.voice
        if not audio:
            return await message.reply("鉂� Reply to an audio file")

        # Download the file
        file = await message.reply_to_message.download()

        try:
            # Try changing stream if already in VC
            await call.change_stream(chat_id, AudioPiped(file, HighQualityAudio()))
        except:
            # Else join VC and play
            await call.join_group_call(chat_id, AudioPiped(file, HighQualityAudio()))

        duration = None
        if audio.duration:
            mins, secs = divmod(audio.duration, 60)
            duration = f"{mins}:{secs:02d}"

        await message.reply(
            f"馃幍 Playing replied audio\n"
            f"鈴� Duration: {duration or 'Unknown'}\n"
            f"馃幍 Requested by: {message.from_user.first_name}\n"
            f"馃敆 Music based on: [Local File]"
        )
        return
    else:
        return await message.reply("鉂� Please reply to an audio or voice message to play it.")

@bot.on_message(filters.command("stop"))
async def stop(client, message):
    try:
        await message.delete()
    except:
        pass
    try:
        await call.leave_group_call(message.chat.id)
        await message.reply("鈴� Stopped")
    except Exception as e:
        await message.reply(f"鈿狅笍 Could not leave VC: {e}")


# ----------------- RUN BOT -------------------
assistant.start()
bot.start()
call.start()
print("馃幍 VC Music Bot Started")
asyncio.get_event_loop().run_forever()

