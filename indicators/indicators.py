import pandas as pd
import streamlit as st


def fix_columns(df):
    # Multi-index fix
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0].lower() for col in df.columns]
    else:
        df.columns = [str(col).lower() for col in df.columns]

    return df


def calculate_indicators(df):
    try:
        df = fix_columns(df)

        # Check required column
        if "close" not in df.columns:
            st.error("❌ Missing 'close' column")
            return None

        # EMA calculations
        df["ema_9"] = df["close"].ewm(span=9).mean()
        df["ema_21"] = df["close"].ewm(span=21).mean()

        return df

    except Exception as e:
        st.error(f"❌ Indicator error: {e}")
        return None
