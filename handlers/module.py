from pyrogram import Client
from pyrogram.raw.functions.contacts import ResolveUsername
from config.config import TgBot, load_config


config: TgBot = load_config()

BOT_TOKEN = config.token

pyrogram_client = Client(
    "bot",
    api_id=6,
    api_hash="eb06d4abfb49dc3eeb1aeb98ae0f581e",
    bot_token=BOT_TOKEN,
    app_version="7.7.2",
    system_version="11 R"
)


def resolve_username_to_user_id(username: str) -> int | None:
    with pyrogram_client:
        r = pyrogram_client.invoke(ResolveUsername(username=username))
        if r.users:
            return r.users[0].id
        return None


