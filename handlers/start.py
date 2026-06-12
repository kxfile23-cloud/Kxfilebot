from aiogram import F, Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from db import supabase

router = Router()

CHANNEL_ID = -1003712587847
GROUP_ID = -1003920865154


@router.message(F.text == "/start")
async def start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or "no_username"

    # simpan user
    supabase.table("users").upsert({
        "user_id": user_id,
        "username": username
    }).execute()

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📤 Upload Media", callback_data="upload")],
        [InlineKeyboardButton(text="📥 Get File", callback_data="getfile")],
        [InlineKeyboardButton(text="💰 Balance", callback_data="balance")],
        [InlineKeyboardButton(text="🏧 Withdraw", callback_data="withdraw")]
    ])

    await message.answer(
        "🤖 MARKETPLACE BOT\n\nSelect menu:",
        reply_markup=keyboard
    )
