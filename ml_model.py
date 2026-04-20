import pandas as pd
from sklearn.ensemble import RandomForestClassifier


# ================= FEATURE =================
def prepare_features(df):
    df = df.copy()

    # Required columns check
    required_cols = ["close", "EMA_9", "EMA_21", "RSI", "volume"]
    for col in required_cols:
        if col not in df.columns:
            return pd.DataFrame()

    df["return"] = df["close"].pct_change()
    df["ema_diff"] = df["EMA_9"] - df["EMA_21"]
    df["rsi"] = df["RSI"]
    df["vol"] = df["volume"]

    # TARGET
    df["target"] = (df["close"].shift(-1) > df["close"]).astype(int)

    # 🔥 CLEAN DATA (MAIN FIX)
    df = df.dropna()

    return df


# ================= TRAIN =================
def train_model(df):
    df = prepare_features(df)

    # 🔥 SAFETY CHECK
    if df is None or df.empty or len(df) < 20:
        return None, None

    features = ["return", "ema_diff", "rsi", "vol"]

    X = df[features]
    y = df["target"]

    # 🔥 FINAL CHECK
    if X.isnull().values.any() or y.isnull().values.any():
        return None, None

    model = RandomForestClassifier(n_estimators=100)
    model.fit(X, y)

    return model, features


# ================= SINGLE PRED =================
def predict_next(df):
    model, features = train_model(df)

    if model is None:
        return "WAIT", 0

    latest = df.iloc[-1:]

    try:
        X_live = latest[features]

        pred = model.predict(X_live)[0]
        prob = model.predict_proba(X_live)[0]

        confidence = round(max(prob) * 100, 2)

        return ("BUY", confidence) if pred == 1 else ("SELL", confidence)

    except:
        return "WAIT", 0


# ================= MULTI =================
def predict_multi(df, steps=3):
    results = []
    temp_df = df.copy()

    for _ in range(steps):
        signal, conf = predict_next(temp_df)
        results.append((signal, conf))

        if temp_df.empty:
            break

        last_close = temp_df["close"].iloc[-1]

        new_close = last_close * (1.001 if signal == "BUY" else 0.999)

        new_row = temp_df.iloc[-1:].copy()
        new_row["close"] = new_close

        temp_df = pd.concat([temp_df, new_row])

    return results


# ================= ACCURACY =================
def calculate_accuracy(df):
    df = prepare_features(df)

    # 🔥 SAFETY
    if df is None or df.empty or len(df) < 30:
        return 0

    correct = 0
    total = 0

    for i in range(30, len(df) - 1):
        sub_df = df.iloc[:i+1]

        model, features = train_model(sub_df)

        if model is None:
            continue

        try:
            X = sub_df.iloc[-1:][features]
            pred = model.predict(X)[0]
            actual = sub_df["target"].iloc[-1]

            if pred == actual:
                correct += 1

            total += 1

        except:
            continue

    if total == 0:
        return 0

    return round((correct / total) * 100, 2)
