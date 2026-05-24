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
    Fetches recent news articles for a given ticker, handling both new nested
    and old flat structures in yfinance.
    """
    stock = yf.Ticker(ticker)
    news = stock.news
    
    articles = []
    if news:
        for item in news:
            # Check if fields are nested inside a 'content' key (newer yfinance versions)
            content = item.get('content', {}) if 'content' in item else item
            
            title = content.get('title', '')
            
            # Fetch publisher display name
            provider = content.get('provider', {})
            if isinstance(provider, dict):
                publisher = provider.get('displayName', '')
            else:
                publisher = content.get('publisher', '')
            if not publisher:
                publisher = content.get('publisher', '')
            if not publisher:
                publisher = 'Market News'
                
            # Fetch redirect URL
            click_through = content.get('clickThroughUrl', {})
            if isinstance(click_through, dict):
                link = click_through.get('url', '')
            else:
                link = ''
            if not link:
                link = content.get('canonicalUrl', '')
            if not link:
                link = content.get('link', '')
                
            # Fetch and parse publish date
            published_at = None
            pub_date = content.get('pubDate', '')
            if pub_date:
                try:
                    published_at = pd.to_datetime(pub_date).to_pydatetime()
                    if published_at.tzinfo is not None:
                        published_at = published_at.replace(tzinfo=None)
                except:
                    pass
            
            if not published_at:
                timestamp = content.get('providerPublishTime', None)
                if timestamp:
                    try:
                        published_at = datetime.fromtimestamp(timestamp)
                    except:
                        published_at = datetime.now()
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

