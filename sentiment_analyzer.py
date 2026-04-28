import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pandas as pd

# Download the VADER lexicon if not already downloaded
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    import ssl
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context
    nltk.download('vader_lexicon', quiet=True)

def analyze_sentiment(texts):
    """
    Analyzes sentiment of a list of strings and returns a list of scores.
    Uses NLTK VADER which is specifically attuned to sentiments expressed in social media and microblogs.
    """
    sia = SentimentIntensityAnalyzer()
    results = []
    
    for text in texts:
        score = sia.polarity_scores(text)
        # score contains: 'neg', 'neu', 'pos', 'compound'
        # compound is normalized between -1 (most extreme negative) and +1 (most extreme positive)
        results.append(score)
        
    return pd.DataFrame(results)

def get_news_with_sentiment(news_df):
    """
    Takes a DataFrame of news and adds sentiment scores.
    """
    if news_df is None or news_df.empty:
        return news_df
        
    if 'title' not in news_df.columns:
        return news_df
        
    sentiments_df = analyze_sentiment(news_df['title'].tolist())
    
    # Combine the dataframes
    result_df = pd.concat([news_df.reset_index(drop=True), sentiments_df.reset_index(drop=True)], axis=1)
    return result_df
