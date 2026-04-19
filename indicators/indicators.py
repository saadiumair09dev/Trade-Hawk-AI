import pandas as pd

def add_indicators(df):
    try:
        # ========= CHECK =========
        if df is None or df.empty:
            print("Empty DF")
            return None

        # ========= FIX COLUMN NAMES =========
        df.columns = [str(c).strip() for c in df.columns]

        # handle yfinance multi-index
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # standardize
        rename_map = {}
        for col in df.columns:
            c = col.lower()
            if "open" in c:
                rename_map[col] = "Open"
            elif "high" in c:
                rename_map[col] = "High"
            elif "low" in c:
                rename_map[col] = "Low"
            elif "close" in c:
                rename_map[col] = "Close"
            elif "volume" in c:
                rename_map[col] = "Volume"

        df = df.rename(columns=rename_map)

        # ========= REQUIRED =========
        required = ["Close"]

        for col in required:
            if col not in df.columns:
                print("Missing:", col)
                return None

        # ========= EMA =========
        df["EMA_9"] = df["Close"].ewm(span=9).mean()
        df["EMA_21"] = df["Close"].ewm(span=21).mean()

        # ========= RSI =========
        delta = df["Close"].diff()

        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()

        rs = avg_gain / (avg_loss + 1e-9)
        df["RSI"] = 100 - (100 / (1 + rs))

        # ========= CLEAN =========
        df = df.fillna(0)

        return df

    except Exception as e:
        print("Indicator Error:", e)
        return None
