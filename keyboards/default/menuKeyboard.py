from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Ovoz berish')
        ],
    ],
    resize_keyboard=True,
)

admin = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="statistika")
        ],
        [
            KeyboardButton(text="To'liq statistika (fayl)"),
        ],
        [
            KeyboardButton(text='Reklama yuborish')
        ]
    ],
    resize_keyboard=True,
)


phoneNumber = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Telefon raqamimni yuborish", request_contact=True)
        ]
    ],
    resize_keyboard=True
)

# location = ReplyKeyboardMarkup(
#     keyboard=[
#         [
#             KeyboardButton(text="Telefon raqamimni yuborish", request_location=True)
#         ]
#     ],
#     resize_keyboard=True
# )