import pandas as pd
import streamlit as st


def fix_columns(df):
    try:
        # अगर multi-index है तो flatten करो
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0].lower() for col in df.columns]
        else:
            df.columns = [str(col).lower() for col in df.columns]

        return df

    except Exception as e:
        st.error(f"Column
