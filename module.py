import logging
from pyrogram import Client
from pyrogram.raw.functions.contacts import ResolveUsername
from config.config import TgBot, load_config

# Установка уровня логирования для pyrogram
logging.getLogger("pyrogram").setLevel(logging.WARNING)


config: TgBot = load_config()

BOT_TOKEN = config.token


async def resolve_username_to_user_id(username: str) -> int | None:
    # Создаем клиент внутри функции
    async with Client(
            "bot",
            api_id=25046789,
            api_hash="3331710ae9db228a2d2834493e6fdd05",
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