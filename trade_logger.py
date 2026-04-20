import pandas as pd
import os

FILE = "trade_log.csv"


# ================= SAVE TRADE =================
def log_trade(signal, price):
    data = {
        "time": pd.Timestamp.now(),
        "signal": signal,
        "entry_price": price,
        "exit_price": None,
        "result": "OPEN"
    }

    df = pd.DataFrame([data])

    if os.path.exists(FILE):
        df.to_csv(FILE, mode='a', header=False, index=False)
    else:
        df.to_csv(FILE, index=False)


# ================= LOAD =================
def load_trades():
    if os.path.exists(FILE):
        return pd.read_csv(FILE)
    return pd.DataFrame()


# ================= UPDATE RESULT =================
def update_results(current_price):
    df = load_trades()

    if df.empty:
        return df

    updated = False

    for i in range(len(df)):
        if df.loc[i, "result"] == "OPEN":
            entry = df.loc[i, "entry_price"]
            signal = df.loc[i, "signal"]

            if signal == "BUY":
                if current_price > entry:
                    df.loc[i, "result"] = "WIN"
                    df.loc[i, "exit_price"] = current_price
                    updated = True
                elif current_price < entry:
                    df.loc[i, "result"] = "LOSS"
                    df.loc[i, "exit_price"] = current_price
                    updated = True

            elif signal == "SELL":
                if current_price < entry:
                    df.loc[i, "result"] = "WIN"
                    df.loc[i, "exit_price"] = current_price
                    updated = True
                elif current_price > entry:
                    df.loc[i, "result"] = "LOSS"
                    df.loc[i, "exit_price"] = current_price
                    updated = True

    if updated:
        df.to_csv(FILE, index=False)

    return df


# ================= STRIKE RATE =================
def calculate_strike_rate(df):
    if df.empty:
        return 0

    closed = df[df["result"] != "OPEN"]

    if closed.empty:
        return 0

    wins = len(closed[closed["result"] == "WIN"])
    total = len(closed)

    return round((wins / total) * 100, 2)
