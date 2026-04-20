import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier

# ================= TRAIN MODEL =================
def train_model(df):
    df = df.copy()

    df["target"] = np.where(df["close"].shift(-1) > df["close"], 1, 0)

    df = df.dropna()

    features = ["close", "EMA_9", "EMA_21", "RSI"]

    X = df[features]
    y = df["target"]

    model = RandomForestClassifier(n_estimators=50)
    model.fit(X, y)

    return model


# ================= SIGNAL =================
def predict_signal(model, df):
    try:
        last = df[["close", "EMA_9", "EMA_21", "RSI"]].dropna().iloc[-1:]
        pred = model.predict(last)[0]

        if pred == 1:
            return "BUY"
        else:
            return "SELL"

    except:
        return "WAIT"


# ================= NEXT 3 CANDLE =================
def predict_next_3(model, df):
    try:
        features = df[["close", "EMA_9", "EMA_21", "RSI"]].dropna()

        if len(features) < 10:
            return ["NA", "NA", "NA"]

        last = features.iloc[-1:].values

        preds = []

        for _ in range(3):
            pred = model.predict(last)[0]

            if pred == 1:
                preds.append("UP")
            else:
                preds.append("DOWN")

        return preds

    except:
        return ["ERR", "ERR", "ERR"]


# ================= ACCURACY =================
def calculate_accuracy(df):
    try:
        df = df.copy()

        df["target"] = np.where(df["close"].shift(-1) > df["close"], 1, 0)
        df = df.dropna()

        features = ["close", "EMA_9", "EMA_21", "RSI"]

        X = df[features]
        y = df["target"]

        model = RandomForestClassifier(n_estimators=50)
        model.fit(X, y)

        acc = model.score(X, y)

        return round(acc * 100, 2)

    except:
        return 0
