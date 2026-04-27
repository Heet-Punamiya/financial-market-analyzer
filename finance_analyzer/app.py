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

import auth
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
    bg_gradient = "linear-gradient(160deg, #0d1117 0%, #0f172a 50%, #111827 100%)"
    text_color = "#f0f6fc"
    card_bg = "rgba(22, 27, 34, 0.85)"
    card_border = "rgba(255,255,255,0.08)"
    card_hover_border = "rgba(0,194,100,0.5)"
    metric_label = "#8b949e"
    metric_val_grad = "linear-gradient(90deg, #f0f6fc 0%, #c9d1d9 100%)"
    sidebar_bg = "rgba(13,17,23,0.97)"
    tab_text = "#8b949e"
    ai_bg = "rgba(22,27,34,0.9)"
    plotly_template = "plotly_dark"
    font_color_plotly = "white"
else:
    bg_gradient = "linear-gradient(160deg, #ffffff 0%, #f6f8fa 60%, #eef2f7 100%)"
    text_color = "#1c2128"
    card_bg = "rgba(255,255,255,0.95)"
    card_border = "rgba(0,0,0,0.08)"
    card_hover_border = "rgba(0,194,100,0.6)"
    metric_label = "#57606a"
    metric_val_grad = "linear-gradient(90deg, #1c2128 0%, #424a53 100%)"
    sidebar_bg = "rgba(246,248,250,0.98)"
    tab_text = "#57606a"
    ai_bg = "rgba(246,248,250,0.95)"
    plotly_template = "plotly_white"
    font_color_plotly = "black"

# -- Professional CSS (Groww / Angel One inspired) --
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif !important;
    }}

    /* ── Background ── */
    .stApp {{
        background: {bg_gradient};
        color: {text_color};
    }}

    /* ── Force readable text everywhere ── */
    .stApp h1, .stApp h2, .stApp h3, .stApp h4,
    .stApp h5, .stApp h6, .stApp p, .stApp span,
    .stApp div[data-testid="stMarkdownContainer"] p {{
        color: {text_color} !important;
    }}

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {{
        background: {sidebar_bg} !important;
        border-right: 1px solid {card_border} !important;
        padding-top: 0 !important;
    }}
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stRadio label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span {{
        color: {text_color} !important;
        font-size: 0.85rem !important;
    }}

    /* ── Metric cards ── */
    div[data-testid="metric-container"] {{
        background: {card_bg} !important;
        backdrop-filter: blur(16px) !important;
        border-radius: 14px !important;
        padding: 18px 20px !important;
        border: 1px solid {card_border} !important;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08) !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
    }}
    div[data-testid="metric-container"]:hover {{
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 24px rgba(0,200,100,0.12) !important;
        border-color: rgba(0,200,100,0.4) !important;
    }}
    div[data-testid="stMetricLabel"] * {{
        color: {metric_label} !important;
        font-size: 0.78rem !important;
        font-weight: 500 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.6px !important;
    }}
    div[data-testid="stMetricValue"] * {{
        font-size: 1.9rem !important;
        font-weight: 700 !important;
        background: {metric_val_grad} !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
    }}
    div[data-testid="stMetricDelta"] * {{
        font-size: 0.85rem !important;
        font-weight: 600 !important;
    }}

    /* ── Tabs ── */
    div[data-testid="stTabs"] button {{
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        color: {tab_text} !important;
        background: transparent !important;
        border: none !important;
        padding: 10px 16px !important;
        border-radius: 8px 8px 0 0 !important;
        letter-spacing: 0.3px !important;
        transition: color 0.2s ease !important;
    }}
    div[data-testid="stTabs"] button:hover {{
        color: #00C264 !important;
    }}
    div[data-testid="stTabs"] button[aria-selected="true"] {{
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

# -- Authentication Logic --
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None

if not st.session_state.logged_in:
    st.markdown("""
    <div class="login-hero">
        <h1>FinTrend Pro</h1>
        <p>Your professional Indian stock market intelligence platform 📊</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        auth_mode = st.radio("", ["🔑 Login", "📝 Sign Up"], horizontal=True, label_visibility="collapsed")
        st.markdown("<br>", unsafe_allow_html=True)
        username_input = st.text_input("👤  Username", placeholder="Enter your username")
        password_input = st.text_input("🔒  Password", type="password", placeholder="Enter your password")
        st.markdown("<br>", unsafe_allow_html=True)

        if "Login" in auth_mode:
            if st.button("Log In →", use_container_width=True):
                success, msg = auth.login(username_input, password_input)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.username = username_input
                    st.rerun()
                else:
                    st.error(f"⚠️ {msg}")
        else:
            if st.button("Create Account →", use_container_width=True):
                success, msg = auth.signup(username_input, password_input)
                if success:
                    st.success(f"✅ {msg} Switch to Login to continue.")
                else:
                    st.error(f"⚠️ {msg}")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

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

# -- Sidebar user info & logout --
st.sidebar.markdown(f"""
<div style="background: rgba(0,194,100,0.08); border: 1px solid rgba(0,194,100,0.2);
     border-radius: 10px; padding: 10px 14px; margin-bottom: 8px;">
    <div style="font-size:0.75rem; color:#8b949e;">Logged in as</div>
    <div style="font-size:0.95rem; font-weight:700; color:#00C264;">👤 {st.session_state.username}</div>
</div>
""", unsafe_allow_html=True)
if st.sidebar.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.session_state.username = None
    st.rerun()
st.sidebar.markdown("---")
st.sidebar.markdown("**📌 Stock Selection**")

selected_company = st.sidebar.selectbox("Select Indian Stock", list(indian_stocks.ALL_STOCKS.keys()))
if indian_stocks.ALL_STOCKS[selected_company] == "CUSTOM":
    ticker = st.sidebar.text_input("Enter Custom Ticker (e.g., ZOMATO.NS)", "ZOMATO.NS").upper()
else:
    ticker = indian_stocks.ALL_STOCKS[selected_company]
    st.sidebar.caption(f"Ticker: `{ticker}`")

period = st.sidebar.selectbox("Select Time Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)

if st.sidebar.button("⭐ Add to Watchlist", use_container_width=True):
    if auth.add_to_watchlist(st.session_state.username, ticker):
        st.sidebar.success(f"{ticker} added to your watchlist!")
    else:
        st.sidebar.info(f"{ticker} is already in your watchlist.")

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
            # Professional header
            prev_price = stock_data['Close'].iloc[-2] if len(stock_data) > 1 else stock_data['Close'].iloc[-1]
            current_price = stock_data['Close'].iloc[-1]
            price_diff = current_price - prev_price
            price_pct  = (price_diff / prev_price) * 100
            arrow = "▲" if price_diff >= 0 else "▼"
            p_color = "#00C264" if price_diff >= 0 else "#EF4444"

            st.markdown(f"""
            <div style="display:flex; align-items:center; justify-content:space-between;
                        padding: 20px 0 12px; border-bottom: 1px solid {card_border}; margin-bottom:20px;">
                <div>
                    <div style="font-size:0.8rem; color:#8b949e; text-transform:uppercase; letter-spacing:1px;">
                        NSE &bull; EQUITY
                    </div>
                    <div style="font-size:2rem; font-weight:800; color:{text_color};">{selected_company}</div>
                    <div style="font-size:0.85rem; color:#8b949e;">{ticker}</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:2.2rem; font-weight:800; color:{text_color};">₹{current_price:,.2f}</div>
                    <div style="font-size:1rem; font-weight:600; color:{p_color};">
                        {arrow} ₹{abs(price_diff):,.2f} ({abs(price_pct):.2f}%)
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
                "📊 Overview", 
                "📉 Tech Analysis", 
                "🔮 AI Forecast", 
                "⚔️ Compare", 
                "💼 Portfolio",
                "⚙️ Backtester",
                "🚀 IPO Zone",
                "⭐ Watchlist",
                "🔥 Market Signals"
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
                st.subheader("🔮 Price Forecast (Machine Learning)")
                st.info("Using Holt-Winters Exponential Smoothing to predict future trends based on historical data.")
                
                forecast_type = st.radio("Select Forecast Horizon", ["Daily Forecast (Next 3 Days)", "Hourly Forecast (Next 5 Hours)"], horizontal=True)
                
                if "Daily" in forecast_type:
                    with st.spinner("Training ML model on long-term data..."):
                        forecast_data = data_fetcher.get_stock_data(ticker, "2y")
                        ts_data = forecast_data[['Date', 'Close']].set_index('Date')
                        ts_data = ts_data.resample('B').ffill() # Business days
                        
                        if len(ts_data) > 60:
                            model = ExponentialSmoothing(ts_data['Close'], trend='add', seasonal=None, initialization_method="estimated")
                            fit_model = model.fit()
                            forecast = fit_model.forecast(3)
                            
                            forecast_dates = pd.bdate_range(start=ts_data.index[-1] + timedelta(days=1), periods=3)
                            
                            last_date = ts_data.index[-1]
                            last_price = ts_data['Close'].iloc[-1]
                            
                            fc_dates = [last_date] + list(forecast_dates)
                            fc_values = [last_price] + list(forecast.values)
                            
                            fig_fc = go.Figure()
                            fig_fc.add_trace(go.Scatter(x=ts_data.index[-30:], y=ts_data['Close'].iloc[-30:], name='Historical Data', line=dict(color='#3B82F6', width=2)))
                            fig_fc.add_trace(go.Scatter(x=fc_dates, y=fc_values, name='3-Day Forecast', line=dict(color='#F59E0B', width=3)))
                            
                            fig_fc.update_layout(template=plotly_template, height=500, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', title="Daily Price Forecast")
                            st.plotly_chart(fig_fc, use_container_width=True)
                        else:
                            st.warning("Not enough historical data available for this ticker to generate a reliable forecast.")
                else:
                    with st.spinner("Training ML model on intraday data..."):
                        forecast_data = data_fetcher.get_stock_data(ticker, period="7d", interval="1h")
                        if not forecast_data.empty and len(forecast_data) > 10:
                            ts_data = forecast_data[['Date', 'Close']].set_index('Date')
                            
                            model = ExponentialSmoothing(ts_data['Close'], trend='add', seasonal=None, initialization_method="estimated")
                            fit_model = model.fit()
                            forecast = fit_model.forecast(5)
                            
                            last_date = ts_data.index[-1]
                            forecast_dates = [last_date + timedelta(hours=i) for i in range(1, 6)]
                            
                            last_price = ts_data['Close'].iloc[-1]
                            
                            fc_dates = [last_date] + list(forecast_dates)
                            fc_values = [last_price] + list(forecast.values)
                            
                            fig_fc = go.Figure()
                            fig_fc.add_trace(go.Scatter(x=ts_data.index[-20:], y=ts_data['Close'].iloc[-20:], name='Recent Hourly Data', line=dict(color='#10B981', width=2)))
                            fig_fc.add_trace(go.Scatter(x=fc_dates, y=fc_values, name='5-Hour Forecast', line=dict(color='#F59E0B', width=3)))
                            
                            fig_fc.update_layout(template=plotly_template, height=500, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', title="Hourly Price Forecast")
                            st.plotly_chart(fig_fc, use_container_width=True)
                        else:
                            st.warning("Not enough hourly data available for this ticker.")

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
                
                pf_col1, pf_col2 = st.columns(2)
                with pf_col1:
                    with st.form("buy_asset"):
                        st.write("Buy Asset")
                        p_ticker_b = st.text_input("Ticker (e.g., RELIANCE.NS)", ticker).upper()
                        p_shares_b = st.number_input("Shares to Buy", min_value=0.01, value=10.0)
                        p_price_b = st.number_input("Buy Price", min_value=0.01, value=float(current_price))
                        if st.form_submit_button("Buy"):
                            if auth.buy_portfolio_item(st.session_state.username, p_ticker_b, p_shares_b, p_price_b):
                                st.success(f"Bought {p_shares_b} shares of {p_ticker_b}!")
                                st.rerun()
                            else:
                                st.error("Failed to buy asset.")
                with pf_col2:
                    with st.form("sell_asset"):
                        st.write("Sell Asset")
                        p_ticker_s = st.text_input("Ticker", ticker).upper()
                        p_shares_s = st.number_input("Shares to Sell", min_value=0.01, value=10.0)
                        if st.form_submit_button("Sell"):
                            if auth.sell_portfolio_item(st.session_state.username, p_ticker_s, p_shares_s):
                                st.success(f"Sold {p_shares_s} shares of {p_ticker_s}!")
                                st.rerun()
                            else:
                                st.error("Failed to sell asset. Check your holdings.")
                                
                portfolio_items = auth.get_portfolio(st.session_state.username)
                
                if portfolio_items:
                    st.markdown("### Current Holdings")
                    port_df = pd.DataFrame([{"Ticker": p["ticker"], "Shares": p["shares"], "Avg Price": p["buy_price"]} for p in portfolio_items])
                    
                    # Group by ticker to show aggregated holdings
                    port_df['Total Invested'] = port_df['Shares'] * port_df['Avg Price']
                    grouped_df = port_df.groupby('Ticker').agg({'Shares': 'sum', 'Total Invested': 'sum'}).reset_index()
                    grouped_df['Avg Price'] = grouped_df['Total Invested'] / grouped_df['Shares']
                    
                    # Fetch current prices for portfolio
                    current_prices = []
                    for t in grouped_df['Ticker'].unique():
                        try:
                            td = yf.Ticker(t).history(period="1d")
                            cp = td['Close'].iloc[-1] if not td.empty else 0
                            current_prices.append({"Ticker": t, "Current Price": cp})
                        except:
                            current_prices.append({"Ticker": t, "Current Price": 0})
                            
                    cp_df = pd.DataFrame(current_prices)
                    grouped_df = grouped_df.merge(cp_df, on='Ticker', how='left')
                    
                    grouped_df['Current Value'] = grouped_df['Shares'] * grouped_df['Current Price']
                    grouped_df['Profit/Loss'] = grouped_df['Current Value'] - grouped_df['Total Invested']
                    grouped_df['Return %'] = (grouped_df['Profit/Loss'] / grouped_df['Total Invested']) * 100
                    
                    # Format for display
                    display_df = grouped_df.copy()
                    for col in ['Avg Price', 'Current Price', 'Total Invested', 'Current Value', 'Profit/Loss']:
                        display_df[col] = display_df[col].apply(lambda x: f"₹{x:,.2f}")
                    display_df['Return %'] = display_df['Return %'].apply(lambda x: f"{x:,.2f}%")
                    
                    st.dataframe(display_df)
                    
                    total_invested = grouped_df['Total Invested'].sum()
                    total_value = grouped_df['Current Value'].sum()
                    total_pl = grouped_df['Profit/Loss'].sum()
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

            # ==========================================
            # TAB 8: WATCHLIST
            # ==========================================
            with tab8:
                st.subheader("⭐ My Watchlist")
                watchlist = auth.get_watchlist(st.session_state.username)
                
                if not watchlist:
                    st.info("Your watchlist is empty. Search for a stock and click '⭐ Add to Watchlist' in the sidebar.")
                else:
                    # Create a nice layout for watchlist
                    st.write("Live updates for your favorite stocks:")
                    
                    for w_ticker in watchlist:
                        w_data = data_fetcher.get_stock_data(w_ticker, "1mo")
                        if not w_data.empty and len(w_data) > 1:
                            w_current = w_data['Close'].iloc[-1]
                            w_prev = w_data['Close'].iloc[-2]
                            w_diff = w_current - w_prev
                            w_pct = (w_diff / w_prev) * 100
                            
                            c1, c2, c3 = st.columns([2, 1, 1])
                            with c1:
                                st.markdown(f"### {w_ticker}")
                            with c2:
                                st.metric("Price", f"₹{w_current:.2f}", f"{w_diff:.2f} ({w_pct:.2f}%)")
                            with c3:
                                if st.button("❌ Remove", key=f"rm_{w_ticker}"):
                                    auth.remove_from_watchlist(st.session_state.username, w_ticker)
                                    st.rerun()
                            st.markdown("---")
                            
            # ==========================================
            # TAB 9: MARKET SIGNALS (Rise/Fall Predictor)
            # ==========================================
            with tab9:
                st.subheader("🔥 Dynamic Market Signal Scanner")
                st.markdown("AI-powered scanner that analyzes **RSI, MACD, and Moving Averages** to predict whether each stock is likely to 🟢 Rise or 🔴 Fall.")
                st.markdown("---")

                def get_signal_score(df):
                    """Returns a score -100 to +100. Positive = Bullish, Negative = Bearish."""
                    if df.empty or len(df) < 30:
                        return None, "Neutral", "⚪"
                    score = 0
                    close = df['Close']

                    # Signal 1: RSI
                    rsi_val = calc_rsi(df).iloc[-1]
                    if rsi_val < 35:
                        score += 35  # Oversold -> likely bounce up
                    elif rsi_val > 65:
                        score -= 35  # Overbought -> likely pullback
                    else:
                        score += (50 - rsi_val) * 0.5

                    # Signal 2: MACD Crossover
                    macd_line, signal_line = calc_macd(df)
                    if macd_line.iloc[-1] > signal_line.iloc[-1] and macd_line.iloc[-2] <= signal_line.iloc[-2]:
                        score += 40  # Fresh bullish crossover
                    elif macd_line.iloc[-1] < signal_line.iloc[-1] and macd_line.iloc[-2] >= signal_line.iloc[-2]:
                        score -= 40  # Fresh bearish crossover
                    elif macd_line.iloc[-1] > signal_line.iloc[-1]:
                        score += 15
                    else:
                        score -= 15

                    # Signal 3: Price vs 20-day MA
                    ma20 = close.rolling(20).mean().iloc[-1]
                    if close.iloc[-1] > ma20:
                        score += 25
                    else:
                        score -= 25

                    score = max(-100, min(100, score))

                    if score >= 30:
                        return score, "Rise", "🟢"
                    elif score <= -30:
                        return score, "Fall", "🔴"
                    else:
                        return score, "Neutral", "🟡"

                # Stock selection for scanning
                scan_col1, scan_col2 = st.columns([2, 1])
                with scan_col1:
                    all_stock_names = [k for k, v in indian_stocks.ALL_STOCKS.items() if v != "CUSTOM"]
                    stocks_to_scan = st.multiselect(
                        "Select stocks to scan (leave empty for Top 20 auto-scan)",
                        all_stock_names,
                        default=[]
                    )
                with scan_col2:
                    scan_period = st.selectbox("Data Period", ["3mo", "6mo", "1y"], index=1, key="scan_period")

                if st.button("🔍 Run Signal Scan", use_container_width=True):
                    scan_list = stocks_to_scan if stocks_to_scan else all_stock_names[:20]
                    results = []

                    progress = st.progress(0, text="Scanning stocks...")
                    for i, stock_name in enumerate(scan_list):
                        t = indian_stocks.ALL_STOCKS[stock_name]
                        try:
                            df_scan = data_fetcher.get_stock_data(t, scan_period)
                            score, signal, emoji = get_signal_score(df_scan)
                            if score is not None:
                                cur_p = df_scan['Close'].iloc[-1]
                                day_chg = ((df_scan['Close'].iloc[-1] - df_scan['Close'].iloc[-2]) / df_scan['Close'].iloc[-2]) * 100
                                results.append({
                                    "Company": stock_name,
                                    "Ticker": t,
                                    "Price": cur_p,
                                    "Day Change %": day_chg,
                                    "Signal": signal,
                                    "Emoji": emoji,
                                    "Score": score
                                })
                        except:
                            pass
                        progress.progress((i + 1) / len(scan_list), text=f"Scanning {stock_name}...")

                    progress.empty()

                    if results:
                        results_df = pd.DataFrame(results).sort_values("Score", ascending=False)

                        # Summary row
                        bullish_count = len(results_df[results_df["Signal"] == "Rise"])
                        bearish_count = len(results_df[results_df["Signal"] == "Fall"])
                        neutral_count = len(results_df[results_df["Signal"] == "Neutral"])

                        m1, m2, m3 = st.columns(3)
                        m1.metric("🟢 Bullish Stocks", bullish_count)
                        m2.metric("🔴 Bearish Stocks", bearish_count)
                        m3.metric("🟡 Neutral Stocks", neutral_count)
                        st.markdown("---")

                        # Display cards
                        st.markdown("### Stock Signal Cards")
                        cols_per_row = 3
                        row_items = [results_df.iloc[i:i+cols_per_row] for i in range(0, len(results_df), cols_per_row)]

                        for row in row_items:
                            card_cols = st.columns(cols_per_row)
                            for col, (_, row_data) in zip(card_cols, row.iterrows()):
                                border_color = "#10B981" if row_data["Signal"] == "Rise" else ("#EF4444" if row_data["Signal"] == "Fall" else "#F59E0B")
                                score_normalized = (row_data["Score"] + 100) / 200  # 0 to 1
                                day_color = "#10B981" if row_data["Day Change %"] >= 0 else "#EF4444"
                                day_arrow = "▲" if row_data["Day Change %"] >= 0 else "▼"
                                col.markdown(f"""
                                <div class="news-card" style="border-left: 4px solid {border_color}; padding: 14px;">
                                    <div style="font-size:1.4rem;">{row_data['Emoji']} <strong>{row_data['Company'][:20]}</strong></div>
                                    <div style="font-size:0.8rem; color:#94a3b8;">{row_data['Ticker']}</div>
                                    <div style="font-size:1.1rem; margin:6px 0;">₹{row_data['Price']:.2f} <span style="color:{day_color}; font-size:0.9rem;">{day_arrow} {abs(row_data['Day Change %']):.2f}%</span></div>
                                    <div style="background:rgba(255,255,255,0.1); border-radius:6px; height:8px; overflow:hidden;">
                                        <div style="background:{border_color}; width:{int(score_normalized*100)}%; height:100%; border-radius:6px;"></div>
                                    </div>
                                    <div style="font-size:0.8rem; color:#94a3b8; margin-top:4px;">Confidence: {abs(row_data['Score']):.0f}/100</div>
                                </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.warning("No signal data could be fetched. Try different stocks.")
                else:
                    st.info("👆 Select stocks above and click 'Run Signal Scan' to see predictions.")

    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
