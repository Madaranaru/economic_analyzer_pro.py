import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import warnings
import requests
warnings.filterwarnings('ignore')

try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except:
    PROPHET_AVAILABLE = False

st.set_page_config(page_title="محلل الأسواق الاقتصادية", layout="wide", page_icon="🪙")

st.title("🪙 محلل الأسواق الاقتصادية الذكي")
st.markdown("**تحليل احترافي • أسلوب TradingView • توقعات AI**")

# Sidebar
st.sidebar.header("⚙️ الإعدادات")
assets = {
    "الذهب": "GC=F", "الفضة": "SI=F", "النفط": "CL=F",
    "البيتكوين": "BTC-USD", "الإيثريوم": "ETH-USD",
    "اليورو/دولار": "EURUSD=X", "S&P 500": "^GSPC",
}

selected_assets = st.sidebar.multiselect("اختر الأصول", list(assets.keys()), default=["الذهب"])
period = st.sidebar.selectbox("الفترة", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)
forecast_days = st.sidebar.slider("أيام التوقع", 7, 90, 30)
news_api_key = st.sidebar.text_input("NewsAPI Key (اختياري)", type="password")

if st.sidebar.button("🚀 ابدأ التحليل الاحترافي", type="primary"):
    for asset_name in selected_assets:
        ticker = assets[asset_name]
        st.subheader(f"📈 {asset_name} - تحليل TradingView Style")

        data = yf.download(ticker, period=period, progress=False)
        if data.empty or len(data) < 50:
            st.error("البيانات غير كافية لهذه الفترة. اختر فترة أطول.")
            continue

        # Professional Main Chart
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.06,
                            row_heights=[0.75, 0.25],
                            subplot_titles=("السعر والمتوسطات المتحركة", "مؤشر RSI"))

        # Price + MAs
        fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name='السعر', line=dict(color='#00ff88', width=2.5)), row=1, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['Close'].rolling(50).mean(), name='MA50', line=dict(color='orange')), row=1, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['Close'].rolling(200).mean(), name='MA200', line=dict(color='red')), row=1, col=1)

        # RSI
        delta = data['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = -delta.where(delta < 0, 0).rolling(14).mean()
        rs = gain / loss
        data['RSI'] = 100 - (100 / (1 + rs))

        fig.add_trace(go.Scatter(x=data.index, y=data['RSI'], name='RSI', line=dict(color='#ba55d3')), row=2, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1, annotation_text="Overbought")
        fig.add_hline(y=30, line_dash="dash", line_color="lime", row=2, col=1, annotation_text="Oversold")

        fig.update_layout(height=750, template="plotly_dark", legend=dict(orientation="h", y=1.1))
        fig.update_yaxes(title="السعر (USD)", row=1, col=1)
        fig.update_yaxes(title="RSI", row=2, col=1)
        st.plotly_chart(fig, use_container_width=True)

        # Live Metrics
        current = data['Close'].iloc[-1]
        change = data['Close'].pct_change().iloc[-1] * 100
        st.metric("السعر الحالي", f"${current:.2f}", f"{change:.2f}%")

        # Prophet Forecast
        if PROPHET_AVAILABLE:
            df = data['Close'].reset_index()
            df.columns = ['ds', 'y']
            model = Prophet(yearly_seasonality=True, weekly_seasonality=True)
            model.fit(df)
            future = model.make_future_dataframe(periods=forecast_days)
            forecast = model.predict(future)
            st.success(f"**توقع Prophet بعد {forecast_days} يوم: ${forecast['yhat'].iloc[-1]:.2f}**")

        st.divider()

st.sidebar.info("احصل على NewsAPI Key من: https://newsapi.org")
st.caption("تم تصميم الرسوم البيانية بأسلوب TradingView • احترافي وسريع")
