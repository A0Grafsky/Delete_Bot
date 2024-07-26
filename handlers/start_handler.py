from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from keyboards.inline_keyboard import create_inline_kb
from aiogram import Bot, Dispatcher
from config.config import TgBot, load_config

router = Router()
config: TgBot = load_config()


@router.message(CommandStart())
async def send_welcome(message: Message):
    await message.answer(
        "Привет! Используй команды для управления подписчиками:\n"
        "Удаление по нику - После ввода ника, пользователей будет удален\n"
        "/remove_first <n> - удалить первых N подписчиков\n"
        "/remove_last <n> - удалить последних N подписчиков\n"
        "/remove_deleted - удалить неактивных пользователей.",
        reply_markup=create_inline_kb(2, 'remove_by_username')
    )


CHANNEL_ID = config.channel_id_one


@router.callback_query(F.data == 'remove_by_username')
async def kick_user(message: Message, bot: Bot, channel_id: str):
    args = message.get_args()
    if not args:
        await message.reply("Пожалуйста, укажите ник пользователя, например: /kick @username")
        return

    username = args.split()[0]
    if not username.startswith('@'):
        username = '@' + username

    try:
        # Получаем информацию о пользователе по его никнейму
        member = await bot.get_chat_member(channel_id, username)
        user_id = member.user.id

        # Удаляем пользователя из канала
        await bot.ban_chat_member(channel_id, user_id)
        await message.reply(f"Пользователь {username} удален из канала.")
    except Exception as e:
        await message.reply(f"Не удалось удалить пользователя {username}. Ошибка: {e}")