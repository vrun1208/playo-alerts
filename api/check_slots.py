"""
Check Slots Cron Job
Runs every 15 minutes to fetch and send badminton alerts
"""

import os
import json
import asyncio
from telegram import Bot
from telegram.constants import ParseMode

from src.finder import find_matching_slots, build_booking_link
from src.playo_client import fetch_slots
from src.storage import load_users, save_message_id, get_message_id


async def send_alerts(slots, token):
    """Send alerts to all subscribed users"""
    users = load_users()["users"]
    bot = Bot(token=token)
    
    users_notified = 0
    
    for user in users:
        chat_id = str(user["chat_id"])
        
        try:
            # Delete old message
            old_msg_id = get_message_id(int(chat_id))
            if old_msg_id:
                try:
                    await bot.delete_message(chat_id=int(chat_id), message_id=old_msg_id)
                except:
                    pass
            
            # Build message
            message_lines = [
                f"🏸 <b>{len(slots)} Courts Available Near Bellandur</b>",
                "",
            ]
            
            for idx, slot in enumerate(slots, start=1):
                message_lines.append(
                    f"<b>{idx}. {slot['venue_name']}</b>\n"
                    f"🕒 {slot['start']} – {slot['end']}\n"
                    f"⏱ {slot['duration']}\n"
                    f"💰 {slot['price']}\n"
                    f"🔗 {slot['link']}\n"
                )
            
            final_message = "\n".join(message_lines)
            
            # Send new message
            sent = await bot.send_message(
                chat_id=int(chat_id),
                text=final_message,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )
            
            # Save message ID
            save_message_id(int(chat_id), sent.message_id)
            users_notified += 1
        
        except Exception as e:
            print(f"Error notifying {chat_id}: {e}")
    
    return users_notified


def handler(request):
    """Vercel cron handler - runs every 15 minutes"""
    
    try:
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        
        # Fetch slots from PlayO API
        activities = fetch_slots(
            lat=12.9784,
            lng=77.6408,
            radius=7,
            sport="SP5"
        )
        
        # Process and filter
        matching_slots = find_matching_slots(
            activities,
            timezone="Asia/Kolkata",
            start_time="19:00",
            end_time="01:00"
        )
        
        slots_found = len(matching_slots)
        users_notified = 0
        
        if matching_slots:
            # Send alerts
            users_notified = asyncio.run(send_alerts(matching_slots, token))
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "success": True,
                "users_notified": users_notified,
                "slots_found": slots_found,
            }),
        }
    
    except Exception as e:
        print(f"Cron error: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "success": False,
                "error": str(e),
            }),
        }
