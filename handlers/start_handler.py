from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from keyboards.inline_keyboard import create_inline_kb
from aiogram import Bot, Dispatcher
from config.config import TgBot, load_config
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import StateFilter


router = Router()
config: TgBot = load_config()

CHANNEL_ID = config.channel_id_one


class Fsm(StatesGroup):
    input = State()
    kick = State()




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
async def kick_user(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Fsm.input)
    await callback.message.answer("Пожалуйста, укажите ник пользователя для удаления (например, @username):")
    await callback.answer()


@router.message(StateFilter(Fsm.input), F.text)
async def kick_user(message: Message, bot: Bot):
    username = message.text.strip() if message.text else None
    if not username:
        await message.reply("Ник пользователя не может быть пустым. Попробуйте снова.")
        return

    if not username.startswith('@'):
        username = '@' + username

    try:
        # Получаем информацию о пользователе по его никнейму
        member = await bot.get_chat_member(CHANNEL_ID, username)
        user_id = member.user.id

        # Удаляем пользователя из канала
        await bot.ban_chat_member(CHANNEL_ID, user_id)
        await message.reply(f"Пользователь {username} удален из канала.")
    except Exception as e:
        await message.reply(f"Не удалось удалить пользователя {username}. Ошибка: {e}")