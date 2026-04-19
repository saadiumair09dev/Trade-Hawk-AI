import streamlit as st
import pandas as pd

# ===== IMPORTS =====
from data.dhan_api import get_data
from indicators.indicators import add_indicators

# ===== UI =====
st.set_page_config(page_title="Trade Hawk AI", layout="wide")

st.title("📈 Trade Hawk AI")

symbol = st.selectbox("Select Index", ["^NSEI", "^NSEBANK"])
interval = st.selectbox("Timeframe", ["5m", "15m", "1h"])

# ===== DATA =====
df = get_data(symbol, interval)

if df is None or df.empty:
    st.error("❌ Data fetch failed")
    st.stop()

st.success("✅ Data Loaded")

# ===== INDICATORS =====
df = add_indicators(df)

if df is None:
    st.error("❌ Indicator calculation failed")
    st.stop()

# ===== DEBUG (IMPORTANT) =====
# uncomment if needed
# st.write(df.columns)

# ===== SIGNAL LOGIC (SAFE) =====
if "EMA_9" not in df.columns or "EMA_21" not in df.columns:
    st.error("❌ EMA not found in data")
    st.stop()

last = df.iloc[-1]

signal = "HOLD"

if last["EMA_9"] > last["EMA_21"]:
    signal = "BUY"
elif last["EMA_9"] < last["EMA_21"]:
    signal = "SELL"

# ===== OUTPUT =====
st.subheader("Signal")

if signal == "BUY":
    st.success("🟢 BUY Signal")
elif signal == "SELL":
    st.error("🔴 SELL Signal")
else:
    st.info("⚪ HOLD")

# ===== SHOW DATA =====
st.dataframe(df.tail(10))
