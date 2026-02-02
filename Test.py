import asyncio
from pyrogram import Client, filters
from pytgcalls import PyTgCalls, idle
from pytgcalls.types import MediaStream, AudioQuality, VideoQuality

# ───── CONFIG ─────
API_ID = 35362137
API_HASH = "c3c3e167ea09bc85369ca2fa3c1be790"
BOT_TOKEN = "8360461005:AAH7uHgra-bYu1I3WOSgpn1VMrFt1Wi1fcw"
SESSION_STRING = "BQIblVkAH2XJrDMiKPGUoIfk4Pr5x0rGPb-mqrs6J4IPMZpSR-QJ6Df3u3iAIhaoZPDWDAfVBaC0PX6GlGdLGobcty7lskWfLDa9PplwsBvPlCFkPaJNB2U6EgdJZptzxrLidISSyqWLVawbpBRZvXWnNZn-qIvOXx-EX1p2koYiCvAOYq3NTSkleVvpnv1Q0Tuo7G2JdU5D7ayhuPXz6tjc6DAIracshRb2vh_KXmFar4mPxXP_VEDsTbtp4bioIsE1Dkh106Uw7PAFTM2LmKTBdLn4ys6OuqH5GSa-TTWgCl_k3G2ScrLOEaovYXvRkAGg3IDnGe23_WOfDV2cvbngcuPRvgAAAAFtutilAA"

ASSISTANT_ID = None
ASSISTANT_USERNAME = None

# 🤖 Bot
bot = Client(
    "music_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# 👤 Userbot (Assistant / VC)
user = Client(
    "music_user",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)
call = PyTgCalls(user)

# ───── QUALITY MAP ─────
QUALITY = {
    "UHD_4K": VideoQuality.UHD_4K,
    "QHD_2K": VideoQuality.QHD_2K,
    "FHD_1080p": VideoQuality.FHD_1080p,
    "HD_720p": VideoQuality.HD_720p,
    "SD_480p": VideoQuality.SD_480p,
    "SD_360p": VideoQuality.SD_360p,
}

# ───── PLAY VIDEO ─────
async def play_video(chat_id, file, quality="SD_480p"):
    quality = quality.upper()
    stream = MediaStream(
        media_path=file,
        audio_parameters=AudioQuality.MEDIUM,
        video_parameters=QUALITY.get(quality, VideoQuality.SD_480p),
    )

    try:
        await call.play(chat_id, stream)
    except:
        await call.change_stream(chat_id, stream)

# ───── COMMANDS ─────
@bot.on_message(filters.command("play") & filters.group)
async def play(_, m):
    if not m.reply_to_message:
        return await m.reply("Reply to **video/audio file**")

    msg = m.reply_to_message

    if not (msg.video or msg.audio or msg.voice):
        return await m.reply("Unsupported file")

    file = await msg.download()
    await play_video(m.chat.id, file, "HD_720p")

    await m.reply("▶️ **Playing in VC (Assistant)**")

@bot.on_message(filters.command("pause") & filters.group)
async def pause(_, m):
    await call.pause_stream(m.chat.id)
    await m.reply("⏸ Paused")

@bot.on_message(filters.command("resume") & filters.group)
async def resume(_, m):
    await call.resume_stream(m.chat.id)
    await m.reply("▶️ Resumed")

@bot.on_message(filters.command("stop") & filters.group)
async def stop(_, m):
    await call.leave_group_call(m.chat.id)
    await m.reply("⏹ Stopped")

# ───── START ─────
async def main():
    await bot.start()
    await user.start()
    await call.start()
    print("Bot + Assistant Started")
    await idle()
    

asyncio.run(main())
  
