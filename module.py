import logging
from datetime import timezone

from pyrogram import Client
from pyrogram.raw.functions.contacts import ResolveUsername
from config.config import TgBot, load_config
import asyncio
from telethon.tl.types import User
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError, ChatAdminRequiredError

logging.getLogger("pyrogram").setLevel(logging.WARNING)

config: TgBot = load_config()
BOT_TOKEN = config.token
API_ID = config.api_id
API_HASH = config.api_hash
CHANNEL_ID = int(config.channel_id_one)


async def resolve_username_to_user_id(username: str) -> int | None:
    # Создаем клиент внутри функции
    async with Client(
            "bot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN
    ) as pyrogram_client:
        try:
            r = await pyrogram_client.invoke(ResolveUsername(username=username))
            if r.users:
                return r.users[0].id
            else:
                print(f"No users found for username: {username}")
                return None
        except Exception as e:
            print(f"Error resolving username {username}: {e}")
            return None


async def get_channel_members(channel_id: int):
    members = []
    async with Client(
            "bot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN
    ) as app:
        # Получаем участников канала по ID
        async for user in app.get_chat_members(channel_id):
            members.append(f'{user.user.id}: {user.user.first_name} {user.user.last_name}')
    return members


async def get_last_message(user_id: int):
    async with Client(
            "bot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN
    ) as app:
        last_message = None
        async for message in app.get_chat_history(CHANNEL_ID, limit=100):
            if message.from_user and message.from_user.id == user_id:
                last_message = message
                break
        return last_message


client = TelegramClient(
    'bot_session',  # Имя файла сессии
    API_ID,  # Ваш API ID
    API_HASH,  # Ваш API Hash
    device_model='Desktop',  # Модель устройства
    system_version='Mac OS',  # Версия операционной системы
    app_version='1.0'  # Версия вашего приложения
)



# Функция получения последнего сообщения пользователя
async def get_last_message_date(user_id: int):
    async with client:
        try:
            # Проверяем, доступен ли канал
            await client.get_entity(int(CHANNEL_ID))

            # Получаем последнее сообщение от пользователя
            async for message in client.iter_messages(int(CHANNEL_ID), from_user=user_id, limit=1):
                last_message_date = message.date
                # Приведение даты к временной зоне (UTC), если она не aware
                if last_message_date.tzinfo is None:
                    last_message_date = last_message_date.replace(tzinfo=timezone.utc)
                return last_message_date

            # Если сообщений нет
            return None

        except FloodWaitError as e:
            print(f"Rate limit exceeded. Waiting for {e.x} seconds.")
            await asyncio.sleep(e.x)
            return await get_last_message_date(user_id)

        except Exception as e:
            print(f"Error getting last message date for user {user_id}: {e}")
            return None