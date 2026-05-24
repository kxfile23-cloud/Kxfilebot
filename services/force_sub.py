from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from config import UPDATE_CHANNEL


async def force_sub(bot, user_id):

    try:

        member = await bot.get_chat_member(
            chat_id=UPDATE_CHANNEL,
            user_id=user_id
        )

        if member.status in [
            "member",
            "administrator",
            "creator"
        ]:
            return True

        return False

    except:
        return False


def join_keyboard():

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "📢 JOIN CHANNEL",
                url="https://t.me/selaputmuda"
            )
        ]
    ])
