import requests
import pandas as pd

# ===== CONFIG =====
BASE_URL = "https://api.dhan.co/v2/charts/intraday"

token = "PASTE_YOUR_TOKEN_HERE"
client_id = "1106554867"

HEADERS = {
    "access-token": token,
    "client-id": client_id,
    "Content-Type": "application/json"
}

# ===== SYMBOL MAPPING =====
SYMBOL_MAP = {
    "^NSEI": {
        "securityId": "13",        # NIFTY 50
        "exchangeSegment": "IDX_I"
    },
    "^NSEBANK": {
        "securityId": "25",        # BANKNIFTY
        "exchangeSegment": "IDX_I"
    }
}

# ===== MAIN FUNCTION =====
def get_data(symbol, interval):
    try:
        if symbol not in SYMBOL_MAP:
            raise Exception("Symbol not supported for Dhan")

        mapping = SYMBOL_MAP[symbol]

        payload = {
            "securityId": mapping["securityId"],
            "exchangeSegment": mapping["exchangeSegment"],
            "instrument": "INDEX",
            "interval": interval,
            "fromDate": "2024-04-01",
            "toDate": "2026-04-20"
        }

        res = requests.post(BASE_URL, json=payload, headers=HEADERS)

        if res.status_code != 200:
            raise Exception(res.text)

        data = res.json()

        df = pd.DataFrame(data["data"])

        df["datetime"] = pd.to_datetime(df["datetime"])
        df.set_index("datetime", inplace=True)

        df.rename(columns={
            "open": "Open",
            "high": "High",
            "low": "Low",
            "close": "Close"
        }, inplace=True)

        return df

    except Exception as e:
        print("Dhan Error:", e)
        return None
