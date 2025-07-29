import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import mplfinance as mpf
from vnstock import Vnstock

st.set_page_config(page_title="Stock Price Analysis", page_icon="📈")

st.title("📈 Stock Price Analysis")

# Sidebar for user inputs
with st.sidebar:
    st.header("Settings")
    ticker = st.text_input("Stock Ticker Symbol:", value="REE", placeholder="e.g., VIC, VNM, VCB")
    start_date = st.date_input("Start Date:", value=pd.to_datetime('2024-01-01'))
    end_date = st.date_input("End Date:", value=pd.to_datetime('2024-12-31'))

if ticker:
    try:
        with st.spinner(f"Loading data for {ticker}..."):
            # Initialize Vnstock
            stock = Vnstock().stock(symbol=ticker, source='VCI')
            
            # Fetch stock data
            stock_price = stock.quote.history(
                symbol=ticker,
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d'),
                interval='1D'
            )
            
            # Set time column as datetime index
            stock_price['time'] = pd.to_datetime(stock_price['time'])
            stock_price = stock_price.set_index('time')
            
            # Rename columns to match mplfinance expected format
            stock_price_mpf = stock_price.rename(columns={
                'open': 'Open',
                'high': 'High',
                'low': 'Low',
                'close': 'Close',
                'volume': 'Volume'
            })
            
            # Show basic statistics at the top
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Latest Close", f"{stock_price['close'].iloc[-1]:,.0f} VND")
            with col2:
                st.metric("Average Close", f"{stock_price['close'].mean():,.0f} VND")
            with col3:
                st.metric("Price Change", f"{stock_price['close'].iloc[-1] - stock_price['close'].iloc[0]:,.0f} VND")
            
            # Create line chart with seaborn
            st.subheader("Close Price Over Time")
            
            # Create figure with seaborn
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Plot close price without grid
            sns.lineplot(
                data=stock_price,
                x=stock_price.index,
                y='close',
                ax=ax,
                color='#1f77b4',
                linewidth=2
            )
            
            # Customize the plot
            ax.set_title(f'{ticker} - Close Price Over Time', fontsize=16, pad=20)
            ax.set_xlabel('Time', fontsize=12)
            ax.set_ylabel('Close Price (VND)', fontsize=12)
            ax.grid(False)  # Remove grid as requested
            
            # Format x-axis to show dates nicely
            fig.autofmt_xdate()
            
            # Display the plot
            st.pyplot(fig)
            
            # Create candlestick chart with mplfinance
            st.subheader("Candlestick Chart")
            
            # Create mplfinance plot
            fig_mpf, axes = mpf.plot(
                stock_price_mpf,
                type='candle',
                style='yahoo',
                title=f'{ticker} - Candlestick Chart',
                ylabel='Price (VND)',
                volume=True,
                figsize=(12, 8),
                returnfig=True
            )
            
            # Display the candlestick chart
            st.pyplot(fig_mpf)
                
    except Exception as e:
        st.error(f"Error loading data for {ticker}: {str(e)}")
        st.info("Please check if the ticker symbol is correct and try again.")

# Footer
st.markdown("---")
st.caption("Data provided by Vnstock API")
