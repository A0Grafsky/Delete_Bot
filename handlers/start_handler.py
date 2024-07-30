import asyncio

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.handlers import callback_query
from aiogram.types import Message, CallbackQuery, InputFile, FSInputFile
from telethon.errors import UserNotParticipantError

from keyboards.inline_keyboard import create_inline_kb
from aiogram import Bot
from config.config import TgBot, load_config
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import StateFilter
from module import resolve_username_to_user_id as u_id
from module import get_channel_members
from module import get_last_message_date
import json
import os
from datetime import datetime, timedelta, timezone
import re

router = Router()
config: TgBot = load_config()

CHANNEL_ID = int(config.channel_id_one)


class Fsm_for_d(StatesGroup):
    input = State()

class Fsm_for_d_l(StatesGroup):
    input_1 = State()


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


@router.callback_query(F.data == 'remove_first')
async def start_remove_first(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Пожалуйста, укажите количество первых пользователей для удаления (например, 10):")
    await callback.answer()
    await state.set_state(Fsm_for_d.input)

@router.message(StateFilter(Fsm_for_d.input), F.text)
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



# Обработчик кнопки 'Удаление последних n-человек'
@router.callback_query(F.data == 'remove_last')
async def start_remove_last(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Пожалуйста, укажите количество последних пользователей для удаления (например, 10):")
    await callback.answer()
    await state.set_state(Fsm_for_d_l.input_1)

@router.message(StateFilter(Fsm_for_d_l.input_1, F.text))
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



def parse_user_ids(members):
    user_ids = []
    for member in members:
        match = re.match(r'(\d+):', member)
        if match:
            user_id = int(match.group(1))
            user_ids.append(user_id)
    return user_ids

