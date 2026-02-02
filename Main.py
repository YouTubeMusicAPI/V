from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from Test import user, bot

app = PyTgCalls(user)

@bot.on_message(filters.command("play"))
async def play(_, m)
    reply = m.reply_to_message

    # ─── CASE 1: Reply to voice / audio ───
    if reply and (reply.voice or reply.audio):

        await m.reply("🎧 Voice / Audio detected, processing...")

        # Download telegram file
        file_path = await reply.download()

        await app.play(
            m.chat.id,
            file_path,
        )

      
