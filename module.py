import logging
from pyrogram import Client
from pyrogram.raw.functions.contacts import ResolveUsername
from config.config import TgBot, load_config

# Установка уровня логирования для pyrogram
logging.getLogger("pyrogram").setLevel(logging.WARNING)


config: TgBot = load_config()
BOT_TOKEN = config.token
API_ID = config.api_id
API_HASH = config.api_hash
CHANNEL_ID = config.channel_id_one


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


async def get_last_message_date(user_id: int,):
    async with Client(
            "bot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN
    ) as app:
        last_message_date = None
        async for message in app.get_chat_history(CHANNEL_ID, limit=100):
            if message.from_user and message.from_user.id == user_id:
                last_message_date = message.date
                break
        return last_message_date
