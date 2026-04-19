import streamlit as st
import yfinance as yf
import pandas as pd
import base64
import datetime
import os
import time
from sklearn.ensemble import RandomForestClassifier

st.set_page_config(page_title="Trade Hawk AI PRO", layout="wide")

# ================= SESSION =================
if "sound_enabled" not in st.session_state:
    st.session_state.sound_enabled = False

if "last_signal" not in st.session_state:
    st.session_state.last_signal = None

if "last_alert_time" not in st.session_state:
    st.session_state.last_alert_time = 0

if "trade_log" not in st.session_state:
    st.session_state.trade_log = []

# ================= SOUND =================
def play_sound(file):
    try:
        if os.path.exists(file):
            with open(file, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()

            st.markdown(f"""
            <audio autoplay playsinline>
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """, unsafe_allow_html=True)
    except:
        pass

# ================= VOICE =================
def voice_alert(text):
    if not st.session_state.sound_enabled:
        return

    st.markdown(f"""
    <script>
    const msg = new SpeechSynthesisUtterance("{text}");
    msg.rate = 1;
    msg.pitch = 1;
    msg.volume = 1;
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(msg);
    </script>
    """, unsafe_allow_html=True)

# ================= DATA =================
@st.cache_data(ttl=60)
def get_data(symbol, interval):
    try:
        return yf.download(symbol, period="5d", interval=interval)
    except:
        return None

# ================= INDICATORS =================
def add_indicators(df):
    df["EMA20"] = df["Close"].ewm(span=20).mean()
    df["EMA50"] = df["Close"].ewm(span=50).mean()

    delta = df["Close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = -delta.clip(upper=0).rolling(14).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))

    return df.dropna()

# ================= ML =================
def prepare_ml(df):
    df["target"] = (df["Close"].shift(-3) > df["Close"]).astype(int)
    df["ema_diff"] = df["EMA20"] - df["EMA50"]
    df["volatility"] = df["High"] - df["Low"]
    df = df.dropna()

    if len(df) < 50:
        return None, None

    X = df[["RSI", "ema_diff", "volatility"]]
    y = df["target"]
    return X, y

@st.cache_resource
def train_model(df):
    X, y = prepare_ml(df)
    if X is None:
        return None

    model = RandomForestClassifier(n_estimators=50)
    model.fit(X, y)
    return model

def predict(model, df):
    if model is None or df.empty:
        return 0.5

    last = df.iloc[-1]
    try:
        X = [[
            last["RSI"],
            last["EMA20"] - last["EMA50"],
            last["High"] - last["Low"]
        ]]
        return model.predict_proba(X)[0][1]
    except:
        return 0.5

# ================= SIGNAL =================
def get_signal(df, prob):
    if df is None or df.empty:
        return "NO DATA"

    last = df.iloc[-1]

    if prob > 0.65 and last["Close"] > last["EMA20"]:
        return "BUY"
    elif prob < 0.35 and last["Close"] < last["EMA20"]:
        return "SELL"
    else:
        return "NO TRADE"

# ================= FILTER =================
def live_filter(df, prob):
    last = df.iloc[-1]

    if prob < 0.6:
        return False

    if abs(last["EMA20"] - last["EMA50"]) < 2:
        return False

    return True

# ================= RISK =================
def risk_control(balance, price):
    risk_per_trade = 0.01
    sl = price * 0.98
    qty = int((balance * risk_per_trade) / (price - sl)) if price != sl else 0
    return qty, sl

# ================= AI REASON =================
def generate_reason(df, prob):
    last = df.iloc[-1]
    reasons = []

    if last["RSI"] > 60:
        reasons.append("RSI strong")
    elif last["RSI"] < 40:
        reasons.append("RSI weak")

    if last["Close"] > last["EMA20"]:
        reasons.append("price above EMA")
    else:
        reasons.append("price below EMA")

    if abs(last["EMA20"] - last["EMA50"]) > 2:
        reasons.append("trend strong")
    else:
        reasons.append("sideways market")

    if prob > 0.7:
        reasons.append("AI confidence high")

    return ", ".join(reasons)

# ================= UI =================
st.title("🦅 Trade Hawk AI PRO")

with st.sidebar:
    symbol = st.selectbox("Market", ["^NSEI", "^NSEBANK"])
    tf = st.selectbox("Timeframe", ["5m", "15m"])

    if st.button("🔊 Enable Sound"):
        st.session_state.sound_enabled = True

    if st.button("🔇 Mute"):
        st.session_state.sound_enabled = False

    if st.button("▶️ Test Voice"):
        voice_alert("System ready")

# ================= MAIN =================
df = get_data(symbol, tf)

if df is None or df.empty:
    st.error("⚠️ Data not available")
    st.stop()

df = add_indicators(df)

if df.empty:
    st.warning("Not enough data")
    st.stop()

model = train_model(df)
prob = predict(model, df)
signal = get_signal(df, prob)
price = df["Close"].iloc[-1]
strike = round(price / 100) * 100

reason = generate_reason(df, prob)

# ================= DISPLAY =================
col1, col2, col3 = st.columns(3)
col1.metric("Signal", signal)
col2.metric("AI Confidence", f"{prob:.2f}")
col3.metric("ATM Strike", strike)

st.line_chart(df["Close"])

st.subheader("🧠 AI Reason")
st.info(reason)

# ================= EXECUTION =================
balance = 10000
current_time = time.time()

if signal in ["BUY", "SELL"] and live_filter(df, prob):

    qty, sl = risk_control(balance, price)

    st.success(f"{signal} ORDER | Price: {price:.2f} | Qty: {qty} | SL: {sl:.2f}")

    if (signal != st.session_state.last_signal) or (current_time - st.session_state.last_alert_time > 60):

        if st.session_state.sound_enabled:
            play_sound("buy.mp3")
            voice_alert(f"{signal} signal. {reason}")

        st.session_state.last_signal = signal
        st.session_state.last_alert_time = current_time

    st.session_state.trade_log.append({
        "time": datetime.datetime.now().strftime("%H:%M"),
        "signal": signal,
        "price": float(price),
        "qty": qty
    })

else:
    st.info("No Trade Condition")

# ================= TRADE LOG =================
st.subheader("📋 Trade Log")

if st.session_state.trade_log:
    st.dataframe(pd.DataFrame(st.session_state.trade_log))
