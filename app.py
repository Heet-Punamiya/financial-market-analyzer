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
# -- Page Configuration --
st.set_page_config(
    page_title="FinTrend Pro - Professional Market Analyzer",
    page_icon="https://img.icons8.com/external-flat-icons-inmotus-design/67/external-analytics-financial-flat-icons-inmotus-design-4.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -- Initialize Session State for Portfolio --
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = []

# -- Theme Selection --
st.sidebar.image("https://img.icons8.com/external-flat-icons-inmotus-design/67/external-analytics-financial-flat-icons-inmotus-design-4.png", width=48)
st.sidebar.title("FinTrend Pro")
st.sidebar.markdown("---")
theme_choice = st.sidebar.radio("Theme", ["Dark Mode", "Light Mode"])

if theme_choice == "Dark Mode":
    bg_gradient = "linear-gradient(160deg, #0B0E14 0%, #0F121C 100%)"
    text_color = "#ECEFF4"
    card_bg = "#121622"
    card_border = "#1E2538"
    card_hover_border = "#00B386"
    metric_label = "#94A3B8"
    metric_val_grad = "linear-gradient(90deg, #ECEFF4 0%, #D8DEE9 100%)"
    sidebar_bg = "#0F121C"
    tab_text = "#94A3B8"
    ai_bg = "#181E2E"
    plotly_template = "plotly_dark"
    font_color_plotly = "white"
else:
    bg_gradient = "linear-gradient(160deg, #FFFFFF 0%, #F4F6F8 100%)"
    text_color = "#1E293B"
    card_bg = "#FFFFFF"
    card_border = "#E2E8F0"
    card_hover_border = "#00B386"
    metric_label = "#64748B"
    metric_val_grad = "linear-gradient(90deg, #1E293B 0%, #475569 100%)"
    sidebar_bg = "#FFFFFF"
    tab_text = "#64748B"
    ai_bg = "#F1F5F9"
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
        border-radius: 10px !important;
        padding: 18px 20px !important;
        border: 1px solid {card_border} !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
        transition: transform 0.2s ease, border-color 0.2s ease !important;
    }}
    div[data-testid="metric-container"]:hover {{
        transform: translateY(-2px) !important;
        border-color: {card_hover_border} !important;
    }}
    div[data-testid="stMetricLabel"] * {{
        color: {metric_label} !important;
        font-size: 0.78rem !important;
        font-weight: 500 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.6px !important;
    }}
    div[data-testid="stMetricValue"] * {{
        font-size: 1.8rem !important;
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
        font-weight: 500 !important;
        font-size: 0.9rem !important;
        color: {tab_text} !important;
        background: transparent !important;
        border: none !important;
        padding: 10px 16px !important;
        transition: color 0.2s ease !important;
    }}
    div[data-testid="stTabs"] button:hover {{
        color: #00B386 !important;
    }}
    div[data-testid="stTabs"] button[aria-selected="true"] {{
        border-bottom: 2px solid #00B386 !important;
        color: #00B386 !important;
    }}
    
    /* News Card */
    .news-card {{
        background: {card_bg} !important;
        border: 1px solid {card_border} !important;
        border-radius: 8px !important;
        padding: 18px !important;
        margin-bottom: 12px !important;
        transition: transform 0.2s ease, border-color 0.2s ease !important;
    }}
    .news-card:hover {{
        transform: translateY(-2px) !important;
        border-color: {card_hover_border} !important;
    }}
    .news-title {{
        font-size: 1.15rem;
        font-weight: 600;
        color: {text_color};
        margin-bottom: 8px;
        line-height: 1.4;
    }}
    .news-meta {{
        font-size: 0.85rem;
        color: {tab_text};
        margin-bottom: 12px;
    }}
    
    /* AI Summary Box */
    .ai-summary {{
        background: {ai_bg} !important;
        border-left: 4px solid #3B82F6 !important;
        border-radius: 8px !important;
        padding: 18px !important;
        margin-bottom: 20px !important;
        font-size: 0.95rem;
        line-height: 1.5;
        color: {text_color};
    }}
    
    /* Badges */
    .sentiment-badge {{
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.5px;
    }}
    .badge-positive {{ background-color: rgba(16, 185, 129, 0.12); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.2); }}
    .badge-negative {{ background-color: rgba(239, 68, 68, 0.12); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.2); }}
    .badge-neutral {{ background-color: rgba(100, 116, 139, 0.12); color: {tab_text}; border: 1px solid rgba(100, 116, 139, 0.2); }}
    
    /* Fundamentals Card */
    .fund-card {{
        background: {card_bg};
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        border: 1px solid {card_border};
    }}
    .fund-title {{
        font-size: 0.85rem;
        color: {tab_text};
        margin-bottom: 5px;
    }}
    .fund-value {{
        font-size: 1.15rem;
        font-weight: 600;
        color: {text_color};
    }}
    
    /* Login Redesign */
    .login-hero {{
        text-align: center;
        margin-top: 60px;
        margin-bottom: 40px;
    }}
    .login-hero h1 {{
        font-size: 2.8rem !important;
        font-weight: 800 !important;
        background: linear-gradient(90deg, #00B386 0%, #3B82F6 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        margin-bottom: 10px !important;
    }}
    .login-hero p {{
        font-size: 1.1rem !important;
        color: {tab_text} !important;
    }}
    .login-box {{
        background: {card_bg} !important;
        border: 1px solid {card_border} !important;
        border-radius: 12px !important;
        padding: 35px !important;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.05) !important;
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
        <p>Professional Indian stock market intelligence and analysis platform</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.3, 1])
    with col2:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        auth_mode = st.radio("", ["Login", "Sign Up"], horizontal=True, label_visibility="collapsed")
        st.markdown("<br>", unsafe_allow_html=True)
        username_input = st.text_input("Username", placeholder="Enter your username")
        password_input = st.text_input("Password", type="password", placeholder="Enter your password")
        st.markdown("<br>", unsafe_allow_html=True)

        if auth_mode == "Login":
            if st.button("Log In", use_container_width=True):
                success, msg = auth.login(username_input, password_input)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.username = username_input
                    st.rerun()
                else:
                    st.error(f"Error: {msg}")
        else:
            if st.button("Create Account", use_container_width=True):
                success, msg = auth.signup(username_input, password_input)
                if success:
                    st.success(f"Success: {msg} Please switch to Login mode to log in.")
                else:
                    st.error(f"Error: {msg}")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# -- Helper function for detailed charges bifurcation --
def render_charges_invoice(tx):
    val = tx["shares"] * tx["price"]
    # Retrieve theme values dynamically
    theme_card_bg = card_bg
    theme_card_border = card_border
    theme_text_color = text_color
    theme_tab_text = tab_text
    
    st.markdown(f"""
    <div style="background-color: {theme_card_bg}; border: 1px solid {theme_card_border}; border-radius: 8px; padding: 20px; margin-top: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
        <div style="display: flex; justify-content: space-between; border-bottom: 1px solid {theme_card_border}; padding-bottom: 10px; margin-bottom: 15px;">
            <span style="font-weight: 700; font-size: 1.1rem; color: #00B386; font-family: 'Inter', sans-serif;">TAX INVOICE / CONTRACT NOTE</span>
            <span style="color: {theme_tab_text}; font-size: 0.9rem; font-family: 'Inter', sans-serif;">{tx['timestamp']}</span>
        </div>
        <table style="width: 100%; font-size: 0.95rem; border-collapse: collapse; color: {theme_text_color}; font-family: 'Inter', sans-serif;">
            <tr style="border-bottom: 1px dashed {theme_card_border};">
                <td style="padding: 8px 0; font-weight: 600;">Stock Ticker</td>
                <td style="padding: 8px 0; text-align: right; font-weight: 600;">{tx['ticker']}</td>
            </tr>
            <tr style="border-bottom: 1px dashed {theme_card_border};">
                <td style="padding: 8px 0; font-weight: 600;">Action / Trade Type</td>
                <td style="padding: 8px 0; text-align: right; font-weight: 600; color: {'#10B981' if tx['trade_type'] == 'BUY' else '#EF4444'};">{tx['trade_type']}</td>
            </tr>
            <tr style="border-bottom: 1px dashed {theme_card_border};">
                <td style="padding: 6px 0;">Quantity</td>
                <td style="padding: 6px 0; text-align: right;">{tx['shares']:.2f}</td>
            </tr>
            <tr style="border-bottom: 1px dashed {theme_card_border};">
                <td style="padding: 6px 0;">Execution Price</td>
                <td style="padding: 6px 0; text-align: right;">₹{tx['price']:,.2f}</td>
            </tr>
            <tr style="border-bottom: 1px solid {theme_card_border}; font-weight: 600; background-color: rgba(0,0,0,0.02);">
                <td style="padding: 10px 0;">Gross Trade Value</td>
                <td style="padding: 10px 0; text-align: right;">₹{val:,.2f}</td>
            </tr>
            <tr><td colspan="2" style="height: 10px;"></td></tr>
            <tr>
                <td style="padding: 4px 0; color: {theme_tab_text}; font-size: 0.85rem;">Brokerage (0.03% or max ₹20)</td>
                <td style="padding: 4px 0; text-align: right; font-size: 0.85rem;">₹{tx['brokerage']:.2f}</td>
            </tr>
            <tr>
                <td style="padding: 4px 0; color: {theme_tab_text}; font-size: 0.85rem;">Securities Transaction Tax (STT - 0.1%)</td>
                <td style="padding: 4px 0; text-align: right; font-size: 0.85rem;">₹{tx['stt']:.2f}</td>
            </tr>
            <tr>
                <td style="padding: 4px 0; color: {theme_tab_text}; font-size: 0.85rem;">Exchange Transaction Charges (NSE - 0.00322%)</td>
                <td style="padding: 4px 0; text-align: right; font-size: 0.85rem;">₹{tx['exchange_charges']:.2f}</td>
            </tr>
            <tr>
                <td style="padding: 4px 0; color: {theme_tab_text}; font-size: 0.85rem;">SEBI Turnover Fees (0.0001%)</td>
                <td style="padding: 4px 0; text-align: right; font-size: 0.85rem;">₹{tx['sebi_fees']:.4f}</td>
            </tr>
            <tr>
                <td style="padding: 4px 0; color: {theme_tab_text}; font-size: 0.85rem;">GST (18% of Brokerage + Exchange + SEBI)</td>
                <td style="padding: 4px 0; text-align: right; font-size: 0.85rem;">₹{tx['gst']:.2f}</td>
            </tr>
            <tr>
                <td style="padding: 4px 0; color: {theme_tab_text}; font-size: 0.85rem;">Stamp Duty (0.015% - BUY only)</td>
                <td style="padding: 4px 0; text-align: right; font-size: 0.85rem;">₹{tx['stamp_duty']:.2f}</td>
            </tr>
            <tr style="border-bottom: 1px solid {theme_card_border};">
                <td style="padding: 4px 0; color: {theme_tab_text}; font-size: 0.85rem;">DP Charges (₹13.5 + GST - SELL only)</td>
                <td style="padding: 4px 0; text-align: right; font-size: 0.85rem;">₹{tx['dp_charges']:.2f}</td>
            </tr>
            <tr style="font-weight: 700; font-size: 1.05rem; background-color: rgba(239, 68, 68, 0.03);">
                <td style="padding: 10px 0; color: {theme_text_color};">Total Charges & Taxes</td>
                <td style="padding: 10px 0; text-align: right; color: #EF4444;">₹{tx['total_charges']:.2f}</td>
            </tr>
            <tr style="font-weight: 700; font-size: 1.1rem; border-top: 1px solid {theme_card_border}; background-color: rgba(16, 185, 129, 0.03);">
                <td style="padding: 10px 0; color: {theme_text_color};">Net Settlement Value</td>
                <td style="padding: 10px 0; text-align: right; color: {'#10B981' if tx['trade_type'] == 'BUY' else '#00B386'};">
                    ₹{val + tx['total_charges'] if tx['trade_type'] == 'BUY' else val - tx['total_charges']:,.2f}
                </td>
            </tr>
        </table>
        <div style="font-size: 0.75rem; color: {theme_tab_text}; margin-top: 15px; text-align: center; font-style: italic;">
            * Calculated as per SEBI regulations & Indian stock market delivery equity standards.
        </div>
    </div>
    """, unsafe_allow_html=True)

# -- Helper Functions for Tech Analysis --
def get_tradingview_widget_html(ticker, theme="dark"):
    # Ensure ticker is uppercase and stripped
    ticker = str(ticker).strip().upper()
    
    # Convert yfinance ticker (e.g. RELIANCE.NS or RELIANCE.BO) to TradingView symbol (e.g. NSE:RELIANCE)
    # Note: TradingView blocks embedding of BSE data feeds on third-party websites.
    # To bypass this restriction, we map all Indian tickers (.NS and .BO) to their NSE equivalent.
    if ticker.endswith(".NS") or ticker.endswith(".BO"):
        symbol_name = ticker[:-3]
    else:
        if ":" in ticker:
            symbol_name = ticker.split(":", 1)[1]
        else:
            symbol_name = ticker
            
    # Manual mappings for known discrepancies between yfinance/BSE tickers and TradingView NSE symbols
    ticker_overrides = {
        "MCDOWELL-N": "UNITDSPR",
        "MCDOWELL_N": "UNITDSPR",
        "MCDOWELL": "UNITDSPR",
    }
    
    if symbol_name in ticker_overrides:
        symbol_name = ticker_overrides[symbol_name]
    else:
        # Clean symbol name to match TradingView's naming convention for special characters:
        # 1. Ampersand (&) is valid and kept in NSE TradingView symbols (e.g. M&M, ARE&M)
        # 2. Hyphens (-) are replaced with underscores (e.g. BAJAJ-AUTO -> BAJAJ_AUTO)
        #    EXCEPT when they represent a share series like -B or -RE at the end (e.g. KLBRENG-B)
        if "-" in symbol_name:
            if len(symbol_name) >= 2 and symbol_name[-2] == "-":
                pass
            else:
                symbol_name = symbol_name.replace("-", "_")
        
        # 3. Spaces are replaced with underscores
        symbol_name = symbol_name.replace(" ", "_")
        
    symbol = f"NSE:{symbol_name}"
        
    theme_str = "dark" if theme == "Dark Mode" else "light"
    
    html_code = f"""
    <style>
      html, body {{
        height: 850px !important;
        margin: 0 !important;
        padding: 0 !important;
        overflow: hidden !important;
      }}
      .tradingview-widget-container, #tradingview_chart {{
        height: 850px !important;
        width: 100% !important;
      }}
    </style>
    <div class="tradingview-widget-container">
      <div id="tradingview_chart"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{
        "width": "100%",
        "height": 850,
        "symbol": "{symbol}",
        "interval": "D",
        "timezone": "Asia/Kolkata",
        "theme": "{theme_str}",
        "style": "1",
        "locale": "en",
        "enable_publishing": false,
        "hide_side_toolbar": false,
        "allow_symbol_change": true,
        "container_id": "tradingview_chart",
        "support_host": "https://www.tradingview.com"
      }});
      </script>
    </div>
    """
    return html_code

@st.fragment(run_every=5.0)
def render_live_header(ticker, company_name, card_border, text_color):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1d")
        if not hist.empty:
            current_price = hist['Close'].iloc[-1]
            prev_price = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
            if len(hist) < 2:
                hist5 = stock.history(period="5d")
                if len(hist5) > 1:
                    prev_price = hist5['Close'].iloc[-2]
            price_diff = current_price - prev_price
            price_pct = (price_diff / prev_price) * 100
        else:
            current_price, price_diff, price_pct = 0.0, 0.0, 0.0
    except:
        current_price, price_diff, price_pct = 0.0, 0.0, 0.0
        
    arrow = "▲" if price_diff >= 0 else "▼"
    p_color = "#00B386" if price_diff >= 0 else "#EB5B3C"

    st.markdown(f"""
    <div style="display:flex; align-items:center; justify-content:space-between;
                padding: 20px 0 12px; border-bottom: 1px solid {card_border}; margin-bottom:20px;">
        <div>
            <div style="font-size:0.8rem; color:#8b949e; text-transform:uppercase; letter-spacing:1px;">
                NSE &bull; EQUITY
            </div>
            <div style="font-size:2rem; font-weight:800; color:{text_color};">{company_name}</div>
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

@st.fragment(run_every=5.0)
def render_live_price_metric(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1d")
        if not hist.empty:
            current_p = hist['Close'].iloc[-1]
            prev_p = hist['Close'].iloc[-2] if len(hist) > 1 else current_p
            if len(hist) < 2:
                hist5 = stock.history(period="5d")
                if len(hist5) > 1:
                    prev_p = hist5['Close'].iloc[-2]
            price_chg = current_p - prev_p
            pct_chg = (price_chg / prev_p) * 100
        else:
            current_p, price_chg, pct_chg = 0.0, 0.0, 0.0
    except:
        current_p, price_chg, pct_chg = 0.0, 0.0, 0.0
        
    st.metric("Current Price", f"₹{current_p:.2f}", f"{price_chg:.2f} ({pct_chg:.2f}%)")

def validate_stock_ticker(ticker):
    """Validate if a stock ticker exists and is accessible"""
    try:
        stock = yf.Ticker(ticker)
        # 1. Fetch 1 day of historical data first (uses a light endpoint that is rarely rate-limited)
        hist = stock.history(period="1d")
        if not hist.empty:
            current_price = hist['Close'].iloc[-1]
            
            # 2. Try to get name from the database locally first to avoid stock.info requests
            long_name = None
            for name, t in indian_stocks.ALL_STOCKS.items():
                if t == ticker:
                    long_name = name
                    break
            
            # If not in local dict, try stock.info, but catch exceptions if rate-limited
            if not long_name:
                try:
                    info = stock.info
                    long_name = info.get('longName', ticker)
                except:
                    long_name = ticker
            
            return True, long_name, current_price
            
        # 3. Fallback: If history is empty, check info as a last resort
        info = stock.info
        if info and 'regularMarketPrice' in info:
            return True, info.get('longName', ticker), info.get('regularMarketPrice', 0)
            
        return False, "Invalid ticker or no data available", 0
    except Exception as e:
        # Final fallback in case of rate limits: look up in local dictionary
        try:
            for name, t in indian_stocks.ALL_STOCKS.items():
                if t == ticker:
                    try:
                        hist = yf.Ticker(ticker).history(period="1d")
                        if not hist.empty:
                            return True, name, hist['Close'].iloc[-1]
                    except:
                        pass
                    return True, name, 0.0
        except:
            pass
        return False, f"Error validating ticker: {str(e)}", 0


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
<div style="background: rgba(0, 179, 134, 0.08); border: 1px solid rgba(0, 179, 134, 0.2);
     border-radius: 10px; padding: 10px 14px; margin-bottom: 8px;">
    <div style="font-size:0.75rem; color:#8b949e;">Logged in as</div>
    <div style="font-size:0.95rem; font-weight:700; color:#00B386;">{st.session_state.username}</div>
</div>
""", unsafe_allow_html=True)
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.username = None
    st.rerun()
st.sidebar.markdown("---")
st.sidebar.markdown("**Stock Selection**")

# Get all available stocks for selection
all_stocks = indian_stocks.ALL_STOCKS.copy()
if "Custom/Other (Type Below)" in all_stocks:
    del all_stocks["Custom/Other (Type Below)"]
elif "🔍 Custom/Other (Type Below)" in all_stocks:
    del all_stocks["🔍 Custom/Other (Type Below)"]

# Handle external selections (browse list, watchlist, recents) BEFORE the selectbox is rendered
if 'selected_ticker' in st.session_state:
    ticker = st.session_state.selected_ticker
    selected_company = st.session_state.selected_company
    del st.session_state.selected_ticker
    del st.session_state.selected_company
    st.session_state.current_stock_company = selected_company
elif 'external_selected_company' in st.session_state:
    selected_company = st.session_state.external_selected_company
    ticker = all_stocks.get(selected_company, selected_company)
    del st.session_state.external_selected_company
    st.session_state.current_stock_company = selected_company

if 'current_stock_company' not in st.session_state:
    st.session_state.current_stock_company = "Reliance Industries Ltd"

# Ensure current_stock_company is in all_stocks keys
if st.session_state.current_stock_company not in all_stocks:
    found = False
    for k, v in all_stocks.items():
        if v == st.session_state.current_stock_company:
            st.session_state.current_stock_company = k
            found = True
            break
    if not found:
        # If it's a custom ticker, add it to all_stocks dynamically
        all_stocks[st.session_state.current_stock_company] = st.session_state.current_stock_company

options_list = list(all_stocks.keys())
try:
    default_index = options_list.index(st.session_state.current_stock_company)
except ValueError:
    default_index = 0

selected_company = st.sidebar.selectbox(
    "Search & Select Stock",
    options=options_list,
    index=default_index,
    format_func=lambda x: f"{x} ({all_stocks[x]})" if all_stocks[x] != x else x,
    key="stock_selectbox_key",
    help="Type 2-3 letters of the stock name or ticker to filter"
)

# Update state if changed via selectbox
if selected_company != st.session_state.current_stock_company:
    st.session_state.current_stock_company = selected_company
    st.rerun()

ticker = all_stocks[selected_company]

# Period selector (added to define 'period' and fix NameError)
period = st.sidebar.selectbox(
    "Select Time Period", 
    ["1mo", "3mo", "6mo", "1y", "2y", "5y"], 
    index=3, 
    key="time_period"
)


st.sidebar.markdown("### Browse All Stocks")
with st.sidebar.expander("View all available stocks"):
    st.markdown(f"**Total stocks available:** {len(all_stocks)}")

    # Group stocks by exchange
    nse_stocks = {name: ticker for name, ticker in all_stocks.items() if ticker.endswith('.NS')}
    bse_stocks = {name: ticker for name, ticker in all_stocks.items() if ticker.endswith('.BO')}

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**NSE:** {len(nse_stocks)} stocks")
        if st.button("Load NSE List", key="nse_list"):
            st.session_state.show_nse = True

    with col2:
        st.markdown(f"**BSE:** {len(bse_stocks)} stocks")
        if st.button("Load BSE List", key="bse_list"):
            st.session_state.show_bse = True

    if st.session_state.get('show_nse', False):
        st.markdown("**NSE Stocks:**")
        for name, ticker in sorted(nse_stocks.items())[:50]:  # Show first 50
            if st.button(f"{name} ({ticker})", key=f"nse_{ticker}"):
                st.session_state.selected_ticker = ticker
                st.session_state.selected_company = name
                st.rerun()
        if len(nse_stocks) > 50:
            st.caption(f"... and {len(nse_stocks) - 50} more NSE stocks")

    if st.session_state.get('show_bse', False):
        st.markdown("**BSE Stocks:**")
        for name, ticker in sorted(bse_stocks.items())[:50]:  # Show first 50
            if st.button(f"{name} ({ticker})", key=f"bse_{ticker}"):
                st.session_state.selected_ticker = ticker
                st.session_state.selected_company = name
                st.rerun()
        if len(bse_stocks) > 50:
            st.caption(f"... and {len(bse_stocks) - 50} more BSE stocks")

# Handle stock selection from browse lists
if 'selected_ticker' in st.session_state:
    ticker = st.session_state.selected_ticker
    selected_company = st.session_state.selected_company
    # Clear the selection
    del st.session_state.selected_ticker
    del st.session_state.selected_company

st.sidebar.markdown("---")

if st.sidebar.button("Add to Watchlist", use_container_width=True):
    if auth.add_to_watchlist(st.session_state.username, ticker):
        st.sidebar.success(f"{ticker} added to your watchlist!")
    else:
        st.sidebar.info(f"{ticker} is already in your watchlist.")

# Initialize user preferences in session state
if 'user_favorites' not in st.session_state:
    st.session_state.user_favorites = []

if 'recent_stocks' not in st.session_state:
    st.session_state.recent_stocks = []

# Add to recent stocks
if ticker not in st.session_state.recent_stocks:
    st.session_state.recent_stocks.insert(0, ticker)
    # Keep only last 10
    st.session_state.recent_stocks = st.session_state.recent_stocks[:10]

# Show favorites/watchlist
try:
    watchlist_data = auth.get_watchlist(st.session_state.username)
    if watchlist_data:
        st.sidebar.markdown("### Watchlist")
        for item in watchlist_data[:5]:  # Show first 5
            watch_ticker = item['ticker']
            if st.sidebar.button(f"{watch_ticker}", key=f"watch_{watch_ticker}"):
                company_names = [name for name, t in all_stocks.items() if t == watch_ticker]
                selected_company = company_names[0] if company_names else watch_ticker
                st.session_state.external_selected_company = selected_company
                st.rerun()
except Exception as e:
    pass

# Show recent stocks
if st.session_state.recent_stocks:
    st.sidebar.markdown("### Recently Viewed")
    for recent_ticker in st.session_state.recent_stocks[:5]:  # Show last 5
        if st.sidebar.button(f"{recent_ticker}", key=f"recent_{recent_ticker}"):
            company_names = [name for name, t in all_stocks.items() if t == recent_ticker]
            selected_company = company_names[0] if company_names else recent_ticker
            st.session_state.external_selected_company = selected_company
            st.rerun()
if ticker:
    # Skip yfinance validation request if it's already a known stock in our database to make loading faster
    is_known = False
    for name, t in all_stocks.items():
        if t == ticker:
            is_known = True
            break
            
    if is_known:
        is_valid = True
        validation_msg = ""
        current_price = 0.0
    else:
        with st.spinner("Validating stock ticker..."):
            is_valid, validation_msg, current_price = validate_stock_ticker(ticker)

    if not is_valid:
        st.error(f"Error: {validation_msg}")
        st.info("Tips:\n- Use .NS for NSE stocks (e.g., RELIANCE.NS)\n- Use .BO for BSE stocks (e.g., RELIANCE.BO)\n- Check ticker spelling and exchange")
        st.stop()

    try:
        with st.spinner(f"Crunching advanced market data for {ticker}..."):
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                # Fetch stock prices, news, and info in parallel (approx 3x faster loading)
                future_data = executor.submit(data_fetcher.get_stock_data, ticker, period)
                future_news = executor.submit(data_fetcher.get_stock_news, ticker)
                future_info = executor.submit(data_fetcher.get_stock_info, ticker)
                
                stock_data = future_data.result()
                news_data = future_news.result()
                stock_info = future_info.result()
                
            analyzed_news = sentiment_analyzer.get_news_with_sentiment(news_data) if not news_data.empty else pd.DataFrame()

        if stock_data.empty:
            st.error(f"Could not fetch data for ticker: {ticker}. Please check the symbol.")
        else:
            # Professional live header (auto-updates every 5s)
            render_live_header(ticker, selected_company, card_border, text_color)
            tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
                "Overview", 
                "Technical Analysis", 
                "AI Forecast", 
                "Compare Stocks", 
                "Portfolio Tracker",
                "Strategy Backtester",
                "IPO Zone",
                "Watchlist",
                "Market Signals"
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
                with col1:
                    render_live_price_metric(ticker)
                
                avg_sentiment = 0
                if not analyzed_news.empty:
                    avg_sentiment = analyzed_news['compound'].mean()
                    mood = "Bullish" if avg_sentiment > 0.1 else ("Bearish" if avg_sentiment < -0.1 else "Neutral")
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
                    st.subheader("Company Fundamentals")
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
                    st.subheader("Actionable Signal")
                    
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
                             'bar': {'color': "rgba(59, 130, 246, 0.6)"},
                             'bgcolor': "rgba(0,0,0,0)",
                             'borderwidth': 1,
                             'bordercolor': "gray",
                             'steps': [
                                 {'range': [0, 35], 'color': "rgba(239, 68, 68, 0.4)"}, # Sell
                                 {'range': [35, 65], 'color': "rgba(100, 116, 139, 0.4)"}, # Hold
                                 {'range': [65, 100], 'color': "rgba(16, 185, 129, 0.4)"}], # Buy
                         }
                    ))
                    fig_gauge.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor='rgba(0,0,0,0)', font={'color': font_color_plotly})
                    st.plotly_chart(fig_gauge, use_container_width=True)

                with main_col2:
                    st.subheader("AI Market Summary")
                    # Company business summary
                    if stock_info.get("longBusinessSummary"):
                        with st.expander("About the Company", expanded=False):
                            st.write(stock_info.get("longBusinessSummary")[:500] + "...")
                            
                    if not analyzed_news.empty:
                        pos_count = len(analyzed_news[analyzed_news['compound'] > 0.1])
                        neg_count = len(analyzed_news[analyzed_news['compound'] < -0.1])
                        summary_text = f"Based on analysis of <b>{len(analyzed_news)}</b> recent articles, the market sentiment is "
                        if avg_sentiment > 0.1: summary_text += f"<span style='color: #10b981; font-weight: bold;'>mostly positive</span> with {pos_count} bullish reports. "
                        elif avg_sentiment < -0.1: summary_text += f"<span style='color: #ef4444; font-weight: bold;'>generally negative</span> with {neg_count} bearish reports. "
                        else: summary_text += "<b>mixed</b>. "
                        
                        price_color = "#10b981" if price_change > 0 else "#ef4444"
                        summary_text += f"The stock price is currently <span style='color: {price_color}; font-weight: bold;'>{'up' if price_change > 0 else 'down'} {abs(pct_change):.2f}%</span> from the previous close."
                        
                        st.markdown(f'<div class="ai-summary">{summary_text}</div>', unsafe_allow_html=True)
                    else:
                        st.info("Not enough recent news to generate an AI summary.")

                st.markdown("<br>", unsafe_allow_html=True)
                # Interactive TradingView Chart (with drawing tools)
                st.markdown("### Interactive Chart (with Drawing Tools & Indicators)")
                tv_html = get_tradingview_widget_html(ticker, theme_choice)
                with st.container(key=f"tv_chart_container_{ticker}_{theme_choice.replace(' ', '_').lower()}"):
                    st.components.v1.html(tv_html, height=900)
                
                # News
                st.subheader("Recent Headlines")
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
                            <a href="{row['link']}" target="_blank" style="margin-left: 15px; color: #3B82F6; text-decoration: none; font-size: 0.85rem;">Read Full Article</a></div>
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
                st.subheader("Price Forecast (Machine Learning)")
                st.markdown("Professional predictive modeling utilizing historical values to forecast future price targets with statistical confidence intervals.")
                
                forecast_type = st.radio("Select Forecast Horizon", ["Daily Forecast (Next 3 Days)", "Hourly Forecast (Next 5 Hours)"], horizontal=True)
                
                if "Daily" in forecast_type:
                    with st.spinner("Training ML model on daily data..."):
                        forecast_data = data_fetcher.get_stock_data(ticker, "2y")
                        if forecast_data.empty:
                            st.warning("Could not fetch historical daily data for this stock.")
                            prices = np.array([])
                        else:
                            ts_data = forecast_data[['Date', 'Close']].set_index('Date')
                            ts_data.index = pd.to_datetime(ts_data.index)
                            ts_data = ts_data.groupby(level=0).mean()
                            ts_data = ts_data.resample('B').ffill().dropna()
                            prices = ts_data['Close'].values
                            dates = ts_data.index
                            steps = 3
                else:
                    with st.spinner("Training ML model on intraday data..."):
                        forecast_data = data_fetcher.get_stock_data(ticker, period="7d", interval="1h")
                        if forecast_data.empty:
                            st.warning("Could not fetch historical intraday hourly data for this stock.")
                            prices = np.array([])
                        else:
                            ts_data = forecast_data[['Date', 'Close']].set_index('Date')
                            ts_data.index = pd.to_datetime(ts_data.index)
                            ts_data = ts_data.groupby(level=0).mean()
                            ts_data = ts_data.resample('1H').ffill().dropna()
                            prices = ts_data['Close'].values
                            dates = ts_data.index
                            steps = 5

                if len(prices) >= 10:
                    model_fitted = False
                    model_name = "Holt-Winters Exponential Smoothing"
                    fitted_values = np.array([])
                    
                    # Try Holt-Winters Exponential Smoothing
                    try:
                        freq = 'B' if "Daily" in forecast_type else '1H'
                        series = pd.Series(prices, index=dates)
                        model = ExponentialSmoothing(series, trend='add', seasonal=None, initialization_method="estimated")
                        fit_model = model.fit()
                        forecast = fit_model.forecast(steps)
                        fitted_values = fit_model.fittedvalues.values
                        model_fitted = True
                    except Exception as e:
                        # Fallback to Linear Trend Regression using numpy polyfit
                        x = np.arange(len(prices))
                        slope, intercept = np.polyfit(x, prices, 1)
                        fitted_values = slope * x + intercept
                        
                        future_x = np.arange(len(prices), len(prices) + steps)
                        forecast_vals = slope * future_x + intercept
                        forecast = pd.Series(forecast_vals)
                        model_name = "Linear Trend Regression"
                        model_fitted = False

                    # Residual analysis for standard error estimation
                    residuals = prices - fitted_values
                    sigma = np.std(residuals) if len(residuals) > 0 else (prices[-1] * 0.02)
                    if sigma == 0:
                        sigma = prices[-1] * 0.02
                    
                    # Target forecast dates
                    if "Daily" in forecast_type:
                        forecast_dates = pd.bdate_range(start=dates[-1] + timedelta(days=1), periods=steps)
                    else:
                        forecast_dates = [dates[-1] + timedelta(hours=i) for i in range(1, steps + 1)]
                    
                    forecast.index = forecast_dates
                    
                    # 95% Confidence bounds propagation: SE(h) = sigma * sqrt(h)
                    lower_bounds = []
                    upper_bounds = []
                    for h in range(1, steps + 1):
                        margin = 1.96 * sigma * np.sqrt(h)
                        lower_bounds.append(max(0.1, forecast.iloc[h-1] - margin))
                        upper_bounds.append(forecast.iloc[h-1] + margin)
                    
                    # Calculate Mean Absolute Percentage Error (MAPE) for model evaluation
                    mape = np.mean(np.abs(residuals / prices)) * 100
                    if mape < 1.5:
                        confidence = "High"
                        confidence_color = "#10B981"
                    elif mape < 4.0:
                        confidence = "Medium"
                        confidence_color = "#F59E0B"
                    else:
                        confidence = "Low"
                        confidence_color = "#EF4444"
                        
                    # Calculate Directional Bias
                    start_p = prices[-1]
                    end_p = forecast.iloc[-1]
                    pct_change = ((end_p - start_p) / start_p) * 100
                    
                    if pct_change > 0.5:
                        trend_dir = "Bullish"
                        trend_color = "#00B386"
                    elif pct_change < -0.5:
                        trend_dir = "Bearish"
                        trend_color = "#EB5B3C"
                    else:
                        trend_dir = "Neutral"
                        trend_color = "#F59E0B"

                    # Metrics display columns
                    mc1, mc2, mc3 = st.columns(3)
                    mc1.metric("Model Confidence", f"{confidence}", f"MAPE: {mape:.2f}%", delta_color="normal" if confidence != "Low" else "inverse")
                    mc2.metric("Directional Bias", f"{trend_dir}", f"{pct_change:+.2f}%", delta_color="normal" if trend_dir == "Bullish" else ("inverse" if trend_dir == "Bearish" else "off"))
                    mc3.metric("Projected Target Range", f"₹{end_p:.2f}", f"₹{lower_bounds[-1]:.2f} - ₹{upper_bounds[-1]:.2f}", delta_color="off")
                    
                    # AI Explanation Summary Box
                    st.markdown(f"""
                    <div class="ai-summary" style="border-left: 4px solid {trend_color} !important;">
                        <strong>Forecast Model Insights:</strong> FinTrend fitted a <strong>{model_name}</strong> to the stock's historical close prices. 
                        The model anticipates a <strong>{trend_dir.upper()}</strong> trend over the projection horizon, targeting a final price of <strong>₹{end_p:.2f}</strong> 
                        (95% confidence range: <strong>₹{lower_bounds[-1]:.2f}</strong> to <strong>₹{upper_bounds[-1]:.2f}</strong>). 
                        Historical fit accuracy exhibits a Mean Absolute Percentage Error (MAPE) of <strong>{mape:.2f}%</strong>.
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Plotly chart
                    fig_fc = go.Figure()
                    
                    # Slice historical data for display: last 30 for daily, last 24 for hourly
                    slice_len = min(len(prices), 30 if "Daily" in forecast_type else 24)
                    hist_dates = dates[-slice_len:]
                    hist_prices = prices[-slice_len:]
                    
                    # Historical Price path
                    fig_fc.add_trace(go.Scatter(
                        x=hist_dates, 
                        y=hist_prices, 
                        name='Historical Close', 
                        line=dict(color='#3B82F6', width=2)
                    ))
                    
                    # Combine last historical close point with future steps for continuous rendering
                    fc_x = [dates[-1]] + list(forecast_dates)
                    fc_y = [prices[-1]] + list(forecast.values)
                    fc_upper = [prices[-1]] + upper_bounds
                    fc_lower = [prices[-1]] + lower_bounds
                    
                    # Upper bound (invisible line, used for fill)
                    fig_fc.add_trace(go.Scatter(
                        x=fc_x, 
                        y=fc_upper, 
                        name='Upper 95% Bound', 
                        line=dict(color='rgba(245, 158, 11, 0)', width=0),
                        showlegend=False
                    ))
                    
                    # Lower bound with fill to upper bound
                    fig_fc.add_trace(go.Scatter(
                        x=fc_x, 
                        y=fc_lower, 
                        name='95% Confidence Interval', 
                        line=dict(color='rgba(245, 158, 11, 0)', width=0),
                        fill='tonexty',
                        fillcolor='rgba(245, 158, 11, 0.12)',
                        showlegend=True
                    ))
                    
                    # Projected Trend line
                    fig_fc.add_trace(go.Scatter(
                        x=fc_x, 
                        y=fc_y, 
                        name='Forecast Trend', 
                        line=dict(color='#F59E0B', width=2.5, dash='dash')
                    ))
                    
                    fig_fc.update_layout(
                        template=plotly_template, 
                        height=450, 
                        margin=dict(l=0, r=0, t=25, b=0),
                        paper_bgcolor='rgba(0,0,0,0)', 
                        plot_bgcolor='rgba(0,0,0,0)',
                        legend=dict(orientation="h", y=1.1, x=0.01),
                        xaxis_title="Timeline",
                        yaxis_title="Price (Rs.)"
                    )
                    
                    st.plotly_chart(fig_fc, use_container_width=True)
                    
                    # Forecast Table details
                    st.markdown("### Projection Details Table")
                    forecast_table = pd.DataFrame({
                        "Timeline": [d.strftime("%Y-%m-%d %H:%M" if "Hourly" in forecast_type else "%Y-%m-%d") for d in forecast_dates],
                        "Forecast Price": [f"₹{v:.2f}" for v in forecast.values],
                        "Lower 95% Bound": [f"₹{v:.2f}" for v in lower_bounds],
                        "Upper 95% Bound": [f"₹{v:.2f}" for v in upper_bounds]
                    })
                    st.dataframe(forecast_table, use_container_width=True)
                else:
                    st.warning("Not enough historical price data available to run predictive modeling. Minimum 10 bars required.")

            # ==========================================
            # TAB 4: COMPARE STOCKS
            # ==========================================
            with tab4:
                st.subheader("Compare Stock Performance")
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
                st.subheader("My Personal Portfolio")
                
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
                        p_price_s = st.number_input("Sell Price", min_value=0.01, value=float(current_price))
                        if st.form_submit_button("Sell"):
                            if auth.sell_portfolio_item(st.session_state.username, p_ticker_s, p_shares_s, p_price_s):
                                st.success(f"Sold {p_shares_s} shares of {p_ticker_s}!")
                                st.rerun()
                            else:
                                st.error("Failed to sell asset. Check your holdings.")
                                
                # Fetch data
                transactions = auth.get_transactions(st.session_state.username)
                
                # Perform chronological calculation of realized P&L, holdings, charges
                realized_gross_pl = 0.0
                total_charges_paid = 0.0
                holdings_calculated = {}
                all_traded_stocks = {}
                
                if transactions:
                    # Sort transactions chronologically
                    sorted_txs = sorted(transactions, key=lambda x: x.get('timestamp', ''))
                    for tx in sorted_txs:
                        t_ticker = tx['ticker'].upper()
                        t_type = tx['trade_type'].upper()
                        t_shares = float(tx['shares'])
                        t_price = float(tx['price'])
                        t_chg = float(tx['total_charges'])
                        
                        total_charges_paid += t_chg
                        
                        if t_ticker not in holdings_calculated:
                            holdings_calculated[t_ticker] = {"shares": 0.0, "avg_price": 0.0}
                        if t_ticker not in all_traded_stocks:
                            all_traded_stocks[t_ticker] = {"total_bought": 0.0, "total_sold": 0.0, "realized_pl": 0.0, "total_charges": 0.0}
                            
                        curr = holdings_calculated[t_ticker]
                        stats = all_traded_stocks[t_ticker]
                        stats["total_charges"] += t_chg
                        
                        if t_type == 'BUY':
                            stats["total_bought"] += t_shares
                            old_shares = curr["shares"]
                            old_avg = curr["avg_price"]
                            new_shares = old_shares + t_shares
                            if new_shares > 0:
                                curr["avg_price"] = (old_shares * old_avg + t_shares * t_price) / new_shares
                            curr["shares"] = new_shares
                        elif t_type == 'SELL':
                            stats["total_sold"] += t_shares
                            avg_buy = curr["avg_price"]
                            trade_realized_pl = t_shares * (t_price - avg_buy)
                            realized_gross_pl += trade_realized_pl
                            stats["realized_pl"] += trade_realized_pl
                            
                            curr["shares"] = max(0.0, curr["shares"] - t_shares)
                            if curr["shares"] == 0.0:
                                curr["avg_price"] = 0.0

                # Fetch active tickers current prices
                active_tickers = [t for t, h in holdings_calculated.items() if h["shares"] > 0]
                current_prices = {}
                if active_tickers:
                    from concurrent.futures import ThreadPoolExecutor
                    
                    def get_single_price(t):
                        try:
                            td = yf.Ticker(t).history(period="1d")
                            if not td.empty:
                                return t, float(td['Close'].iloc[-1])
                        except:
                            pass
                        return t, 0.0
                        
                    with ThreadPoolExecutor(max_workers=10) as executor:
                        results = executor.map(get_single_price, active_tickers)
                        for t, price in results:
                            current_prices[t] = price

                # Calculate unrealized metrics and active holdings table data
                unrealized_gross_pl = 0.0
                total_current_value = 0.0
                total_invested_value = 0.0
                est_sell_charges = 0.0
                active_rows = []
                
                for t in active_tickers:
                    h = holdings_calculated[t]
                    shares = h["shares"]
                    avg_buy = h["avg_price"]
                    cp = current_prices.get(t, 0.0)
                    if cp == 0.0:
                        cp = avg_buy
                    
                    invested = shares * avg_buy
                    curr_val = shares * cp
                    gross_pl = curr_val - invested
                    
                    # Estimate sell charges if liquidated today
                    chg_dict = auth.calculate_charges("SELL", shares, cp)
                    esc = chg_dict["total"]
                    est_sell_charges += esc
                    
                    net_pl = gross_pl - esc
                    ret_pct = (gross_pl / invested) * 100 if invested > 0 else 0.0
                    
                    unrealized_gross_pl += gross_pl
                    total_current_value += curr_val
                    total_invested_value += invested
                    
                    active_rows.append({
                        "Ticker": t,
                        "Shares": f"{shares:.2f}",
                        "Avg Price": f"₹{avg_buy:,.2f}",
                        "Total Invested": f"₹{invested:,.2f}",
                        "Current Price": f"₹{cp:,.2f}",
                        "Current Value": f"₹{curr_val:,.2f}",
                        "Gross P&L": f"₹{gross_pl:,.2f}",
                        "Est. Sell Charges": f"₹{esc:,.2f}",
                        "Net P&L": f"₹{net_pl:,.2f}",
                        "Return %": f"{ret_pct:,.2f}%"
                    })

                total_gross_pl = unrealized_gross_pl + realized_gross_pl
                total_charges_all = total_charges_paid + est_sell_charges
                net_profit_in_hand = total_gross_pl - total_charges_all

                # --- Overview Metrics ---
                st.markdown("### Portfolio Overview")
                m_col1, m_col2, m_col3, m_col4 = st.columns(4)
                
                m_col1.metric("Active Invested Value", f"₹{total_invested_value:,.2f}")
                m_col2.metric("Active Current Value", f"₹{total_current_value:,.2f}", f"₹{unrealized_gross_pl:,.2f} ({ (unrealized_gross_pl / total_invested_value * 100) if total_invested_value > 0 else 0.0 :.2f}%)")
                m_col3.metric(
                    label="Net Profit In Hand",
                    value=f"₹{net_profit_in_hand:,.2f}",
                    delta=f"Gross P&L: ₹{total_gross_pl:,.2f}",
                    delta_color="normal" if net_profit_in_hand >= 0 else "inverse"
                )
                m_col4.metric(
                    label="Total Charges & Taxes",
                    value=f"₹{total_charges_all:,.2f}",
                    delta=f"Est. Sell Chg: ₹{est_sell_charges:,.2f}",
                    delta_color="inverse"
                )

                # --- Active Holdings ---
                st.markdown("### Current Holdings")
                if active_rows:
                    st.dataframe(pd.DataFrame(active_rows), use_container_width=True)
                else:
                    st.info("No active holdings in your portfolio.")

                # --- Traded Stocks Summary ---
                st.markdown("### Traded Stocks Summary")
                if all_traded_stocks:
                    traded_rows = []
                    for t, stats in all_traded_stocks.items():
                        h = holdings_calculated.get(t, {"shares": 0.0})
                        current_shares = h["shares"]
                        gross_realized = stats["realized_pl"]
                        chg_paid = stats["total_charges"]
                        net_realized = gross_realized - chg_paid
                        
                        traded_rows.append({
                            "Ticker": t,
                            "Total Bought": f"{stats['total_bought']:.2f}",
                            "Total Sold": f"{stats['total_sold']:.2f}",
                            "Current Position": f"{current_shares:.2f}",
                            "Realized Gross P&L": f"₹{gross_realized:,.2f}",
                            "Charges Paid": f"₹{chg_paid:,.2f}",
                            "Net Realized P&L": f"₹{net_realized:,.2f}"
                        })
                    st.dataframe(pd.DataFrame(traded_rows), use_container_width=True)
                else:
                    st.info("No transaction history available.")

                # --- Transaction History ---
                st.markdown("### Detailed Transaction History")
                if transactions:
                    tx_display = []
                    for idx, tx in enumerate(transactions):
                        val = tx["shares"] * tx["price"]
                        tx_display.append({
                            "Index": idx + 1,
                            "Date & Time": tx["timestamp"],
                            "Ticker": tx["ticker"],
                            "Action": tx["trade_type"],
                            "Shares": f"{tx['shares']:.2f}",
                            "Price": f"₹{tx['price']:,.2f}",
                            "Trade Value": f"₹{val:,.2f}",
                            "Total Charges": f"₹{tx['total_charges']:,.2f}"
                        })
                    st.dataframe(pd.DataFrame(tx_display), use_container_width=True)
                    
                    st.markdown("#### 🔍 Tax Invoice & Charges Bifurcation")
                    tx_options = [f"#{idx + 1}: {tx['trade_type']} {tx['shares']:.2f} {tx['ticker']} @ ₹{tx['price']} on {tx['timestamp']}" for idx, tx in enumerate(transactions)]
                    selected_tx_str = st.selectbox("Select a transaction to inspect charges invoice", tx_options)
                    if selected_tx_str:
                        selected_idx = tx_options.index(selected_tx_str)
                        selected_tx = transactions[selected_idx]
                        render_charges_invoice(selected_tx)
                else:
                    st.info("No transactions logged yet.")

            # ==========================================
            # TAB 6: BACKTESTER
            # ==========================================
            with tab6:
                st.subheader("Strategy Backtester")
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
                    fig_bt.add_trace(go.Scatter(x=bt_data['Date'], y=cumulative_strategy, name="Strategy Return", line=dict(color='#00B386', width=3)))
                    
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
                st.subheader("NSE & BSE IPO Zone")
                st.markdown("Track active, ongoing, upcoming, and recently listed Initial Public Offerings (IPOs) in real-time.")
                
                with st.spinner("Fetching real-time IPO data from Moneycontrol..."):
                    try:
                        ipo_dict = data_fetcher.get_live_ipo_data()
                    except Exception as e:
                        st.error("Error connecting to real-time IPO feed. Showing fallback data.")
                        ipo_dict = {
                            "ongoing": pd.DataFrame(),
                            "listed": pd.DataFrame(),
                            "upcoming": pd.DataFrame()
                        }
                    
                ongoing_df = ipo_dict.get("ongoing", pd.DataFrame())
                listed_df = ipo_dict.get("listed", pd.DataFrame())
                upcoming_df = ipo_dict.get("upcoming", pd.DataFrame())
                
                upcoming_col, ongoing_col, listed_col = st.columns(3)
                
                with upcoming_col:
                    st.markdown("### Upcoming IPOs (DRHP Filed)")
                    if upcoming_df.empty:
                        st.info("No upcoming DRHP filings found.")
                    else:
                        for idx, row in upcoming_df.iterrows():
                            company_name = row.get("Company Name", "N/A")
                            filing_date = row.get("DRHP Filing Date", "TBD")
                            st.markdown(f"""
                            <div class="news-card" style="padding: 15px; border-left: 4px solid #F59E0B; margin-bottom: 12px;">
                                <h4 style="margin: 0 0 6px 0; font-size: 1rem; font-weight: 600; color: {text_color};">{company_name}</h4>
                                <div style="font-size: 0.85rem; color: {tab_text};">DRHP Filed: {filing_date}</div>
                            </div>
                            """, unsafe_allow_html=True)

                with ongoing_col:
                    st.markdown("### Ongoing / Open IPOs")
                    if ongoing_df.empty:
                        st.info("No active open IPOs at this time.")
                    else:
                        for idx, row in ongoing_df.iterrows():
                            company_name = row.get("Company Name", "N/A")
                            segment = row.get("Segment", "Mainline")
                            issue_price = row.get("Issue Price", "TBD")
                            subscription = row.get("Subscription", "-")
                            listing_date = row.get("Listing Date", "TBD")
                            st.markdown(f"""
                            <div class="news-card" style="padding: 15px; border-left: 4px solid #3B82F6; margin-bottom: 12px;">
                                <h4 style="margin: 0 0 6px 0; font-size: 1rem; font-weight: 600; color: {text_color};">{company_name}</h4>
                                <div style="display: flex; gap: 8px; margin-bottom: 6px;">
                                    <span class="sentiment-badge badge-neutral" style="font-size: 0.7rem; padding: 2px 6px;">{segment}</span>
                                    <span class="sentiment-badge badge-positive" style="font-size: 0.7rem; padding: 2px 6px; background-color: rgba(59, 130, 246, 0.12); color: #3B82F6; border: 1px solid rgba(59, 130, 246, 0.2);">Active</span>
                                </div>
                                <div style="font-size: 0.85rem; margin-top: 4px;">Price: <strong style="color: {text_color};">{issue_price}</strong></div>
                                <div style="font-size: 0.85rem; margin-top: 2px;">Subscription: <strong style="color: {text_color};">{subscription}</strong></div>
                                <div style="font-size: 0.85rem; margin-top: 2px;">Listing Date: <strong style="color: {text_color};">{listing_date}</strong></div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                with listed_col:
                    st.markdown("### Recently Listed IPOs")
                    if listed_df.empty:
                        st.info("No recently listed IPOs found.")
                    else:
                        for idx, row in listed_df.iterrows():
                            company_name = str(row.get("Company Name", "N/A"))
                            segment = str(row.get("Segment", "Mainline"))
                            listing_date = str(row.get("Listing Date", "TBD"))
                            issue_price = str(row.get("Issue Price", "TBD"))
                            listing_gain = str(row.get("Listing Gain", "-"))
                            ltp = str(row.get("LTP", "-"))
                            
                            # Clean listing gain color logic
                            gain_badge_class = "badge-positive" if "+" in listing_gain or "positive" in listing_gain.lower() else ("badge-negative" if "-" in listing_gain or "negative" in listing_gain.lower() else "badge-neutral")
                            
                            st.markdown(f"""
                            <div class="news-card" style="padding: 15px; border-left: 4px solid #10B981; margin-bottom: 12px;">
                                <h4 style="margin: 0 0 6px 0; font-size: 1rem; font-weight: 600; color: {text_color};">{company_name}</h4>
                                <div style="display: flex; gap: 8px; margin-bottom: 6px;">
                                    <span class="sentiment-badge badge-neutral" style="font-size: 0.7rem; padding: 2px 6px;">{segment}</span>
                                    <span class="sentiment-badge {gain_badge_class}" style="font-size: 0.7rem; padding: 2px 6px;">Gain: {listing_gain}</span>
                                </div>
                                <div style="font-size: 0.85rem; margin-top: 4px;">Listed on: <strong style="color: {text_color};">{listing_date}</strong></div>
                                <div style="font-size: 0.85rem; margin-top: 2px;">Issue Price: <strong style="color: {text_color};">{issue_price}</strong></div>
                                <div style="font-size: 0.85rem; margin-top: 2px;">LTP: <strong style="color: {text_color};">{ltp}</strong></div>
                            </div>
                            """, unsafe_allow_html=True)

            # ==========================================
            # TAB 8: WATCHLIST
            # ==========================================
            with tab8:
                st.subheader("My Watchlist")
                watchlist = auth.get_watchlist(st.session_state.username)
                
                if not watchlist:
                    st.info("Your watchlist is empty. Search for a stock and click 'Add to Watchlist' in the sidebar.")
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
                                if st.button("Remove", key=f"rm_{w_ticker}"):
                                    auth.remove_from_watchlist(st.session_state.username, w_ticker)
                                    st.rerun()
                            st.markdown("---")
                            
            # ==========================================
            # TAB 9: MARKET SIGNALS (Rise/Fall Predictor)
            # ==========================================
            with tab9:
                st.subheader("Dynamic Market Signal Scanner")
                st.markdown("AI-powered scanner that analyzes **RSI, MACD, and Moving Averages** to predict whether each stock is likely to Rise or Fall.")
                st.markdown("---")

                def get_signal_score(df):
                    """Returns a score -100 to +100. Positive = Bullish, Negative = Bearish."""
                    if df.empty or len(df) < 30:
                        return None, "Neutral", ""
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
                        return score, "Rise", ""
                    elif score <= -30:
                        return score, "Fall", ""
                    else:
                        return score, "Neutral", ""

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

                if st.button("Run Signal Scan", use_container_width=True):
                    scan_list = stocks_to_scan if stocks_to_scan else all_stock_names[:20]
                    results = []

                    progress = st.progress(0, text="Running bulk market scan...")
                    ticker_list = [indian_stocks.ALL_STOCKS[name] for name in scan_list if name in indian_stocks.ALL_STOCKS]
                    
                    try:
                        # Fetch all tickers in a single bulk request to prevent rate-limiting on Streamlit Cloud
                        bulk_data = yf.download(
                            tickers=ticker_list,
                            period=scan_period,
                            interval="1d",
                            group_by='ticker',
                            threads=True,
                            progress=False
                        )
                        
                        for i, stock_name in enumerate(scan_list):
                            t = indian_stocks.ALL_STOCKS.get(stock_name)
                            if not t:
                                continue
                                
                            # Extract single stock DataFrame from bulk data
                            df_scan = pd.DataFrame()
                            if isinstance(bulk_data.columns, pd.MultiIndex):
                                ticker_level = 1
                                if 'Ticker' in bulk_data.columns.names:
                                    ticker_level = bulk_data.columns.names.index('Ticker')
                                try:
                                    df_scan = bulk_data.xs(t, level=ticker_level, axis=1).copy()
                                except:
                                    pass
                            else:
                                df_scan = bulk_data.copy()
                                    
                            if not df_scan.empty:
                                df_scan.dropna(subset=['Close'], inplace=True)
                                
                            if not df_scan.empty and 'Close' in df_scan.columns:
                                df_scan.reset_index(inplace=True)
                                if 'Date' in df_scan.columns:
                                    df_scan['Date'] = pd.to_datetime(df_scan['Date']).dt.tz_localize(None)
                                    
                                score, signal, emoji = get_signal_score(df_scan)
                                if score is not None:
                                    cur_p = df_scan['Close'].iloc[-1]
                                    prev_p = df_scan['Close'].iloc[-2] if len(df_scan) > 1 else cur_p
                                    day_chg = ((cur_p - prev_p) / prev_p) * 100
                                    results.append({
                                        "Company": stock_name,
                                        "Ticker": t,
                                        "Price": cur_p,
                                        "Day Change %": day_chg,
                                        "Signal": signal,
                                        "Score": score
                                    })
                            progress.progress((i + 1) / len(scan_list), text=f"Processed {stock_name}...")
                    except Exception as scan_err:
                        st.error(f"Bulk scan error: {str(scan_err)}")
                        
                    progress.empty()

                    if results:
                        results_df = pd.DataFrame(results).sort_values("Score", ascending=False)

                        # Summary row
                        bullish_count = len(results_df[results_df["Signal"] == "Rise"])
                        bearish_count = len(results_df[results_df["Signal"] == "Fall"])
                        neutral_count = len(results_df[results_df["Signal"] == "Neutral"])

                        m1, m2, m3 = st.columns(3)
                        m1.metric("Bullish Stocks", bullish_count)
                        m2.metric("Bearish Stocks", bearish_count)
                        m3.metric("Neutral Stocks", neutral_count)
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
                                    <div style="font-size:1.15rem; font-weight:600; display:flex; align-items:center;">
                                        <span style="display:inline-block; width:10px; height:10px; border-radius:50%; background-color:{border_color}; margin-right:8px;"></span>
                                        <strong>{row_data['Company'][:20]}</strong>
                                    </div>
                                    <div style="font-size:0.8rem; color:#94a3b8; margin-top:2px;">{row_data['Ticker']}</div>
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
                    st.info("Select stocks above and click 'Run Signal Scan' to see predictions.")

    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
