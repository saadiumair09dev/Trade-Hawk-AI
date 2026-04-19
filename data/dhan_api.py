import pandas as pd
import yfinance as yf
import streamlit as st

# ================= GET DATA =================
def get_data(security_id):
    try:
        symbol_map = {
            "13": "^NSEI",       # NIFTY
            "25": "^NSEBANK"    # BANKNIFTY
        }

        symbol = symbol_map.get(security_id, "^NSEI")

        df = yf.download(symbol, interval="5m", period="1d")

        if df is None or df.empty:
            st.error("No data from yfinance")
            return None

        df.reset_index(inplace=True)

        df.rename(columns={
            "Open": "Open",
            "High": "High",
            "Low": "Low",
            "Close": "Close",
            "Volume": "Volume"
        }, inplace=True)

        return df

    except Exception as e:
        st.error(f"Data error: {e}")
        return None
