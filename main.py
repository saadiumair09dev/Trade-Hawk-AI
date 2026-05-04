import streamlit as st
import time

from data_fetcher import get_data
from indicators.indicators import add_indicators, generate_signal
from ml_model import predict_next, predict_multi, calculate_accuracy
from trade_logger import (
    log_trade,
    load_trades,
    update_results,
    calculate_strike_rate
)


# ================= PAGE =================
st.set_page_config(
    page_title="Trade Hawk AI PRO",
    layout="wide"
)

st.title("📈 Trade Hawk AI PRO")


# ================= AUTO REFRESH =================
refresh_rate = st.slider(
    "Refresh Speed (sec)",
    2,
    15,
    5
)

# Safe refresh
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()


# ================= ALERT MEMORY =================
if "last_signal" not in st.session_state:
    st.session_state.last_signal = None


# ================= SIGNAL ALERT =================
def trigger_alert(signal):

    if signal not in ["BUY", "SELL"]:
        return

    if signal == st.session_state.last_signal:
        return

    st.session_state.last_signal = signal

    st.audio(
        "https://www.soundjay.com/buttons/beep-07.mp3"
    )

    st.markdown(
        """
        <script>
        if (navigator.vibrate){
            navigator.vibrate([300,200,300]);
        }
        </script>
        """,
        unsafe_allow_html=True
    )


# ================= SL TP =================
def calculate_sl_tp(price, signal):

    if signal == "BUY":

        sl = round(
            price * 0.995,
            2
        )

        tp = round(
            price * 1.01,
            2
        )

        return sl, tp

    elif signal == "SELL":

        sl = round(
            price * 1.005,
            2
        )

        tp = round(
            price * 0.99,
            2
        )

        return sl, tp

    return None, None


# ================= INPUT =================
symbol = st.selectbox(
    "Select Symbol",
    [
        "^NSEI",
        "^BANKNIFTY",
        "RELIANCE.NS",
        "HDFCBANK.NS"
    ]
)

interval = st.selectbox(
    "Timeframe",
    [
        "1m",
        "5m",
        "15m",
        "1h"
    ]
)


# ================= MODE =================
mode_options = {
    "⚡ Scalping": "Scalping",
    "⚖️ Balanced": "Balanced",
    "🎯 Strict": "Strict",
    "🔀 Hybrid": "Hybrid",
    "🤖 AI Mode": "AI Mode",
    "🧠 ML Mode": "ML Mode"
}

selected_label = st.selectbox(
    "Trading Mode",
    list(mode_options.keys())
)

mode = mode_options[selected_label]

st.info(
    f"📌 Mode: {selected_label}"
)


# ================= DATA =================
df = get_data(
    symbol,
    interval
)

if df is None or df.empty:

    st.error(
        "❌ Data fetch failed"
    )

    st.stop()


df = add_indicators(df)


# ================= ACCURACY =================
accuracy = calculate_accuracy(df)

st.info(
    f"📊 Accuracy: {accuracy}%"
)


# ================= SIGNAL =================
signal = "WAIT"

confidence = 0

if mode == "ML Mode":

    signal, confidence = predict_next(
        df
    )

else:

    signal, confidence, reasons = generate_signal(
        df,
        mode
    )


# ================= SIGNAL UI =================
if signal == "BUY":

    st.success(
        f"🚀 BUY ({confidence}%)"
    )

elif signal == "SELL":

    st.error(
        f"🔻 SELL ({confidence}%)"
    )

else:

    st.warning(
        "⏳ WAIT"
    )


# ================= ALERT =================
trigger_alert(
    signal
)


# ================= TRADE =================
price = df[
    "close"
].iloc[-1]


# Avoid duplicate logs
if signal != st.session_state.last_signal:

    if signal in ["BUY", "SELL"]:

        log_trade(
            signal,
            price
        )


# ================= UPDATE LOG =================
trades = update_results(
    price
)


# ================= STRIKE RATE =================
strike = calculate_strike_rate(
    trades
)

st.info(
    f"🎯 Strike Rate: {strike}%"
)


# ================= SL TP =================
sl, tp = calculate_sl_tp(
    price,
    signal
)

if sl and tp:

    st.write(
        f"Entry: {round(price,2)}"
    )

    st.success(
        f"TP: {tp}"
    )

    st.error(
        f"SL: {sl}"
    )


# ================= MULTI CANDLE =================
st.subheader(
    "🔮 Next 3 Candles"
)

try:

    multi = predict_multi(
        df,
        3
    )

    for i, (label, conf) in enumerate(multi):

        st.write(
            f"{i+1}: {label} ({conf}%)"
        )

except:

    st.warning(
        "Prediction unavailable"
    )


# ================= TRADE LOG =================
st.subheader(
    "📒 Trade Log"
)

if not trades.empty:

    st.dataframe(
        trades.tail(20)
    )


# ================= CHART =================
st.subheader(
    "📉 Live Chart"
)

st.line_chart(
    df["close"]
)
