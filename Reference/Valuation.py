import numpy as np
import pandas as pd
from vnstock import Quote

quote = Quote(symbol="VNINDEX", source="VCI")
# Get historical data
vnindex_data = quote.history(start=start_date, end=end_date, interval=interval)

# 1. Prepare & align prices on common dates
aligned = (
    stock_price[["time", "close"]]
    .rename(columns={"close": "stock_close"})
    .merge(
        vnindex_data[["time", "close"]].rename(columns={"close": "index_close"}),
        on="time",
        how="inner",
    )
    .sort_values("time")
)

# 2. Compute daily percentage returns
aligned["stock_ret"] = aligned["stock_close"].pct_change()
aligned["index_ret"] = aligned["index_close"].pct_change()

# 3. Drop the first NaN row produced by pct_change
returns = aligned.dropna(subset=["stock_ret", "index_ret"])

# 4. Covariance matrix (2×2) and beta calculation
cov_matrix = np.cov(returns["stock_ret"], returns["index_ret"])
beta = cov_matrix[0, 1] / cov_matrix[1, 1]

print(f"Stock beta (covariance method): {beta:.4f}")
# Step 1: Get book values from Balance Sheet
short_term_debt = BalanceSheet["Short-term borrowings (Bn. VND)"]
long_term_debt = BalanceSheet["Long-term borrowings (Bn. VND)"]
total_debt = short_term_debt + long_term_debt
book_equity = BalanceSheet["OWNER'S EQUITY(Bn.VND)"]

# Step 2: Get market values
# Market capitalization for equity
market_value_of_equity = Ratio[
    ("Chỉ tiêu định giá", "Market Capital (Bn. VND)")
]  # Market capitalization

# Use book value of debt as a proxy for market value of debt
# (In practice, we'd prefer bond prices or yield-based valuation if available)
market_value_of_debt = total_debt

# Calculate total market capital and weights
total_market_capital = market_value_of_equity + market_value_of_debt
market_weight_of_debt = market_value_of_debt.div(total_market_capital).fillna(0)
market_weight_of_equity = market_value_of_equity.div(total_market_capital).fillna(0)

# Step 3: Market-based cost of debt
# Option 1: If you have specific bond yield data (example values)
# In reality, this would vary by company or be derived from external data sources
base_interest_rate = 0.04  # e.g., Vietnamese government bond rate
credit_spread = 0.03  # Credit spread based on company rating
company_bond_yield = base_interest_rate + credit_spread  # = 0.05 (5%)

# Option 2: Use credit rating to determine yield (if available)
# This would be a mapping from credit ratings to yields
# rating_to_yield = {'AAA': 0.035, 'AA': 0.04, 'A': 0.045, 'BBB': 0.05, 'BB': 0.06, 'B': 0.07}
# company_bond_yield = rating_to_yield.get(company_rating, 0.05)  # Default to 5% if rating unknown

# Use fixed rate for simplicity (you would replace this with company-specific data)
market_cost_of_debt = 0.07  # 7% bond yield

# Apply tax shield
statutory_tax_rate = 0.20  # Vietnamese corporate tax rate
after_tax_market_cost_of_debt = market_cost_of_debt * (1 - statutory_tax_rate)

# Step 4: Cost of Equity using CAPM
risk_free_rate = 0.03  # Vietnamese government bond yield

# Option 1: If you have beta data from external sources
# estimated_beta = external_beta_data  # This would be company-specific

# Option 2: Estimate beta using financial leverage
financial_leverage = Ratio[("Chỉ tiêu thanh khoản", "Financial Leverage")]
leverage_mean = financial_leverage.mean()
estimated_beta = beta


# 1. Prepare & align prices on common dates
aligned = (
    stock_price[["time", "close"]]
    .rename(columns={"close": "stock_close"})
    .merge(
        vnindex_data[["time", "close"]].rename(columns={"close": "index_close"}),
        on="time",
        how="inner",
    )
    .sort_values("time")
)

# 2. Compute daily percentage returns
aligned["stock_ret"] = aligned["stock_close"].pct_change()
aligned["index_ret"] = aligned["index_close"].pct_change()

# 3. Drop the first NaN row produced by pct_change
returns = aligned.dropna(subset=["stock_ret", "index_ret"])

# 4. Covariance matrix (2×2) and beta calculation
cov_matrix = np.cov(returns["stock_ret"], returns["index_ret"])
beta = cov_matrix[0, 1] / cov_matrix[1, 1]

print(f"Stock beta (covariance method): {beta:.4f}")

# Market risk premium
market_risk_premium = 0.05  # Estimated risk premium for Vietnamese market

# Calculate cost of equity using CAPM
cost_of_equity = risk_free_rate + (estimated_beta * market_risk_premium)

# Step 5: Calculate market-based WACC
wacc_market_based = (market_weight_of_debt * after_tax_market_cost_of_debt) + (
    market_weight_of_equity * cost_of_equity
)

# Create a DataFrame with the results
result_df = pd.DataFrame(
    {
        "ticker": BalanceSheet["ticker"],
        "yearReport": BalanceSheet["yearReport"],
        "market_cap": market_value_of_equity,
        "market_debt": market_value_of_debt,
        "market_weight_of_debt": market_weight_of_debt,
        "market_weight_of_equity": market_weight_of_equity,
        "market_cost_of_debt": after_tax_market_cost_of_debt,
        "beta": estimated_beta,
        "cost_of_equity": cost_of_equity,
        "wacc_market_based": wacc_market_based,
    }
)

result_df[["yearReport", "wacc_market_based"]].round(3)  # round to 3 decimal places
