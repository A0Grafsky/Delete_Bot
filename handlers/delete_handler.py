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


# FSM для "удаление по нику"
class Fsm(StatesGroup):
    input = State()
    kick = State()


# Обработчик кнопки 'Удаление по нику'
@router.callback_query(F.data == 'remove_by_username')
async def kick_user(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Пожалуйста, укажите ник пользователя для удаления (например, username):")
    await callback.answer()
    await state.set_state(Fsm.input)


# Удаление по нику
@router.message(StateFilter(Fsm.input), F.text)
async def kick_user(message: Message, bot: Bot, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Fsm.kick)
    username_dict = await state.get_data()
    username = username_dict.get('name')
    if not username:
        await message.reply("Ник пользователя не может быть пустым. Попробуйте снова.")
        return

    try:
        # Получаем информацию о пользователе по его никнейму
        user_id = await u_id(username)

        # Удаляем пользователя из канала
        await bot.ban_chat_member(CHANNEL_ID, user_id)
        await message.reply(f"Пользователь {username} удален из канала.")
    except Exception as e:
        await message.reply(f"Не удалось удалить пользователя {username}. Ошибка: {e}")




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