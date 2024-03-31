from aiogram import Bot, Dispatcher
from decouple import config

API_TOKEN = config('TELEGRAM_TOKEN')

bot = Bot(token=API_TOKEN)
dp = Dispatcher()



