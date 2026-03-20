
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os

# Path to DB
start_path = os.getcwd()
db_path = os.path.join(start_path, "trading_bot.db")
print(f"Checking DB at: {db_path}")

engine = create_engine(f"sqlite:///{db_path}")
Session = sessionmaker(bind=engine)
session = Session()

try:
    print("--- TRADES INSPECTION ---")
    # Select first 5 trades
    trades = session.execute(text("SELECT id, timestamp, ticker, mode, pnl FROM trades LIMIT 5")).fetchall()
    
    for t in trades:
        print(f"ID: {t.id}, Time: {t.timestamp}, Ticker: {t.ticker}, Mode: '{t.mode}', PnL: {t.pnl}")
        
    # Check distinct modes
    modes = session.execute(text("SELECT DISTINCT mode FROM trades")).fetchall()
    print(f"Distinct Modes: {modes}")

except Exception as e:
    print(f"Error: {e}")
finally:
    session.close()
