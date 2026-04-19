import requests
import pandas as pd
import streamlit as st
import yfinance as yf

BASE_URL = "https://api.dhan.co/v2/charts/intraday"


# ================= DHAN FETCH =================
def fetch_dhan(symbol, interval):
    try:
        # ===== READ TOKEN =====
        dhan_secrets = st.secrets.get("dhan", {})
        token = dhan_secrets.get("token", None)

        if not token:
            st.warning("⚠️ No Dhan token found → using fallback")
            return None

        # ===== SYMBOL MAP =====
        if symbol == "^NSEI":
            security_id = "13"   # NIFTY
        elif symbol == "^NSEBANK":
            security_id = "25"  # BANKNIFTY
        else:
            security_id = "13"

        # ===== INTERVAL MAP =====
        interval_map = {
            "1m": "1",
            "5m": "5",
            "15m": "15"
        }

        dhan_interval = interval_map.get(interval, "5")

        # ===== PAYLOAD =====
        payload = {
            "securityId": security_id,
            "exchangeSegment": "IDX_I",
            "interval": dhan_interval
        }

        headers = {
            "access-token": token,
            "Content-Type": "application/json"
        }

        # ===== API CALL =====
        res = requests.post(BASE_URL, json=payload, headers=headers, timeout=10)

        # ===== DEBUG =====
        if res.status_code != 200:
            st.error(f"❌ Dhan API Error: {res.status_code}")
            st.write(res.text)
            return None

        data = res.json()

        # ===== DATA PARSE =====
        if "data" in data:
            raw = data["data"]
        elif "candles" in data:
            raw = data["candles"]
        else:
            st.error("❌ Unexpected response format from Dhan")
            st.write(data)
            return None

        df = pd.DataFrame(raw)

        if df.empty:
            st.warning("⚠️ Empty data from Dhan")
            return None

        # ===== NORMALIZE COLUMNS =====
        df.columns = [c.lower() for c in df.columns]

        # Ensure required columns
        required = ["open", "high", "low", "close"]
        for col in required:
            if col not in df.columns:
                st.error(f"❌ Missing column: {col}")
                return None

        return df

    except Exception as e:
        st.error(f"❌ Dhan fetch error: {e}")
        return None


# ================= YFINANCE FALLBACK =================
def fetch_yfinance(symbol, interval):
    try:
        df = yf.download(
            symbol,
            interval=interval,
            period="1d",
            progress=False
        )

        if df is None or df.empty:
            return None

        df.reset_index(inplace=True)

        df.rename(columns={
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume"
        }, inplace=True)

        df.columns = [c.lower() for c in df.columns]

        return df

    except Exception as e:
        st.error(f"❌ YFinance error: {e}")
        return None


# ================= MAIN FUNCTION =================
def get_data(symbol, interval):
    # 1️⃣ Try Dhan
    df = fetch_dhan(symbol, interval)

    if df is not None and not df.empty:
        st.success("✅ Data from Dhan API")
        return df

    # 2️⃣ Fallback
    df = fetch_yfinance(symbol, interval)

    if df is not None:
        st.warning("⚠️ Using fallback data")
        return df

    return None
