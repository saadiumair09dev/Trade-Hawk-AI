import streamlit as st
import pandas as pd

from data_fetcher import get_data
from indicators.indicators import add_indicators, generate_signal
from ml_model import train_model, predict_signal, predict_next_3, calculate_accuracy


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
logic_raw = generate_signal(df)

# FIX tuple issue
if isinstance(logic_raw, tuple):
    logic_signal = logic_raw[0]
else:
    logic_signal = logic_raw


# ================= AI =================
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

else:
    if logic_signal == ai_signal:
        final_signal = logic_signal
    else:
        final_signal = "HOLD"


# ================= ENTRY / EXIT =================
last_price = df["close"].iloc[-1]

entry = last_price
sl = last_price * 0.995
tp = last_price * 1.01


# ================= MODE TEXT =================
mode_text = mode

if mode != "LOGIC":
    mode_text = f"{mode} ({round(accuracy,2)}% accuracy)"

# ================= DISPLAY =================
st.subheader(f"📊 Mode: {mode_text}")

st.subheader(f"📈 Signal: {final_signal}")

# ================= NEXT 3 CANDLES =================
if model is not None:
    preds = predict_next_3(model, df)

    st.markdown("### 🔮 Next 3 Candle Prediction")

    for p in preds:
        st.write(
            f"Candle {p['candle']} → {p['direction']} @ {p['expected_price']}"
        )
# ================= TRADE INFO =================
col1, col2, col3 = st.columns(3)

col1.metric("Entry", round(entry, 2))
col2.metric("Stop Loss", round(sl, 2))
col3.metric("Target", round(tp, 2))


# ================= LIVE PREDICTION =================
if model is not None:
    st.info("🔮 Live ML Prediction Active")


# ================= EOD REPORT =================
day_high = df["high"].max()
day_low = df["low"].min()

st.markdown("### 📊 EOD Report")

st.write(f"🔼 Day High: {round(day_high,2)}")
st.write(f"🔽 Day Low: {round(day_low,2)}")


# ================= TABLE =================
st.dataframe(df.tail(10))
