import streamlit as st
import pandas as pd
import requests
import yfinance as yf
import streamlit.components.v1 as components

st.set_page_config(page_title="Trade Hawk AI LIVE", layout="wide")

# ================= SESSION =================
if "sound_enabled" not in st.session_state:
    st.session_state.sound_enabled = False
if "last_signal" not in st.session_state:
    st.session_state.last_signal = None

# ================= SOUND =================
def toggle_sound():
    st.session_state.sound_enabled = not st.session_state.sound_enabled

with st.sidebar:
    st.button("🔊 Sound ON/OFF", on_click=toggle_sound)

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

if st.sidebar.button("▶️ Test Voice"):
    st.session_state.sound_enabled = True
    voice_alert("System ready")

# ================= DHAN DATA =================
def get_dhan_data(security_id="13", interval="5"):
    try:
        token = st.secrets["dhan"]["token"]
        client_id = st.secrets["dhan"]["client_id"]

        url = "https://api.dhan.co/v2/charts/intraday"

        payload = {
            "securityId": security_id,
            "exchangeSegment": "IDX_I",
            "interval": interval
        }

        headers = {
            "access-token": token,
            "client-id": client_id,
            "Content-Type": "application/json"
        }

        res = requests.post(url, json=payload, headers=headers)
        data = res.json()

        if "data" not in data:
            return None

        df = pd.DataFrame(data["data"])

        df.rename(columns={
            "open": "Open",
            "high": "High",
            "low": "Low",
            "close": "Close",
            "volume": "Volume"
        }, inplace=True)

        return df

    except Exception as e:
        st.error(f"Dhan Error: {e}")
        return None

# ================= YAHOO BACKUP =================
def get_backup():
    try:
        df = yf.download("^NSEI", period="5d", interval="5m")
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except:
        return None

# ================= INDICATORS =================
def add_indicators(df):
    if df is None or df.empty:
        return df

    df["EMA20"] = df["Close"].ewm(span=20).mean()

    delta = df["Close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = -delta.clip(upper=0).rolling(14).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100/(1+rs))

    df["VWAP"] = (df["Close"] * df["Volume"]).cumsum() / df["Volume"].cumsum()

    return df.dropna()

# ================= SIGNAL LOGIC =================
def ai_signal(df):
    if df is None or len(df) < 20:
        return "NO DATA"
    last = df.iloc[-1]
    if last["Close"] > last["EMA20"] and last["RSI"] > 60:
        return "BUY"
    elif last["Close"] < last["EMA20"] and last["RSI"] < 40:
        return "SELL"
    return "NO TRADE"

def gap_signal(df):
    if df is None or len(df) < 20:
        return "WAIT"

    prev_close = df["Close"].iloc[-20]
    open_price = df["Open"].iloc[-1]
    gap = open_price - prev_close

    orb_high = df["High"].iloc[-3:].max()
    orb_low = df["Low"].iloc[-3:].min()
    last = df.iloc[-1]

    if gap > 80:
        if last["Close"] > orb_high and last["Close"] > last["VWAP"]:
            return "BUY"
        elif last["Close"] < orb_low and last["Close"] < last["VWAP"]:
            return "SELL"

    elif gap < -80:
        if last["Close"] < orb_low and last["Close"] < last["VWAP"]:
            return "SELL"
        elif last["Close"] > orb_high and last["Close"] > last["VWAP"]:
            return "BUY"

    return "WAIT"

def liquidity(df):
    if df is None or len(df) < 10:
        return None
    last = df.iloc[-1]
    prev_high = df["High"].iloc[-6:-1].max()
    prev_low = df["Low"].iloc[-6:-1].min()

    if last["High"] > prev_high and last["Close"] < prev_high:
        return "SELL"
    if last["Low"] < prev_low and last["Close"] > prev_low:
        return "BUY"
    return None

def fake_breakout(df):
    if df is None or len(df) < 3:
        return False
    last = df.iloc[-1]
    prev = df.iloc[-2]

    if last["High"] > prev["High"] and last["Close"] < prev["High"]:
        return True
    if last["Low"] < prev["Low"] and last["Close"] > prev["Low"]:
        return True
    return False

def spike(df):
    if df is None or len(df) < 3:
        return False
    last = df.iloc[-1]
    prev = df.iloc[-2]
    return abs(last["Close"] - prev["Close"]) > 80

# ================= MAIN =================
st.title("🦅 Trade Hawk AI LIVE (Dhan Powered)")

df = get_dhan_data("13")

if df is None or df.empty:
    st.warning("Using backup data...")
    df = get_backup()

if df is None or df.empty:
    st.error("No data available")
    st.stop()

df = add_indicators(df)

if df is None or df.empty:
    st.stop()

ai = ai_signal(df)
gap = gap_signal(df)
liq = liquidity(df)
fake = fake_breakout(df)
spk = spike(df)

final = "NO TRADE"

if fake:
    st.warning("Fake breakout detected")

elif spk:
    st.error("Spike detected")

elif liq:
    final = liq

elif ai == gap:
    final = ai

# ================= UI =================
st.metric("FINAL SIGNAL", final)
st.metric("AI SIGNAL", ai)
st.metric("GAP SIGNAL", gap)

st.line_chart(df["Close"])

# ================= ALERT =================
if final in ["BUY", "SELL"] and final != st.session_state.last_signal:
    voice_alert(f"{final} trade detected")
    st.session_state.last_signal = final
