import requests
import pandas as pd
import streamlit as st
import yfinance as yf


# -------------------------------
# CONFIG
# -------------------------------
BASE_URL = "https://api.dhan.co/v2/charts/intraday"


# -------------------------------
# MAIN FUNCTION
# -------------------------------
def get_data(symbol, interval):
    try:
        # =========================
        # TRY DHAN API FIRST
        # =========================
        token = None

        # Safe secret access
        if "token" in st.secrets:
            token = st.secrets["token"]

        if token:
            headers = {
                "access-token": token,
                "Content-Type": "application/json"
            }

            payload = {
                "securityId": "13",        # NIFTY
                "exchangeSegment": "NSE_EQ",
                "instrument": "INDEX",
                "interval": interval,
                "fromDate": "2024-01-01",
                "toDate": "2024-12-31"
            }

            res = requests.post(BASE_URL, json=payload, headers=headers)

            if res.status_code == 200:
                data = res.json()

                if "data" in data:
                    df = pd.DataFrame(data["data"])

                    # Standardize columns
                    df.rename(columns={
                        "open": "open",
                        "high": "high",
                        "low": "low",
                        "close": "close"
                    }, inplace=True)

                    return df

                else:
                    st.warning("⚠️ Dhan API: No data field")

            else:
                st.warning(f"⚠️ Dhan API Error {res.status_code}")

        else:
            st.warning("⚠️ No Dhan token found → Using fallback")

        # =========================
        # FALLBACK: YFINANCE
        # =========================
        df = yf.download(symbol, interval=interval, period="1d")

        if df is None or df.empty:
            return None

        df.reset_index(inplace=True)

        # Rename columns properly
        df.rename(columns={
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close"
        }, inplace=True)

        return df

    except Exception as e:
        st.error(f"❌ Data fetch error: {e}")
        return None
