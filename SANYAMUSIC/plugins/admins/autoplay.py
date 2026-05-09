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
                "🚫 ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴏʀ ꜱᴜᴅᴏᴇʀꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ."
            )

    chat_id = message.chat.id
    args = message.command

    # Agar koi argument nahi diya toh current status batao
    if len(args) == 1:
        status = await is_autoplay(chat_id)
        state = "✅ <b>ON</b>" if status else "❌ <b>OFF</b>"
        return await message.reply_text(
            f"🎵 <b>ᴀᴜᴛᴏᴘʟᴀʏ</b> ɪꜱ ᴄᴜʀʀᴇɴᴛʟʏ {state}\n\n"
            f"ᴜꜱᴇ <code>/autoplay on</code> ᴏʀ <code>/autoplay off</code> ᴛᴏ ᴄʜᴀɴɢᴇ ɪᴛ."
        )

    action = args[1].lower()

    if action == "on":
        if await is_autoplay(chat_id):
            return await message.reply_text(
                "✅ ᴀᴜᴛᴏᴘʟᴀʏ ɪꜱ ᴀʟʀᴇᴀᴅʏ <b>ON</b> ɪɴ ᴛʜɪꜱ ɢʀᴏᴜᴘ !"
            )
        await autoplay_on(chat_id)
        await message.reply_text(
            "🎵 <b>ᴀᴜᴛᴏᴘʟᴀʏ ON</b> ᴇɴᴀʙʟᴇᴅ !\n\n"
            "ɴᴏᴡ ᴛʜᴇ ʙᴏᴛ ᴡɪʟʟ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ᴘʟᴀʏ ᴛʜᴇ ɴᴇxᴛ ꜱᴏɴɢ "
            "ᴡʜᴇɴ ᴛʜᴇ Qᴜᴇᴜᴇ ɪꜱ ᴇᴍᴘᴛʏ. 🔄"
        )

    elif action == "off":
        if not await is_autoplay(chat_id):
            return await message.reply_text(
                "🚫 ᴀᴜᴛᴏᴘʟᴀʏ ɪꜱ ᴀʟʀᴇᴀᴅʏ <b>OFF</b> ɪɴ ᴛʜɪꜱ ɢʀᴏᴜᴘ !"
            )
        await autoplay_off(chat_id)
        await message.reply_text(
            "🎵 <b>ᴀᴜᴛᴏᴘʟᴀʏ OFF</b> ᴅɪꜱᴀʙʟᴇᴅ !\n\n"
            "ɴᴏᴡ ꜱᴏɴɢꜱ ᴍᴜꜱᴛ ʙᴇ ᴘʟᴀʏᴇᴅ ᴍᴀɴᴜᴀʟʟʏ. 🎧"
        )

    else:
        await message.reply_text(
            "<u>❓ <b>ᴄᴏʀʀᴇᴄᴛ ᴜꜱᴀɢᴇ :</b></u>\n\n"
            "<code>/autoplay on</code> ➠ ᴇɴᴀʙʟᴇ ᴀᴜᴛᴏᴘʟᴀʏ\n"
            "<code>/autoplay off</code> ➠ ᴅɪꜱᴀʙʟᴇ ᴀᴜᴛᴏᴘʟᴀʏ\n"
            "<code>/autoplay</code> ➠ ᴄʜᴇᴄᴋ ᴄᴜʀʀᴇɴᴛ ꜱᴛᴀᴛᴜꜱ"
        )
