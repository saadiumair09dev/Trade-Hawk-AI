import streamlit as st
import pandas as pd

from data_fetcher import get_data
from indicators.indicators import add_indicators, generate_signal
from ml_model import train_model, predict_signal, calculate_accuracy


st.set_page_config(layout="wide")

st.title("📈 Trade Hawk AI")


# ================= UI =================
symbol = st.selectbox("Select Index", ["^NSEI", "^BANKNIFTY"])
interval = st.selectbox("Timeframe", ["1m", "5m", "15m"])

mode = st.selectbox("Trading Mode", ["LOGIC", "AI", "HYBRID"])


# ================= DATA =================
df = get_data(symbol, interval)

if df is None or df.empty:
    st.error("❌ Data fetch failed")
    st.stop()

st.success("✅ Data Loaded")


# ================= INDICATORS =================
df = add_indicators(df)


# ================= LOGIC SIGNAL =================
logic_signal = generate_signal(df)


# ================= AI MODEL =================
model = train_model(df)

ai_signal = "HOLD"
accuracy = 0

if model is not None:
    ai_signal = predict_signal(model, df)
    accuracy = calculate_accuracy(df)


# ================= FINAL SIGNAL =================
if mode == "LOGIC":
    final_signal = logic_signal

elif mode == "AI":
    final_signal = ai_signal

else:  # HYBRID
    if logic_signal == ai_signal:
        final_signal = logic_signal
    else:
        final_signal = "HOLD"


# ================= DISPLAY =================
st.subheader(f"📊 Mode: {mode}")

st.metric("📈 Signal", final_signal)

if mode != "LOGIC":
    st.metric("🎯 Accuracy %", f"{accuracy:.2f}%")


# ================= TABLE =================
st.dataframe(df.tail(10))
