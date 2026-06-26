import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# Check available models
try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False

try:
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    from sklearn.preprocessing import MinMaxScaler
    LSTM_AVAILABLE = True
except ImportError:
    LSTM_AVAILABLE = False

st.set_page_config(page_title="محلل الأسواق الاقتصادية الذكي", layout="wide", page_icon="🪙")

st.title("🪙 محلل الأسواق الاقتصادية الذكي بالذكاء الاصطناعي")
st.markdown("**تحليل متقدم + توقعات AI + مؤشرات فنية** للذهب، الفضة، النفط، البيتكوين والعملات")

# Sidebar controls
st.sidebar.header("إعدادات التحليل")

assets = {
    "الذهب (Gold)": "GC=F",
    "الفضة (Silver)": "SI=F",
    "النفط الخام (Crude Oil)": "CL=F",
    "البيتكوين (Bitcoin)": "BTC-USD",
    "الإيثريوم (Ethereum)": "ETH-USD",
    "اليورو مقابل الدولار (EUR/USD)": "EURUSD=X",
    "الجنيه الإسترليني (GBP/USD)": "GBPUSD=X",
    "مؤشر S&P 500": "^GSPC",
    "الدولار مقابل الين (USD/JPY)": "USDJPY=X",
}

selected_assets = st.sidebar.multiselect(
    "اختر الأصول للتحليل",
    options=list(assets.keys()),
    default=["الذهب (Gold)", "البيتكوين (Bitcoin)"]
)

period = st.sidebar.selectbox("الفترة التاريخية", ["1y", "2y", "5y", "10y", "max"], index=2)
forecast_days = st.sidebar.slider("عدد أيام التوقع المستقبلي", 7, 180, 30)
model_type = st.sidebar.selectbox("نوع نموذج الذكاء الاصطناعي", 
                                 ["Prophet (موصى به)", "LSTM (متقدم)"] if LSTM_AVAILABLE and PROPHET_AVAILABLE else ["Prophet (موصى به)"])

if st.sidebar.button("🚀 ابدأ التحليل", type="primary"):
    if not selected_assets:
        st.error("يرجى اختيار أصل واحد على الأقل")
    else:
        progress_bar = st.progress(0)
        data_dict = {}
        
        for i, asset_name in enumerate(selected_assets):
            ticker = assets[asset_name]
            st.subheader(f"🔍 تحليل {asset_name}")
            
            # Download data
            with st.spinner(f"جاري جلب بيانات {asset_name}..."):
                data = yf.download(ticker, period=period, progress=False)
            
            if data.empty:
                st.error(f"تعذر جلب بيانات {asset_name}")
                continue
            
            data_dict[asset_name] = data['Close'].copy()
            
            # Price chart
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name='السعر الحالي', line=dict(color='#00ff00')))
            fig.update_layout(
                title=f"سعر {asset_name} التاريخي",
                xaxis_title="التاريخ",
                yaxis_title="السعر (USD)",
                template="plotly_dark"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Technical indicators
            data['MA50'] = data['Close'].rolling(window=50).mean()
            data['MA200'] = data['Close'].rolling(window=200).mean()
            
            # RSI
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            data['RSI'] = 100 - (100 / (1 + rs))
            
            # Stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("السعر الحالي", f"${data['Close'].iloc[-1]:.2f}")
            with col2:
                st.metric("أعلى 52 أسبوع", f"${data['High'].max():.2f}")
            with col3:
                st.metric("أدنى 52 أسبوع", f"${data['Low'].min():.2f}")
            
            # Forecast
            if model_type.startswith("Prophet") and PROPHET_AVAILABLE:
                df_prophet = data['Close'].reset_index()
                df_prophet.columns = ['ds', 'y']
                
                model = Prophet(daily_seasonality=True, yearly_seasonality=True, weekly_seasonality=True, uncertainty_samples=50)
                model.fit(df_prophet)
                
                future = model.make_future_dataframe(periods=forecast_days)
                forecast = model.predict(future)
                
                fig_forecast = go.Figure()
                fig_forecast.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], name='التوقع', line=dict(color='#00ff00')))
                fig_forecast.add_trace(go.Scatter(x=df_prophet['ds'], y=df_prophet['y'], name='السعر الفعلي', line=dict(color='orange')))
                fig_forecast.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_lower'], name='الحد الأدنى', line=dict(dash='dash', color='red')))
                fig_forecast.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_upper'], name='الحد الأعلى', line=dict(dash='dash', color='green')))
                fig_forecast.update_layout(title=f"توقع سعر {asset_name} للـ{forecast_days} يوم القادمة", template="plotly_dark")
                st.plotly_chart(fig_forecast, use_container_width=True)
                
                latest = forecast.iloc[-1]
                st.success(f"**التوقع بعد {forecast_days} يوم:** ${latest['yhat']:.2f} (نطاق: ${latest['yhat_lower']:.2f} - ${latest['yhat_upper']:.2f})")
            
            elif model_type.startswith("LSTM") and LSTM_AVAILABLE:
                st.info("جاري تدريب نموذج LSTM... (قد يستغرق بعض الوقت)")
                # Simple LSTM implementation
                scaler = MinMaxScaler()
                scaled_data = scaler.fit_transform(data['Close'].values.reshape(-1, 1))
                
                X, y = [], []
                time_step = 60
                for i in range(time_step, len(scaled_data)):
                    X.append(scaled_data[i-time_step:i, 0])
                    y.append(scaled_data[i, 0])
                
                X, y = np.array(X), np.array(y)
                X = X.reshape(X.shape[0], X.shape[1], 1)
                
                model = Sequential()
                model.add(LSTM(50, return_sequences=True, input_shape=(time_step, 1)))
                model.add(Dropout(0.2))
                model.add(LSTM(50, return_sequences=False))
                model.add(Dropout(0.2))
                model.add(Dense(25))
                model.add(Dense(1))
                model.compile(optimizer='adam', loss='mean_squared_error')
                
                model.fit(X, y, epochs=10, batch_size=32, verbose=0)
                
                # Predict future
                last_sequence = scaled_data[-time_step:]
                future_predictions = []
                current_sequence = last_sequence.copy()
                
                for _ in range(forecast_days):
                    pred = model.predict(current_sequence.reshape(1, time_step, 1), verbose=0)
                    future_predictions.append(pred[0, 0])
                    current_sequence = np.append(current_sequence[1:], pred[0]).reshape(-1, 1)
                
                future_predictions = scaler.inverse_transform(np.array(future_predictions).reshape(-1, 1))
                
                st.success(f"**توقع LSTM بعد {forecast_days} يوم:** ${future_predictions[-1][0]:.2f}")
            
            progress_bar.progress(int((i+1)/len(selected_assets)*100))
        
        # Correlation analysis
        if len(data_dict) > 1:
            st.subheader("📊 تحليل الارتباط بين الأصول")
            combined = pd.DataFrame(data_dict)
            corr = combined.corr()
            
            fig_corr = go.Figure(data=go.Heatmap(
                z=corr.values,
                x=corr.columns,
                y=corr.columns,
                colorscale='RdYlGn',
                text=np.round(corr.values, 2),
                texttemplate='%{text}'
            ))
            fig_corr.update_layout(title="مصفوفة الارتباط", template="plotly_dark")
            st.plotly_chart(fig_corr, use_container_width=True)

st.sidebar.info("⚠️ التوقعات غير مضمونة ولا تشكل نصيحة استثمارية. استخدم لأغراض تحليلية فقط.")
st.caption("Powered by Streamlit + yfinance + Prophet/LSTM")
