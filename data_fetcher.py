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
    First tries Google News search by company name, and falls back to yfinance.
    """
    import urllib.request
    import urllib.parse
    from xml.etree import ElementTree
    import indian_stocks
    
    articles = []
    
    # 1. Try Google News RSS search by company name
    company_name = ticker
    for name, t in indian_stocks.ALL_STOCKS.items():
        if t == ticker:
            company_name = name
            break
            
    # Clean company name for better search matching
    clean_name = company_name
    for suffix in [" Limited", " Ltd.", " Ltd", " LTD", " Limited.", " incorporated", " inc."]:
        if clean_name.endswith(suffix):
            clean_name = clean_name[:-len(suffix)]
    clean_name = clean_name.strip()
    
    try:
        query = urllib.parse.quote(clean_name + " stock")
        url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
        
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        )
        
        with urllib.request.urlopen(req, timeout=5) as response:
            xml_data = response.read()
            root = ElementTree.fromstring(xml_data)
            
            for item in root.findall('.//item'):
                full_title = item.find('title').text if item.find('title') is not None else ""
                link = item.find('link').text if item.find('link') is not None else ""
                pub_date_str = item.find('pubDate').text if item.find('pubDate') is not None else ""
                
                if not full_title:
                    continue
                    
                # Extract publisher from the source tag if present
                source_elem = item.find('source')
                if source_elem is not None and source_elem.text:
                    publisher = source_elem.text
                    suffix_to_remove = f" - {publisher}"
                    title = full_title
                    if title.endswith(suffix_to_remove):
                        title = title[:-len(suffix_to_remove)]
                else:
                    if " - " in full_title:
                        parts = full_title.rsplit(" - ", 1)
                        title = parts[0]
                        publisher = parts[1]
                    else:
                        title = full_title
                        publisher = "Google News"
                
                published_at = None
                if pub_date_str:
                    try:
                        published_at = pd.to_datetime(pub_date_str).to_pydatetime()
                        if published_at.tzinfo is not None:
                            published_at = published_at.replace(tzinfo=None)
                    except:
                        pass
                if not published_at:
                    published_at = datetime.now()
                    
                articles.append({
                    'title': title,
                    'publisher': publisher,
                    'link': link,
                    'published_at': published_at
                })
    except Exception as e:
        pass
        
    # 2. Fallback to yfinance if Google News returned no articles
    if not articles:
        try:
            stock = yf.Ticker(ticker)
            news = stock.news
            if news:
                for item in news:
                    content = item.get('content', {}) if 'content' in item else item
                    title = content.get('title', '')
                    provider = content.get('provider', {})
                    if isinstance(provider, dict):
                        publisher = provider.get('displayName', '')
                    else:
                        publisher = content.get('publisher', '')
                    if not publisher:
                        publisher = content.get('publisher', '')
                    if not publisher:
                        publisher = 'Market News'
                        
                    click_through = content.get('clickThroughUrl', {})
                    if isinstance(click_through, dict):
                        link = click_through.get('url', '')
                    else:
                        link = ''
                    if not link:
                        link = content.get('canonicalUrl', '')
                    if not link:
                        link = content.get('link', '')
                        
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
        except:
            pass
            
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


def get_live_ipo_data():
    """
    Scrapes real-time IPO data from Moneycontrol with robust mock fallbacks in case of network/parse failures.
    """
    import requests
    import pandas as pd
    import io

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    url = "https://www.moneycontrol.com/ipo/"

    # Default fallbacks
    fallback_ongoing = pd.DataFrame({
        "Company Name": ["Adisoft Technologies", "Citius Transnet InvIT", "Leapfrog Engineering"],
        "Segment": ["Mainline", "InvIT", "SME"],
        "Issue Price": ["Rs.125 - 130", "TBD", "TBD"],
        "Subscription": ["-", "-", "-"],
        "Listing Date": ["TBD", "TBD", "TBD"]
    })

    fallback_listed = pd.DataFrame({
        "Company Name": ["Powerica Ltd", "Vivid Electromech Ltd", "Amir Chand Jagdish"],
        "Segment": ["Mainline", "SME", "Mainline"],
        "Listing Date": ["08 Jun 2026", "08 Jun 2026", "05 Jun 2026"],
        "Issue Price": ["Rs.560.00", "Rs.85.00", "Rs.245.00"],
        "Listing Gain": ["+28.20%", "+45.00%", "+12.50%"],
        "LTP": ["Rs.718.00", "Rs.123.25", "Rs.275.60"]
    })

    fallback_upcoming = pd.DataFrame({
        "Company Name": ["Laser Power and Infra Limited", "Arohan Financial Services", "Matangi Rubber"],
        "DRHP Filing Date": ["03 Jun 2026", "02 Jun 2026", "02 Jun 2026"]
    })

    try:
        r = requests.get(url, headers=headers, timeout=8)
        if r.status_code == 200:
            html = r.text.replace('₹', 'Rs.')
            tables = pd.read_html(io.StringIO(html), flavor='lxml')
            
            ongoing_list = []
            listed_list = []
            upcoming_list = []

            for idx, t in enumerate(tables):
                cols = [str(c).strip().lower() for c in t.columns]
                
                # Check for Upcoming (DRHP Filed)
                if any('drhp filing date' in c or 'drhp' in c for c in cols):
                    for _, row in t.iterrows():
                        name = str(row.get('Company Name', '')).strip()
                        filing_date = str(row.get('DRHP Filing Date', '-')).strip()
                        if name and name != 'nan' and not name.startswith('---'):
                            upcoming_list.append({
                                "Company Name": name,
                                "DRHP Filing Date": filing_date
                            })
                            
                # Check for Recently Listed
                elif any('listing gain' in c or 'ltp' in c for c in cols):
                    for _, row in t.iterrows():
                        name = str(row.get('Company Name', '')).replace(' IPO', '').strip()
                        segment = str(row.get('Unnamed: 1', 'Mainline')).strip()
                        if segment == 'nan':
                            segment = 'Mainline'
                        lst_date = str(row.get('Listing Date', '-')).strip()
                        price = str(row.get('Issue Price', '-')).strip()
                        gain = str(row.get('Listing Gain', '-')).strip()
                        ltp = str(row.get('LTP (Rs.)', '')).strip()
                        if not ltp or ltp == 'nan':
                            ltp = str(row.get('LTP', '-')).strip()
                        if name and name != 'nan' and not name.startswith('---'):
                            listed_list.append({
                                "Company Name": name,
                                "Segment": segment,
                                "Listing Date": lst_date,
                                "Issue Price": price,
                                "Listing Gain": gain,
                                "LTP": ltp
                            })
                            
                # Check for Ongoing (has Total Subscription / Allotment Date)
                elif any('total subscription' in c or 'allotment date' in c or 'refund date' in c for c in cols):
                    # Make sure it's not the listed table (which also has total subscription sometimes)
                    if not any('listing gain' in c or 'ltp' in c for c in cols):
                        for _, row in t.iterrows():
                            name = str(row.get('Company Name', '')).replace(' IPO', '').strip()
                            segment = str(row.get('Unnamed: 1', 'Mainline')).strip()
                            if segment == 'nan':
                                segment = 'Mainline'
                            price = str(row.get('Issue Price', 'TBD')).strip()
                            sub = str(row.get('Total Subscription', '-')).strip()
                            lst_date = str(row.get('Listing Date', '-')).strip()
                            if name and name != 'nan' and not name.startswith('---'):
                                ongoing_list.append({
                                    "Company Name": name,
                                    "Segment": segment,
                                    "Issue Price": price,
                                    "Subscription": sub,
                                    "Listing Date": lst_date
                                })
            
            ongoing_df = pd.DataFrame(ongoing_list)
            listed_df = pd.DataFrame(listed_list)
            upcoming_df = pd.DataFrame(upcoming_list)

            return {
                "ongoing": ongoing_df if not ongoing_df.empty else fallback_ongoing,
                "listed": listed_df if not listed_df.empty else fallback_listed,
                "upcoming": upcoming_df if not upcoming_df.empty else fallback_upcoming
            }
    except Exception as e:
        pass

    return {
        "ongoing": fallback_ongoing,
        "listed": fallback_listed,
        "upcoming": fallback_upcoming
    }

