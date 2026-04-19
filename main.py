import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import base64
from sklearn.ensemble import RandomForestClassifier

st.set_page_config(page_title="Trade Hawk AI PRO", layout="wide")

# ================= SESSION =================
if "sound_enabled" not in st.session_state:
    st.session_state.sound_enabled = False

if "signals_log" not in st.session_state:
    st.session_state.signals_log = []

# ================= SOUND =================
def play_sound(file):
    with open(file, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    st.markdown(f"""
        <audio autoplay>
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
    """, unsafe_allow_html=True)

# ================= DATA =================
@st.cache_data(ttl=60)
def get_data(symbol, interval):
    df = yf.download(symbol, period="1d", interval=interval)
    return df

# ================= INDICATORS =================
def add_indicators(df):
    df["EMA20"] = df["Close"].ewm(span=20).mean()
    df["EMA50"] = df["Close"].ewm(span=50).mean()

    delta = df["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))

    df["VWAP"] = (df["Close"] * df["Volume"]).cumsum() / df["Volume"].cumsum()
    df["ATR"] = (df["High"] - df["Low"]).rolling(14).mean()

    return df.dropna()

# ================= ML =================
def prepare_ml(df):
    df["target"] = (df["Close"].shift(-3) > df["Close"]).astype(int)
    df["ema_diff"] = df["EMA20"] - df["EMA50"]
    df["volatility"] = df["High"] - df["Low"]
    df = df.dropna()
    X = df[["RSI", "ema_diff", "volatility"]]
    y = df["target"]
    return X, y

@st.cache_resource
def train_model(df):
    X, y = prepare_ml(df)
    if len(X) < 50:
        return None
    model = RandomForestClassifier(n_estimators=50)
    model.fit(X, y)
    return model

def predict(model, df):
    if model is None:
        return 0.5
    last = df.iloc[-1]
    X = [[last["RSI"], last["EMA20"]-last["EMA50"], last["High"]-last["Low"]]]
    return model.predict_proba(X)[0][1]

# ================= SIGNAL =================
def get_signal(df, prob):
    last = df.iloc[-1]

    if prob > 0.65 and last["Close"] > last["EMA20"]:
        return "BUY"
    elif prob < 0.35 and last["Close"] < last["EMA20"]:
        return "SELL"
    else:
        return "NO TRADE"

# ================= OPTION =================
def get_atm(price):
    return round(price/100)*100

# ================= BACKTEST =================
def backtest(df, model):
    balance = 10000
    trades = []

    for i in range(50, len(df)-3):
        sub = df.iloc[:i]
        prob = predict(model, sub)
        sig = get_signal(sub, prob)

        if sig == "NO TRADE":
            continue

        entry = df["Close"].iloc[i]
        exit = df["Close"].iloc[i+3]

        pnl = exit-entry if sig=="BUY" else entry-exit
        balance += pnl

        trades.append(pnl)

    return trades, balance

# ================= UI =================
st.title("🦅 Trade Hawk AI PRO")

with st.sidebar:
    symbol = st.selectbox("Market", ["^NSEI","^NSEBANK"])
    tf = st.selectbox("Timeframe", ["5m","15m"])

    if st.button("🔔 Enable Sound"):
        st.session_state.sound_enabled = True

df = get_data(symbol, tf)

if df is not None and not df.empty:
    df = add_indicators(df)

    model = train_model(df)
    prob = predict(model, df)

    signal = get_signal(df, prob)

    price = df["Close"].iloc[-1]
    strike = get_atm(price)

    col1, col2, col3 = st.columns(3)
    col1.metric("Signal", signal)
    col2.metric("AI Confidence", f"{prob:.2f}")
    col3.metric("ATM Strike", strike)

    st.line_chart(df["Close"])

    # SOUND
    if st.session_state.sound_enabled and signal in ["BUY","SELL"]:
        play_sound("buy.mp3")

    # LOG
    import datetime
    st.session_state.signals_log.append({
        "time": datetime.datetime.now().strftime("%H:%M"),
        "signal": signal,
        "price": float(price)
    })

    # BACKTEST
    trades, bal = backtest(df, model)

    st.subheader("📊 Backtest")
    st.write("Balance:", round(bal,2))
    st.line_chart(pd.Series(trades).cumsum())

    # REPORT
    st.subheader("🧾 Daily Report")
    st.dataframe(pd.DataFrame(st.session_state.signals_log))

else:
    st.warning("No data")
