import datetime
import time

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import Command
from aiogram.types import InputFile

from keyboards.default.menuKeyboard import admin
from loader import dp, db, bot
from states.anketa import data
from .start import send_captcha

ADMINS = [1350025588, 954723360, 996596288]


@dp.message_handler(Command("admin"), user_id=ADMINS)
async def bot_help(message: types.Message):
    if message.from_user.id in ADMINS:
        await message.answer("Admin buyruqlari:", reply_markup=admin)


@dp.message_handler(Command("captcha"), user_id=ADMINS)
async def bot_help(message: types.Message):
    for i in range(3):
        await send_captcha(message.from_user.id)


###REKLAMA YUBORISH
@dp.message_handler(text="Reklama yuborish")
async def bot_help(message: types.Message):
    if message.from_user.id in ADMINS:
        await message.answer("Reklama matnini yuboring: ")
        await data.reklama.set()


@dp.message_handler(state=data.reklama)
async def bot_help(message: types.Message, state: FSMContext):
    if str(message.text).lower() == "bekor":
        await state.finish()
        await message.answer("Reklama jo'natish bekor qilindi. Hech nima jo'natilmadi")
    elif message.from_user.id in ADMINS:
        users = db.select_all_users()
        s = message.text
        c = 0
        d = 0
        for i in users:
            if i[3] == '0':
                try:
                    await bot.send_message(i[0], s)
                    c = c + 1
                except Exception:
                    db.update_user_bloklaganmi(i[0], '1')
                    d = d + 1
                    pass
                time.sleep(0.1)
        await message.answer(
            f"{c} ta foydalanuvchiga reklama yuborildi. Botni bloklagan {d} ta foydalanuvchiga reklama yuborib bo'lmadi")
        await state.finish()
        await bot.send_message(1350025588, f"{message.from_user.full_name} matnli reklama tarqatdi")


@dp.message_handler(state=data.reklama, content_types=['photo', 'video', 'animation', 'document'], user_id=ADMINS)
async def bot_help(message: types.Message, state: FSMContext):
    if message.from_user.id in ADMINS:
        users = db.select_all_users()
        s = message.caption
        c = 0
        d = 0
        for i in users:
            if i[3] == '0':
                try:
                    # await bot.send_message(i[0], s)
                    await bot.forward_message(chat_id=i[0], from_chat_id=message.from_user.id,
                                              message_id=message.message_id)
                    c = c + 1
                except Exception:
                    db.update_user_bloklaganmi(i[0], '1')
                    d = d + 1
                time.sleep(0.1)
        await message.answer(
            f"{c} ta foydalanuvchiga reklama yuborildi. Botni bloklagan {d} ta foydalanuvchiga reklama yuborib bo'lmadi")
        await state.finish()
        await bot.send_message(1350025588, f"{message.from_user.full_name} media reklama tarqatdi")


###REKLAMA YUBORILDI

@dp.message_handler(text="Survey", user_id=ADMINS)
async def bot_help(message: types.Message):
    a = db.select_all_sorovnoma()
    ans = "s_id; s_name; variant; ovozlar; guruh; message_id;  channel_id.\n\n"
    for i in a:
        ans = ans + f"{i[0]}; {i[1]}; {i[2]}; {i[3]}; {i[4]}; {i[5]}; {i[6]}.\n"
    await message.answer(ans)


@dp.message_handler(text="statistika")
async def bot_help(message: types.Message):
    if message.from_user.id in ADMINS:
        alll, active, passive, dele = db.count_users()
        ans = f"Jami foydalanuvchilar soni: {alll[0]} ta\nAktiv foydalanuvchilar soni: {active[0]} ta\nBloklaganlar soni: {passive[0]} ta\nO'chirilgan hisoblar: {dele} ta"
        await message.reply(ans)
        await bot.send_message(1350025588, f"{message.from_user.full_name} statistikani ko'rdi")


@dp.message_handler(text="To'liq statistika (fayl)")
async def bot_help(message: types.Message):
    if message.from_user.id in ADMINS:
        users = db.select_all_users()
        count, active, passive, dele = db.count_users()

        now = datetime.datetime.now()
        timezone = datetime.timezone(datetime.timedelta(hours=5))
        gmt_time = now.astimezone(timezone)
        await message.answer(str(gmt_time))

        # active = 0
        # passive = 0
        # dele = 0
        # for i in users:
        #     if i[2] == 'dele':
        #         dele = dele + 1
        #     else:
        #         if i[3] == '1':
        #             passive = passive + 1
        #         else:
        #             active = active + 1

        # Open the file for writing
        # with open("stats.txt", "w") as f:
        #     # Write some text to the file
        #     f.write(
        #         f"{gmt_time} holatiga ko'ra bot statistikasi:\n\n Botdagi jami foydalanuvchilar soni: {count[0]} ta.\n")
        #     f.write(
        #         f"Aktiv foydalanuvchilar: {active} ta\nBloklaganlar: {passive} ta\nO'chirilgan akkauntlar: {dele} ta\n\n")
        #     f.write("Aktiv foydalanuvchilar:\n")
        # f.close()

        ans = ""
        c = 1
        for i in users:
            if i[2] != 'dele' and i[3] == '0':
                try:
                    linku = await bot.get_chat(i[0])
                    fullname = linku.full_name
                    username = "@"
                    ans = ans + f"{c}) {fullname}\n"
                    if linku.username:
                        username = username + linku.username
                        ans = ans + f"{username}\n"
                    userid = i[0]
                    ans = ans + f"id:{userid}\n"
                    phone = i[1]
                    if phone != '0':
                        ans = ans + f"Tel: {phone}\n\n"
                    else:
                        ans = ans + "\n"
                    c = c + 1
                except:
                    db.update_user_captcha_text(i[0], 'dele')

        with open("stats.txt", "w") as f:
            # Write some text to the file
            f.write(
                f"{gmt_time} holatiga ko'ra bot statistikasi:\n\nBotdagi jami foydalanuvchilar soni: {count[0]} ta.\n")
            f.write(
                f"Aktiv foydalanuvchilar: {active[0]} ta\nBloklaganlar: {passive[0]} ta\nO'chirilgan akkauntlar: {dele} ta\n\n")
            f.write("Aktiv foydalanuvchilar:\n")
            f.write(f"{ans}Botni bloklaganlar:\n")

        ans = ""
        c = 1
        for i in users:
            if i[2] != 'dele' and i[3] == '1':
                try:
                    linku = await bot.get_chat(i[0])
                    fullname = linku.full_name
                    username = "@"
                    ans = ans + f"{c}) {fullname}\n"
                    if linku.username:
                        username = username + linku.username
                        ans = ans + f"{username}\n"
                    userid = i[0]
                    ans = ans + f"id:{userid}\n"
                    phone = i[1]
                    if phone != '0':
                        ans = ans + f"Tel: {phone}\n\n"
                    else:
                        ans = ans + "\n"
                    c = c + 1
                except:
                    db.update_user_captcha_text(i[0], 'dele')

        with open("stats.txt", "a") as f:
            f.write(f"{ans}\n\nO'chirilgan akkauntlar:\n")
        f.close()
        ans = ""
        c = 1
        for i in users:
            if i[2] == 'dele':
                userid = i[0]
                ans = ans + f"id:{userid}\n"
                phone = i[1]
                if phone != '0':
                    ans = ans + f"Tel: {phone}\n\n"
                else:
                    ans = ans + "\n"
                c = c + 1

        with open("stats.txt", "a") as f:
            f.write(f"{ans}")
        f.close()
        file_path = 'stats.txt'
        path = InputFile(path_or_bytesio="stats.txt")
        await message.reply_document(document=path)
        await bot.send_message(1350025588, f"{message.from_user.full_name} stats.txt faylni oldi")
