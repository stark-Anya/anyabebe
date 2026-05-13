
import asyncio
from pyrogram import filters, enums
from pyrogram.errors import PeerIdInvalid, RPCError, FloodWait
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from SANYAMUSIC import app


def get_full_name(user):
    return f"{user.first_name} {user.last_name}" if user.last_name else user.first_name


def get_last_seen(status):
    if isinstance(status, str):
        status = status.replace("UserStatus.", "").lower()
    elif isinstance(status, enums.UserStatus):
        status = status.name.lower()

    return {
        "online": "☑️ ᴏɴʟɪɴᴇ",
        "offline": "❄️ ᴏғғʟɪɴᴇ",
        "recently": "⏱ ʀᴇᴄᴇɴᴛʟʏ",
        "last_week": "🗓 ʟᴀsᴛ ᴡᴇᴇᴋ",
        "last_month": "📆 ʟᴀsᴛ ᴍᴏɴᴛʜ",
        "long_ago": "😴 ʟᴏɴɢ ᴛɪᴍᴇ ᴀɢᴏ"
    }.get(status, "❓ ᴜɴᴋɴᴏᴡɴ")


@app.on_message(filters.command(["info", "userinfo", "whois"]))
async def whois_handler(_, message: Message):
    try:
        if message.reply_to_message:
            user = message.reply_to_message.from_user
        elif len(message.command) > 1:
            user = await app.get_users(message.command[1])
        else:
            user = message.from_user

        loading = await message.reply("🔍 <b>ɢᴀᴛʜᴇʀɪɴɢ ᴜsᴇʀ ɪɴғᴏ...</b>")
        await asyncio.sleep(0.5)

        chat_user = await app.get_chat(user.id)

        name = get_full_name(user)
        username = f"@{user.username}" if user.username else "ɴ/ᴀ"
        bio = chat_user.bio or "ɴᴏ ʙɪᴏ"
        dc_id = getattr(user, "dc_id", "ɴ/ᴀ")
        last_seen = get_last_seen(user.status)
        lang = getattr(user, "language_code", "ɴ/ᴀ")

        text = (
            f"<blockquote>👤 <b>ᴜsᴇʀ ɪɴғᴏ</b></blockquote>\n"
            f"<blockquote>"
            f"❖ <b>ᴜsᴇʀ ɪᴅ:</b> <code>{user.id}</code>\n"
            f"❖ <b>ɴᴀᴍᴇ:</b> {name}\n"
            f"❖ <b>ᴜsᴇʀɴᴀᴍᴇ:</b> {username}\n"
            f"❖ <b>ʟᴀsᴛ sᴇᴇɴ:</b> {last_seen}\n"
            f"❖ <b>ᴅᴀᴛᴀᴄᴇɴᴛᴇʀ ɪᴅ:</b> {dc_id}\n"
            f"❖ <b>ʟᴀɴɢᴜᴀɢᴇ:</b> {lang}"
            f"</blockquote>\n"
            f"<blockquote>"
            f"✬ <b>ᴠᴇʀɪғɪᴇᴅ:</b> {'ʏᴇs ✅' if user.is_verified else 'ɴᴏ 🥀'}\n"
            f"✬ <b>ᴘʀᴇᴍɪᴜᴍ:</b> {'ʏᴇs ☑️' if user.is_premium else 'ɴᴏ 🥀'}\n"
            f"✬ <b>ʙᴏᴛ:</b> {'ʏᴇs 🤖' if user.is_bot else 'ɴᴏ 👤'}\n"
            f"✬ <b>sᴄᴀᴍ ᴀᴄᴄᴏᴜɴᴛ:</b> {'ʏᴇs ⚠️' if getattr(user, 'is_scam', False) else 'ɴᴏ ☑️'}\n"
            f"✬ <b>ғᴀᴋᴇ ᴀᴄᴄᴏᴜɴᴛ:</b> {'ʏᴇs 🎭' if getattr(user, 'is_fake', False) else 'ɴᴏ ☑️'}\n"
            f"✬ <b>ᴘʀᴏғɪʟᴇ ᴘɪᴄᴛᴜʀᴇ:</b> {'ʏᴇs 🌠' if user.photo else 'ɴᴏ 🥀'}"
            f"</blockquote>\n"
            f"<blockquote>"
            f"❖ <b>ʙɪᴏ:</b> <code>{bio}</code>"
            f"</blockquote>\n"
            f"<blockquote>❖ 𝐌ᴧᴅє ʙʏ » <a href=\"https://t.me/Anya_Bots\">˹𝐀ɴʏᴀ ꭙ 𝐁ᴏᴛ𝐬˼ </blockquote>"
        )

        profile_url = f"https://t.me/{user.username}" if user.username else f"tg://openmessage?user_id={user.id}"
        buttons = InlineKeyboardMarkup([[
            InlineKeyboardButton("👤 ᴠɪᴇᴡ ᴘʀᴏғɪʟᴇ", url=profile_url)
        ]])

        await app.edit_message_text(
            chat_id=message.chat.id,
            message_id=loading.id,
            text=text,
            parse_mode=enums.ParseMode.HTML,
            reply_markup=buttons
        )

    except PeerIdInvalid:
        await message.reply("🥀 ɪ ᴄᴏᴜʟᴅɴ'ᴛ ꜰɪɴᴅ ᴛʜᴀᴛ ᴜsᴇʀ.")
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await whois_handler(_, message)
    except RPCError as e:
        await message.reply(f"⚠️ ʀᴘᴄ ᴇʀʀᴏʀ:\n<code>{e}</code>")
    except Exception as e:
        await message.reply(f"🥀 ᴇʀʀᴏʀ:\n<code>{e}</code>")
