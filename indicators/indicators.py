import pandas as pd

def add_indicators(df):
    try:
        if df is None or df.empty:
            return None

        # column fix
        df.columns = [c.capitalize() for c in df.columns]

        # required columns check
        if "Close" not in df.columns:
            return None

        # ================= EMA =================
        df["EMA_9"] = df["Close"].ewm(span=9).mean()
        df["EMA_21"] = df["Close"].ewm(span=21).mean()

        # ================= RSI =================
        delta = df["Close"].diff()

        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()

        rs = avg_gain / avg_loss
        df["RSI"] = 100 - (100 / (1 + rs))

        # ================= CLEAN =================
        df.fillna(0, inplace=True)

        return df

    except Exception as e:
        print("Indicator Error:", e)
        return None
