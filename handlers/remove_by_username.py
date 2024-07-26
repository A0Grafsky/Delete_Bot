from aiogram.filters import Command
from aiogram import Router
from aiogram import types
import os
from aiogram import Bot, Dispatcher

router = Router()

CHANNEL_ID = os.getenv('CHANNEL_ID')


async def kick_user(message: types.Message, bot: Bot, channel_id: str):
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
        await bot.kick_chat_member(channel_id, user_id)
        await message.reply(f"Пользователь {username} удален из канала.")
    except Exception as e:
        await message.reply(f"Не удалось удалить пользователя {username}. Ошибка: {e}")


def reregister_handlers(dp: Dispatcher):
    dp.message.register(kick_user, Command("kick"))
