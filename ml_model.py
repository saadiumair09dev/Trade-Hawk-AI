import pandas as pd
from sklearn.ensemble import RandomForestClassifier


# ================= FEATURE BUILD =================
def prepare_features(df):
    df = df.copy()

    df["return"] = df["close"].pct_change()
    df["ema_diff"] = df["EMA_9"] - df["EMA_21"]
    df["rsi"] = df["RSI"]
    df["vol"] = df["volume"]

    df.dropna(inplace=True)

    # TARGET (next candle direction)
    df["target"] = (df["close"].shift(-1) > df["close"]).astype(int)

    return df


# ================= TRAIN MODEL =================
def train_model(df):
    df = prepare_features(df)

    features = ["return", "ema_diff", "rsi", "vol"]

    X = df[features]
    y = df["target"]

    model = RandomForestClassifier(n_estimators=100)
    model.fit(X, y)

    return model, features


# ================= PREDICT =================
def predict_next(df):
    model, features = train_model(df)

    latest = df.iloc[-1:]

    X_live = latest[features]

    pred = model.predict(X_live)[0]
    prob = model.predict_proba(X_live)[0]

    confidence = round(max(prob) * 100, 2)

    if pred == 1:
        return "BUY", confidence
    else:
        return "SELL", confidence
