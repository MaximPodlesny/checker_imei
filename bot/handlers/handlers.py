import asyncio
import json
from aiogram import Router, types
from aiogram import F
from aiogram.filters import StateFilter
from aiogram.types import ReplyKeyboardMarkup
# from openai import AsyncOpenAI

router = Router()

# @router.message((F.text == "admin @"))
# async def process_add_admin(message: types.Message, state: FSMContext):
#     await add_admin_id(message.from_user.id)

# @router.message(CreateVacancyInfoStates.create_vacancy)
# async def create_v(message: types.Message, state: FSMContext):
#     await state.clear()

# @router.message((F.text == "Нет портрета") & (F.from_user.id.in_(ADMINS)))
# async def find_candidate(message: types.Message, state: FSMContext):
#     print('in Нет портрета admin')

# @router.message((F.text.in_(["Поиск кандидата","К поиску кандидата", "Создать портрет"])) & (F.from_user.id.in_(ADMINS)))
# async def list_vacancies(message: types.Message, state: FSMContext, data=None):
#     await state.set_state(DocumentInfoStates)

# @router.message(CandidateInfoStates.waiting_for_data_of_candidate)
# @router.message((F.text == "Искать") & (F.from_user.id.in_(ADMINS)))
# async def search_vacancies(message: types.Message, state: FSMContext, data=None):
#     pass

# @router.message((F.document) & (F.from_user.id.in_(ADMINS)))
# async def handle_file(message: types.Message, state: FSMContext):
#     if message.document:
#         pass

# @router.message((F.text == "Получить тестовое задание") & (~F.from_user.id.in_(ADMINS)))
# async def give_test_task(message: types.Message, state: FSMContext):
#     pass

