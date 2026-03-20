import requests
from datetime import datetime
from sqlalchemy.orm import Session
from src.database import News
from src.utils.time import now_utc
from src.utils.config import load_config
import structlog

logger = structlog.get_logger()

MARKETAUX_URL = "https://api.marketaux.com/v1/news/all"

class NewsManager:
    def __init__(self, db: Session):
        self.db = db
        self.config = load_config()
        self.api_token = self.config.api_keys.marketaux
        
    def fetch_latest_news(self, tickers: str = None, limit: int = 5) -> int:
        """
        Fetch news from MarketAux and store.
        tickers: comma separated list of symbols (or generic market news if None)
        """
        if not self.api_token:
            logger.warning("missing_marketaux_key", msg="Skipping news fetch")
            return 0
            
        params = {
            'api_token': self.api_token,
            'language': 'en',
            'limit': limit,
            # 'symbols': tickers, # Need to map NS tickers to US/Global equivalents if possible, or search query.
            # MarketAux often needs 'Reliance Industries' instead of 'RELIANCE.NS'.
            # For Phase 1, we might just query generic market news or specific query.
            # 'search': 'India Stock Market' 
        }
        
        try:
            response = requests.get(MARKETAUX_URL, params=params, timeout=10)
            data = response.json()
            
            if 'data' not in data:
                logger.error("marketaux_error", response=data)
                return 0
                
            new_count = 0
            for item in data['data']:
                # Dedupe by URL
                exists = self.db.query(News).filter_by(url=item['url']).first()
                if exists:
                    continue
                    
                # MarketAux gives 'sentiment_score' inside 'entities' or 'sentiment' object
                # Fallback to 0 if not present
                score = 0.0
                # Parsing logic depends on exact API response shape (mocking safe default)
                
                n = News(
                    ticker=None, # Global news
                    title=item['title'],
                    source=item['source'],
                    url=item['url'],
                    published_at=datetime.fromisoformat(item['published_at'].replace('Z', '+00:00')),
                    sentiment_score=score
                )
                self.db.add(n)
                new_count += 1
                
            self.db.commit()
            return new_count
            
        except Exception as e:
            logger.error("news_fetch_failed", error=str(e))
            self.db.rollback()
            return 0
