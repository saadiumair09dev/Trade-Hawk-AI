import streamlit as st
import time
from data_fetcher import get_data
from indicators.indicators import add_indicators, generate_signal
from ml_model import predict_next, predict_multi, calculate_accuracy
from trade_logger import log_trade, load_trades, update_results, calculate_strike_rate


# ================= PAGE =================
st.set_page_config(page_title="Trade Hawk AI PRO", layout="wide")
st.title("📈 Trade Hawk AI PRO")


# ================= ALERT MEMORY =================
if "last_signal" not in st.session_state:
    st.session_state.last_signal = None


# ================= ALERT FUNCTION =================
def trigger_alert(signal):
    if signal not in ["BUY", "SELL"]:
        return

    if st.session_state.last_signal == signal:
        return

    st.session_state.last_signal = signal

    for _ in range(3):
        st.audio("https://www.soundjay.com/buttons/beep-07.mp3")

    st.markdown("""
    <script>
    if (navigator.vibrate) {
        navigator.vibrate([300,200,300,200,500]);
    }
    </script>
    """, unsafe_allow_html=True)


# ================= SL/TP =================
def calculate_sl_tp(price, signal):
    if signal == "BUY":
        sl = price * 0.995
        tp = price * 1.01
    elif signal == "SELL":
        sl = price * 1.005
        tp = price * 0.99
    else:
        return None, None

    return round(sl, 2), round(tp, 2)


# ================= INPUT =================
symbol = st.selectbox(
    "Select Symbol",
    ["^NSEI", "^BANKNIFTY", "RELIANCE", "HDFCBANK"]
)

interval = st.selectbox(
    "Timeframe",
    ["1m", "5m", "15m", "1h"]
)


# ================= MODE =================
mode_options = {
    "⚡ Scalping (Fast | 50%)": "Scalping",
    "⚖️ Balanced (Medium | 60%)": "Balanced",
    "🎯 Strict (Safe | 75%)": "Strict",
    "🔀 Hybrid (Smart | 70%)": "Hybrid",
    "🤖 AI Mode (Adaptive | 72%)": "AI Mode",
    "🧠 ML Mode (Predictive | 75-80%)": "ML Mode"
}

selected_label = st.selectbox("Trading Mode", list(mode_options.keys()))
mode = mode_options[selected_label]

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
signal = "WAIT"
confidence = 0

if mode == "ML Mode":
    try:
        signal, confidence = predict_next(df)

        if signal == "BUY":
            st.success(f"🤖 ML BUY | Confidence: {confidence}%")
        elif signal == "SELL":
            st.error(f"🤖 ML SELL | Confidence: {confidence}%")
        else:
            st.warning("⏳ WAIT")

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


# ================= ALERT =================
trigger_alert(signal)


# ================= TRADE LOG =================
price = df["close"].iloc[-1]

if signal in ["BUY", "SELL"]:
    log_trade(signal, price)

trades = update_results(price)


# ================= STRIKE RATE =================
strike = calculate_strike_rate(trades)
st.info(f"🎯 Strike Rate: {strike}%")


# ================= SL/TP DISPLAY =================
sl, tp = calculate_sl_tp(price, signal)

if sl and tp:
    st.subheader("🎯 Risk Management")
    st.info(f"Entry: {round(price,2)}")
    st.success(f"Take Profit (TP): {tp}")
    st.error(f"Stop Loss (SL): {sl}")


# ================= MULTI =================
st.subheader("🔮 Next 3 Candle Prediction")

try:
    multi = predict_multi(df, 3)

    for i, (sig, conf) in enumerate(multi):
        st.write(f"Candle {i+1}: {sig} ({conf}%)")

except:
    st.write("Prediction not available")


# ================= TRADE LOG UI =================
st.subheader("📒 Trade Log")

if not trades.empty:
    st.dataframe(trades.tail(20))
else:
    st.write("No trades yet")


# ================= EOD =================
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
