import streamlit as st
import pandas as pd

from data_fetcher import get_data
from indicators.indicators import add_indicators, generate_signal


# ================= PAGE =================
st.set_page_config(page_title="Trade Hawk AI", layout="wide")

st.title("📈 Trade Hawk AI")


# ================= INPUT (ALWAYS VISIBLE) =================
symbol = st.selectbox(
    "Select Index / Stock",
    ["^NSEI", "^BANKNIFTY", "RELIANCE", "HDFCBANK"]
)

interval = st.selectbox(
    "Timeframe",
    ["1m", "5m", "15m", "1h"]
)

# 🔥 MODE ALWAYS VISIBLE (FIXED)
mode = st.selectbox(
    "Select Trading Mode",
    ["Scalping", "Balanced", "Strict"]
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
signal, confidence, reasons = generate_signal(df, mode)

if signal in ["BUY", "STRONG BUY"]:
    st.success(f"🚀 {signal} | Confidence: {confidence}%")
elif signal in ["SELL", "STRONG SELL"]:
    st.error(f"🔻 {signal} | Confidence: {confidence}%")
else:
    st.warning("⏳ WAIT")

# 🔍 AI reasoning show
if reasons:
    st.subheader("🧠 Decision Reason")
    for r in reasons:
        st.write("•", r)

# ================= DATA =================
st.subheader("📊 Latest Data")
st.dataframe(df.tail(50))


# ================= CHART =================
st.subheader("📉 Price Chart")
st.line_chart(df["close"])
