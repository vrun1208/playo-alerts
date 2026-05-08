# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "python-dotenv",
#     "python-telegram-bot",
# ]
# ///

import os

from dotenv import load_dotenv
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
)

from storage import (
    add_user,
    remove_user,
    load_users,
)

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


async def start(update, context):
    chat_id = update.effective_chat.id
    username = update.effective_user.username

    added = add_user(chat_id, username)

    if added:
        await update.message.reply_text(
            "🏸 Subscribed to badminton court alerts!"
        )
    else:
        await update.message.reply_text(
            "✅ You are already subscribed."
        )


async def stop(update, context):
    chat_id = update.effective_chat.id

    removed = remove_user(chat_id)

    if removed:
        await update.message.reply_text(
            "❌ Unsubscribed from alerts."
        )
    else:
        await update.message.reply_text(
            "You were not subscribed."
        )


async def status(update, context):
    users = load_users()["users"]

    await update.message.reply_text(
        f"🏸 Active subscribers: {len(users)}"
    )


def main():
    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("status", status))

    print("Bot listener running...")

    app.run_polling()


if __name__ == "__main__":
    main()