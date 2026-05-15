# -----------------------------------------------
# 🔸 SanyaMusic Project
# 🔹 Developed & Maintained by: Stark (https://github.com/urstark)
# 📅 Copyright © 2022 – All Rights Reserved
#
# 📖 License:
# This source code is open for educational and non-commercial use ONLY.
# You are required to retain this credit in all copies or substantial portions of this file.
# Commercial use, redistribution, or removal of this notice is strictly prohibited
# without prior written permission from the author.
#
# ❤️ Made with dedication and love by urstark
# -----------------------------------------------
from os import path
import asyncio
import aiohttp
from yt_dlp import YoutubeDL
from SANYAMUSIC.utils.formatters import seconds_to_min
from SANYAMUSIC import LOGGER


class SoundAPI:
    def __init__(self):
        self.opts = {
            "outtmpl": "downloads/%(id)s.%(ext)s",
            "format": "bestaudio/best",
            "retries": 3,
            "nooverwrites": False,
            "continuedl": True,
            "quiet": True,
            "no_warnings": True,
        }
        self.search_opts = {
            "outtmpl": "downloads/%(id)s.%(ext)s",
            "format": "bestaudio/best",
            "quiet": True,
            "no_warnings": True,
            "default_search": "scsearch",
            "nooverwrites": True,
        }

    async def valid(self, link: str):
        return "soundcloud" in link

    async def search_and_download(self, query: str) -> tuple | None:
        """Search SoundCloud aur best match download karo."""
        try:
            loop = asyncio.get_running_loop()

            def _search():
                opts = self.search_opts.copy()
                opts["outtmpl"] = "downloads/%(id)s.%(ext)s"
                with YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(f"scsearch1:{query}", download=True)
                    if not info or not info.get("entries"):
                        return None
                    entry = info["entries"][0]
                    filepath = path.join("downloads", f"{entry['id']}.{entry.get('ext', 'mp3')}")
                    # Check common extensions
                    for ext in [entry.get('ext', 'mp3'), 'mp3', 'opus', 'm4a']:
                        fp = path.join("downloads", f"{entry['id']}.{ext}")
                        if path.exists(fp):
                            filepath = fp
                            break
                    return {
                        "title": entry.get("title", query),
                        "duration_sec": entry.get("duration", 0),
                        "duration_min": seconds_to_min(entry.get("duration", 0)),
                        "uploader": entry.get("uploader", ""),
                        "filepath": filepath,
                    }, filepath

            result = await loop.run_in_executor(None, _search)
            if result:
                LOGGER(__name__).info(f"SoundCloud: Found '{result[0]['title']}'")
            return result
        except Exception as e:
            LOGGER(__name__).warning(f"SoundCloud search failed: {e}")
            return None

    async def download(self, url):
        d = YoutubeDL(self.opts)
        try:
            info = d.extract_info(url)
        except:
            return False
        xyz = path.join("downloads", f"{info['id']}.{info['ext']}")
        duration_min = seconds_to_min(info["duration"])
        track_details = {
            "title": info["title"],
            "duration_sec": info["duration"],
            "duration_min": duration_min,
            "uploader": info["uploader"],
            "filepath": xyz,
        }
        return track_details, xyz
