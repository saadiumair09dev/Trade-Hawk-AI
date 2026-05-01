import websocket
import json
import pandas as pd
from datetime import datetime

tick_buffer = []


def on_message(ws, message):
    data = json.loads(message)

    if "last_price" in data:
        tick = {
            "datetime": datetime.now(),
            "price": data["last_price"]
        }

        tick_buffer.append(tick)

        # buffer limit (memory safe)
        if len(tick_buffer) > 500:
            tick_buffer.pop(0)


def on_open(ws):
    print("✅ WebSocket Connected")


def start_ws():
    ws = websocket.WebSocketApp(
        "wss://api-feed.dhan.co",
        on_message=on_message
    )
    ws.run_forever()


def get_tick_df():
    if not tick_buffer:
        return None

    df = pd.DataFrame(tick_buffer)
    df.set_index("datetime", inplace=True)

    df.rename(columns={"price": "close"}, inplace=True)

    df["open"] = df["close"]
    df["high"] = df["close"]
    df["low"] = df["close"]
    df["volume"] = 0

    return df
