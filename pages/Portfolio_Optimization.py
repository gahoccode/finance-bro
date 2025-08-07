import streamlit as st
from vnstock import Quote
import pandas as pd
import matplotlib.pyplot as plt
from pypfopt import EfficientFrontier, risk_models, expected_returns, DiscreteAllocation
from pypfopt.exceptions import OptimizationError
from pypfopt.expected_returns import mean_historical_return
from pypfopt.risk_models import sample_cov
from pypfopt import plotting
import numpy as np
from datetime import datetime, timedelta
from bokeh.plotting import figure
from bokeh.transform import cumsum
from bokeh.palettes import Spectral
from bokeh.models import ColumnDataSource
from math import pi

# Streamlit page configuration
st.set_page_config(
    page_title="Stock Portfolio Optimization",
    page_icon="",
    layout="wide"
)

import os

# CSS loading removed

# Get stock symbol from session state (set in main app)
# If not available, show message to use main app first
if 'stock_symbol' in st.session_state and st.session_state.stock_symbol:
    main_stock_symbol = st.session_state.stock_symbol
else:
    st.warning("⚠️ No stock symbol selected. Please go to the main Finance Bro page and select a stock symbol first.")
    st.stop()

# Sidebar for user inputs
st.sidebar.header("Portfolio Configuration")

# Get stock symbols from session state (cached from bro.py)
if 'stock_symbols_list' in st.session_state:
    stock_symbols_list = st.session_state.stock_symbols_list
else:
    # If not cached, user should visit bro.py first
    st.warning("⚠️ Stock symbols not loaded. Please visit the Stock Analysis page first to load symbols.")
    stock_symbols_list = ["REE", "FMC", "DHC", "VNM", "VCB", "BID", "HPG", "FPT"]

# Set default symbols to include the main symbol from session state
default_symbols = [main_stock_symbol, "FMC", "DHC"] if main_stock_symbol not in ["FMC", "DHC"] else [main_stock_symbol, "REE", "VNM"]
# Remove duplicates and ensure main symbol is first
default_symbols = list(dict.fromkeys(default_symbols))

# Ticker symbols input
symbols = st.sidebar.multiselect(
    "Select ticker symbols:",
    options=stock_symbols_list,
    default=default_symbols,
    placeholder="Choose stock symbols...",
    help="Select multiple stock symbols for portfolio optimization (main symbol included by default)"
)

# Date range inputs
col1, col2 = st.sidebar.columns(2)
with col1:
    start_date = st.date_input(
        "Start Date",
        value=pd.to_datetime("2024-01-01"),
        max_value=pd.to_datetime("today")
    )

with col2:
    end_date = st.date_input(
        "End Date", 
        value=pd.to_datetime("today") - pd.Timedelta(days=1), # Default to yesterday
        max_value=pd.to_datetime("today")
    )

# Risk parameters


risk_aversion = st.sidebar.number_input(
    "Risk Aversion Parameter",
    value=1.0,
    min_value=0.1,
    max_value=10.0,
    step=0.1
)

# Visualization settings
colormap_options = ['copper','gist_heat', 'Greys', 'gist_yarg', 'gist_gray', 'cividis', 'magma', 'inferno', 'plasma', 'viridis']
colormap = st.sidebar.selectbox(
    "Scatter Plot Colormap",
    options=colormap_options,
    index=0,  # Default to gist_heat
    help="Choose the color scheme for the efficient frontier scatter plot"
)

# Interval selection
interval = '1D'

# Convert dates to strings
start_date_str = start_date.strftime('%Y-%m-%d')
end_date_str = end_date.strftime('%Y-%m-%d')

# Main title
st.title("Stock Portfolio Optimization")
st.write("Optimize your portfolio using Modern Portfolio Theory")

# Validate inputs
if len(symbols) < 2:
    st.error("Please enter at least 2 ticker symbols.")
    st.stop()

if start_date >= end_date:
    st.error("Start date must be before end date.")
    st.stop()

# Progress indicator
progress_bar = st.progress(0)
status_text = st.empty()

@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_stock_data(symbols, start_date_str, end_date_str, interval):
    """Cache stock data to avoid repeated API calls."""
    all_data = {}
    
    for symbol in symbols:
        try:
            quote = Quote(symbol=symbol)
            historical_data = quote.history(
                start=start_date_str,
                end=end_date_str,
                interval=interval,
                to_df=True
            )
            
            if not historical_data.empty:
                # Ensure we have the required columns
                if 'time' not in historical_data.columns:
                    historical_data['time'] = historical_data.index
                
                all_data[symbol] = historical_data
        except Exception as e:
            st.error(f"Error fetching data for {symbol}: {e}")
    
    return all_data

# Fetch historical data with caching
status_text.text("Fetching historical data...")
all_historical_data = fetch_stock_data(symbols, start_date_str, end_date_str, interval)

progress_bar.empty()
status_text.empty()

if not all_historical_data:
    st.error("No data was fetched for any symbol. Please check your inputs.")
    st.stop()

# Process the data
status_text.text("Processing data...")
combined_prices = pd.DataFrame()

for symbol, data in all_historical_data.items():
    if not data.empty:
        # Ensure we have a 'time' column
        if 'time' not in data.columns:
            if hasattr(data.index, 'name') and data.index.name is None:
                data = data.reset_index()
            data = data.rename(columns={data.columns[0]: 'time'})
        
        # Extract time and close price
        temp_df = data[['time', 'close']].copy()
        temp_df.rename(columns={'close': f'{symbol}_close'}, inplace=True)
        
        if combined_prices.empty:
            combined_prices = temp_df
        else:
            combined_prices = pd.merge(combined_prices, temp_df, on='time', how='outer')

if combined_prices.empty:
    st.error("No valid data to process.")
    st.stop()

combined_prices = combined_prices.sort_values('time')
combined_prices.set_index('time', inplace=True)

# Extract close prices
close_price_columns = [col for col in combined_prices.columns if '_close' in col]
prices_df = combined_prices[close_price_columns]
prices_df.columns = [col.replace('_close', '') for col in close_price_columns]
prices_df = prices_df.dropna()

if prices_df.empty:
    st.error("No valid price data after processing.")
    st.stop()

# Display data summary
st.header("Data Summary")
col1, col2 = st.columns(2)
with col1:
    st.metric("Symbols", len(symbols))
with col2:
    st.metric("Data Points", len(prices_df))

# Show price data
with st.expander("View Price Data"):
    view_option = st.radio(
        "Display option:",
        ["First 5 rows", "Last 5 rows"],
        horizontal=True,
        key="price_data_view"
    )
    
    if view_option == "First 5 rows":
        st.dataframe(prices_df.head())
    else:
        st.dataframe(prices_df.tail())
    
    st.write(f"Shape: {prices_df.shape}")

# Calculate returns and optimize portfolio
status_text.text("Calculating portfolio optimization...")
returns = prices_df.pct_change().dropna()
mu = expected_returns.mean_historical_return(prices_df)
S = risk_models.sample_cov(prices_df)

# Max Sharpe Ratio Portfolio
ef_tangent = EfficientFrontier(mu, S)
weights_tangent = ef_tangent.max_sharpe()
weights_max_sharpe = ef_tangent.clean_weights()
ret_tangent, std_tangent, sharpe = ef_tangent.portfolio_performance()

# Min Volatility Portfolio
ef_min_vol = EfficientFrontier(mu, S)
ef_min_vol.min_volatility()
weights_min_vol = ef_min_vol.clean_weights()
ret_min_vol, std_min_vol, sharpe_min_vol = ef_min_vol.portfolio_performance()

# Max Utility Portfolio
ef_max_utility = EfficientFrontier(mu, S)
ef_max_utility.max_quadratic_utility(risk_aversion=risk_aversion, market_neutral=False)
weights_max_utility = ef_max_utility.clean_weights()
ret_utility, std_utility, sharpe_utility = ef_max_utility.portfolio_performance()

status_text.empty()

# Display results
st.header("Portfolio Optimization Results")

# Performance metrics
st.subheader("Performance Metrics")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Max Sharpe Portfolio",
        f"{sharpe:.1f}",
        f"Return: {(ret_tangent*100):.1f}%"
    )

with col2:
    st.metric(
        "Min Volatility Portfolio", 
        f"{sharpe_min_vol:.1f}",
        f"Return: {(ret_min_vol*100):.1f}%"
    )

with col3:
    st.metric(
        "Max Utility Portfolio",
        f"{sharpe_utility:.1f}",
        f"Return: {(ret_utility*100):.1f}%"
    )

# Efficient Frontier Plot
st.subheader("Efficient Frontier Analysis")
fig, ax = plt.subplots(figsize=(12, 8))

# Plot efficient frontier
ef_plot = EfficientFrontier(mu, S)
plotting.plot_efficient_frontier(ef_plot, ax=ax, show_assets=True)

# Plot portfolios
ax.scatter(std_tangent, ret_tangent, marker="*", s=200, c="red", label="Max Sharpe", zorder=5)
ax.scatter(std_min_vol, ret_min_vol, marker="*", s=200, c="green", label="Min Volatility", zorder=5)
ax.scatter(std_utility, ret_utility, marker="*", s=200, c="blue", label="Max Utility", zorder=5)

# Generate random portfolios
n_samples = 5000
w = np.random.dirichlet(np.ones(ef_plot.n_assets), n_samples)
rets = w.dot(ef_plot.expected_returns)
stds = np.sqrt(np.diag(w @ ef_plot.cov_matrix @ w.T))
sharpes = rets / stds

scatter = ax.scatter(stds, rets, marker=".", c=sharpes, cmap=colormap, alpha=0.6)
plt.colorbar(scatter, label='Sharpe Ratio')

ax.set_title("Efficient Frontier with Random Portfolios")
ax.set_xlabel("Annual Volatility")
ax.set_ylabel("Annual Return")
ax.legend()
#ax.grid(True, alpha=0.3)

st.pyplot(fig)

# Portfolio Weights
st.subheader("Portfolio Weights")
col1, col2, col3 = st.columns(3)

with col1:
    st.write("**Max Sharpe Portfolio**")
    weights_df = pd.DataFrame(list(weights_max_sharpe.items()), columns=['Symbol', 'Weight'])
    weights_df['Weight'] = weights_df['Weight'].apply(lambda x: f"{x:.2%}")
    st.dataframe(weights_df, hide_index=True)

with col2:
    st.write("**Min Volatility Portfolio**")
    weights_df = pd.DataFrame(list(weights_min_vol.items()), columns=['Symbol', 'Weight'])
    weights_df['Weight'] = weights_df['Weight'].apply(lambda x: f"{x:.2%}")
    st.dataframe(weights_df, hide_index=True)

with col3:
    st.write("**Max Utility Portfolio**")
    weights_df = pd.DataFrame(list(weights_max_utility.items()), columns=['Symbol', 'Weight'])
    weights_df['Weight'] = weights_df['Weight'].apply(lambda x: f"{x:.2%}")
    st.dataframe(weights_df, hide_index=True)

# Weight visualization
st.subheader("Portfolio Weights Visualization")

# Define colors for pie charts
pie_colors = ["#56524D", "#76706C", "#AAA39F"]

def create_pie_chart(weights_dict, title, colors):
    """Create a Bokeh pie chart for portfolio weights."""
    # Filter out zero weights and prepare data
    data = pd.DataFrame(list(weights_dict.items()), columns=['Symbol', 'Weight'])
    data = data[data['Weight'] > 0.01]  # Filter out very small weights
    data = data.sort_values('Weight', ascending=False)
    
    if len(data) == 0:
        return None
    
    # Calculate angles for pie chart
    data['angle'] = data['Weight'] / data['Weight'].sum() * 2 * pi
    data['color'] = colors[:len(data)] if len(data) <= len(colors) else colors + ["#D3D3D3"] * (len(data) - len(colors))
    
    # Create pie chart with increased height for better visibility
    p = figure(
        height=400, 
        width=350, 
        title=title,
        toolbar_location=None,
        tools="hover",
        tooltips="@Symbol: @Weight{0.00%}",
        x_range=(-0.5, 0.5), 
        y_range=(-0.5, 0.5),
        sizing_mode="scale_both"
    )
    
    p.wedge(
        x=0, y=0, radius=0.35,
        start_angle=cumsum('angle', include_zero=True), 
        end_angle=cumsum('angle'),
        line_color="white", 
        fill_color='color',
        legend_field='Symbol',
        source=data
    )
    
    p.axis.axis_label = None
    p.axis.visible = False
    p.grid.grid_line_color = None
    p.title.text_font_size = "12pt"
    p.legend.label_text_font_size = "10pt"
    
    return p

# Create three pie charts in columns
col1, col2, col3 = st.columns(3)

with col1:
    pie1 = create_pie_chart(weights_max_sharpe, "Max Sharpe Portfolio", pie_colors)
    if pie1:
        st.bokeh_chart(pie1, use_container_width=True)
    else:
        st.write("No significant weights in Max Sharpe Portfolio")

with col2:
    pie2 = create_pie_chart(weights_min_vol, "Min Volatility Portfolio", pie_colors)
    if pie2:
        st.bokeh_chart(pie2, use_container_width=True)
    else:
        st.write("No significant weights in Min Volatility Portfolio")

with col3:
    pie3 = create_pie_chart(weights_max_utility, "Max Utility Portfolio", pie_colors)
    if pie3:
        st.bokeh_chart(pie3, use_container_width=True)
    else:
        st.write("No significant weights in Max Utility Portfolio")

# Detailed performance table
st.subheader("Detailed Performance Analysis")
performance_df = pd.DataFrame({
    'Portfolio': ['Max Sharpe', 'Min Volatility', 'Max Utility'],
    'Expected Return': [f"{ret_tangent:.4f}", f"{ret_min_vol:.4f}", f"{ret_utility:.4f}"],
    'Volatility': [f"{std_tangent:.4f}", f"{std_min_vol:.4f}", f"{std_utility:.4f}"],
    'Sharpe Ratio': [f"{sharpe:.4f}", f"{sharpe_min_vol:.4f}", f"{sharpe_utility:.4f}"]
})
st.dataframe(performance_df, hide_index=True)

# Footer
st.markdown("---")
st.markdown("*Portfolio optimization based on Modern Portfolio Theory. Past performance does not guarantee future results.*")

