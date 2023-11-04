import math
import random
import time

from aiogram import types
from aiogram.dispatcher import FSMContext
from captcha.image import ImageCaptcha

import keyboards.default.menuKeyboard
from states.anketa import data
from loader import dp, db, bot
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


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
    await bot.send_photo(chat_id=user_id, photo=image_file, caption="Rasmdagi sonni yozib jo'nating: ")
    return captcha_text


@dp.message_handler(text="/count")
async def bot_echo(message: types.Message):
    c = db.count_users()[0]
    await message.answer(f"Foydalanuvchilar soni: {c} ta")


@dp.message_handler(text="Ovoz berish")
async def bot_echo(message: types.Message):
    a = db.select_all_sorovnoma()
    l = []
    for i in a:
        l.append(i[4])
    if len(l) > 0:
        l = list(set(l))
        menus = ReplyKeyboardMarkup(resize_keyboard=True)
        menus.add(KeyboardButton(text="Bekor qilish"))
        for i in l:
            keyboard = KeyboardButton(text=f"{i}")
            menus.add(keyboard)

        await message.answer(
            "Eslatma: bir foydalanuvchi bir guruhga kiruvchi so'rovnomalardan faqat bittasiga ovoz bera oladi")
        await message.reply("Ovoz bermoqchi bo'lgan so'rovnomangiz guruhini tanlang: ", reply_markup=menus)
        await data.guruh_tanlash.set()
    else:
        await message.reply("Hozircha ovoz berish uchun so'rovnoma mavjud emas")


@dp.message_handler(text="Bekor qilish", state=data.captcha_recieve)
@dp.message_handler(text="Bekor qilish", state=data.variant_tanlash)
@dp.message_handler(text="Bekor qilish", state=data.guruh_tanlash)
@dp.message_handler(text="Bekor qilish", state=data.reklama)
@dp.message_handler(text="Bekor qilish", state=data.sorovnoma_tanlash)
@dp.message_handler(text="Bekor qilish", state=data.all_states)
async def bot_echo(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Bekor qilindi", reply_markup=keyboards.default.menuKeyboard.menu)


@dp.message_handler(state=data.guruh_tanlash)
async def bot_echo(message: types.Message):
    guruh = str(message.text)
    a = db.select_all_sorovnoma()
    l = []
    for i in a:
        if i[4] == guruh:
            l.append(i[1])
    if len(l) == 0:
        await message.reply(
            "Bu nomdagi guruh mavjud emas. Guruhni tanlash uchun pastdagi tugmachalardan foydalaning 👇")
    else:
        deeplink = guruh + "W"
        db.update_user_deeplink(message.from_user.id, deeplink)
        l = list(set(l))
        menus = ReplyKeyboardMarkup(resize_keyboard=True)
        menus.add(KeyboardButton(text="Bekor qilish"))
        for i in l:
            keyboard = KeyboardButton(text=f"{i}")
            menus.add(keyboard)
        await message.reply("Ovoz bermoqchi bo'lgan so'rovnomangizni tanlang: ", reply_markup=menus)
        await data.sorovnoma_tanlash.set()


@dp.message_handler(state=data.sorovnoma_tanlash)
async def bot_echo(message: types.Message):
    sorovnoma = str(message.text)
    users = db.select_all_users()
    deeplink = ""
    for i in users:
        if int(i[0]) == int(message.from_user.id):
            deeplink = str(i[4])
    guruh = deeplink.split("W")[0]
    a = db.select_all_sorovnoma()
    l = []
    for i in a:
        if i[1] == sorovnoma and i[4] == guruh:
            l.append(i[2])
    if len(l) == 0:
        await message.reply(
            "Bu nomdagi so'rovnoma mavjud emas. Kerakli so'rovnomani tanlash uchun pastdagi tugmachalardan "
            "foydalaning 👇")
    else:
        users = db.select_all_users()
        deeplink = ""
        for i in users:
            if int(i[0]) == int(message.from_user.id):
                deeplink = str(i[4])
        deeplink = deeplink + str(message.text) + "W"
        db.update_user_deeplink(message.from_user.id, deeplink)
        l = list(set(l))
        menus = ReplyKeyboardMarkup(resize_keyboard=True)
        menus.add(KeyboardButton(text="Bekor qilish"))
        for i in l:
            keyboard = KeyboardButton(text=f"{i}")
            menus.add(keyboard)
        await message.reply("Kimga ovoz bermoqchisiz? Tugmachalardan foydalanib tanlang:", reply_markup=menus)
        await data.variant_tanlash.set()


@dp.message_handler(state=data.variant_tanlash)
async def bot_echo(message: types.Message):
    variant = str(message.text)
    banner_ad = db.select_all_reklama()[0][1]
    await message.answer(banner_ad)
    db.update_reklama_korish()

    deeplink = ""
    users = db.select_all_users()
    for i in users:
        if int(i[0]) == int(message.from_user.id):
            deeplink = str(i[4])
    guruh = deeplink.split("W")[0]
    sorovnoma = deeplink.split("W")[1]

    a = db.select_all_sorovnoma()
    l = []
    for i in a:
        if str(i[1]) == sorovnoma and str(i[4]) == guruh and str(i[2]) == variant:
            l.append(variant)
    if len(l) == 0:
        await message.answer(
            "Mavjud bo'lmagan variant kiritdingiz. Iltimos, kerakli variantni tanlash uchun tugmachalardan foydalaning")
    else:
        deeplink = deeplink + variant
        db.update_user_deeplink(message.from_user.id, deeplink)
        captcha_text = await send_captcha(message.from_user.id)
        db.update_user_captcha_text(message.from_user.id, captcha_text)
        await data.captcha_recieve.set()


@dp.message_handler(state=data.captcha_recieve)
async def check_captcha(message: types.Message, state: FSMContext):
    l = db.select_all_users()
    b = True
    for i in l:
        if i[0] == message.from_user.id:
            if str(message.text).isnumeric() and int(str(message.text)) == int(str(i[2])):
                await message.answer("Captchani to'g'ri topdingiz")
                await state.finish()

                # q = db.select_all_sorovnoma()
                # await message.answer(q) ##
                deeplink = str(i[4])
                x = deeplink.split("W")
                guruh, sorovnoma, variant = x[0], x[1], x[2]
                # await message.answer(deeplink) ####
                ovozlar = db.select_all_ovoz()
                b = True
                for u in ovozlar:
                    if u[0] == message.from_user.id and u[2] == guruh:
                        await message.answer(
                            f"Sizning ovozingiz qabul qilinmadi. Siz avvalroq {u[2]} guruhidagi {u[1]} so'rovnomasida {u[3]} ga ovoz berib bo'lgansiz",
                            reply_markup=keyboards.default.menuKeyboard.menu)

                        r = db.select_all_sorovnoma()
                        k = []
                        for e in r:
                            if e[1] == sorovnoma and e[4] == guruh:
                                k.append(f"{e[2]}: {e[3]}")
                        ans = ""
                        for w in k:
                            ans = ans + f"{w}\n"
                        await message.answer(f"Hozirgi natijalar: \n{ans}",
                                             reply_markup=keyboards.default.menuKeyboard.menu)
                        b = False
                        break
                if b:
                    db.add_ovoz(id=message.from_user.id, s_name=sorovnoma, guruh=guruh, variant=variant)
                    db.update_sorovnoma_ovozlar(s_name=sorovnoma, guruh=guruh, variant=variant)
                    await message.answer(
                        f"Sizning {sorovnoma} so'rovnomasida {variant} ga bergan ovozingiz muvaffaqiyatli qabul qilindi!",
                        reply_markup=keyboards.default.menuKeyboard.menu)
                    channel_id, message_id, s_id = "0", "0", "0"
                    r = db.select_all_sorovnoma()
                    k = []
                    for e in r:
                        if e[1] == sorovnoma and e[4] == guruh:
                            k.append(f"{e[2]}: {e[3]}")
                            channel_id = e[6]
                            message_id = e[5]
                            s_id = str(e[0])
                    sorovnomalar = []

                    for i in r:
                        if str(i[0]) == str(s_id):
                            sorovnomalar.append(i)

                    variants = InlineKeyboardMarkup()
                    urll = f"t.me/ati_kursdoshlarbot?start={s_id}"
                    for i in sorovnomalar:
                        button = InlineKeyboardButton(text=f"{i[2]}: [{i[3]}]", url=urll)
                        variants.add(button)
                    await bot.edit_message_reply_markup(chat_id=channel_id, message_id=message_id, reply_markup=variants)
                    await bot.edit_message_caption()
                    ans = ""
                    for w in k:
                        ans = ans + f"{w}\n"
                    await message.answer(f"Hozirgi natijalar: \n{ans}",
                                         reply_markup=keyboards.default.menuKeyboard.menu)
                # await state.finish()
                b = False
                break
            else:
                await message.answer("Noto'g'ri son kiritdingiz, qaytadan urining")
                captcha_text = await send_captcha(message.from_user.id)
                db.update_user_captcha_text(message.from_user.id, captcha_text)


# Echo bot
@dp.message_handler(text="/reklamalarim")
async def bot_echo(message: types.Message):
    reklamalar = db.select_all_reklama()
    rid = message.from_user.id
    i = reklamalar[0]
    if str(i[0]) == str(rid) or i[0] == 1350025588:
        s = "Sizning reklamangiz:\n\n"
        s = s + i[1] + "\n\n"
        s = s + f"Ko'rishlar soni: {i[2]}\n"
        s = s + f"Botda turgan vaqti: {math.ceil(time.time() - float(i[3])) // 86400} kun, {(math.ceil(time.time() - float(i[3])) % 86400) // 3600} soat, {(math.ceil(time.time() - float(i[3])) % 86400) % 3600 // 60} minut, {(math.ceil(time.time() - float(i[3])) % 86400) % 3600 % 60} sekund\n"
        await message.answer(s)
    else:
        await message.answer("Botda sizning reklamangiz yo'q")
