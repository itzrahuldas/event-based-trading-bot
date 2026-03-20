from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Enum, UniqueConstraint, Index, Text, Date, JSON
from sqlalchemy.orm import declarative_base, sessionmaker
from src.constants import Mode, TimeFrame
import os

DB_PATH = "trading_bot.db"
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Check for Postgres env vars
    user = os.getenv("POSTGRES_USER")
    if user:
        pwd = os.getenv("POSTGRES_PASSWORD", "")
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = os.getenv("POSTGRES_PORT", "5432")
        db = os.getenv("POSTGRES_DB", "tradedb")
        DATABASE_URL = f"postgresql://{user}:{pwd}@{host}:{port}/{db}"
    else:
        # Fallback to SQLite
        DATABASE_URL = f"sqlite:///{DB_PATH}"

Base = declarative_base()

class Stock(Base):
    __tablename__ = 'stocks'
    ticker = Column(String, primary_key=True)
    name = Column(String)
    limit = Column(Integer) # Max qty limit if specific

class Price(Base):
    __tablename__ = 'prices'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False) # UTC
    interval = Column(String, default=TimeFrame.M15)
    
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)
    
    # Ensuring unique candle per interval per ticker
    __table_args__ = (
        UniqueConstraint('ticker', 'timestamp', 'interval', name='uix_ticker_ts_interval'),
        Index('idx_price_ticker_ts', 'ticker', 'timestamp'),
    )

class News(Base):
    __tablename__ = 'news'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String, nullable=True) # Can be null for general market news
    title = Column(Text, nullable=False)
    source = Column(String)
    url = Column(String, nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=False)
    sentiment_score = Column(Float) # -1.0 to 1.0
    
    __table_args__ = (
        UniqueConstraint('source', 'url', name='uix_source_url'),
        Index('idx_news_ticker_date', 'ticker', 'published_at'),
    )

from sqlalchemy.orm import declarative_base, sessionmaker, validates

# ... (rest of imports)

class Trade(Base):
    __tablename__ = 'trades'
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    ticker = Column(String, nullable=False)
    side = Column(String, nullable=False) # BUY/SELL
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    pnl = Column(Float, default=0.0)
    reason = Column(String)
    
    mode = Column(String, default=Mode.LIVE)
    strategy_version = Column(String, default="v2.0")
    run_id = Column(String, nullable=True) # Link to RunLog

    __table_args__ = (
        Index('idx_trades_ts_mode', 'timestamp', 'mode'),
    )

    @validates('mode')
    def validate_mode(self, key, value):
        # Allow None if default handles it, but here we want strictness if provided
        if value is None:
            return Mode.LIVE.value
        
        # Auto-uppercase
        upper_val = value.upper()
        if upper_val not in Mode.__members__:
            raise ValueError(f"Invalid mode: {value}. Must be one of {list(Mode.__members__.keys())}")
        return upper_val

# ... (rest of file)

class RunLog(Base):
    __tablename__ = 'runs'
    run_id = Column(String, primary_key=True)
    start_time = Column(DateTime(timezone=True), default=datetime.now)
    end_time = Column(DateTime(timezone=True), nullable=True)
    mode = Column(String)
    status = Column(String) # RUNNING, COMPLETED, FAILED
    error_message = Column(Text, nullable=True)

class Report(Base):
    __tablename__ = 'reports'
    id = Column(Integer, primary_key=True, autoincrement=True)
    report_date = Column(Date, nullable=False)
    universe = Column(String, default="NIFTY50")
    mode = Column(String, default=Mode.LIVE)
    metrics = Column(JSON, nullable=False) 
    created_at = Column(DateTime(timezone=True), default=datetime.now)

    __table_args__ = (
        UniqueConstraint('report_date', 'universe', 'mode', name='uix_report_date_univ_mode'),
    )

# Engine & Session
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    """Create tables. Safe to call multiple times (checkfirst=True)."""
    Base.metadata.create_all(engine)

def get_db():
    """Dependency for DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
