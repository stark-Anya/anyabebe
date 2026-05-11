# -----------------------------------------------
# SanyaMusic — AI-Powered Autoplay
# Uses Groq (llama-3.1-8b-instant) to analyze
# song vibe and find perfect next song
# -----------------------------------------------
import asyncio
import random
import json
import aiohttp

from SANYAMUSIC import LOGGER, YouTube, app
from SANYAMUSIC.utils.database import get_cmode, get_lang
from SANYAMUSIC.utils.formatters import time_to_seconds
from strings import get_string
import config

# Per-chat played songs history (ID based)
_played_history: dict = {}
_MAX_HISTORY = 50

# Groq config
_GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
_GROQ_MODEL = "llama-3.1-8b-instant"

# Ultimate fallbacks — kabhi fail nahi hote
_FALLBACKS = [
    "top hindi songs",
    "bollywood hits",
    "best hindi songs",
    "popular songs",
    "top songs 2024",
]

# ── Groq AI Analysis ─────────────────────────────────────────────────

_SYSTEM_PROMPT = """You are a music analysis AI. Given a song title and artist, analyze the song and return search queries to find similar songs on YouTube. But the exact same song should not be repeated again.

Analyze:
- mood (sad / romantic / happy / energetic / chill / devotional / motivational)
- language (hindi / english / punjabi / bengali / other)
- genre (pop / classical / lofi / rap / folk / devotional / indie)
- era (90s / 2000s / 2010s / modern)
- vibe (party / heartbreak / love / spiritual / workout / night / rain / wedding)

Return ONLY valid JSON, no explanation, no markdown:
{
  "mood": "romantic",
  "language": "hindi",
  "genre": "pop",
  "era": "modern",
  "vibe": "love",
  "queries": [
    "Arijit Singh romantic songs",
    "emotional bollywood love songs 2010s",
    "hindi sad romantic songs arijit"
  ]
}

Rules:
- queries must be YouTube search friendly
- provide exactly 3 queries, most specific first
- if artist is known, include artist name in first query
- match the mood and language precisely"""


async def _ask_groq(title: str, artist: str) -> dict | None:
    """Groq AI se song analyze karwao — search queries lo."""
    groq_key = getattr(config, "GROQ_API_KEY", None)
    if not groq_key:
        LOGGER(__name__).warning("Autoplay AI: GROQ_API_KEY not set, using fallback")
        return None

    user_msg = f'Song title: "{title}"\nArtist: "{artist or "Unknown"}"'

    payload = {
        "model": _GROQ_MODEL,
        "messages": [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        "temperature": 0.4,
        "max_tokens": 300,
    }

    headers = {
        "Authorization": f"Bearer {groq_key}",
        "Content-Type": "application/json",
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                _GROQ_URL,
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=8),
            ) as resp:
                if resp.status != 200:
                    LOGGER(__name__).warning(f"Autoplay AI: Groq HTTP {resp.status}")
                    return None
                data = await resp.json()
                raw = data["choices"][0]["message"]["content"].strip()

                # JSON parse karo
                raw = raw.replace("```json", "").replace("```", "").strip()
                result = json.loads(raw)
                LOGGER(__name__).info(
                    f"Autoplay AI: mood={result.get('mood')} "
                    f"lang={result.get('language')} "
                    f"queries={result.get('queries')}"
                )
                return result
    except json.JSONDecodeError as e:
        LOGGER(__name__).warning(f"Autoplay AI: JSON parse failed: {e}")
        return None
    except Exception as e:
        LOGGER(__name__).warning(f"Autoplay AI: Groq request failed: {e}")
        return None


# ── Fallback artist extractor (AI fail hone pe) ──────────────────────

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
    return " ".join(title.split()[:2])


def _fallback_queries(title: str, artist: str) -> list:
    """AI fail hone pe basic queries banao."""
    queries = []
    if artist:
        queries.append(f"{artist} songs")
        queries.append(f"{artist} best hits")
    if title:
        words = title.split()[:3]
        queries.append(" ".join(words) + " songs")
    queries.extend(_FALLBACKS)
    # Deduplicate
    seen = set()
    result = []
    for q in queries:
        if q not in seen:
            seen.add(q)
            result.append(q)
    return result


# ── Search ───────────────────────────────────────────────────────────

async def _search_with_queries(queries: list, limit: int = 10) -> list:
    """Queries list try karo — pehli successful return karo."""
    # Shuffle after first 2 (top 2 most relevant rakhо)
    if len(queries) > 3:
        top = queries[:2]
        rest = queries[2:]
        random.shuffle(rest)
        queries = top + rest

    for q in queries:
        try:
            LOGGER(__name__).info(f"Autoplay: Searching '{q}'")
            results = await YouTube.suggestions(q, limit=limit)
            if results:
                LOGGER(__name__).info(f"Autoplay: {len(results)} results for '{q}'")
                return results
        except Exception as e:
            LOGGER(__name__).warning(f"Autoplay: Search '{q}' failed: {e}")
            continue

    LOGGER(__name__).error("Autoplay: All searches failed")
    return []


# ── Song Picker ──────────────────────────────────────────────────────

def _pick_next_song(suggestions: list, current_title: str, chat_id: int) -> dict | None:
    history = _played_history.get(chat_id, set())
    current_lower = current_title.lower()[:40]

    candidates = []
    for song in suggestions:
        song_id = song.get("id", "")
        song_title = song.get("title", "")

        if song_id in history:
            continue
        if current_lower and current_lower in song_title.lower():
            continue
        duration_sec = time_to_seconds(song.get("duration", "0:00"))
        if duration_sec == 0 or duration_sec > config.DURATION_LIMIT:
            continue
        candidates.append(song)

    if candidates:
        return random.choice(candidates)

    # History full — reset karo
    LOGGER(__name__).info(f"Autoplay: History full for chat {chat_id}, resetting")
    _played_history[chat_id] = set()

    for song in suggestions:
        if current_lower and current_lower in song.get("title", "").lower():
            continue
        duration_sec = time_to_seconds(song.get("duration", "0:00"))
        if duration_sec == 0 or duration_sec > config.DURATION_LIMIT:
            continue
        return song

    return suggestions[0] if suggestions else None


def _mark_played(chat_id: int, song_id: str):
    if chat_id not in _played_history:
        _played_history[chat_id] = set()
    history = _played_history[chat_id]
    history.add(song_id)
    if len(history) > _MAX_HISTORY:
        _played_history[chat_id] = set(list(history)[-_MAX_HISTORY:])


# ── Main Function ────────────────────────────────────────────────────

async def _autoplay_next(client, chat_id: int, last_played: dict):
    try:
        title = last_played.get("title", "") if last_played else ""
        original_chat_id = last_played.get("chat_id", chat_id) if last_played else chat_id
        artist = _extract_artist(title)

        LOGGER(__name__).info(
            f"Autoplay AI: chat={chat_id} | song='{title}' | artist='{artist}'"
        )

        # Step 1: Groq AI se analyze karwao
        ai_result = await _ask_groq(title, artist)

        if ai_result and ai_result.get("queries"):
            queries = ai_result["queries"]
            # Artist based query bhi add karo agar AI ne nahi diya
            if artist and not any(artist.lower() in q.lower() for q in queries):
                queries.insert(0, f"{artist} songs")
            # Fallbacks append karo end mein
            queries.extend(_FALLBACKS)
        else:
            # AI fail — basic fallback queries
            LOGGER(__name__).warning("Autoplay AI: Using fallback queries")
            queries = _fallback_queries(title, artist)

        # Step 2: YouTube search
        suggestions = await _search_with_queries(queries, limit=10)

        if not suggestions:
            LOGGER(__name__).error(f"Autoplay: No results for chat {chat_id}")
            return

        # Step 3: Best song pick karo
        next_song = _pick_next_song(suggestions, title, chat_id)
        if not next_song:
            LOGGER(__name__).error(f"Autoplay: No suitable song for chat {chat_id}")
            return

        LOGGER(__name__).info(f"Autoplay: Selected '{next_song['title']}'")

        # Step 4: Track details fetch
        details = None
        for song in [next_song] + [s for s in suggestions if s != next_song]:
            try:
                details, track_id = await YouTube.track(song["id"], True)
                next_song = song
                break
            except Exception as e:
                LOGGER(__name__).warning(
                    f"Autoplay: Track fetch failed '{song.get('title')}': {e}"
                )
                continue

        if not details:
            LOGGER(__name__).error("Autoplay: All track fetches failed")
            return

        _mark_played(chat_id, next_song.get("id", ""))

        # Step 5: Stream setup
        chat_id_for_stream = chat_id
        channel = await get_cmode(chat_id)
        if channel:
            chat_id_for_stream = channel

        language = await get_lang(chat_id)
        _ = get_string(language)

        # AI detected mood show karo notification mein
        mood_text = ""
        if ai_result:
            mood = ai_result.get("mood", "")
            vibe = ai_result.get("vibe", "")
            if mood:
                mood_text = f"\n🎭 <i>{mood.capitalize()}{' • ' + vibe.capitalize() if vibe else ''}</i>"

        try:
            msg = await app.send_message(
                original_chat_id,
                f"🔄 <b>Autoplay</b>\n\n"
                f"🎵 <b>{next_song['title']}</b>\n"
                f"🎤 <i>{artist or 'Auto Selected'}</i>"
                f"{mood_text}",
            )
        except Exception:
            msg = None

        # Step 6: Play
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
            LOGGER(__name__).error(f"Autoplay: Stream error: {e}")
            if msg:
                try:
                    await msg.delete()
                except Exception:
                    pass

    except Exception as e:
        LOGGER(__name__).error(f"Autoplay: Fatal error: {e}")
