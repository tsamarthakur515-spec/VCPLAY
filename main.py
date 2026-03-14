

import asyncio
import aiohttp
from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped
from pytgcalls.types.input_stream.quality import HighQualityAudio

# ------------------- CONFIG -------------------
API_ID = 33603336
API_HASH = "c9683a8ec3b886c18219f650fc8ed429"
SESSION = "BQIAvwgAtGpTYJxvUNp8rbi2VNdfNGw-foSWWvDtrWSVnLbKeor1FcHdS2DO3WAwKRUHYT9NyJGuBAIjd9cYSh0JGW7SZjxsMTs0xEWFeU7dxKhHatLzbjhIA8kUOxWj2chH_ags_7fIToe7_LFolcHFbdJhCKAuStVEV4bUXvn43vmALgKi87JQHAId5p9xB7atUNHxMebmAOq6JqABdoBCdtUJC7tEov8GBF0a1C4r8WE8wKoSp5vDjcu7mRIJrUcQ17LMHYY6ACErur_iH3zN2Ny7Nd3VYyIu7Fk7VfeErEZlw-EoNvB89m_e_KYWE3E6ITu-vAtHeTAMG_cDo771-c7GAwAAAAIAgPwVAA"
  # replace with your session
# ----------------------------------------------

app = Client("vcbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION)
call = PyTgCalls(app)

# ----------------- COMMANDS ------------------

@app.on_message(filters.command("play", "."))
async def play(client, message):
    if len(message.command) < 2:
        return await message.reply("❌ Please provide a song name.\nExample: `.play Sabrina Carpenter`")

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

    await message.reply(f"▶️ Playing: {title} — {artist}")

#REPLY TO FILE PLAY
@app.on_message(filters.command("rfplay", ".") & filters.me)
async def rfplay_music(_, message):

    chat_id = message.chat.id

    # REPLY AUDIO
    if message.reply_to_message:

        audio = message.reply_to_message.audio or message.reply_to_message.voice

        if not audio:
            return await message.reply("❌ Reply to an audio file")

        file = await message.reply_to_message.download()

        try:
            await call.change_stream(
                chat_id,
                AudioPiped(file, HighQualityAudio())
            )
        except:
            await call.join_group_call(
                chat_id,
                AudioPiped(file, HighQualityAudio())
            )

        return await message.reply("🎵 Playing replied audio")


    # YOUTUBE / SEARCH
    if len(message.command) < 2:
        return await message.reply("Usage: `.play song name or url`")

    query = message.text.split(None, 1)[1]

    ydl_opts = {
        "format": "bestaudio",
        "quiet": True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)["entries"][0]

    url = info["url"]
    title = info["title"]

    try:
        await call.change_stream(
            chat_id,
            AudioPiped(url, HighQualityAudio())
        )

    except:
        await call.join_group_call(
            chat_id,
            AudioPiped(url, HighQualityAudio())
        )

    await message.reply(f"🎵 Playing: {title}")


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
