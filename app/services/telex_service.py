import os
import requests

TELEX_API_KEY = os.getenv("TELEX_AGENT_API_KEY")
TELEX_API_URL = "https://api.telex.im/v1/messages"  # placeholder; replace with exact if different

def send_message_to_telex(channel_id: str, text: str):
    if not TELEX_API_KEY:
        raise RuntimeError("TELEX_AGENT_API_KEY not set")
    headers = {"Authorization": f"Bearer {TELEX_API_KEY}", "Content-Type": "application/json"}
    payload = {"channel_id": channel_id, "text": text}
    resp = requests.post(TELEX_API_URL, json=payload, headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.json()
