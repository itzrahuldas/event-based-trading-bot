import feedparser
import urllib.parse
from datetime import datetime

def fetch_latest_news(query="India Stock Market"):
    """
    Fetches the latest news headlines from Google News RSS.
    
    Args:
        query (str): The search query (e.g., 'TATASTEEL').
    
    Returns:
        list: A list of headlines (str).
    """
    encoded_query = urllib.parse.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-IN&gl=IN&ceid=IN:en"
    
    print(f"Fetching news for: {query} from {rss_url}")
    
    try:
        feed = feedparser.parse(rss_url)
        headlines = []
        
        # Get top 5 headlines
        for entry in feed.entries[:5]:
            headlines.append(entry.title)
            
        return headlines
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []

if __name__ == "__main__":
    # Test
    news = fetch_latest_news("TATASTEEL")
    print(f"Found {len(news)} headlines:")
    for h in news:
        print(f"- {h}")
