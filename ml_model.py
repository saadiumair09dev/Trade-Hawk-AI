import pandas as pd
from sklearn.ensemble import RandomForestClassifier

# ================= FEATURE =================
def prepare_features(df):
    df = df.copy()

    df["return"] = df["close"].pct_change()
    df["ema_diff"] = df["EMA_9"] - df["EMA_21"]
    df["rsi"] = df["RSI"]
    df["vol"] = df["volume"]

    df.dropna(inplace=True)

    df["target"] = (df["close"].shift(-1) > df["close"]).astype(int)

    return df


# ================= TRAIN =================
def train_model(df):
    df = prepare_features(df)

    features = ["return", "ema_diff", "rsi", "vol"]

    X = df[features]
    y = df["target"]

    model = RandomForestClassifier(n_estimators=120)
    model.fit(X, y)

    return model, features


# ================= SINGLE PRED =================
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


# ================= MULTI CANDLE =================
def predict_multi(df, steps=3):
    results = []
    temp_df = df.copy()

    for i in range(steps):
        signal, conf = predict_next(temp_df)

        results.append((signal, conf))

        # simulate next candle
        last_close = temp_df["close"].iloc[-1]
        if signal == "BUY":
            new_close = last_close * (1 + 0.001)
        else:
            new_close = last_close * (1 - 0.001)

        new_row = temp_df.iloc[-1:].copy()
        new_row["close"] = new_close

        temp_df = pd.concat([temp_df, new_row])

    return results


# ================= ACCURACY =================
def calculate_accuracy(df):
    df = prepare_features(df)

    correct = 0
    total = 0

    for i in range(len(df)-1):
        sub_df = df.iloc[:i+1]

        model, features = train_model(sub_df)

        X = sub_df.iloc[-1:][features]
        pred = model.predict(X)[0]

        actual = sub_df["target"].iloc[-1]

        if pred == actual:
            correct += 1

        total += 1

    if total == 0:
        return 0

    return round((correct / total) * 100, 2)
