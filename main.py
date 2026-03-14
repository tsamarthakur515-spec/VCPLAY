import time
import psutil
from datetime import datetime, timedelta
import asyncio
import aiohttp
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

# ----------------- COMMANDS ------------------

#PINH COMMAND


@app.on_message(filters.command("ping", "."))
async def ping(client, message):
    start = time.monotonic()

    # Loading bar animation
    loading = await message.reply("0% ▒▒▒▒▒▒▒▒▒▒")
    stages = [
        ("20% ███▒▒▒▒▒▒▒ sᴀᴍᴀʀ", 0.08),
        ("40% █████▒▒▒▒ sᴀᴍᴀʀ ɪs", 0.08),
        ("60% ███████▒▒ sᴀᴍᴀʀ ᴄᴏᴍᴇ", 0.09),
        ("80% █████████▒ sᴀᴍᴀʀ", 0.09),
        ("100% ██████████ ᴄᴏᴍɪɴɢ", 0.10),
    ]

    for text, delay in stages:
        await asyncio.sleep(delay)
        await loading.edit(text)

    # Calculate ping and uptime
    end = time.monotonic()
    ping_ms = round((end - start) * 1000, 1)
    uptime_sec = int((datetime.now() - BOT_START_TIME).total_seconds())
    uptime = str(timedelta(seconds=uptime_sec)).split('.')[0]

    # CPU usage
    cpu_percent = psutil.cpu_percent(interval=0.5)

    # PyTgCalls status
    try:
        pytgcalls_status = "🟢 Active" if call.is_connected else "🔴 Not active"
    except:
        pytgcalls_status = "⚠️ Unknown"

    # Bot user info
    me = await client.get_me()
    fullname = f"{me.first_name or ''} {me.last_name or ''}".strip() or me.username or "User"

    # Final formatted message
    final_msg = (
        f"❏ ╰☞ 😈 {fullname} 😈\n"
        f"├• ╰☞ 𝐒ᴘᴇᴇᴅ: {ping_ms} ms\n"
        f"├• ╰☞ 𝐔ᴘᴛɪᴍᴇ: {uptime}\n"
        f"├• ╰☞ 💻 CPU: {cpu_percent}%\n"
        f"├• ╰☞ 🎵 PyTgCalls: {pytgcalls_status}\n"
        f"└• ╰☞ API by: [JioSaavn](https://t.me/sxyaru)"
    )

    await loading.edit(final_msg)

# ----------------- PLAY COMMAND -----------------
@app.on_message(filters.command("play", "."))
async def play(client, message):
    if len(message.command) < 2:
        return await message.reply(
            "❌ Please provide a song name.\nExample: `.play Sabrina Carpenter`"
        )

    query = message.text.split(None, 1)[1]
    await message.reply("🔎 Searching Saavn...")

    # Fetch song from Flip-Saavn API
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://flip-saavn.vercel.app/search?query={query}"
            async with session.get(url) as resp:
                data = await resp.json()
    except Exception as e:
        return await message.reply(f"⚠️ Failed to fetch API: {e}")

    results = data.get("results")
    if not results:
        return await message.reply("❌ No results found!")

    song = results[0]
    stream_url = song["download"].get("320kbps") or song["download"].get("160kbps")
    title = song.get("title")
    artist = song.get("artist")
    duration = song.get("duration")  # duration from API if available

    if not stream_url:
        return await message.reply("❌ No playable link found!")

    # Join or change VC stream
    try:
        await call.join_group_call(
            message.chat.id,
            AudioPiped(stream_url, HighQualityAudio())
        )
    except Exception as e:
        try:
            await call.change_stream(
                message.chat.id,
                AudioPiped(stream_url, HighQualityAudio())
            )
        except Exception as e2:
            return await message.reply(f"⚠️ Could not play in VC: {e2}")

    await message.reply(
        f"▶️ Playing: {title} — {artist}\n"
        f"⏱ Duration: {duration or 'Unknown'}\n"
        f"🎵 Requested by: {message.from_user.first_name}\n"
        f"🔗 Music based on: [JioSaavn](https://t.me/sxyaru)"
    )


# ----------------- REPLY TO AUDIO FILE PLAY -----------------
@app.on_message(filters.command("rfplay", "."))
async def rfplay_music(_, message):
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
        await call.leave_group_call(message.chat.id)
        await message.reply("⏹ Stopped")
    except Exception as e:
        await message.reply(f"⚠️ Could not leave VC: {e}")


# ----------------- RUN BOT -------------------
app.start()
call.start()
print("🎵 VC Music Bot Started")
asyncio.get_event_loop().run_forever()
