import os
import pandas as pd

from datetime import datetime


LOG_FILE = "trade_log.csv"


# ================= INIT =================
def _create_if_missing():

    if not os.path.exists(
        LOG_FILE
    ):

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

        if df is None:

            return pd.DataFrame()

        return df

    except:

        return pd.DataFrame()


# ================= LOG =================
def log_trade(
    signal,
    entry
):

    if signal not in [
        "BUY",
        "SELL"
    ]:

        return

    _create_if_missing()

    df = load_trades()

    # Duplicate protection
    if not df.empty:

        open_trades = df[
            df["result"] == "OPEN"
        ]

        if not open_trades.empty:

            latest = open_trades.iloc[-1]

            same_signal = (
                latest["signal"] == signal
            )

            same_price = abs(

                float(
                    latest["entry"]
                ) - float(
                    entry
                )

            ) < 0.2

            if same_signal and same_price:

                return


    # SL / TP
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

                "time":
                datetime.now(),

                "signal":
                signal,

                "entry":
                entry,

                "sl":
                sl,

                "tp":
                tp,

                "exit":
                None,

                "result":
                "OPEN"

            }

        ]

    )


    df = pd.concat(

        [
            df,
            new_trade
        ],

        ignore_index=True

    )


    df.to_csv(

        LOG_FILE,

        index=False

    )


# ================= UPDATE =================
def update_results(
    current_price
):

    df = load_trades()

    if df.empty:

        return df


    for i in range(
        len(df)
    ):

        row = df.iloc[i]

        if row[
            "result"
        ] != "OPEN":

            continue


        signal = row[
            "signal"
        ]

        sl = float(
            row["sl"]
        )

        tp = float(
            row["tp"]
        )


        # BUY
        if signal == "BUY":

            if current_price >= tp:

                df.at[
                    i,
                    "exit"
                ] = current_price

                df.at[
                    i,
                    "result"
                ] = "WIN"


            elif current_price <= sl:

                df.at[
                    i,
                    "exit"
                ] = current_price

                df.at[
                    i,
                    "result"
                ] = "LOSS"


        # SELL
        elif signal == "SELL":

            if current_price <= tp:

                df.at[
                    i,
                    "exit"
                ] = current_price

                df.at[
                    i,
                    "result"
                ] = "WIN"


            elif current_price >= sl:

                df.at[
                    i,
                    "exit"
                ] = current_price

                df.at[
                    i,
                    "result"
                ] = "LOSS"


    df.to_csv(

        LOG_FILE,

        index=False

    )

    return df


# ================= STRIKE =================
def calculate_strike_rate(
    df
):

    if df is None:

        return 0

    if df.empty:

        return 0


    closed = df[

        df[
            "result"
        ].isin(

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

            closed[
                "result"
            ] == "WIN"

        ]

    )


    total = len(
        closed
    )


    if total == 0:

        return 0


    return round(

        (
            wins / total
        ) * 100,

        2

    )
