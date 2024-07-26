from dataclasses import dataclass
from environs import Env


@dataclass
class TgBot:
    token: str


# Создание функции, которая будет читать файл .env и возвращать экземпляр
# класса Config с заполненными полями token и admin_ids
def load_config(path: str | None = None) -> TgBot:
    env = Env()
    env.read_env(path)
    return TgBot(
        token=env('BOT_TOKEN')
    )
