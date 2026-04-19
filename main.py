import streamlit as st

from data.dhan_api import get_data
from indicators.indicators import add_indicators
from strategies.signal_engine import base_signal
from strategies.filters import crash_detection, trap_detection
from strategies.correlation import correlation
from ai.ai_model import train_model, predict
from risk.position import position_size
from ui.chart import plot_chart
from config import SYMBOLS

st.title("🦅 Trade Hawk AI PRO (Modular)")

# DATA
n = add_indicators(get_data(SYMBOLS["NIFTY"]))
b = add_indicators(get_data(SYMBOLS["BANKNIFTY"]))
f = add_indicators(get_data(SYMBOLS["FINNIFTY"]))

# SIGNAL
base = base_signal(n)
corr = correlation(n,b,f)

final = corr if base == corr else "NO"

# FILTERS
if crash_detection(n) or trap_detection(n):
    final = "NO"

# AI
model = train_model(n)
pred, conf = predict(n, model)

if final == "BUY" and pred == "DOWN":
    final = "NO"

size = position_size(conf)

# UI
st.write("Final Signal:", final)
st.write("AI:", pred, conf)
st.write("Position:", size)

# CHART
st.plotly_chart(plot_chart(n))
