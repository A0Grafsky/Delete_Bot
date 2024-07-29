from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from keyboards.inline_keyboard import create_inline_kb
from config.config import TgBot, load_config

router = Router()
config: TgBot = load_config()


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


