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



# Вывод всех пользователей (json)
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

############################################################

#
# async def get_last_message_date(user_id: int):
#     async for message in bot.get_chat_history(CHANNEL_ID):
#         if message.from_user and message.from_user.id == user_id:
#             return message.date
#     return None
#
# @router.callback_query(F.data == 'remove_deleted')
# async def remove_inactive(callback: CallbackQuery):
#     try:
#         await callback.message.answer("Начинаю процесс удаления неактивных пользователей...")
#
#         # Период неактивности
#         inactivity_threshold = timedelta(days=30)
#         cutoff_date = datetime.now() - inactivity_threshold
#
#         # Получаем список участников
#         members = await get_channel_members(CHANNEL_ID)
#
#         for member in members:
#             # Период времени после которого пользователь считается неактивным
#             last_message_date = await get_last_message_date(member.user.id)
#             if last_message_date and last_message_date < cutoff_date:
#                 try:
#                     await callback.bot.ban_chat_member(CHANNEL_ID, member.user.id)
#                     print(f"Пользователь {member.user.id} удален из канала из-за неактивности.")
#                 except Exception as e:
#                     print(f"Не удалось удалить пользователя {member.user.id}. Ошибка: {e}")
#
#         await callback.message.answer("Процесс удаления неактивных пользователей завершен.")
#
#     except Exception as e:
#         await callback.message.answer(f"Произошла ошибка: {e}")
#
#
