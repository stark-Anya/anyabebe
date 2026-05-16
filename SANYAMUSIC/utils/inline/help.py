# -----------------------------------------------
# 🔸 SanyaMusic Project
# 🔹 Developed & Maintained by: Stark (https://github.com/urstark)
# 📅 Copyright © 2022 – All Rights Reserved
# -----------------------------------------------
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ButtonStyle
from SANYAMUSIC import app


def help_pannel(_, start: bool = False):
    buttons = [
        [
            InlineKeyboardButton(text="⌯ ᴍᴜsɪᴄ ⌯", callback_data="help_category music", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton(text="⌯ ᴍᴧηᴧɢᴇᴍᴇηᴛ ⌯", callback_data="help_category management", style=ButtonStyle.PRIMARY),
        ],
        [
            InlineKeyboardButton(text="⌯ ᴛᴏᴏʟs ⌯", callback_data="help_category tools", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton(text="⌯ ғᴜɴ ⌯", callback_data="help_category fun", style=ButtonStyle.PRIMARY),
        ],
        [
            InlineKeyboardButton(text="⌯ ʙᴏᴛ sᴇᴛᴛɪηɢs ⌯", callback_data="help_category settings", style=ButtonStyle.PRIMARY),
        ],
        [
            InlineKeyboardButton(text=_["BACK_BUTTON"], callback_data="settings_back_helper", style=ButtonStyle.SUCCESS),
            InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close", style=ButtonStyle.DANGER),
        ],
    ]
    return InlineKeyboardMarkup(buttons)


def help_category_pannel(_, category):
    buttons = []

    if category == "music":
        buttons = [
            [
                InlineKeyboardButton(text=_["H_B_11"], callback_data="help_callback hb11 music", style=ButtonStyle.PRIMARY),
                InlineKeyboardButton(text="ᴀᴅᴍɪɴ", callback_data="help_callback hb1 music", style=ButtonStyle.PRIMARY),
            ],
            [
                InlineKeyboardButton(text=_["H_B_6"], callback_data="help_callback hb6 music", style=ButtonStyle.PRIMARY),
                InlineKeyboardButton(text=_["H_B_8"], callback_data="help_callback hb8 music", style=ButtonStyle.PRIMARY),
            ],
            [
                InlineKeyboardButton(text=_["H_B_12"], callback_data="help_callback hb12 music", style=ButtonStyle.PRIMARY),
                InlineKeyboardButton(text=_["H_B_13"], callback_data="help_callback hb13 music", style=ButtonStyle.PRIMARY),
            ],
            [
                InlineKeyboardButton(text=_["H_B_15"], callback_data="help_callback hb15 music", style=ButtonStyle.PRIMARY),
                InlineKeyboardButton(text=_["H_B_14"], callback_data="help_callback hb14 music", style=ButtonStyle.PRIMARY),
            ],
            [
                InlineKeyboardButton(text="ᴠᴏɪᴄᴇ ᴄʜᴀᴛ", callback_data="help_callback hb42 music", style=ButtonStyle.PRIMARY),
                InlineKeyboardButton(text="ᴄʜᴀɴɴᴇʟ ᴀᴅᴍɪɴ", callback_data="help_callback hb47 music", style=ButtonStyle.PRIMARY),
            ],
        ]
    elif category == "management":
        buttons = [
            [
                InlineKeyboardButton(text=_["H_B_2"], callback_data="help_callback hb2 management", style=ButtonStyle.PRIMARY),
                InlineKeyboardButton(text=_["H_B_7"], callback_data="help_callback hb7 management", style=ButtonStyle.PRIMARY),
            ],
            [
                InlineKeyboardButton(text=_["H_B_4"], callback_data="help_callback hb4 management", style=ButtonStyle.PRIMARY),
                InlineKeyboardButton(text=_["H_B_5"], callback_data="help_callback hb5 management", style=ButtonStyle.PRIMARY),
            ],
            [
                InlineKeyboardButton(text="ɢʀᴏᴜᴘ sᴇᴛᴛɪɴɢs", callback_data="help_callback hb17 management", style=ButtonStyle.PRIMARY),
                InlineKeyboardButton(text=_["H_B_23"], callback_data="help_callback hb23 management", style=ButtonStyle.PRIMARY),
            ],
            [
                InlineKeyboardButton(text="ᴀᴘᴘʀᴏᴠᴇ", callback_data="help_callback hb36 management", style=ButtonStyle.PRIMARY),
                InlineKeyboardButton(text="ғɪʟᴛᴇʀs", callback_data="help_callback hb37 management", style=ButtonStyle.PRIMARY),
            ],
            [
                InlineKeyboardButton(text="ɴᴏᴛᴇs", callback_data="help_callback hb39 management", style=ButtonStyle.PRIMARY),
                InlineKeyboardButton(text="ɢʀᴏᴜᴘ ɪɴғᴏ", callback_data="help_callback hb46 management", style=ButtonStyle.PRIMARY),
            ],
            [
                InlineKeyboardButton(text="ɢʀᴏᴜᴘ ᴍᴏᴅ", callback_data="help_callback hb49 management", style=ButtonStyle.PRIMARY),
                InlineKeyboardButton(text="ᴘʀᴏᴛᴇᴄᴛɪᴏɴ", callback_data="help_callback hb52 management", style=ButtonStyle.PRIMARY),
            ],
            [
                InlineKeyboardButton(text=_["H_B_28"], callback_data="help_callback hb28 management", style=ButtonStyle.PRIMARY),
            ],
        ]
    elif category == "tools":
        buttons = [
            [
                InlineKeyboardButton(text=_["H_B_16"], callback_data="help_callback hb16 tools", style=ButtonStyle.PRIMARY),
                InlineKeyboardButton(text=_["H_B_22"], callback_data="help_callback hb22 tools", style=ButtonStyle.PRIMARY),
            ],
            [
                InlineKeyboardButton(text=_["H_B_24"], callback_data="help_callback hb24 tools", style=ButtonStyle.PRIMARY),
                InlineKeyboardButton(text=_["H_B_27"], callback_data="help_callback hb27 tools", style=ButtonStyle.PRIMARY),
            ],
            [
                InlineKeyboardButton(text=_["H_B_31"], callback_data="help_callback hb31 tools", style=ButtonStyle.PRIMARY),
                InlineKeyboardButton(text="ᴍᴇᴅɪᴀ/ᴡᴇʙ", callback_data="help_callback hb43 tools", style=ButtonStyle.PRIMARY),
            ],
            [
                InlineKeyboardButton(text="ᴇxᴛʀᴀ ᴛᴏᴏʟs", callback_data="help_callback hb21 tools", style=ButtonStyle.PRIMARY),
                InlineKeyboardButton(text=_["H_B_20"], callback_data="help_callback hb20 tools", style=ButtonStyle.PRIMARY),
            ],
            [
                InlineKeyboardButton(text=_["H_B_25"], callback_data="help_callback hb25 tools", style=ButtonStyle.PRIMARY),
                InlineKeyboardButton(text=_["H_B_18"], callback_data="help_callback hb18 tools", style=ButtonStyle.PRIMARY),
            ],
        ]
    elif category == "fun":
        buttons = [
            [
                InlineKeyboardButton(text=_["H_B_26"], callback_data="help_callback hb26 fun", style=ButtonStyle.PRIMARY),
                InlineKeyboardButton(text=_["H_B_29"], callback_data="help_callback hb29 fun", style=ButtonStyle.PRIMARY),
            ],
            [
                InlineKeyboardButton(text=_["H_B_32"], callback_data="help_callback hb32 fun", style=ButtonStyle.PRIMARY),
                InlineKeyboardButton(text="ᴄᴏᴜᴘʟᴇs", callback_data="help_callback hb40 fun", style=ButtonStyle.PRIMARY),
            ],
            [
                InlineKeyboardButton(text="ᴍɪsᴄ ᴇxᴛʀᴀ", callback_data="help_callback hb51 fun", style=ButtonStyle.PRIMARY),
                InlineKeyboardButton(text=_["H_B_33"], callback_data="help_callback hb33 fun", style=ButtonStyle.PRIMARY),
            ],
            [
                InlineKeyboardButton(text=_["H_B_30"], callback_data="help_callback hb30 fun", style=ButtonStyle.PRIMARY),
                InlineKeyboardButton(text="ɢᴇɴᴇʀᴀʟ ᴛᴀɢ", callback_data="help_callback hb19 fun", style=ButtonStyle.PRIMARY),
            ],
            [
                InlineKeyboardButton(text="sᴘᴇᴄɪᴀʟ ᴛᴀɢ", callback_data="help_callback hb50 fun", style=ButtonStyle.PRIMARY),
            ],
        ]
    elif category == "settings":
        buttons = [
            [
                InlineKeyboardButton(text=_["H_B_10"], callback_data="help_callback hb10 settings", style=ButtonStyle.PRIMARY),
                InlineKeyboardButton(text="sᴇᴛᴛɪɴɢs", callback_data="help_callback hb44 settings", style=ButtonStyle.PRIMARY),
            ],
            [
                InlineKeyboardButton(text="ᴀssɪsᴛᴀɴᴛ", callback_data="help_callback hb38 settings", style=ButtonStyle.PRIMARY),
                InlineKeyboardButton(text=_["H_B_35"], callback_data="help_callback hb35 settings", style=ButtonStyle.PRIMARY),
            ],
            [
                InlineKeyboardButton(text=_["H_B_3"], callback_data="help_callback hb3 settings", style=ButtonStyle.PRIMARY),
                InlineKeyboardButton(text=_["H_B_9"], callback_data="help_callback hb9 settings", style=ButtonStyle.PRIMARY),
            ],
            [
                InlineKeyboardButton(text="ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ", callback_data="help_callback hb48 settings", style=ButtonStyle.PRIMARY),
                InlineKeyboardButton(text="ᴅᴇᴠ ᴛᴏᴏʟs", callback_data="help_callback hb45 settings", style=ButtonStyle.PRIMARY),
            ],
            [
                InlineKeyboardButton(text=_["H_B_34"], callback_data="help_callback hb34 settings", style=ButtonStyle.PRIMARY),
            ],
        ]

    buttons.append(
        [
            InlineKeyboardButton(text=_["BACK_BUTTON"], callback_data="open_help_panel", style=ButtonStyle.SUCCESS),
            InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close", style=ButtonStyle.DANGER),
        ]
    )
    return InlineKeyboardMarkup(buttons)


def help_back_markup(_, category):
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=_["BACK_BUTTON"],
                    callback_data=f"help_category {category}",
                    style=ButtonStyle.SUCCESS,
                ),
                InlineKeyboardButton(
                    text=_["CLOSE_BUTTON"],
                    callback_data="close",
                    style=ButtonStyle.DANGER,
                ),
            ]
        ]
    )


def private_help_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_4"],
                url=f"https://t.me/{app.username}?start=help",
                style=ButtonStyle.PRIMARY,
            ),
        ],
    ]
    return buttons
