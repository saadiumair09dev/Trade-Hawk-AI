import streamlit as st
import pandas as pd

from data_fetcher import get_data
from indicators.indicators import add_indicators, generate_signal


# ================= UI =================
st.set_page_config(page_title="Trade Hawk AI", layout="wide")

st.title("📈 Trade Hawk AI")


# ================= INPUT =================
symbol = st.selectbox(
    "Select Index / Stock",
    ["^NSEI", "^BANKNIFTY", "RELIANCE", "HDFCBANK"]
)

interval = st.selectbox(
    "Timeframe",
    ["1m", "5m", "15m", "1h"]
)


# ================= FETCH DATA =================
df = get_data(symbol, interval)

if df is None or df.empty:
    st.error("❌ Data fetch failed")
    st.stop()


st.success("✅ Data Loaded")


# ================= INDICATORS =================
try:
    df = add_indicators(df)
except Exception as e:
    st.error(f"❌ Indicator error: {e}")
    st.stop()


# ================= SIGNAL =================
try:
    signal = generate_signal(df)

    if signal == "BUY":
        st.success("📊 Signal: BUY")
    elif signal == "SELL":
        st.error("📊 Signal: SELL")
    else:
        st.warning("📊 Signal: HOLD")

except Exception as e:
    st.error(f"❌ Signal error: {e}")


# ================= DATA TABLE =================
st.subheader("📊 Latest Data")

# last rows only
st.dataframe(df.tail(50))


# ================= CHART =================
st.subheader("📉 Price Chart")

st.line_chart(df["close"])
