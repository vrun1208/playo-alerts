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

import asyncio
import datetime
import json

import click
import pytz
import requests
from dateutil import parser
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from telegram import Bot
from telegram.constants import ParseMode

from storage import (
    load_users,
    load_messages,
    save_messages,
)

load_dotenv()

console = Console()

PLAYO_API_URL = "https://api.playo.io/activity-public/list/location"


# --------------------------------------------------
# Utilities
# --------------------------------------------------

def is_in_time_window(game_start_local, start_time_str, end_time_str):
    desired_start = datetime.datetime.strptime(
        start_time_str,
        "%H:%M"
    ).time()

    desired_end = datetime.datetime.strptime(
        end_time_str,
        "%H:%M"
    ).time()

    current_time = game_start_local.time().replace(
        second=0,
        microsecond=0
    )

    # Normal range
    if desired_start <= desired_end:
        return desired_start <= current_time <= desired_end

    # Midnight crossing
    return (
        current_time >= desired_start
        or current_time <= desired_end
    )


def build_booking_link(venue_id):
    if not venue_id:
        return "https://playo.co"

    return f"https://playo.co/booking?venueId={venue_id}"


def format_price(activity):
    price_val = activity.get("price") or 0
    return f"Rs.{price_val}" if price_val else "See venue"


# --------------------------------------------------
# PlayO API
# --------------------------------------------------

def fetch_slots(lat, lng, radius, sport):
    payload = {
        "lat": lat,
        "lng": lng,
        "cityRadius": radius,
        "gameTimeActivities": False,
        "page": 0,
        "lastId": "",
        "sportId": [sport],
        "booking": True,
        "date": [
            datetime.datetime.utcnow().strftime(
                "%Y-%m-%dT%H:%M:%S.%fZ"
            )
        ],
    }

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
    }

    response = requests.post(
        PLAYO_API_URL,
        headers=headers,
        json=payload,
        timeout=20,
    )

    response.raise_for_status()

    data = response.json()

    if data.get("requestStatus") != 1:
        raise Exception("Invalid PlayO response")

    return data["data"].get("activities", [])


# --------------------------------------------------
# Slot Processing
# --------------------------------------------------

def process_slots(
    activities,
    timezone,
    start_time,
    end_time,
    verbose=False,
):
    local_tz = pytz.timezone(timezone)

    matching_slots = []

    for activity in activities:
        start_utc = parser.parse(activity["startTime"])
        end_utc = parser.parse(activity["endTime"])

        start_local = start_utc.astimezone(local_tz)
        end_local = end_utc.astimezone(local_tz)

        duration_minutes = int(
            (end_utc - start_utc).total_seconds() / 60
        )

        in_window = is_in_time_window(
            start_local,
            start_time,
            end_time,
        )

        if verbose:
            print_verbose_slot(
                activity,
                start_local,
                duration_minutes,
                in_window,
            )

        if not in_window:
            continue

        venue_name = (
            activity.get("venueName")
            or activity.get("location")
            or "Unknown venue"
        )

        venue_id = activity.get("venueId", "")

        matching_slots.append({
            "id": activity["id"],
            "venue_name": venue_name,
            "start": start_local.strftime("%I:%M %p"),
            "end": end_local.strftime("%I:%M %p"),
            "duration": f"{duration_minutes}m",
            "price": format_price(activity),
            "link": build_booking_link(venue_id),
        })

    return matching_slots


def print_verbose_slot(
    activity,
    start_local,
    duration_minutes,
    in_window,
):
    in_str = (
        "[green]yes[/green]"
        if in_window
        else "[dim]no[/dim]"
    )

    console.print(
        f"[dim]{activity.get('location', 'Unknown'):50s}[/dim]  "
        f"Start: [bold]{start_local.strftime('%H:%M')}[/bold]  "
        f"Duration: {duration_minutes}m  "
        f"In window: {in_str}"
    )


# --------------------------------------------------
# CLI Table
# --------------------------------------------------

def print_slots_table(slots):
    table = Table(
        title=f"Bookable Badminton Courts ({len(slots)} slots)",
        show_lines=True,
    )

    table.add_column("Venue", style="cyan", min_width=28)
    table.add_column("Time", style="green", min_width=20)
    table.add_column("Duration", style="yellow")
    table.add_column("Price", style="white")
    table.add_column("Booking Link", style="bright_blue")

    for slot in slots:
        table.add_row(
            slot["venue_name"],
            f"{slot['start']} – {slot['end']}",
            slot["duration"],
            slot["price"],
            slot["link"],
        )

    console.print(table)


# --------------------------------------------------
# Telegram
# --------------------------------------------------

async def send_slots_to_telegram(slots, token):
    users = load_users()["users"]

    if not users:
        console.print(
            "[yellow]No subscribed users found[/yellow]"
        )
        return

    bot = Bot(token=token)

    messages_store = load_messages()

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

    for user in users:
        chat_id = str(user["chat_id"])

        # ----------------------------------------
        # Delete old alert message
        # ----------------------------------------

        old_message_id = messages_store.get(chat_id)

        if old_message_id:
            try:
                await bot.delete_message(
                    chat_id=chat_id,
                    message_id=old_message_id,
                )

                console.print(
                    f"[dim]Deleted old alert for {chat_id}[/dim]"
                )

            except Exception:
                pass

        # ----------------------------------------
        # Send new alert
        # ----------------------------------------

        try:
            sent_message = await bot.send_message(
                chat_id=chat_id,
                text=final_message,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )

            # Save latest message ID
            messages_store[chat_id] = sent_message.message_id

            console.print(
                f"[green]Alert sent to {chat_id}[/green]"
            )

        except Exception as e:
            console.print(
                f"[red]Failed for {chat_id}:[/red] {e}"
            )

    # Persist latest message IDs
    save_messages(messages_store)


# --------------------------------------------------
# Main CLI
# --------------------------------------------------

@click.command()
@click.option("--lat", default=12.9261)
@click.option("--lng", default=77.6762)
@click.option("--radius", default=5)
@click.option("--sport", default="SP5")
@click.option("--start-time", default="19:00")
@click.option("--end-time", default="01:00")
@click.option("--timezone", default="Asia/Kolkata")
@click.option("--verbose", is_flag=True)
@click.option("--telegram", is_flag=True)
@click.option(
    "--telegram-token",
    envvar="TELEGRAM_BOT_TOKEN"
)
def find_games(
    lat,
    lng,
    radius,
    sport,
    start_time,
    end_time,
    timezone,
    verbose,
    telegram,
    telegram_token,
):
    console.print(
        "[bold green]Searching badminton courts...[/bold green]"
    )

    try:
        activities = fetch_slots(
            lat,
            lng,
            radius,
            sport,
        )

        console.print(
            f"[green]{len(activities)} slots fetched[/green]"
        )

        matching_slots = process_slots(
            activities,
            timezone,
            start_time,
            end_time,
            verbose,
        )

        if not matching_slots:
            console.print(
                "[yellow]No matching slots found[/yellow]"
            )
            return

        print_slots_table(matching_slots)

        if telegram:
            if not telegram_token:
                console.print(
                    "[red]Telegram token missing[/red]"
                )
                return

            asyncio.run(
                send_slots_to_telegram(
                    matching_slots,
                    telegram_token,
                )
            )

            console.print(
                "[green]Telegram alerts sent[/green]"
            )

    except requests.RequestException as e:
        console.print(f"[red]API error:[/red] {e}")

    except json.JSONDecodeError:
        console.print("[red]Invalid JSON response[/red]")

    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}")


if __name__ == "__main__":
    find_games()