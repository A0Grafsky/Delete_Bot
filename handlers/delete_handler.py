from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram import Bot
from config.config import TgBot, load_config
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import StateFilter
from telethon.errors import UserNotParticipantError
from module import resolve_username_to_user_id as u_id
from module import get_channel_members
from module import get_last_message_date
from datetime import datetime, timedelta, timezone
import asyncio
import re


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


# Удаление неактивных пользователей
@router.callback_query(F.data == 'remove_deleted')
async def remove_inactive(callback: CallbackQuery, bot: Bot):
    try:
        await callback.message.answer("Начинаю процесс удаления неактивных пользователей...")

        # Период неактивности
        inactivity_threshold = timedelta(days=30)
        cutoff_date = datetime.now(timezone.utc) - inactivity_threshold

        # Получаем список участников
        members = await get_channel_members(CHANNEL_ID)
        user_ids = parse_user_ids(members)

        for user_id in user_ids:
            try:
                last_message_date = await get_last_message_date(user_id)
                print(f"Last message date for user {user_id}: {last_message_date}")

                if last_message_date:
                    # Приведение last_message_date к временной зоне UTC, если она не aware
                    if last_message_date.tzinfo is None:
                        last_message_date = last_message_date.replace(tzinfo=timezone.utc)

                    if last_message_date < cutoff_date:
                        try:
                            await bot.ban_chat_member(CHANNEL_ID, user_id)
                            print(f"Пользователь {user_id} удален из канала из-за неактивности.")
                        except Exception as e:
                            print(f"Не удалось удалить пользователя {user_id}. Ошибка: {e}")
                else:
                    # Если дата сообщения не найдена, считаем пользователя неактивным
                    await bot.ban_chat_member(CHANNEL_ID, user_id)
                    print(f"Пользователь {user_id} удален из канала, так как неактивен (сообщение не найдено).")

            except UserNotParticipantError:
                # Пользователь не является участником, так что можно считать его неактивным и удалить
                try:
                    await bot.ban_chat_member(CHANNEL_ID, user_id)
                    print(f"Пользователь {user_id} удален из канала, так как не является участником.")
                except Exception as e:
                    print(f"Не удалось удалить пользователя {user_id}. Ошибка: {e}")

            except Exception as e:
                print(f"Error getting last message date for user {user_id}: {e}")
                # В случае любой другой ошибки считаем пользователя неактивным
                try:
                    await bot.ban_chat_member(CHANNEL_ID, user_id)
                    print(f"Пользователь {user_id} удален из канала из-за ошибки при получении данных.")
                except Exception as e:
                    print(f"Не удалось удалить пользователя {user_id}. Ошибка: {e}")

            await asyncio.sleep(1)  # Ожидание 1 секунда

        await callback.message.answer("Процесс удаления неактивных пользователей завершен.")

    except Exception as e:
        await callback.message.answer(f"Произошла ошибка: {e}")


# Парсим пользователей канала
def parse_user_ids(members):
    user_ids = []
    for member in members:
        match = re.match(r'(\d+):', member)
        if match:
            user_id = int(match.group(1))
            user_ids.append(user_id)
    return user_ids
