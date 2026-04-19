import pandas as pd

def add_indicators(df):
    try:
        # ================= SAFETY =================
        if df is None or df.empty:
            print("DataFrame empty")
            return None

        # normalize column names
        df.columns = [str(c).strip().capitalize() for c in df.columns]

        # required columns check
        required = ["Open", "High", "Low", "Close"]
        for col in required:
            if col not in df.columns:
                print(f"Missing column: {col}")
                return None

        # ================= EMA =================
        df["EMA_9"] = df["Close"].ewm(span=9, adjust=False).mean()
        df["EMA_21"] = df["Close"].ewm(span=21, adjust=False).mean()

        # ================= RSI =================
        delta = df["Close"].diff()

        gain = delta.copy()
        loss = delta.copy()

        gain[gain < 0] = 0
        loss[loss > 0] = 0
        loss = abs(loss)

        avg_gain = gain.rolling(window=14, min_periods=1).mean()
        avg_loss = loss.rolling(window=14, min_periods=1).mean()

        rs = avg_gain / (avg_loss + 1e-9)
        df["Rsi"] = 100 - (100 / (1 + rs))

        # ================= VWAP =================
        df["Vwap"] = (df["Close"] * df.get("Volume", 1)).cumsum() / (df.get("Volume", 1).cumsum())

        # ================= CLEAN =================
        df = df.fillna(0)

        return df

    except Exception as e:
        print("Indicator Error:", e)
        return None
