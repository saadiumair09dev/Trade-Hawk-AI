import streamlit as st
from data.dhan_api import get_data
from indicators.indicators import add_indicators

st.set_page_config(page_title="Trade Hawk AI", layout="wide")

st.title("📈 Trade Hawk AI")

# ================= INPUT =================
symbol = st.selectbox("Select Index", ["^NSEI", "^BANKNIFTY", "^FINNIFTY"])
interval = st.selectbox("Timeframe", ["5m", "15m", "1h"])

# ================= DATA =================
df = get_data(symbol, interval)

if df is None or df.empty:
    st.error("❌ Data fetch failed")
    st.stop()

st.success("✅ Data Loaded")

# ================= INDICATORS =================
df = add_indicators(df)

if df is None or df.empty:
    st.error("❌ Indicator calculation failed")
    st.stop()

st.success("✅ Indicators Ready")

# ================= DEBUG =================
st.subheader("Last Data")
st.dataframe(df.tail())

# ================= SIMPLE SIGNAL =================
signal = "NO TRADE"

if df["EMA_9"].iloc[-1] > df["EMA_21"].iloc[-1] and df["Rsi"].iloc[-1] > 50:
    signal = "BUY"
elif df["EMA_9"].iloc[-1] < df["EMA_21"].iloc[-1] and df["Rsi"].iloc[-1] < 50:
    signal = "SELL"

st.subheader("Signal")
st.write(signal)
