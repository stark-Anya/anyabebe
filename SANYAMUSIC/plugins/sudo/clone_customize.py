# -----------------------------------------------
# SanyaMusic — Clone Customize Plugin
# Commands: /addstart, /addsupport, /addupdate, /ownerlink
# Only clone owner can use these
# -----------------------------------------------
from pyrogram import Client, filters, enums
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)

from SANYAMUSIC import app
from SANYAMUSIC.utils.clone_db import (
    get_clone_links,
    get_clone_owner_link,
    get_clone_start,
    is_clone_owner,
    set_clone_owner_link,
    set_clone_start_photo,
    set_clone_start_text,
    set_clone_support,
    set_clone_update,
)
import config


def _get_bot_id(client) -> int:
    try:
        return client.me.id
    except Exception:
        return app.me.id


async def _is_authorized(client, message: Message) -> bool:
    """Main owner or clone owner — both allowed."""
    user_id = message.from_user.id
    if user_id == config.OWNER_ID:
        return True
    bot_id = _get_bot_id(client)
    return await is_clone_owner(bot_id, user_id)


async def _is_authorized_cb(client, callback: CallbackQuery) -> bool:
    user_id = callback.from_user.id
    if user_id == config.OWNER_ID:
        return True
    bot_id = _get_bot_id(client)
    return await is_clone_owner(bot_id, user_id)


# ── /addstart ───────────────────────────────────────────────────────
@app.on_message(filters.command("addstart") & filters.private)
async def add_start_message(client, message: Message):
    if not await _is_authorized(client, message):
        return await message.reply_text(
            "🚫 ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ɪꜱ ᴏɴʟʏ ꜰᴏʀ ᴛʜᴇ <b>ᴄʟᴏɴᴇ ᴏᴡɴᴇʀ</b>.",
            parse_mode=enums.ParseMode.HTML,
        )

    bot_id = _get_bot_id(client)
    reply = message.reply_to_message

    if reply:
        if reply.photo:
            file_id = reply.photo.file_id
            await set_clone_start_photo(bot_id, file_id)
            if reply.caption:
                await set_clone_start_text(bot_id, reply.caption.html)
                return await message.reply_text(
                    "✅ <b>ꜱᴛᴀʀᴛ ᴍᴇꜱꜱᴀɢᴇ ᴜᴘᴅᴀᴛᴇᴅ !</b>\n\n"
                    "📸 ᴘʜᴏᴛᴏ + ᴛᴇxᴛ ʙᴏᴛʜ ꜱᴀᴠᴇᴅ.\n"
                    "<i>ꜱᴇɴᴅ /start ᴛᴏ ᴘʀᴇᴠɪᴇᴡ.</i>",
                    parse_mode=enums.ParseMode.HTML,
                )
            return await message.reply_text(
                "✅ <b>ꜱᴛᴀʀᴛ ᴘʜᴏᴛᴏ ᴜᴘᴅᴀᴛᴇᴅ !</b>\n\n"
                "<i>ᴛᴏ ᴀᴅᴅ ᴛᴇxᴛ, ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴘʜᴏᴛᴏ ᴡɪᴛʜ ᴄᴀᴘᴛɪᴏɴ ᴀɴᴅ ᴜꜱᴇ /addstart.</i>",
                parse_mode=enums.ParseMode.HTML,
            )
        elif reply.text:
            await set_clone_start_text(bot_id, reply.text.html)
            return await message.reply_text(
                "✅ <b>Start message updated!</b>\n\n"
                f"📝 <b>Preview:</b>\n\n{reply.text.html}",
                parse_mode=enums.ParseMode.HTML,
            )

    elif len(message.command) > 1:
        text = message.text.split(None, 1)[1]
        await set_clone_start_text(bot_id, text)
        return await message.reply_text(
            "✅ <b>Start message updated!</b>\n\n"
            f"📝 <b>Preview:</b>\n\n{text}",
            parse_mode=enums.ParseMode.HTML,
        )

    return await message.reply_text(
        "❓ <b>ʜᴏᴡ ᴛᴏ ᴜꜱᴇ /addstart :</b>\n\n"
        "1. ʀᴇᴘʟʏ ᴛᴏ ᴀɴʏ ᴛᴇxᴛ ᴍᴇꜱꜱᴀɢᴇ ➠ <code>/addstart</code>\n"
        "2. ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴘʜᴏᴛᴏ (ᴡɪᴛʜ ᴏʀ ᴡɪᴛʜᴏᴜᴛ ᴄᴀᴘᴛɪᴏɴ) ➠ <code>/addstart</code>\n"
        "3. <code>/addstart Your custom message here</code>\n\n"
        "<b>ʜᴛᴍʟ ꜰᴏʀᴍᴀᴛᴛɪɴɢ ꜱᴜᴘᴘᴏʀᴛᴇᴅ :</b>\n"
        "<code>&lt;b&gt;Bold&lt;/b&gt;</code>\n"
        "<code>&lt;i&gt;Italic&lt;/i&gt;</code>\n"
        "<code>&lt;a href='link'&gt;Text&lt;/a&gt;</code>\n\n"
        "✅ ɴᴇᴡ ʟɪɴᴇꜱ ᴀɴᴅ ꜱᴘᴀᴄɪɴɢ ᴀʀᴇ ᴘʀᴇꜱᴇʀᴠᴇᴅ.",
        parse_mode=enums.ParseMode.HTML,
    )

# ── /addsupport ─────────────────────────────────────────────────────
@app.on_message(filters.command("addsupport") & filters.private)
async def add_support_link(client, message: Message):
    if not await _is_authorized(client, message):
        return await message.reply_text(
            "❌ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ɪꜱ ᴏɴʟʏ ꜰᴏʀ ᴛʜᴇ <b>ᴄʟᴏɴᴇ ᴏᴡɴᴇʀ</b>.",
            parse_mode=enums.ParseMode.HTML,
        )

    if len(message.command) < 2:
        return await message.reply_text(
            "❓ <b>ᴜꜱᴀɢᴇ :</b> <code>/addsupport https://t.me/yourgroup</code>",
            parse_mode=enums.ParseMode.HTML,
        )

    link = message.command[1]
    if not link.startswith("http"):
        return await message.reply_text(
            "❌ ɪɴᴠᴀʟɪᴅ ʟɪɴᴋ. ɪᴛ ᴍᴜꜱᴛ ꜱᴛᴀʀᴛ ᴡɪᴛʜ <code>https://</code>",
            parse_mode=enums.ParseMode.HTML,
        )

    bot_id = _get_bot_id(client)
    await set_clone_support(bot_id, link)
    await message.reply_text(
        f"✅ <b>ꜱᴜᴘᴘᴏʀᴛ ʟɪɴᴋ ᴜᴘᴅᴀᴛᴇᴅ !</b>\n\n"
        f"🔗 <code>{link}</code>\n\n"
        f"ᴀ <b>🆘 ꜱᴜᴘᴘᴏʀᴛ</b> ʙᴜᴛᴛᴏɴ ᴡɪʟʟ ɴᴏᴡ ᴀᴘᴘᴇᴀʀ ᴏɴ ᴛʜᴇ ꜱᴛᴀʀᴛ ᴍᴇꜱꜱᴀɢᴇ.",
        parse_mode=enums.ParseMode.HTML,
    )


# ── /addupdate ──────────────────────────────────────────────────────
@app.on_message(filters.command("addupdate") & filters.private)
async def add_update_link(client, message: Message):
    if not await _is_authorized(client, message):
        return await message.reply_text(
            "❌ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ɪꜱ ᴏɴʟʏ ꜰᴏʀ ᴛʜᴇ <b>ᴄʟᴏɴᴇ ᴏᴡɴᴇʀ</b>.",
            parse_mode=enums.ParseMode.HTML,
        )

    if len(message.command) < 2:
        return await message.reply_text(
            "❓ <b>ᴜꜱᴀɢᴇ :</b> <code>/addupdate https://t.me/yourchannel</code>",
            parse_mode=enums.ParseMode.HTML,
        )

    link = message.command[1]
    if not link.startswith("http"):
        return await message.reply_text(
            "❌ ɪɴᴠᴀʟɪᴅ ʟɪɴᴋ. ɪᴛ ᴍᴜꜱᴛ ꜱᴛᴀʀᴛ ᴡɪᴛʜ <code>https://</code>",
            parse_mode=enums.ParseMode.HTML,
        )

    bot_id = _get_bot_id(client)
    await set_clone_update(bot_id, link)
    await message.reply_text(
        f"✅ <b>ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ ʟɪɴᴋ ᴜᴘᴅᴀᴛᴇᴅ !</b>\n\n"
        f"🔗 <code>{link}</code>\n\n"
        f"ᴀ <b>📢 ᴜᴘᴅᴀᴛᴇꜱ</b> ʙᴜᴛᴛᴏɴ ᴡɪʟʟ ɴᴏᴡ ᴀᴘᴘᴇᴀʀ ᴏɴ ᴛʜᴇ ꜱᴛᴀʀᴛ ᴍᴇꜱꜱᴀɢᴇ.",
        parse_mode=enums.ParseMode.HTML,
    )


# ── /ownerlink ──────────────────────────────────────────────────────
@app.on_message(filters.command("ownerlink") & filters.private)
async def set_owner_link(client, message: Message):
    if not await _is_authorized(client, message):
        return await message.reply_text(
            "❌ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ɪꜱ ᴏɴʟʏ ꜰᴏʀ ᴛʜᴇ <b>ᴄʟᴏɴᴇ ᴏᴡɴᴇʀ</b>.",
            parse_mode=enums.ParseMode.HTML,
        )

    if len(message.command) < 2:
        return await message.reply_text(
            "❓ <b>ᴜꜱᴀɢᴇ :</b> <code>/ownerlink https://t.me/yourprofile</code>\n\n"
            "ɪᴛ ꜱᴇᴛꜱ ᴛʜᴇ ᴏᴡɴᴇʀ ʙᴜᴛᴛᴏɴ ʟɪɴᴋ ꜱʜᴏᴡɴ ᴏɴ ᴛʜᴇ ꜱᴛᴀʀᴛ ᴍᴇꜱꜱᴀɢᴇ.",
            parse_mode=enums.ParseMode.HTML,
        )

    link = message.command[1]
    if not link.startswith("http"):
        return await message.reply_text(
            "❌ ɪɴᴠᴀʟɪᴅ ʟɪɴᴋ. ɪᴛ ᴍᴜꜱᴛ ꜱᴛᴀʀᴛ ᴡɪᴛʜ <code>https://</code>",
            parse_mode=enums.ParseMode.HTML,
        )

    bot_id = _get_bot_id(client)
    await set_clone_owner_link(bot_id, link)
    await message.reply_text(
        f"✅ <b>ᴏᴡɴᴇʀ ʟɪɴᴋ ᴜᴘᴅᴀᴛᴇᴅ !</b>\n\n"
        f"🔗 <code>{link}</code>\n\n"
        f"ᴛʜᴇ ᴏᴡɴᴇʀ ʙᴜᴛᴛᴏɴ ᴏɴ ᴛʜᴇ ꜱᴛᴀʀᴛ ᴍᴇꜱꜱᴀɢᴇ ᴡɪʟʟ ɴᴏᴡ ᴘᴏɪɴᴛ ᴛᴏ ʏᴏᴜʀ ᴘʀᴏꜰɪʟᴇ.",
        parse_mode=enums.ParseMode.HTML,
    )


# ── /mysettings ─────────────────────────────────────────────────────
@app.on_message(filters.command("mysettings") & filters.private)
async def my_settings(client, message: Message):
    if not await _is_authorized(client, message):
        return await message.reply_text(
            "❌ This command is only for the <b>clone owner</b>.",
            parse_mode=enums.ParseMode.HTML,
        )

    bot_id = _get_bot_id(client)
    start_data = await get_clone_start(bot_id)
    links = await get_clone_links(bot_id)
    owner_link = await get_clone_owner_link(bot_id)

    photo_status = "✅ Custom set" if start_data.get("photo") else "❌ Default (main bot photo)"
    text_status = "✅ Custom set" if start_data.get("text") else "❌ Default (main bot text)"
    support_status = f"✅ {links['support']}" if links.get("support") else "❌ Default"
    update_status = f"✅ {links['update']}" if links.get("update") else "❌ Default"
    owner_status = f"✅ {owner_link}" if owner_link else "❌ Default"

    await message.reply_text(
        "⚙️ <b>ʏᴏᴜʀ ʙᴏᴛ ꜱᴇᴛᴛɪɴɢꜱ</b>\n\n"
        f"📸 <b>ꜱᴛᴀʀᴛ ᴘʜᴏᴛᴏ :</b> {photo_status}\n"
        f"📝 <b>ꜱᴛᴀʀᴛ ᴛᴇxᴛ :</b> {text_status}\n"
        f"🆘 <b>ꜱᴜᴘᴘᴏʀᴛ ʟɪɴᴋ :</b> {support_status}\n"
        f"📢 <b>ᴜᴘᴅᴀᴛᴇ ʟɪɴᴋ :</b> {update_status}\n"
        f"👤 <b>ᴏᴡɴᴇʀ ʟɪɴᴋ :</b> {owner_status}\n\n"
        "<b>ᴀᴠᴀɪʟᴀʙʟᴇ ᴄᴏᴍᴍᴀɴᴅꜱ :</b>\n"
        "• <code>/addstart</code> ➠ ᴄʜᴀɴɢᴇ ꜱᴛᴀʀᴛ ᴍᴇꜱꜱᴀɢᴇ\n"
        "• <code>/addsupport link</code> ➠ ꜱᴇᴛ ꜱᴜᴘᴘᴏʀᴛ ʙᴜᴛᴛᴏɴ\n"
        "• <code>/addupdate link</code> ➠ ꜱᴇᴛ ᴜᴘᴅᴀᴛᴇ ʙᴜᴛᴛᴏɴ\n"
        "• <code>/ownerlink link</code> ➠ ꜱᴇᴛ ᴏᴡɴᴇʀ ʙᴜᴛᴛᴏɴ\n"
        "• <code>/mysettings</code> ➠ ꜱʜᴏᴡ ᴛʜɪꜱ ᴘᴀɴᴇʟ\n\n"
        "<i>ɪꜰ ɴᴏᴛ ᴄᴜꜱᴛᴏᴍɪᴢᴇᴅ, ᴅᴇꜰᴀᴜʟᴛ ʙᴏᴛ ꜱᴇᴛᴛɪɴɢꜱ ᴡɪʟʟ ʙᴇ ᴜꜱᴇᴅ.</i>",
        parse_mode=enums.ParseMode.HTML,
    )


# ── Callback: Customise panel ────────────────────────────────────────
@app.on_callback_query(filters.regex("clone_customize_panel"))
async def clone_customize_callback(client, callback: CallbackQuery):
    if not await _is_authorized_cb(client, callback):
        return await callback.answer("❌ Only for clone owner!", show_alert=True)

    await callback.answer()
    await callback.edit_message_text(
        "⚙️ <b>ᴄᴜꜱᴛᴏᴍɪꜱᴇ ʏᴏᴜʀ ʙᴏᴛ</b>\n\n"
        "ᴜꜱᴇ ᴛʜᴇꜱᴇ ᴄᴏᴍᴍᴀɴᴅꜱ ɪɴ ᴍʏ PM ᴛᴏ ᴘᴇʀꜱᴏɴᴀʟɪᴢᴇ ʏᴏᴜʀ ʙᴏᴛ :\n\n"
        "📝 <b>/addstart</b>\n"
        "ᴄʜᴀɴɢᴇ ᴛʜᴇ ꜱᴛᴀʀᴛ ᴍᴇꜱꜱᴀɢᴇ. ʀᴇᴘʟʏ ᴛᴏ ᴀɴʏ ᴛᴇxᴛ ᴏʀ ᴘʜᴏᴛᴏ,\n"
        "ᴏʀ ᴜꜱᴇ <code>/addstart Your message</code>.\n"
        "ʜᴛᴍʟ ꜰᴏʀᴍᴀᴛᴛɪɴɢ ᴀɴᴅ ɴᴇᴡ ʟɪɴᴇꜱ ᴀʀᴇ ꜱᴜᴘᴘᴏʀᴛᴇᴅ.\n\n"
        "🆘 <b>/addsupport {link}</b>\n"
        "ꜱᴇᴛ ʏᴏᴜʀ ꜱᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ ᴏʀ ᴄʜᴀɴɴᴇʟ ʟɪɴᴋ.\n"
        "ɪᴛ ᴡɪʟʟ ᴀᴘᴘᴇᴀʀ ᴀꜱ ᴀ ʙᴜᴛᴛᴏɴ ᴏɴ ᴛʜᴇ ꜱᴛᴀʀᴛ ᴍᴇꜱꜱᴀɢᴇ.\n\n"
        "📢 <b>/addupdate {link}</b>\n"
        "ꜱᴇᴛ ʏᴏᴜʀ ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ ʟɪɴᴋ.\n"
        "ɪᴛ ᴡɪʟʟ ᴀᴘᴘᴇᴀʀ ᴀꜱ ᴀ ʙᴜᴛᴛᴏɴ ᴏɴ ᴛʜᴇ ꜱᴛᴀʀᴛ ᴍᴇꜱꜱᴀɢᴇ.\n\n"
        "👤 <b>/ownerlink {link}</b>\n"
        "ꜱᴇᴛ ʏᴏᴜʀ ᴘʀᴏꜰɪʟᴇ ʟɪɴᴋ ꜰᴏʀ ᴛʜᴇ ᴏᴡɴᴇʀ ʙᴜᴛᴛᴏɴ.\n\n"
        "⚙️ <b>/mysettings</b>\n"
        "ᴠɪᴇᴡ ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ ᴄᴜꜱᴛᴏᴍɪᴢᴀᴛɪᴏɴ ꜱᴛᴀᴛᴜꜱ.\n\n"
        "<i>ᴜɴᴛɪʟ ʏᴏᴜ ᴄᴜꜱᴛᴏᴍɪᴢᴇ ɪᴛ, ᴅᴇꜰᴀᴜʟᴛ ʙᴏᴛ ꜱᴇᴛᴛɪɴɢꜱ ᴡɪʟʟ ʙᴇ ᴜꜱᴇᴅ.</i>",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="clone_back_start")]
        ]),
        parse_mode=enums.ParseMode.HTML,
    )


# ── Callback: Back to clone start panel ────────────────────────────
@app.on_callback_query(filters.regex("clone_back_start"))
async def clone_back_to_start(client, callback: CallbackQuery):
    """Back button — clone ka apna start panel show karo, main bot ka nahi."""
    await callback.answer()

    is_clone = getattr(client, "is_clone", False)
    bot_id = getattr(client, "bot_id", None)
    user_id = callback.from_user.id

    if not (is_clone and bot_id):
        return await callback.edit_message_text(
            "❌ This is not a clone bot.",
            parse_mode=enums.ParseMode.HTML,
        )

    from SANYAMUSIC.utils.clone_db import (
        get_clone_start, get_clone_links, get_clone_owner_link
    )

    start_data = await get_clone_start(bot_id)
    links = await get_clone_links(bot_id)
    owner_link = await get_clone_owner_link(bot_id)

    buttons = []

    try:
        me = await client.get_me()
        username = me.username
        bot_name = me.first_name
    except:
        username = None
        bot_name = "Music Bot"

    if username:
        buttons.append([
            InlineKeyboardButton(
                "✙ 𝐀ᴅᴅ 𝐌є 𝐈η 𝐘συʀ 𝐆ʀσυᴘ ✙",
                url=f"https://t.me/{username}?startgroup=true"
            )
        ])

    support_link = links.get("support") or config.SUPPORT_CHAT
    update_link = links.get("update") or config.SUPPORT_CHANNEL
    buttons.append([
        InlineKeyboardButton("⌯ 𝐒ᴜᴘᴘσʀᴛ ⌯", url=support_link),
        InlineKeyboardButton("⌯ 𝐔ᴘᴅᴀᴛᴇ ⌯", url=update_link),
    ])

    # Owner button
    final_owner_link = owner_link or f"https://t.me/{config.OWNER_ID}"
    buttons.append([
        InlineKeyboardButton("⌯ 𝐌ʏ 𝐌ᴧsᴛᴇʀ ⌯", url=final_owner_link)
    ])

    # Help button
    buttons.append([
        InlineKeyboardButton("⌯ 𝐇єʟᴘ 𝐀ηᴅ 𝐂ᴏᴍᴍᴧηᴅ𝐬 ⌯", callback_data="open_help_panel")
    ])

    # Customize button — only for clone owner or main owner
    owner_id = getattr(client, "owner_id", None)
    if user_id == owner_id or user_id == config.OWNER_ID:
        buttons.append([
            InlineKeyboardButton("⚙️ 𝐂ᴜsᴛᴏᴍɪᴢᴇ 𝐘ᴏᴜ 𝐁ᴏᴛ", callback_data="clone_customize_panel")
        ])

    caption = start_data.get("text") or f"👋 ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ <b>{bot_name}</b> !  🎵 ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴀɴᴅ ᴘʟᴀʏ ᴍᴜꜱɪᴄ."

    try:
        if start_data.get("photo"):
            await callback.message.delete()
            await client.send_photo(
                callback.message.chat.id,
                photo=start_data["photo"],
                caption=caption,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=enums.ParseMode.HTML,
            )
        else:
            await callback.edit_message_text(
                caption,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=enums.ParseMode.HTML,
            )
    except Exception:
        await callback.edit_message_text(
            caption,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML,
        )
