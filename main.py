import streamlit as st
import yfinance as yf
import pandas as pd
import base64
import datetime
from sklearn.ensemble import RandomForestClassifier

st.set_page_config(page_title="Trade Hawk AI PRO", layout="wide")

# ================= SESSION =================
if "sound_enabled" not in st.session_state:
    st.session_state.sound_enabled = False

if "last_signal" not in st.session_state:
    st.session_state.last_signal = None

# ================= SOUND =================
def play_sound(file):
    try:
        with open(file, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        st.markdown(f"""
        <audio autoplay>
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        """, unsafe_allow_html=True)
    except:
        pass

# ================= DATA =================
@st.cache_data(ttl=60)
def get_data(symbol, interval):
    try:
        df = yf.download(symbol, period="5d", interval=interval)
        return df
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

# ================= UI =================
st.title("🦅 Trade Hawk AI PRO")

with st.sidebar:
    symbol = st.selectbox("Market", ["^NSEI", "^NSEBANK"])
    tf = st.selectbox("Timeframe", ["5m", "15m"])

    if st.button("🔔 Enable Sound"):
        st.session_state.sound_enabled = True

# ================= MAIN =================
df = get_data(symbol, tf)

# 🔥 CRITICAL FIX
if df is None or df.empty:
    st.error("⚠️ Data not available (Rate limit / Market closed)")
    st.stop()

df = add_indicators(df)

if df.empty:
    st.warning("Not enough data after indicators")
    st.stop()

model = train_model(df)
prob = predict(model, df)

signal = get_signal(df, prob)

price = df["Close"].iloc[-1]
strike = round(price / 100) * 100

# ================= UI DISPLAY =================
col1, col2, col3 = st.columns(3)
col1.metric("Signal", signal)
col2.metric("AI Confidence", f"{prob:.2f}")
col3.metric("ATM Strike", strike)

st.line_chart(df["Close"])

# ================= SOUND =================
if signal != st.session_state.last_signal:
    if st.session_state.sound_enabled:
        if signal == "BUY":
            play_sound("buy.mp3")
        elif signal == "SELL":
            play_sound("sell.mp3")

    st.session_state.last_signal = signal
