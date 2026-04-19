import streamlit as st

# ================= IMPORTS =================
from data.dhan_api import get_data
from indicators.indicators import add_indicators
from strategies.signal_engine import base_signal
from strategies.filters import crash_detection, trap_detection, gap_detection
from strategies.correlation import correlation
from ai.ai_model import train_model, predict
from risk.position import position_size, risk_label
from ui.chart import plot_chart
from config import SYMBOLS

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Trade Hawk AI PRO", layout="wide")

st.title("🦅 Trade Hawk AI PRO (Modular System)")

# ================= FETCH DATA =================
nifty = get_data(SYMBOLS["NIFTY"])
bank = get_data(SYMBOLS["BANKNIFTY"])
fin = get_data(SYMBOLS["FINNIFTY"])

if nifty is None or bank is None or fin is None:
    st.error("❌ Data fetch error (Check Dhan API)")
    st.stop()

# ================= ADD INDICATORS =================
nifty = add_indicators(nifty)
bank = add_indicators(bank)
fin = add_indicators(fin)

if nifty is None or nifty.empty:
    st.error("❌ Indicator calculation failed")
    st.stop()

# ================= BASE SIGNAL =================
base = base_signal(nifty)

# ================= CORRELATION =================
corr = correlation(nifty, bank, fin)

# ================= FINAL SIGNAL =================
final = "NO"

if base == corr:
    final = base

# ================= FILTERS =================
crash = crash_detection(nifty)
trap = trap_detection(nifty)
gap = gap_detection(nifty)

if crash:
    st.warning("🚨 Crash / Spike Detected")
    final = "NO"

if trap:
    st.warning("🪤 Trap Candle Detected")
    final = "NO"

if gap:
    st.info("📊 Gap Detected")

# ================= AI =================
model = train_model(nifty)
ai_pred, confidence = predict(nifty, model)

# AI FILTER
if final == "BUY" and ai_pred == "DOWN":
    final = "NO"

elif final == "SELL" and ai_pred == "UP":
    final = "NO"

# ================= POSITION SIZE =================
pos_size = position_size(confidence)
risk_text = risk_label(pos_size)

if pos_size == 0:
    final = "NO"

# ================= UI =================
st.subheader("📊 Signal Dashboard")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Base Signal", base)

with col2:
    st.metric("Correlation", corr)

with col3:
    st.metric("Final Signal", final)

# ================= AI DISPLAY =================
st.subheader("🤖 AI Prediction")

st.write(f"Direction: **{ai_pred}**")
st.write(f"Confidence: **{confidence}%**")

# ================= POSITION =================
st.subheader("💰 Position Sizing")

st.write(f"Allocation: **{int(pos_size*100)}%**")
st.write(f"Risk Level: **{risk_text}**")

# ================= CHART =================
st.subheader("📉 Market Chart")

fig = plot_chart(nifty, final)
if fig:
    st.plotly_chart(fig, use_container_width=True)

# ================= FINAL STATUS =================
st.subheader("📢 System Status")

if final == "BUY":
    st.success("🟢 BUY Signal Confirmed")

elif final == "SELL":
    st.error("🔴 SELL Signal Confirmed")

else:
    st.warning("🟡 NO TRADE (Filtered)")
