import pandas as pd


# ================= INDICATORS =================
def add_indicators(df):
    df["EMA_9"] = df["close"].ewm(span=9, adjust=False).mean()
    df["EMA_21"] = df["close"].ewm(span=21, adjust=False).mean()
    return df


# ================= SIGNAL =================
def generate_signal(df, mode="Balanced"):
    if df is None or len(df) < 25:
        return "NO DATA"

    last = df.iloc[-1]
    prev = df.iloc[-2]

    trend_up = last["EMA_9"] > last["EMA_21"]
    trend_down = last["EMA_9"] < last["EMA_21"]

    price_above = last["close"] > last["EMA_21"]
    price_below = last["close"] < last["EMA_21"]

    candle_green = last["close"] > last["open"]
    candle_red = last["close"] < last["open"]

    breakout = last["close"] > prev["high"]
    breakdown = last["close"] < prev["low"]

    # ================= MODES =================

    # ⚡ SCALPING MODE
    if mode == "Scalping":
        if trend_up:
            return "BUY"
        if trend_down:
            return "SELL"

    # ⚖️ BALANCED MODE
    elif mode == "Balanced":
        if trend_up and price_above and candle_green:
            if breakout:
                return "STRONG BUY"
            return "BUY"

        if trend_down and price_below and candle_red:
            if breakdown:
                return "STRONG SELL"
            return "SELL"

    # 🎯 STRICT MODE
    elif mode == "Strict":
        if trend_up and price_above and candle_green and breakout:
            return "STRONG BUY"

        if trend_down and price_below and candle_red and breakdown:
            return "STRONG SELL"

    return "WAIT"
