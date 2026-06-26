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

st.set_page_config(page_title="محلل الأسواق الاقتصادية الذكي", layout="wide", page_icon="🪙")

st.title("🪙 محلل الأسواق الاقتصادية الذكي")
st.markdown("**تحليل لحظي • مؤشرات احترافية • أخبار + مشاعر • Premium Advisor**")

# شريط إعلانات
st.markdown("""
<div style="background: linear-gradient(90deg, #1E1E1E, #16213E); padding:12px; text-align:center; border-radius:10px; margin:10px 0;">
    📢 مساحة إعلانية - تواصل للإعلان على التطبيق
</div>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.header("⚙️ الإعدادات")
assets = {
    "الذهب": "GC=F", "الفضة": "SI=F", "النفط": "CL=F",
    "البيتكوين": "BTC-USD", "الإيثريوم": "ETH-USD",
    "اليورو/دولار": "EURUSD=X", "S&P 500": "^GSPC",
}

selected_assets = st.sidebar.multiselect("اختر الأصول", list(assets.keys()), default=["الذهب"])
period = st.sidebar.selectbox("الفترة", ["1mo", "3mo", "6mo", "1y", "2y"], index=2)
forecast_days = st.sidebar.slider("أيام التوقع", 7, 90, 30)
news_api_key = st.sidebar.text_input("NewsAPI Key", type="password")

# Premium Advisor
if st.sidebar.button("🌟 المساعد المستقبلي (Premium - 5$/شهر)"):
    st.session_state.premium = True

if st.session_state.get("premium", False):
    st.subheader("🌟 المساعد المستقبلي")
    st.success("نسخة Premium مفعلة")
    st.info("**نصيحة اليوم:** الذهب يحافظ على قوته بسبب التضخم والتوترات الجيوسياسية. يُفضل الاحتفاظ مع التركيز على مستويات الدعم.")
    st.button("احصل على تقرير يومي كامل")

# Main Analysis
if st.sidebar.button("🚀 ابدأ التحليل", type="primary"):
    for asset_name in selected_assets:
        st.subheader(f"📈 {asset_name}")
        
        data = yf.download(assets[asset_name], period=period, progress=False)
        if data.empty or len(data) < 20:
            st.warning("البيانات غير كافية لهذه الفترة")
            continue

        current = float(data['Close'].iloc[-1])
        change = float(data['Close'].pct_change().iloc[-1] * 100)

        col1, col2 = st.columns(2)
        with col1:
            st.metric("السعر الحالي", f"${current:.2f}", f"{change:.2f}%")

        # Chart
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1, row_heights=[0.7, 0.3])
        
        fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name='السعر', line=dict(color='#00ff9d')), row=1, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['Close'].rolling(50).mean(), name='MA50'), row=1, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['Close'].rolling(200).mean(), name='MA200'), row=1, col=1)

        # RSI
        delta = data['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = -delta.where(delta < 0, 0).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        fig.add_trace(go.Scatter(x=data.index, y=rsi, name='RSI', line=dict(color='#c766ff')), row=2, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="lime", row=2, col=1)

        fig.update_layout(height=720, template="plotly_dark", legend=dict(orientation="h"))
        st.plotly_chart(fig, use_container_width=True)

        # Forecast
        if PROPHET_AVAILABLE:
            df = data['Close'].reset_index()
            df.columns = ['ds', 'y']
            model = Prophet(yearly_seasonality=True)
            model.fit(df)
            future = model.make_future_dataframe(periods=forecast_days)
            forecast = model.predict(future)
            st.success(f"توقع Prophet بعد {forecast_days} يوم: ${forecast['yhat'].iloc[-1]:.2f}")

st.caption("تم تصميم التطبيق بأسلوب احترافي • Premium Features مفعلة")
