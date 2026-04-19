import streamlit as st
from data.dhan_api import get_data
from indicators.indicators import add_indicators

st.set_page_config(page_title="Trade Hawk AI", layout="wide")

st.title("📈 Trade Hawk AI")

# Inputs
symbol = st.selectbox("Select Index", ["^NSEI"])
interval = st.selectbox("Timeframe", ["5m", "15m", "1h"])

# Fetch data
df = get_data(symbol, interval)

if df is None or df.empty:
    st.error("❌ Data fetch failed")
    st.stop()

st.success("✅ Data Loaded")

# Add indicators
df = add_indicators(df)

# Check columns exist BEFORE using
required_cols = ["EMA_9", "EMA_21"]

missing = [col for col in required_cols if col not in df.columns]

if missing:
    st.error(f"❌ Indicator calculation failed: Missing {missing}")
    st.dataframe(df.tail())
    st.stop()

st.success("✅ Indicators Calculated")

# Signal Logic
last = df.iloc[-1]

if last["EMA_9"] > last["EMA_21"]:
    st.success("🟢 BUY Signal")
else:
    st.error("🔴 SELL Signal")

# Show data
st.dataframe(df.tail(10))
