import streamlit as st
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import func
import plotly.express as px
import sys
import os

# Ensure src is in path
sys.path.append(os.getcwd())

from src.database import SessionLocal, Price, Trade, RunLog, News
from src.constants import Mode

st.set_page_config(page_title="Trading Bot v2.0", layout="wide")

st.title("Event-Based Trading Bot v2.0 🚀")

# DB Connection
def get_db():
    return SessionLocal()

db = get_db()

import time

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["🔴 Live Monitor", "📊 Backtest Results", "🗄️ Data Health", "🛠️ System Logs"])

with tab1:
    st.header("Live Trading Monitor")
    
    col_a, col_b = st.columns([1, 3])
    with col_a:
        refresh = st.toggle("Auto-Refresh (5s)", value=True)
    
    if refresh:
        time.sleep(5)
        st.rerun()

    # Metrics
    today_start = pd.Timestamp.utcnow().floor('D')
    
    # Live Trades (PAPER or LIVE)
    trades_query = db.query(Trade).filter(
        Trade.mode.in_([Mode.LIVE, Mode.PAPER]),
        Trade.timestamp >= today_start
    ).order_by(Trade.timestamp.desc())
    
    trades_df = pd.read_sql(trades_query.statement, db.bind)
    
    # Calculate Daily PnL
    daily_pnl = trades_df['pnl'].sum() if not trades_df.empty else 0.0
    daily_trades = len(trades_df)
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Daily PnL", f"₹{daily_pnl:.2f}", delta=f"{daily_pnl:.2f}")
    m2.metric("Trades Today", daily_trades)
    
    # Active Runs
    st.subheader("Active Runs")
    runs = pd.read_sql(db.query(RunLog).filter(RunLog.mode.in_([Mode.LIVE, Mode.PAPER])).order_by(RunLog.start_time.desc()).limit(3).statement, db.bind)
    st.dataframe(runs, hide_index=True)
    
    st.subheader("Recent Trades")
    st.dataframe(trades_df, hide_index=True, use_container_width=True)

with tab2:
    st.header("Backtest Results")
    # In v3, we can have a selector to run backtest from UI.
    # For now, this tab can show results of BACKTEST mode runs if we stored them?
    # Or just placeholder.
    st.write("Backtest reports are generated in console currently.")
    st.markdown("""
    To run a backtest:
    ```bash
    python scripts/run_backtest.py --days 60 --universe NIFTY_NEXT50
    ```
    """)

with tab3:
    st.header("Data Health")
    
    # Stats
    total_prices = db.query(func.count(Price.ticker)).scalar()
    total_news = db.query(func.count(News.url)).scalar()
    
    col1, col2 = st.columns(2)
    col1.metric("Total Price Records", total_prices)
    col2.metric("Total News Articles", total_news)
    
    st.subheader("Latest Data per Ticker")
    # Group by ticker, max(timestamp)
    # This is a bit heavy for SQL, so simplistic query:
    query = """
    SELECT ticker, MAX(timestamp) as last_update, COUNT(*) as count 
    FROM prices 
    GROUP BY ticker 
    ORDER BY last_update DESC
    """
    try:
        freshness = pd.read_sql(query, db.bind)
        st.dataframe(freshness)
    except:
        st.error("Could not fetch data freshness stats.")

with tab4:
    st.header("System Logs")
    # Show last 20 Run Logs
    logs = pd.read_sql(db.query(RunLog).order_by(RunLog.start_time.desc()).limit(20).statement, db.bind)
    st.dataframe(logs)

db.close()