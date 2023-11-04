from aiogram import types
import sqlite3

from loader import dp, db, bot
from keyboards.default.menuKeyboard import menu
from utils.db_api.sqlite import Database
from states.anketa import data
from aiogram.dispatcher import FSMContext


# Echo bot
@dp.message_handler(state=data.phoneNumber, content_types=types.ContentTypes.CONTACT)
async def contact(msg: types.Message, state: FSMContext):
    num = msg.contact.phone_number
    if not num.startswith('+'):
        num = '+' + num
    id = msg.from_user.id
    db.update_user_phone(id, num)
    await msg.answer("Siz botda to'liq ro'yxatdan o'tdingiz! Endi pastdagi tugmacha orqali bemalol ovoz berishingiz mumkin!", reply_markup=menu)
    await state.finish()
    # if not num.startswith('+'):
    #     num = '+' + num
    # await msg.answer("Qabul qildim")
    # await msg.answer(num)
    # if not num.startswith('+998'):
    #     await msg.answer(
    #         "❎ Kechirasiz, botdan faqat O'zbek telefon raqamlari orqali ro'yxatdan o'tish mumkin. Siz bu telegram "
    #         "hisobi bilan ishtirok eta olmaysiz")
    #     await state.finish()
    # else:
    #     datas = await state.get_data()
    #     name = datas.get("name")
    #     deeplink = datas.get("deeplink")
    #
    #     try:
    #         db.add_user(id=id, name=str(name), added=0, phone=str(num))
    #         await msg.answer("Siz botda to'liq ro'yxatdan o'tdingiz! Tanlovda ishtirok etish tugmasini bosing va "
    #                          "do'stlaringizni taklif qilib bal to'plang!",reply_markup=menu)
    #         if deeplink != "0":
    #             db.update_user_added(deeplink, 1)
    #             await bot.send_message(deeplink, f"siz {msg.from_user.full_name} ni takli qildingiz")
    #     except sqlite3.IntegrityError as err:
    #         pass
    #     await state.finish()
