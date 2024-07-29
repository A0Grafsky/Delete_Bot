from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.handlers import callback_query
from aiogram.types import Message, CallbackQuery, InputFile, FSInputFile
from keyboards.inline_keyboard import create_inline_kb
from aiogram import Bot
from config.config import TgBot, load_config
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import StateFilter
from module import resolve_username_to_user_id as u_id
from module import get_channel_members
import json
import os
from datetime import datetime, timedelta


router = Router()
config: TgBot = load_config()

CHANNEL_ID = int(config.channel_id_one)


# FSM для "удаление по нику"
class Fsm(StatesGroup):
    input = State()
    kick = State()


# Обработка '/start'
@router.message(CommandStart())
async def send_welcome(message: Message):
    await message.answer(
        "Привет! Используй команды для управления подписчиками:\n\n"
        "Удаление по нику - После ввода ника, пользователей будет удален\n\n"
        "Удаление первых n-человек - введите n-число и именно столько первых"
        "в списке пользователей удалит бот\n\n"
        "Удаление последних n-человек - введите n-число и именно столько последних"
        "в списке пользователей удалит бот\n\n"
        "Удаление неактивных пользователей - бот удалит всех неактивных пользователей.",
        reply_markup=create_inline_kb(1, 'remove_by_username',
                                      'remove_first', 'remove_last', 'remove_deleted', 'print_all_user')
    )




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


@router.callback_query(F.data == 'print_all_user')
async def print_1(callback: CallbackQuery):
    channel_id = CHANNEL_ID

    try:
        # Получаем список участников
        members = await get_channel_members(channel_id)

        # Сохраняем список участников в JSON-файл
        filename = "members_list.json"
        with open(filename, "w") as file:
            json.dump(members, file, indent=4)

        message_text = "JSON-файл для Вас ❤️"

        file = FSInputFile('members_list.json')

        await callback.bot.send_document(chat_id=callback.from_user.id, document=file, caption=message_text)

        os.remove(filename)

    except Exception as e:
        print(f"An error occurred: {e}")

@router.callback_query(F.data == 'remove_deleted')
async def remove_inactive_users(callback: CallbackQuery, bot: Bot):
    channel_id = CHANNEL_ID
    # Определите период неактивности (например, 30 дней)
    inactivity_threshold = timedelta(days=30)
    cutoff_date = datetime.now() - inactivity_threshold

    try:
        # Получаем список участников
        members = await get_channel_members(channel_id)

        # Удаление неактивных пользователей
        for member in members:
            # Пример проверки последней активности
            last_active_date = member.get('last_active_date')  # Замените на правильное поле
            if last_active_date and last_active_date < cutoff_date:

                await bot.ban_chat_member(channel_id, member['user_id'])
                print(f"Пользователь {member['user_id']} удален из канала из-за неактивности.")

        await callback.message.answer("Неактивные пользователи удалены.")
        await callback.answer()

    except Exception as e:
        print(f"An error occurred: {e}")
        await callback.message.answer(f"Произошла ошибка: {e}")
