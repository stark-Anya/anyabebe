# -----------------------------------------------
# SanyaMusic — JioSaavn Platform
# Direct 320kbps stream — no watermark, no YouTube
# -----------------------------------------------
import aiohttp
from SANYAMUSIC import LOGGER

SAAVN_BASE = "https://www.jiosaavn.com/api.php"


class JioSaavnAPI:

    async def search(self, query: str, limit: int = 5) -> list:
        """Song search karo — list of results return karo."""
        try:
            params = {
                "__call": "search.getResults",
                "q": query,
                "_format": "json",
                "_marker": "0",
                "api_version": "4",
                "cc": "in",
                "ctx": "web6dot0",
            }
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    SAAVN_BASE, params=params,
                    timeout=aiohttp.ClientTimeout(total=8)
                ) as resp:
                    if resp.status != 200:
                        return []
                    data = await resp.json(content_type=None)
                    results = data.get("results", [])
                    songs = []
                    for item in results[:limit]:
                        songs.append({
                            "id": item.get("id", ""),
                            "title": item.get("title", ""),
                            "artist": item.get("more_info", {}).get("singers", ""),
                            "duration": item.get("more_info", {}).get("duration", "0"),
                            "image": item.get("image", "").replace("150x150", "500x500"),
                            "encrypted_url": item.get("more_info", {}).get("encrypted_media_url", ""),
                        })
                    return songs
        except Exception as e:
            LOGGER(__name__).error(f"JioSaavn search error: {e}")
            return []

    async def get_stream_url(self, encrypted_url: str, bitrate: int = 320) -> str | None:
        """Encrypted URL se direct stream URL lo."""
        try:
            params = {
                "__call": "song.generateAuthToken",
                "url": encrypted_url,
                "bitrate": str(bitrate),
                "api_version": "4",
                "_format": "json",
                "ctx": "web6dot0",
                "_marker": "0",
            }
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    SAAVN_BASE, params=params,
                    timeout=aiohttp.ClientTimeout(total=8)
                ) as resp:
                    if resp.status != 200:
                        return None
                    data = await resp.json(content_type=None)
                    auth_url = data.get("auth_url", "")
                    if auth_url:
                        return auth_url.replace("http://", "https://")
                    return None
        except Exception as e:
            LOGGER(__name__).error(f"JioSaavn stream URL error: {e}")
            return None

    async def get_song_url(self, query: str) -> tuple[str | None, dict | None]:
        """
        Query se song dhundo aur direct stream URL return karo.
        Returns: (stream_url, song_info) or (None, None)
        """
        try:
            songs = await self.search(query, limit=5)
            if not songs:
                LOGGER(__name__).warning(f"JioSaavn: No results for '{query}'")
                return None, None

            for song in songs:
                if not song.get("encrypted_url"):
                    continue
                # 320kbps try karo, fail hone pe 160kbps
                for bitrate in [320, 160, 96]:
                    url = await self.get_stream_url(song["encrypted_url"], bitrate)
                    if url:
                        LOGGER(__name__).info(
                            f"JioSaavn: Found '{song['title']}' at {bitrate}kbps"
                        )
                        return url, song

            return None, None
        except Exception as e:
            LOGGER(__name__).error(f"JioSaavn get_song_url error: {e}")
            return None, None
