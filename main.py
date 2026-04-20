import streamlit as st

from data_fetcher import get_data
from indicators.indicators import add_indicators, generate_signal
from ml_model import predict_next, predict_multi, calculate_accuracy


# ================= PAGE =================
st.set_page_config(page_title="Trade Hawk AI PRO", layout="wide")
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


# ================= MODE OPTIONS =================
mode_options = {
    "⚡ Scalping (Fast | 50%)": "Scalping",
    "⚖️ Balanced (Medium | 60%)": "Balanced",
    "🎯 Strict (Safe | 75%)": "Strict",
    "🔀 Hybrid (Smart | 70%)": "Hybrid",
    "🤖 AI Mode (Adaptive | 72%)": "AI Mode",
    "🧠 ML Mode (Predictive | 75-80%)": "ML Mode"
}

selected_label = st.selectbox(
    "Trading Mode",
    list(mode_options.keys())
)

mode = mode_options[selected_label]

# ✅ BONUS (ONLY ONCE, CORRECT PLACE)
st.info(f"📌 Selected Mode: {selected_label}")


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
    try:
        signal, confidence = predict_next(df)

        if signal == "BUY":
            st.success(f"🤖 ML BUY | Confidence: {confidence}%")
        else:
            st.error(f"🤖 ML SELL | Confidence: {confidence}%")

    except:
        st.warning("⏳ WAIT")

else:
    signal, confidence, reasons = generate_signal(df, mode)

    if signal in ["BUY", "STRONG BUY"]:
        st.success(f"🚀 {signal} | Confidence: {confidence}%")
    elif signal in ["SELL", "STRONG SELL"]:
        st.error(f"🔻 {signal} | Confidence: {confidence}%")
    else:
        st.warning("⏳ WAIT")

    if reasons:
        st.subheader("🧠 Reason")
        for r in reasons:
            st.write("•", r)


# ================= MULTI CANDLE =================
st.subheader("🔮 Next 3 Candle Prediction")

try:
    multi = predict_multi(df, 3)

    for i, (sig, conf) in enumerate(multi):
        st.write(f"Candle {i+1}: {sig} ({conf}%)")

except:
    st.write("Prediction not available")


# ================= EOD REPORT =================
st.subheader("📋 EOD Report")

st.write(f"Symbol: {symbol}")
st.write(f"Mode: {selected_label}")
st.write(f"Accuracy: {accuracy}%")
st.write(f"Last Signal: {signal}")


# ================= DATA =================
st.subheader("📊 Data")
st.dataframe(df.tail(50))

st.subheader("📉 Chart")
st.line_chart(df["close"])
