# -----------------------------------------------
# 🔸 SanyaMusic — Autoplay Helper
# Multi-strategy search — fail hone ka chance nahi
# -----------------------------------------------
import asyncio
from SANYAMUSIC import LOGGER, YouTube, app
from SANYAMUSIC.utils.database import get_cmode, get_lang
from SANYAMUSIC.utils.formatters import time_to_seconds
from strings import get_string
import config


# ── Vibe keywords title se detect karo ──────────────────────────────
_VIBE_MAP = {
    "sad":          ["sad songs", "heartbreak songs", "emotional songs hindi"],
    "emotional":    ["emotional songs", "sad hindi songs", "dard bhari songs"],
    "romantic":     ["romantic songs hindi", "love songs bollywood"],
    "party":        ["party songs hindi", "dance hits bollywood"],
    "birthday":     ["birthday songs", "happy birthday hindi songs"],
    "lofi":         ["lofi hindi songs", "lofi bollywood chill"],
    "motivational": ["motivational songs hindi", "josh wale gaane"],
    "devotional":   ["bhajan", "devotional songs hindi"],
    "punjabi":      ["punjabi hits", "new punjabi songs"],
    "rap":          ["hindi rap songs", "desi hip hop"],
    "chill":        ["chill hindi songs", "late night hindi songs"],
    "workout":      ["workout songs hindi", "gym motivation songs"],
    "wedding":      ["wedding songs bollywood", "shaadi ke gaane"],
    "breakup":      ["breakup songs hindi", "sad breakup songs"],
    "rain":         ["rain songs hindi", "barish ke gaane"],
    "night":        ["late night songs hindi", "night drive songs"],
    "old":          ["old hindi songs", "classic bollywood"],
    "retro":        ["retro hindi songs", "70s 80s bollywood hits"],
}

_ULTIMATE_FALLBACK = [
    "top hindi songs 2024",
    "bollywood hits",
    "best hindi songs",
    "popular songs india",
    "top songs",
]

_HINDI_WORDS = {
    "ki", "ka", "ke", "hai", "ho", "na", "tu", "tum",
    "mere", "tera", "pyaar", "dil", "aaj", "kya", "mera",
    "teri", "teri", "hum", "koi", "sab", "bhi", "main",
}


def _extract_artist(title: str) -> str:
    if not title:
        return ""
    if " - " in title:
        parts = title.split(" - ")
        if len(parts[0].split()) <= 3:
            return parts[0].strip()
        elif len(parts[1].split()) <= 3:
            return parts[1].strip()
        return parts[0].strip()
    if " | " in title:
        parts = [p.strip() for p in title.split(" | ")]
        for p in reversed(parts):
            if len(p.split()) <= 4:
                return p
        return parts[-1]
    for sep in [" ft.", " ft ", " feat.", " feat "]:
        if sep.lower() in title.lower():
            idx = title.lower().index(sep.lower())
            after = title[idx + len(sep):].split("(")[0].split("[")[0].strip()
            if after:
                return after
    return " ".join(title.split()[:3])


def _build_search_strategies(title: str, artist: str) -> list:
    strategies = []

    # 1. Artist based
    if artist:
        strategies.append(f"{artist} songs")
        strategies.append(f"{artist} best songs")
        strategies.append(f"{artist} hits")

    # 2. Vibe based
    title_lower = title.lower()
    for keyword, queries in _VIBE_MAP.items():
        if keyword in title_lower:
            strategies.extend(queries[:2])
            break

    # 3. Title words based
    if title:
        words = title.split()[:3]
        strategies.append(" ".join(words) + " songs")

    # 4. Language detect
    title_words = set(title.lower().split())
    if title_words & _HINDI_WORDS:
        strategies.append("popular hindi songs 2024")
        strategies.append("bollywood hits 2024")
    else:
        strategies.append("popular english songs 2024")
        strategies.append("top hits 2024")

    # 5. Ultimate fallbacks
    strategies.extend(_ULTIMATE_FALLBACK)

    # Deduplicate
    seen = set()
    unique = []
    for s in strategies:
        if s not in seen:
            seen.add(s)
            unique.append(s)
    return unique


async def _search_with_fallback(title: str, artist: str, limit: int = 8) -> list:
    strategies = _build_search_strategies(title, artist)
    for strategy in strategies:
        try:
            LOGGER(__name__).info(f"Autoplay: Trying → '{strategy}'")
            results = await YouTube.suggestions(strategy, limit=limit)
            if results:
                LOGGER(__name__).info(f"Autoplay: {len(results)} results for '{strategy}'")
                return results
        except Exception as e:
            LOGGER(__name__).warning(f"Autoplay: '{strategy}' failed: {e}")
            continue
    LOGGER(__name__).error("Autoplay: ALL strategies failed!")
    return []


def _pick_next_song(suggestions: list, current_title: str) -> dict:
    current_lower = current_title.lower()[:30]
    for song in suggestions:
        if current_lower and current_lower in song.get("title", "").lower():
            continue
        duration_sec = time_to_seconds(song.get("duration", "0:00"))
        if duration_sec == 0 or duration_sec > config.DURATION_LIMIT:
            continue
        return song
    return suggestions[0] if suggestions else None


async def _autoplay_next(client, chat_id: int, last_played: dict):
    try:
        title = last_played.get("title", "") if last_played else ""
        original_chat_id = last_played.get("chat_id", chat_id) if last_played else chat_id
        artist = _extract_artist(title)

        LOGGER(__name__).info(
            f"Autoplay: chat={chat_id} | song='{title}' | artist='{artist}'"
        )

        suggestions = await _search_with_fallback(title, artist, limit=8)

        if not suggestions:
            LOGGER(__name__).error(f"Autoplay: No results at all for chat {chat_id}")
            return

        next_song = _pick_next_song(suggestions, title)
        if not next_song:
            LOGGER(__name__).error(f"Autoplay: No suitable song for chat {chat_id}")
            return

        LOGGER(__name__).info(f"Autoplay: Selected '{next_song['title']}'")

        # Track fetch — agar fail ho to dusra try karo
        details = None
        for song in [next_song] + [s for s in suggestions if s != next_song]:
            try:
                details, track_id = await YouTube.track(song["id"], True)
                next_song = song
                break
            except Exception as e:
                LOGGER(__name__).warning(f"Autoplay: track fetch failed for '{song.get('title')}': {e}")
                continue

        if not details:
            LOGGER(__name__).error("Autoplay: All track fetches failed")
            return

        # Channel mode
        chat_id_for_stream = chat_id
        channel = await get_cmode(chat_id)
        if channel:
            chat_id_for_stream = channel

        language = await get_lang(chat_id)
        _ = get_string(language)

        # Notification
        try:
            msg = await app.send_message(
                original_chat_id,
                f"🔄 <b>Autoplay</b>\n\n"
                f"🎵 <b>{next_song['title']}</b>\n"
                f"🎤 <i>{artist or 'Auto Selected'}</i>",
            )
        except Exception:
            msg = None

        # Play — forceplay=True taaki bot rejoin kare
        try:
            from SANYAMUSIC.utils.stream.stream import stream
            await stream(
                app,
                _,
                msg,
                app.id,
                details,
                chat_id_for_stream,
                "Autoplay",
                original_chat_id,
                video=None,
                streamtype="youtube",
                forceplay=True,
            )
        except Exception as e:
            LOGGER(__name__).error(f"Autoplay: stream error: {e}")
            if msg:
                try:
                    await msg.delete()
                except Exception:
                    pass

    except Exception as e:
        LOGGER(__name__).error(f"Autoplay: fatal error: {e}")
