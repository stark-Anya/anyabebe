# -----------------------------------------------
# 🔸 SanyaMusic — Clone Customize Plugin
# Commands: /addstart, /addsupport, /addupdate
# Sirf clone owner use kar sakta hai
# -----------------------------------------------
import asyncio
from pyrogram import filters
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)

from SANYAMUSIC import app
from SANYAMUSIC.utils.clone_db import (
    get_clone_owner,
    get_clone_links,
    get_clone_start,
    is_clone_owner,
    set_clone_start_text,
    set_clone_start_photo,
    set_clone_support,
    set_clone_update,
)
import config


# ── Helper: Current bot ka ID lo ────────────────────────────────────
def _get_bot_id(client) -> int:
    """Client se bot ID lo — main bot ya clone dono ke liye."""
    try:
        return client.me.id
    except Exception:
        return app.me.id


# ── Helper: Check karo ye clone owner hai ───────────────────────────
async def _check_clone_owner(client, message: Message) -> bool:
    """Sirf clone owner ko allow karo. Main owner bhi allowed hai."""
    bot_id = _get_bot_id(client)
    user_id = message.from_user.id

    # Main owner (env wala) always allowed
    if user_id == config.OWNER_ID:
        return True

    # Clone ka specific owner
    if await is_clone_owner(bot_id, user_id):
        return True

    return False


# ── /addstart command ────────────────────────────────────────────────
@app.on_message(filters.command("addstart") & filters.private)
async def add_start_message(client, message: Message):
    if not await _check_clone_owner(client, message):
        return await message.reply_text(
            "❌ Ye command sirf <b>clone owner</b> use kar sakta hai.",
            parse_mode="html",
        )

    bot_id = _get_bot_id(client)

    # Photo + text dono check karo
    reply = message.reply_to_message

    if reply:
        # Reply mein photo hai?
        if reply.photo:
            file_id = reply.photo.file_id
            await set_clone_start_photo(bot_id, file_id)

            # Caption bhi hai?
            if reply.caption:
                await set_clone_start_text(bot_id, reply.caption.html)
                return await message.reply_text(
                    "✅ <b>Start message set ho gaya!</b>\n\n"
                    "📸 Photo + Text dono save ho gaye.\n"
                    "<i>Ab /start karo aur dekho.</i>",
                    parse_mode="html",
                )
            return await message.reply_text(
                "✅ <b>Start photo set ho gayi!</b>\n\n"
                "<i>Text add karna ho to photo reply mein caption likho ya dobara /addstart karo text ke saath.</i>",
                parse_mode="html",
            )

        # Sirf text hai reply mein?
        elif reply.text:
            text = reply.text.html
            await set_clone_start_text(bot_id, text)
            return await message.reply_text(
                "✅ <b>Start message set ho gaya!</b>\n\n"
                f"📝 <b>Preview:</b>\n{text}",
                parse_mode="html",
            )

    # Command ke saath text diya?
    elif len(message.command) > 1:
        text = message.text.split(None, 1)[1]
        await set_clone_start_text(bot_id, text)
        return await message.reply_text(
            "✅ <b>Start message set ho gaya!</b>\n\n"
            f"📝 <b>Preview:</b>\n{text}",
            parse_mode="html",
        )

    # Kuch nahi diya
    else:
        return await message.reply_text(
            "❓ <b>Kaise use karein:</b>\n\n"
            "1️⃣ Kisi message ko reply karke <code>/addstart</code>\n"
            "2️⃣ Photo reply karke <code>/addstart</code> (caption bhi ho sakta hai)\n"
            "3️⃣ <code>/addstart Mera custom message</code>\n\n"
            "<b>HTML format supported hai:</b>\n"
            "<code>&lt;b&gt;Bold&lt;/b&gt;</code> → <b>Bold</b>\n"
            "<code>&lt;i&gt;Italic&lt;/i&gt;</code> → <i>Italic</i>\n"
            "Newlines normal kaam karti hain ✅",
            parse_mode="html",
        )


# ── /addsupport command ──────────────────────────────────────────────
@app.on_message(filters.command("addsupport") & filters.private)
async def add_support_link(client, message: Message):
    if not await _check_clone_owner(client, message):
        return await message.reply_text(
            "❌ Ye command sirf <b>clone owner</b> use kar sakta hai.",
            parse_mode="html",
        )

    if len(message.command) < 2:
        return await message.reply_text(
            "❓ <b>Usage:</b> <code>/addsupport https://t.me/yourgroup</code>",
            parse_mode="html",
        )

    link = message.command[1]
    if not link.startswith("http"):
        return await message.reply_text(
            "❌ Valid link do — <code>https://</code> se shuru hona chahiye.",
            parse_mode="html",
        )

    bot_id = _get_bot_id(client)
    await set_clone_support(bot_id, link)

    await message.reply_text(
        f"✅ <b>Support link set ho gaya!</b>\n\n"
        f"🔗 <code>{link}</code>\n\n"
        f"Ab start message mein <b>🆘 Support</b> button aayega.",
        parse_mode="html",
    )


# ── /addupdate command ───────────────────────────────────────────────
@app.on_message(filters.command("addupdate") & filters.private)
async def add_update_link(client, message: Message):
    if not await _check_clone_owner(client, message):
        return await message.reply_text(
            "❌ Ye command sirf <b>clone owner</b> use kar sakta hai.",
            parse_mode="html",
        )

    if len(message.command) < 2:
        return await message.reply_text(
            "❓ <b>Usage:</b> <code>/addupdate https://t.me/yourchannel</code>",
            parse_mode="html",
        )

    link = message.command[1]
    if not link.startswith("http"):
        return await message.reply_text(
            "❌ Valid link do — <code>https://</code> se shuru hona chahiye.",
            parse_mode="html",
        )

    bot_id = _get_bot_id(client)
    await set_clone_update(bot_id, link)

    await message.reply_text(
        f"✅ <b>Update channel link set ho gaya!</b>\n\n"
        f"🔗 <code>{link}</code>\n\n"
        f"Ab start message mein <b>📢 Updates</b> button aayega.",
        parse_mode="html",
    )


# ── /mysettings — Clone owner ka customize panel ─────────────────────
@app.on_message(filters.command("mysettings") & filters.private)
async def my_settings(client, message: Message):
    if not await _check_clone_owner(client, message):
        return await message.reply_text(
            "❌ Ye command sirf <b>clone owner</b> use kar sakta hai.",
            parse_mode="html",
        )

    bot_id = _get_bot_id(client)
    start_data = await get_clone_start(bot_id)
    links = await get_clone_links(bot_id)

    has_photo = "✅" if start_data.get("photo") else "❌"
    has_text = "✅" if start_data.get("text") else "❌ (Default use ho raha)"
    has_support = f"✅ {links['support']}" if links.get("support") else "❌ (Default use ho raha)"
    has_update = f"✅ {links['update']}" if links.get("update") else "❌ (Default use ho raha)"

    text = (
        f"⚙️ <b>Customize Settings</b>\n\n"
        f"📸 <b>Start Photo:</b> {has_photo}\n"
        f"📝 <b>Start Text:</b> {has_text}\n"
        f"🆘 <b>Support Link:</b> {has_support}\n"
        f"📢 <b>Update Link:</b> {has_update}\n\n"
        f"<b>Commands:</b>\n"
        f"• <code>/addstart</code> — Start message change karo\n"
        f"• <code>/addsupport link</code> — Support button set karo\n"
        f"• <code>/addupdate link</code> — Update button set karo"
    )

    await message.reply_text(text, parse_mode="html")


# ── Callback: Customize panel button ────────────────────────────────
@app.on_callback_query(filters.regex("clone_customize_panel"))
async def clone_customize_callback(client, callback: CallbackQuery):
    user_id = callback.from_user.id
    bot_id = _get_bot_id(client)

    # Sirf clone owner ya main owner dekh sake
    is_owner = (user_id == config.OWNER_ID) or await is_clone_owner(bot_id, user_id)
    if not is_owner:
        return await callback.answer("❌ Sirf clone owner ke liye!", show_alert=True)

    await callback.answer()

    text = (
        "⚙️ <b>Customise Your Bot</b>\n\n"
        "Ye commands use karo apne bot ko personalize karne ke liye:\n\n"
        "📝 <b>/addstart</b>\n"
        "   Start message change karo. Kisi message ko reply karke ya\n"
        "   photo reply karke use karo. HTML format supported hai.\n\n"
        "🆘 <b>/addsupport {link}</b>\n"
        "   Apna support group/channel link add karo.\n"
        "   Start message mein button aayega.\n\n"
        "📢 <b>/addupdate {link}</b>\n"
        "   Update channel link add karo.\n"
        "   Start message mein button aayega.\n\n"
        "⚙️ <b>/mysettings</b>\n"
        "   Current customize status dekho.\n\n"
        "<i>💡 Jab tak customize na karo, default settings chalti rahegi.</i>"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="settings_back_helper")]
    ])

    await callback.edit_message_text(text, reply_markup=keyboard, parse_mode="html")
