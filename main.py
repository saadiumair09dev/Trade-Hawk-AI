import streamlit as st
from data_fetcher import get_data
from indicators.indicators import add_indicators
from ml_model import train_model, predict_signal, predict_next_3, calculate_accuracy

st.set_page_config(page_title="Trade Hawk AI", layout="wide")

st.title("📈 Trade Hawk AI")

# ================= INPUT =================
symbol = st.selectbox("Select Index", ["^NSEI", "^BANKNIFTY"])
interval = st.selectbox("Timeframe", ["1m", "5m", "15m"])

mode = st.selectbox("Trading Mode", ["LOGIC", "AI"])

# ================= DATA =================
df = get_data(symbol, interval)

if df is None:
    st.error("❌ Data fetch failed")
    st.stop()

df = add_indicators(df)

st.success("✅ Data Loaded")

# ================= ML =================
model = train_model(df)

signal = predict_signal(model, df)
next3 = predict_next_3(model, df)
accuracy = calculate_accuracy(df)

# ================= ENTRY LOGIC =================
price = df["close"].iloc[-1]

if signal == "BUY":
    entry = price
    sl = price - 50
    tp = price + 100
elif signal == "SELL":
    entry = price
    sl = price + 50
    tp = price - 100
else:
    entry, sl, tp = "-", "-", "-"

# ================= DISPLAY =================
st.subheader(f"📊 Mode: {mode} ({accuracy}% accuracy - {signal})")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Signal", signal)
col2.metric("Entry", entry)
col3.metric("SL", sl)
col4.metric("TP", tp)

# ================= NEXT 3 =================
st.subheader("🔮 Next 3 Candle Prediction")
st.write(next3)

# ================= TABLE =================
st.dataframe(df.tail(20))

# ================= EOD REPORT =================
st.subheader("📄 EOD Report")

st.write({
    "Symbol": symbol,
    "Timeframe": interval,
    "Final Signal": signal,
    "Accuracy": f"{accuracy}%",
    "Next 3": next3
})
