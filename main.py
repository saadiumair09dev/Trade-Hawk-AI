import streamlit as st
import pandas as pd
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
# DATA FETCH (YFINANCE)
# =========================
@st.cache_data(ttl=60)
def get_data(symbol, interval):
    try:
        df = yf.download(
            tickers=symbol,
            interval=interval,
            period="1d",
            progress=False
        )

        if df is None or df.empty:
            return None

        # ===== FIX MULTI INDEX =====
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0].lower() for col in df.columns]
        else:
            df.columns = [str(col).lower() for col in df.columns]

        return df

    except Exception as e:
        st.error(f"YFinance error: {e}")
        return None


df = get_data(symbol, interval)

# =========================
# CHECK DATA
# =========================
if df is None:
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

    # EMA
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
