import requests
import pandas as pd
import streamlit as st
import yfinance as yf
from datetime import datetime
import pytz

BASE_URL = "https://api.dhan.co/v2/charts/intraday"

# ================= MARKET TIME CHECK =================
def is_market_open():
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)

    # Weekday check (Mon-Fri)
    if now.weekday() >= 5:
        return False

    # Time check (9:15 to 15:30)
    market_start = now.replace(hour=9, minute=15, second=0)
    market_end = now.replace(hour=15, minute=30, second=0)

    return market_start <= now <= market_end


# ================= DHAN FETCH =================
def fetch_dhan(symbol, interval):
    try:
        token = st.secrets["dhan"]["token"]

        symbol_map = {
            "RELIANCE": {"securityId": "1333", "exchangeSegment": "NSE_EQ"},
            "HDFCBANK": {"securityId": "1330", "exchangeSegment": "NSE_EQ"},
        }

        if symbol not in symbol_map:
            return None

        interval_map = {
            "1m": "1",
            "5m": "5",
            "15m": "15",
            "1h": "60"
        }

        payload = {
            "securityId": symbol_map[symbol]["securityId"],
            "exchangeSegment": symbol_map[symbol]["exchangeSegment"],
            "instrument": "EQUITY",
            "interval": interval_map.get(interval, "5")
        }

        headers = {
            "access-token": token,
            "Content-Type": "application/json"
        }

        res = requests.post(BASE_URL, json=payload, headers=headers, timeout=10)

        if res.status_code != 200:
            return None

        data = res.json()
        if "data" not in data:
            return None

        raw = data["data"]

        df = pd.DataFrame({
            "datetime": raw.get("timestamp", []),
            "open": raw.get("open", []),
            "high": raw.get("high", []),
            "low": raw.get("low", []),
            "close": raw.get("close", []),
            "volume": raw.get("volume", [0]*len(raw.get("close", [])))
        })

        if df.empty:
            return None

        df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
        df.dropna(inplace=True)
        df.set_index("datetime", inplace=True)

        return df

    except:
        return None


# ================= YFINANCE FETCH =================
def fetch_yfinance(symbol, interval):
    try:
        market_open = is_market_open()

        # 🔥 SMART SWITCH
        if market_open:
            period = "1d"
        else:
            period = "5d"   # night safe

        df = yf.download(
            tickers=symbol,
            interval=interval,
            period=period,
            progress=False
        )

        if df is None or df.empty:
            return None

        # Fix columns
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0].lower() for col in df.columns]
        else:
            df.columns = [str(col).lower() for col in df.columns]

        df.dropna(inplace=True)

        return df

    except:
        return None


# ================= MAIN =================
def get_data(symbol, interval):

    market_open = is_market_open()

    # 🔥 STATUS SHOW
    if market_open:
        st.success("🟢 Market Open Mode (Live Data)")
    else:
        st.warning("🌙 Market Closed Mode (Auto Adjusted Data)")

    df = None

    # Dhan only for stocks
    if not symbol.startswith("^") and market_open:
        df = fetch_dhan(symbol, interval)

        if df is not None and not df.empty:
            st.success("⚡ Data from Dhan API")
            return df

    # Fallback always works
    df = fetch_yfinance(symbol, interval)

    if df is not None and not df.empty:
        st.info("📊 Data from yfinance")
        return df

    st.error("❌ Data fetch failed")
    return None
