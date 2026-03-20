
import sqlite3
import pandas as pd
from datetime import datetime

conn = sqlite3.connect('trading_bot.db')
today = datetime.now().strftime('%Y-%m-%d')
query = f"SELECT count(*) as count FROM trades WHERE mode='LIVE' AND timestamp >= '{today}'"
try:
    df = pd.read_sql_query(query, conn)
    print(f"Trades Today ({today}): {df.iloc[0]['count']}")
    
    # Also show last 3 trades
    q2 = "SELECT timestamp, ticker, mode, pnl FROM trades WHERE mode='LIVE' ORDER BY timestamp DESC LIMIT 3"
    print("\nLast 3 Trades:")
    print(pd.read_sql_query(q2, conn))
except Exception as e:
    print(e)
finally:
    conn.close()
