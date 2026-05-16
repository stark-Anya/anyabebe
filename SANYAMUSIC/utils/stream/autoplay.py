# -----------------------------------------------
# SanyaMusic — AI-Powered Autoplay
# Search: Artist + Vibe/Mood only (no title)
# -----------------------------------------------
import asyncio
import random
import json
import re
import aiohttp

from SANYAMUSIC import LOGGER, YouTube, app
from SANYAMUSIC.utils.database import get_cmode, get_lang
from SANYAMUSIC.utils.formatters import time_to_seconds
from strings import get_string
import config

_played_history: dict = {}
_MAX_HISTORY = 80

_GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
_GROQ_MODEL = "llama-3.1-8b-instant"

_SYSTEM_PROMPT = """You are a music expert AI. Given a song title and artist, analyze the song deeply.

Return ONLY valid JSON — no markdown, no explanation:
{
  "artist": "Arijit Singh",
  "language": "hindi",
  "mood": "romantic",
  "vibe": "heartbreak",
  "genre": "bollywood pop",
  "similar_artists": ["Jubin Nautiyal", "Atif Aslam"],
  "search_queries": [
    "Arijit Singh romantic sad songs",
    "Jubin Nautiyal heartbreak hindi songs",
    "bollywood emotional love songs hindi"
  ]
}

Rules:
- search_queries must NOT contain the original song title
- search_queries should be based on artist, mood, vibe, genre only
- similar_artists should be 2 real artists with similar style
- exactly 3 search_queries
- language detection must be accurate"""

_STOP_WORDS = {
    'the','a','an','and','or','in','on','at','to','for','of','with','by',
    'ka','ki','ke','hai','ho','na','aur','se','me','mein',
    'official','audio','video','lyrical','lyrics','full','song',
    'hd','ft','feat','version','remix','cover','new','latest','slow','reverb',
}

def _fingerprint(title: str) -> frozenset:
    title = title.lower()
    title = re.sub(r'\([^)]*\)|\[[^\]]*\]', '', title)
    title = re.sub(r'[^\w\s]', ' ', title)
    return frozenset(
        w for w in title.split()
        if w and w not in _STOP_WORDS and len(w) > 2
    )

def _is_duplicate(title: str, history: list) -> bool:
    new_fp = _fingerprint(title)
    if not new_fp:
        return False
    return any(new_fp & old_fp for old_fp in history)

def _mark_played(chat_id: int, title: str):
    if chat_id not in _played_history:
        _played_history[chat_id] = []
    _played_history[chat_id].append(_fingerprint(title))
    if len(_played_history[chat_id]) > _MAX_HISTORY:
        _played_history[chat_id] = _played_history[chat_id][-_MAX_HISTORY:]

def _extract_artist(title: str) -> str:
    """Basic artist extract — AI ke liye hint."""
    if " - " in title:
        parts = title.split(" - ")
        return parts[0].strip() if len(parts[0].split()) <= 3 else parts[-1].strip()
    if " | " in title:
        parts = [p.strip() for p in title.split(" | ")]
        for p in reversed(parts):
            if len(p.split()) <= 4:
                return p
    return ""

async def _ask_groq(title: str, artist: str) -> dict | None:
    groq_key = getattr(config, "GROQ_API_KEY", None)
    if not groq_key:
        LOGGER(__name__).warning("Autoplay: GROQ_API_KEY not set")
        return None
    try:
        payload = {
            "model": _GROQ_MODEL,
            "messages": [
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": f'Song: "{title}"\nArtist hint: "{artist or "Unknown"}"'},
            ],
            "temperature": 0.6,
            "max_tokens": 300,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                _GROQ_URL, json=payload,
                headers={
                    "Authorization": f"Bearer {groq_key}",
                    "Content-Type": "application/json"
                },
                timeout=aiohttp.ClientTimeout(total=8),
            ) as resp:
                if resp.status != 200:
                    LOGGER(__name__).warning(f"Autoplay AI: HTTP {resp.status}")
                    return None
                data = await resp.json()
                raw = data["choices"][0]["message"]["content"].strip()
                raw = raw.replace("```json", "").replace("```", "").strip()
                result = json.loads(raw)
                LOGGER(__name__).info(
                    f"Autoplay AI: artist={result.get('artist')} "
                    f"mood={result.get('mood')} vibe={result.get('vibe')} "
                    f"queries={result.get('search_queries')}"
                )
                return result
    except Exception as e:
        LOGGER(__name__).warning(f"Autoplay AI failed: {e}")
        return None

def _fallback_queries(artist: str, title: str) -> list:
    """AI fail hone pe artist + genre based queries."""
    queries = []
    if artist:
        queries.append(f"{artist} best songs")
        queries.append(f"{artist} hits playlist")
    # Language detect from title
    hindi_words = {'ki','ka','ke','hai','tum','mere','tera','pyaar','dil','aaj'}
    if any(w in title.lower().split() for w in hindi_words):
        queries.append("best hindi bollywood songs")
        queries.append("popular hindi songs playlist")
    else:
        queries.append("top english songs playlist")
    queries.append("best songs playlist")
    return queries

async def _search(queries: list, limit: int = 15) -> list:
    top2, rest = queries[:2], queries[2:]
    random.shuffle(rest)
    for q in top2 + rest:
        try:
            results = await YouTube.suggestions(q, limit=limit)
            if results:
                LOGGER(__name__).info(f"Autoplay: Got {len(results)} results for '{q}'")
                random.shuffle(results)
                return results
        except Exception as e:
            LOGGER(__name__).warning(f"Autoplay: Search '{q}' failed: {e}")
    return []

def _pick(suggestions: list, current_title: str, history: list) -> dict | None:
    current_fp = _fingerprint(current_title)
    candidates = []
    for song in suggestions:
        t = song.get("title", "")
        fp = _fingerprint(t)
        if current_fp & fp:
            continue
        if _is_duplicate(t, history):
            continue
        dur = time_to_seconds(song.get("duration", "0:00"))
        if dur == 0 or dur > config.DURATION_LIMIT:
            continue
        candidates.append(song)
    return random.choice(candidates) if candidates else None

async def _autoplay_next(client, chat_id: int, last_played: dict):
    try:
        title = last_played.get("title", "") if last_played else ""
        original_chat_id = last_played.get("chat_id", chat_id) if last_played else chat_id
        artist = _extract_artist(title)
        history = _played_history.get(chat_id, [])

        LOGGER(__name__).info(f"Autoplay: chat={chat_id} | '{title}' | artist='{artist}'")

        # Step 1: AI se artist+mood based queries lo
        ai_result = await _ask_groq(title, artist)

        if ai_result and ai_result.get("search_queries"):
            queries = ai_result["search_queries"]
            # Extra queries — similar artists se bhi
            similar = ai_result.get("similar_artists", [])
            mood = ai_result.get("mood", "")
            lang = ai_result.get("language", "hindi")
            for sim_artist in similar[:2]:
                queries.append(f"{sim_artist} {mood} songs")
            queries.append(f"best {lang} {mood} songs")
        else:
            LOGGER(__name__).warning("Autoplay AI: No result, using fallback")
            queries = _fallback_queries(artist, title)

        # Step 2: Search
        suggestions = await _search(queries, limit=15)
        if not suggestions:
            LOGGER(__name__).error(f"Autoplay: No results for chat {chat_id}")
            return

        # Step 3: Pick — no duplicate
        next_song = _pick(suggestions, title, history)
        if not next_song:
            LOGGER(__name__).info(f"Autoplay: History reset for chat {chat_id}")
            _played_history[chat_id] = []
            next_song = _pick(suggestions, title, [])

        if not next_song:
            LOGGER(__name__).error(f"Autoplay: No suitable song")
            return

        LOGGER(__name__).info(f"Autoplay: Playing '{next_song['title']}'")

        # Step 4: Track fetch
        details = None
        for song in [next_song] + [s for s in suggestions if s != next_song]:
            if _is_duplicate(song.get("title", ""), _played_history.get(chat_id, [])):
                continue
            try:
                details, _ = await YouTube.track(song["id"], True)
                next_song = song
                break
            except Exception:
                continue

        if not details:
            LOGGER(__name__).error("Autoplay: Track fetch failed")
            return

        _mark_played(chat_id, next_song["title"])

        # Channel mode
        chat_id_for_stream = chat_id
        channel = await get_cmode(chat_id)
        if channel:
            chat_id_for_stream = channel

        language = await get_lang(chat_id)
        _ = get_string(language)

        # Mood/vibe notification
        mood_line = ""
        if ai_result:
            mood = ai_result.get("mood", "")
            vibe = ai_result.get("vibe", "")
            if mood:
                mood_line = f"\n🎭 <i>{mood.capitalize()}{' • ' + vibe.capitalize() if vibe else ''}</i>"

        # Notification — 20 sec baad delete
        msg = None
        try:
            msg = await app.send_message(
                original_chat_id,
                f"<blockquote><b>❖ 𝐀ɴʏᴀ’s ʟɪᴛᴛʟᴇ ɢɪғᴛ ғᴏʀ ʏᴏᴜ 🎧</b></blockquote>\n"
                f"<blockquote><b>✬ 𝐒ᴏɴɢ : {next_song['title']}</b></blockquote>\n"
                f"<blockquote><b>✬ 𝐓ʜᴇᴍᴇs : {mood_line}</b></blockquote>",
            )
            async def _del():
                await asyncio.sleep(20)
                try:
                    await msg.delete()
                except Exception:
                    pass
            asyncio.create_task(_del())
        except Exception:
            pass

        # Play
        try:
            from SANYAMUSIC.utils.stream.stream import stream
            await stream(
                app, _, msg, app.id, details,
                chat_id_for_stream, "Autoplay", original_chat_id,
                video=None, streamtype="youtube", forceplay=True,
            )
        except Exception as e:
            LOGGER(__name__).error(f"Autoplay: Stream error: {e}")
            if msg:
                try:
                    await msg.delete()
                except Exception:
                    pass

    except Exception as e:
        LOGGER(__name__).error(f"Autoplay: Fatal: {e}")
