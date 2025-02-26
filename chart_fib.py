import yfinance as yf
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import numpy as np
import mplfinance as mpf

def create_chart(ticker):
    aapl = yf.Ticker(ticker)
    end_date = datetime.datetime.today()
    start_date = end_date - datetime.timedelta(days=250)  # Fetch 250 days to ensure enough data
    df = aapl.history(start=start_date, end=end_date)

    # Ensure enough data exists
    if df.empty or len(df) < 60:
        print("Not enough data available for calculations.")
    else:
        # Calculate 2-month high and low (last 60 days)
        df_2m = df.tail(60)
        high_2m = df_2m['High'].max()
        low_2m = df_2m['Low'].min()


        # Calculate moving averages
        df['SMA_50'] = df['Close'].rolling(window=10).mean()
        df['SMA_200'] = df['Close'].rolling(window=50).mean()

        # Drop rows with NaN values in SMA columns
        df.dropna(inplace=True)
        df_last_60 = df.tail(60)


        # Calculate 60-day high and low
        high = float(df_last_60['High'].max())  # Convert to float
        low = float(df_last_60['Low'].min())  # Convert to float
        fib_0_7 = high - (high - low) * 0.7
        fib_0_786 = high - (high - low) * 0.786

        # Set the index as datetime for mplfinance
        df.index = pd.to_datetime(df.index)

        # Plot candlestick chart
        #mpf.plot(df, type='candle', style='charles', volume=False, title=f"{ticker} - Last 60 Days Candlestick Chart", ylabel='Price (USD)')

        # Plot candlestick chart with Fibonacci levels
        fig, ax = plt.subplots()
        mpf.plot(df_last_60, type='candle', style='default', ax=ax)
        
        # Add horizontal lines for Fibonacci levels
        ax.axhline(y=fib_0_786, color='orange', linestyle='dashed', linewidth=1.5)
        ax.axhline(y=fib_0_7, color='brown', linestyle='dashed', linewidth=1.5)
        
        # Set title and labels
        ax.set_title(f"{ticker} Chart")
        ax.set_ylabel("Price (USD)")
        
        # Show legend
        ax.legend()
        
        # Save the plot
        plt.savefig("chart.png")
        plt.close()

# Define the ticker


ticker = "RCL"
create_chart("RCL")