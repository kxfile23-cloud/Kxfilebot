import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

DATABASE_CHANNEL_ID = int(os.getenv("DATABASE_CHANNEL_ID"))
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))

FORCE_SUB_CHANNEL = os.getenv("FORCE_SUB_CHANNEL")
UPDATE_CHANNEL = os.getenv("UPDATE_CHANNEL")

BOT_USERNAME = os.getenv("BOT_USERNAME")

ADMIN_IDS = list(
    map(
        int,
        os.getenv("ADMIN_IDS").split(",")
    )
)
