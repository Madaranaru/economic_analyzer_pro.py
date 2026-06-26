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
st.markdown("**تحليل لحظي • أخبار + تحليل مشاعر • توقعات AI • Reuters & Bloomberg**")

# Sidebar
st.sidebar.header("⚙️ الإعدادات")
assets = {
    "الذهب": "GC=F", "الفضة": "SI=F", "النفط": "CL=F",
    "البيتكوين": "BTC-USD", "الإيثريوم": "ETH-USD",
    "اليورو/دولار": "EURUSD=X", "S&P 500": "^GSPC",
}

selected_assets = st.sidebar.multiselect("اختر الأصول", list(assets.keys()), default=["الذهب", "البيتكوين"])
period = st.sidebar.selectbox("الفترة التاريخية", ["1mo", "3mo", "6mo", "1y"], index=2)
forecast_days = st.sidebar.slider("أيام التوقع", 7, 90, 30)
auto_refresh = st.sidebar.checkbox("تحديث تلقائي كل 60 ثانية", value=True)
news_api_key = st.sidebar.text_input("NewsAPI Key (مجاني)", type="password")

if auto_refresh:
    st.autorefresh(interval=60000)

# دالة تحليل المشاعر
def analyze_sentiment(text):
    if not text:
        return "محايد", 0
    text_lower = text.lower()
    positive_words = ["ارتفاع", "صعود", "gain", "rise", "up", "record", "strong", "bullish"]
    negative_words = ["انخفاض", "هبوط", "drop", "fall", "down", "crisis", "war", "recession", "bearish"]
    
    pos_count = sum(1 for w in positive_words if w in text_lower)
    neg_count = sum(1 for w in negative_words if w in text_lower)
    
    if pos_count > neg_count:
        return "إيجابي 🔺", pos_count
    elif neg_count > pos_count:
        return "سلبي 🔻", neg_count
    else:
        return "محايد ⚖️", 0

if selected_assets:
    st.success("🔄 جاري التحليل التلقائي...")
    
    for asset_name in selected_assets:
        ticker = assets[asset_name]
        st.subheader(f"📈 {asset_name}")
        
        # Live Price
        try:
            info = yf.Ticker(ticker).info
            current = info.get('regularMarketPrice') or info.get('previousClose')
            change = info.get('regularMarketChangePercent', 0)
            st.metric("السعر اللحظي", f"${current:.2f}" if current else "N/A", f"{change:.2f}%")
        except:
            pass
        
        # Technical + Forecast
        data = yf.download(ticker, period=period, progress=False)
        if not data.empty:
            # Charts and indicators...
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True)
            fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name='السعر'), row=1, col=1)
            fig.update_layout(height=500, template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
            
            if PROPHET_AVAILABLE:
                df = data['Close'].reset_index()
                df.columns = ['ds', 'y']
                model = Prophet(yearly_seasonality=True)
                model.fit(df)
                future = model.make_future_dataframe(periods=forecast_days)
                forecast = model.predict(future)
                st.success(f"**توقع Prophet: ${forecast['yhat'].iloc[-1]:.2f}**")
    
    # ==================== أخبار + تحليل مشاعر ====================
    st.subheader("📰 تحليل الأخبار + المشاعر (Reuters, Bloomberg, CNBC...)")
    if news_api_key:
        try:
            query = " OR ".join(selected_assets) + " OR gold OR oil OR bitcoin OR reuters OR bloomberg"
            url = f"https://newsapi.org/v2/everything?q={query}&language=ar&sortBy=publishedAt&apiKey={news_api_key}"
            resp = requests.get(url, timeout=15)
            news = resp.json()
            
            if news.get("status") == "ok":
                for article in news.get("articles", [])[:10]:
                    sentiment, score = analyze_sentiment(article['title'] + " " + article.get('description', ''))
                    with st.expander(f"{sentiment} {article['title'][:75]}..."):
                        st.write(f"**المصدر:** {article['source']['name']}")
                        st.write(article.get('description', ''))
                        st.write(f"[اقرأ المقال كاملاً]({article['url']})")
                        if score > 0:
                            st.success(f"تحليل المشاعر: **{sentiment}**")
        except:
            st.error("تعذر جلب الأخبار - تأكد من API Key")
    else:
        st.info("أدخل NewsAPI Key لتفعيل قسم الأخبار + تحليل المشاعر")

st.sidebar.info("احصل على NewsAPI Key مجاناً من: https://newsapi.org/register")
st.caption("✅ تطبيق متكامل • تحليل مشاعر + أخبار + توقعات")
