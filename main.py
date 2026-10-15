import asyncio
import logging
 
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
 
import config
import db
from utils import clean_answer, load_data
 
dp = Dispatcher()
data = load_data(config.DATA_FILE)
 
 
@dp.message(CommandStart())
async def cmd_start(message: Message):
    name = message.from_user.full_name
    db.add_user(message.from_user.id, name)
    await message.answer(
        f"Привет, {name}!\n\nВопрос: {data['question']}\n"
        "Напиши ответ. Статистика — команда /stats"
    )
 
 
@dp.message(Command("stats"))
async def cmd_stats(message: Message):
    stats = db.get_stats(message.from_user.id)
    if stats is None:
        await message.answer("Сначала нажми /start")
        return
    name, errors, correct = stats
    await message.answer(
        f"{name}\nПравильных ответов: {correct}\nОшибок: {errors}"
    )
 
 
@dp.message(F.text, ~F.text.startswith("/"))
async def check_answer(message: Message):
    user_id = message.from_user.id
    db.add_user(user_id, message.from_user.full_name)
 
    user_answer = clean_answer(message.text).lower()
    right_answer = clean_answer(data["answer"]).lower()
 
    if user_answer == right_answer:
        db.add_correct(user_id)
        await message.answer("Верно! ✅")
    else:
        db.add_error(user_id)
        await message.answer("Неверно, попробуй ещё раз ❌")
 
 
async def main():
    logging.basicConfig(level=logging.INFO)
    db.init_db()
    bot = Bot(token=config.BOT_TOKEN)
    await dp.start_polling(bot)
 
 
if __name__ == "__main__":
    asyncio.run(main())
