import pandas as pd
import os

FILE = "trade_log.csv"


def log_trade(signal, price):
    data = {
        "time": pd.Timestamp.now(),
        "signal": signal,
        "price": price
    }

    df = pd.DataFrame([data])

    if os.path.exists(FILE):
        df.to_csv(FILE, mode='a', header=False, index=False)
    else:
        df.to_csv(FILE, index=False)


def load_trades():
    if os.path.exists(FILE):
        return pd.read_csv(FILE)
    return pd.DataFrame()


def calculate_win_rate(df, current_price):
    if df.empty:
        return 0

    correct = 0
    total = len(df)

    for _, row in df.iterrows():
        if row["signal"] == "BUY" and current_price > row["price"]:
            correct += 1
        elif row["signal"] == "SELL" and current_price < row["price"]:
            correct += 1

    return round((correct / total) * 100, 2)
