import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from config import BOT_TOKEN
from db import supabase

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(F.text == "/start")
async def start(message: Message):
    await message.answer("🤖 Marketplace Bot Aktif!")

@dp.message(F.text == "/db")
async def test_db(message: Message):
    data = supabase.table("users").select("*").execute()
    await message.answer(f"DB OK: {len(data.data)} users")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
