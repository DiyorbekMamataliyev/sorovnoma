import random

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from captcha.image import ImageCaptcha

from data.config import CHANNELS
from keyboards.default.menuKeyboard import menu
from keyboards.default.menuKeyboard import phoneNumber
from keyboards.inline.subscription import check_button
from loader import db, dp, bot
from states.anketa import data
from utils.misc import subscription


@dp.callback_query_handler(text="check_subs")
@dp.callback_query_handler(text="check_subs", state=data.kanalga_obuna)
@dp.callback_query_handler(text="check_subs", state=data.all_states)
async def checker(call: types.CallbackQuery, state: FSMContext):
    result = "Barcha kanallarimizga obuna bo'lmadingiz! Avval obuna bo'ling:\n"
    final_status = True
    for channel in CHANNELS:
        status = await subscription.check(user_id=call.from_user.id, channel=channel)
        final_status *= status
        channel = await bot.get_chat(channel)
        if not status:
            invite_link = await channel.export_invite_link()
            result += f"👉 <a href='{invite_link}'>{channel.title}</a>\n"

    if final_status:
        await call.message.answer("Ajoyib! Barcha kanallarimizga obuna bo'ldingiz!", reply_markup=menu)
        await call.message.delete()
        l = db.select_all_users()
        b = False
        for i in l:
            if i[0] == call.from_user.id:
                if i[1] == '0':
                    b = True
                    break
        if b:
            await call.message.answer(
                "Ro'yxatdan o'tishni tugallash uchun, pastdagi tugma orqali telefon raqamingizni yuboring: ",
                reply_markup=phoneNumber)
            await data.phoneNumber.set()

    else:
        await call.message.answer(f"{result}",
                                  disable_web_page_preview=True, reply_markup=check_button)


async def send_captcha(user_id: int):
    # Create an image instance of the given size
    image = ImageCaptcha(width=280, height=90, font_sizes=(30,), fonts=['tahoma_0.ttf'])
    # Image captcha text
    captcha_text = "     " + str(random.randint(1000, 9999)).replace('7', '1')

    # generate the image of the given text
    data = image.generate(captcha_text)

    # write the image on the given file and save it
    image.write(captcha_text, 'captcha.png')

    image_file = types.InputFile('captcha.png')
    await bot.send_photo(chat_id=user_id, photo=image_file)
    return captcha_text


@dp.message_handler(Command("start"))
async def sender(message: types.Message):
    a = message.get_args()
    if not a:
        a = "0"
    l = db.select_all_users()
    b = True
    for i in l:
        if i[0] == message.from_user.id:
            b = False
            break
    if b:
        db.add_user(id=message.from_user.id)
    else:
        db.update_user_bloklaganmi(message.from_user.id, '0')

    final_status = True
    result = ""
    for channel in CHANNELS:
        status = await subscription.check(user_id=message.from_user.id, channel=channel)
        final_status *= status
        channel = await bot.get_chat(channel)
        if not status:
            invite_link = await channel.export_invite_link()
            result += f"👉 <a href='{invite_link}'>{channel.title}</a>\n"
    if not final_status:
        await message.answer(f"Botdan foydalanish uchun, quyidagi kanallarga obuna bo'ling:\n {result}",
                             reply_markup=check_button, disable_web_page_preview=True)
        await data.kanalga_obuna.set()
    else:
        r = db.select_all_users()
        b = True
        for i in r:
            if i[0] == message.from_user.id:
                if i[1] == "0":
                    b = False
                    await message.answer(
                        "To'liq ro'yxatdan o'tish uchun pastdagi tugma orqali telefon raqamingizni yuboring: ",
                        reply_markup=phoneNumber)
                    await data.phoneNumber.set()
                    break
        if b:
            if a != "0":
                r = db.select_all_sorovnoma()
                l = []
                sorovnoma = ""
                guruh = ""
                for i in r:
                    if str(i[0]) == str(a):
                        l.append(i[2])
                        sorovnoma = str(i[1])
                        guruh = str(i[4])
                if len(l) == 0:
                    await message.reply(
                        "Bu so'rovnoma hozirda mavjud emas. Kerakli so'rovnomani tanlash uchun pastdagi tugmachalardan "
                        "foydalaning 👇", reply_markup=menu)
                else:
                    users = db.select_all_users()
                    deeplink = f"{guruh}W{sorovnoma}W"
                    db.update_user_deeplink(message.from_user.id, deeplink)
                    l = list(set(l))
                    menus = ReplyKeyboardMarkup(resize_keyboard=True)
                    menus.add(KeyboardButton(text="Bekor qilish"))
                    for i in l:
                        keyboard = KeyboardButton(text=f"{i}")
                        menus.add(keyboard)
                    await message.reply(f"{sorovnoma} da kimga ovoz bermoqchisiz? Tugmachalardan foydalanib tanlang:",
                                        reply_markup=menus)
                    await data.variant_tanlash.set()
            else:
                await message.answer("Qaytganingiz bilan! Bemalol ovoz berishingiz mumkin: ", reply_markup=menu)


@dp.message_handler(state=data.kanalga_obuna)
async def qaytaruvchi(message: types.message, state: FSMContext):
    final_status = True
    result = ""
    for channel in CHANNELS:
        status = await subscription.check(user_id=message.from_user.id, channel=channel)
        final_status *= status
        channel = await bot.get_chat(channel)
        if not status:
            invite_link = await channel.export_invite_link()
            result += f"👉 <a href='{invite_link}'>{channel.title}</a>\n"
    if not final_status:
        await message.answer(f"Botdan foydalanish uchun, quyidagi kanallarga obuna bo'ling:\n {result}",
                             reply_markup=check_button, disable_web_page_preview=True)
    else:
        await message.answer("Barcha kanallarimizga obuna bo'ldingiz! Endi ovoz berishingiz mumkin: ",
                             reply_markup=menu)
        await state.finish()


# @dp.message_handler(Command("start"))
# async def show_channels(message: types.Message, state: FSMContext):
#     a = message.get_args()
#     l = db.select_all_users()
#     b = True
#     for i in l:
#         if i[0] == message.from_user.id:
#             await message.answer("Sizni allaqachon taklif qilishgan!", reply_markup=menu)
#             b = False
#             break
#
#     if b:
#         if a:
#             await state.update_data(deeplink=a)
#         else:
#             await state.update_data(deeplink="0")


# @dp.chat_join_request_handler()
# async def approver(request1: types.ChatJoinRequest):
#     userid = request1.from_user.id
#     chatid = request1.chat.id
#     await bot.approve_chat_join_request(chatid, userid)
#     await bot.send_message(userid, "Salom")


@dp.callback_query_handler(text="check_subs")
async def checker(call: types.CallbackQuery):
    result = "Barcha kanallarimizga obuna bo'lmadingiz! Avval obuna bo'ling:\n"
    final_status = True
    for channel in CHANNELS:
        status = await subscription.check(user_id=call.from_user.id, channel=channel)
        final_status *= status
        channel = await bot.get_chat(channel)
        if not status:
            invite_link = await channel.export_invite_link()
            result += f"👉 <a href='{invite_link}'>{channel.title}</a>\n"

    if final_status:
        await call.message.answer("Ajoyib! Barcha kanallarimizga obuna bo'ldingiz!")
        await call.message.delete()
        l = db.select_all_users()
        b = False
        for i in l:
            if i[0] == call.from_user.id:
                if i[1] == '0':
                    b = True
                    break
        if b:
            await call.message.answer(
                "Ro'yxatdan o'tishni tugallash uchun, pastdagi tugma orqali telefon raqamingizni yuboring: ",
                reply_markup=phoneNumber)
            await data.phoneNumber.set()

    else:
        await call.message.answer(f"{result}",
                                  disable_web_page_preview=True, reply_markup=check_button)
