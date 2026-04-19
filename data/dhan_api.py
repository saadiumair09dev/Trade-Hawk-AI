import requests
import pandas as pd
import streamlit as st
import yfinance as yf

BASE_URL = "https://api.dhan.co/v2/charts/intraday"


# ================= DHAN FETCH =================
def fetch_dhan(symbol, interval):
    try:
        # ===== SECRETS =====
        token = st.secrets["dhan"]["token"]
        client_id = st.secrets["dhan"]["client_id"]

        # ===== SYMBOL MAP =====
        symbol_map = {
            "^NSEI": {"securityId": "26000", "exchangeSegment": "NSE_INDEX"},
            "^BANKNIFTY": {"securityId": "26009", "exchangeSegment": "NSE_INDEX"},
        }

        if symbol not in symbol_map:
            return None

        # ===== INTERVAL MAP =====
        interval_map = {
            "1m": "1",
            "5m": "5",
            "15m": "15",
            "1h": "60"
        }

        dhan_interval = interval_map.get(interval, "5")

        # ===== PAYLOAD =====
        payload = {
            "securityId": symbol_map[symbol]["securityId"],
            "exchangeSegment": symbol_map[symbol]["exchangeSegment"],
            "instrument": "INDEX",
            "interval": dhan_interval
        }

        headers = {
            "access-token": token,
            "client-id": client_id,
            "Content-Type": "application/json"
        }

        # ===== API CALL =====
        res = requests.post(BASE_URL, json=payload, headers=headers, timeout=10)

        if res.status_code != 200:
            st.warning(f"⚠️ Dhan API Error: {res.status_code}")
            st.write(res.text)
            return None

        data = res.json()

        if "data" not in data:
            st.warning("⚠️ Invalid Dhan response")
            st.write(data)
            return None

        raw = data["data"]

        # ===== BUILD DATAFRAME =====
        df = pd.DataFrame({
            "datetime": raw["timestamp"],
            "open": raw["open"],
            "high": raw["high"],
            "low": raw["low"],
            "close": raw["close"],
            "volume": raw.get("volume", [0]*len(raw["close"]))
        })

        df["datetime"] = pd.to_datetime(df["datetime"])
        df.set_index("datetime", inplace=True)

        return df

    except Exception as e:
        st.error(f"❌ Dhan error: {e}")
        return None


# ================= YFINANCE FALLBACK =================
def fetch_yfinance(symbol, interval):
    try:
        df = yf.download(
            tickers=symbol,
            interval=interval,
            period="1d",
            progress=False
        )

        if df is None or df.empty:
            return None

        # ===== FIX MULTI-INDEX =====
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0].lower() for col in df.columns]
        else:
            df.columns = [str(col).lower() for col in df.columns]

        return df

    except Exception as e:
        st.warning(f"⚠️ YFinance error: {e}")
        return None


# ================= MAIN FUNCTION =================
def get_data(symbol, interval):
    # 1️⃣ Try Dhan
    df = fetch_dhan(symbol, interval)

    if df is not None and not df.empty:
        st.success("⚡ Data from Dhan API")
        return df

    # 2️⃣ Fallback
    df = fetch_yfinance(symbol, interval)

    if df is not None and not df.empty:
        st.warning("⚠️ Using fallback (yfinance)")
        return df

    return None
