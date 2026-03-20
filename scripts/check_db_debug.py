
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
    print("--- START DEBUG ---")
    # Check Trade count
    result_trades = session.execute(text("SELECT count(*) FROM trades")).scalar()
    print(f"Total Trades: {result_trades}")
    
    # Check Report count
    try:
        result_reports = session.execute(text("SELECT count(*) FROM reports")).scalar()
        print(f"Total Reports: {result_reports}")
        
        if result_reports > 0:
            # Check modes
            modes = session.execute(text("SELECT DISTINCT mode FROM reports")).fetchall()
            print(f"Available Report Modes: {modes}")
    except Exception as e:
        print(f"Error checking reports: {e}")

    print("--- END DEBUG ---")

except Exception as e:
    print(f"Error: {e}")
finally:
    session.close()
