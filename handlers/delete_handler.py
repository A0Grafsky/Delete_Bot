from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from keyboards.inline_keyboard import create_inline_kb
from aiogram import Bot
from config.config import TgBot, load_config
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import StateFilter
from module import resolve_username_to_user_id as u_id


router = Router()
config: TgBot = load_config()

CHANNEL_ID = config.channel_id_one


# Обработчик кнопки 'Удаление первых n-человек'
@router.callback_query(F.data == 'remove_first')
async def kick_first_users(callback: CallbackQuery):
    pass


# Обработка конпки 'Удаление последних n-человек'
@router.callback_query(F.data == 'remove_last')
async def kick_last_users(callback: CallbackQuery):
    pass


# Обработка кнопки 'Удаление неактивных пользователей'
@router.callback_query(F.data == 'remove_deleted')
async def kick_deleted_users(callback: CallbackQuery):
    pass