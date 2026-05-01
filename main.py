import streamlit as st
import time

from data_fetcher import get_data
from indicators.indicators import add_indicators, generate_signal
from ml_model import predict_next, predict_multi, calculate_accuracy
from trade_logger import log_trade, load_trades, update_results, calculate_strike_rate


# ================= PAGE =================
st.set_page_config(page_title="Trade Hawk AI PRO", layout="wide")
st.title("📈 Trade Hawk AI PRO (Live Mode)")


# ================= SETTINGS =================
refresh_rate = st.slider("⏱ Refresh Speed (sec)", 1, 10, 2)


# ================= ALERT MEMORY =================
if "last_signal" not in st.session_state:
    st.session_state.last_signal = None


# ================= ALERT =================
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
        navigator.vibrate([300,200,300]);
    }
    </script>
    """, unsafe_allow_html=True)


# ================= SL TP =================
def calculate_sl_tp(price, signal):
    if signal == "BUY":
        return round(price * 0.995, 2), round(price * 1.01, 2)
    elif signal == "SELL":
        return round(price * 1.005, 2), round(price * 0.99, 2)
    return None, None


# ================= INPUT =================
symbol = st.selectbox(
    "Select Symbol",
    ["^NSEI", "^BANKNIFTY", "RELIANCE.NS", "HDFCBANK.NS"]
)

interval = st.selectbox(
    "Timeframe",
    ["1m", "5m", "15m", "1h"]
)

mode_options = {
    "⚡ Scalping": "Scalping",
    "⚖️ Balanced": "Balanced",
    "🎯 Strict": "Strict",
    "🔀 Hybrid": "Hybrid",
    "🤖 AI Mode": "AI Mode",
    "🧠 ML Mode": "ML Mode"
}

selected_label = st.selectbox("Trading Mode", list(mode_options.keys()))
mode = mode_options[selected_label]

st.info(f"📌 Selected Mode: {selected_label}")


# ================= LIVE LOOP =================
placeholder = st.empty()

while True:
    with placeholder.container():

        # ===== DATA =====
        df = get_data(symbol, interval)

        if df is None or df.empty:
            st.error("❌ Data fetch failed")
            break

        df = add_indicators(df)

        # ===== ACCURACY =====
        accuracy = calculate_accuracy(df)
        st.info(f"📊 Accuracy: {accuracy}%")

        # ===== SIGNAL =====
        signal = "WAIT"
        confidence = 0

        if mode == "ML Mode":
            signal, confidence = predict_next(df)
        else:
            signal, confidence, _ = generate_signal(df, mode)

        # ===== SHOW SIGNAL =====
        if signal == "BUY":
            st.success(f"🚀 BUY ({confidence}%)")
        elif signal == "SELL":
            st.error(f"🔻 SELL ({confidence}%)")
        else:
            st.warning("⏳ WAIT")

        # ===== ALERT =====
        trigger_alert(signal)

        # ===== TRADE LOG =====
        price = df["close"].iloc[-1]

        if signal in ["BUY", "SELL"]:
            log_trade(signal, price)

        trades = update_results(price)

        # ===== STRIKE RATE =====
        strike = calculate_strike_rate(trades)
        st.info(f"🎯 Strike Rate: {strike}%")

        # ===== SL TP =====
        sl, tp = calculate_sl_tp(price, signal)

        if sl and tp:
            st.write(f"Entry: {round(price,2)}")
            st.success(f"TP: {tp}")
            st.error(f"SL: {sl}")

        # ===== MULTI =====
        st.subheader("🔮 Next 3 Candles")

        try:
            multi = predict_multi(df, 3)
            for i, (sig, conf) in enumerate(multi):
                st.write(f"{i+1}: {sig} ({conf}%)")
        except:
            pass

        # ===== TRADE LOG =====
        st.subheader("📒 Trade Log")
        if not trades.empty:
            st.dataframe(trades.tail(20))

        # ===== CHART =====
        st.subheader("📉 Live Chart")
        st.line_chart(df["close"])

    time.sleep(refresh_rate)
    st.rerun()
# ================= KAL KA EOD =================
st.subheader("📅 Yesterday EOD Report")

import pandas as pd
from datetime import datetime, timedelta

trades = load_trades()

if not trades.empty:
    # time column को datetime बनाओ (safe)
    if "time" in trades.columns:
        trades["time"] = pd.to_datetime(trades["time"], errors="coerce")

    # कल की date
    yesterday = (datetime.now() - timedelta(days=1)).date()

    # सिर्फ कल के trades
    y_trades = trades[trades["time"].dt.date == yesterday]

    if not y_trades.empty:
        closed = y_trades[y_trades["result"] != "OPEN"]

        total = len(closed)
        wins = len(closed[closed["result"] == "WIN"])
        losses = len(closed[closed["result"] == "LOSS"])

        strike = round((wins / total) * 100, 2) if total > 0 else 0

        st.write(f"📊 Total Trades: {total}")
        st.write(f"✅ Wins: {wins}")
        st.write(f"❌ Losses: {losses}")
        st.write(f"🎯 Strike Rate: {strike}%")

        st.dataframe(y_trades.tail(20))
    else:
        st.write("No trades found for yesterday")
else:
    st.write("No trade data available")
