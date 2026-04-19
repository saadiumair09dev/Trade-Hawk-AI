import requests
import pandas as pd

# ===== CONFIG =====
BASE_URL = "https://api.dhan.co/v2/charts/intraday"

TOKEN = "PASTE_YOUR_TOKEN_HERE"
CLIENT_ID = "1106554867"

HEADERS = {
    "access-token": TOKEN,
    "Content-Type": "application/json"
}

# ===== SYMBOL MAP =====
SYMBOL_MAP = {
    "^NSEI": "13",       # NIFTY
    "^NSEBANK": "25"     # BANKNIFTY
}

# ===== INTERVAL MAP =====
INTERVAL_MAP = {
    "1m": "1",
    "5m": "5",
    "15m": "15"
}

# ===== MAIN FUNCTION =====
def get_data(symbol, interval):
    try:
        security_id = SYMBOL_MAP.get(symbol)
        interval_val = INTERVAL_MAP.get(interval, "5")

        if not security_id:
            raise Exception("Unsupported symbol")

        payload = {
            "securityId": security_id,
            "exchangeSegment": "IDX_I",
            "instrument": "INDEX",
            "interval": interval_val
        }

        response = requests.post(BASE_URL, json=payload, headers=HEADERS)

        if response.status_code != 200:
            raise Exception(response.text)

        data = response.json()

        # 👇 Important: correct key
        candles = data.get("data", [])

        if not candles:
            raise Exception("No data returned")

        df = pd.DataFrame(candles)

        # rename columns
        df.columns = ["datetime", "open", "high", "low", "close", "volume"]

        df["datetime"] = pd.to_datetime(df["datetime"])
        df.set_index("datetime", inplace=True)

        return df

    except Exception as e:
        print("Dhan Error:", e)
        return None
