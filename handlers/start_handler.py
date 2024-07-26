from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery

from keyboards.inline_keyboard import create_inline_kb


router = Router()


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


@router.callback_query(F.data == 'remove_by_username')
async def remove_by_username(callback: CallbackQuery, message: Message):
    username = message.get_args().strip()

    if not username:
        await message.answer("Пожалуйста, укажите имя пользователя (ник).")
        return

    try:
        async for member in bot.get_chat_administrators(chat_id=CHANNEL_ID):
            if member.user.username == username:
                await bot.ban_chat_member(chat_id=CHANNEL_ID, user_id=member.user.id)
                await message.reply(f"Пользователь @{username} удален.")
                return
        await message.answer("Пользователь с таким ником не найден.")
    except Exception as e:
        await message.answer(f"Ошибка при удалении пользователя: {e}")


    await state.set_state()



