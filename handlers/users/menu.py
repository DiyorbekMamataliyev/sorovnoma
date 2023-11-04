from aiogram.dispatcher.filters import Command, Text
from aiogram.types import Message,ReplyKeyboardRemove
from keyboards.default.menuKeyboard import menu

from loader import dp


@dp.message_handler(Command("menu"))
async def show_menu(message: Message):
    await message.answer("menu: ", reply_markup=menu)
