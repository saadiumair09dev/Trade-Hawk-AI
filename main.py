import streamlit as st

from data_fetcher import get_data
from indicators.indicators import add_indicators, generate_signal
from ml_model import predict_next, predict_multi, calculate_accuracy


st.set_page_config(page_title="Trade Hawk AI", layout="wide")
st.title("📈 Trade Hawk AI PRO")

# ================= INPUT =================
symbol = st.selectbox(
    "Select Symbol",
    ["^NSEI", "^BANKNIFTY", "RELIANCE", "HDFCBANK"]
)

interval = st.selectbox(
    "Timeframe",
    ["1m", "5m", "15m", "1h"]
)

mode = st.selectbox(
    "Trading Mode",
    ["Scalping", "Balanced", "Strict", "Hybrid", "AI Mode", "ML Mode"]
)

# ================= DATA =================
df = get_data(symbol, interval)

if df is None or df.empty:
    st.error("❌ Data fetch failed")
    st.stop()

df = add_indicators(df)

# ================= ACCURACY =================
accuracy = calculate_accuracy(df)

st.info(f"📊 Model Accuracy: {accuracy}%")

# ================= SIGNAL =================
if mode == "ML Mode":
    signal, confidence = predict_next(df)

    if signal == "BUY":
        st.success(f"🤖 ML BUY | Confidence: {confidence}%")
    else:
        st.error(f"🤖 ML SELL | Confidence: {confidence}%")

else:
    signal, confidence, reasons = generate_signal(df, mode)

    if signal in ["BUY", "STRONG BUY"]:
        st.success(f"🚀 {signal} | Confidence: {confidence}%")
    elif signal in ["SELL", "STRONG SELL"]:
        st.error(f"🔻 {signal} | Confidence: {confidence}%")
    else:
        st.warning("⏳ WAIT")

# ================= MULTI CANDLE =================
st.subheader("🔮 Next 3 Candle Prediction")

multi = predict_multi(df, 3)

for i, (sig, conf) in enumerate(multi):
    st.write(f"Candle {i+1}: {sig} ({conf}%)")

# ================= EOD REPORT =================
st.subheader("📋 EOD Report")

st.write(f"Symbol: {symbol}")
st.write(f"Mode: {mode}")
st.write(f"Accuracy: {accuracy}%")

# ================= DATA =================
st.subheader("📊 Data")
st.dataframe(df.tail(50))

st.subheader("📉 Chart")
st.line_chart(df["close"])
