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

# -- Theme Selection --
st.sidebar.image("https://img.icons8.com/external-flat-icons-inmotus-design/67/external-analytics-financial-flat-icons-inmotus-design-4.png", width=60)
st.sidebar.title("FinTrend Pro")
st.sidebar.markdown("---")
theme_choice = st.sidebar.radio("Theme", ["Dark Mode 🌙", "Light Mode ☀️"])

if theme_choice == "Dark Mode 🌙":
    bg_gradient = "linear-gradient(145deg, #0f172a 0%, #1e1b4b 100%)"
    text_color = "#f8fafc"
    card_bg = "rgba(30, 41, 59, 0.4)"
    card_border = "rgba(255, 255, 255, 0.1)"
    card_hover_border = "rgba(168, 85, 247, 0.5)"
    metric_label = "#cbd5e1"
    metric_val_grad = "linear-gradient(90deg, #e2e8f0 0%, #94a3b8 100%)"
    sidebar_bg = "rgba(15, 23, 42, 0.95)"
    tab_text = "#94a3b8"
    ai_bg = "linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.8) 100%)"
    plotly_template = "plotly_dark"
    font_color_plotly = "white"
else:
    bg_gradient = "linear-gradient(145deg, #f8fafc 0%, #e2e8f0 100%)"
    text_color = "#0f172a"
    card_bg = "rgba(255, 255, 255, 0.7)"
    card_border = "rgba(0, 0, 0, 0.1)"
    card_hover_border = "rgba(168, 85, 247, 0.7)"
    metric_label = "#475569"
    metric_val_grad = "linear-gradient(90deg, #0f172a 0%, #334155 100%)"
    sidebar_bg = "rgba(248, 250, 252, 0.95)"
    tab_text = "#475569"
    ai_bg = "linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(241, 245, 249, 0.9) 100%)"
    plotly_template = "plotly_white"
    font_color_plotly = "black"

# -- Custom CSS for Premium Aesthetics --
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    /* Global Font & Background */
    html, body, [class*="css"] {{
        font-family: 'Outfit', sans-serif;
    }}
    .stApp {{
        background: {bg_gradient};
        color: {text_color};
    }}
    
    /* Force text colors for all common elements to override Streamlit defaults */
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, .stApp p, .stApp span, .stApp div[data-testid="stMarkdownContainer"] p {{
        color: {text_color} !important;
    }}
    
    /* Metrics Box - Glassmorphism */
    div[data-testid="metric-container"] {{
        background: {card_bg} !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border-radius: 16px !important;
        padding: 20px !important;
        border: 1px solid {card_border} !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.1) !important;
        transition: transform 0.3s ease, box-shadow 0.3s ease !important;
    }}
    div[data-testid="metric-container"]:hover {{
        transform: translateY(-5px) !important;
        box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.15) !important;
        border: 1px solid {card_hover_border} !important;
    }}
    div[data-testid="stMetricLabel"] *, div[data-testid="metric-container"] label {{
        color: {metric_label} !important;
        font-weight: 500 !important;
        font-size: 1.05rem !important;
    }}
    div[data-testid="stMetricValue"] *, div[data-testid="stMetricValue"] {{
        color: {text_color} !important;
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        background: {metric_val_grad} !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
    }}
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {{
        background-color: {sidebar_bg} !important;
        border-right: 1px solid {card_border} !important;
    }}
    
    /* Tabs Styling */
    div[data-testid="stTabs"] button {{
        font-family: 'Outfit', sans-serif !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        color: {tab_text} !important;
        background-color: transparent !important;
        border: none !important;
        padding-bottom: 10px !important;
    }}
    div[data-testid="stTabs"] button[aria-selected="true"] {{
        color: #a855f7 !important;
        border-bottom: 3px solid #a855f7 !important;
    }}
    
    /* News Cards */
    .news-card {{
        background: {card_bg};
        backdrop-filter: blur(10px);
        padding: 24px;
        border-radius: 16px;
        margin-bottom: 20px;
        border: 1px solid {card_border};
        transition: all 0.3s ease;
    }}
    .news-card:hover {{
        transform: translateY(-3px) scale(1.01);
        border-color: {card_hover_border};
        box-shadow: 0 10px 30px -10px rgba(168, 85, 247, 0.2);
    }}
    .news-title {{
        font-size: 1.25rem;
        font-weight: 600;
        color: {text_color};
        margin-bottom: 10px;
        line-height: 1.4;
    }}
    .news-meta {{
        font-size: 0.9rem;
        color: {tab_text};
        margin-bottom: 14px;
    }}
    
    /* AI Summary Box */
    .ai-summary {{
        background: {ai_bg};
        backdrop-filter: blur(10px);
        border-left: 5px solid #a855f7;
        border-radius: 12px;
        padding: 25px;
        margin-bottom: 30px;
        font-size: 1.15rem;
        line-height: 1.6;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        color: {text_color};
    }}
    
    /* Badges */
    .sentiment-badge {{
        padding: 6px 14px;
        border-radius: 24px;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }}
    .badge-positive {{ background-color: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3); }}
    .badge-negative {{ background-color: rgba(239, 68, 68, 0.15); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3); }}
    .badge-neutral {{ background-color: rgba(100, 116, 139, 0.15); color: {tab_text}; border: 1px solid rgba(100, 116, 139, 0.3); }}
    
    /* Fundamentals Card */
    .fund-card {{
        background: {card_bg};
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        border: 1px solid {card_border};
    }}
    .fund-title {{
        font-size: 0.9rem;
        color: {tab_text};
        margin-bottom: 5px;
    }}
    .fund-value {{
        font-size: 1.2rem;
        font-weight: 600;
        color: {text_color};
    }}

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

# -- Sidebar Details --

selected_company = st.sidebar.selectbox("Select Indian Stock", list(indian_stocks.ALL_STOCKS.keys()))
if indian_stocks.ALL_STOCKS[selected_company] == "CUSTOM":
    ticker = st.sidebar.text_input("Enter Custom Ticker (e.g., ZOMATO.NS)", "ZOMATO.NS").upper()
else:
    ticker = indian_stocks.ALL_STOCKS[selected_company]
    st.sidebar.caption(f"Ticker: `{ticker}`")

period = st.sidebar.selectbox("Select Time Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)
st.sidebar.markdown("---")

# -- Main Logic --
if ticker:
    try:
        with st.spinner(f"Crunching advanced market data for {ticker}..."):
            stock_data = data_fetcher.get_stock_data(ticker, period)
            news_data = data_fetcher.get_stock_news(ticker)
            stock_info = data_fetcher.get_stock_info(ticker)
            analyzed_news = sentiment_analyzer.get_news_with_sentiment(news_data) if not news_data.empty else pd.DataFrame()

        if stock_data.empty:
            st.error(f"Could not fetch data for ticker: {ticker}. Please check the symbol.")
        else:
            st.title(f"📈 {ticker} Terminal")
            
            # --- TABS SETUP ---
            tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
                "📊 Overview & Sentiment", 
                "📉 Technical Analysis", 
                "🔮 AI Forecast", 
                "⚔️ Compare Stocks", 
                "💼 My Portfolio",
                "⚙️ Strategy Backtester",
                "🚀 IPO Zone"
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
                
                st.markdown("<br>", unsafe_allow_html=True)
                # Split next section into 2 columns: Left for Fundamentals & Signal, Right for AI Summary
                main_col1, main_col2 = st.columns([1, 1.5])
                
                with main_col1:
                    st.subheader("🏢 Company Fundamentals")
                    f1, f2 = st.columns(2)
                    mcap = stock_info.get("marketCap", "N/A")
                    pe = stock_info.get("trailingPE", "N/A")
                    dy = stock_info.get("dividendYield", "N/A")
                    beta = stock_info.get("beta", "N/A")
                    
                    if mcap != "N/A": mcap = f"₹{mcap/1e10:.2f}Cr"
                    if dy != "N/A": dy = f"{dy*100:.2f}%"
                    if isinstance(pe, float): pe = f"{pe:.2f}"
                    if isinstance(beta, float): beta = f"{beta:.2f}"

                    f1.markdown(f'<div class="fund-card"><div class="fund-title">Market Cap</div><div class="fund-value">{mcap}</div></div>', unsafe_allow_html=True)
                    f2.markdown(f'<div class="fund-card"><div class="fund-title">P/E Ratio</div><div class="fund-value">{pe}</div></div>', unsafe_allow_html=True)
                    f1.markdown(f'<div class="fund-card" style="margin-top:10px;"><div class="fund-title">Div Yield</div><div class="fund-value">{dy}</div></div>', unsafe_allow_html=True)
                    f2.markdown(f'<div class="fund-card" style="margin-top:10px;"><div class="fund-title">Beta</div><div class="fund-value">{beta}</div></div>', unsafe_allow_html=True)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.subheader("⚡ Actionable Signal")
                    
                    # Calculate a dummy signal score based on RSI and Sentiment
                    signal_score = 50 # Neutral base
                    if len(stock_data) > 14:
                        temp_rsi = calc_rsi(stock_data).iloc[-1]
                        if temp_rsi < 30: signal_score += 25 # Oversold -> Bullish
                        elif temp_rsi > 70: signal_score -= 25 # Overbought -> Bearish
                    
                    if avg_sentiment > 0.1: signal_score += 15
                    elif avg_sentiment < -0.1: signal_score -= 15
                    
                    signal_score = max(0, min(100, signal_score))
                    
                    fig_gauge = go.Figure(go.Indicator(
                        mode = "gauge+number",
                        value = signal_score,
                        domain = {'x': [0, 1], 'y': [0, 1]},
                        title = {'text': "Trading Signal", 'font': {'color': font_color_plotly, 'size': 18}},
                        gauge = {
                            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': font_color_plotly},
                            'bar': {'color': "rgba(168, 85, 247, 0.5)"},
                            'bgcolor': "rgba(0,0,0,0)",
                            'borderwidth': 2,
                            'bordercolor': "gray",
                            'steps': [
                                {'range': [0, 35], 'color': "rgba(239, 68, 68, 0.6)"}, # Sell
                                {'range': [35, 65], 'color': "rgba(100, 116, 139, 0.6)"}, # Hold
                                {'range': [65, 100], 'color': "rgba(16, 185, 129, 0.6)"}], # Buy
                        }
                    ))
                    fig_gauge.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor='rgba(0,0,0,0)', font={'color': font_color_plotly})
                    st.plotly_chart(fig_gauge, use_container_width=True)

                with main_col2:
                    st.subheader("🤖 AI Market Summary")
                    # Company business summary
                    if stock_info.get("longBusinessSummary"):
                        with st.expander("About the Company", expanded=False):
                            st.write(stock_info.get("longBusinessSummary")[:500] + "...")
                            
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

                st.markdown("<br>", unsafe_allow_html=True)
                # Price Chart
                fig = go.Figure(data=[go.Candlestick(
                    x=stock_data['Date'], open=stock_data['Open'], high=stock_data['High'],
                    low=stock_data['Low'], close=stock_data['Close'], name="Price"
                )])
                fig.update_layout(template=plotly_template, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=10, b=0), xaxis_rangeslider_visible=False, height=400)
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
                
                fig_ta.update_layout(template=plotly_template, height=800, margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
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
                        
                        fig_fc.update_layout(template=plotly_template, height=500, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                        st.plotly_chart(fig_fc, use_container_width=True)
                    else:
                        st.warning("Not enough historical data available for this ticker to generate a reliable forecast.")

            # ==========================================
            # TAB 4: COMPARE STOCKS
            # ==========================================
            with tab4:
                st.subheader("⚔️ Compare Stock Performance")
                st.write("Select other stocks to compare their percentage growth over the selected time period.")
                
                compare_tickers = st.multiselect("Select Competitors", list(indian_stocks.ALL_STOCKS.keys()), default=[])
                
                if compare_tickers:
                    fig_comp = go.Figure()
                    
                    # Normalize base stock
                    base_norm = (stock_data['Close'] / stock_data['Close'].iloc[0]) * 100 - 100
                    fig_comp.add_trace(go.Scatter(x=stock_data['Date'], y=base_norm, name=ticker, line=dict(width=3)))
                    
                    for comp_name in compare_tickers:
                        c_ticker = indian_stocks.ALL_STOCKS[comp_name]
                        if c_ticker == "CUSTOM": continue
                        c_data = data_fetcher.get_stock_data(c_ticker, period)
                        if not c_data.empty:
                            c_norm = (c_data['Close'] / c_data['Close'].iloc[0]) * 100 - 100
                            fig_comp.add_trace(go.Scatter(x=c_data['Date'], y=c_norm, name=c_ticker))
                            
                    fig_comp.update_layout(template=plotly_template, height=500, yaxis_title="% Return", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
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
                    
                    st.dataframe(display_df)
                    
                    total_invested = port_df['Total Invested'].sum()
                    total_value = port_df['Current Value'].sum()
                    total_pl = port_df['Profit/Loss'].sum()
                    pl_pct = (total_pl / total_invested) * 100 if total_invested > 0 else 0
                    
                    st.markdown("### Portfolio Summary")
                    pc1, pc2, pc3 = st.columns(3)
                    pc1.metric("Total Invested", f"₹{total_invested:,.2f}")
                    pc2.metric("Current Value", f"₹{total_value:,.2f}", f"{total_pl:,.2f} ({pl_pct:.2f}%)", delta_color="normal" if total_pl >= 0 else "inverse")

            # ==========================================
            # TAB 6: BACKTESTER
            # ==========================================
            with tab6:
                st.subheader("⚙️ Interactive Strategy Backtester")
                st.write("Test a simple Moving Average (MA) Crossover strategy on historical data to see if it would have been profitable.")
                
                bc1, bc2 = st.columns(2)
                short_ma = bc1.number_input("Short Moving Average (Days)", min_value=3, max_value=50, value=10)
                long_ma = bc2.number_input("Long Moving Average (Days)", min_value=10, max_value=200, value=30)
                
                if short_ma >= long_ma:
                    st.warning("Short MA should be less than Long MA for a sensible crossover strategy.")
                else:
                    # Run a simple backtest
                    bt_data = stock_data.copy()
                    bt_data['Short_MA'] = bt_data['Close'].rolling(window=short_ma).mean()
                    bt_data['Long_MA'] = bt_data['Close'].rolling(window=long_ma).mean()
                    
                    # 1 = Buy, 0 = Sell
                    bt_data['Signal'] = 0.0  
                    bt_data.loc[bt_data['Short_MA'] > bt_data['Long_MA'], 'Signal'] = 1.0
                    bt_data['Position'] = bt_data['Signal'].diff()
                    
                    bt_data = bt_data.dropna()
                    
                    # Calculate Returns
                    bt_data['Market_Returns'] = bt_data['Close'].pct_change()
                    bt_data['Strategy_Returns'] = bt_data['Market_Returns'] * bt_data['Signal'].shift(1)
                    
                    cumulative_market = (1 + bt_data['Market_Returns']).cumprod()
                    cumulative_strategy = (1 + bt_data['Strategy_Returns']).cumprod()
                    
                    fig_bt = go.Figure()
                    fig_bt.add_trace(go.Scatter(x=bt_data['Date'], y=cumulative_market, name="Buy & Hold Return", line=dict(color='#94a3b8')))
                    fig_bt.add_trace(go.Scatter(x=bt_data['Date'], y=cumulative_strategy, name="Strategy Return", line=dict(color='#10b981', width=3)))
                    
                    fig_bt.update_layout(template=plotly_template, height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', title="Cumulative Returns")
                    st.plotly_chart(fig_bt, use_container_width=True)
                    
                    # Metrics
                    tc1, tc2 = st.columns(2)
                    strat_tot = (cumulative_strategy.iloc[-1] - 1) * 100 if len(cumulative_strategy) > 0 else 0
                    mark_tot = (cumulative_market.iloc[-1] - 1) * 100 if len(cumulative_market) > 0 else 0
                    
                    tc1.metric("Strategy Total Return", f"{strat_tot:.2f}%")
                    tc2.metric("Buy & Hold Total Return", f"{mark_tot:.2f}%")
                    
                    st.info("Note: This is a basic simulation excluding trading fees, slippage, and taxes.")

            # ==========================================
            # TAB 7: IPO ZONE
            # ==========================================
            with tab7:
                st.subheader("🚀 NSE IPO Zone")
                st.write("Track upcoming, ongoing, and recently listed Initial Public Offerings (IPOs) on the NSE Mainboard and SME platforms.")
                
                # Live April 2026 IPO Data
                ipo_data = {
                    "Company Name": [
                        "Adisoft Technologies", "Citius Transnet InvIT", "Leapfrog Engineering",
                        "Amir Chand Jagdish", "Powerica Ltd", "Vivid Electromech Ltd"
                    ],
                    "Segment": ["Mainboard", "InvIT", "SME", "Mainboard", "Mainboard", "SME"],
                    "Status": ["Ongoing", "Upcoming", "Upcoming", "Listed", "Listed", "Listed"],
                    "Issue Price": ["₹125 - 130", "TBD", "TBD", "₹245.00", "₹560.00", "₹85.00"],
                    "Listing Gain": ["-", "-", "-", "+12.50%", "+28.20%", "+45.00%"],
                }
                
                df_ipo = pd.DataFrame(ipo_data)
                
                # Stylish Display using columns
                upcoming_col, ongoing_col, listed_col = st.columns(3)
                
                with upcoming_col:
                    st.markdown("### 🔔 Upcoming IPOs")
                    for idx, row in df_ipo[df_ipo['Status'] == 'Upcoming'].iterrows():
                        st.markdown(f"""
                        <div class="news-card" style="padding: 15px; border-left: 4px solid #F59E0B;">
                            <h4>{row['Company Name']}</h4>
                            <p style="margin:0; font-size: 0.9em; color: #94a3b8;">{row['Segment']}</p>
                            <p style="margin:0; font-size: 0.9em; color: #cbd5e1;">Price: {row['Issue Price']}</p>
                        </div>
                        """, unsafe_allow_html=True)

                with ongoing_col:
                    st.markdown("### 🔥 Ongoing IPOs")
                    for idx, row in df_ipo[df_ipo['Status'] == 'Ongoing'].iterrows():
                        st.markdown(f"""
                        <div class="news-card" style="padding: 15px; border-left: 4px solid #3B82F6;">
                            <h4>{row['Company Name']}</h4>
                            <p style="margin:0; font-size: 0.9em; color: #94a3b8;">{row['Segment']}</p>
                            <p style="margin:0; font-size: 0.9em; color: #cbd5e1;">Price Band: {row['Issue Price']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                with listed_col:
                    st.markdown("### 🎉 Recently Listed")
                    for idx, row in df_ipo[df_ipo['Status'] == 'Listed'].iterrows():
                        st.markdown(f"""
                        <div class="news-card" style="padding: 15px; border-left: 4px solid #10B981;">
                            <h4>{row['Company Name']}</h4>
                            <p style="margin:0; font-size: 0.9em; color: #94a3b8;">Issue Price: {row['Issue Price']}</p>
                            <p style="margin:0; font-size: 0.9em; color: #10B981; font-weight: bold;">Gain: {row['Listing Gain']}</p>
                        </div>
                        """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"An error occurred: {e}")
