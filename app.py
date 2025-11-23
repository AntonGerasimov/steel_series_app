import json
import requests
from pathlib import Path

# ---- CONFIG ----
GAME_NAME = "MYAPP"
EVENT_NAME = "MYSCREEN"

# Adjust this to your OS:
# Windows:
core_props_path = Path(r"C:\ProgramData\SteelSeries\SteelSeries Engine 3\coreProps.json")
# macOS (uncomment if on mac):
# core_props_path = Path("/Library/Application Support/SteelSeries Engine 3/coreProps.json")

# ---- DISCOVER LOCAL API ----
core_config = json.loads(core_props_path.read_text(encoding="utf-8"))
address = core_config["address"]          # e.g. "127.0.0.1:12345"
base_url = f"http://{address}"

URL_REMOVE_GAME   = f"{base_url}/remove_game"
URL_GAME_METADATA = f"{base_url}/game_metadata"
URL_BIND_EVENT    = f"{base_url}/bind_game_event"
URL_GAME_EVENT    = f"{base_url}/game_event"
URL_HEARTBEAT     = f"{base_url}/game_heartbeat"

headers = {"Content-Type": "application/json"}

# ---- 1. REGISTER GAME ----
def register_game():
    # clean up if it already exists
    requests.post(URL_REMOVE_GAME, json={"game": GAME_NAME})
    payload = {
        "game": GAME_NAME,
        "game_display_name": GAME_NAME,
        "developer": "Me",
        "deinitialize_timer_length_ms": 60000,
    }
    r = requests.post(URL_GAME_METADATA, json=payload, headers=headers)
    print("register_game:", r.text)

# ---- 2. BIND SCREEN EVENT (OLED HANDLER) ----
def bind_screen_event():
    payload = {
        "game": GAME_NAME,
        "event": EVENT_NAME,
        "icon_id": 4,
        "handlers": [
            {
                "device-type": "screened-128x40",  # Apex 7 / GameDAC
                "zone": "one",
                "mode": "screen",
                "datas": [
                    {
                        "lines": [
                            {"has-text": True, "context-frame-key": "line1"},
                            {"has-text": True, "context-frame-key": "line2"},
                        ]
                    }
                ],
            }
        ],
    }
    r = requests.post(URL_BIND_EVENT, json=payload, headers=headers)
    print("bind_screen_event:", r.text)

# ---- 3. SEND TEXT TO THE OLED ----
counter = 0

def send_screen_text(line1: str, line2: str):
    global counter
    payload = {
        "game": GAME_NAME,
        "event": EVENT_NAME,
        "device-type": "screened-128x40",
        "zone": "one",
        "mode": "screen",
        "data": {
            "value": counter,          # can be anything, just has to change sometimes
            "frame": {
                "line1": line1,
                "line2": line2,
            },
        },
    }
    counter += 1
    r = requests.post(URL_GAME_EVENT, json=payload, headers=headers)
    print("send_screen_text:", r.text)

def heartbeat():
    r = requests.post(URL_HEARTBEAT, json={"game": GAME_NAME}, headers=headers)
    print("heartbeat:", r.text)

if __name__ == "__main__":
    register_game()
    bind_screen_event()
    send_screen_text("Hello, Denis", "from Python :)")
    # optionally keep app "alive":
    heartbeat()