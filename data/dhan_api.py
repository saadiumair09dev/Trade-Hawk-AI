import requests
import pandas as pd
import streamlit as st
import yfinance as yf

BASE_URL = "https://api.dhan.co/v2/charts/intraday"

# ================= GET DATA =================
def get_data(security_id):
    try:
        # ================= SECRETS =================
        token = st.secrets.get("dhan", {}).get("token", "")
        client_id = st.secrets.get("dhan", {}).get("client_id", "")

        # अगर token नहीं है → fallback
        if token == "" or client_id == "":
            st.warning("⚠️ Using fallback data (No Dhan API)")
            return get_yfinance_data(security_id)

        # ================= PAYLOAD =================
        payload = {
            "securityId": security_id,
            "exchangeSegment": "IDX_I",
            "interval": "1"
        }

        headers = {
            "access-token": token,
            "client-id": client_id,
            "Content-Type": "application/json"
        }

        # ================= API CALL =================
        res = requests.post(BASE_URL, json=payload, headers=headers, timeout=10)

        # DEBUG
        st.write("Status:", res.status_code)

        if res.status_code != 200:
            st.error(f"Dhan API Error: {res.text}")
            return get_yfinance_data(security_id)

        data = res.json()

        # ================= DATA FORMAT =================
        if "data" in data:
            raw = data["data"]
        elif "candles" in data:
            raw = data["candles"]
        else:
            st.error("Unexpected API format")
            return get_yfinance_data(security_id)

        df = pd.DataFrame(raw)

        df.rename(columns={
            "open": "Open",
            "high": "High",
            "low": "Low",
            "close": "Close",
            "volume": "Volume"
        }, inplace=True)

        if df.empty or "Close" not in df.columns:
            return get_yfinance_data(security_id)

        return df

    except Exception as e:
        st.error(f"API Crash: {e}")
        return get_yfinance_data(security_id)


# ================= FALLBACK =================
def get_yfinance_data(security_id):
    try:
        # mapping
        symbol_map = {
            "13": "^NSEI",        # NIFTY
            "25": "^NSEBANK"     # BANKNIFTY
        }

        symbol = symbol_map.get(security_id, "^NSEI")

        df = yf.download(symbol, interval="5m", period="1d")

        if df is None or df.empty:
            return None

        df.reset_index(inplace=True)
        df.rename(columns={
            "Open": "Open",
            "High": "High",
            "Low": "Low",
            "Close": "Close",
            "Volume": "Volume"
        }, inplace=True)

        return df

    except Exception as e:
        st.error(f"Fallback error: {e}")
        return None
