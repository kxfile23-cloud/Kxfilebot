from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler

from database import supabase
from services.force_sub import force_sub, join_keyboard

# ================= ADMIN =================
ADMIN_IDS = [8603038811]  # ganti ID kamu


# ================= MENUS =================
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


# ================= START COMMAND =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    # ================= FORCE SUB =================
    try:
        cek_join = await force_sub(context.bot, user.id)
    except Exception:
        cek_join = True  # fallback biar bot tidak mati

    if not cek_join:
        await update.message.reply_text(
            "🚫 JOIN CHANNEL DULU UNTUK MENGGUNAKAN BOT",
            reply_markup=join_keyboard()
        )
        return

    # ================= USER CHECK / INSERT =================
    try:
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

    except Exception as e:
        print("SUPABASE ERROR:", e)

    # ================= TEXT =================
    teks = (
        "🔥 WELCOME TO FILE BOT 🔥\n\n"
        "📥 Upload media jadi code\n"
        "📤 Get file pakai code\n"
    )

    # ================= MENU =================
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


# ================= HANDLER =================
start_handler = CommandHandler("start", start)
