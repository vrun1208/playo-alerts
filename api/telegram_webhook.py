"""
Telegram Webhook Handler
Receives Telegram updates and processes /start, /stop, /status commands
"""

import os
import json
import logging
from telegram import Bot, Update
from telegram.ext import ContextTypes

from src.storage import add_user, remove_user, get_user_count

logger = logging.getLogger(__name__)
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(token=TOKEN)


async def handle_telegram_update(update_data):
    """Process incoming Telegram webhook update"""
    try:
        update = Update.de_json(update_data, bot)
        
        if not update.message:
            return
        
        chat_id = update.effective_chat.id
        text = update.message.text
        
        message = None
        
        if text == "/start":
            added = add_user(chat_id)
            if added:
                message = "🏸 Subscribed to badminton court alerts!"
            else:
                message = "✅ You are already subscribed."
        
        elif text == "/stop":
            removed = remove_user(chat_id)
            if removed:
                message = "❌ Unsubscribed from alerts."
            else:
                message = "You were not subscribed."
        
        elif text == "/status":
            count = get_user_count()
            message = f"📊 Total subscribers: {count}"
        
        if message:
            await bot.send_message(chat_id=chat_id, text=message)
    
    except Exception as e:
        logger.error(f"Error handling update: {e}")


def handler(request):
    """Vercel serverless handler for Telegram webhook"""
    
    # Handle POST requests (webhook)
    if request.method == "POST":
        try:
            update_data = request.json
            
            # Process asynchronously
            import asyncio
            asyncio.run(handle_telegram_update(update_data))
            
            return {
                "statusCode": 200,
                "body": json.dumps({"ok": True}),
            }
        
        except Exception as e:
            logger.error(f"Webhook error: {e}")
            return {
                "statusCode": 500,
                "body": json.dumps({"ok": False, "error": str(e)}),
            }
    
    # Handle GET (health check on webhook URL)
    return {
        "statusCode": 200,
        "body": json.dumps({"ok": True, "message": "Webhook active"}),
    }
