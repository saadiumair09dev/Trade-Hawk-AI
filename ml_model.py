import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score


# ================= FEATURE ENGINEERING =================
def prepare_features(df):
    df = df.copy()

    # Basic indicators
    df["returns"] = df["close"].pct_change()
    df["ma_5"] = df["close"].rolling(5).mean()
    df["ma_10"] = df["close"].rolling(10).mean()
    df["volatility"] = df["returns"].rolling(5).std()

    # Target (next candle up/down)
    df["target"] = np.where(df["close"].shift(-1) > df["close"], 1, 0)

    # Drop NaN rows
    df = df.dropna()

    return df


# ================= TRAIN MODEL =================
def train_model(df):
    try:
        df = prepare_features(df)

        # ❌ IMPORTANT FIX: empty data check
        if df is None or df.empty or len(df) < 20:
            return None, None

        features = ["returns", "ma_5", "ma_10", "volatility"]

        X = df[features]
        y = df["target"]

        # ❌ IMPORTANT FIX: ensure no NaN
        if X.isnull().values.any() or y.isnull().values.any():
            return None, None

        # Train/Test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, shuffle=False
        )

        model = RandomForestClassifier(n_estimators=50)
        model.fit(X_train, y_train)

        return model, (X_test, y_test)

    except Exception as e:
        print("ML Train Error:", e)
        return None, None


# ================= PREDICT =================
def predict_signal(model, df):
    try:
        df = prepare_features(df)

        if model is None or df is None or df.empty:
            return "HOLD"

        features = ["returns", "ma_5", "ma_10", "volatility"]

        last_row = df[features].iloc[-1:]

        if last_row.isnull().values.any():
            return "HOLD"

        pred = model.predict(last_row)[0]

        return "BUY" if pred == 1 else "SELL"

    except:
        return "HOLD"


# ================= ACCURACY =================
def calculate_accuracy(df):
    try:
        model, test_data = train_model(df)

        if model is None or test_data is None:
            return 0

        X_test, y_test = test_data

        preds = model.predict(X_test)

        acc = accuracy_score(y_test, preds)

        return round(acc * 100, 2)

    except:
        return 0
