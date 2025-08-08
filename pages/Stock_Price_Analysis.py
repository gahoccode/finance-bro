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
import quantstats as qs
from datetime import datetime

st.set_page_config(page_title="Stock Price Analysis", layout="wide")

# Extend pandas functionality with QuantStats
qs.extend_pandas()

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
    
    # Store in session state for cross-page access
    st.session_state.stock_price_data = stock_price
    
    return stock_price

if ticker:
    try:
        with st.spinner(f"Loading data for {ticker}..."):
            # Fetch cached stock data
            stock_price = fetch_stock_data(ticker, start_date, end_date)
            

            
            # Calculate returns using session state data and pct_change method
            # Use the stock_price data stored in session state for consistency across pages
            # Check if session state data exists, otherwise use the just-fetched data
            if 'stock_price_data' in st.session_state:
                session_stock_price = st.session_state.stock_price_data
            else:
                session_stock_price = stock_price
            
            clean_prices = session_stock_price['close'].dropna()
            clean_prices = clean_prices[clean_prices > 0]  # Remove zero/negative prices
            
            if len(clean_prices) > 1:
                # Calculate percentage returns using pct_change() for consistency with Portfolio Optimization
                returns = clean_prices.pct_change().dropna()
                # Store returns in session state for cross-page access
                st.session_state.stock_returns = returns
                
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
            
            # Create metrics tabs including Tearsheet
            st.subheader("Performance Analytics")
            tearsheet_tab, metrics_tab = st.tabs(["📊 Tearsheet", "📈 Quick Metrics"])
            
            with tearsheet_tab:
                st.write("Generate comprehensive performance analytics using QuantStats")
                
                if st.button("Generate Tearsheet", key="generate_tearsheet"):
                    # Check if returns data exists in session state
                    if 'stock_returns' in st.session_state and len(st.session_state.stock_returns) > 0:
                        
                        # Set up exports directory
                        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                        tearsheets_dir = os.path.join(project_root, "exports", "tearsheets")
                        os.makedirs(tearsheets_dir, exist_ok=True)
                        
                        # Generate timestamp and filename
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"{ticker}_tearsheet_{timestamp}.html"
                        filepath = os.path.join(tearsheets_dir, filename)
                        
                        with st.spinner("Generating QuantStats tearsheet..."):
                            try:
                                # Generate HTML tearsheet using QuantStats
                                returns_data = st.session_state.stock_returns
                                
                                # Generate tearsheet HTML and save to disk
                                qs.reports.html(returns_data, output=filepath)
                                
                                # Check if file was created at expected location, if not check project root
                                if not os.path.exists(filepath):
                                    # QuantStats 0.0.59 may save to project root with default name
                                    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                                    default_file = os.path.join(project_root, "quantstats-tearsheet.html")
                                    if os.path.exists(default_file):
                                        # Move file to our desired location
                                        import shutil
                                        shutil.move(default_file, filepath)
                                
                                # Read the generated HTML file for display
                                with open(filepath, 'r', encoding='utf-8') as f:
                                    html_content = f.read()
                                
                                # Success message
                                st.success("✅ Tearsheet generated successfully!")
                                
                                # Display HTML content using iframe for better chart rendering
                                st.subheader("QuantStats Tearsheet")
                                
                                # Use iframe to display the HTML with proper chart rendering
                                import streamlit.components.v1 as components
                                components.html(html_content, height=2000, scrolling=True)
                                
                                # Download button
                                with open(filepath, "rb") as file:
                                    st.download_button(
                                        label="📥 Download HTML Report",
                                        data=file.read(),
                                        file_name=filename,
                                        mime="text/html",
                                        help="Download the tearsheet as an HTML file"
                                    )
                                    
                            except Exception as e:
                                st.error(f"Error generating tearsheet: {str(e)}")
                                st.info("Please ensure you have sufficient data points for analysis.")
                    else:
                        st.warning("⚠️ No returns data available. Please ensure stock data is loaded properly.")
                else:
                    st.info("👆 Click 'Generate Tearsheet' to create a comprehensive performance analysis report using QuantStats.")
                    
                    # Show what will be included in the tearsheet
                    st.markdown("### 📋 Tearsheet Contents")
                    st.markdown("""
                    The QuantStats tearsheet will include:
                    - **Performance Metrics**: Sharpe, Sortino, and Calmar ratios
                    - **Risk Analysis**: VaR, CVaR, maximum drawdown, volatility
                    - **Visual Charts**: Cumulative returns, drawdown periods, monthly heatmap
                    - **Statistical Summary**: Win rate, best/worst performance, tail ratio
                    - **Distribution Analysis**: Returns histogram and risk-return scatter
                    """)
            
            with metrics_tab:
                st.write("Quick performance metrics overview")
                
                if 'stock_returns' in st.session_state and len(st.session_state.stock_returns) > 0:
                    returns_data = st.session_state.stock_returns
                    
                    # Calculate additional metrics using QuantStats
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Sharpe Ratio", f"{qs.stats.sharpe(returns_data):.4f}")
                        st.metric("Sortino Ratio", f"{qs.stats.sortino(returns_data):.4f}")
                        st.metric("Max Drawdown", f"{qs.stats.max_drawdown(returns_data):.2%}")
                    
                    with col2:
                        st.metric("Calmar Ratio", f"{qs.stats.calmar(returns_data):.4f}")
                        st.metric("VaR (95%)", f"{qs.stats.value_at_risk(returns_data):.2%}")
                        st.metric("Win Rate", f"{qs.stats.win_rate(returns_data):.2%}")
                else:
                    st.warning("⚠️ No returns data available for metrics calculation.")
            
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
            stock_price_bokeh = stock_price.copy()
            stock_price_bokeh['date'] = stock_price_bokeh.index
            
            # Calculate candlestick properties
            stock_price_bokeh['color'] = ['green' if close >= open_price else 'red' 
                                          for close, open_price in zip(stock_price_bokeh['close'], stock_price_bokeh['open'])]
            
            # Create two subplots: price and volume with proper alignment
            from bokeh.layouts import column
            from bokeh.models import LinearAxis, Range1d
            
            # Calculate min/max values for consistent scaling
            min_date = stock_price_bokeh.index.min()
            max_date = stock_price_bokeh.index.max()
            max_volume = stock_price_bokeh['volume'].max()
            
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
                x0='date', y0='high', 
                x1='date', y1='low',
                source=stock_price_bokeh,
                color='black',
                line_width=1
            )
            
            # Add rectangles for open-close range
            price.vbar(
                x='date',
                width=12*60*60*1000,  # 12 hours in milliseconds
                top='open',
                bottom='close',
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
                top='volume',
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
                    ('Open', '@open{0,0}'),
                    ('High', '@high{0,0}'),
                    ('Low', '@low{0,0}'),
                    ('Close', '@close{0,0}'),
                    ('Volume', '@volume{0,0}')
                ],
                formatters={'@date': 'datetime'},
                mode='vline'
            )
            price.add_tools(hover_price)
            
            hover_volume = HoverTool(
                tooltips=[
                    ('Date', '@date{%F}'),
                    ('Volume', '@volume{0,0}')
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
