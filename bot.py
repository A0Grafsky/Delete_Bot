import asyncio
import logging

from aiogram import Bot, Dispatcher

from config.config import TgBot, load_config
from handlers import start_handler
from handlers import remove_by_username as rm


# Функция конфигурирования и запуска бота
async def main():
    # Конфигурация логирования
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(filename)s:%(lineno)d #%(levelname)-8s'
               '[%(asctime)s] - %(name)s - %(message)s'
    )

    # Выводим в консоль информацию о начале запуска бота
    logging.info('Starting bot')

    # Загружаем конфиг в переменную config
    config: TgBot = load_config()

    # Диспетчер
    bot = Bot(token=config.token)
    dp = Dispatcher()

    # Настраиваем главное меню

    # Регистрируем роутеры
    dp.include_router(start_handler.router)

    rm.reregister_handlers(dp)
    asyncio.run(dp.start_polling(bot, skip_updates=True))

    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    main()
