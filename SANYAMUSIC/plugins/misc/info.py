import asyncio
import os
from PIL import Image, ImageDraw
from SANYAMUSIC import app
from pyrogram import filters, enums
from pyrogram.types import Message
from typing import Union

bg_path = "SANYAMUSIC/assets/userinfo.png"
font_path = "SANYAMUSIC/assets/hiroko.ttf"
DEFAULT_PROFILE_IMAGE = "SANYAMUSIC/assets/upic.png"

INFO_TEXT = """<b>
[ᯤ] 𝗨𝗦𝗘𝗥 𝗜𝗡𝗙𝗢𝗥𝗠𝗔𝗧𝗜𝗢𝗡 [ᯤ]

[🍹] ᴜsᴇʀ ɪᴅ ‣ <code>{}</code>
[💓] ғɪʀsᴛ ɴᴀᴍᴇ ‣ {}
[💗] ʟᴀsᴛ ɴᴀᴍᴇ ‣ {}
[🍷] ᴜsᴇʀɴᴀᴍᴇ ‣ <code>{}</code>
[🍬] ᴍᴇɴᴛɪᴏɴ ‣ {}
[🍁] ʟᴀsᴛ sᴇᴇɴ ‣ {}
[🎫] ᴅᴄ ɪᴅ ‣ {}
[🗨️] ʙɪᴏ ‣ <code>{}</code>

☉━━☉━━☉━侖━☉━━☉━━☉</b>"""


def get_font(size):
    from PIL import ImageFont
    try:
        return ImageFont.truetype(font_path, size)
    except:
        return ImageFont.load_default()


async def get_userinfo_img(user_id, profile_path):
    bg = Image.open(bg_path)
    img = Image.open(profile_path).convert("RGBA")
    mask = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.pieslice([(0, 0), img.size], 0, 360, fill=255)
    circular_img = Image.new("RGBA", img.size, (0, 0, 0, 0))
    circular_img.paste(img, (0, 0), mask)
    resized = circular_img.resize((400, 400))
    bg.paste(resized, (440, 160), resized)
    img_draw = ImageDraw.Draw(bg)
    img_draw.text(
        (529, 627),
        text=str(user_id).upper(),
        font=get_font(46),
        fill=(255, 255, 255),
    )
    path = f"./userinfo_img_{user_id}.png"
    bg.save(path)
    return path


async def userstatus(user_id):
    try:
        user = await app.get_users(user_id)
        x = user.status
        if x == enums.UserStatus.RECENTLY:
            return "Recently"
        elif x == enums.UserStatus.LAST_WEEK:
            return "Last Week"
        elif x == enums.UserStatus.LONG_AGO:
            return "Long Time Ago"
        elif x == enums.UserStatus.OFFLINE:
            return "Offline"
        elif x == enums.UserStatus.ONLINE:
            return "Online"
        else:
            return "Unknown"
    except:
        return "Unknown"


@app.on_message(filters.command(["info", "userinfo"], prefixes=["/", "!", "%", ",", "", ".", "@", "#"]))
async def userinfo(_, message: Message):
    chat_id = message.chat.id

    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    elif len(message.command) == 2:
        user_id = message.text.split(None, 1)[1]
    else:
        user_id = message.from_user.id

    try:
        user_info = await app.get_chat(user_id)
        user = await app.get_users(user_id)

        status = await userstatus(user.id)
        uid = user_info.id
        dc_id = user.dc_id or "N/A"
        first_name = user_info.first_name or "N/A"
        last_name = user_info.last_name or "No last name"
        username = f"@{user_info.username}" if user_info.username else "No Username"
        mention = user.mention
        bio = user_info.bio or "No bio set"

        # User ka actual PFP download karo
        pfp_path = DEFAULT_PROFILE_IMAGE
        try:
            photos = await app.get_profile_photos(user.id, limit=1)
            if photos:
                pfp_path = await app.download_media(
                    photos[0].file_id,
                    file_name=f"pfp_{uid}.jpg"
                )
        except Exception:
            pass

        final_img_path = await get_userinfo_img(uid, pfp_path)

        await app.send_photo(
            chat_id,
            photo=final_img_path,
            caption=INFO_TEXT.format(
                uid, first_name, last_name,
                username, mention, status, dc_id, bio
            ),
            parse_mode=enums.ParseMode.HTML,
            reply_to_message_id=message.id,
        )

    except Exception as e:
        await message.reply_text(
            f"<b>Error:</b> <code>{str(e)}</code>",
            parse_mode=enums.ParseMode.HTML,
        )
    finally:
        # Cleanup
        for f in [f"./userinfo_img_{user_id}.png", f"pfp_{user_id}.jpg"]:
            try:
                if os.path.exists(f):
                    os.remove(f)
            except:
                pass
