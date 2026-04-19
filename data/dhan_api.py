import requests
import pandas as pd
import streamlit as st

BASE_URL = "https://api.dhan.co/v2/charts/intraday"

def get_data(security_id, interval="5"):
    try:
        token = st.secrets["dhan"]["token"]
        client_id = st.secrets["dhan"]["client_id"]

        headers = {
            "access-token": token,
            "client-id": client_id,
            "Content-Type": "application/json"
        }

        payload = {
            "securityId": security_id,
            "exchangeSegment": "IDX_I",
            "interval": interval
        }

        # ✅ FIXED LINE
        res = requests.post(BASE_URL, json=payload, headers=headers, timeout=10)

        if res.status_code != 200:
            st.warning(f"Dhan API Error: {res.status_code}")
            return None

        data = res.json()

        if "data" in data:
            raw = data["data"]
        elif "candles" in data:
            raw = data["candles"]
        else:
            st.warning("Unexpected response format")
            return None

        df = pd.DataFrame(raw)

        df.rename(columns={
            "open": "Open",
            "high": "High",
            "low": "Low",
            "close": "Close",
            "volume": "Volume"
        }, inplace=True)

        if "Close" not in df.columns:
            return None

        return df.dropna()

    except Exception as e:
        st.error(f"Dhan API Crash: {e}")
        return None
