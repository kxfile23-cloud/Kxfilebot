import logging
import traceback

from telegram.ext import Application

from config import BOT_TOKEN
from handlers.start import start_handler

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

print("STARTING BOT...")

try:

    app = Application.builder().token(
        BOT_TOKEN
    ).build()

    print("APPLICATION SUCCESS")

    app.add_handler(start_handler)

    print("HANDLER SUCCESS")

    print("BOT RUNNING...")
    print("SUPABASE CONNECTED...")

    app.run_polling(
        drop_pending_updates=True
    )

except Exception as e:

    print("\nERROR DETECTED:\n")

    traceback.print_exc()

    print("\nERROR MESSAGE:")
    print(str(e))
