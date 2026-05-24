from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler

from database import supabase
from services.force_sub import force_sub, join_keyboard

ADMIN_IDS = [8603038811]  # ganti ID kamu


from telegram import ReplyKeyboardMarkup

def main_menu():
    return ReplyKeyboardMarkup(
        [
            ["📥 Get File", "📤 Up File"],
            ["👤 Account", "🆘 Help"],
            ["💎 VIP", "👑 VVIP"]
        ],
        resize_keyboard=True
    )


def admin_menu():
    return ReplyKeyboardMarkup(
        [
            ["📥 Get File", "📤 Up File"],
            ["👤 Account", "💹 Statistik"],
            ["💎 VIP User", "👑 VVIP User"],
            ["✖️ Unvip User"]
        ],
        resize_keyboard=True
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    cek_join = await force_sub(context.bot, user.id)

    if not cek_join:
        await update.message.reply_text(
            "🚫 JOIN CHANNEL DULU",
            reply_markup=join_keyboard()
        )
        return

    cek = supabase.table("users") \
        .select("*") \
        .eq("id", user.id) \
        .execute()

    if not cek.data:
        supabase.table("users").insert({
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name
        }).execute()

    teks = "🔥 WELCOME TO FILE BOT 🔥"

    if user.id in ADMIN_IDS:
        await update.message.reply_text(
            teks,
            reply_markup=admin_menu()
        )
    else:
        await update.message.reply_text(
            teks,
            reply_markup=main_menu()
        )


start_handler = CommandHandler("start", start)
