from dataclasses import dataclass
from environs import Env


@dataclass
class TgBot:
    token: str
    channel_id_one: str
    api_id: int
    api_hash: str


# Создание функции, которая будет читать файл .env и возвращать экземпляр
# класса Config с заполненными полями token и admin_ids
def load_config(path: str | None = None) -> TgBot:
    env = Env()
    env.read_env(path)
    return TgBot(
        token=env('BOT_TOKEN'),
        channel_id_one=env('CHANNEL_ID'),
        api_id=env('API_ID'),
        api_hash=env('API_HASH')
    )
