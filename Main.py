from pyrogram import Client, filters
from pyrogram.errors import ChatAdminRequired, UserAlreadyParticipant, PeerIdInvalid
from pyrogram.enums import ChatMemberStatus

from AbhiCalls import VoiceEngine, idle, Plugin

# ───────── CONFIG ─────────
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

engine = VoiceEngine(user)

# ───────── ASSISTANT INFO ─────────
async def fetch_assistant():
    global ASSISTANT_ID, ASSISTANT_USERNAME

    me = await user.get_me()
    ASSISTANT_ID = me.id
    ASSISTANT_USERNAME = me.username or "NoUsername"

    print(
        "Assistant loaded\n"
        f"Id: {ASSISTANT_ID}\n"
        f"Username: @{ASSISTANT_USERNAME}"
    )

# ───────── ENSURE ASSISTANT ─────────
async def ensure_assistant(bot, user, chat_id, m):
    try:
        await bot.get_chat_member(chat_id, ASSISTANT_ID)
        return True
    except:
        pass

    try:
        bot_member = await bot.get_chat_member(chat_id, bot.me.id)

        if not bot_member.privileges or not bot_member.privileges.can_invite_users:
            raise ChatAdminRequired

        invite = await bot.export_chat_invite_link(chat_id)
        await user.join_chat(invite)
        return True

    except UserAlreadyParticipant:
        return True

    except (ChatAdminRequired, PeerIdInvalid):
        await m.reply(
            f"❌ **Assistant is not in this group**\n\n"
            f"Give **Invite Users** permission or add manually:\n\n"
            f"👤 @{ASSISTANT_USERNAME}\n"
            f"🆔 `{ASSISTANT_ID}`"
        )
        return False

    except Exception as e:
        await m.reply(f"❌ Failed to add assistant\n\n`{e}`")
        return False

# ───────── PLAY ─────────
@bot.on_message(filters.command("play"))
async def play(_, m):

    ok = await ensure_assistant(bot, user, m.chat.id, m)
    if not ok:
        return

    reply = m.reply_to_message

    # ─── CASE 1: Reply to voice / audio ───
    if reply and (reply.voice or reply.audio):

      #  await m.reply("🎧 Voice / Audio detected, processing...")

        file_path = await reply.download()

        # ✅ FINAL FIX: reply passed to engine
        song, pos = await engine.vc.play_file(
            m.chat.id,
            file_path,
            m.from_user.mention,
            reply=reply
        )

        if not song:
            return await m.reply("❌ Unable to play voice/audio")

        return

    # ─── CASE 2: Normal /play text ───
    if len(m.command) < 2:
        return await m.reply(
            "❌ Usage:\n"
            "/play <song name | youtube link>\n"
            "or reply to a voice/audio file"
        )

    query = m.text.split(None, 1)[1]

    song, pos = await engine.vc.play(
        m.chat.id,
        query,
        m.from_user.mention
    )

    if not song:
        await m.reply("❌ Unable to play song")

# ───────── PLAY FORCE ─────────
@bot.on_message(filters.command("playforce"))
async def playforce(_, m):

    ok = await ensure_assistant(bot, user, m.chat.id, m)
    if not ok:
        return

    reply = m.reply_to_message

    # 🔥 Force stop current playback
    await engine.vc.stop(m.chat.id)

    # ─── CASE 1: Reply to voice / audio ───
    if reply and (reply.voice or reply.audio):

        file_path = await reply.download()

        song, pos = await engine.vc.play_file(
            m.chat.id,
            file_path,
            m.from_user.mention,
            reply=reply
        )

        if not song:
            return await m.reply("❌ Unable to force play voice/audio")

        return

    # ─── CASE 2: Force play normal song ───
    if len(m.command) < 2:
        return await m.reply(
            "❌ Usage:\n"
            "/playforce <song name | youtube link>\n"
            "or reply to a voice/audio file"
        )

    query = m.text.split(None, 1)[1]
    song, pos = await engine.vc.play(
        m.chat.id,
        query,
        m.from_user.mention
    )

    if not song:
        await m.reply("❌ Unable to force play song")

# ───────── SKIP ─────────
@bot.on_message(filters.command("skip"))
async def skip(_, m):
    await engine.vc.skip(m.chat.id)
    await m.reply("⏭ Skipped")

# ───────── STOP ─────────
@bot.on_message(filters.command("end"))
async def stop(_, m):
    await engine.vc.stop(m.chat.id)
    await m.reply("⏹ Stopped and queue cleared")

# ───────── PAUSE ─────────
@bot.on_message(filters.command("pause"))
async def pause(_, m):
    await engine.vc.pause(m.chat.id)
    await m.reply("⏸ Paused")

# ───────── RESUME ─────────
@bot.on_message(filters.command("resume"))
async def resume(_, m):
    await engine.vc.resume(m.chat.id)
    await m.reply("▶️ Resumed")

# ───────── PREVIOUS ─────────
@bot.on_message(filters.command("previous"))
async def previous(_, m):
    song = await engine.vc.previous(m.chat.id)
    if not song:
        await m.reply("❌ No previous song")

# ───────── QUEUE ─────────
@bot.on_message(filters.command("queue"))
async def queue(_, m):
    q = engine.vc.player.queues.get(m.chat.id)

    if not q or not q.items:
        return await m.reply("📭 Queue is empty")

    text = "📜 **Queue list**\n\n"
    for i, s in enumerate(q.items, 1):
        text += f"{i}. {s.title} ({s.duration_sec}s)\n"

    await m.reply(text)

# ───────── MAIN ─────────
async def main():
    await bot.start()
    await user.start()
    await engine.start()
    await fetch_assistant()

    engine.vc.load_plugin(Plugin(bot))
    await idle()

bot.run(main())
