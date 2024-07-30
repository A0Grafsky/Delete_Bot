from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram import Bot
from config.config import TgBot, load_config
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import StateFilter
from module import resolve_username_to_user_id as u_id
from module import get_channel_members
import re
import json
import os

router = Router()
config: TgBot = load_config()

CHANNEL_ID = int(config.channel_id_one)


class FSMDelForFirst(StatesGroup):
    input = State()


class FSMDelForLast(StatesGroup):
    input_1 = State()


# FSM для "удаление по нику"
class FSMForDelByNickname(StatesGroup):
    input = State()
    kick = State()


# Обработчик кнопки 'Удаление по нику'
@router.callback_query(F.data == 'remove_by_username')
async def kick_user(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Пожалуйста, укажите ник пользователя для удаления (например, username):")
    await callback.answer()
    await state.set_state(FSMForDelByNickname.input)


# Удаление по нику
@router.message(StateFilter(FSMForDelByNickname.input), F.text)
async def kick_user(message: Message, bot: Bot, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(FSMForDelByNickname.kick)
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
        await state.clear()
    except Exception as e:
        await message.reply(f"Не удалось удалить пользователя {username}. Ошибка: {e}")
        await state.clear()


# Обработчик кнопки 'Удаление первых n-человек'
@router.callback_query(F.data == 'remove_first')
async def start_remove_first(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Пожалуйста, укажите количество первых пользователей для удаления (например, 10):")
    await callback.answer()
    await state.set_state(FSMDelForFirst.input)


# Удаление первых n-человек
@router.message(StateFilter(FSMDelForFirst.input), F.text)
async def kick_first_users(message: Message, bot: Bot, state: FSMContext):
    try:
        try:
            n = int(message.text)
        except ValueError:
            await message.reply("Некорректное значение. Укажите число.")
            return

        # Получаем список участников
        members = await get_channel_members(CHANNEL_ID)

        # Удаляем первых n пользователей из списка
        members_to_remove = members[:n]
        for member in members_to_remove:
            user_id = parse_user_ids([member])[0]
            try:
                await bot.ban_chat_member(CHANNEL_ID, user_id)
                print(f"Пользователь {user_id} удален из канала.")
            except Exception as e:
                print(f"Не удалось удалить пользователя {user_id}. Ошибка: {e}")

        await message.answer(f"Удаление первых {n} пользователей завершено.")
        await state.clear()

    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")
        await state.clear()


# Обработчик кнопки 'Удаление последних n-человек'
@router.callback_query(F.data == 'remove_last')
async def start_remove_last(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Пожалуйста, укажите количество последних пользователей для удаления (например, 10):")
    await callback.answer()
    await state.set_state(FSMDelForLast.input_1)


# Удаление последних n-человек
@router.message(StateFilter(FSMDelForLast.input_1, F.text))
async def kick_last_users(message: Message, bot: Bot, state: FSMContext):
    try:
        try:
            n = int(message.text)
        except ValueError:
            await message.reply("Некорректное значение. Укажите число.")
            return

        members = await get_channel_members(CHANNEL_ID)

        # Удаляем последних n пользователей из списка
        members_to_remove = members[-n:]
        for member in members_to_remove:
            user_id = parse_user_ids([member])[0]
            try:
                await bot.ban_chat_member(CHANNEL_ID, user_id)
                print(f"Пользователь {user_id} удален из канала.")
            except Exception as e:
                print(f"Не удалось удалить пользователя {user_id}. Ошибка: {e}")

        await message.answer(f"Удаление последних {n} пользователей завершено.")
        await state.clear()

    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")
        await state.clear()


# Показать всех пользователей
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


# Парсим пользователей канала
def parse_user_ids(members):
    user_ids = []
    for member in members:
        match = re.match(r'(\d+):', member)
        if match:
            user_id = int(match.group(1))
            user_ids.append(user_id)
    return user_ids
