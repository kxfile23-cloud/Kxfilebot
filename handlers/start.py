from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from database import supabase

from services.force_sub import (
    force_sub,
    join_keyboard
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    cek_join = await force_sub(
        context.bot,
        user.id
    )

    if not cek_join:

        teks = """
🚫 WOI JOIN CHANNEL DULU NGAB 😹

Belum join udah napsu pengen buka koleksi 😭

📢 Join dulu baru gua kasih akses.
"""

        await update.message.reply_text(
            teks,
            reply_markup=join_keyboard()
        )

        return

    cek = supabase.table(
        "users"
    ).select(
        "*"
    ).eq(
        "id",
        user.id
    ).execute()

    if not cek.data:

        supabase.table(
            "users"
        ).insert({
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name
        }).execute()

    teks = f"""
🔥 WELCOME TO KX FILE BOT 🔥

📦 Upload media jadi code.
🔓 Paste code buat buka media.

💎 FREE USER:
• 25 media / 24 jam

💎 VIP USER:
• 100 media / 24 jam

😈 Gaskeun Bray.
"""

    await update.message.reply_text(
        teks
    )


start_handler = CommandHandler(
    "start",
    start
)
