def base_signal(df):
    """
    Generate base BUY / SELL / NO signal
    based on EMA + RSI + VWAP
    """

    # Safety check
    if df is None or df.empty or len(df) < 20:
        return "NO"

    last = df.iloc[-1]

    # Extract values safely
    close = last.get("Close", 0)
    ema = last.get("EMA20", 0)
    rsi = last.get("RSI", 50)
    vwap = last.get("VWAP", close)

    # ================= BUY CONDITION =================
    if close > ema and close > vwap and rsi > 60:
        return "BUY"

    # ================= SELL CONDITION =================
    elif close < ema and close < vwap and rsi < 40:
        return "SELL"

    # ================= NO TRADE =================
    return "NO"
