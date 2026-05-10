"""
PlayO API Client
Handles all PlayO API interactions
"""

import datetime
import requests

PLAYO_API_URL = "https://api.playo.io/activity-public/list/location"


def fetch_slots(lat, lng, radius, sport):
    """
    Fetch available slots from PlayO API
    
    Args:
        lat: Latitude
        lng: Longitude
        radius: Search radius in km
        sport: Sport ID (e.g., "SP5" for Badminton)
    
    Returns:
        List of activities
    """
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
