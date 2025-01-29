import logging
import os
import subprocess

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup

from bot import bot
from handlers import start_router, handlers_router
from middlewares.logging import LoggingMiddleware



# Настройка логирования
logging.basicConfig(level=logging.INFO)

storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Подключение мидлвара
dp.message.middleware(LoggingMiddleware())

# Регистрация роутеров
dp.include_router(start_router)
dp.include_router(handlers_router)


async def main():
    await dp.start_polling(bot)
    

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())

