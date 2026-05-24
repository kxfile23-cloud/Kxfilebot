from telegram.ext import Application
from config import BOT_TOKEN
from database import supabase

app = Application.builder().token(
    BOT_TOKEN
).build()

print("BOT RUNNING...")
print("SUPABASE CONNECTED...")

app.run_polling()
