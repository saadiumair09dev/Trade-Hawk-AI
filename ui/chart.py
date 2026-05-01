# ================= AUTO REFRESH =================
refresh_rate = st.slider("⏱ Refresh Speed (sec)", 1, 10, 2)

placeholder = st.empty()

while True:
    with placeholder.container():

        df = get_data(symbol, interval)

        if df is None or df.empty:
            st.error("❌ Data fetch failed")
            break

        df = add_indicators(df)

        # ===== SIGNAL =====
        if mode == "ML Mode":
            signal, confidence = predict_next(df)
        else:
            signal, confidence, _ = generate_signal(df, mode)

        st.write(f"📡 Live Signal: {signal} ({confidence}%)")

        st.line_chart(df["close"])

    time.sleep(refresh_rate)
    st.rerun()
    
import plotly.graph_objects as go

def plot_chart(df, signal=None):
    """
    Create professional candlestick chart
    """

    if df is None or df.empty:
        return None

    fig = go.Figure()

    # ================= CANDLESTICK =================
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        name="Price"
    ))

    # ================= EMA LINE =================
    if "EMA20" in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df["EMA20"],
            mode="lines",
            name="EMA20"
        ))

    # ================= VWAP =================
    if "VWAP" in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df["VWAP"],
            mode="lines",
            name="VWAP"
        ))

    # ================= SIGNAL MARKER =================
    if signal in ["BUY", "SELL"]:
        last = df.iloc[-1]

        color = "green" if signal == "BUY" else "red"

        fig.add_trace(go.Scatter(
            x=[df.index[-1]],
            y=[last["Close"]],
            mode="markers+text",
            marker=dict(size=12, color=color),
            text=[signal],
            textposition="top center",
            name="Signal"
        ))

    # ================= LAYOUT =================
    fig.update_layout(
        height=500,
        template="plotly_dark",
        xaxis_rangeslider_visible=False,
        title="Market Chart"
    )

    return fig
