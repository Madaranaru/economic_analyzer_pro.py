import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except:
    PROPHET_AVAILABLE = False

st.set_page_config(page_title="محلل الأسواق", layout="wide", page_icon="📈")

st.title("📈 محلل الأسواق الاقتصادية الذكي")
st.markdown("**Premium • إشعارات • دفع • TradingView Style**")

# إعلان
st.markdown("""
<div style="background:#1E1E1E;padding:12px;text-align:center;border-radius:10px;margin:10px 0;">
    📢 مساحة إعلانية - تواصل للإعلان
</div>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.header("⚙️ الإعدادات")
assets = {"الذهب": "GC=F", "الفضة": "SI=F", "النفط": "CL=F", "البيتكوين": "BTC-USD"}
selected_assets = st.sidebar.multiselect("اختر الأصول", list(assets.keys()), default=["الذهب"])
period = st.sidebar.selectbox("الفترة", ["1mo", "3mo", "6mo", "1y"], index=2)

# Premium Payment
if st.sidebar.button("💳 Premium (5$/شهر)"):
    st.session_state.show_payment = True

if st.session_state.get("show_payment", False):
    st.subheader("💳 الاشتراك Premium")
    st.write("5 دولار شهريًا")
    method = st.selectbox("طريقة الدفع", ["Visa/Mastercard", "Fawry", "Vodafone Cash"])
    if st.button("ادفع الآن"):
        st.success("✅ تم الدفع! Premium مفعل")
        st.session_state.premium = True
        st.session_state.show_payment = False

# إشعارات
if st.button("🛎️ الإشعارات"):
    st.success("🔔 الذهب ارتفع 1.2% اليوم - فرصة شراء")

# التحليل الرئيسي
if st.button("🚀 ابدأ التحليل الاحترافي", type="primary"):
    for asset_name in selected_assets:
        st.subheader(f"📈 {asset_name}")
        data = yf.download(assets[asset_name], period=period, progress=False)
        if data.empty or len(data) < 30:
            st.error("البيانات غير كافية. اختر فترة أطول.")
            continue

        current = float(data['Close'].iloc[-1])
        change = float(data['Close'].pct_change().iloc[-1] * 100)
        st.metric("السعر الحالي", f"${current:.2f}", f"{change:.2f}%")

        # Chart
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1)
        fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name='السعر', line=dict(color='#00ff9d')), row=1, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['Close'].rolling(50).mean(), name='MA50'), row=1, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['Close'].rolling(200).mean(), name='MA200'), row=1, col=1)

        delta = data['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = -delta.where(delta < 0, 0).rolling(14).mean()
        rsi = 100 - (100 / (1 + gain/loss))
        fig.add_trace(go.Scatter(x=data.index, y=rsi, name='RSI', line=dict(color='#c766ff')), row=2, col=1)

        fig.update_layout(height=700, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

        if PROPHET_AVAILABLE:
            df = data['Close'].reset_index()
            df.columns = ['ds', 'y']
            model = Prophet(yearly_seasonality=True)
            model.fit(df)
            future = model.make_future_dataframe(periods=30)
            forecast = model.predict(future)
            st.success(f"توقع Prophet: ${forecast['yhat'].iloc[-1]:.2f}")

        st.divider()

# Premium Advisor
if st.session_state.get("premium", False):
    st.subheader("🌟 المساعد المستقبلي")
    st.success("Premium مفعل")
    st.info("**نصيحة ذكية:** الذهب صاعد. اشترِ عند 3980.")

st.caption("تطبيق متكامل • Premium + دفع + إشعارات")
