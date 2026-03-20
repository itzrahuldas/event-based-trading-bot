import pandas as pd
import matplotlib.pyplot as plt
from strategy import generate_signals

def run_backtest_and_plot(ticker='RELIANCE.NS', period='3mo'):
    """
    Runs the strategy and plots the results.
    """
    print(f"Running backtest for {ticker} over {period}...")
    
    # 1. Get Data with Signals
    df = generate_signals(ticker, period=period)
    
    if df.empty:
        print("No data to plot.")
        return

    # 2. Plotting
    plt.figure(figsize=(14, 7))
    
    # Plot Close Price
    plt.plot(df.index, df['Close'], label='Close Price', color='skyblue', linewidth=2)
    
    # Extract Buy and Sell Signals
    buy_signals = df[df['Signal'] == 'BUY']
    sell_signals = df[df['Signal'] == 'SELL']
    
    # Plot Buy Signals (Green Triangles)
    if not buy_signals.empty:
        plt.scatter(buy_signals.index, buy_signals['Close'], 
                    marker='^', color='green', s=150, label='BUY Signal', zorder=5)
        
    # Plot Sell Signals (Red Triangles)
    if not sell_signals.empty:
        plt.scatter(sell_signals.index, sell_signals['Close'], 
                    marker='v', color='red', s=150, label='SELL Signal', zorder=5)

    plt.title(f'Event-Based Trading Strategy: {ticker}', fontsize=16)
    plt.xlabel('Date')
    plt.ylabel('Price (INR)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Save Plot
    output_file = 'trade_analysis.png'
    plt.savefig(output_file)
    print(f"Plot saved to {output_file}")
    
    # plt.show() # Uncomment if running locally with UI

if __name__ == "__main__":
    try:
        run_backtest_and_plot()
    except Exception as e:
        print(f"Error during backtest: {e}")
