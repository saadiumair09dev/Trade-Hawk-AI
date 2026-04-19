import streamlit as st
import pandas as pd
import requests
import yfinance as yf

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Trade Hawk AI", layout="wide")
st.title("📈 Trade Hawk AI")

# =========================
# INPUTS
# =========================
symbol = st.selectbox("Select Index", ["^NSEI", "^BANKNIFTY"])
interval = st.selectbox("Timeframe", ["5m", "15m", "1h"])

# =========================
# DHAN DATA FUNCTION
# =========================
def get_dhan_data(symbol, interval):
    try:
        token = st.secrets["dhan"]["token"]
        client_id = st.secrets["dhan"]["client_id"]

        mapping = {
            "^NSEI": {"securityId": "26000", "exchangeSegment": "NSE_INDEX"},
            "^BANKNIFTY": {"securityId": "26009", "exchangeSegment": "NSE_INDEX"},
        }

        if symbol not in mapping:
            return None

        # interval fix for dhan
        interval_map = {
            "5m": "5",
            "15m": "15",
            "1h": "60"
        }

        url = "https://api.dhan.co/v2/charts/intraday"

        payload = {
            "securityId": mapping[symbol]["securityId"],
            "exchangeSegment": mapping[symbol]["exchangeSegment"],
            "instrument": "INDEX",
            "interval": interval_map.get(interval, "5")
        }

        headers = {
            "access-token": token,
            "client-id": client_id,
            "Content-Type": "application/json"
        }

        res = requests.post(url, json=payload, headers=headers)

        if res.status_code != 200:
            st.error(f"❌ Dhan API Error: {res.status_code}")
            st.write(res.text)
            return None

        data = res.json()

        if "data" not in data:
            st.error("❌ Invalid Dhan response")
            return None

        df = pd.DataFrame({
            "datetime": data["data"]["timestamp"],
            "open": data["data"]["open"],
            "high": data["data"]["high"],
            "low": data["data"]["low"],
            "close": data["data"]["close"],
        })

        df["datetime"] = pd.to_datetime(df["datetime"])
        df.set_index("datetime", inplace=True)

        return df

    except Exception as e:
        st.error(f"❌ Dhan fetch error: {e}")
        return None


# =========================
# YFINANCE FALLBACK
# =========================
def get_yf_data(symbol, interval):
    try:
        df = yf.download(
            tickers=symbol,
            interval=interval,
            period="1d",
            progress=False
        )

        if df is None or df.empty:
            return None

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0].lower() for col in df.columns]
        else:
            df.columns = [str(col).lower() for col in df.columns]

        return df

    except Exception as e:
        st.error(f"YFinance error: {e}")
        return None


# =========================
# MAIN DATA FLOW
# =========================
df = get_dhan_data(symbol, interval)

if df is not None and not df.empty:
    st.success("⚡ Using Dhan (Fast Data)")
else:
    st.warning("⚠️ Using fallback (yfinance)")
    df = get_yf_data(symbol, interval)

# =========================
# CHECK DATA
# =========================
if df is None or df.empty:
    st.error("❌ Data fetch failed")
    st.stop()

st.success("✅ Data Loaded")

# =========================
# INDICATORS
# =========================
try:
    if "close" not in df.columns:
        st.error("❌ 'close' column missing")
        st.stop()

    df["ema_9"] = df["close"].ewm(span=9).mean()
    df["ema_21"] = df["close"].ewm(span=21).mean()

except Exception as e:
    st.error(f"❌ Indicator calculation failed: {e}")
    st.stop()

# =========================
# SIGNAL LOGIC
# =========================
try:
    last = df.iloc[-1]

    signal = "NEUTRAL"

    if last["ema_9"] > last["ema_21"]:
        signal = "BUY"
    elif last["ema_9"] < last["ema_21"]:
        signal = "SELL"

    st.subheader(f"📊 Signal: {signal}")

except Exception as e:
    st.error(f"❌ Signal error: {e}")

# =========================
# DISPLAY DATA
# =========================
st.dataframe(df.tail(10))
