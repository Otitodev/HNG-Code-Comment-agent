import os
import requests
from datetime import datetime
from app.services.telex_service import send_message_to_telex

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8080")
TELEX_CHANNEL = os.getenv("TELEX_CHANNEL")  # set this to where you want to post (channel id or user id)

def get_daily_tip():
    try:
        r = requests.get(f"{API_BASE_URL}/api/daily-tip", timeout=10)
        r.raise_for_status()
        return r.json().get("tip")
    except Exception as e:
        return f"Failed to fetch daily tip: {e}"

def main():
    tip = get_daily_tip()
    if not tip:
        tip = "No tip available today."
    msg = f"🧠 Daily Code Insight ({datetime.utcnow().strftime('%Y-%m-%d')}):\n\n{tip}"
    if TELEX_CHANNEL:
        try:
            send_message_to_telex(TELEX_CHANNEL, msg)
            print("Daily message posted to Telex.")
        except Exception as e:
            print("Failed to post to Telex:", e)
    else:
        print(msg)

if __name__ == "__main__":
    main()
