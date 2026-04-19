import requests
import pandas as pd
import streamlit as st
import yfinance as yf

BASE_URL = "https://api.dhan.co/v2/charts/intraday"

# ================= DHAN FETCH (ONLY STOCKS) =================
def fetch_dhan(symbol, interval):
    try:
        token = st.secrets["dhan"]["token"]

        # 👉 ONLY STOCKS (example mapping)
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
            st.warning(f"⚠️ Dhan API Error: {res.status_code}")
            return None

        data = res.json()

        if "data" not in data or not data["data"]:
            return None

        raw = data["data"]

        # 🔥 SAFE PARSE
        if isinstance(raw, dict):
            df = pd.DataFrame({
                "datetime": raw.get("timestamp", []),
                "open": raw.get("open", []),
                "high": raw.get("high", []),
                "low": raw.get("low", []),
                "close": raw.get("close", []),
                "volume": raw.get("volume", [0]*len(raw.get("close", [])))
            })
        else:
            return None

        if df.empty:
            return None

        df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
        df.dropna(inplace=True)
        df.set_index("datetime", inplace=True)

        return df

    except Exception as e:
        st.warning(f"⚠️ Dhan error: {e}")
        return None


# ================= YFINANCE FETCH (INDEX + FALLBACK) =================
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

        # 🔥 FIX MULTI INDEX
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0].lower() for col in df.columns]
        else:
            df.columns = [str(col).lower() for col in df.columns]

        df.dropna(inplace=True)

        return df

    except Exception as e:
        st.warning(f"⚠️ YFinance error: {e}")
        return None


# ================= MAIN FUNCTION =================
def get_data(symbol, interval):

    df = None

    # ✅ Dhan only for stocks
    if not symbol.startswith("^"):
        df = fetch_dhan(symbol, interval)

    if df is not None and not df.empty:
        st.success("⚡ Data from Dhan API")
        return df

    # ✅ Fallback (Index + backup)
    df = fetch_yfinance(symbol, interval)

    if df is not None and not df.empty:
        st.warning("⚠️ Using fallback (yfinance)")
        return df

    st.error("❌ Data fetch failed")
    return None
