import pathlib
from datetime import datetime

import altair as alt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import riskfolio as rp
import streamlit as st
from pypfopt import (
    DiscreteAllocation,
    EfficientFrontier,
    HRPOpt,
    expected_returns,
    plotting,
    risk_models,
)
from pypfopt.discrete_allocation import get_latest_prices

from src.components.ui_components import inject_custom_success_styling
from src.services.data import process_portfolio_price_data
from src.services.vnstock_api import fetch_portfolio_stock_data


# Streamlit page configuration
st.set_page_config(
    page_title="Stock Portfolio Optimization", page_icon="", layout="wide"
)

# Apply custom CSS styling for success alerts
inject_custom_success_styling()


# Get stock symbol from session state (set in main app)
# If not available, show message to use main app first
if "stock_symbol" in st.session_state and st.session_state.stock_symbol:
    main_stock_symbol = st.session_state.stock_symbol
else:
    st.warning(
        "⚠️ No stock symbol selected. Please go to the main Finance Bro page and select a stock symbol first."
    )
    st.stop()

# Sidebar for user inputs
st.sidebar.header("Portfolio Configuration")

# Get stock symbols from session state (cached from any analysis page)
if "stock_symbols_list" in st.session_state:
    stock_symbols_list = st.session_state.stock_symbols_list
else:
    # If not cached, user should visit any analysis page first
    st.warning(
        "⚠️ Stock symbols not loaded. Please visit the Stock Analysis page first to load symbols."
    )
    stock_symbols_list = ["REE", "FMC", "DHC", "VNM", "VCB", "BID", "HPG", "FPT"]

# Set default symbols to include the main symbol from session state
default_symbols = (
    [main_stock_symbol, "FMC", "DHC"]
    if main_stock_symbol not in ["FMC", "DHC"]
    else [main_stock_symbol, "REE", "VNM"]
)
# Remove duplicates and ensure main symbol is first
default_symbols = list(dict.fromkeys(default_symbols))

# Ticker symbols input
symbols = st.sidebar.multiselect(
    "Select ticker symbols:",
    options=stock_symbols_list,
    default=default_symbols,
    placeholder="Choose stock symbols...",
    help="Select multiple stock symbols for portfolio optimization (main symbol included by default)",
)

# Initialize global date session state variables (if not already set)
if "analysis_start_date" not in st.session_state:
    st.session_state.analysis_start_date = pd.to_datetime("2024-01-01")

if "analysis_end_date" not in st.session_state:
    st.session_state.analysis_end_date = pd.to_datetime("today") - pd.Timedelta(days=1)

if "date_range_changed" not in st.session_state:
    st.session_state.date_range_changed = False

# Date range inputs connected to session state
col1, col2 = st.sidebar.columns(2)
with col1:
    start_date = st.date_input(
        "Start Date",
        value=st.session_state.analysis_start_date,
        max_value=pd.to_datetime("today"),
    )

with col2:
    end_date = st.date_input(
        "End Date",
        value=st.session_state.analysis_end_date,
        max_value=pd.to_datetime("today"),
    )

# Update session state and detect changes
if (
    start_date != st.session_state.analysis_start_date
    or end_date != st.session_state.analysis_end_date
):
    st.session_state.analysis_start_date = start_date
    st.session_state.analysis_end_date = end_date
    st.session_state.date_range_changed = True

# Risk parameters


risk_aversion = st.sidebar.number_input(
    "Risk Aversion Parameter", value=1.0, min_value=0.1, max_value=10.0, step=0.1
)

# Visualization settings
colormap_options = [
    "copper",
    "gist_heat",
    "Greys",
    "gist_yarg",
    "gist_gray",
    "cividis",
    "magma",
    "inferno",
    "plasma",
    "viridis",
]
colormap = st.sidebar.selectbox(
    "Scatter Plot Colormap",
    options=colormap_options,
    index=0,  # Default to gist_heat
    help="Choose the color scheme for the efficient frontier scatter plot",
)

# Interval selection
interval = "1D"

# Convert session state dates to strings for API calls
start_date_str = st.session_state.analysis_start_date.strftime("%Y-%m-%d")
end_date_str = st.session_state.analysis_end_date.strftime("%Y-%m-%d")

# Main title
st.title("Stock Portfolio Optimization")
st.write("Optimize your portfolio using Modern Portfolio Theory")

# Validate inputs
if len(symbols) < 2:
    st.error("Please enter at least 2 ticker symbols.")
    st.stop()

if st.session_state.analysis_start_date >= st.session_state.analysis_end_date:
    st.error("Start date must be before end date.")
    st.stop()

# Progress indicator
progress_bar = st.progress(0)
status_text = st.empty()


# Fetch historical data with caching
status_text.text("Fetching historical data...")

# Clear cache if date range changed
if st.session_state.date_range_changed:
    st.cache_data.clear()
    st.session_state.date_range_changed = False

all_historical_data = fetch_portfolio_stock_data(
    symbols, start_date_str, end_date_str, interval
)

progress_bar.empty()
status_text.empty()

if not all_historical_data:
    st.error("No data was fetched for any symbol. Please check your inputs.")
    st.stop()

# Process the data
status_text.text("Processing data...")
prices_df = process_portfolio_price_data(all_historical_data)

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
        key="price_data_view",
    )

    if view_option == "First 5 rows":
        st.dataframe(prices_df.head())
    else:
        st.dataframe(prices_df.tail())

    st.write(f"Shape: {prices_df.shape}")

# Calculate returns and optimize portfolio
status_text.text("Calculating portfolio optimization...")
returns = prices_df.pct_change().dropna()
# Store returns in session state for HRP tab
st.session_state.portfolio_returns = returns
mu = expected_returns.mean_historical_return(prices_df)
S = risk_models.sample_cov(prices_df)

# Max Sharpe Ratio Portfolio
ef_tangent = EfficientFrontier(mu, S)
weights_tangent = ef_tangent.max_sharpe()
weights_max_sharpe = ef_tangent.clean_weights()
# Store weights dictionary in session state for riskfolio plot_table
st.session_state.weights_max_sharpe = weights_max_sharpe
ret_tangent, std_tangent, sharpe = ef_tangent.portfolio_performance()

# Min Volatility Portfolio
ef_min_vol = EfficientFrontier(mu, S)
ef_min_vol.min_volatility()
weights_min_vol = ef_min_vol.clean_weights()
# Store weights dictionary in session state for riskfolio plot_table
st.session_state.weights_min_vol = weights_min_vol
ret_min_vol, std_min_vol, sharpe_min_vol = ef_min_vol.portfolio_performance()

# Max Utility Portfolio
ef_max_utility = EfficientFrontier(mu, S)
ef_max_utility.max_quadratic_utility(risk_aversion=risk_aversion, market_neutral=False)
weights_max_utility = ef_max_utility.clean_weights()
# Store weights dictionary in session state for riskfolio plot_table
st.session_state.weights_max_utility = weights_max_utility
ret_utility, std_utility, sharpe_utility = ef_max_utility.portfolio_performance()

status_text.empty()

# Display results
st.header("Portfolio Optimization Results")

# Performance metrics
st.subheader("Performance Metrics")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Max Sharpe Portfolio", f"{sharpe:.4f}", f"Return: {(ret_tangent * 100):.1f}%"
    )

with col2:
    st.metric(
        "Min Volatility Portfolio",
        f"{sharpe_min_vol:.4f}",
        f"Return: {(ret_min_vol * 100):.1f}%",
    )

with col3:
    st.metric(
        "Max Utility Portfolio",
        f"{sharpe_utility:.4f}",
        f"Return: {(ret_utility * 100):.1f}%",
    )

# Create tabs for different analysis views
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Efficient Frontier & Weights",
    "🌳 Hierarchical Risk Parity",
    "💰 Dollars Allocation",
    "📊 Report",
    "📋 Risk Analysis",
])

with tab1:
    # Efficient Frontier Plot
    st.subheader("Efficient Frontier Analysis")
    fig, ax = plt.subplots(figsize=(12, 8))

    # Plot efficient frontier
    ef_plot = EfficientFrontier(mu, S)
    plotting.plot_efficient_frontier(ef_plot, ax=ax, show_assets=True)

    # Plot portfolios
    ax.scatter(
        std_tangent,
        ret_tangent,
        marker="*",
        s=200,
        c="red",
        label="Max Sharpe",
        zorder=5,
    )
    ax.scatter(
        std_min_vol,
        ret_min_vol,
        marker="*",
        s=200,
        c="green",
        label="Min Volatility",
        zorder=5,
    )
    ax.scatter(
        std_utility,
        ret_utility,
        marker="*",
        s=200,
        c="blue",
        label="Max Utility",
        zorder=5,
    )

    # Generate random portfolios
    n_samples = 5000
    w = np.random.dirichlet(np.ones(ef_plot.n_assets), n_samples)
    rets = w.dot(ef_plot.expected_returns)
    stds = np.sqrt(np.diag(w @ ef_plot.cov_matrix @ w.T))
    sharpes = rets / stds

    scatter = ax.scatter(stds, rets, marker=".", c=sharpes, cmap=colormap, alpha=0.6)
    plt.colorbar(scatter, label="Sharpe Ratio")

    ax.set_title("Efficient Frontier with Random Portfolios")
    ax.set_xlabel("Annual Volatility")
    ax.set_ylabel("Annual Return")
    ax.legend()
    # ax.grid(True, alpha=0.3)

    st.pyplot(fig)

    # Portfolio Weights
    st.subheader("Portfolio Weights")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.write("**Max Sharpe Portfolio**")
        weights_df = pd.DataFrame(
            list(weights_max_sharpe.items()), columns=["Symbol", "Weight"]
        )
        weights_df["Weight"] = weights_df["Weight"].apply(lambda x: f"{x:.2%}")
        st.dataframe(weights_df, hide_index=True)

    with col2:
        st.write("**Min Volatility Portfolio**")
        weights_df = pd.DataFrame(
            list(weights_min_vol.items()), columns=["Symbol", "Weight"]
        )
        weights_df["Weight"] = weights_df["Weight"].apply(lambda x: f"{x:.2%}")
        st.dataframe(weights_df, hide_index=True)

    with col3:
        st.write("**Max Utility Portfolio**")
        weights_df = pd.DataFrame(
            list(weights_max_utility.items()), columns=["Symbol", "Weight"]
        )
        weights_df["Weight"] = weights_df["Weight"].apply(lambda x: f"{x:.2%}")
        st.dataframe(weights_df, hide_index=True)

    # Weight visualization
    st.subheader("Portfolio Weights Visualization")

    # Define colors for pie charts
    pie_colors = ["#56524D", "#76706C", "#AAA39F"]

    def create_pie_chart(weights_dict, title, colors):
        """Create an Altair pie chart for portfolio weights."""
        # Filter out zero weights and prepare data
        data = pd.DataFrame(list(weights_dict.items()), columns=["Symbol", "Weight"])
        data = data[data["Weight"] > 0.01]  # Filter out very small weights
        data = data.sort_values("Weight", ascending=False)

        if len(data) == 0:
            return None

        # Assign colors to symbols
        data["color"] = (
            colors[: len(data)]
            if len(data) <= len(colors)
            else colors + ["#D3D3D3"] * (len(data) - len(colors))
        )

        # Create Altair pie chart
        chart = (
            alt.Chart(data)
            .mark_arc(innerRadius=50, stroke="white", strokeWidth=2)
            .encode(
                theta=alt.Theta("Weight:Q", title="Weight"),
                color=alt.Color(
                    "Symbol:N",
                    scale=alt.Scale(range=data["color"].tolist()),
                    legend=alt.Legend(title="Symbols"),
                ),
                tooltip=[
                    alt.Tooltip("Symbol:N", title="Symbol"),
                    alt.Tooltip("Weight:Q", title="Weight", format=".2%"),
                ],
            )
            .properties(width=350, height=350, title=title)
        )

        return chart

    # Create three pie charts in columns
    col1, col2, col3 = st.columns(3)

    with col1:
        pie1 = create_pie_chart(weights_max_sharpe, "Max Sharpe Portfolio", pie_colors)
        if pie1:
            st.altair_chart(pie1, use_container_width=True)
        else:
            st.write("No significant weights in Max Sharpe Portfolio")

    with col2:
        pie2 = create_pie_chart(weights_min_vol, "Min Volatility Portfolio", pie_colors)
        if pie2:
            st.altair_chart(pie2, use_container_width=True)
        else:
            st.write("No significant weights in Min Volatility Portfolio")

    with col3:
        pie3 = create_pie_chart(
            weights_max_utility, "Max Utility Portfolio", pie_colors
        )
        if pie3:
            st.altair_chart(pie3, use_container_width=True)
        else:
            st.write("No significant weights in Max Utility Portfolio")

    # Detailed performance table
    st.subheader("Detailed Performance Analysis")
    performance_df = pd.DataFrame({
        "Portfolio": ["Max Sharpe", "Min Volatility", "Max Utility"],
        "Expected Return": [
            f"{ret_tangent:.4f}",
            f"{ret_min_vol:.4f}",
            f"{ret_utility:.4f}",
        ],
        "Volatility": [
            f"{std_tangent:.4f}",
            f"{std_min_vol:.4f}",
            f"{std_utility:.4f}",
        ],
        "Sharpe Ratio": [
            f"{sharpe:.4f}",
            f"{sharpe_min_vol:.4f}",
            f"{sharpe_utility:.4f}",
        ],
    })
    st.dataframe(performance_df, hide_index=True)

with tab2:
    if "portfolio_returns" in st.session_state:
        returns = st.session_state.portfolio_returns

        # HRP Implementation
        hrp = HRPOpt(returns=returns)
        weights_hrp = hrp.optimize()

        # Display HRP weights
        st.subheader("HRP Portfolio Weights")
        weights_df = pd.DataFrame(
            list(weights_hrp.items()), columns=["Symbol", "Weight"]
        )
        weights_df["Weight"] = weights_df["Weight"].apply(lambda x: f"{x:.2%}")
        st.dataframe(weights_df, hide_index=True)

        # Dendrogram Visualization
        st.subheader("HRP Dendrogram")
        fig_dendro, ax_dendro = plt.subplots(figsize=(12, 8))
        plotting.plot_dendrogram(hrp, ax=ax_dendro, show_tickers=True)
        st.pyplot(fig_dendro)
    else:
        st.warning("Returns data not available. Please refresh the page.")

with tab3:
    st.subheader("Discrete Portfolio Allocation")

    # Portfolio value input
    portfolio_value = st.number_input(
        "Portfolio Value (VND)",
        min_value=1000000,  # 1 million VND minimum
        max_value=100000000000,  # 100 billion VND maximum
        value=100000000,  # Default 100 million VND
        step=1000000,  # 1 million VND steps
        help="Enter your total portfolio value in Vietnamese Dong (VND)",
    )

    # Get portfolio strategy from session state (set in Tab 4)
    if "portfolio_strategy_choice" in st.session_state:
        portfolio_choice = st.session_state.portfolio_strategy_choice
    else:
        portfolio_choice = "Max Sharpe Portfolio"  # Default fallback
        st.info(
            "💡 Go to the **Report** tab to select portfolio strategy for all analysis tabs"
        )

    # Display current selection for user awareness
    symbol_display = ", ".join(symbols[:3]) + ("..." if len(symbols) > 3 else "")
    st.info(
        f"📊 **Using Strategy**: {portfolio_choice} | **Symbols**: {symbol_display}"
    )

    # Get the selected weights
    if portfolio_choice == "Max Sharpe Portfolio":
        selected_weights = weights_max_sharpe
        portfolio_label = "Max Sharpe"
    elif portfolio_choice == "Min Volatility Portfolio":
        selected_weights = weights_min_vol
        portfolio_label = "Min Volatility"
    else:  # Max Utility Portfolio
        selected_weights = weights_max_utility
        portfolio_label = "Max Utility"

    # Calculate discrete allocation
    if st.button("Calculate Allocation", key="discrete_allocation"):
        try:
            # Get latest prices and convert from thousands to actual VND
            latest_prices = get_latest_prices(prices_df)
            # Convert prices from thousands to actual VND (multiply by 1000)
            latest_prices_actual = latest_prices * 1000

            # Create DiscreteAllocation object
            da = DiscreteAllocation(
                selected_weights,
                latest_prices_actual,
                total_portfolio_value=portfolio_value,
            )
            allocation, leftover = da.greedy_portfolio()

            # Display results
            st.success(
                f"✅ Allocation calculated successfully for {portfolio_label} Portfolio!"
            )

            # Show allocation results
            st.subheader("Stock Allocation")
            allocation_df = pd.DataFrame(
                list(allocation.items()), columns=["Symbol", "Shares"]
            )
            allocation_df["Latest Price (VND)"] = allocation_df["Symbol"].map(
                latest_prices_actual
            )
            allocation_df["Total Value (VND)"] = (
                allocation_df["Shares"] * allocation_df["Latest Price (VND)"]
            )
            allocation_df["Weight %"] = (
                allocation_df["Total Value (VND)"] / portfolio_value * 100
            ).round(2)

            # Format numbers for display
            allocation_df["Latest Price (VND)"] = allocation_df[
                "Latest Price (VND)"
            ].apply(lambda x: f"{x:,.0f}")
            allocation_df["Total Value (VND)"] = allocation_df[
                "Total Value (VND)"
            ].apply(lambda x: f"{x:,.0f}")

            st.dataframe(allocation_df, hide_index=True)

            # Summary metrics
            col1, col2, col3 = st.columns(3)

            with col1:
                allocated_value = portfolio_value - leftover
                st.metric(
                    "Allocated Amount",
                    f"{allocated_value:,.0f} VND",
                    f"{(allocated_value / portfolio_value * 100):.1f}% of portfolio",
                )

            with col2:
                st.metric(
                    "Leftover Cash",
                    f"{leftover:,.0f} VND",
                    f"{(leftover / portfolio_value * 100):.1f}% of portfolio",
                )

            with col3:
                total_stocks = len(allocation)
                st.metric("Stocks to Buy", total_stocks)

            # Investment summary
            st.subheader("Investment Summary")
            st.info(f"""
            **Portfolio Strategy**: {portfolio_label}
            **Total Investment**: {portfolio_value:,.0f} VND
            **Allocated**: {allocated_value:,.0f} VND ({(allocated_value / portfolio_value * 100):.1f}%)
            **Remaining Cash**: {leftover:,.0f} VND ({(leftover / portfolio_value * 100):.1f}%)
            **Number of Stocks**: {total_stocks} stocks
            """)

        except Exception as e:
            st.error(f"Error calculating allocation: {str(e)}")
            st.error(
                "Please ensure you have selected stocks and loaded price data first."
            )
    else:
        st.info(
            "👆 Click 'Calculate Allocation' to see how many shares to buy for each stock based on your selected portfolio strategy and investment amount."
        )

with tab4:
    st.subheader("Portfolio Excel Report Generator")
    st.write(
        "Generate comprehensive Excel reports for your optimized portfolios using Riskfolio-lib."
    )

    # Portfolio selection - Master control for all strategy-dependent tabs
    portfolio_choice = st.radio(
        "Select Portfolio Strategy for All Tabs:",
        ["Max Sharpe Portfolio", "Min Volatility Portfolio", "Max Utility Portfolio"],
        help="This selection applies to Dollar Allocation, Report, and Risk Analysis tabs",
        key="portfolio_strategy_master",
    )

    # Store in session state for other tabs to access
    st.session_state.portfolio_strategy_choice = portfolio_choice

    # Display info about master control
    st.info(
        f"📊 **Current Strategy**: {portfolio_choice} (applies to all analysis tabs)"
    )

    # Generate report button
    if st.button("Generate Report", key="generate_excel_report"):
        # Production-safe absolute path resolution
        project_root = pathlib.Path(
            pathlib.Path(pathlib.Path(__file__).resolve()).parent
        ).parent
        reports_dir = project_root / "exports" / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)

        # Get the selected weights and create meaningful names
        if portfolio_choice == "Max Sharpe Portfolio":
            selected_weights = weights_max_sharpe
            portfolio_name = "Max_Sharpe_Portfolio"
            portfolio_label = "Max Sharpe"
        elif portfolio_choice == "Min Volatility Portfolio":
            selected_weights = weights_min_vol
            portfolio_name = "Min_Volatility_Portfolio"
            portfolio_label = "Min Volatility"
        else:  # Max Utility Portfolio
            selected_weights = weights_max_utility
            portfolio_name = "Max_Utility_Portfolio"
            portfolio_label = "Max Utility"

        # Convert weights dictionary to DataFrame
        selected_weights_df = pd.DataFrame.from_dict(
            selected_weights, orient="index", columns=[portfolio_name]
        )

        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_base = f"{portfolio_name}_{timestamp}"
        filepath_base = reports_dir / filename_base

        # Generate Excel report using riskfolio-lib
        rp.excel_report(returns=returns, w=selected_weights_df, name=filepath_base)

        # Success message and download interface
        st.success("✅ Excel report generated successfully!")

        # Display report information
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Portfolio**: {portfolio_label}")
        with col2:
            st.info(f"**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}")

        # File download
        filepath_xlsx = pathlib.Path(str(filepath_base) + ".xlsx")
        with filepath_xlsx.open("rb") as file:
            st.download_button(
                label="📥 Download Excel Report",
                data=file.read(),
                file_name=filename_base + ".xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help=f"Download the {portfolio_label} portfolio Excel report",
            )

        # Show file details
        file_size = pathlib.Path(filepath_xlsx).stat().st_size / 1024  # Size in KB
        st.caption(f"File: {filename_base}.xlsx ({file_size:.1f} KB)")

    else:
        st.info(
            "👆 Select a portfolio strategy and click 'Generate Report' to create a comprehensive Excel analysis."
        )

        # Show what will be included in the report
        st.markdown("### 📋 Report Contents")
        st.markdown("""
        The Excel report will include:
        - **Portfolio Weights**: Detailed allocation percentages
        - **Performance Metrics**: Returns, volatility, and Sharpe ratio
        - **Risk Analysis**: Comprehensive risk assessment
        - **Asset Statistics**: Individual asset performance data
        - **Correlation Matrix**: Asset correlation analysis
        """)

with tab5:
    st.subheader("Risk Analysis Table")

    # Check if required data is available in session state
    if (
        "portfolio_returns" in st.session_state
        and "weights_max_sharpe" in st.session_state
    ):
        returns = st.session_state.portfolio_returns

        # Get portfolio strategy from session state (set in Tab 4)
        if "portfolio_strategy_choice" in st.session_state:
            portfolio_choice = st.session_state.portfolio_strategy_choice
        else:
            portfolio_choice = "Max Sharpe Portfolio"  # Default fallback
            st.info(
                "💡 Go to the **Report** tab to select portfolio strategy for all analysis tabs"
            )

        # Display current selection for user awareness
        symbol_display = ", ".join(symbols[:3]) + ("..." if len(symbols) > 3 else "")
        st.info(
            f"📊 **Analyzing Strategy**: {portfolio_choice} | **Symbols**: {symbol_display}"
        )

        # Get the selected weights
        if portfolio_choice == "Max Sharpe Portfolio":
            selected_weights = st.session_state.weights_max_sharpe
            portfolio_label = "Max Sharpe"
        elif portfolio_choice == "Min Volatility Portfolio":
            selected_weights = st.session_state.weights_min_vol
            portfolio_label = "Min Volatility"
        else:  # Max Utility Portfolio
            selected_weights = st.session_state.weights_max_utility
            portfolio_label = "Max Utility"

        # Convert weights dictionary to DataFrame as required by riskfolio plot_table
        weights_df = pd.DataFrame.from_dict(
            selected_weights, orient="index", columns=["Weights"]
        )

        # Create matplotlib figure for riskfolio plot_table
        fig, ax = plt.subplots(figsize=(12, 8))

        # Generate risk analysis table using riskfolio-lib
        ax = rp.plot_table(
            returns=returns,
            w=weights_df,
            MAR=0,  # Minimum acceptable return
            alpha=0.05,  # Significance level for confidence intervals 95%
            ax=ax,
        )

        # Display the risk analysis table
        st.pyplot(fig)

        # Drawdown Analysis
        st.subheader("Portfolio Drawdown Analysis")

        # Create matplotlib figure for riskfolio plot_drawdown
        fig_drawdown, ax_drawdown = plt.subplots(figsize=(12, 8))

        # Generate drawdown analysis using riskfolio-lib
        ax_drawdown = rp.plot_drawdown(
            returns=returns,
            w=weights_df,
            alpha=0.05,
            kappa=0.3,
            solver="CLARABEL",
            height=8,
            width=10,
            height_ratios=[2, 3],
            ax=ax_drawdown,
        )

        # Display the drawdown analysis
        st.pyplot(fig_drawdown)

        # Portfolio Returns Risk Measures
        st.subheader("Portfolio Returns Risk Measures")

        # Create matplotlib figure for riskfolio plot_range
        fig_range, ax_range = plt.subplots(figsize=(12, 6))

        # Generate portfolio returns risk measures using riskfolio-lib
        ax_range = rp.plot_range(
            returns=returns,
            w=weights_df,
            alpha=0.05,
            a_sim=100,
            beta=None,
            b_sim=None,
            bins=50,
            height=6,
            width=10,
            ax=ax_range,
        )

        # Display the portfolio returns risk measures
        st.pyplot(fig_range)

        # Add informational expander
        with st.expander("📚 Understanding the Risk Analysis Table"):
            st.markdown(f"""
            This table provides comprehensive risk metrics for your {portfolio_label} portfolio:

            **Key Metrics:**
            - **Expected Return**: Annualized expected portfolio return
            - **Volatility**: Portfolio standard deviation (risk measure)
            - **Sharpe Ratio**: Risk-adjusted return measure
            - **VaR**: Value at Risk - potential loss at 95% confidence
            - **CVaR**: Conditional Value at Risk - expected loss beyond VaR
            - **Max Drawdown**: Largest peak-to-trough decline
            - **Calmar Ratio**: Return to max drawdown ratio

            *Generated using riskfolio-lib risk analysis framework*
            """)

    else:
        st.warning("⚠️ Risk analysis requires portfolio data.")
        st.info(
            "Please visit the 'Efficient Frontier & Weights' tab first to calculate portfolio optimization, then return here for risk analysis."
        )

# Footer
st.markdown("---")
st.markdown(
    "*Portfolio optimization based on Modern Portfolio Theory. Past performance does not guarantee future results.*"
)
