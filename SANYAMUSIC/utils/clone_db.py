# -----------------------------------------------
# 🔸 SanyaMusic — Clone Customize Database
# Per-clone settings: start message, buttons, owner
# -----------------------------------------------
from SANYAMUSIC.core.mongo import mongodb

# Per-clone customize data collection
clone_customize_db = mongodb.clone_customize

# Per-clone served chats (alag alag broadcast ke liye)
# Collection name: clone_chats_{bot_id}


# ── Clone Owner Management ───────────────────────────────────────────

async def set_clone_owner(bot_id: int, user_id: int):
    """Clone bot ka owner set karo — sirf us bot ka, kisi aur ka nahi."""
    await clone_customize_db.update_one(
        {"bot_id": bot_id},
        {"$set": {"owner_id": user_id}},
        upsert=True,
    )


async def get_clone_owner(bot_id: int) -> int | None:
    """Clone bot ka owner ID lo."""
    doc = await clone_customize_db.find_one({"bot_id": bot_id})
    if doc:
        return doc.get("owner_id")
    return None


async def is_clone_owner(bot_id: int, user_id: int) -> bool:
    """Check karo — ye user is clone ka owner hai?"""
    owner = await get_clone_owner(bot_id)
    return owner == user_id


async def set_clone_owner_link(bot_id: int, link: str):
    """Clone owner ka custom link set karo (start button mein dikhega)."""
    await clone_customize_db.update_one(
        {"bot_id": bot_id},
        {"$set": {"owner_link": link}},
        upsert=True,
    )


async def get_clone_owner_link(bot_id: int) -> str | None:
    """Clone owner ka custom link lo."""
    doc = await clone_customize_db.find_one({"bot_id": bot_id})
    if doc:
        return doc.get("owner_link")
    return None


# ── Start Message Customize ──────────────────────────────────────────

async def set_clone_start_text(bot_id: int, text: str):
    """Custom start message text set karo (HTML format)."""
    await clone_customize_db.update_one(
        {"bot_id": bot_id},
        {"$set": {"start_text": text}},
        upsert=True,
    )


async def set_clone_start_photo(bot_id: int, file_id: str):
    """Custom start photo file_id set karo."""
    await clone_customize_db.update_one(
        {"bot_id": bot_id},
        {"$set": {"start_photo": file_id}},
        upsert=True,
    )


async def get_clone_start(bot_id: int) -> dict:
    """
    Clone ka start message data lo.
    Return: {"text": ..., "photo": ...} ya empty dict agar customize nahi kiya.
    """
    doc = await clone_customize_db.find_one({"bot_id": bot_id})
    if not doc:
        return {}
    result = {}
    if doc.get("start_text"):
        result["text"] = doc["start_text"]
    if doc.get("start_photo"):
        result["photo"] = doc["start_photo"]
    return result


# ── Support & Update Links ───────────────────────────────────────────

async def set_clone_support(bot_id: int, link: str):
    """Support link set karo."""
    await clone_customize_db.update_one(
        {"bot_id": bot_id},
        {"$set": {"support_link": link}},
        upsert=True,
    )


async def set_clone_update(bot_id: int, link: str):
    """Update channel link set karo."""
    await clone_customize_db.update_one(
        {"bot_id": bot_id},
        {"$set": {"update_link": link}},
        upsert=True,
    )


async def get_clone_links(bot_id: int) -> dict:
    """Support aur update links lo."""
    doc = await clone_customize_db.find_one({"bot_id": bot_id})
    if not doc:
        return {}
    result = {}
    if doc.get("support_link"):
        result["support"] = doc["support_link"]
    if doc.get("update_link"):
        result["update"] = doc["update_link"]
    return result


# ── Per-Clone Served Chats (Broadcast ke liye) ──────────────────────

def _clone_chats_collection(bot_id: int):
    """Har clone ka alag chats collection."""
    return mongodb[f"clone_chats_{bot_id}"]


async def add_clone_served_chat(bot_id: int, chat_id: int):
    """Clone bot ke served chat add karo."""
    col = _clone_chats_collection(bot_id)
    existing = await col.find_one({"chat_id": chat_id})
    if not existing:
        await col.insert_one({"chat_id": chat_id})


async def get_clone_served_chats(bot_id: int) -> list:
    """Clone bot ke saare served chats lo."""
    col = _clone_chats_collection(bot_id)
    chats = []
    async for doc in col.find({"chat_id": {"$lt": 0}}):
        chats.append(doc)
    return chats


async def remove_clone_data(bot_id: int):
    """Clone delete hone pe saara data hata do."""
    await clone_customize_db.delete_one({"bot_id": bot_id})
    col = _clone_chats_collection(bot_id)
    await col.drop()


# ── Clone Assistant String ───────────────────────────────────────────

async def set_clone_assistant(bot_id: int, string_session: str):
    """Clone ka custom assistant string session save karo."""
    await clone_customize_db.update_one(
        {"bot_id": bot_id},
        {"$set": {"assistant_string": string_session}},
        upsert=True,
    )


async def get_clone_assistant(bot_id: int) -> str | None:
    """Clone ka assistant string session lo."""
    doc = await clone_customize_db.find_one({"bot_id": bot_id})
    return doc.get("assistant_string") if doc else None


# ── Per-Clone Served Users ───────────────────────────────────────────

def _clone_users_collection(bot_id: int):
    return mongodb[f"clone_users_{bot_id}"]


async def add_clone_served_user(bot_id: int, user_id: int):
    col = _clone_users_collection(bot_id)
    existing = await col.find_one({"user_id": user_id})
    if not existing:
        await col.insert_one({"user_id": user_id})


async def get_clone_served_users(bot_id: int) -> list:
    col = _clone_users_collection(bot_id)
    users = []
    async for doc in col.find({}):
        users.append(doc)
    return users
