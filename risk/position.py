from sklearn.linear_model import LogisticRegression
import numpy as np

def train_model(df):
    """
    Train simple AI model on price movement
    """

    if df is None or len(df) < 50:
        return None

    df = df.copy()

    # Feature
    df["return"] = df["Close"].pct_change()

    # Target (next candle direction)
    df["target"] = (df["Close"].shift(-1) > df["Close"]).astype(int)

    df = df.dropna()

    if len(df) < 50:
        return None

    X = df[["return"]].values
    y = df["target"].values

    model = LogisticRegression()
    model.fit(X[:-1], y[:-1])

    return model


def predict(df, model):
    """
    Predict next candle direction
    """

    if model is None or df is None or len(df) < 2:
        return "NONE", 0

    last_return = df["Close"].iloc[-1] - df["Close"].iloc[-2]

    X = np.array([[last_return]])

    prob = model.predict_proba(X)[0]

    up_prob = prob[1]
    down_prob = prob[0]

    if up_prob > 0.6:
        return "UP", round(up_prob * 100, 1)

    elif down_prob > 0.6:
        return "DOWN", round(down_prob * 100, 1)

    else:
        return "SIDEWAYS", round(max(up_prob, down_prob) * 100, 1)
