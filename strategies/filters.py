def crash_detection(df):
    """
    Detect sudden crash / spike using last 5 candles
    """
    if df is None or len(df) < 5:
        return False

    move = df["Close"].iloc[-1] - df["Close"].iloc[-5]

    # threshold tune कर सकते हो (index vs stock अलग हो सकता है)
    return abs(move) > 80


def trap_detection(df):
    """
    Detect trap candle (fake breakout / indecision)
    Small body + large wick
    """
    if df is None or len(df) < 1:
        return False

    last = df.iloc[-1]

    body = abs(last["Close"] - last["Open"])
    wick = last["High"] - last["Low"]

    # avoid divide by zero
    if wick == 0:
        return False

    # small body relative to full range = trap/indecision
    return body < (wick * 0.3)


def gap_detection(df):
    """
    Detect gap up / gap down
    """
    if df is None or len(df) < 2:
        return False

    gap = abs(df["Open"].iloc[-1] - df["Close"].iloc[-2])

    return gap > 50
