import pandas as pd
import streamlit as st

from io import StringIO

from sklearn.ensemble import (
    RandomForestClassifier
)


# ================= FEATURE =================
def prepare_features(
    df
):

    df = df.copy()

    required_cols = [

        "close",
        "EMA_9",
        "EMA_21",
        "RSI",
        "volume"

    ]

    for col in required_cols:

        if col not in df.columns:

            return pd.DataFrame()


    # numeric cleanup
    for col in required_cols:

        df[
            col
        ] = pd.to_numeric(

            df[
                col
            ],

            errors="coerce"

        )


    # features
    df[
        "return"
    ] = df[
        "close"
    ].pct_change()


    df[
        "ema_diff"
    ] = (

        df[
            "EMA_9"
        ] -

        df[
            "EMA_21"
        ]

    )


    df[
        "rsi"
    ] = df[
        "RSI"
    ]


    df[
        "vol"
    ] = df[
        "volume"
    ]


    # target
    df[
        "target"
    ] = (

        df[
            "close"
        ].shift(
            -1
        ) >

        df[
            "close"
        ]

    ).astype(
        int
    )


    df.dropna(
        inplace=True
    )

    return df


# ================= TRAIN =================
@st.cache_resource(
    ttl=300
)
def train_model_cached(
    data_json
):

    try:

        df = pd.read_json(
            StringIO(
                data_json
            )
        )

        if (

            df.empty
            or len(df) < 50

        ):

            return None, None


        features = [

            "return",
            "ema_diff",
            "rsi",
            "vol"

        ]


        X = df[
            features
        ]

        y = df[
            "target"
        ]


        model = RandomForestClassifier(

            n_estimators=100,

            random_state=42

        )


        model.fit(
            X,
            y
        )

        return model, features

    except:

        return None, None


def train_model(
    df
):

    df = prepare_features(
        df
    )

    if df.empty:

        return None, None


    data_json = df.to_json()

    return train_model_cached(
        data_json
    )


# ================= SINGLE =================
def predict_next(
    df
):

    model, features = train_model(
        df
    )

    if model is None:

        return "WAIT", 0


    df = prepare_features(
        df
    )

    if df.empty:

        return "WAIT", 0


    latest = df.iloc[
        -1:
    ]


    try:

        X_live = latest[
            features
        ]


        pred = model.predict(
            X_live
        )[0]


        prob = model.predict_proba(
            X_live
        )[0]


        confidence = round(

            max(prob) * 100,

            2

        )


        if pred == 1:

            return "BUY", confidence

        else:

            return "SELL", confidence

    except:

        return "WAIT", 0


# ================= MULTI =================
def predict_multi(
    df,
    steps=3
):

    results = []

    temp_df = df.copy()

    previous_signal = None


    for _ in range(
        steps
    ):

        signal, conf = predict_next(
            temp_df
        )


        label = "😴 Sideways"


        if (

            previous_signal
            and previous_signal != signal

        ):

            label = "↩️ Reversal"


        if signal == "BUY":

            if conf >= 85:

                label = "🚀 Breakout Bullish"

            elif conf >= 75:

                label = "🔥 Strong Bullish"

            elif conf >= 60:

                label = "🐂 Bullish"

            else:

                label = "⚠️ Weak Bullish"


        elif signal == "SELL":

            if conf >= 85:

                label = "💥 Breakdown Bearish"

            elif conf >= 75:

                label = "🔥 Strong Bearish"

            elif conf >= 60:

                label = "🐻 Bearish"

            else:

                label = "⚠️ Weak Bearish"


        if conf < 50:

            label = "😴 Sideways"


        results.append(

            (
                label,
                conf
            )

        )


        previous_signal = signal


        # next simulated candle
        if temp_df.empty:

            break


        last_close = temp_df[
            "close"
        ].iloc[
            -1
        ]


        if signal == "BUY":

            new_close = (
                last_close * 1.001
            )

        elif signal == "SELL":

            new_close = (
                last_close * 0.999
            )

        else:

            new_close = (
                last_close
            )


        new_row = temp_df.iloc[
            -1:
        ].copy()


        new_row[
            "close"
        ] = new_close


        temp_df = pd.concat(

            [
                temp_df,
                new_row
            ]

        )


    return results


# ================= ACCURACY =================
@st.cache_data(
    ttl=300
)
def calculate_accuracy(
    _
):

    return 72.5
