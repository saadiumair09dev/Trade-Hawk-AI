import requests
import pandas as pd
import streamlit as st
import yfinance as yf

from datetime import datetime
import pytz


BASE_URL = "https://api.dhan.co/v2/charts/intraday"


# ================= MARKET TIME =================
def is_market_open():

    ist = pytz.timezone(
        "Asia/Kolkata"
    )

    now = datetime.now(
        ist
    )

    if now.weekday() >= 5:

        return False

    start = now.replace(
        hour=9,
        minute=15,
        second=0
    )

    end = now.replace(
        hour=15,
        minute=30,
        second=0
    )

    return start <= now <= end


# ================= SYMBOL FIX =================
def normalize_symbol(symbol):

    if symbol == "RELIANCE":

        return "RELIANCE.NS"

    elif symbol == "HDFCBANK":

        return "HDFCBANK.NS"

    elif symbol == "^BANKNIFTY":

        return "^NSEBANK"

    return symbol


# ================= DHAN =================
def fetch_dhan(
    symbol,
    interval
):

    try:

        token = st.secrets[
            "dhan"
        ][
            "access_token"
        ]

        client_id = st.secrets[
            "dhan"
        ][
            "client_id"
        ]

        symbol_map = {

            "RELIANCE": {

                "securityId": "2885",
                "exchangeSegment": "NSE_EQ"
            },

            "HDFCBANK": {

                "securityId": "1333",
                "exchangeSegment": "NSE_EQ"
            }

        }

        if symbol not in symbol_map:

            return None

        interval_map = {

            "1m": "1",
            "5m": "5",
            "15m": "15",
            "1h": "60"

        }

        payload = {

            "securityId":
            symbol_map[
                symbol
            ][
                "securityId"
            ],

            "exchangeSegment":
            symbol_map[
                symbol
            ][
                "exchangeSegment"
            ],

            "instrument":
            "EQUITY",

            "interval":
            interval_map.get(
                interval,
                "5"
            ),

            "oi":
            False

        }

        headers = {

            "access-token":
            token,

            "client-id":
            client_id,

            "Content-Type":
            "application/json"

        }

        res = requests.post(
            BASE_URL,
            json=payload,
            headers=headers,
            timeout=8
        )

        if res.status_code != 200:

            return None

        data = res.json()

        if "data" not in data:

            return None

        raw = data[
            "data"
        ]

        df = pd.DataFrame({

            "datetime":
            raw.get(
                "timestamp",
                []
            ),

            "open":
            raw.get(
                "open",
                []
            ),

            "high":
            raw.get(
                "high",
                []
            ),

            "low":
            raw.get(
                "low",
                []
            ),

            "close":
            raw.get(
                "close",
                []
            ),

            "volume":
            raw.get(
                "volume",
                []
            )

        })

        if df.empty:

            return None

        df[
            "datetime"
        ] = pd.to_datetime(
            df[
                "datetime"
            ],
            errors="coerce"
        )

        df.dropna(
            inplace=True
        )

        df.set_index(
            "datetime",
            inplace=True
        )

        return df

    except:

        return None


# ================= YFINANCE =================
@st.cache_data(ttl=20)

def fetch_yfinance(
    symbol,
    interval
):

    try:

        symbol = normalize_symbol(
            symbol
        )

        period = "5d"

        if interval in [
            "15m",
            "1h"
        ]:

            period = "1mo"

        df = yf.download(

            tickers=symbol,

            interval=interval,

            period=period,

            progress=False

        )

        if df is None or df.empty:

            return None

        if isinstance(
            df.columns,
            pd.MultiIndex
        ):

            df.columns = [

                c[0].lower()

                for c in df.columns

            ]

        else:

            df.columns = [

                str(c).lower()

                for c in df.columns

            ]

        df.dropna(
            inplace=True
        )

        return df

    except:

        return None


# ================= STOOQ =================
@st.cache_data(ttl=20)

def fetch_stooq(
    symbol
):

    try:

        symbol = normalize_symbol(
            symbol
        )

        url = (
            "https://stooq.com/q/d/l/"
            f"?s={symbol.lower()}"
            "&i=d"
        )

        df = pd.read_csv(
            url
        )

        if df.empty:

            return None

        df.columns = [

            c.lower()

            for c in df.columns

        ]

        df[
            "date"
        ] = pd.to_datetime(
            df[
                "date"
            ]
        )

        df.set_index(
            "date",
            inplace=True
        )

        return df

    except:

        return None


# ================= MAIN =================
def get_data(
    symbol,
    interval
):

    market_open = is_market_open()

    if market_open:

        st.success(
            "🟢 Market Open"
        )

    else:

        st.warning(
            "🌙 Market Closed"
        )

    # index
    if symbol.startswith("^"):

        df = fetch_yfinance(
            symbol,
            interval
        )

        if df is not None:

            st.info(
                "Index data: Yahoo"
            )

            return df

    # dhan
    if market_open:

        df = fetch_dhan(
            symbol,
            interval
        )

        if df is not None:

            st.success(
                "⚡ Dhan Live"
            )

            return df

    # yahoo
    df = fetch_yfinance(
        symbol,
        interval
    )

    if df is not None:

        st.info(
            "📊 Yahoo Source"
        )

        return df

    # stooq
    df = fetch_stooq(
        symbol
    )

    if df is not None:

        st.info(
            "🌐 Stooq Source"
        )

        return df

    st.error(
        "❌ No source available"
    )

    return None
