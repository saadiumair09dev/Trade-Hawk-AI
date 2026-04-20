import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
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


# ================= SINGLE
