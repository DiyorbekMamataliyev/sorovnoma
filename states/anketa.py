from aiogram.dispatcher.filters.state import StatesGroup, State


class data(StatesGroup):
    phoneNumber = State()
    reklama = State()
    captcha_recieve = State()
    kanalga_obuna=State()
    guruh_tanlash=State()
    sorovnoma_tanlash=State()
    variant_tanlash=State()
