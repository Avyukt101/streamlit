import pandas as pd
import numpy as np

def sma(data, window=20):
    return data['Close'].rolling(window).mean()

def ema(data, window=20):
    return data['Close'].ewm(span=window).mean()

def rsi(data, period=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def bollinger_bands(data, window=20):
    sma = data['Close'].rolling(window).mean()
    std = data['Close'].rolling(window).std()
    upper = sma + (2 * std)
    lower = sma - (2 * std)
    return upper, lowerdef ai_chatbot(question, indicators):
    rsi = indicators.get("rsi", None)
    trend = indicators.get("trend", "Neutral")

    response = f"""
### 🤖 AI Trading Assistant (Educational)

**Your Question:** {question}

**Current Market Summary:**
- Trend: {trend}
- RSI: {rsi}

**Explanation:**
- RSI above 70 → Overbought
- RSI below 30 → Oversold
- Moving averages help identify trend direction
- Use multiple indicators together

⚠️ *This is NOT financial advice. Always do your own research.*
    """
    return responseimport streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

from indicators import sma, ema, rsi, bollinger_bands
from chatbot import ai_chatbot

st.set_page_config(page_title="AI Stock Analyzer", layout="wide")

st.title("📈 AI-Powered Stock Market Analyzer")

# ======================
# Sidebar Controls
# ======================
st.sidebar.header("Stock Settings")

ticker = st.sidebar.text_input("Stock Symbol", value="AAPL")
period = st.sidebar.selectbox(
    "Time Period",
    ["1mo", "3mo", "6mo", "1y", "2y", "5y"]
)

show_sma = st.sidebar.checkbox("Show SMA", True)
show_ema = st.sidebar.checkbox("Show EMA", False)
show_bb = st.sidebar.checkbox("Show Bollinger Bands", True)

# ======================
# Fetch Data
# ======================
data = yf.download(ticker, period=period)

if data.empty:
    st.error("Invalid stock symbol")
    st.stop()

# ======================
# Indicators
# ======================
data['SMA'] = sma(data)
data['EMA'] = ema(data)
data['RSI'] = rsi(data)
data['BB_UPPER'], data['BB_LOWER'] = bollinger_bands(data)

trend = "Bullish" if data['Close'].iloc[-1] > data['SMA'].iloc[-1] else "Bearish"

# ======================
# Candlestick Chart
# ======================
fig = go.Figure()

fig.add_trace(go.Candlestick(
    x=data.index,
    open=data['Open'],
    high=data['High'],
    low=data['Low'],
    close=data['Close'],
    name="Price"
))

if show_sma:
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['SMA'],
        name="SMA",
        line=dict(width=2)
    ))

if show_ema:
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['EMA'],
        name="EMA"
    ))

if show_bb:
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['BB_UPPER'],
        name="BB Upper",
        line=dict(dash="dot")
    ))
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['BB_LOWER'],
        name="BB Lower",
        line=dict(dash="dot")
    ))

fig.update_layout(
    height=600,
    xaxis_rangeslider_visible=False
)

st.plotly_chart(fig, use_container_width=True)

# ======================
# RSI Chart
# ======================
st.subheader("📉 RSI Indicator")

rsi_fig = go.Figure()
rsi_fig.add_trace(go.Scatter(
    x=data.index,
    y=data['RSI'],
    name="RSI"
))
rsi_fig.add_hline(y=70, line_dash="dash")
rsi_fig.add_hline(y=30, line_dash="dash")

st.plotly_chart(rsi_fig, use_container_width=True)

# ======================
# Portfolio Upload
# ======================
st.subheader("💼 Portfolio Analysis")

file = st.file_uploader("Upload Portfolio CSV", type=["csv", "xlsx"])

if file:
    portfolio = pd.read_csv(file)
    st.dataframe(portfolio)

    st.write("### Stock Correlation")
    corr = portfolio.corr()
    st.dataframe(corr)

# ======================
# AI Chatbot
# ======================
st.sidebar.header("🤖 AI Trading Assistant")

question = st.sidebar.text_input("Ask about market or indicators")

if question:
    indicators = {
        "rsi": round(data['RSI'].iloc[-1], 2),
        "trend": trend
    }

    reply = ai_chatbot(question, indicators)
    st.sidebar.markdown(reply)
