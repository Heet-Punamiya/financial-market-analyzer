import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def get_stock_data(ticker, period="1y", interval="1d"):
    """
    Fetches historical stock price data for a given ticker.
    """
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period, interval=interval)
    hist.reset_index(inplace=True)
    # yfinance sometimes returns timezone-aware dates, standardize them
    if 'Date' in hist.columns:
        hist['Date'] = pd.to_datetime(hist['Date']).dt.tz_localize(None)
    elif 'Datetime' in hist.columns:
        hist.rename(columns={'Datetime': 'Date'}, inplace=True)
        hist['Date'] = pd.to_datetime(hist['Date']).dt.tz_localize(None)
    return hist

def get_stock_news(ticker):
    """
    Fetches recent news articles for a given ticker.
    """
    stock = yf.Ticker(ticker)
    news = stock.news
    
    # Extract relevant fields
    articles = []
    if news:
        for item in news:
            title = item.get('title', '')
            publisher = item.get('publisher', '')
            link = item.get('link', '')
            # Convert timestamp to readable date
            timestamp = item.get('providerPublishTime', None)
            if timestamp:
                published_at = datetime.fromtimestamp(timestamp)
            else:
                published_at = datetime.now()
            
            articles.append({
                'title': title,
                'publisher': publisher,
                'link': link,
                'published_at': published_at
            })
    return pd.DataFrame(articles)

def get_stock_info(ticker):
    """
    Fetches fundamental data and company information for a given ticker.
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return info
    except Exception:
        return {}
