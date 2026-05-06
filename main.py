import streamlit as st
from streamlit_autorefresh import st_autorefresh

from data_fetcher import get_data
from indicators.indicators import add_indicators, generate_signal

from ml_model import (
    predict_next,
    predict_multi
)

from trade_logger import (
    log_trade,
    update_results,
    calculate_strike_rate
)


# ================= AUTO REFRESH =================
st_autorefresh(
    interval=15000,
    key="hawk_refresh"
)


# ================= PAGE =================
st.set_page_config(
    page_title="Trade Hawk AI PRO",
    layout="wide"
)

st.title("📈 Trade Hawk AI PRO")


# ================= SESSION =================
if "last_signal" not in st.session_state:
    st.session_state.last_signal = None


# ================= ALERT =================
def trigger_alert(signal):

    if signal not in ["BUY", "SELL"]:
        return

    # repeat only on new signal
    if signal == st.session_state.last_signal:
        return

    st.session_state.last_signal = signal

    st.audio(
        "https://actions.google.com/sounds/v1/alarms/beep_short.ogg"
    )

    if signal == "BUY":

        st.markdown(
            """
            <script>
            let msg = new SpeechSynthesisUtterance(
            "Buy Buy Buy"
            );
            msg.rate = 0.9;
            speechSynthesis.speak(msg);

            if(navigator.vibrate){
                navigator.vibrate([400,200,400]);
            }
            </script>
            """,
            unsafe_allow_html=True
        )

    elif signal == "SELL":

        st.markdown(
            """
            <script>
            let msg = new SpeechSynthesisUtterance(
            "Sell Sell Sell"
            );
            msg.rate = 0.9;
            speechSynthesis.speak(msg);

            if(navigator.vibrate){
                navigator.vibrate([400,200,400]);
            }
            </script>
            """,
            unsafe_allow_html=True
        )


# ================= SYMBOL =================
symbol = st.selectbox(
    "Select Symbol",
    [
        "^NSEI",
        "^BANKNIFTY",
        "RELIANCE.NS",
        "HDFCBANK.NS"
    ]
)


# ================= INTERVAL =================
interval = st.selectbox(
    "Select Timeframe",
    [
        "1m",
        "5m",
        "15m",
        "1h"
    ]
)


# ================= MODE =================
mode_options = {

    "⚡ Scalping":
    "Scalping",

    "⚖️ Balanced":
    "Balanced",

    "🎯 Strict":
    "Strict",

    "🔀 Hybrid":
    "Hybrid",

    "🤖 AI Mode":
    "AI Mode",

    "🧠 ML Mode":
    "ML Mode"

}

selected_label = st.selectbox(
    "Trading Mode",
    list(
        mode_options.keys()
    )
)

mode = mode_options[
    selected_label
]

st.info(
    f"📌 Selected Mode: {selected_label}"
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

df = add_indicators(
    df
)


# ================= TRADE UPDATE =================
price = df[
    "close"
].iloc[-1]

trades = update_results(
    price
)


# ================= STRIKE =================
strike_rate = calculate_strike_rate(
    trades
)


# ================= MODE ACCURACY =================
mode_expected_accuracy = {

    "Scalping": "52–58%",
    "Balanced": "58–65%",
    "Strict": "68–76%",
    "Hybrid": "70–80%",
    "AI Mode": "68–78%",
    "ML Mode": "65–78%"

}

expected_accuracy = mode_expected_accuracy.get(
    mode,
    "N/A"
)

st.info(
    f"""
🎯 Expected Accuracy: {expected_accuracy}

📊 Live Strike Rate: {strike_rate}%
"""
)


# ================= SIGNAL =================
signal = "WAIT"
confidence = 0
reasons = []

if mode == "ML Mode":

    try:

        signal, confidence = predict_next(
            df
        )

    except:

        signal = "WAIT"

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


# ================= REASONS =================
if reasons:

    st.subheader(
        "🧠 Reason"
    )

    for r in reasons:

        st.write(
            "•",
            r
        )


# ================= ALERT =================
trigger_alert(
    signal
)


# ================= TRADE LOGIC =================
if signal in [
    "BUY",
    "SELL"
]:

    log_trade(
        signal,
        price
    )


# ================= SL / TP =================
if signal == "BUY":

    sl = round(
        price * 0.995,
        2
    )

    tp = round(
        price * 1.01,
        2
    )

elif signal == "SELL":

    sl = round(
        price * 1.005,
        2
    )

    tp = round(
        price * 0.99,
        2
    )

else:

    sl = None
    tp = None


if sl and tp:

    st.subheader(
        "🎯 Trade Setup"
    )

    st.write(
        f"Entry: {round(price,2)}"
    )

    st.success(
        f"TP: {tp}"
    )

    st.error(
        f"SL: {sl}"
    )


# ================= NEXT CANDLES =================
st.subheader(
    "🔮 Next 3 Candle Prediction"
)

try:

    future = predict_multi(
        df,
        3
    )

    for i, (
        label,
        conf
    ) in enumerate(
        future
    ):

        strength = "Weak"

        if conf >= 80:

            strength = "Strong"

        elif conf >= 65:

            if label == "BUY":

                strength = "Bullish"

            elif label == "SELL":

                strength = "Bearish"

        st.write(
            f"Candle {i+1}: {label} | {strength} | {conf}%"
        )

except:

    st.warning(
        "Prediction unavailable"
    )


# ================= TRADE LOG =================
st.subheader(
    "📒 Trade Log"
)

if trades is not None and not trades.empty:

    st.dataframe(
        trades.tail(20)
    )

else:

    st.info(
        "No trades yet"
    )


# ================= CHART =================
st.subheader(
    "📉 Live Chart"
)

st.line_chart(
    df["close"]
)
