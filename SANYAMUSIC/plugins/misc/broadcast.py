import asyncio
from pyrogram import filters, enums
from pyrogram.errors import FloodWait
from SANYAMUSIC import app
from SANYAMUSIC.misc import SUDOERS
from SANYAMUSIC.utils.database import (
    get_client,
    get_served_chats,
    get_served_users,
)
from SANYAMUSIC.utils.clone_db import get_clone_served_chats
from SANYAMUSIC.utils.decorators.language import language
from config import OWNER_ID

IS_BROADCASTING = False


async def _send_to_chats(client, chats: list, y: int, x: int, reply_msg, query: str, message):
    """Helper — chats ki list mein broadcast karo, count return karo."""
    sent = 0
    pin = 0
    for chat_id in chats:
        try:
            m = (
                await client.forward_messages(chat_id, y, x)
                if reply_msg
                else await client.send_message(chat_id, text=query)
            )
            if "-pin" in message.text:
                try:
                    await m.pin(disable_notification=True)
                    pin += 1
                except:
                    pass
            elif "-pinloud" in message.text:
                try:
                    await m.pin(disable_notification=False)
                    pin += 1
                except:
                    pass
            sent += 1
            await asyncio.sleep(0.2)
        except FloodWait as fw:
            flood_time = int(fw.value)
            if flood_time > 200:
                continue
            await asyncio.sleep(flood_time)
        except:
            continue
    return sent, pin


@app.on_message(filters.command("broadcast") & SUDOERS)
@language
async def broadcast_message(client, message, _):
    global IS_BROADCASTING

    # Clone bot me broadcast allowed nahi
    is_clone = getattr(client, "is_clone", False)
    if is_clone:
        return await message.reply_text(
            "❌ Broadcast is not available in clone bots.\n"
            "Use the <b>main bot</b> to broadcast to all groups.",
            parse_mode=enums.ParseMode.HTML,
        )

    # Sirf main owner
    if message.from_user.id != OWNER_ID:
        return await message.reply_text(
            "❌ Only the <b>main owner</b> can use broadcast.",
            parse_mode=enums.ParseMode.HTML,
        )

    reply_msg = message.reply_to_message
    if reply_msg:
        x = reply_msg.id
        y = message.chat.id
        query = ""
    else:
        if len(message.command) < 2:
            return await message.reply_text(_["broad_2"])
        query = message.text.split(None, 1)[1]
        for flag in ["-pin", "-nobot", "-pinloud", "-assistant", "-user"]:
            query = query.replace(flag, "")
        query = query.strip()
        if not query:
            return await message.reply_text(_["broad_8"])
        x = y = 0

    IS_BROADCASTING = True
    status_msg = await message.reply_text(_["broad_1"])

    total_sent = 0
    total_pin = 0

    if "-nobot" not in message.text:
        # ── Main bot ke groups ──────────────────────────────────────
        schats = await get_served_chats()
        main_chats = [int(c["chat_id"]) for c in schats]
        s, p = await _send_to_chats(app, main_chats, y, x, reply_msg, query, message)
        total_sent += s
        total_pin += p

        # ── Saare clone bots ke groups ──────────────────────────────
        try:
            from SANYAMUSIC.plugins.sudo.clone import clone_bot_clients
            for bot_id, clone_client in clone_bot_clients.items():
                try:
                    clone_chats = await get_clone_served_chats(bot_id)
                    clone_chat_ids = [int(c["chat_id"]) for c in clone_chats]
                    if not clone_chat_ids:
                        continue
                    s, p = await _send_to_chats(
                        clone_client, clone_chat_ids, y, x, reply_msg, query, message
                    )
                    total_sent += s
                    total_pin += p
                except Exception:
                    continue
        except Exception:
            pass

        try:
            await status_msg.edit_text(_["broad_3"].format(total_sent, total_pin))
        except:
            pass

    # ── User broadcast ──────────────────────────────────────────────
    if "-user" in message.text:
        susr = 0
        susers = await get_served_users()
        for u in susers:
            try:
                (
                    await app.forward_messages(int(u["user_id"]), y, x)
                    if reply_msg
                    else await app.send_message(int(u["user_id"]), text=query)
                )
                susr += 1
                await asyncio.sleep(0.2)
            except FloodWait as fw:
                flood_time = int(fw.value)
                if flood_time > 200:
                    continue
                await asyncio.sleep(flood_time)
            except:
                pass
        try:
            await message.reply_text(_["broad_4"].format(susr))
        except:
            pass

    # ── Assistant broadcast ─────────────────────────────────────────
    if "-assistant" in message.text:
        aw = await message.reply_text(_["broad_5"])
        text = _["broad_6"]
        from SANYAMUSIC.core.userbot import assistants
        for num in assistants:
            sent = 0
            assist_client = await get_client(num)
            async for dialog in assist_client.get_dialogs():
                try:
                    (
                        await assist_client.forward_messages(dialog.chat.id, y, x)
                        if reply_msg
                        else await assist_client.send_message(dialog.chat.id, text=query)
                    )
                    sent += 1
                    await asyncio.sleep(3)
                except FloodWait as fw:
                    flood_time = int(fw.value)
                    if flood_time > 200:
                        continue
                    await asyncio.sleep(flood_time)
                except:
                    continue
            text += _["broad_7"].format(num, sent)
        try:
            await aw.edit_text(text)
        except:
            pass

    IS_BROADCASTING = False
