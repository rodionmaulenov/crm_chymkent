from aiogram import Dispatcher
from django.core.management.base import BaseCommand
import asyncio
from mothers.management.commands.handlers import bot, router

dp = Dispatcher()


async def main():
    dp.include_router(router)
    await dp.start_polling(bot)


class Command(BaseCommand):
    help = 'Run the Telegram bot'

    def handle(self, *args, **kwargs):
        asyncio.run(main())
