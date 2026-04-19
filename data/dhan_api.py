import pandas as pd
import yfinance as yf
import requests
import streamlit as st


# ================= DHAN FUNCTION =================
def fetch_dhan(symbol, interval):
    try:
        token = st.secrets.get("dhan", {}).get("token", None)

        if not token:
            return None

        url = "https://api.dhan.co/v2/charts/intraday"

        payload = {
            "securityId": "13",
            "exchangeSegment": "IDX_I",
            "instrument": "INDEX",
            "interval": interval.replace("m", ""),
            "fromDate": "2024-01-01",
            "toDate": "2024-12-31"
        }

        headers = {
            "access-token": token,
            "Content-Type": "application/json"
        }

        res = requests.post(url, json=payload, headers=headers)

        if res.status_code != 200:
            return None

        data = res.json()

        if "data" not in data:
            return None

        df = pd.DataFrame(data["data"])

        df.rename(columns={
            "open": "Open",
            "high": "High",
            "low": "Low",
            "close": "Close",
            "volume": "Volume"
        }, inplace=True)

        return df

    except Exception as e:
        print("Dhan Error:", e)
        return None


# ================= YFINANCE FALLBACK =================
def fetch_yf(symbol, interval):
    try:
        df = yf.download(
            symbol,
            period="1d",
            interval=interval,
            progress=False
        )

        if df is None or df.empty:
            return None

        df = df.reset_index()
        return df

    except Exception as e:
        print("YF Error:", e)
        return None


# ================= MAIN GET DATA =================
def get_data(symbol, interval):

    # 1️⃣ Try Dhan
    df = fetch_dhan(symbol, interval)

    if df is not None and not df.empty:
        return df

    # 2️⃣ Fallback
    df = fetch_yf(symbol, interval)

    return df
