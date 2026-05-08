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
from typing import Union
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from SANYAMUSIC import app


def help_pannel(_, start: bool = False):
    buttons = [
        [
            InlineKeyboardButton(text="◈ ᴍᴜsɪᴄ ◈", callback_data="help_category music"),
            InlineKeyboardButton(text="◈ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ◈", callback_data="help_category management"),
        ],
        [
            InlineKeyboardButton(text="◈ ᴛᴏᴏʟs ◈", callback_data="help_category tools"),
            InlineKeyboardButton(text="◈ ғᴜɴ ◈", callback_data="help_category fun"),
        ],
        [
            InlineKeyboardButton(text="◈ ʙᴏᴛ sᴇᴛᴛɪɴɢs ◈", callback_data="help_category settings"),
        ],
    ]

    if start:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=_["BACK_BUTTON"],
                    callback_data="settings_back_helper",
                ),
                InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close"),
            ]
        )
    else:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=_["BACK_BUTTON"],
                    callback_data="settings_back_helper",
                ),
                InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close"),
            ]
        )

    return InlineKeyboardMarkup(buttons)


def help_category_pannel(_, category):
    buttons = []

    if category == "music":
        buttons = [
            [InlineKeyboardButton(text=_["H_B_11"], callback_data="help_callback hb11 music"), InlineKeyboardButton(text="ᴀᴅᴍɪɴ", callback_data="help_callback hb1 music")],
            [InlineKeyboardButton(text=_["H_B_6"], callback_data="help_callback hb6 music"), InlineKeyboardButton(text=_["H_B_8"], callback_data="help_callback hb8 music")],
            [InlineKeyboardButton(text=_["H_B_12"], callback_data="help_callback hb12 music"), InlineKeyboardButton(text=_["H_B_13"], callback_data="help_callback hb13 music")],
            [InlineKeyboardButton(text=_["H_B_15"], callback_data="help_callback hb15 music"), InlineKeyboardButton(text=_["H_B_14"], callback_data="help_callback hb14 music")],
            [InlineKeyboardButton(text="ᴠᴏɪᴄᴇ ᴄʜᴀᴛ", callback_data="help_callback hb42 music"), InlineKeyboardButton(text="ᴄʜᴀɴɴᴇʟ ᴀᴅᴍɪɴ", callback_data="help_callback hb47 music")],
        ]
    elif category == "management":
        buttons = [
            [InlineKeyboardButton(text=_["H_B_2"], callback_data="help_callback hb2 management"), InlineKeyboardButton(text=_["H_B_7"], callback_data="help_callback hb7 management")],
            [InlineKeyboardButton(text=_["H_B_4"], callback_data="help_callback hb4 management"), InlineKeyboardButton(text=_["H_B_5"], callback_data="help_callback hb5 management")],
            [InlineKeyboardButton(text="ɢʀᴏᴜᴘ sᴇᴛᴛɪɴɢs", callback_data="help_callback hb17 management"), InlineKeyboardButton(text=_["H_B_23"], callback_data="help_callback hb23 management")],
            [InlineKeyboardButton(text="ᴀᴘᴘʀᴏᴠᴇ", callback_data="help_callback hb36 management"), InlineKeyboardButton(text="ғɪʟᴛᴇʀs", callback_data="help_callback hb37 management")],
            [InlineKeyboardButton(text="ɴᴏᴛᴇs", callback_data="help_callback hb39 management"), InlineKeyboardButton(text="ɢʀᴏᴜᴘ ɪɴғᴏ", callback_data="help_callback hb46 management")],
            [InlineKeyboardButton(text="ɢʀᴏᴜᴘ ᴍᴏᴅ", callback_data="help_callback hb49 management")],
        ]
    elif category == "tools":
        buttons = [
            [InlineKeyboardButton(text=_["H_B_16"], callback_data="help_callback hb16 tools"), InlineKeyboardButton(text=_["H_B_22"], callback_data="help_callback hb22 tools")],
            [InlineKeyboardButton(text=_["H_B_24"], callback_data="help_callback hb24 tools"), InlineKeyboardButton(text=_["H_B_25"], callback_data="help_callback hb25 tools")],
            [InlineKeyboardButton(text=_["H_B_31"], callback_data="help_callback hb31 tools"), InlineKeyboardButton(text=_["H_B_18"], callback_data="help_callback hb18 tools")],
            [InlineKeyboardButton(text="ᴇxᴛʀᴀ ᴛᴏᴏʟs", callback_data="help_callback hb21 tools"), InlineKeyboardButton(text=_["H_B_20"], callback_data="help_callback hb20 tools")],
        ]
    elif category == "fun":
        buttons = [
            [InlineKeyboardButton(text=_["H_B_26"], callback_data="help_callback hb26 fun"), InlineKeyboardButton(text=_["H_B_29"], callback_data="help_callback hb29 fun")],
            [InlineKeyboardButton(text=_["H_B_32"], callback_data="help_callback hb32 fun"), InlineKeyboardButton(text="ᴄᴏᴜᴘʟᴇs", callback_data="help_callback hb40 fun")],
            [InlineKeyboardButton(text="ᴍɪsᴄ ᴇxᴛʀᴀ", callback_data="help_callback hb51 fun"), InlineKeyboardButton(text=_["H_B_33"], callback_data="help_callback hb33 fun")],
            [InlineKeyboardButton(text=_["H_B_30"], callback_data="help_callback hb30 fun"), InlineKeyboardButton(text="ɢᴇɴᴇʀᴀʟ ᴛᴀɢ", callback_data="help_callback hb19 fun")],
            [InlineKeyboardButton(text="sᴘᴇᴄɪᴀʟ ᴛᴀɢ", callback_data="help_callback hb50 fun")],
        ]
    elif category == "settings":
        buttons = [
            [InlineKeyboardButton(text=_["H_B_10"], callback_data="help_callback hb10 settings"), InlineKeyboardButton(text="sᴇᴛᴛɪɴɢs", callback_data="help_callback hb44 settings")],
            [InlineKeyboardButton(text="ᴀssɪsᴛᴀɴᴛ", callback_data="help_callback hb38 settings"), InlineKeyboardButton(text=_["H_B_35"], callback_data="help_callback hb35 settings")],
            [InlineKeyboardButton(text=_["H_B_3"], callback_data="help_callback hb3 settings"), InlineKeyboardButton(text=_["H_B_9"], callback_data="help_callback hb9 settings")],
            [InlineKeyboardButton(text="ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ", callback_data="help_callback hb48 settings"), InlineKeyboardButton(text=_["H_B_34"], callback_data="help_callback hb34 settings")],
        ]

    buttons.append(
        [
            InlineKeyboardButton(text=_["BACK_BUTTON"], callback_data="open_help_panel"),
            InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close"),
        ]
    )
    return InlineKeyboardMarkup(buttons)


def help_back_markup(_, category):
    upl = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=_["BACK_BUTTON"],
                    callback_data=f"help_category {category}",
                ),
                InlineKeyboardButton(
                    text=_["CLOSE_BUTTON"],
                    callback_data="close",
                ),
            ]
        ]
    )
    return upl


def private_help_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_4"],
                url=f"https://t.me/{app.username}?start=help",
            ),
        ],
    ]
    return buttons
