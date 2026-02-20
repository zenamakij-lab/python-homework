import asyncio
import random
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

TOKEN = "8561779148:AAFyntqN-vgFTLQJ2TmLQ29ZACZrVPjEK_4"

bot = Bot(token=TOKEN)
dp = Dispatcher()

participants = []

@dp.message(CommandStart())
async def start(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text=" Участвовать", callback_data="join"))
    builder.add(InlineKeyboardButton(text=" Крутить", callback_data="spin"))

    await message.answer(
        "Добро пожаловать в игру 'Кто сегодня ПИДОР?'",
        reply_markup=builder.as_markup()
    )

@dp.callback_query(lambda c: c.data == "join")
async def join(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in participants:
        participants.append(user_id)
        await callback.message.answer("Ты добавлен в игру ")
    else:
        await callback.message.answer("Ты уже участвуешь ")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "spin")
async def spin(callback: types.CallbackQuery):
    if not participants:
        await callback.message.answer("Никто не участвует 😢")
    else:
        winner = random.choice(participants)
        if callback.from_user.id == winner:
            await callback.message.answer(" Сегодня ты ПИДОР!")
        else:
            await callback.message.answer("Сегодня ты не пидор(")
    await callback.answer()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())