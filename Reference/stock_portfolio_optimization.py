import pandas as pd
from vnstock import Quote


# Define the symbols you want to fetch data for
symbols = ["REE", "FMC", "DHC"]
print(f"Fetching historical price data for: {symbols}")

# Dictionary to store historical data for each symbol
all_historical_data = {}

# Set date range
start_date = "2024-01-01"
end_date = "2025-03-19"
interval = "1D"

# Fetch historical data for each symbol
for symbol in symbols:
    try:
        print(f"\nProcessing {symbol}...")
        quote = Quote(symbol=symbol)

        # Fetch historical price data
        historical_data = quote.history(
            start=start_date, end=end_date, interval=interval, to_df=True
        )

        if not historical_data.empty:
            all_historical_data[symbol] = historical_data
            print(f"Successfully fetched {len(historical_data)} records for {symbol}")
        else:
            print(f"No historical data available for {symbol}")
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")

# Export all historical data to a single CSV file
if all_historical_data:
    # Create a combined DataFrame with all data
    combined_data = pd.DataFrame()

    for symbol, data in all_historical_data.items():
        if not data.empty:
            # Make a copy of the data and rename columns to include symbol
            temp_df = data.copy()
            # Keep 'time' column as is for merging
            for col in temp_df.columns:
                if col != "time":
                    temp_df.rename(columns={col: f"{symbol}_{col}"}, inplace=True)

            if combined_data.empty:
                combined_data = temp_df
            else:
                combined_data = pd.merge(combined_data, temp_df, on="time", how="outer")

    # Sort by time
    if not combined_data.empty:
        combined_data = combined_data.sort_values("time")

        # Display sample of combined data
        print("\nSample of combined data:")
        print(combined_data.head(3))

    # Also create a combined DataFrame for close prices only (for comparison purposes)
    combined_prices = pd.DataFrame()

    for symbol, data in all_historical_data.items():
        if not data.empty:
            # Extract time and close price
            temp_df = data[["time", "close"]].copy()
            temp_df.rename(columns={"close": f"{symbol}_close"}, inplace=True)

            if combined_prices.empty:
                combined_prices = temp_df
            else:
                combined_prices = pd.merge(
                    combined_prices, temp_df, on="time", how="outer"
                )

    # Sort by time
    if not combined_prices.empty:
        combined_prices = combined_prices.sort_values("time")
    else:
        print("No historical data was fetched for any symbol.")

prices_df.set_index("time", inplace=True)
prices_df  # 4. Extract only the close price columns and rename them to just the symbol names
close_price_columns = [col for col in prices_df.columns if "_close" in col]
prices_df = prices_df[close_price_columns]
prices_df.columns = [col.replace("_close", "") for col in close_price_columns]
prices_df = prices_df.dropna()
risk_free_rate = 0.02
risk_aversion = 1
from pypfopt.expected_returns import returns_from_prices


log_returns = False
returns = returns_from_prices(prices_df, log_returns=log_returns)


from pypfopt import EfficientFrontier
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt.expected_returns import mean_historical_return
from pypfopt.risk_models import (
    sample_cov,
)  # for covariance matrix, get more methods from risk_models


mu = mean_historical_return(
    prices_df, log_returns=log_returns
)  # Optional: add log_returns=True
"""
For most portfolio optimization purposes, the default simple returns pct_change() are adequate, 
but logarithmic returns can provide more robust results in some cases, 
especially when dealing with volatile assets or longer time horizons.
"""
S = sample_cov(prices_df)

# Matplotlib Dashboard

import matplotlib.pyplot as plt
import numpy as np
from pypfopt import plotting


# Create the plot
fig, ax = plt.subplots(figsize=(10, 7))

# Create a new instance for plotting the efficient frontier
ef_plot = EfficientFrontier(mu, S)
plotting.plot_efficient_frontier(ef_plot, ax=ax, show_assets=False)

# Create a separate instance for max Sharpe ratio portfolio
ef_max_sharpe = EfficientFrontier(mu, S)
ef_max_sharpe.max_sharpe(risk_free_rate=risk_free_rate)
weights_max_sharpe = ef_max_sharpe.clean_weights()
ret_tangent, std_tangent, sharpe = ef_max_sharpe.portfolio_performance(
    risk_free_rate=risk_free_rate
)

# Create another separate instance for min volatility portfolio
ef_min_vol = EfficientFrontier(mu, S)
ef_min_vol.min_volatility()
weights_min_vol = ef_min_vol.clean_weights()
ret_min_vol, std_min_vol, sharpe_min_vol = ef_min_vol.portfolio_performance(
    risk_free_rate=risk_free_rate
)

# Create another separate instance for max utility portfolio
ef_max_utility = EfficientFrontier(mu, S)
ef_max_utility.max_quadratic_utility(risk_aversion=risk_aversion, market_neutral=False)
weights_max_utility = ef_max_utility.clean_weights()
ret_utility, std_utility, sharpe_utility = ef_max_utility.portfolio_performance(
    risk_free_rate=risk_free_rate
)

# Plot the tangency portfolio (max Sharpe)
ax.scatter(std_tangent, ret_tangent, marker="*", s=100, c="r", label="Max Sharpe")

# Plot the minimum volatility portfolio
ax.scatter(std_min_vol, ret_min_vol, marker="*", s=100, c="g", label="Min Volatility")

# Plot the maximum utility portfolio
ax.scatter(std_utility, ret_utility, marker="*", s=100, c="b", label="Max Utility")

# Generate random portfolios
n_samples = 10000
w = np.random.dirichlet(np.ones(ef_plot.n_assets), n_samples)
rets = w.dot(ef_plot.expected_returns)
stds = np.sqrt(np.diag(w @ ef_plot.cov_matrix @ w.T))
sharpes = rets / stds
ax.scatter(stds, rets, marker=".", c=sharpes, cmap="viridis_r")

# Output
ax.set_title("Efficient Frontier with random portfolios")
ax.legend()
plt.tight_layout()
plt.savefig("./outputs/ef_scatter.png", dpi=200)
plt.show()

# In a separate cell, plot the weights for all three portfolios
plt.figure(figsize=(15, 5))

plt.subplot(1, 3, 1)
plotting.plot_weights(weights_max_sharpe)
plt.title("Max Sharpe Portfolio Weights")

plt.subplot(1, 3, 2)
plotting.plot_weights(weights_min_vol)
plt.title("Min Volatility Portfolio Weights")

plt.subplot(1, 3, 3)
plotting.plot_weights(weights_max_utility)
plt.title("Max Utility Portfolio Weights")

plt.tight_layout()
plt.show()

# Print the performance metrics for comparison
print("Maximum Sharpe Portfolio:")
print(f"Expected annual return: {ret_tangent:.4f}")
print(f"Annual volatility: {std_tangent:.4f}")
print(f"Sharpe Ratio: {sharpe:.4f}")

print("\nMinimum Volatility Portfolio:")
print(f"Expected annual return: {ret_min_vol:.4f}")
print(f"Annual volatility: {std_min_vol:.4f}")
print(f"Sharpe Ratio: {sharpe_min_vol:.4f}")

print("\nMaximum Utility Portfolio:")
print(f"Expected annual return: {ret_utility:.4f}")
print(f"Annual volatility: {std_utility:.4f}")
print(f"Sharpe Ratio: {sharpe_utility:.4f}")
print(f"Risk Aversion Parameter: {risk_aversion}")
