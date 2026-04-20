import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestClassifier

# ================= FEATURES =================
def prepare_features(df):
    df = df.copy()

    df["returns"] = df["close"].pct_change()
    df["ma_5"] = df["close"].rolling(5).mean()
    df["ma_10"] = df["close"].rolling(10).mean()
    df["volatility"] = df["returns"].rolling(5).std()

    df = df.dropna()
    return df


# ================= TRAIN =================
def train_model(df):
    df = prepare_features(df)

    if df is None or len(df) < 30:
        return None

    df["target"] = np.where(df["close"].shift(-1) > df["close"], 1, 0)

    features = ["returns", "ma_5", "ma_10", "volatility"]

    X = df[features]
    y = df["target"]

    model = RandomForestClassifier(n_estimators=100)
    model.fit(X, y)

    return model


# ================= SINGLE PREDICTION =================
def predict_signal(model, df):
    try:
        df = prepare_features(df)

        features = ["returns", "ma_5", "ma_10", "volatility"]

        last = df[features].iloc[-1:]
        pred = model.predict(last)[0]

        return "BUY" if pred == 1 else "SELL"
    except:
        return "HOLD"


# ================= 3 CANDLE PREDICTION =================
def predict_next_3(model, df):
    try:
        df = prepare_features(df)

        features = ["returns", "ma_5", "ma_10", "volatility"]

        last_price = df["close"].iloc[-1]
        last_row = df.iloc[-1:].copy()

        predictions = []

        for i in range(3):
            X = last_row[features]
            pred = model.predict(X)[0]

            direction = "UP" if pred == 1 else "DOWN"

            # simple price projection
            move = last_price * 0.002   # ~0.2% move

            if direction == "UP":
                next_price = last_price + move
            else:
                next_price = last_price - move

            predictions.append({
                "candle": i+1,
                "direction": direction,
                "expected_price": round(next_price, 2)
            })

            # update for next step
            last_price = next_price
            last_row["close"] = next_price

        return predictions

    except:
        return []
