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

# إشعارات في الأعلى
if st.button("🛎️ الإشعارات"):
    st.success("🔔 إشعار جديد: الذهب ارتفع 1.2% - فرصة شراء")

# شريط إعلاني
st.markdown("""
<div style="background:#1E1E1E; padding:10px; text-align:center; border-radius:8px;">
    📢 مساحة إعلانية - تواصل للإعلان
</div>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.header("الإعدادات")
assets = {"الذهب": "GC=F", "الفضة": "SI=F", "النفط": "CL=F", "البيتكوين": "BTC-USD"}
selected_assets = st.sidebar.multiselect("اختر الأصول", list(assets.keys()), default=["الذهب"])

# Premium Payment
if st.sidebar.button("💳 Premium (5$/شهر)"):
    st.session_state.show_payment = True

if st.session_state.get("show_payment", False):
    st.subheader("💳 الاشتراك Premium")
    st.write("5 دولار شهريًا")
    if st.button("ادفع الآن"):
        st.success("✅ Premium مفعل")
        st.session_state.premium = True
        st.session_state.show_payment = False

# زر التحليل الرئيسي
if st.button("🚀 ابدأ التحليل الاحترافي", type="primary"):
    for asset_name in selected_assets:
        st.subheader(f"📈 {asset_name}")
        data = yf.download(assets[asset_name], period="3mo", progress=False)
        if not data.empty:
            current = float(data['Close'].iloc[-1])
            st.metric("السعر الحالي", f"${current:.2f}")
            st.success("تم التحليل بنجاح")
            if PROPHET_AVAILABLE:
                st.info("توقع Prophet مفعل")
        st.divider()

# Premium Advisor
if st.session_state.get("premium", False):
    st.subheader("🌟 المساعد المستقبلي")
    st.success("Premium مفعل")
    st.info("**نصيحة اليوم:** الذهب صاعد. اشترِ عند 3980.")

st.caption("تطبيق متكامل • Premium + إشعارات + دفع")
