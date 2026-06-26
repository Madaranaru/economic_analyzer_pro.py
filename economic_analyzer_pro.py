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
news_api_key = st.sidebar.text_input("NewsAPI Key (مجاني)", type="password", help="احصل عليه من newsapi.org")

# زر التحليل الرئيسي
if st.sidebar.button("🚀 ابدأ التحليل الشامل", type="primary"):
    st.success("🔄 جاري التحليل...")

    for asset_name in selected_assets:
        ticker = assets[asset_name]
        st.subheader(f"📈 {asset_name}")
        
        # Live Price
        try:
            info = yf.Ticker(ticker).info
            current = info.get('regularMarketPrice') or info.get('previousClose')
            change = info.get('regularMarketChangePercent', 0)
            st.metric("السعر اللحظي", f"${current:.2f}" if current else "جاري...", f"{change:.2f}%")
        except:
            st.warning("جاري تحميل السعر...")

        # Technical Analysis
        data = yf.download(ticker, period=period, progress=False)
        if not data.empty:
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.12)
            fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name='السعر'), row=1, col=1)
            
            data['MA50'] = data['Close'].rolling(50).mean()
            data['MA200'] = data['Close'].rolling(200).mean()
            delta = data['Close'].diff()
            gain = delta.where(delta > 0, 0).rolling(14).mean()
            loss = -delta.where(delta < 0, 0).rolling(14).mean()
            data['RSI'] = 100 - (100 / (1 + gain/loss))
            
            fig.add_trace(go.Scatter(x=data.index, y=data['MA50'], name='MA50'), row=1, col=1)
            fig.add_trace(go.Scatter(x=data.index, y=data['MA200'], name='MA200'), row=1, col=1)
            fig.add_trace(go.Scatter(x=data.index, y=data['RSI'], name='RSI'), row=2, col=1)
            
            fig.update_layout(height=650, template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
            
            # Prophet Forecast
            if PROPHET_AVAILABLE:
                df = data['Close'].reset_index()
                df.columns = ['ds', 'y']
                model = Prophet(yearly_seasonality=True)
                model.fit(df)
                future = model.make_future_dataframe(periods=forecast_days)
                forecast = model.predict(future)
                st.success(f"**توقع Prophet بعد {forecast_days} يوم: ${forecast['yhat'].iloc[-1]:.2f}**")
        
        st.divider()

    # أخبار + تحليل مشاعر
    st.subheader("📰 تحليل الأخبار + المشاعر (Reuters & Bloomberg)")
    if news_api_key:
        try:
            query = " OR ".join(selected_assets) + " OR gold OR oil OR bitcoin OR reuters OR bloomberg"
            url = f"https://newsapi.org/v2/everything?q={query}&language=ar&sortBy=publishedAt&apiKey={news_api_key}"
            resp = requests.get(url, timeout=15)
            news = resp.json()
            
            if news.get("status") == "ok":
                for article in news.get("articles", [])[:10]:
                    title_desc = (article['title'] + " " + article.get('description', '')).lower()
                    sentiment = "إيجابي 🔺" if any(w in title_desc for w in ["ارتفاع","صعود","gain","rise","up","record"]) else \
                               "سلبي 🔻" if any(w in title_desc for w in ["انخفاض","هبوط","drop","fall","down","crisis"]) else "محايد ⚖️"
                    
                    with st.expander(f"{sentiment} {article['title'][:70]}..."):
                        st.write(f"**المصدر:** {article['source']['name']}")
                        st.write(article.get('description', ''))
                        st.write(f"[اقرأ المقال]({article['url']})")
                        st.success(f"تحليل المشاعر: **{sentiment}**")
            else:
                st.info("لا توجد أخبار جديدة")
        except:
            st.error("خطأ في جلب الأخبار - تأكد من صحة API Key")
    else:
        st.info("أدخل NewsAPI Key ثم اضغط على زر 'ابدأ التحليل الشامل'")

st.sidebar.info("احصل على NewsAPI Key مجاناً من: https://newsapi.org/register")
st.caption("✅ تطبيق متكامل • تحليل مشاعر + أخبار + توقعات")
