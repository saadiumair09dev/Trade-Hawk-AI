import pandas as pd

def add_indicators(df):
    try:
        df = df.copy()

        # Basic validation
        if df is None or df.empty:
            return df

        # Ensure Close column exists
        if "close" not in df.columns:
            return df

        # EMA calculations
        df["EMA_9"] = df["close"].ewm(span=9, adjust=False).mean()
        df["EMA_21"] = df["close"].ewm(span=21, adjust=False).mean()

        return df

    except Exception as e:
        print("Indicator Error:", e)
        return df
