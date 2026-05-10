# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "click",
#     "requests",
#     "pytz",
#     "rich",
#     "python-dateutil",
#     "python-telegram-bot",
#     "python-dotenv",
# ]
# ///

import os
import asyncio
from datetime import datetime, time as dt_time

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

# Import finder logic
from finder import fetch_slots, process_slots, send_slots_to_telegram

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


async def start(update, context):
    chat_id = update.effective_chat.id
    username = update.effective_user.username

    added = add_user(chat_id, username)

    if added:
        await update.message.reply_text(
            "🏸 Subscribed to badminton court alerts!\n\n"
            "You'll receive notifications at 11 AM and 1 PM IST daily."
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


async def check_slots_now(update, context):
    """Manual trigger to check slots immediately"""
    await update.message.reply_text("🔍 Checking for available slots...")
    
    try:
        # Fetch and process slots
        activities = fetch_slots(
            lat=12.9261,
            lng=77.6762,
            radius=5,
            sport="SP5"
        )
        
        slots = process_slots(
            activities=activities,
            timezone="Asia/Kolkata",
            start_time="19:00",
            end_time="01:00",
            verbose=False
        )
        
        if not slots:
            await update.message.reply_text(
                "No available slots found in the 7 PM - 1 AM window."
            )
            return
        
        # Send to this user only
        await send_slots_to_telegram(slots, TOKEN)
        
    except Exception as e:
        await update.message.reply_text(
            f"❌ Error checking slots: {str(e)}"
        )


async def scheduled_check(app):
    """Background task that runs on schedule"""
    print("📅 Scheduler started")
    
    # Schedule times in IST (11 AM and 1 PM)
    schedule_times = [
        dt_time(11, 0),  # 11:00 AM IST
        dt_time(13, 0),  # 1:00 PM IST
    ]
    
    while True:
        try:
            # Get current time in IST
            import pytz
            ist = pytz.timezone("Asia/Kolkata")
            now = datetime.now(ist)
            current_time = now.time().replace(second=0, microsecond=0)
            
            # Check if current time matches any schedule
            for scheduled_time in schedule_times:
                target_time = scheduled_time.replace(second=0, microsecond=0)
                
                if current_time == target_time:
                    print(f"⏰ Scheduled check triggered at {now.strftime('%I:%M %p IST')}")
                    
                    try:
                        # Fetch and process slots
                        activities = fetch_slots(
                            lat=12.9261,
                            lng=77.6762,
                            radius=5,
                            sport="SP5"
                        )
                        
                        slots = process_slots(
                            activities=activities,
                            timezone="Asia/Kolkata",
                            start_time="19:00",
                            end_time="01:00",
                            verbose=False
                        )
                        
                        if slots:
                            print(f"✅ Found {len(slots)} slots, sending alerts...")
                            await send_slots_to_telegram(slots, TOKEN)
                        else:
                            print("ℹ️  No slots found")
                    
                    except Exception as e:
                        print(f"❌ Error in scheduled check: {e}")
                    
                    # Sleep for 61 seconds to avoid triggering twice in same minute
                    await asyncio.sleep(61)
                    break
            
            # Check every 60 seconds
            await asyncio.sleep(60)
            
        except Exception as e:
            print(f"❌ Scheduler error: {e}")
            await asyncio.sleep(60)


async def post_init(app):
    """Start background scheduler after bot is initialized"""
    asyncio.create_task(scheduled_check(app))


def main():
    app = (
        ApplicationBuilder() 
        .token(TOKEN)
        .post_init(post_init)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("check", check_slots_now))

    print("🤖 Bot listener running...")
    print("📅 Scheduler: 11:00 AM & 1:00 PM IST daily")

    app.run_polling()


if __name__ == "__main__":
    main()
