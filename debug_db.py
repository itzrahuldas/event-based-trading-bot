
import sqlite3
import pandas as pd

conn = sqlite3.connect('trading_bot.db')
query = "SELECT timestamp, ticker, mode, pnl FROM trades WHERE mode='LIVE' ORDER BY timestamp DESC LIMIT 5"
try:
    df = pd.read_sql_query(query, conn)
    print(df)
except Exception as e:
    print(e)
finally:
    conn.close()
