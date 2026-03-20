
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os

# Path to DB
start_path = os.getcwd()
db_path = os.path.join(start_path, "trading_bot.db")

engine = create_engine(f"sqlite:///{db_path}")
Session = sessionmaker(bind=engine)
session = Session()

try:
    print("--- MIGRATION START ---")
    
    # Check count of 'backtest' trades
    cnt = session.execute(text("SELECT count(*) FROM trades WHERE mode = 'backtest'")).scalar()
    print(f"Found {cnt} trades with mode 'backtest'.")
    
    if cnt > 0:
        print("Migrating 'backtest' -> 'LIVE'...")
        session.execute(text("UPDATE trades SET mode = 'LIVE' WHERE mode = 'backtest'"))
        session.commit()
        print("Migration complete.")
    else:
        print("No trades to migrate.")
        
    # Verify
    modes = session.execute(text("SELECT DISTINCT mode FROM trades")).fetchall()
    print(f"Current Modes in DB: {modes}")
    
    print("--- MIGRATION END ---")
except Exception as e:
    print(f"Error: {e}")
    session.rollback()
finally:
    session.close()
