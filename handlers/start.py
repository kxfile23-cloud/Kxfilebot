from aiogram import F, Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from db import supabase

router = Router()

CHANNEL_ID = -1003777107004
GROUP_ID = -1003721009353


# cek join
async def check_join(bot, user_id):
    try:
        ch = await bot.get_chat_member(CHANNEL_ID, user_id)
        gp = await bot.get_chat_member(GROUP_ID, user_id)

        if ch.status in ["left", "kicked"]:
            return False
        if gp.status in ["left", "kicked"]:
            return False

        return True
    except:
        return False


@router.message(F.text == "/start")
async def start(message: Message):
    user = message.from_user
    user_id = user.id
    username = user.username or "no_username"

    # simpan user
    supabase.table("users").upsert({
        "user_id": user_id,
        "username": username
    }).execute()

    # FORCE JOIN CHECK
    joined = await check_join(message.bot, user_id)

    if not joined:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📢 Join Channel", url="https://t.me/+OzP85qRqCUhjMDE1")],
            [InlineKeyboardButton(text="👥 Join Group", url="https://t.me/+DTL9cOR34ipmM2U1")],
            [InlineKeyboardButton(text="🔄 Cek Join", callback_data="check_join")]
        ])

        await message.answer(
            "⚠️ Join Terlebih Dahulu sebelum menggunakan bot\n\n"
            "˗ˏˋ © EarnFileBot ˎˊ˗",
            reply_markup=keyboard
        )
        return

    # ambil balance
    user_data = supabase.table("users").select("*").eq("user_id", user_id).execute()
    balance = 0

    if user_data.data:
        balance = user_data.data[0].get("balance", 0)

    text = (
        "🤖 EARNFILEBOT\n\n"
        f"🆔 ID : {user_id}\n"
        f"👤 NAME : @{username}\n"
        f"💰 BALANCE : Rp{balance}\n\n"
        "˗ˏˋ © EarnFileBot Of Telegram ˎˊ˗"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📤 Upfile", callback_data="upload"),
            InlineKeyboardButton(text="📥 Getfile", callback_data="getfile")
        ],
        [
            InlineKeyboardButton(text="⚙️ Setting", callback_data="setting"),
            InlineKeyboardButton(text="🏧 Withdraw", callback_data="withdraw")
        ],
        [
            InlineKeyboardButton(text="🆘 Help", callback_data="help"),
            InlineKeyboardButton(text="ℹ️ About", callback_data="about")
        ]
    ])

    await message.answer(text, reply_markup=keyboard)
