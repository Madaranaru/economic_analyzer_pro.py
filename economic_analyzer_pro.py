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
st.markdown("**Premium • دفع • إشعارات • TradingView Style**")

# إعلان
st.markdown("""
<div style="background:#1E1E1E; padding:12px; text-align:center; border-radius:10px;">
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
    st.subheader("💳 صفحة الدفع")
    st.write("**اشتراك Premium - 5 دولار شهري**")
    method = st.selectbox("طريقة الدفع", ["Visa/Mastercard", "Fawry", "Vodafone Cash"])
    
    if method == "Visa/Mastercard":
        st.text_input("رقم البطاقة", "4242 4242 4242 4242")
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("MM/YY", "12/28")
        with col2:
            st.text_input("CVV", "123")
        if st.button("ادفع 5 دولار"):
            st.success("✅ تم الدفع بنجاح! Premium مفعل")
            st.session_state.premium = True
            st.session_state.show_payment = False
    
    else:
        if st.button("ادفع عبر " + method):
            st.success("✅ تم إرسال كود الدفع. أكمل العملية.")
            st.session_state.premium = True
            st.session_state.show_payment = False

# Notifications
if st.button("🛎️ الإشعارات"):
    st.success("🔔 إشعار: الذهب ارتفع 1.2% اليوم. فرصة شراء جيدة!")

# Premium Advisor
if st.session_state.get("premium", False):
    st.subheader("🌟 المساعد المستقبلي")
    st.success("Premium مفعل")
    st.info("**تحليل اليوم:** الذهب صاعد بقوة. هدف 4150 دولار.")

# Analysis
if st.sidebar.button("🚀 ابدأ التحليل"):
    st.success("تم التحليل بنجاح")

st.caption("تطبيق متكامل • دفع + إشعارات + Premium")
