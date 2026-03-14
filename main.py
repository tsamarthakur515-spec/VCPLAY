import time
import psutil
from urllib.parse import quote
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
BOT_START_TIME = datetime.now()
# ----------------- COMMANDS ------------------

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
        f"╭─❖ **{name} Bot Status**\n"
        f"├⚡ **Ping:** `{ping} ms`\n"
        f"├⏱ **Uptime:** `{uptime}`\n"
        f"├💻 **CPU:** `{cpu}%`\n"
        f"├🎧 **VC:** {vc_status}\n"
        f"╰🔗 **API:** [Aru x API Bots](https://t.me/sxyaru)"
    )

    await msg.edit(text, disable_web_page_preview=True)

    await loading.edit(final_msg, parse_mode="html")
# ----------------- PLAY COMMAND -----------------

@app.on_message(filters.command("play", "."))
async def play(client, message):
    try:
        await message.delete()
    except:
        pass
    if len(message.command) < 2:
        return await message.reply_text(
            "```ɢɪᴠᴇ ǫᴜᴇʀʏ ᴛᴏ sᴇᴀʀᴄʜ ʙᴀʙᴇ\n.play <song name>```",
            quote=True
        )

    query = message.text.split(None, 1)[1]

    searching = await message.reply_text(
        "```🥀 sᴇᴀʀᴄʜɪɴɢ ʏᴏᴜʀ ǫᴜᴇʀʏ...```",
        quote=True
    )

    query_encoded = quote(query)

    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://flip-saavn.vercel.app/search?query={query_encoded}"
            async with session.get(url) as resp:
                data = await resp.json()
    except Exception as e:
        return await searching.edit_text(
            f"⚠️ API Error:\n{e}"
        )

    results = data.get("results")
    if not results:
        return await searching.edit_text("❌ No results found!")

    song = results[0]

    stream_url = (
        song.get("download", {}).get("320kbps")
        or song.get("download", {}).get("160kbps")
        or song.get("download", {}).get("128kbps")
    )

    title = song.get("title", "Unknown")
    artist = song.get("artist", "Unknown")
    duration = song.get("duration", "Unknown")

    if not stream_url:
        return await searching.edit_text("❌ No playable link found!")

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
            return await searching.edit_text(
                f"⚠️ Could not play in VC:\n{e}"
            )

    await searching.edit_text(
        f"▶️ <b>ᴘʟᴀʏɪɴɢ:</b> {title} — {artist}\n"
        f"⏱ <b>ᴅᴜʀᴀᴛɪᴏɴ:</b> {duration}\n"
        f"🎵 <b>ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ:</b> {message.from_user.first_name}\n"
        f"🔗 <b>ᴍᴜsɪᴄ ʙᴀsᴇᴅ ᴏɴ:</b> "
        f"<a href='https://t.me/sxyaru'>ᴀʀᴜ x ᴀᴘɪ ʙᴏᴛs</a>",
        parse_mode="html"
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
