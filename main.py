import base64

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

# =========================================
# CONFIG
# =========================================

import os
import os

BOT_TOKEN = os.getenv(
    "BOT_TOKEN"
)

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
# =========================================
# TEMP STORAGE
# =========================================

user_media = {}

# =========================================
# ENCODE CODE
# =========================================

def encode_code(ids):

    text = "-".join(map(str, ids))

    encoded = base64.urlsafe_b64encode(
        text.encode()
    ).decode()

    return f"kxfilebot_{encoded}"

# =========================================
# DECODE CODE
# =========================================

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

# =========================================
# FORCE SUB CHECK
# =========================================

async def subscribed(
    user_id,
    bot
):

    try:

        channel = await bot.get_chat_member(
            FORCE_CHANNEL,
            user_id
        )

        group = await bot.get_chat_member(
            FORCE_GROUP,
            user_id
        )

        if channel.status in [
            "member",
            "administrator",
            "creator"
        ] and group.status in [
            "member",
            "administrator",
            "creator"
        ]:

            return True

        return False

    except:
        return False

# =========================================
# FORCE SUB MESSAGE
# =========================================

async def force_sub_message(
    update
):

    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Join Channel",
                    url=f"https://t.me/{FORCE_CHANNEL.replace('@','')}"
                )
            ],

            [
                InlineKeyboardButton(
                    "Join Group",
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

After joining click ✅ Joined
""",
        reply_markup=buttons
    )

# =========================================
# MAIN MENU
# =========================================

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

# =========================================
# START
# =========================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    check = await subscribed(
        update.effective_user.id,
        context.bot
    )

    if not check:

        return await force_sub_message(
            update
        )

    text = """
Welcome to KXBOT 🚀

Send media to me and I will create code.

Send code to me and I will send media.
"""

    await update.message.reply_text(
        text,
        reply_markup=main_menu()
    )

# =========================================
# CHECK JOIN BUTTON
# =========================================

async def check_join(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    check = await subscribed(
        query.from_user.id,
        context.bot
    )

    if not check:

        return await query.answer(
            "Join channel and group first",
            show_alert=True
        )

    await query.message.delete()

    await query.message.chat.send_message(
"""
✅ Verification success

Welcome to KXBOT 🚀
""",
        reply_markup=main_menu()
    )

# =========================================
# SAVE MEDIA
# =========================================

async def save_media(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    check = await subscribed(
        update.effective_user.id,
        context.bot
    )

    if not check:

        return await force_sub_message(
            update
        )

    user_id = update.effective_user.id

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

    video = 0
    photo = 0
    document = 0

    for msg_id in user_media[user_id]:

        try:

            msg = await context.bot.forward_message(
                chat_id=user_id,
                from_chat_id=DB_CHANNEL,
                message_id=msg_id
            )

            if msg.video:
                video += 1

            elif msg.photo:
                photo += 1

            elif msg.document:
                document += 1

            await context.bot.delete_message(
                chat_id=user_id,
                message_id=msg.message_id
            )

        except:
            pass

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Create",
                    callback_data="create_code"
                )
            ]
        ]
    )

    text = f"""
✅ {total} media received

🎥 Video : {video}
🖼 Photo : {photo}
📄 Document : {document}
"""

    await update.message.reply_text(
        text,
        reply_markup=keyboard
    )

# =========================================
# CREATE CODE
# =========================================

async def create_code(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    user_id = query.from_user.id

    ids = user_media.get(user_id)

    if not ids:

        return await query.message.reply_text(
            "No media found"
        )

    code = encode_code(ids)

    await query.message.reply_text(
f"""
✅ Code Created Successfully

<code>{code}</code>
""",
        parse_mode="HTML"
    )

    user_media[user_id] = []

# =========================================
# OPEN CODE
# =========================================

async def open_code(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    code
):

    try:

        ids = decode_code(code)

    except:

        return await update.message.reply_text(
            "❌ Invalid code"
        )

    pages = [
        ids[i:i + 10]
        for i in range(
            0,
            len(ids),
            10
        )
    ]

    total_pages = len(pages)

    first_page = pages[0]

    for msg_id in first_page:

        try:

            await context.bot.copy_message(
                chat_id=update.effective_chat.id,
                from_chat_id=DB_CHANNEL,
                message_id=msg_id,
                protect_content=True
            )

        except:
            pass

    row = []

    for i in range(total_pages):

        if i == 0:
            txt = f"🔵{i+1}"
        else:
            txt = f"🔴{i+1}"

        row.append(
            InlineKeyboardButton(
                txt,
                callback_data=f"page_{i}_{code}"
            )
        )

    await update.message.reply_text(
f"""
📄 Current Page : 1/{total_pages}
📦 Total Media : {len(ids)}
""",
        reply_markup=InlineKeyboardMarkup(
            [row]
        )
    )

# =========================================
# PAGE CALLBACK
# =========================================

async def page_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    data = query.data.split("_")

    page = int(data[1])

    code = "_".join(data[2:])

    ids = decode_code(code)

    pages = [
        ids[i:i + 10]
        for i in range(
            0,
            len(ids),
            10
        )
    ]

    selected_page = pages[page]

    for msg_id in selected_page:

        try:

            await context.bot.copy_message(
                chat_id=query.message.chat.id,
                from_chat_id=DB_CHANNEL,
                message_id=msg_id,
                protect_content=True
            )

        except:
            pass

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

    await query.message.edit_text(
f"""
📄 Current Page : {page+1}/{total_pages}
📦 Total Media : {len(ids)}
""",
        reply_markup=InlineKeyboardMarkup(
            [row]
        )
    )

# =========================================
# TEXT MENU
# =========================================

async def text_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    check = await subscribed(
        update.effective_user.id,
        context.bot
    )

    if not check:

        return await force_sub_message(
            update
        )

    text = update.message.text

    # =====================================
    # START
    # =====================================

    if text == "Start🚀":

        return await start(
            update,
            context
        )

    # =====================================
    # TRENDING
    # =====================================

    elif text == "Trending🔥":

        return await update.message.reply_text(
"""
🔥 Trending Codes

Coming soon...
"""
        )

    # =====================================
    # NEW
    # =====================================

    elif text == "New 🆕":

        return await update.message.reply_text(
"""
🆕 New Codes

Coming soon...
"""
        )

    # =====================================
    # MY CODE
    # =====================================

    elif text == "My Code📁":

        return await update.message.reply_text(
"""
📁 Your Codes

Coming soon...
"""
        )

    # =====================================
    # MY ACCOUNT
    # =====================================

    elif text == "My Account🧑‍🏫":

        user = update.effective_user

        return await update.message.reply_text(
f"""
🧑‍🏫 MY ACCOUNT

👤 Username:
@{user.username}

🆔 ID:
{user.id}

💎 Plan:
FREE
"""
        )

    # =====================================
    # HELP
    # =====================================

    elif text == "Help📃":

        return await update.message.reply_text(
"""
📃 HOW TO USE BOT

1. Send media to bot
2. Click Create
3. Copy generated code
4. Send code to open media

💎 FREE PLAN
• 20 media/day
• Protected media

💎 VIP PLAN
• 100 media/day
• 50 media shareable

💎 VVIP PLAN
• Unlimited access
• Unlimited sharing
"""
        )

    # =====================================
    # ADMIN
    # =====================================

    elif text == "Admin🧑‍💼":

        if update.effective_user.id != ADMIN_ID:

            return await update.message.reply_text(
                "❌ Admin only"
            )

        return await update.message.reply_text(
"""
🧑‍💼 ADMIN PANEL

• Statistics
• Broadcast
• Delete Media
• Users
"""
        )

    # =====================================
    # OPEN CODE
    # =====================================

    elif text.startswith(
        "kxfilebot_"
    ):

        return await open_code(
            update,
            context,
            text
        )

# =========================================
# RUN BOT
# =========================================

app = Application.builder().token(
    BOT_TOKEN
).build()

# START
app.add_handler(
    CommandHandler(
        "start",
        start
    )
)

# SAVE MEDIA
app.add_handler(
    MessageHandler(
        filters.PHOTO
        | filters.VIDEO
        | filters.Document.ALL
        | filters.AUDIO
        | filters.ANIMATION,
        save_media
    )
)

# CREATE CODE
app.add_handler(
    CallbackQueryHandler(
        create_code,
        pattern="create_code"
    )
)

# PAGE
app.add_handler(
    CallbackQueryHandler(
        page_callback,
        pattern="^page_"
    )
)

# CHECK JOIN
app.add_handler(
    CallbackQueryHandler(
        check_join,
        pattern="check_join"
    )
)

# TEXT
app.add_handler(
    MessageHandler(
        filters.TEXT
        & ~filters.COMMAND,
        text_handler
    )
)

print("KXBOT RUNNING...")

app.run_polling()
