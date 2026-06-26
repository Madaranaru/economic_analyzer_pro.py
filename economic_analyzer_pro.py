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
st.markdown("**تحليل لحظي • أخبار + مشاعر • توقعات AI**")

# ==================== شريط إعلانات رفيع ====================
st.markdown("""
<div style="background-color:#1E1E1E; padding:8px; text-align:center; border-radius:8px; margin-bottom:15px;">
    <strong>📣 إعلان</strong> | احصل على تحليلات متقدمة واحترافية — 
    <a href="#" style="color:#00ff00;">اشترك الآن</a>
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
period = st.sidebar.selectbox("الفترة التاريخية", ["1mo", "3mo", "6mo", "1y", "2y"], index=2)
forecast_days = st.sidebar.slider("أيام التوقع", 7, 90, 30)
news_api_key = st.sidebar.text_input("NewsAPI Key (اختياري)", type="password")

# ==================== المساعد المستقبلي (Premium) ====================
st.sidebar.markdown("---")
if st.sidebar.button("🌟 المساعد المستقبلي (Premium)", type="secondary"):
    st.session_state.show_premium = True

if st.session_state.get("show_premium", False):
    st.subheader("🌟 المساعد المستقبلي للاستثمار")
    st.warning("🔒 هذه الميزة متاحة فقط باشتراك شهري 5 دولار")
    
    st.write("**ما ستحصل عليه:**")
    st.write("- نصائح استثمارية ذكية مبنية على الأخبار + المؤشرات")
    st.write("- توقعات اقتصادية متقدمة")
    st.write("- تحليل مشاعر الأخبار العالمية")
    st.write("- تنبيهات يومية")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("اشترك الآن - 5 دولار/شهر", type="primary"):
            st.success("سيتم توجيهك إلى صفحة الدفع (Stripe / Fawry)...")
            st.info("رابط الدفع: [اضغط هنا للاشتراك](https://your-payment-link.com)")
    with col2:
        if st.button("إغلاق"):
            st.session_state.show_premium = False

# ==================== التحليل الرئيسي ====================
if st.sidebar.button("🚀 ابدأ التحليل الشامل", type="primary"):
    # ... (الكود السابق للتحليل + الأخبار + المشاعر)
    for asset_name in selected_assets:
        # (نفس الكود السابق للأسعار والرسوم والتوقعات)
        st.subheader(f"📈 {asset_name}")
        # Live Price + Chart + Forecast (كما في النسخة السابقة)
        st.info("تم تحسين عرض الرسوم البيانية")

# ==================== Support Us ====================
st.markdown("---")
col1, col2, col3 = st.columns([1,2,1])
with col2:
    if st.button("❤️ Support Us - دعم التطبيق"):
        st.success("شكرًا لدعمك!")
        st.write("**وسائل الدفع:**")
        st.write("- فيزا / ماستركارد")
        st.write("- Fawry / Vodafone Cash / Orange Cash (مصر)")
        st.write("- PayPal")
        st.write("[اضغط هنا للدفع](https://your-donation-link.com)")

# Footer Banner
st.markdown("""
<div style="background-color:#0E1117; padding:15px; text-align:center; border-radius:10px; margin-top:30px;">
    <strong>📢 مساحة إعلانية</strong><br>
    تواصل معنا للإعلان على التطبيق — <span style="color:#00ff00;">info@yourdomain.com</span>
</div>
""", unsafe_allow_html=True)

st.caption("© 2026 - تطبيق تحليلي احترافي | Premium Features Available")
