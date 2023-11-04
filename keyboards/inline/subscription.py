from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

check_button = InlineKeyboardMarkup(
    inline_keyboard=[[
        InlineKeyboardButton(text="Obuna bo'ldim", callback_data="check_subs")
    ]]
)
# channels_inline = InlineKeyboardMarkup(
#     inline_keyboard=[
#         [
#             InlineKeyboardButton(text="sariqdev", url="https://t.me/sariqdev")
#         ],
#         [
#             InlineKeyboardButton(text="c# darslarii", url="https://t.me/c_sharp_darslari"),
#         ],
#         [
#             InlineKeyboardButton(text="obuna bo'ldim", callback_data="check_subs")
#         ]
#     ]
# )
