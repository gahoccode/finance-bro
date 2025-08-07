import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from vnstock import Vnstock
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.transform import factor_cmap
from bokeh.palettes import Spectral6
import altair as alt
import os

st.set_page_config(page_title="Stock Price Analysis", layout="wide")

# CSS loading removed

# Get stock symbol from session state (set in main app)
# If not available, show message to use main app first
if 'stock_symbol' in st.session_state and st.session_state.stock_symbol:
    ticker = st.session_state.stock_symbol
else:
    st.warning("⚠️ No stock symbol selected. Please go to the main Finance Bro page and select a stock symbol first.")
    st.stop()

st.title("Stock Price Analysis")

# Sidebar for user inputs
with st.sidebar:
    st.header("Settings")
    st.metric("Current Symbol", ticker)
    start_date = st.date_input("Start Date:", value=pd.to_datetime('2024-01-01'))
    end_date = st.date_input("End Date:", value=pd.to_datetime('2024-12-31'))
    
    # Chart type selector
    chart_type = st.selectbox(
        "Chart Type:", 
        options=["Line Chart", "Area Chart"],
        index=0,
        help="Choose between line chart and area chart with gradient"
    )

@st.cache_data(ttl=3600, show_spinner="Loading stock data...")
def fetch_stock_data(ticker, start_date, end_date):
    """Fetch stock data with caching to prevent repeated API calls."""
    stock = Vnstock().stock(symbol=ticker, source='VCI')
    stock_price = stock.quote.history(
        symbol=ticker,
        start=start_date.strftime('%Y-%m-%d'),
        end=end_date.strftime('%Y-%m-%d'),
        interval='1D'
    )
    
    # Set time column as datetime index
    stock_price['time'] = pd.to_datetime(stock_price['time'])
    stock_price = stock_price.set_index('time')
    
    return stock_price

if ticker:
    try:
        with st.spinner(f"Loading data for {ticker}..."):
            # Fetch cached stock data
            stock_price = fetch_stock_data(ticker, start_date, end_date)
            
            # Rename columns to match mplfinance expected format
            stock_price_mpf = stock_price.rename(columns={
                'open': 'Open',
                'high': 'High',
                'low': 'Low',
                'close': 'Close',
                'volume': 'Volume'
            })
            
            # Calculate returns with data validation
            # Clean price data for returns calculation
            clean_prices = stock_price['close'].dropna()
            clean_prices = clean_prices[clean_prices > 0]  # Remove zero/negative prices
            
            if len(clean_prices) > 1:
                # Calculate log returns
                returns = np.log(clean_prices / clean_prices.shift(1)).dropna()
                
                # Calculate mean return (annualized)
                mean_daily_return = returns.mean()
                annualized_return = mean_daily_return * 252  # 252 trading days per year
                
                # Format as percentage
                mean_return_pct = annualized_return * 100
                
                # Calculate volatility (annualized)
                volatility = returns.std() * np.sqrt(252) * 100
                
            else:
                mean_return_pct = 'Error'
                volatility = 'Error'
            
            # Show returns statistics at the top
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Latest Close", f"{stock_price['close'].iloc[-1]*1000:,.0f}")
            with col2:
                st.metric("Mean Return (Annualized)", f"{mean_return_pct:.2f}%")
            with col3:
                st.metric("Annualized Volatility", f"{volatility:.2f}%")
            
            # Create interactive chart with Altair
            st.subheader("Stock Performance")
            
            # Prepare data for Altair
            chart_data = stock_price.reset_index()
            chart_data = chart_data.rename(columns={'time': 'date', 'close': 'price'})
            
            # Create chart based on selected type
            if chart_type == "Line Chart":
                # Line chart
                stock_chart = alt.Chart(chart_data).mark_line(
                    color='black',
                    strokeWidth=2
                ).encode(
                    x=alt.X('date:T', title='Date'),
                    y=alt.Y('price:Q', title='Close Price (in thousands)', 
                           axis=alt.Axis(format=',.0f')),
                    tooltip=[
                        alt.Tooltip('date:T', title='Date'),
                        alt.Tooltip('price:Q', title='Close Price', format=',.0f')
                    ]
                ).properties(
                    width='container',
                    height=400,
                    title=f'{ticker}'
                ).interactive()
            else:
                # Area chart with gradient
                stock_chart = alt.Chart(chart_data).mark_area(
                    line={'color': '#3C3C3C', 'strokeWidth': 2},
                    color=alt.Gradient(
                        gradient='linear',
                        stops=[
                            alt.GradientStop(color='#3C3C3C', offset=0),
                            alt.GradientStop(color='#807F80', offset=1)
                        ],
                        x1=1, x2=1, y1=1, y2=0
                    )
                ).encode(
                    x=alt.X('date:T', title='Date'),
                    y=alt.Y('price:Q', title='Close Price (in thousands)', 
                           axis=alt.Axis(format=',.0f')),
                    tooltip=[
                        alt.Tooltip('date:T', title='Date'),
                        alt.Tooltip('price:Q', title='Close Price', format=',.0f')
                    ]
                ).properties(
                    width='container',
                    height=400,
                    title=f'{ticker}'
                ).interactive()
            
            # Display the Altair chart
            st.altair_chart(stock_chart, use_container_width=True)
            
            # Create candlestick chart with volume using Bokeh
            st.subheader("Candlestick Chart with Volume")
            
            # Prepare data for Bokeh
            stock_price_bokeh = stock_price_mpf.copy()
            stock_price_bokeh['date'] = stock_price_bokeh.index
            
            # Calculate candlestick properties
            stock_price_bokeh['color'] = ['green' if close >= open_price else 'red' 
                                          for close, open_price in zip(stock_price_bokeh['Close'], stock_price_bokeh['Open'])]
            
            # Create two subplots: price and volume with proper alignment
            from bokeh.layouts import column
            from bokeh.models import LinearAxis, Range1d
            
            # Calculate min/max values for consistent scaling
            min_date = stock_price_bokeh.index.min()
            max_date = stock_price_bokeh.index.max()
            max_volume = stock_price_bokeh['Volume'].max()
            
            # Price chart - use responsive sizing
            price = figure(
                x_axis_type='datetime',
                title=f'{ticker} - Candlestick Chart',
                height=400,
                tools="pan,wheel_zoom,box_zoom,reset,save",
                toolbar_location="above",
                x_range=(min_date, max_date),
                sizing_mode="stretch_width"
            )
            
            # Add segments for high-low range
            price.segment(
                x0='date', y0='High', 
                x1='date', y1='Low',
                source=stock_price_bokeh,
                color='black',
                line_width=1
            )
            
            # Add rectangles for open-close range
            price.vbar(
                x='date',
                width=12*60*60*1000,  # 12 hours in milliseconds
                top='Open',
                bottom='Close',
                source=stock_price_bokeh,
                fill_color='color',
                line_color='black',
                line_width=1
            )
            
            # Customize price plot
            price.yaxis.axis_label = 'Price (in thousands)'
            price.grid.grid_line_alpha = 0.3
            price.xaxis.visible = False  # Hide x-axis labels on price chart
            
            # Volume chart - use same responsive sizing
            volume = figure(
                x_axis_type='datetime',
                height=200,
                tools="pan,wheel_zoom,box_zoom,reset,save",
                toolbar_location=None,
                x_range=price.x_range,  # Link x-axis with price chart
                sizing_mode="stretch_width"
            )
            
            # Add volume bars
            volume.vbar(
                x='date',
                width=12*60*60*1000,
                top='Volume',
                bottom=0,
                source=stock_price_bokeh,
                fill_color='color',
                line_color='black',
                line_width=0.5,
                alpha=0.7
            )
            
            # Customize volume plot
            volume.yaxis.axis_label = 'Volume'
            volume.grid.grid_line_alpha = 0.3
            volume.xaxis.axis_label = 'Date'
            
            # Add hover tools for both charts
            hover_price = HoverTool(
                tooltips=[
                    ('Date', '@date{%F}'),
                    ('Open', '@Open{0,0}'),
                    ('High', '@High{0,0}'),
                    ('Low', '@Low{0,0}'),
                    ('Close', '@Close{0,0}'),
                    ('Volume', '@Volume{0,0}')
                ],
                formatters={'@date': 'datetime'},
                mode='vline'
            )
            price.add_tools(hover_price)
            
            hover_volume = HoverTool(
                tooltips=[
                    ('Date', '@date{%F}'),
                    ('Volume', '@Volume{0,0}')
                ],
                formatters={'@date': 'datetime'},
                mode='vline'
            )
            volume.add_tools(hover_volume)
            
            # Combine charts vertically with proper alignment
            combined_chart = column(price, volume, sizing_mode="stretch_width")
            
            # Display the combined Bokeh chart
            st.bokeh_chart(combined_chart, use_container_width=True)
                
    except Exception as e:
        st.error(f"Error loading data for {ticker}: {str(e)}")
        st.info("Please check if the ticker symbol is correct and try again.")

# Footer
st.markdown("---")
st.caption("Data provided by Vnstock API")
