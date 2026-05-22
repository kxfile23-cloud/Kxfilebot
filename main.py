import os
import base64
import sqlite3
import logging
from math import ceil

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup
)

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# =========================================================
# LOGGING
# =========================================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# =========================================================
# CONFIG
# =========================================================

BOT_TOKEN = os.getenv("BOT_TOKEN")

DB_CHANNEL = int(
    os.getenv("DB_CHANNEL")
)

ADMIN_ID = int(
    os.getenv("ADMIN_ID")
)

FORCE_CHANNEL = os.getenv(
    "FORCE_CHANNEL"
)

FORCE_GROUP = os.getenv(
    "FORCE_GROUP"
)

ADMIN_USERNAME = os.getenv(
    "ADMIN_USERNAME"
)

BOT_USERNAME = os.getenv(
    "BOT_USERNAME"
)

# =========================================================
# SQLITE
# =========================================================

conn = sqlite3.connect(
    "database.db",
    check_same_thread=False
)

db = conn.cursor()

# =========================================================
# TABLE USERS
# =========================================================

db.execute("""
CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    plan TEXT DEFAULT 'FREE',
    opened INTEGER DEFAULT 0
)
""")

# =========================================================
# TABLE CODES
# =========================================================

db.execute("""
CREATE TABLE IF NOT EXISTS codes(
    code TEXT,
    owner INTEGER,
    views INTEGER DEFAULT 0,
    total INTEGER DEFAULT 0
)
""")

conn.commit()

# =========================================================
# TEMP STORAGE
# =========================================================

user_media = {}

user_notif = {}

# =========================================================
# ADD USER
# =========================================================

def add_user(user_id, username):

    db.execute(
        "SELECT * FROM users WHERE user_id=?",
        (user_id,)
    )

    data = db.fetchone()

    if data is None:

        db.execute(
            """
            INSERT INTO users(
                user_id,
                username
            )
            VALUES(?,?)
            """,
            (
                user_id,
                username
            )
        )

        conn.commit()

# =========================================================
# GET PLAN
# =========================================================

def get_user_plan(user_id):

    db.execute(
        """
        SELECT plan, opened
        FROM users
        WHERE user_id=?
        """,
        (user_id,)
    )

    data = db.fetchone()

    if not data:
        return "FREE", 0

    return data[0], data[1]

# =========================================================
# UPDATE OPENED
# =========================================================

def update_opened(user_id, total):

    db.execute(
        """
        UPDATE users
        SET opened = opened + ?
        WHERE user_id=?
        """,
        (
            total,
            user_id
        )
    )

    conn.commit()

# =========================================================
# CHECK LIMIT
# =========================================================

def check_limit(user_id, total_media):

    plan, opened = get_user_plan(
        user_id
    )

    if plan == "FREE":

        if opened + total_media > 25:
            return False

    elif plan == "VIP":

        if opened + total_media > 100:
            return False

    elif plan == "VVIP":
        return True

    return True

# =========================================================
# MAIN MENU
# =========================================================

def main_menu():

    keyboard = [
        ["Start🚀", "Trending🔥"],
        ["New 🆕", "My Code📁"],
        ["My Account🧑‍🏫"],
        ["Help📃", "Admin🧑‍💼"]
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )

# =========================================================
# UPGRADE BUTTON
# =========================================================

def upgrade_button():

    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "💎 Upgrade Plan",
                    url=f"https://t.me/{ADMIN_USERNAME}"
                )
            ]
        ]
    )

# =========================================================
# ENCODE CODE
# =========================================================

def encode_code(ids):

    text = "-".join(
        map(str, ids)
    )

    encoded = base64.urlsafe_b64encode(
        text.encode()
    ).decode()

    return f"kxfilebot_{encoded}"

# =========================================================
# DECODE CODE
# =========================================================

def decode_code(code):

    encoded = code.replace(
        "kxfilebot_",
        ""
    )

    decoded = base64.urlsafe_b64decode(
        encoded
    ).decode()

    return list(
        map(
            int,
            decoded.split("-")
        )
    )

# =========================================================
# FORCE SUB CHECK
# =========================================================

async def subscribed(user_id, bot):

    try:

        channel = await bot.get_chat_member(
            FORCE_CHANNEL,
            user_id
        )

        group = await bot.get_chat_member(
            FORCE_GROUP,
            user_id
        )

        ok1 = channel.status in [
            "member",
            "administrator",
            "creator"
        ]

        ok2 = group.status in [
            "member",
            "administrator",
            "creator"
        ]

        return ok1 and ok2

    except:
        return False

# =========================================================
# FORCE MESSAGE
# =========================================================

async def force_sub_message(update):

    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "📢 Join Channel",
                    url=f"https://t.me/{FORCE_CHANNEL.replace('@','')}"
                )
            ],
            [
                InlineKeyboardButton(
                    "👥 Join Group",
                    url=f"https://t.me/{FORCE_GROUP.replace('@','')}"
                )
            ],
            [
                InlineKeyboardButton(
                    "✅ Joined",
                    callback_data="check_join"
                )
            ]
        ]
    )

    await update.message.reply_text(
"""
❌ You must join channel and group first.
""",
        reply_markup=buttons
    )

# =========================================================
# START
# =========================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    add_user(
        user.id,
        user.username
    )

    check = await subscribed(
        user.id,
        context.bot
    )

    if not check:
        return await force_sub_message(update)

    text = f"""
🚀 Welcome to KXBOT

Send media to me and I will create permanent code.

Send code to me and I will send media.

🤖 @{BOT_USERNAME}
"""

    await update.message.reply_text(
        text,
        reply_markup=main_menu()
    )

# =========================================================
# CHECK JOIN
# =========================================================

async def check_join(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    check = await subscribed(
        query.from_user.id,
        context.bot
    )

    if not check:

        return await query.answer(
            "Join first",
            show_alert=True
        )

    await query.message.delete()

    await context.bot.send_message(
        chat_id=query.message.chat.id,
        text="✅ Verification Success",
        reply_markup=main_menu()
    )

# =========================================================
# SAVE MEDIA
# =========================================================

async def save_media(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    check = await subscribed(
        user_id,
        context.bot
    )

    if not check:
        return await force_sub_message(update)

    copied = await context.bot.copy_message(
        chat_id=DB_CHANNEL,
        from_chat_id=update.message.chat.id,
        message_id=update.message.message_id
    )

    if user_id not in user_media:
        user_media[user_id] = []

    user_media[user_id].append(
        copied.message_id
    )

    total = len(
        user_media[user_id]
    )

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "✅ Create Code",
                    callback_data="create_code"
                )
            ]
        ]
    )

    text = f"""
📥 Media Added

📦 Total Media : {total}

Click button below to create code.
"""

    try:

        old_msg = user_notif.get(user_id)

        if old_msg:

            await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=old_msg,
                text=text,
                reply_markup=keyboard
            )

        else:

            msg = await update.message.reply_text(
                text,
                reply_markup=keyboard
            )

            user_notif[user_id] = msg.message_id

    except:

        msg = await update.message.reply_text(
            text,
            reply_markup=keyboard
        )

        user_notif[user_id] = msg.message_id

# =========================================================
# CREATE CODE
# =========================================================

async def create_code(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    user_id = query.from_user.id

    ids = user_media.get(user_id)

    if not ids:

        return await query.message.reply_text(
            "❌ No media"
        )

    code = encode_code(ids)

    total = len(ids)

    db.execute(
        """
        INSERT INTO codes(
            code,
            owner,
            total
        )
        VALUES(?,?,?)
        """,
        (
            code,
            user_id,
            total
        )
    )

    conn.commit()

    try:

        notif = user_notif.get(user_id)

        if notif:

            await context.bot.delete_message(
                chat_id=query.message.chat.id,
                message_id=notif
            )

    except:
        pass

    await query.message.reply_text(
f"""
✅ Code Created

📦 Total Media : {total}

🔑 CODE:

<code>{code}</code>
""",
        parse_mode="HTML"
    )

    user_media[user_id] = []

    if user_id in user_notif:
        del user_notif[user_id]

# =========================================================
# SEND PAGE
# =========================================================

async def send_page(
    update,
    context,
    code,
    page
):

    ids = decode_code(code)

    user_id = update.effective_user.id

    plan, opened = get_user_plan(
        user_id
    )

    protect = True

    if plan in ["VIP", "VVIP"]:
        protect = False

    pages = [
        ids[i:i + 10]
        for i in range(
            0,
            len(ids),
            10
        )
    ]

    selected = pages[page]

    for msg_id in selected:

        try:

            await context.bot.copy_message(
                chat_id=update.effective_chat.id,
                from_chat_id=DB_CHANNEL,
                message_id=msg_id,
                protect_content=protect
            )

        except:
            pass

    update_opened(
        user_id,
        len(selected)
    )

    total_pages = len(pages)

    row = []

    for i in range(total_pages):

        if i == page:
            txt = f"🔵{i+1}"
        else:
            txt = f"🔴{i+1}"

        row.append(
            InlineKeyboardButton(
                txt,
                callback_data=f"page_{i}_{code}"
            )
        )

    return InlineKeyboardMarkup([row])

# =========================================================
# OPEN CODE
# =========================================================

async def open_code(update: Update, context: ContextTypes.DEFAULT_TYPE, code):

    try:

        ids = decode_code(code)

    except Exception as e:

        return await update.message.reply_text(
f"""
❌ Invalid / Old Code

Reason:
{e}
"""
        )

    user_id = update.effective_user.id

    total_media = len(ids)

    allowed = check_limit(
        user_id,
        total_media
    )

    plan, opened = get_user_plan(
        user_id
    )

    if not allowed:

        if plan == "FREE":

            return await update.message.reply_text(
"""
❌ FREE LIMIT REACHED

📦 25 Media / Day
""",
                reply_markup=upgrade_button()
            )

        elif plan == "VIP":

            return await update.message.reply_text(
"""
❌ VIP LIMIT REACHED

📦 100 Media / Day
""",
                reply_markup=upgrade_button()
            )

    keyboard = await send_page(
        update,
        context,
        code,
        0
    )

    db.execute(
        """
        UPDATE codes
        SET views = views + 1
        WHERE code=?
        """,
        (code,)
    )

    conn.commit()

    total_pages = ceil(
        len(ids) / 10
    )

    await update.message.reply_text(
f"""
📄 Current Page : 1/{total_pages}

📦 Total Media : {len(ids)}

💎 Plan : {plan}
""",
        reply_markup=keyboard
    )

# =========================================================
# PAGE CALLBACK
# =========================================================

async def page_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    data = query.data.split("_")

    page = int(data[1])

    code = "_".join(data[2:])

    ids = decode_code(code)

    keyboard = await send_page(
        query,
        context,
        code,
        page
    )

    total_pages = ceil(
        len(ids) / 10
    )

    await query.message.edit_text(
f"""
📄 Current Page : {page+1}/{total_pages}

📦 Total Media : {len(ids)}
""",
        reply_markup=keyboard
    )

# =========================================================
# TEXT HANDLER
# =========================================================

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    # START
    if text == "Start🚀":
        return await start(update, context)

    # TRENDING
    elif text == "Trending🔥":

        db.execute(
            """
            SELECT code, views
            FROM codes
            ORDER BY views DESC
            LIMIT 10
            """
        )

        data = db.fetchall()

        if not data:

            return await update.message.reply_text(
                "No trending code"
            )

        txt = "🔥 TRENDING CODES\n\n"

        for code, views in data:

            txt += f"""
🔑 {code}

👁 Views : {views}

"""

        return await update.message.reply_text(txt)

    # NEW
    elif text == "New 🆕":

        db.execute(
            """
            SELECT code
            FROM codes
            ORDER BY rowid DESC
            LIMIT 10
            """
        )

        data = db.fetchall()

        if not data:

            return await update.message.reply_text(
                "No code"
            )

        txt = "🆕 NEW CODES\n\n"

        for x in data:
            txt += f"🔑 {x[0]}\n\n"

        return await update.message.reply_text(txt)

    # MY CODE
    elif text == "My Code📁":

        db.execute(
            """
            SELECT code, views
            FROM codes
            WHERE owner=?
            ORDER BY views DESC
            """,
            (update.effective_user.id,)
        )

        data = db.fetchall()

        if not data:

            return await update.message.reply_text(
                "No code"
            )

        txt = "📁 MY CODES\n\n"

        for code, views in data:

            txt += f"""
🔑 {code}

👁 Views : {views}

"""

        return await update.message.reply_text(txt)

    # ACCOUNT
    elif text == "My Account🧑‍🏫":

        user = update.effective_user

        plan, opened = get_user_plan(
            user.id
        )

        return await update.message.reply_text(
f"""
🧑‍🏫 MY ACCOUNT

👤 Username :
@{user.username}

🆔 ID :
{user.id}

💎 Plan :
{plan}

📦 Daily Opened :
{opened}

💰 PRICE

VIP
1D = 15K
2D = 20K
3D = 25K
4D = 30K

VVIP
1M = 120K
2M = 200K
""",
            reply_markup=upgrade_button()
        )

    # HELP
    elif text == "Help📃":

        return await update.message.reply_text(
"""
📃 HOW TO USE

1. Send media
2. Click create code
3. Copy code
4. Send code

💎 FREE
• 25 media/day
• no forward

💎 VIP
• 100 media/day
• can forward

💎 VVIP
• unlimited
• unlimited forward
"""
        )

    # ADMIN
    elif text == "Admin🧑‍💼":

        if update.effective_user.id != ADMIN_ID:

            return await update.message.reply_text(
                "❌ Admin only"
            )

        db.execute(
            "SELECT COUNT(*) FROM users"
        )

        users = db.fetchone()[0]

        db.execute(
            "SELECT COUNT(*) FROM codes"
        )

        codes = db.fetchone()[0]

        return await update.message.reply_text(
f"""
🧑‍💼 ADMIN PANEL

👤 Users : {users}

🔑 Codes : {codes}
"""
        )

    # OPEN CODE
    elif text.startswith("kxfilebot_"):

        return await open_code(
            update,
            context,
            text
        )

# =========================================================
# VIP COMMAND
# =========================================================

async def vip(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    try:

        user_id = int(
            context.args[0]
        )

        plan = context.args[1]

    except:

        return await update.message.reply_text(
"""
Usage:

/vip user_id VIP
/vip user_id VVIP
"""
        )

    db.execute(
        """
        UPDATE users
        SET plan=?
        WHERE user_id=?
        """,
        (
            plan,
            user_id
        )
    )

    conn.commit()

    await update.message.reply_text(
        f"✅ {user_id} upgraded to {plan}"
    )

# =========================================================
# BROADCAST
# =========================================================

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    text = " ".join(context.args)

    if not text:

        return await update.message.reply_text(
            "/broadcast your message"
        )

    db.execute(
        "SELECT user_id FROM users"
    )

    users = db.fetchall()

    success = 0

    for user in users:

        try:

            await context.bot.send_message(
                chat_id=user[0],
                text=text
            )

            success += 1

        except:
            pass

    await update.message.reply_text(
        f"✅ Broadcast sent to {success} users"
    )

# =========================================================
# APPLICATION
# =========================================================

app = Application.builder().token(
    BOT_TOKEN
).build()

# COMMANDS
app.add_handler(
    CommandHandler(
        "start",
        start
    )
)

app.add_han
