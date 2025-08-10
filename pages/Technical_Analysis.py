import streamlit as st
import pandas as pd
import numpy as np
from vnstock import Screener, Vnstock
import mplfinance as mpf
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import io
import base64

st.set_page_config(
    page_title="Technical Analysis - Finance Bro",
    page_icon="📊",
    layout="wide"
)

def get_heating_up_stocks():
    """Get stocks with heating_up indicator"""
    
    # Initialize screener and get data
    screener = Screener(show_log=False)
    screener_df = screener.stock(
        params={"exchangeName": "HOSE,HNX,UPCOM"},
        limit=1700,
        lang="en"
    )
    
    # Filter for heating_up condition only
    filtered_stocks = screener_df[
        screener_df['heating_up'] == 'Overheated in previous trading session'
    ]
    
    # Select only required columns
    result_columns = [
        'ticker', 'industry', 'exchange', 'heating_up', 'uptrend', 'breakout', 
        'tcbs_buy_sell_signal', 'pct_1y_from_peak', 'pct_away_from_hist_peak', 
        'pct_1y_from_bottom', 'pct_off_hist_bottom', 'active_buy_pct', 'strong_buy_pct', 'market_cap',
        'avg_trading_value_5d', 'total_trading_value', 'foreign_transaction', 'num_increase_continuous_day'
    ]
    
    # Only include columns that exist in the DataFrame
    available_columns = [col for col in result_columns if col in filtered_stocks.columns]
    
    return filtered_stocks[available_columns]

def create_candlestick_chart(ticker, data, title_suffix=""):
    """Create candlestick chart using mplfinance with Finance Bro theme"""
    
    if data.empty:
        return None
    
    # Finance Bro color scheme
    marketcolors = mpf.make_marketcolors(
        up='#76706C',      # Earth tone up
        down='#2B2523',    # Dark earth tone down
        edge='inherit',
        wick={'up':'#76706C', 'down':'#2B2523'},
        volume='in'
    )
    
    style = mpf.make_mpf_style(
        marketcolors=marketcolors,
        gridstyle='',
        y_on_right=True,
        facecolor='white',
        figcolor='white'
    )
    
    # Create figure
    fig, axes = mpf.plot(
        data,
        type='candle',
        style=style,
        title=f'{ticker} - Candlestick Chart{title_suffix}',
        ylabel='Price (VND)',
        volume=True,
        figsize=(12, 8),
        returnfig=True
    )
    
    return fig

def get_stock_data(ticker, days=30):
    """Get historical stock data for the ticker using correct Vnstock API pattern"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Use the same pattern as Stock_Price_Analysis.py
        stock = Vnstock().stock(symbol=ticker, source='VCI')
        data = stock.quote.history(
            symbol=ticker,
            start=start_date.strftime('%Y-%m-%d'),
            end=end_date.strftime('%Y-%m-%d'),
            interval='1D'
        )
        
        if data is not None and not data.empty:
            # Prepare data for mplfinance
            data = data.copy()
            
            # Set time column as datetime index
            if 'time' in data.columns:
                data['time'] = pd.to_datetime(data['time'])
                data = data.set_index('time')
            
            # mplfinance expects specific column names (capitalize first letter)
            column_mapping = {
                'open': 'Open',
                'high': 'High', 
                'low': 'Low',
                'close': 'Close',
                'volume': 'Volume'
            }
            
            # Rename columns to match mplfinance expectations
            data = data.rename(columns=column_mapping)
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            
            # Check if all required columns exist and return them
            if all(col in data.columns for col in required_columns):
                return data[required_columns]
        
        return pd.DataFrame()
        
    except Exception as e:
        st.error(f"Error fetching data for {ticker}: {str(e)}")
        return pd.DataFrame()

def main():
    st.title("📊 Technical Analysis")
    st.markdown("---")
    
    # Page description
    st.markdown("""
    **Technical Analysis** - Discover stocks showing technical heating signals and analyze their price patterns.
    
    This page identifies Vietnamese stocks that are "**Overheated in previous trading session**" according to vnstock technical indicators,
    then displays their candlestick charts for visual technical analysis.
    """)
    
    st.markdown("---")
    
    # Load heating up stocks
    with st.spinner("🔍 Scanning market for heating up stocks..."):
        try:
            heating_stocks = get_heating_up_stocks()
        except Exception as e:
            st.error(f"Error loading heating up stocks: {str(e)}")
            st.stop()
    
    if heating_stocks.empty:
        st.info("🔥 No stocks showing 'Overheated in previous trading session' signal today.")
        st.stop()
    
    # Display results summary
    st.success(f"🔥 Found **{len(heating_stocks)}** stocks with heating up signals!")
    
    # Display the heating stocks DataFrame
    st.subheader("📋 Heating Up Stocks Summary")
    st.dataframe(
        heating_stocks,
        use_container_width=True,
        height=300
    )
    
    # Charts section
    st.subheader("📈 Candlestick Charts")
    st.markdown("Individual candlestick charts for each heating up stock (last 30 days)")
    
    # Create tabs for better organization if many stocks
    tickers = heating_stocks['ticker'].tolist()
    
    if len(tickers) <= 5:
        # Display all charts directly if 5 or fewer stocks
        for ticker in tickers:
            with st.expander(f"📊 {ticker} - Candlestick Chart", expanded=True):
                with st.spinner(f"Loading chart for {ticker}..."):
                    stock_data = get_stock_data(ticker)
                    
                    if not stock_data.empty:
                        fig = create_candlestick_chart(ticker, stock_data)
                        if fig:
                            st.pyplot(fig)
                            plt.close(fig)  # Clean up memory
                    else:
                        st.warning(f"No data available for {ticker}")
    else:
        # Use tabs for many stocks
        tab_chunks = [tickers[i:i+5] for i in range(0, len(tickers), 5)]
        tab_names = [f"Stocks {i*5+1}-{min((i+1)*5, len(tickers))}" for i in range(len(tab_chunks))]
        
        tabs = st.tabs(tab_names)
        
        for tab_idx, tab in enumerate(tabs):
            with tab:
                current_tickers = tab_chunks[tab_idx]
                for ticker in current_tickers:
                    with st.expander(f"📊 {ticker} - Candlestick Chart", expanded=False):
                        with st.spinner(f"Loading chart for {ticker}..."):
                            stock_data = get_stock_data(ticker)
                            
                            if not stock_data.empty:
                                fig = create_candlestick_chart(ticker, stock_data)
                                if fig:
                                    st.pyplot(fig)
                                    plt.close(fig)  # Clean up memory
                            else:
                                st.warning(f"No data available for {ticker}")
    
    # Footer information
    st.markdown("---")
    st.info("""
    **Note:** Charts show the last 30 days of trading data. Heating up signals are based on vnstock technical indicators 
    that identify stocks "Overheated in previous trading session". This is Phase 1 of Technical Analysis - 
    advanced technical indicators will be added in Phase 2.
    """)

if __name__ == "__main__":
    main()