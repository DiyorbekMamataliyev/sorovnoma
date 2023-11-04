import datetime
import logging
import time

import captcha

from aiogram.dispatcher import FSMContext
from aiogram import types
from data.config import CHANNELS
from keyboards.inline.subscription import check_button
from keyboards.default.menuKeyboard import menu, phoneNumber
from aiogram.dispatcher.filters.builtin import CommandStart, Command
from loader import db, dp, bot
from utils.misc import subscription
from keyboards.default.menuKeyboard import phoneNumber
from aiogram.utils.deep_linking import get_start_link
from states.anketa import data
from captcha.image import ImageCaptcha
from aiogram.types import InputFile, InlineKeyboardMarkup, InlineKeyboardButton
import io


@dp.message_handler(user_id=1350025588)
async def yangi_sorovnoma(message: types.Message):
    s = str(message.text)
    s_id = "0"
    if s.startswith("..new"):
        try:
            s = s[5:]
            a = s.split('^')
            s_id = a[0]
            s_name = a[1]
            guruh = a[2]

            variantlar = a[3].split(',')

            for i in variantlar:
                db.add_sorovnoma(s_id=s_id, s_name=s_name, variant=i, guruh=guruh)

            await message.answer(
                f"{s_id} id ga ega bo'lgan {s_name} nomli so'rovnoma {len(variantlar)} ta variantlar bilan muvaffaqiyatli qo'shildi")
        except Exception as er:
            await message.answer(str(er))
            a = db.select_all_sorovnoma()
            await message.answer(a)
            await message.answer(f"id: {s_id}")
        # s_id int
        # s_name varchar(100)
        # variant varchar(40)
        # ovozlar int
        # guruh varchar(10)
        # message_id varchar(20)
        # channel_id varchar(20)
    elif s.startswith("del"):
        s = s[3:]
        try:
            # sorovnoma fayli
            q = db.select_all_sorovnoma()
            Q = db.select_all_ovoz()
            sorovnomalar = []
            ovozlar = []
            for i in q:
                if str(i[0]) == s:
                    sorovnomalar.append(i)
            s_name = sorovnomalar[0][1]
            for i in Q:
                if str(i[0]) == s:
                    ovozlar.append(i)
            if len(sorovnomalar) == 0:
                await message.answer("id xato")
            else:
                now = datetime.datetime.now()
                timezone = datetime.timezone(datetime.timedelta(hours=5))
                gmt_time = now.astimezone(timezone)
                await message.answer(str(gmt_time))
                with open("sorovnoma.txt", "w") as f:
                    f.write(
                        f"Vaqt: {gmt_time}\n\n{sorovnomalar[0][1]}\nid:{sorovnomalar[0][0]}\nSo'rovnoma guruhi:{sorovnomalar[0][4]}\n\n")
                    f.write(f"Ovozlar:\n")
                    for y in sorovnomalar:
                        f.write(f"{y[2]}: {y[3]} ta ovoz\n")

                    for y in sorovnomalar:
                        variant = y[2]
                        k = 1
                        f.write(f"\n{variant}:\n")
                        for t in ovozlar:
                            if str(t[3]) == variant:
                                uid = t[0]
                                user = await bot.get_chat(uid)
                                full_name = user.full_name
                                username = user.username if user.username else " "
                                f.write(f"{k}) {uid} | {full_name} | {username}\n")

                path = InputFile(path_or_bytesio="sorovnoma.txt")
                await message.reply_document(document=path)
                db.delete_sorovnoma(s)
                db.delete_ovoz_sorovnoma(s_name)
                await message.answer(f"{s} id ga ega so'rovnoma ma'lumotlari botdan to'liq o'chirildi")
        except Exception as err:
            await message.answer(str(err))

    elif s.startswith("..ad"):
        try:
            t = s[4:].split('^')
            rid = t[0]
            txt = t[1]
            db.delete_reklama()
            db.add_reklama(id=rid, text=txt, vaqt=time.time())
            await message.answer("Reklama muvaffaqiyatli yangilandi")
        except Exception as err:
            await message.answer(str(err))

    elif s.startswith("Yoz"):
        s = s[3:]
        try:
            # sorovnoma fayli
            q = db.select_all_sorovnoma()
            Q = db.select_all_ovoz()
            sorovnomalar = []
            ovozlar = []
            for i in q:
                if str(i[0]) == s:
                    sorovnomalar.append(i)
            s_name = sorovnomalar[0][1]
            for i in Q:
                if str(i[1]) == s_name:
                    ovozlar.append(i)
            if len(sorovnomalar) == 0:
                await message.answer("id xato")
            else:
                now = datetime.datetime.now()
                timezone = datetime.timezone(datetime.timedelta(hours=5))
                gmt_time = now.astimezone(timezone)
                await message.answer(str(gmt_time))
                with open("sorovnoma.txt", "w") as f:
                    f.write(
                        f"Vaqt: {gmt_time}\n\n{sorovnomalar[0][1]}\nid:{sorovnomalar[0][0]}\nSo'rovnoma guruhi:{sorovnomalar[0][4]}\n\n")
                    f.write(f"Ovozlar:\n")
                    for y in sorovnomalar:
                        f.write(f"{y[2]}: {y[3]} ta ovoz\n")

                    for y in sorovnomalar:
                        variant = y[2]
                        k = 1
                        f.write(f"\n{variant}:\n")

                        for t in ovozlar:
                            if str(t[3]) == variant:
                                uid = t[0]
                                user = await bot.get_chat(uid)
                                full_name = user.full_name
                                username = f"@{user.username}" if user.username else " "
                                f.write(f"{k}) {uid} | {full_name} | {username}\n")
                                k = k + 1

                path = InputFile(path_or_bytesio="sorovnoma.txt")
                await message.reply_document(document=path)
        except Exception as err:
            await message.answer(str(err))
    elif s.startswith("send"):
        try:
            s = s[4:]
            s_id, channel_id = s.split('^')[0], s.split('^')[1]
            sorovnomalar = []
            so = db.select_all_sorovnoma()
            for i in so:
                if str(i[0]) == s_id:
                    sorovnomalar.append(i)

            urll = f"t.me/ati_kursdoshlarbot?start={s_id}"
            variants = InlineKeyboardMarkup()
            for i in sorovnomalar:
                button = InlineKeyboardButton(text=f"{i[2]}: [{i[3]}]", url=urll)
                variants.add(button)
            sent = await bot.send_message(chat_id=channel_id, text=f"{sorovnomalar[0][1]} so'rovnomasida ovoz bering!\n\n<a href='{urll}'>Ovoz berish</a>", disable_web_page_preview=True, reply_markup=variants)

            db.update_sorovnoma_ids(s_id, sent.message_id, channel_id)
            await message.answer("Post muvaffaqiyatli jo'natildi")
        except Exception as err:
            await message.answer(str(err))


@dp.message_handler(user_id=1350025588, content_types=['photo'])
async def yangi_sorovnoma(message: types.Message):
    s = message.caption
    file_id = message.photo[-1].file_id
    if s.startswith("send"):
        try:
            s = s[4:]
            s_id, channel_id = s.split('^')[0], s.split('^')[1]
            sorovnomalar = []
            so = db.select_all_sorovnoma()
            for i in so:
                if str(i[0]) == s_id:
                    sorovnomalar.append(i)

            urll = f"t.me/ati_kursdoshlarbot?start={s_id}"
            variants = InlineKeyboardMarkup()
            for i in sorovnomalar:
                button = InlineKeyboardButton(text=f"{i[2]}: [{i[3]}]", url=f"t.me/ati_kursdoshlarbot?start={s_id}")
                variants.add(button)
            sent = await bot.send_photo(chat_id=channel_id, photo=file_id, caption=f"{sorovnomalar[0][1]} so'rovnomasida ovoz bering!\n\n<a href='{urll}'>Ovoz berish</a>",
                                        reply_markup=variants)
            db.update_sorovnoma_ids(s_id, sent.message_id, channel_id)
            await message.answer("Post muvaffaqiyatli jo'natildi")
        except Exception as err:
            await message.answer(str(err))


@dp.message_handler(user_id=1350025588, content_types=['video'])
async def yangi_sorovnoma(message: types.Message):
    s = message.caption
    file_id = message.video.file_id
    if s.startswith("send"):
        try:
            s = s[4:]
            s_id, channel_id = s.split('^')[0], s.split('^')[1]
            sorovnomalar = []
            so = db.select_all_sorovnoma()
            for i in so:
                if str(i[0]) == s_id:
                    sorovnomalar.append(i)
            urll = f"t.me/ati_kursdoshlarbot?start={s_id}"
            variants = InlineKeyboardMarkup()
            for i in sorovnomalar:
                button = InlineKeyboardButton(text=f"{i[2]}: [{i[3]}]", url=urll)
                variants.add(button)
            sent = await bot.send_video(chat_id=channel_id, video=file_id, caption=f"{sorovnomalar[0][1]} so'rovnomasida ovoz bering!\n\n<a href='{urll}'>Ovoz berish</a>", disable_web_page_preview=True,
                                        reply_markup=variants)
            db.update_sorovnoma_ids(s_id, sent.message_id, channel_id)
            await message.answer("Post muvaffaqiyatli jo'natildi")
        except Exception as err:
            await message.answer(str(err))
