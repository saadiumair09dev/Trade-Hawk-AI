import streamlit as st
import yfinance as yf
import pandas as pd
import time
import streamlit.components.v1 as components

st.set_page_config(page_title="Trade Hawk AI PRO", layout="wide")

# ================= SESSION =================
if "sound_enabled" not in st.session_state:
    st.session_state.sound_enabled = False

if "last_signal" not in st.session_state:
    st.session_state.last_signal = None

if "last_alert_time" not in st.session_state:
    st.session_state.last_alert_time = 0

# ================= TOGGLE =================
def toggle_sound():
    st.session_state.sound_enabled = not st.session_state.sound_enabled

with st.sidebar:
    st.button(
        "🔊 Sound ON" if st.session_state.sound_enabled else "🔇 Sound OFF",
        on_click=toggle_sound
    )

# ================= VOICE =================
def voice_alert(text):
    if not st.session_state.sound_enabled:
        return

    components.html(f"""
    <script>
    var msg = new SpeechSynthesisUtterance("{text}");
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(msg);

    if (navigator.vibrate) {{
        navigator.vibrate([200,100,200]);
    }}
    </script>
    """, height=0)

# ================= TEST =================
if st.sidebar.button("▶️ Test Voice"):
    st.session_state.sound_enabled = True
    voice_alert("System ready. Voice working")

# ================= DATA =================
@st.cache_data(ttl=60)
def get_data(symbol, tf):
    try:
        df = yf.download(symbol, period="5d", interval=tf)

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        return df
    except:
        return None

# ================= GIFT =================
def get_gift_bias():
    try:
        df = yf.download("^NSEI", period="1d", interval="5m")

        if df is None or df.empty:
            return "UNKNOWN"

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        change = df["Close"].iloc[-1] - df["Close"].iloc[-10]

        if change > 30:
            return "BULLISH"
        elif change < -30:
            return "BEARISH"
        else:
            return "SIDEWAYS"
    except:
        return "UNKNOWN"

# ================= INDICATORS =================
def add_indicators(df):
    df["EMA20"] = df["Close"].ewm(span=20).mean()

    delta = df["Close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = -delta.clip(upper=0).rolling(14).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100/(1+rs))

    return df.dropna()

# ================= ADVANCED SIGNAL =================
def advanced_signal(df):
    if df is None or df.empty or len(df) < 30:
        return "NO DATA"

    last = df.iloc[-1]

    ema20 = last["EMA20"]
    price = last["Close"]
    rsi = last["RSI"]

    trend_strength = abs(df["EMA20"].iloc[-1] - df["EMA20"].iloc[-5])
    atr = (df["High"] - df["Low"]).rolling(14).mean().iloc[-1]

    if atr < 5:
        return "NO TRADE"

    if trend_strength < 2:
        return "NO TRADE"

    if price > ema20 and rsi > 60:
        return "BUY"
    elif price < ema20 and rsi < 40:
        return "SELL"
    else:
        return "NO TRADE"

# ================= SPIKE =================
def detect_spike(df):
    if df is None or len(df) < 5:
        return False

    last = df.iloc[-1]
    prev = df.iloc[-2]

    move = abs(last["Close"] - prev["Close"])
    candle = last["High"] - last["Low"]

    return move > 80 or candle > 120

# ================= CRASH =================
def market_crash_guard(df):
    if len(df) < 10:
        return False

    move = df["Close"].iloc[-1] - df["Close"].iloc[-10]

    return abs(move) > 150

# ================= GIFT FILTER =================
def gift_filter(signal, bias):
    if bias == "UNKNOWN":
        return True

    if signal == "BUY" and bias != "BULLISH":
        return False

    if signal == "SELL" and bias != "BEARISH":
        return False

    return True

# ================= MAIN =================
st.title("🦅 Trade Hawk AI PRO")

symbol = "^NSEI"
tf = "5m"

df = get_data(symbol, tf)

if df is None or df.empty:
    st.error("❌ No data")
    st.stop()

df = add_indicators(df)

if df.empty:
    st.stop()

signal = advanced_signal(df)
price = df["Close"].iloc[-1]

gift_bias = get_gift_bias()

spike = detect_spike(df)
crash = market_crash_guard(df)

# ================= FILTER =================
if spike:
    st.warning("⚠️ Spike detected")
    signal = "NO TRADE"

if crash:
    st.error("🚨 Market crash/pump")
    signal = "NO TRADE"

if not gift_filter(signal, gift_bias):
    st.info("Filtered by global bias")
    signal = "NO TRADE"

# ================= DISPLAY =================
st.metric("Signal", signal)
st.metric("Price", f"{price:.2f}")
st.metric("GIFT Bias", gift_bias)

st.line_chart(df["Close"])

# ================= ALERT =================
now = time.time()

if signal in ["BUY", "SELL"]:

    if (signal != st.session_state.last_signal) or (now - st.session_state.last_alert_time > 60):

        if st.session_state.sound_enabled:
            voice_alert(f"{signal} signal confirmed. Market stable")

        st.session_state.last_signal = signal
        st.session_state.last_alert_time = now

        st.success(f"{signal} TRADE")

elif spike:
    voice_alert("Warning. Market spike detected")

elif crash:
    voice_alert("Danger. Market crash detected")

else:
    st.info("No Trade")
