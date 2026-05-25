import random
import string

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, MessageHandler, filters

UPLOAD_SESSION = {}
LOG_CHANNEL = -1003993516320


# ================= START UPLOAD =================
async def up_file_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    user_id = query.from_user.id

    UPLOAD_SESSION[user_id] = {
        "files": [],
        "active": True
    }

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel_upload")]
    ])

    await query.message.edit_text(
        "📤 SILAKAN KIRIM MEDIA SEKARANG",
        reply_markup=keyboard
    )

    await query.answer()


# ================= HANDLE MEDIA =================
async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if user_id not in UPLOAD_SESSION:
        return

    session = UPLOAD_SESSION[user_id]

    if not session.get("active"):
        return

    file_id = None
    mtype = None

    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        mtype = "p"

    elif update.message.video:
        file_id = update.message.video.file_id
        mtype = "v"

    elif update.message.document:
        file_id = update.message.document.file_id
        mtype = "d"

    if not file_id:
        return

    session["files"].append({"file_id": file_id, "type": mtype})

    total = len(session["files"])

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ DONE", callback_data="done_upload"),
            InlineKeyboardButton("❌ CANCEL", callback_data="cancel_upload")
        ]
    ])

    await update.message.reply_text(
        f"📦 UPLOADING...\nTotal: {total}",
        reply_markup=keyboard
    )

    try:
        await update.message.delete()
    except:
        pass


# ================= GENERATE CODE =================
def generate_code(files):

    v = sum(1 for x in files if x["type"] == "v")
    p = sum(1 for x in files if x["type"] == "p")
    d = sum(1 for x in files if x["type"] == "d")

    mix = f"{v}v_{p}p_{d}d"
    rand = ''.join(random.choices(string.ascii_letters + string.digits, k=10))

    return mix, f"kxfilebot_{len(files)}V_{rand}"


# ================= DONE =================
async def done_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    user_id = query.from_user.id

    session = UPLOAD_SESSION.get(user_id)

    if not session:
        await query.answer()
        return

    files = session["files"]

    mix, code = generate_code(files)

    await context.bot.send_message(
        chat_id=LOG_CHANNEL,
        text=f"""
📥 NEW UPLOAD

Code: {code}
Mix: {mix}
Total: {len(files)}
User: {user_id}
"""
    )

    await query.message.edit_text(
        f"""
📥 UPLOAD SELESAI

Code: {code}
Total: {len(files)}
"""
    )

    UPLOAD_SESSION.pop(user_id, None)

    await query.answer()


# ================= CANCEL =================
async def cancel_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    UPLOAD_SESSION.pop(query.from_user.id, None)

    await query.message.edit_text("❌ UPLOAD DIBATALKAN")

    await query.answer()


# ================= HANDLERS =================
up_file_callback_handler = CallbackQueryHandler(up_file_callback, pattern="up_file")
done_upload_handler = CallbackQueryHandler(done_upload, pattern="done_upload")
cancel_upload_handler = CallbackQueryHandler(cancel_upload, pattern="cancel_upload")

handle_media_handler = MessageHandler(
    filters.PHOTO | filters.VIDEO | filters.Document.ALL,
    handle_media
    )
    files = session["files"]

    mix, code = generate_code(files)

    await context.bot.send_message(
        chat_id=LOG_CHANNEL,
        text=f"""
📥 NEW UPLOAD

Code: {code}
Mix: {mix}
Total: {len(files)}
User: {user_id}
"""
    )

    await query.message.edit_text(
        f"📥 DONE\nCode: {code}\nTotal: {len(files)}"
    )

    UPLOAD_SESSION.pop(user_id, None)

    await query.answer()


# ================= CANCEL =================
async def cancel_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    UPLOAD_SESSION.pop(query.from_user.id, None)

    await query.message.edit_text("❌ CANCELLED")

    await query.answer()


# ================= HANDLERS (FIX PENTING) =================
up_file_callback_handler = CallbackQueryHandler(up_file_callback, pattern="up_file")
done_upload_handler = CallbackQueryHandler(done_upload, pattern="done_upload")
cancel_upload_handler = CallbackQueryHandler(cancel_upload, pattern="cancel_upload")

handle_media_handler = MessageHandler(
    filters.PHOTO | filters.VIDEO | filters.Document.ALL,
    handle_media
    )
