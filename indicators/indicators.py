import pandas as pd

def add_indicators(df):
    """
    Add EMA, RSI, VWAP indicators
    """

    # Safety check
    if df is None or df.empty:
        return df

    df = df.copy()

    # ================= EMA =================
    df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()

    # ================= RSI =================
    delta = df["Close"].diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()

    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))

    # ================= VWAP =================
    if "Volume" in df.columns:
        df["VWAP"] = (df["Close"] * df["Volume"]).cumsum() / df["Volume"].cumsum()
    else:
        df["VWAP"] = df["Close"]

    # ================= CLEAN =================
    df = df.dropna()

    return df
