def get_direction(df):
    """
    Determine short-term direction (last 5 candles)
    """
    if df is None or len(df) < 5:
        return "NONE"

    if df["Close"].iloc[-1] > df["Close"].iloc[-5]:
        return "UP"
    else:
        return "DOWN"


def correlation(nifty_df, bank_df, fin_df):
    """
    Multi-asset confirmation using NIFTY, BANKNIFTY, FINNIFTY
    """

    n_dir = get_direction(nifty_df)
    b_dir = get_direction(bank_df)
    f_dir = get_direction(fin_df)

    directions = [n_dir, b_dir, f_dir]

    # ================= BUY CONFIRM =================
    if directions.count("UP") >= 2:
        return "BUY"

    # ================= SELL CONFIRM =================
    elif directions.count("DOWN") >= 2:
        return "SELL"

    # ================= NO TRADE =================
    return "NO"
