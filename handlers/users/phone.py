from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from keyboards.default.menuKeyboard import menu
from loader import dp, db
from states.anketa import data


# Echo bot
@dp.message_handler(state=data.phoneNumber, content_types=types.ContentTypes.CONTACT)
async def contact(message: types.Message, state: FSMContext):
    num = message.contact.phone_number
    if not num.startswith('+'):
        num = '+' + num
    id = message.from_user.id
    db.update_user_phone(id, num)
    deeplink = ""
    users = db.select_all_users()
    for i in users:
        if str(i[0]) == str(message.from_user.id):
            deeplink = str(i[4])
    # await message.answer(deeplink)
    if deeplink != "0":
        r = db.select_all_sorovnoma()
        l = []
        sorovnoma = deeplink.split("W")[1]
        guruh = deeplink.split("W")[0]
        for i in r:
            if str(i[1]) == str(sorovnoma) and str(i[4]) == str(guruh):
                l.append(i[2])
        if len(l) == 0:
            await message.reply(
                "Bu so'rovnoma hozirda mavjud emas. Kerakli so'rovnomani tanlash uchun pastdagi tugmachalardan "
                "foydalaning 👇", reply_markup=menu)
        else:
            l = list(set(l))
            menus = ReplyKeyboardMarkup(resize_keyboard=True)
            menus.add(KeyboardButton(text="Bekor qilish"))
            for i in l:
                keyboard = KeyboardButton(text=f"{i}")
                menus.add(keyboard)
            await message.reply(f"{sorovnoma} da kimga ovoz bermoqchisiz? Tugmachalardan foydalanib tanlang: 👇",
                                reply_markup=menus)
            await data.variant_tanlash.set()
    else:
        await message.answer("🎉 Siz botda to'liq ro'yxatdan o'tdingiz! Endi pastdagi tugmacha orqali bemalol ovoz berishingiz mumkin! 👇", reply_markup=menu)
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
