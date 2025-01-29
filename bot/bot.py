import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from aiogram import Bot
from config.settings import settings


bot = Bot(settings.bot_token)

