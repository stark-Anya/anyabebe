# -----------------------------------------------
# 🔸 SanyaMusic — Autoplay Helper
# Jab queue empty ho aur autoplay ON ho,
# same artist ka next song fetch karke play karo
# -----------------------------------------------
import asyncio
import re

from SANYAMUSIC import LOGGER, YouTube, app
from SANYAMUSIC.utils.database import get_cmode, get_lang
from SANYAMUSIC.utils.formatters import time_to_seconds
from strings import get_string
import config


def _extract_artist(title: str) -> str:
    """
    Title se artist ka naam nikalo.
    Common formats:
      'Shape of You - Ed Sheeran'
      'Ed Sheeran - Shape of You'
      'Tum Hi Ho | Aashiqui 2 | Arijit Singh'
    """
    if not title:
        return ""

    # Pehle ' - ' se split karo
    if " - " in title:
        parts = title.split(" - ")
        # Agar pehla part chota hai toh artist wahi hai (Ed Sheeran - Song)
        # Agar doosra part chota hai toh artist wahi hai (Song - Ed Sheeran)
        if len(parts[0].split()) <= 3:
            return parts[0].strip()
        elif len(parts[1].split()) <= 3:
            return parts[1].strip()
        return parts[0].strip()

    # '|' se split
    if " | " in title:
        parts = title.split(" | ")
        # Last part usually artist hota hai Indian songs mein
        return parts[-1].strip()

    # Koi separator nahi — pehle 2 words use karo
    words = title.split()
    return " ".join(words[:2])


async def _autoplay_next(client, chat_id: int, last_played: dict):
    """
    Last played song ke title se artist nikalo,
    us artist ka ek naya song fetch karo aur queue mein daalo.
    """
    try:
        title = last_played.get("title", "") if last_played else ""
        original_chat_id = last_played.get("chat_id", chat_id) if last_played else chat_id

        artist = _extract_artist(title)
        keyword = f"{artist} songs" if artist else "Hindi hits"

        LOGGER(__name__).info(f"Autoplay: Searching '{keyword}' for chat {chat_id}")

        # YouTube se suggestions fetch karo
        suggestions = await YouTube.suggestions(keyword, limit=6)

        if not suggestions:
            LOGGER(__name__).warning(f"Autoplay: No results for '{keyword}'")
            return

        # Last played wala skip karo
        next_song = None
        for s in suggestions:
            if title.lower() not in s["title"].lower():
                next_song = s
                break

        if not next_song:
            next_song = suggestions[0]

        LOGGER(__name__).info(f"Autoplay: Playing '{next_song['title']}' in chat {chat_id}")

        # Duration check
        duration_sec = time_to_seconds(next_song.get("duration", "0:00"))
        if duration_sec > config.DURATION_LIMIT:
            LOGGER(__name__).warning(f"Autoplay: Song too long, skipping")
            return

        # Track details fetch karo
        try:
            details, track_id = await YouTube.track(next_song["id"], True)
        except Exception as e:
            LOGGER(__name__).error(f"Autoplay track fetch error: {e}")
            return

        # Channel mode check
        chat_id_for_stream = chat_id
        channel = await get_cmode(chat_id)
        if channel:
            chat_id_for_stream = channel

        # Language
        language = await get_lang(chat_id)
        _ = get_string(language)

        # Notification message bhejo
        try:
            msg = await app.send_message(
                original_chat_id,
                f"🔄 <b>Autoplay</b>\n\n"
                f"🎵 Ab play ho raha hai:\n"
                f"<b>{next_song['title']}</b>\n\n"
                f"🎤 Artist: <i>{artist or 'Unknown'}</i>",
            )
        except Exception:
            msg = None

        # Stream start karo
        try:
            from SANYAMUSIC.utils.stream.stream import stream
            await stream(
                app,              # PyTgCalls nahi, Pyrogram app
                _,
                msg,
                app.id,
                details,
                chat_id_for_stream,
                "Autoplay",
                original_chat_id,
                video=None,
                streamtype="youtube",
                forceplay=None,
            )
        except Exception as e:
            LOGGER(__name__).error(f"Autoplay stream error: {e}")
            if msg:
                try:
                    await msg.delete()
                except Exception:
                    pass

    except Exception as e:
        LOGGER(__name__).error(f"_autoplay_next fatal error: {e}")
