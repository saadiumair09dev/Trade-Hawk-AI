import pandas as pd


# ================= INDICATORS =================
def add_indicators(df):
    df["EMA_9"] = df["close"].ewm(span=9, adjust=False).mean()
    df["EMA_21"] = df["close"].ewm(span=21, adjust=False).mean()

    # RSI
    delta = df["close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))

    # Volume avg
    if "volume" in df.columns:
        df["vol_avg"] = df["volume"].rolling(20).mean()
    else:
        df["volume"] = 0
        df["vol_avg"] = 0

    return df


# ================= AI ENGINE =================
def ai_decision(df):
    last = df.iloc[-1]
    prev = df.iloc[-2]

    score = 0
    reasons = []

    # Trend
    if last["EMA_9"] > last["EMA_21"]:
        score += 2
        reasons.append("Trend Up (EMA9 > EMA21)")
    else:
        score -= 2
        reasons.append("Trend Down (EMA9 < EMA21)")

    # Price position
    if last["close"] > last["EMA_21"]:
        score += 1
        reasons.append("Price Above EMA21")
    else:
        score -= 1
        reasons.append("Price Below EMA21")

    # RSI
    if last["RSI"] > 60:
        score += 1
        reasons.append("RSI Strong (>60)")
    elif last["RSI"] < 40:
        score -= 1
        reasons.append("RSI Weak (<40)")

    # Breakout
    if last["close"] > prev["high"]:
        score += 1
        reasons.append("Breakout")
    elif last["close"] < prev["low"]:
        score -= 1
        reasons.append("Breakdown")

    # Volume
    if last["volume"] > last["vol_avg"]:
        score += 1
        reasons.append("High Volume")

    # Final decision
    if score >= 3:
        signal = "BUY"
    elif score <= -3:
        signal = "SELL"
    else:
        signal = "WAIT"

    confidence = min(abs(score) * 20, 100)

    return signal, confidence, reasons


# ================= MAIN SIGNAL =================
def generate_signal(df, mode="Balanced"):
    if df is None or len(df) < 30:
        return "NO DATA", 0, []

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

    # ================= AI MODE =================
    if mode == "AI Mode":
        return ai_decision(df)

    # ================= HYBRID =================
    if mode == "Hybrid":
        if trend_up and breakout:
            return "STRONG BUY", 80, ["Trend + Breakout"]
        if trend_down and breakdown:
            return "STRONG SELL", 80, ["Trend + Breakdown"]

    # ================= BALANCED =================
    if mode == "Balanced":
        if trend_up and price_above and candle_green:
            return "BUY", 60, ["Trend + Price + Candle"]
        if trend_down and price_below and candle_red:
            return "SELL", 60, ["Trend + Price + Candle"]

    # ================= SCALPING =================
    if mode == "Scalping":
        if trend_up:
            return "BUY", 50, ["Fast Trend"]
        if trend_down:
            return "SELL", 50, ["Fast Trend"]

    # ================= STRICT =================
    if mode == "Strict":
        if trend_up and breakout:
            return "STRONG BUY", 85, ["Strict Breakout"]
        if trend_down and breakdown:
            return "STRONG SELL", 85, ["Strict Breakdown"]

    return "WAIT", 0, []
