import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score


# ================= FEATURE =================
def prepare_features(df):
    df = df.copy()

    df["returns"] = df["close"].pct_change()
    df["ma_5"] = df["close"].rolling(5).mean()
    df["ma_10"] = df["close"].rolling(10).mean()
    df["volatility"] = df["returns"].rolling(5).std()

    df["target"] = np.where(df["close"].shift(-1) > df["close"], 1, 0)

    df = df.dropna()

    return df


# ================= TRAIN =================
def train_model(df):
    df = prepare_features(df)

    if df is None or df.empty or len(df) < 20:
        return None

    features = ["returns", "ma_5", "ma_10", "volatility"]

    X = df[features]
    y = df["target"]

    if X.isnull().values.any():
        return None

    model = RandomForestClassifier(n_estimators=50)
    model.fit(X, y)

    return model


# ================= PREDICT =================
def predict_signal(model, df):
    try:
        df = prepare_features(df)

        if model is None or df.empty:
            return "HOLD"

        features = ["returns", "ma_5", "ma_10", "volatility"]

        last_row = df[features].iloc[-1:]

        pred = model.predict(last_row)[0]

        return "BUY" if pred == 1 else "SELL"

    except:
        return "HOLD"


# ================= ACCURACY =================
def calculate_accuracy(df):
    try:
        df = prepare_features(df)

        if df is None or len(df) < 20:
            return 0

        features = ["returns", "ma_5", "ma_10", "volatility"]

        X = df[features]
        y = df["target"]

        model = RandomForestClassifier(n_estimators=50)
        model.fit(X, y)

        preds = model.predict(X)

        acc = accuracy_score(y, preds) * 100

        return acc

    except:
        return 0
