import logging
import os
import sys

from telegram.ext import Application
from handlers.start import start_handler
from handlers.upload import (
    up_file_callback_handler,
    done_upload_handler,
    cancel_upload_handler,
    handle_media_handler
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

print("STARTING BOT...")

# ================= LOCK =================
LOCK_FILE = "bot.lock"

if os.path.exists(LOCK_FILE):
    print("BOT SUDAH BERJALAN! STOP DUPLICATE INSTANCE.")
    sys.exit()

with open(LOCK_FILE, "w") as f:
    f.write(str(os.getpid()))

# ================= TOKEN =================
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is missing!")

try:
    app = Application.builder().token(BOT_TOKEN).build()

    print("APPLICATION SUCCESS")

    app.add_handler(start_handler)

    app.add_handler(up_file_callback_handler)
    app.add_handler(done_upload_handler)
    app.add_handler(cancel_upload_handler)
    app.add_handler(handle_media_handler)

    print("HANDLER SUCCESS")
    print("BOT RUNNING...")

    app.run_polling(drop_pending_updates=True)

except Exception as e:
    logging.exception("BOT ERROR OCCURRED")
    print(str(e))

finally:
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)
