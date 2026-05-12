import asyncio
import os
import re
import shutil
from typing import Union

import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from youtubesearchpython.__future__ import VideosSearch

import config
from SANYAMUSIC import LOGGER
from SANYAMUSIC.utils.database import is_on_off
from SANYAMUSIC.utils.formatters import time_to_seconds, seconds_to_min


class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    def _yt_dlp_call_with_fallback(self, action, opts):
        """yt-dlp call — cookies fallback agar fail ho."""
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                return action(ydl)
        except Exception as e:
            cookie_path = "SANYAMUSIC/assets/cookies.txt"
            if not os.path.exists(cookie_path):
                raise e

            temp_cookie = "SANYAMUSIC/assets/cookies_temp.txt"
            shutil.copy2(cookie_path, temp_cookie)

            opts_fb = opts.copy()
            opts_fb.update({
                "cookiefile": temp_cookie,
                "cachedir": False,
                "user_agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/121.0.0.0 Safari/537.36"
                ),
            })
            try:
                with yt_dlp.YoutubeDL(opts_fb) as ydl:
                    return action(ydl)
            finally:
                if os.path.exists(temp_cookie):
                    os.remove(temp_cookie)

    def _get_stream_url(self, link: str, video: bool = False) -> str | None:
        """yt-dlp se direct stream URL lo — file download nahi hogi."""
        fmt = (
            "(bestvideo[height<=?720][width<=?1280][ext=mp4])+(bestaudio[ext=m4a])/best[ext=mp4]/best"
            if video
            else "bestaudio/best"
        )
        opts = {
            "format": fmt,
            "quiet": True,
            "no_warnings": True,
            "geo_bypass": True,
            "nocheckcertificate": True,
            "skip_download": True,
        }
        try:
            info = self._yt_dlp_call_with_fallback(
                lambda ydl: ydl.extract_info(link, download=False), opts
            )
            if not info:
                return None
            # Playlist ya single video
            if "entries" in info:
                info = info["entries"][0]
            return info.get("url")
        except Exception as e:
            LOGGER(__name__).error(f"yt-dlp stream URL failed: {e}")
            return None

    def _download_file(self, link: str, video: bool = False) -> str | None:
        """yt-dlp se file download karo — stream fail hone pe fallback."""
        ext = "mp4" if video else "%(ext)s"
        video_id = link.split("v=")[-1].split("&")[0] if "v=" in link else link.split("/")[-1]
        os.makedirs("downloads", exist_ok=True)

        fmt = (
            "(bestvideo[height<=?720][width<=?1280][ext=mp4])+(bestaudio[ext=m4a])/best[ext=mp4]/best"
            if video
            else "bestaudio/best"
        )
        opts = {
            "format": fmt,
            "outtmpl": f"downloads/{video_id}.{ext}",
            "geo_bypass": True,
            "nocheckcertificate": True,
            "quiet": True,
            "no_warnings": True,
            "prefer_ffmpeg": True,
        }
        if video:
            opts["merge_output_format"] = "mp4"

        try:
            def action(ydl):
                info = ydl.extract_info(link, download=False)
                if "entries" in info:
                    info = info["entries"][0]
                fpath = ydl.prepare_filename(info)
                if not os.path.exists(fpath):
                    ydl.download([link])
                return fpath

            return self._yt_dlp_call_with_fallback(action, opts)
        except Exception as e:
            LOGGER(__name__).error(f"yt-dlp download failed: {e}")
            return None

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        return bool(re.search(self.regex, link))

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)
        text = ""
        offset = None
        length = None
        for message in messages:
            if offset:
                break
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption
                        offset, length = entity.offset, entity.length
                        break
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        if offset is None:
            return None
        return text[offset: offset + length]

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
            duration_min = result["duration"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            vidid = result["id"]
            duration_sec = int(time_to_seconds(duration_min)) if duration_min else 0
        return title, duration_min, duration_sec, thumbnail, vidid

    async def title(self, link: str, videoid: Union[bool, str] = None):
        title, _, _, _, _ = await self.details(link, videoid)
        return title

    async def duration(self, link: str, videoid: Union[bool, str] = None):
        _, duration, _, _, _ = await self.details(link, videoid)
        return duration

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        _, _, _, thumbnail, _ = await self.details(link, videoid)
        return thumbnail

    async def video(self, link: str, videoid: Union[bool, str] = None, stream: bool = True):
        """Direct stream URL lo yt-dlp se — koi API nahi."""
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]

        loop = asyncio.get_running_loop()
        try:
            url = await loop.run_in_executor(
                None, lambda: self._get_stream_url(link, video=stream)
            )
            if url:
                return 1, url
            return 0, "yt-dlp: Could not extract stream URL"
        except Exception as e:
            return 0, str(e)

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        if videoid:
            link = self.listbase + link
        if "&" in link:
            link = link.split("&")[0]

        proc = await asyncio.create_subprocess_shell(
            f"yt-dlp -i --get-id --flat-playlist --playlist-end {limit} --skip-download {link}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        out, errorz = await proc.communicate()
        if errorz:
            if "unavailable videos are hidden" in errorz.decode("utf-8").lower():
                output = out.decode("utf-8")
            else:
                output = errorz.decode("utf-8")
        else:
            output = out.decode("utf-8")

        try:
            result = [x for x in output.split("\n") if x]
        except:
            result = []
        return result

    async def track(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
            duration_min = result["duration"]
            vidid = result["id"]
            yturl = result["link"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        track_details = {
            "title": title,
            "link": yturl,
            "vidid": vidid,
            "duration_min": duration_min,
            "thumb": thumbnail,
        }
        return track_details, vidid

    async def formats(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]

        def get_fmt():
            opts = {"quiet": True, "no_warnings": True}
            info = self._yt_dlp_call_with_fallback(
                lambda ydl: ydl.extract_info(link, download=False), opts
            )
            formats_available = []
            for fmt in info.get("formats", []):
                try:
                    if "dash" not in str(fmt.get("format", "")).lower():
                        formats_available.append({
                            "format": fmt.get("format"),
                            "filesize": fmt.get("filesize"),
                            "format_id": fmt.get("format_id"),
                            "ext": fmt.get("ext"),
                            "format_note": fmt.get("format_note"),
                            "yturl": link,
                        })
                except:
                    continue
            return formats_available

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, get_fmt), link

    async def slider(self, link: str, query_type: int, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        a = VideosSearch(link, limit=10)
        result = (await a.next()).get("result")
        title = result[query_type]["title"]
        duration_min = result[query_type]["duration"]
        vidid = result[query_type]["id"]
        thumbnail = result[query_type]["thumbnails"][0]["url"].split("?")[0]
        return title, duration_min, thumbnail, vidid

    async def suggestions(self, keyword: str, limit: int = 2):
        try:
            results = VideosSearch(keyword, limit=limit + 5)
            data = (await results.next())["result"]
            suggestions = []
            for item in data:
                suggestions.append({
                    "title": item["title"],
                    "id": item["id"],
                    "duration": item["duration"],
                    "thumb": item["thumbnails"][0]["url"].split("?")[0],
                })
            return suggestions[1: limit + 1]
        except Exception:
            return []

    async def download(
        self,
        link: str,
        mystic,
        video: Union[bool, str] = None,
        videoid: Union[bool, str] = None,
        songaudio: Union[bool, str] = None,
        songvideo: Union[bool, str] = None,
        format_id: Union[bool, str] = None,
        title: Union[bool, str] = None,
    ) -> str:
        if videoid:
            link = self.base + link
        loop = asyncio.get_running_loop()

        # /song command — file download
        def song_video_dl():
            opts = {
                "format": f"{format_id}+140",
                "outtmpl": f"downloads/{title}",
                "geo_bypass": True, "nocheckcertificate": True,
                "quiet": True, "no_warnings": True,
                "prefer_ffmpeg": True, "merge_output_format": "mp4",
            }
            self._yt_dlp_call_with_fallback(lambda ydl: ydl.download([link]), opts)

        def song_audio_dl():
            opts = {
                "format": format_id,
                "outtmpl": f"downloads/{title}.%(ext)s",
                "geo_bypass": True, "nocheckcertificate": True,
                "quiet": True, "no_warnings": True,
                "prefer_ffmpeg": True,
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }],
            }
            self._yt_dlp_call_with_fallback(lambda ydl: ydl.download([link]), opts)

        if songvideo:
            await loop.run_in_executor(None, song_video_dl)
            return f"downloads/{title}.mp4"

        if songaudio:
            await loop.run_in_executor(None, song_audio_dl)
            return f"downloads/{title}.mp3"

        # /play command — stream URL pehle, file fallback
        # Step 1: Direct stream URL (no download needed)
        stream_url = await loop.run_in_executor(
            None, lambda: self._get_stream_url(link, video=bool(video))
        )
        if stream_url:
            return stream_url, None

        # Step 2: Download file fallback
        LOGGER(__name__).warning(f"Stream URL failed for {link}, downloading file")
        file_path = await loop.run_in_executor(
            None, lambda: self._download_file(link, video=bool(video))
        )
        if file_path:
            return file_path, True

        return None, None
