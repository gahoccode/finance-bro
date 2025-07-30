import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from vnstock import Vnstock
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.transform import factor_cmap
from bokeh.palettes import Spectral6
import altair as alt

st.set_page_config(page_title="Stock Price Analysis", page_icon="📈")

st.title("📈 Stock Price Analysis")

# Sidebar for user inputs
with st.sidebar:
    st.header("Settings")
    ticker = st.text_input("Stock Ticker Symbol:", value="REE", placeholder="e.g., VIC, VNM, VCB")
    start_date = st.date_input("Start Date:", value=pd.to_datetime('2024-01-01'))
    end_date = st.date_input("End Date:", value=pd.to_datetime('2024-12-31'))

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
            
            # Show basic statistics at the top
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Latest Close", f"{stock_price['close'].iloc[-1]:,.0f} VND")
            with col2:
                st.metric("Average Close", f"{stock_price['close'].mean():,.0f} VND")
            with col3:
                st.metric("Price Change", f"{stock_price['close'].iloc[-1] - stock_price['close'].iloc[0]:,.0f} VND")
            
            # Create interactive line chart with Altair
            st.subheader("Close Price Over Time")
            
            # Prepare data for Altair
            line_data = stock_price.reset_index()
            line_data = line_data.rename(columns={'time': 'date', 'close': 'price'})
            
            # Create Altair chart
            line_chart = alt.Chart(line_data).mark_line(
                color='black',
                strokeWidth=2
            ).encode(
                x=alt.X('date:T', title='Date'),
                y=alt.Y('price:Q', title='Close Price (VND)', 
                       axis=alt.Axis(format=',.0f')),
                tooltip=[
                    alt.Tooltip('date:T', title='Date'),
                    alt.Tooltip('price:Q', title='Close Price', format=',.0f')
                ]
            ).properties(
                width='container',
                height=400,
                title=f'{ticker} - Close Price Over Time'
            ).interactive()
            
            # Display the Altair chart
            st.altair_chart(line_chart, use_container_width=True)
            
            # Create candlestick chart with Bokeh
            st.subheader("Candlestick Chart")
            
            # Prepare data for Bokeh
            stock_price_bokeh = stock_price_mpf.copy()
            stock_price_bokeh['date'] = stock_price_bokeh.index
            
            # Calculate candlestick properties
            stock_price_bokeh['color'] = ['green' if close >= open_price else 'red' 
                                          for close, open_price in zip(stock_price_bokeh['Close'], stock_price_bokeh['Open'])]
            
            # Create Bokeh figure
            p = figure(
                x_axis_type='datetime',
                title=f'{ticker} - Candlestick Chart',
                width=800,
                height=400,
                tools="pan,wheel_zoom,box_zoom,reset,save",
                toolbar_location="above"
            )
            
            # Add segments for high-low range
            p.segment(
                x0='date', y0='High', 
                x1='date', y1='Low',
                source=stock_price_bokeh,
                color='black',
                line_width=1
            )
            
            # Add rectangles for open-close range
            p.vbar(
                x='date',
                width=12*60*60*1000,  # 12 hours in milliseconds
                top='Open',
                bottom='Close',
                source=stock_price_bokeh,
                fill_color='color',
                line_color='black',
                line_width=1
            )
            
            # Customize the plot
            p.yaxis.axis_label = 'Price (VND)'
            p.xaxis.axis_label = 'Date'
            p.grid.grid_line_alpha = 0.3
            
            # Add hover tool
            hover = HoverTool(
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
            p.add_tools(hover)
            
            # Display the Bokeh chart
            st.bokeh_chart(p, use_container_width=True)
                
    except Exception as e:
        st.error(f"Error loading data for {ticker}: {str(e)}")
        st.info("Please check if the ticker symbol is correct and try again.")

# Footer
st.markdown("---")
st.caption("Data provided by Vnstock API")
