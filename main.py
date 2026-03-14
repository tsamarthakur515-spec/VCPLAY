import time
import psutil
from urllib.parse import quote
from datetime import datetime, timedelta
import asyncio
import aiohttp
from pyrogram.enums import ParseMode
from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped
from pytgcalls.types.input_stream.quality import HighQualityAudio

# ------------------- CONFIG -------------------
API_ID = 33603336
API_HASH = "c9683a8ec3b886c18219f650fc8ed429"
SESSION = "BQE-4i0ASxu8TXk4s870tFMn-D2Ijs-7DaTep8qcmRnZuowGYTiKDzzy9fKRT3pCc7aFI9oql0Rp5k1FkymDhRbewYPN11p5G7exMCs-z2bdMPuRoJCF60r7p_xq0TBjtLw5P1f-pXHHRxeXSAq0nKyNglv2pZ-GVCbYL4J-OwIkfck4wZyfiU0H58LZla5Il4VmVww-ewK3roa4mVjIxGKYoFva7LqYEf9Iti77jLz7HW7gCfuNessLDXqH1se4DuOSmoJzbacJxofENDQJChGjP4K7gbkMQQKwjCQfndvTmHLyDnc5jDqwfngZK1ogepmyiXZhhzHVebIieznK4DXTM1Q7pAAAAAHKarFXAA"
# ----------------------------------------------

app = Client("vcbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION)
call = PyTgCalls(app)
BOT_START_TIME = datetime.now()
# ----------------- COMMANDS ------------------

# VOICE COMMAND
@app.on_message(filters.command("level", "."))
async def volume(client, message):

    try:
        await message.delete()
    except:
        pass

    if len(message.command) < 2:
        return await client.send_message(
            message.chat.id,
            "Usage: .level 1-20"
        )

    level = int(message.command[1])

    if level < 1 or level > 20:
        return await client.send_message(
            message.chat.id,
            "Level must be between 1 - 20"
        )

    volume = level * 5   # convert to VC volume

    try:
        await call.change_volume_call(
            message.chat.id,
            volume
        )
    except Exception as e:
        return await client.send_message(
            message.chat.id,
            f"VC Error: {e}"
        )

    await client.send_message(
        message.chat.id,
        f"🔊 Voice level set to {level}"
    )
#PINH COMMAND

@app.on_message(filters.command("ping", "."))
async def ping(client, message):

    try:
        await message.delete()
    except:
        pass

    start = time.monotonic()

    msg = await message.reply_text("⚡ Pinging...")

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
        await asyncio.sleep(0.3)
        try:
            await msg.edit(f"⚡ Checking Bot Speed...\n\n{frame}")
        except:
            pass

    end = time.monotonic()
    ping = round((end - start) * 1000, 2)

    uptime_sec = int((datetime.now() - BOT_START_TIME).total_seconds())
    uptime = str(timedelta(seconds=uptime_sec)).split('.')[0]

    cpu = psutil.cpu_percent()

    try:
        vc_status = "🟢 Active" if call.is_connected else "🔴 Not Active"
    except:
        vc_status = "⚠️ Unknown"

    me = await client.get_me()
    name = me.first_name

    text = (
    f"<blockquote>"
    f"╭─❖ <b>{name} Bot Status</b>\n"
    f"├⚡ <b>Ping:</b> <code>{ping} ms</code>\n"
    f"├⏱ <b>Uptime:</b> <code>{uptime}</code>\n"
    f"├💻 <b>CPU:</b> <code>{cpu}%</code>\n"
    f"├🎧 <b>VC:</b> {vc_status}\n"
    f"╰🔗 <b>API:</b> <a href='https://t.me/sxyaru'>Aru x API Bots</a>"
    f"</blockquote>"
)

    await msg.edit_text(
    text,
    parse_mode=ParseMode.HTML,
    disable_web_page_preview=True
)
# ----------------- PLAY COMMAND -----------------
@app.on_message(filters.command("play", "."))
async def play(client, message):
    if len(message.command) < 2:
        return await message.reply("ᴋᴏɪ sᴏɴɢ ᴋᴀ ɴᴀᴍᴇ ʙᴀᴛᴀᴏ ɴᴀ ʙᴀʙᴜ 🤭\nExample: `.play mann mera`")

    query = message.text.split(None, 1)[1]
    await message.reply("sᴏɴɢ ᴘʟᴀʏ ʜᴏ ʀᴀʜᴀ ʜᴀɪ ᴛʜᴏᴅᴀ ᴡᴀɪᴛ ᴋɪᴊɪʏᴇ ɴᴀ ʙᴀʙᴜ 💋")

    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://flip-saavn.vercel.app/search?query={query}"
            async with session.get(url) as resp:
                data = await resp.json()
    except Exception as e:
        return await message.reply(f"⚠️ Failed to fetch API: {e}")

    results = data.get("results")
    if not results:
        return await message.reply("ʏᴀ ᴡᴀʟᴀ sᴏɴɢ ᴍᴜᴊʜᴇ ɴᴀʜɪ ᴍɪʟᴀ ʀᴀʜᴀ ʜᴀɪ 🥺")

    song = results[0]

    stream_url = song["download"].get("320kbps") or song["download"].get("160kbps")
    title = song.get("title", "Unknown")
    artist = song.get("artist", "Unknown")
    duration = song.get("duration", "Unknown")

    if not stream_url:
        return await message.reply("❌ No playable link found!")

    try:
        await call.join_group_call(
            message.chat.id,
            AudioPiped(stream_url, HighQualityAudio())
        )
    except:
        try:
            await call.change_stream(
                message.chat.id,
                AudioPiped(stream_url, HighQualityAudio())
            )
        except Exception as e:
            return await message.reply(f"⚠️ Could not play in VC: {e}")

    await message.reply(
        f"🎧 Started Streaming\n\n"
        f"🎵 Title: {title}\n"
        f"👤 Artist: {artist}\n"
        f"⏱ Duration: {duration}\n\n"
        f"🙋 Requested by: {message.from_user.first_name}\n"
        f"🔗 API by: https://t.me/sxyaru"
    )
# ----------------- REPLY TO AUDIO FILE PLAY -----------------
@app.on_message(filters.command("rfplay", "."))
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
            return await message.reply("❌ Reply to an audio file")

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
            f"🎵 Playing replied audio\n"
            f"⏱ Duration: {duration or 'Unknown'}\n"
            f"🎵 Requested by: {message.from_user.first_name}\n"
            f"🔗 Music based on: [Local File]"
        )
        return
    else:
        return await message.reply("❌ Please reply to an audio or voice message to play it.")

@app.on_message(filters.command("stop", "."))
async def stop(client, message):
    try:
        await message.delete()
    except:
        pass
    try:
        await call.leave_group_call(message.chat.id)
        await message.reply("⏹ Stopped")
    except Exception as e:
        await message.reply(f"⚠️ Could not leave VC: {e}")


# ----------------- RUN BOT -------------------
app.start()
call.start()
print("🎵 VC Music Bot Started")
asyncio.get_event_loop().run_forever()
