from aiogram import executor
from loader import dp, db
import middlewares, filters, handlers
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands


async def on_startup(dispatcher):
    # Birlamchi komandalar (/star va /help)
    await set_default_commands(dispatcher)

    # Malumotlar bazasi uchun jadval yaratish

    try:
        db.create_table_captchas()
        db.create_table_channels()
        db.create_table_users()
        db.create_table_reklama()
        db.create_table_sorovnoma()
        db.create_table_ovoz()

    except Exception as err:
        print(str(err) + "!")

    # Bot ishga tushgani haqida adminga xabar berish
    await on_startup_notify(dispatcher)


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)
