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

# Streamlit page configuration
st.set_page_config(
    page_title="Stock Portfolio Optimization",
    page_icon="📈",
    layout="wide"
)

# Sidebar for user inputs
st.sidebar.header("Portfolio Configuration")

# Ticker symbols input
symbols_input = st.sidebar.text_input(
    "Enter ticker symbols (comma-separated):",
    value="REE, FMC, DHC",
    placeholder="e.g., VNM, VCB, BID"
)

# Parse symbols
symbols = [s.strip() for s in symbols_input.split(',') if s.strip()]

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
        value=pd.to_datetime("2025-03-19"),
        max_value=pd.to_datetime("today")
    )

# Risk parameters
risk_free_rate = st.sidebar.number_input(
    "Risk-free Rate (%)", 
    value=2.0, 
    min_value=0.0, 
    max_value=10.0, 
    step=0.1
) / 100

risk_aversion = st.sidebar.number_input(
    "Risk Aversion Parameter",
    value=1.0,
    min_value=0.1,
    max_value=10.0,
    step=0.1
)

# Interval selection
interval = '1D'

# Convert dates to strings
start_date_str = start_date.strftime('%Y-%m-%d')
end_date_str = end_date.strftime('%Y-%m-%d')

# Main title
st.title("📈 Stock Portfolio Optimization")
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

# Fetch historical data
status_text.text("Fetching historical data...")
all_historical_data = {}

for i, symbol in enumerate(symbols):
    try:
        progress_bar.progress((i + 1) / len(symbols))
        status_text.text(f"Processing {symbol}...")
        
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
            
            all_historical_data[symbol] = historical_data
        else:
            st.warning(f"⚠️ No data available for {symbol}")
    except Exception as e:
        st.error(f"❌ Error fetching data for {symbol}: {e}")

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
st.header("📊 Data Summary")
col1, col2 = st.columns(2)
with col1:
    st.metric("Symbols", len(symbols))
with col2:
    st.metric("Data Points", len(prices_df))

# Show price data
with st.expander("View Price Data"):
    st.dataframe(prices_df.head())
    st.write(f"Shape: {prices_df.shape}")

# Calculate returns and optimize portfolio
status_text.text("Calculating portfolio optimization...")
returns = expected_returns.returns_from_prices(prices_df, log_returns=False)
mu = mean_historical_return(prices_df, log_returns=False)
S = sample_cov(prices_df)

# Portfolio optimization
ef_max_sharpe = EfficientFrontier(mu, S)
ef_max_sharpe.max_sharpe(risk_free_rate=risk_free_rate)
weights_max_sharpe = ef_max_sharpe.clean_weights()
ret_tangent, std_tangent, sharpe = ef_max_sharpe.portfolio_performance(risk_free_rate=risk_free_rate)

ef_min_vol = EfficientFrontier(mu, S)
ef_min_vol.min_volatility()
weights_min_vol = ef_min_vol.clean_weights()
ret_min_vol, std_min_vol, sharpe_min_vol = ef_min_vol.portfolio_performance(risk_free_rate=risk_free_rate)

ef_max_utility = EfficientFrontier(mu, S)
ef_max_utility.max_quadratic_utility(risk_aversion=risk_aversion, market_neutral=False)
weights_max_utility = ef_max_utility.clean_weights()
ret_utility, std_utility, sharpe_utility = ef_max_utility.portfolio_performance(risk_free_rate=risk_free_rate)

status_text.empty()

# Display results
st.header("📈 Portfolio Optimization Results")

# Performance metrics
st.subheader("Performance Metrics")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Max Sharpe Portfolio",
        f"{sharpe:.4f}",
        f"Return: {(ret_tangent*100):.2f}%\nVol: {(std_tangent*100):.2f}%"
    )

with col2:
    st.metric(
        "Min Volatility Portfolio", 
        f"{sharpe_min_vol:.4f}",
        f"Return: {(ret_min_vol*100):.2f}%\nVol: {(std_min_vol*100):.2f}%"
    )

with col3:
    st.metric(
        "Max Utility Portfolio",
        f"{sharpe_utility:.4f}",
        f"Return: {(ret_utility*100):.2f}%\nVol: {(std_utility*100):.2f}%"
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

scatter = ax.scatter(stds, rets, marker=".", c=sharpes, cmap="viridis_r", alpha=0.6)
plt.colorbar(scatter, label='Sharpe Ratio')

ax.set_title("Efficient Frontier with Random Portfolios")
ax.set_xlabel("Annual Volatility")
ax.set_ylabel("Annual Return")
ax.legend()
ax.grid(True, alpha=0.3)

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
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

plotting.plot_weights(weights_max_sharpe, ax=axes[0])
axes[0].set_title("Max Sharpe Portfolio")

plotting.plot_weights(weights_min_vol, ax=axes[1])
axes[1].set_title("Min Volatility Portfolio")

plotting.plot_weights(weights_max_utility, ax=axes[2])
axes[2].set_title("Max Utility Portfolio")

plt.tight_layout()
st.pyplot(fig)

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

