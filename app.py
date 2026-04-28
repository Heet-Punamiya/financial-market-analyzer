import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import yfinance as yf

# For Forecasting
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import warnings
warnings.filterwarnings("ignore")

import data_fetcher
import sentiment_analyzer
import indian_stocks

# -- Page Configuration --
st.set_page_config(
    page_title="FinTrend Pro: Market Analyzer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -- Initialize Session State for Portfolio --
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = []

# -- Custom CSS for Premium Aesthetics --
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    /* Global Font & Background */
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    .stApp {
        background: linear-gradient(145deg, #0f172a 0%, #1e1b4b 100%);
        color: #f8fafc;
    }
    
    /* Metrics Box - Glassmorphism */
    div[data-testid="metric-container"] {
        background: rgba(30, 41, 59, 0.4) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border-radius: 16px !important;
        padding: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3) !important;
        transition: transform 0.3s ease, box-shadow 0.3s ease !important;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px) !important;
        box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.5) !important;
        border: 1px solid rgba(168, 85, 247, 0.5) !important;
    }
    div[data-testid="metric-container"] label {
        color: #cbd5e1 !important;
        font-weight: 500 !important;
        font-size: 1.05rem !important;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        background: linear-gradient(90deg, #e2e8f0 0%, #94a3b8 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.95) !important;
        border-right: 1px solid rgba(255,255,255,0.05) !important;
    }
    
    /* Tabs Styling */
    div[data-testid="stTabs"] button {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        color: #94a3b8 !important;
        background-color: transparent !important;
        border: none !important;
        padding-bottom: 10px !important;
    }
    div[data-testid="stTabs"] button[aria-selected="true"] {
        color: #a855f7 !important;
        border-bottom: 3px solid #a855f7 !important;
    }
    
    /* News Cards */
    .news-card {
        background: rgba(30, 41, 59, 0.4);
        backdrop-filter: blur(10px);
        padding: 24px;
        border-radius: 16px;
        margin-bottom: 20px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        transition: all 0.3s ease;
    }
    .news-card:hover {
        transform: translateY(-3px) scale(1.01);
        border-color: rgba(168, 85, 247, 0.4);
        box-shadow: 0 10px 30px -10px rgba(168, 85, 247, 0.2);
    }
    .news-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #f1f5f9;
        margin-bottom: 10px;
        line-height: 1.4;
    }
    .news-meta {
        font-size: 0.9rem;
        color: #94a3b8;
        margin-bottom: 14px;
    }
    
    /* AI Summary Box */
    .ai-summary {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.8) 100%);
        backdrop-filter: blur(10px);
        border-left: 5px solid #a855f7;
        border-radius: 12px;
        padding: 25px;
        margin-bottom: 30px;
        font-size: 1.15rem;
        line-height: 1.6;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    }
    
    /* Badges */
    .sentiment-badge {
        padding: 6px 14px;
        border-radius: 24px;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .badge-positive { background-color: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
    .badge-negative { background-color: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }
    .badge-neutral { background-color: rgba(100, 116, 139, 0.15); color: #94a3b8; border: 1px solid rgba(100, 116, 139, 0.3); }
</style>
""", unsafe_allow_html=True)

# -- Helper Functions for Tech Analysis --
def calc_rsi(data, periods=14):
    close_delta = data['Close'].diff()
    up = close_delta.clip(lower=0)
    down = -1 * close_delta.clip(upper=0)
    ma_up = up.ewm(com=periods - 1, adjust=True, min_periods=periods).mean()
    ma_down = down.ewm(com=periods - 1, adjust=True, min_periods=periods).mean()
    rsi = ma_up / ma_down
    return 100 - (100/(1 + rsi))

def calc_macd(data, slow=26, fast=12, signal=9):
    exp1 = data['Close'].ewm(span=fast, adjust=False).mean()
    exp2 = data['Close'].ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    return macd, signal_line

def calc_bollinger(data, window=20):
    sma = data['Close'].rolling(window).mean()
    std = data['Close'].rolling(window).std()
    return sma + (std * 2), sma - (std * 2)

# -- Sidebar --
st.sidebar.image("https://img.icons8.com/external-flat-icons-inmotus-design/67/external-analytics-financial-flat-icons-inmotus-design-4.png", width=60)
st.sidebar.title("FinTrend Pro")
st.sidebar.markdown("---")

selected_company = st.sidebar.selectbox("Select Indian Stock", list(indian_stocks.NIFTY_50.keys()))
if indian_stocks.NIFTY_50[selected_company] == "CUSTOM":
    ticker = st.sidebar.text_input("Enter Custom Ticker (e.g., ZOMATO.NS)", "ZOMATO.NS").upper()
else:
    ticker = indian_stocks.NIFTY_50[selected_company]
    st.sidebar.caption(f"Ticker: `{ticker}`")

period = st.sidebar.selectbox("Select Time Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)
st.sidebar.markdown("---")

# -- Main Logic --
if ticker:
    try:
        with st.spinner(f"Crunching advanced market data for {ticker}..."):
            stock_data = data_fetcher.get_stock_data(ticker, period)
            news_data = data_fetcher.get_stock_news(ticker)
            analyzed_news = sentiment_analyzer.get_news_with_sentiment(news_data) if not news_data.empty else pd.DataFrame()

        if stock_data.empty:
            st.error(f"Could not fetch data for ticker: {ticker}. Please check the symbol.")
        else:
            st.title(f"📈 {ticker} Terminal")
            
            # --- TABS SETUP ---
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📊 Overview & Sentiment", 
                "📉 Technical Analysis", 
                "🔮 AI Forecast", 
                "⚔️ Compare Stocks", 
                "💼 My Portfolio"
            ])
            
            current_price = stock_data['Close'].iloc[-1]
            
            # ==========================================
            # TAB 1: OVERVIEW & SENTIMENT
            # ==========================================
            with tab1:
                prev_price = stock_data['Close'].iloc[-2] if len(stock_data) > 1 else current_price
                price_change = current_price - prev_price
                pct_change = (price_change / prev_price) * 100
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Current Price", f"₹{current_price:.2f}", f"{price_change:.2f} ({pct_change:.2f}%)")
                
                avg_sentiment = 0
                if not analyzed_news.empty:
                    avg_sentiment = analyzed_news['compound'].mean()
                    mood = "Bullish 🚀" if avg_sentiment > 0.1 else ("Bearish 📉" if avg_sentiment < -0.1 else "Neutral ⚖️")
                    d_color = "normal" if avg_sentiment > 0.1 else ("inverse" if avg_sentiment < -0.1 else "off")
                    col2.metric("Overall Sentiment", mood)
                    col3.metric("Avg Sentiment Score", f"{avg_sentiment:.2f}", delta_color=d_color)
                    col4.metric("Articles Analyzed", len(analyzed_news))
                else:
                    col2.metric("Overall Sentiment", "N/A")
                    col3.metric("Avg Sentiment Score", "N/A")
                    col4.metric("Articles Analyzed", 0)
                
                # AI Summary
                st.markdown("<br>", unsafe_allow_html=True)
                st.subheader("🤖 AI Market Summary")
                if not analyzed_news.empty:
                    pos_count = len(analyzed_news[analyzed_news['compound'] > 0.1])
                    neg_count = len(analyzed_news[analyzed_news['compound'] < -0.1])
                    summary_text = f"Based on analysis of {len(analyzed_news)} recent articles, the market sentiment is "
                    if avg_sentiment > 0.1: summary_text += f"**mostly positive** with {pos_count} bullish reports. "
                    elif avg_sentiment < -0.1: summary_text += f"**generally negative** with {neg_count} bearish reports. "
                    else: summary_text += "**mixed**. "
                    summary_text += f"The stock price is currently {'up' if price_change > 0 else 'down'} {abs(pct_change):.2f}% from the previous close."
                    
                    st.markdown(f'<div class="ai-summary">{summary_text}</div>', unsafe_allow_html=True)
                else:
                    st.info("Not enough recent news to generate an AI summary.")

                # Price Chart
                fig = go.Figure(data=[go.Candlestick(
                    x=stock_data['Date'], open=stock_data['Open'], high=stock_data['High'],
                    low=stock_data['Low'], close=stock_data['Close'], name="Price"
                )])
                fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=10, b=0), xaxis_rangeslider_visible=False, height=400)
                st.plotly_chart(fig, use_container_width=True)
                
                # News
                st.subheader("📰 Recent Headlines")
                if not analyzed_news.empty:
                    for idx, row in analyzed_news.head(5).iterrows():
                        date_str = row['published_at'].strftime("%Y-%m-%d %H:%M")
                        comp_score = row['compound']
                        badge_class = "badge-positive" if comp_score >= 0.05 else ("badge-negative" if comp_score <= -0.05 else "badge-neutral")
                        s_text = "POSITIVE" if comp_score >= 0.05 else ("NEGATIVE" if comp_score <= -0.05 else "NEUTRAL")
                        st.markdown(f"""
                        <div class="news-card">
                            <div class="news-title">{row['title']}</div>
                            <div class="news-meta">{row['publisher']} • {date_str}</div>
                            <div><span class="sentiment-badge {badge_class}">{s_text} (Score: {comp_score:.2f})</span>
                            <a href="{row['link']}" target="_blank" style="margin-left: 15px; color: #3B82F6; text-decoration: none; font-size: 0.85rem;">Read Full Article →</a></div>
                        </div>
                        """, unsafe_allow_html=True)
                        
            # ==========================================
            # TAB 2: TECHNICAL ANALYSIS
            # ==========================================
            with tab2:
                st.subheader(f"Advanced Indicators for {ticker}")
                
                # Calculate indicators
                df_ta = stock_data.copy()
                df_ta['RSI'] = calc_rsi(df_ta)
                df_ta['MACD'], df_ta['Signal'] = calc_macd(df_ta)
                df_ta['BB_Up'], df_ta['BB_Down'] = calc_bollinger(df_ta)
                
                # Plotly Subplots
                fig_ta = make_subplots(rows=3, cols=1, shared_xaxes=True, 
                                     vertical_spacing=0.05, row_heights=[0.5, 0.25, 0.25])
                
                # Row 1: Price + BB
                fig_ta.add_trace(go.Scatter(x=df_ta['Date'], y=df_ta['Close'], name='Close', line=dict(color='#FAFAFA')), row=1, col=1)
                fig_ta.add_trace(go.Scatter(x=df_ta['Date'], y=df_ta['BB_Up'], name='BB Upper', line=dict(color='rgba(255,255,255,0.2)', dash='dash')), row=1, col=1)
                fig_ta.add_trace(go.Scatter(x=df_ta['Date'], y=df_ta['BB_Down'], name='BB Lower', line=dict(color='rgba(255,255,255,0.2)', dash='dash'), fill='tonexty', fillcolor='rgba(255,255,255,0.05)'), row=1, col=1)
                
                # Row 2: RSI
                fig_ta.add_trace(go.Scatter(x=df_ta['Date'], y=df_ta['RSI'], name='RSI', line=dict(color='#A855F7')), row=2, col=1)
                fig_ta.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
                fig_ta.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
                
                # Row 3: MACD
                fig_ta.add_trace(go.Scatter(x=df_ta['Date'], y=df_ta['MACD'], name='MACD', line=dict(color='#3B82F6')), row=3, col=1)
                fig_ta.add_trace(go.Scatter(x=df_ta['Date'], y=df_ta['Signal'], name='Signal', line=dict(color='#EF4444')), row=3, col=1)
                fig_ta.add_trace(go.Bar(x=df_ta['Date'], y=df_ta['MACD'] - df_ta['Signal'], name='Histogram', marker_color='rgba(156,163,175,0.5)'), row=3, col=1)
                
                fig_ta.update_layout(template="plotly_dark", height=800, margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_ta, use_container_width=True)
                
            # ==========================================
            # TAB 3: FORECASTING
            # ==========================================
            with tab3:
                st.subheader("🔮 3-Day Price Forecast (Machine Learning)")
                st.info("Using Holt-Winters Exponential Smoothing to predict future trends based on historical data.")
                
                # Fetch dedicated long-term data for forecasting to ensure reliability
                with st.spinner("Training ML model on long-term data..."):
                    forecast_data = data_fetcher.get_stock_data(ticker, "2y")
                    ts_data = forecast_data[['Date', 'Close']].set_index('Date')
                    ts_data = ts_data.resample('B').ffill() # Business days
                    
                    if len(ts_data) > 60:
                        model = ExponentialSmoothing(ts_data['Close'], trend='add', seasonal=None, initialization_method="estimated")
                        fit_model = model.fit()
                        forecast = fit_model.forecast(3)
                        
                        forecast_dates = pd.bdate_range(start=ts_data.index[-1] + timedelta(days=1), periods=3)
                        
                        # Connect the forecast line to the last historical point
                        last_date = ts_data.index[-1]
                        last_price = ts_data['Close'].iloc[-1]
                        
                        fc_dates = [last_date] + list(forecast_dates)
                        fc_values = [last_price] + list(forecast.values)
                        
                        fig_fc = go.Figure()
                        # Show last 30 days of history so the 3-day forecast is actually visible
                        fig_fc.add_trace(go.Scatter(x=ts_data.index[-30:], y=ts_data['Close'].iloc[-30:], name='Historical Data', line=dict(color='#3B82F6', width=2)))
                        fig_fc.add_trace(go.Scatter(x=fc_dates, y=fc_values, name='3-Day Forecast', line=dict(color='#F59E0B', width=3)))
                        
                        fig_fc.update_layout(template="plotly_dark", height=500, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                        st.plotly_chart(fig_fc, use_container_width=True)
                    else:
                        st.warning("Not enough historical data available for this ticker to generate a reliable forecast.")

            # ==========================================
            # TAB 4: COMPARE STOCKS
            # ==========================================
            with tab4:
                st.subheader("⚔️ Compare Stock Performance")
                st.write("Select other stocks to compare their percentage growth over the selected time period.")
                
                compare_tickers = st.multiselect("Select Competitors", list(indian_stocks.NIFTY_50.keys()), default=[])
                
                if compare_tickers:
                    fig_comp = go.Figure()
                    
                    # Normalize base stock
                    base_norm = (stock_data['Close'] / stock_data['Close'].iloc[0]) * 100 - 100
                    fig_comp.add_trace(go.Scatter(x=stock_data['Date'], y=base_norm, name=ticker, line=dict(width=3)))
                    
                    for comp_name in compare_tickers:
                        c_ticker = indian_stocks.NIFTY_50[comp_name]
                        if c_ticker == "CUSTOM": continue
                        c_data = data_fetcher.get_stock_data(c_ticker, period)
                        if not c_data.empty:
                            c_norm = (c_data['Close'] / c_data['Close'].iloc[0]) * 100 - 100
                            fig_comp.add_trace(go.Scatter(x=c_data['Date'], y=c_norm, name=c_ticker))
                            
                    fig_comp.update_layout(template="plotly_dark", height=500, yaxis_title="% Return", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig_comp, use_container_width=True)

            # ==========================================
            # TAB 5: PORTFOLIO
            # ==========================================
            with tab5:
                st.subheader("💼 My Personal Portfolio")
                
                with st.form("add_asset"):
                    st.write("Add an asset to your mock portfolio")
                    p_ticker = st.text_input("Ticker (e.g., RELIANCE.NS)", ticker).upper()
                    p_shares = st.number_input("Number of Shares", min_value=0.01, value=10.0)
                    p_price = st.number_input("Average Buy Price", min_value=0.01, value=float(current_price))
                    
                    if st.form_submit_button("Add to Portfolio"):
                        st.session_state.portfolio.append({"Ticker": p_ticker, "Shares": p_shares, "Avg Price": p_price})
                        st.success(f"Added {p_shares} shares of {p_ticker} to portfolio!")
                        
                if st.session_state.portfolio:
                    st.markdown("### Current Holdings")
                    port_df = pd.DataFrame(st.session_state.portfolio)
                    
                    # Fetch current prices for portfolio
                    current_prices = []
                    for t in port_df['Ticker'].unique():
                        try:
                            # Quick fetch
                            td = yf.Ticker(t).history(period="1d")
                            cp = td['Close'].iloc[-1] if not td.empty else 0
                            current_prices.append({"Ticker": t, "Current Price": cp})
                        except:
                            current_prices.append({"Ticker": t, "Current Price": 0})
                            
                    cp_df = pd.DataFrame(current_prices)
                    port_df = port_df.merge(cp_df, on='Ticker', how='left')
                    
                    port_df['Total Invested'] = port_df['Shares'] * port_df['Avg Price']
                    port_df['Current Value'] = port_df['Shares'] * port_df['Current Price']
                    port_df['Profit/Loss'] = port_df['Current Value'] - port_df['Total Invested']
                    port_df['Return %'] = (port_df['Profit/Loss'] / port_df['Total Invested']) * 100
                    
                    # Format for display
                    display_df = port_df.copy()
                    for col in ['Avg Price', 'Current Price', 'Total Invested', 'Current Value', 'Profit/Loss']:
                        display_df[col] = display_df[col].apply(lambda x: f"₹{x:,.2f}")
                    display_df['Return %'] = display_df['Return %'].apply(lambda x: f"{x:,.2f}%")
                    
                    st.dataframe(display_df, use_container_width=True)
                    
                    total_invested = port_df['Total Invested'].sum()
                    total_value = port_df['Current Value'].sum()
                    total_pl = port_df['Profit/Loss'].sum()
                    pl_pct = (total_pl / total_invested) * 100 if total_invested > 0 else 0
                    
                    st.markdown("### Portfolio Summary")
                    pc1, pc2, pc3 = st.columns(3)
                    pc1.metric("Total Invested", f"₹{total_invested:,.2f}")
                    pc2.metric("Current Value", f"₹{total_value:,.2f}", f"{total_pl:,.2f} ({pl_pct:.2f}%)", delta_color="normal" if total_pl >= 0 else "inverse")

    except Exception as e:
        st.error(f"An error occurred: {e}")
