from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import logging
from aiogram import Bot, Dispatcher, types

bot = Bot(token='7483152723:AAE5cqGZ7jgXUghqRvc6LE_-8QrPtbJXE9o')
dp = Dispatcher()

CHAT_ID = '-1002171039112'

logger = logging.getLogger(__name__)




async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    dp.run_polling(bot)
