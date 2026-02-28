import pathlib
from datetime import datetime

import numpy as np
import pandas as pd
import quantstats as qs
import streamlit as st

from src.components.ui_components import inject_custom_success_styling
from src.services.chart import (
    create_altair_area_chart,
    create_altair_line_chart,
    create_plotly_candlestick_chart,
)
from src.services.quantstats_metrics import (
    calculate_custom_metrics,
    get_metric_categories,
)
from src.services.vnstock_api import fetch_stock_price_data


st.set_page_config(page_title="Stock Price Analysis", layout="wide")

# Apply custom CSS styling for success alerts
inject_custom_success_styling()

# Extend pandas functionality with QuantStats
qs.extend_pandas()

# Get stock symbol from session state (set in main app)
# If not available, show message to use main app first
ticker = None
if "stock_symbol" in st.session_state and st.session_state.stock_symbol:
    ticker = st.session_state.stock_symbol
else:
    st.warning(
        "No stock symbol selected. Please go to the main Finance Bro page and select a stock symbol first."
    )
    st.stop()

st.title("Stock Price Analysis")

# Initialize global date session state variables
if "analysis_start_date" not in st.session_state:
    st.session_state.analysis_start_date = pd.to_datetime("2024-01-01")

if "analysis_end_date" not in st.session_state:
    st.session_state.analysis_end_date = pd.to_datetime("today") - pd.Timedelta(days=1)

if "date_range_changed" not in st.session_state:
    st.session_state.date_range_changed = False

# Sidebar for user inputs
with st.sidebar:
    st.header("Settings")
    st.metric("Current Symbol", ticker)

    # Date range inputs connected to session state
    start_date = st.date_input(
        "Start Date:",
        value=st.session_state.analysis_start_date,
        max_value=pd.to_datetime("today"),
    )
    end_date = st.date_input(
        "End Date:",
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

    # Validate date range
    if start_date >= end_date:
        st.error("Start date must be before end date.")
        st.stop()

    # Chart type selector
    chart_type = st.selectbox(
        "Chart Type:",
        options=["Line Chart", "Area Chart"],
        index=0,
        help="Choose between line chart and area chart with gradient",
    )

    # Custom Metrics Section
    with st.expander("Custom Metrics"):
        # Category selector
        categories = get_metric_categories()
        selected_category = st.selectbox(
            "Metric Category:",
            options=list(categories.keys()),
            index=1,  # Default to "Core Performance"
            help="Choose a category to filter available metrics",
        )

        # Multi-select for metrics based on category
        available_metrics = categories[selected_category]
        default_metrics = (
            ["sharpe", "sortino", "max_drawdown", "cagr"]
            if selected_category == "Core Performance"
            else []
        )

        selected_metrics = st.multiselect(
            f"Select Metrics ({len(available_metrics)} available):",
            options=available_metrics,
            default=[m for m in default_metrics if m in available_metrics],
            help=f"Select metrics from {selected_category} category to display",
        )

        # Display format options
        col1, col2 = st.columns(2)
        with col1:
            include_descriptions = st.checkbox("Include Descriptions", value=False)
        with col2:
            grid_columns = st.selectbox("Grid Columns:", options=[2, 3, 4], index=1)


# Import cached function from modular utilities


if ticker:
    try:
        with st.spinner(f"Loading data for {ticker}..."):
            # Clear cache if date range changed
            if st.session_state.date_range_changed:
                st.cache_data.clear()
                st.session_state.date_range_changed = False

            # Fetch cached stock data using session state dates
            stock_price = fetch_stock_price_data(
                ticker,
                st.session_state.analysis_start_date,
                st.session_state.analysis_end_date,
            )

            # Calculate returns using session state data and pct_change method
            # Use the stock_price data stored in session state for consistency across pages
            # Check if session state data exists, otherwise use the just-fetched data
            if "stock_price_data" in st.session_state:
                session_stock_price = st.session_state.stock_price_data
            else:
                session_stock_price = stock_price

            clean_prices = session_stock_price["close"].dropna()
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
                mean_return_pct = "Error"
                volatility = "Error"

            # Show returns statistics at the top
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    "Latest Close", f"{stock_price['close'].iloc[-1] * 1000:,.0f}"
                )
            with col2:
                st.metric("Mean Return (Annualized)", f"{mean_return_pct:.2f}%")
            with col3:
                st.metric("Annualized Volatility", f"{volatility:.2f}%")

            # Create metrics tabs including Tearsheet
            st.subheader("Performance Analytics")
            tearsheet_tab, metrics_tab = st.tabs(["📊 Tearsheet", "📈 Quick Metrics"])

            with tearsheet_tab:
                st.write(
                    "Generate comprehensive performance analytics using QuantStats"
                )

                if st.button("Generate Tearsheet", key="generate_tearsheet"):
                    # Check if returns data exists in session state
                    if (
                        "stock_returns" in st.session_state
                        and len(st.session_state.stock_returns) > 0
                    ):
                        # Set up exports directory
                        project_root = pathlib.Path(
                            pathlib.Path(pathlib.Path(__file__).resolve()).parent
                        ).parent
                        tearsheets_dir = project_root / "exports" / "tearsheets"
                        tearsheets_dir.mkdir(parents=True, exist_ok=True)

                        # Generate timestamp and filename
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"{ticker}_tearsheet_{timestamp}.html"
                        filepath = tearsheets_dir / filename

                        with st.spinner("Generating QuantStats tearsheet..."):
                            try:
                                # Generate HTML tearsheet using QuantStats
                                returns_data = st.session_state.stock_returns

                                # Generate tearsheet HTML and save to disk
                                qs.reports.html(returns_data, output=filepath)

                                # Check if file was created at expected location, if not check project root
                                if not pathlib.Path(filepath).exists():
                                    # QuantStats may save to project root with default name
                                    project_root = pathlib.Path(
                                        pathlib.Path(
                                            pathlib.Path(__file__).resolve()
                                        ).parent
                                    ).parent
                                    default_file = (
                                        project_root / "quantstats-tearsheet.html"
                                    )
                                    if pathlib.Path(default_file).exists():
                                        # Move file to our desired location
                                        import shutil

                                        shutil.move(default_file, filepath)

                                # Read the generated HTML file for display
                                with pathlib.Path(filepath).open(encoding="utf-8") as f:
                                    html_content = f.read()

                                # Success message
                                st.success("Tearsheet generated successfully!")

                                # Display HTML content using iframe for better chart rendering
                                st.subheader("QuantStats Tearsheet")

                                # Use iframe to display the HTML with proper chart rendering
                                import streamlit.components.v1 as components

                                components.html(
                                    html_content, height=2000, scrolling=True
                                )

                                # Download button
                                with pathlib.Path(filepath).open("rb") as file:
                                    st.download_button(
                                        label="Download HTML Report",
                                        data=file.read(),
                                        file_name=filename,
                                        mime="text/html",
                                        help="Download the tearsheet as an HTML file",
                                    )

                            except Exception as e:
                                st.error(f"Error generating tearsheet: {str(e)}")
                                st.info(
                                    "Please ensure you have sufficient data points for analysis."
                                )
                    else:
                        st.warning(
                            "No returns data available. Please ensure stock data is loaded properly."
                        )
                else:
                    st.info(
                        "Click 'Generate Tearsheet' to create a comprehensive performance analysis report using QuantStats."
                    )

                    # Show what will be included in the tearsheet
                    st.markdown("Tearsheet Contents")
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

                if (
                    "stock_returns" in st.session_state
                    and len(st.session_state.stock_returns) > 0
                ):
                    returns_data = st.session_state.stock_returns

                    # Calculate additional metrics using QuantStats
                    col1, col2 = st.columns(2)

                    with col1:
                        st.metric(
                            "Sharpe Ratio", f"{qs.stats.sharpe(returns_data):.4f}"
                        )
                        st.metric(
                            "Sortino Ratio", f"{qs.stats.sortino(returns_data):.4f}"
                        )
                        st.metric(
                            "Max Drawdown", f"{qs.stats.max_drawdown(returns_data):.2%}"
                        )

                    with col2:
                        st.metric(
                            "Calmar Ratio", f"{qs.stats.calmar(returns_data):.4f}"
                        )
                        st.metric(
                            "VaR (95%)", f"{qs.stats.value_at_risk(returns_data):.2%}"
                        )
                        st.metric("Win Rate", f"{qs.stats.win_rate(returns_data):.2%}")
                else:
                    st.warning("No returns data available for metrics calculation.")

            # Custom Metrics Display Section
            if (
                selected_metrics
                and "stock_returns" in st.session_state
                and len(st.session_state.stock_returns) > 0
            ):
                st.subheader("Custom Performance Metrics")

                # Calculate custom metrics
                returns_data = st.session_state.stock_returns
                custom_results = calculate_custom_metrics(
                    returns_data, selected_metrics, include_descriptions
                )

                if custom_results:
                    # Create responsive grid layout
                    cols = st.columns(grid_columns)

                    for idx, (_metric_key, metric_data) in enumerate(
                        custom_results.items()
                    ):
                        col_idx = idx % grid_columns

                        with cols[col_idx]:
                            # Create metric card with styling
                            if include_descriptions and metric_data["description"]:
                                st.metric(
                                    label=metric_data["name"],
                                    value=metric_data["value"],
                                    help=metric_data["description"],
                                )
                            else:
                                st.metric(
                                    label=metric_data["name"],
                                    value=metric_data["value"],
                                )
                else:
                    st.info(
                        "No metrics could be calculated. Try selecting different metrics."
                    )
            elif selected_metrics:
                st.info("wSelect a stock and load data to see custom metrics.")

            # Create interactive chart with Altair
            st.subheader("Stock Performance")

            # Prepare data for Altair
            chart_data = stock_price.reset_index()
            chart_data = chart_data.rename(columns={"time": "date", "close": "price"})

            # Create chart based on selected type
            if chart_type == "Line Chart":
                # Line chart
                stock_chart = create_altair_line_chart(chart_data, ticker)
            else:
                # Area chart with gradient
                stock_chart = create_altair_area_chart(chart_data, ticker)

            # Display the Altair chart
            st.altair_chart(stock_chart, use_container_width=True)

            # Create candlestick chart with volume using Bokeh
            st.subheader("Candlestick Chart with Volume")

            # Prepare data for Bokeh
            stock_price_bokeh = stock_price.copy()
            stock_price_bokeh["date"] = stock_price_bokeh.index

            # Create candlestick chart using chart service
            combined_chart = create_plotly_candlestick_chart(stock_price_bokeh, ticker)

            # Display the combined Plotly chart
            st.plotly_chart(combined_chart, use_container_width=True)

    except Exception as e:
        st.error(f"Error loading data for {ticker}: {str(e)}")
        st.info("Please check if the ticker symbol is correct and try again.")

# Footer
st.markdown("---")
st.caption("Data provided by Vnstock API")
