import yfinance as yf
import pandas as pd

def get_indian_stock_data(ticker, period='1y'):
    """
    Fetches historical data for an Indian stock.
    
    Args:
        ticker (str): Ticker symbol (e.g., 'RELIANCE.NS')
        period (str): Data period (default '1y')
        
    Returns:
        pd.DataFrame: OHLCV data
    """
    print(f"Fetching data for {ticker} over {period}...")
    stock = yf.Ticker(ticker)
    df = stock.history(period=period)
    
    if df.empty:
        print(f"Warning: No data found for {ticker}")
    else:
        print(f"Successfully fetched {len(df)} records.")
        
    return df

if __name__ == "__main__":
    # Test block
    try:
        data = get_indian_stock_data('RELIANCE.NS')
        print("\nLast 5 rows of data:")
        print(data.tail(5))
    except Exception as e:
        print(f"An error occurred: {e}")
