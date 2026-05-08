# -----------------------------------------------
# 🔸 SanyaMusic Project — Autoplay Plugin
# -----------------------------------------------
from pyrogram import filters
from pyrogram.types import Message

from SANYAMUSIC import app
from SANYAMUSIC.misc import SUDOERS
from config import BANNED_USERS
from SANYAMUSIC.utils.admin_check import admin_check
from SANYAMUSIC.utils.database import autoplay_off, autoplay_on, is_autoplay
from SANYAMUSIC.utils.decorators.language import language


@app.on_message(filters.command(["autoplay"]) & filters.group & ~BANNED_USERS)
@language
async def autoplay_command(client, message: Message, _):
    # Admin ya SUDOERS check
    if message.from_user.id not in SUDOERS:
        if not await admin_check(message):
            return await message.reply_text(
                "❌ Ye command sirf admins ya sudoers ke liye hai."
            )

    chat_id = message.chat.id
    args = message.command

    # Agar koi argument nahi diya toh current status batao
    if len(args) == 1:
        status = await is_autoplay(chat_id)
        state = "✅ <b>ON</b>" if status else "❌ <b>OFF</b>"
        return await message.reply_text(
            f"🎵 <b>Autoplay</b> is currently {state}\n\n"
            f"Use <code>/autoplay on</code> or <code>/autoplay off</code> to change."
        )

    action = args[1].lower()

    if action == "on":
        if await is_autoplay(chat_id):
            return await message.reply_text(
                "✅ Autoplay pehle se <b>ON</b> hai is group mein!"
            )
        await autoplay_on(chat_id)
        await message.reply_text(
            "🎵 <b>Autoplay ON</b> kar diya!\n\n"
            "Ab jab bhi koi song khatam hoga aur queue empty hogi, "
            "same artist ka next song automatically play hoga. 🔄"
        )

    elif action == "off":
        if not await is_autoplay(chat_id):
            return await message.reply_text(
                "❌ Autoplay pehle se <b>OFF</b> hai is group mein!"
            )
        await autoplay_off(chat_id)
        await message.reply_text(
            "🎵 <b>Autoplay OFF</b> kar diya!\n\n"
            "Ab songs manually play karne padenge. 🎧"
        )

    else:
        await message.reply_text(
            "❓ Sahi use karo:\n"
            "<code>/autoplay on</code> — Autoplay ON karo\n"
            "<code>/autoplay off</code> — Autoplay OFF karo\n"
            "<code>/autoplay</code> — Current status dekho"
        )
