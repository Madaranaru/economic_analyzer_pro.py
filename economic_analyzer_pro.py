import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objs as go
import warnings
warnings.filterwarnings('ignore')

try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except:
    PROPHET_AVAILABLE = False

st.set_page_config(page_title="محلل الأسواق الاقتصادية", layout="wide", page_icon="🪙")

st.title("🪙 محلل الأسواق الاقتصادية بالذكاء الاصطناعي")
st.markdown("**تحليل + توقعات Prophet**")

assets = {
    "الذهب (Gold)": "GC=F",
    "الفضة (Silver)": "SI=F",
    "النفط الخام": "CL=F",
    "البيتكوين": "BTC-USD",
    "الإيثريوم": "ETH-USD",
    "اليورو/دولار": "EURUSD=X",
    "S&P 500": "^GSPC",
}

selected_assets = st.sidebar.multiselect("اختر الأصول", options=list(assets.keys()), default=["الذهب (Gold)", "البيتكوين"])
period = st.sidebar.selectbox("الفترة", ["1y", "2y", "5y", "max"], index=2)
forecast_days = st.sidebar.slider("أيام التوقع", 7, 90, 30)

if st.sidebar.button("ابدأ التحليل", type="primary"):
    for asset_name in selected_assets:
        ticker = assets[asset_name]
        st.subheader(f"🔍 {asset_name}")
        
        data = yf.download(ticker, period=period, progress=False)
        if data.empty:
            st.error(f"تعذر جلب {asset_name}")
            continue
            
        # رسم السعر
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name='السعر'))
        fig.update_layout(title=f"سعر {asset_name}", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
        
        # توقع Prophet
        if PROPHET_AVAILABLE:
            df = data['Close'].reset_index()
            df.columns = ['ds', 'y']
            
            model = Prophet(yearly_seasonality=True, weekly_seasonality=True)
            model.fit(df)
            
            future = model.make_future_dataframe(periods=forecast_days)
            forecast = model.predict(future)
            
            fig_f = go.Figure()
            fig_f.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], name='التوقع'))
            fig_f.add_trace(go.Scatter(x=df['ds'], y=df['y'], name='السعر الفعلي'))
            fig_f.update_layout(title=f"توقع {asset_name} لـ{forecast_days} يوم", template="plotly_dark")
            st.plotly_chart(fig_f, use_container_width=True)
            
            last = forecast.iloc[-1]
            st.success(f"التوقع بعد {forecast_days} يوم: **${last['yhat']:.2f}**")

st.sidebar.info("⚠️ التوقعات للتحليل فقط - ليست نصيحة استثمارية")
