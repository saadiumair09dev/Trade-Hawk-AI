import pandas as pd

# ================= INDICATORS =================
def add_indicators(df):
    df["ema_9"] = df["close"].ewm(span=9).mean()
    df["ema_21"] = df["close"].ewm(span=21).mean()
    return df


# ================= SIGNAL =================
def generate_signal(df):
    if len(df) < 2:
        return "HOLD"

    last = df.iloc[-1]
    prev = df.iloc[-2]

    # EMA crossover
    if prev["ema_9"] < prev["ema_21"] and last["ema_9"] > last["ema_21"]:
        return "BUY"

    elif prev["ema_9"] > prev["ema_21"] and last["ema_9"] < last["ema_21"]:
        return "SELL"

    return "HOLD"
