import os
import pandas as pd
from datetime import datetime

LOG_FILE = "trade_log.csv"


# ================= INIT =================
def _create_if_missing():

    if not os.path.exists(LOG_FILE):

        df = pd.DataFrame(
            columns=[
                "time",
                "signal",
                "entry",
                "sl",
                "tp",
                "exit",
                "result"
            ]
        )

        df.to_csv(
            LOG_FILE,
            index=False
        )


# ================= LOAD =================
def load_trades():

    _create_if_missing()

    try:

        df = pd.read_csv(
            LOG_FILE
        )

        return df

    except:

        return pd.DataFrame()


# ================= LOG =================
def log_trade(signal, entry):

    _create_if_missing()

    df = load_trades()

    # duplicate block
    if not df.empty:

        last = df.iloc[-1]

        if (
            last["signal"] == signal
            and last["result"] == "OPEN"
        ):

            return

    # SL TP
    if signal == "BUY":

        sl = round(
            entry * 0.995,
            2
        )

        tp = round(
            entry * 1.01,
            2
        )

    else:

        sl = round(
            entry * 1.005,
            2
        )

        tp = round(
            entry * 0.99,
            2
        )

    new_trade = pd.DataFrame(
        [
            {
                "time": datetime.now(),
                "signal": signal,
                "entry": entry,
                "sl": sl,
                "tp": tp,
                "exit": None,
                "result": "OPEN"
            }
        ]
    )

    df = pd.concat(
        [df, new_trade]
    )

    df.to_csv(
        LOG_FILE,
        index=False
    )


# ================= UPDATE =================
def update_results(current_price):

    df = load_trades()

    if df.empty:
        return df

    for i in range(len(df)):

        row = df.iloc[i]

        if row["result"] != "OPEN":
            continue

        signal = row["signal"]

        entry = row["entry"]

        sl = row["sl"]

        tp = row["tp"]

        if signal == "BUY":

            if current_price >= tp:

                df.at[
                    i,
                    "result"
                ] = "WIN"

                df.at[
                    i,
                    "exit"
                ] = current_price

            elif current_price <= sl:

                df.at[
                    i,
                    "result"
                ] = "LOSS"

                df.at[
                    i,
                    "exit"
                ] = current_price

        elif signal == "SELL":

            if current_price <= tp:

                df.at[
                    i,
                    "result"
                ] = "WIN"

                df.at[
                    i,
                    "exit"
                ] = current_price

            elif current_price >= sl:

                df.at[
                    i,
                    "result"
                ] = "LOSS"

                df.at[
                    i,
                    "exit"
                ] = current_price

    df.to_csv(
        LOG_FILE,
        index=False
    )

    return df


# ================= STRIKE =================
# ================= STRIKE =================
def calculate_strike_rate(df):

    # None safety
    if df is None:

        return 0

    # empty safety
    if df.empty:

        return 0

    closed = df[
        df["result"].isin(
            [
                "WIN",
                "LOSS"
            ]
        )
    ]

    if closed.empty:

        return 0

    wins = len(
        closed[
            closed["result"] == "WIN"
        ]
    )

    total = len(
        closed
    )

    if total == 0:

        return 0

    return round(
        (wins / total) * 100,
        2
    )
