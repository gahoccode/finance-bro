import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
from datetime import datetime

# Import project components and services
from src.components.ui_components import (
    inject_custom_success_styling,
    render_financial_display_options,
)
from src.services.vnstock_api import fetch_stock_price_data
from src.services.data import format_financial_display
from src.services.financial_analysis import calculate_effective_tax_rate
from src.services.session_state import (
    init_global_session_state,
    ensure_valuation_data_loaded,
    get_current_company_name,
)
from src.core.config import DEFAULT_STATUTORY_TAX_RATE
from src.utils.session_utils import get_analysis_dates
from vnstock import Quote, Vnstock
from vnstock.explorer.vci import Company

# Page configuration
st.set_page_config(page_title="Stock Valuation Analysis", layout="wide")
inject_custom_success_styling()

# Initialize global session state
init_global_session_state()

# Page header
st.title("Stock Valuation Analysis")
st.markdown(
    "Comprehensive WACC (Weighted Average Cost of Capital) and Beta analysis for Vietnamese stocks"
)

# Smart data loading for valuation analysis - no more page dependencies!
symbol = st.session_state.get("stock_symbol")

if not symbol:
    st.warning("Please select a stock from the homepage first")
    st.stop()

# Display current selection
company_name = get_current_company_name()
st.success(f"Analyzing valuation for **{company_name}** ({symbol})")

# Progressive data loading with user feedback
loading_result = ensure_valuation_data_loaded(symbol)

if not loading_result["success"]:
    st.error(
        f"❌ Failed to load valuation data: {loading_result.get('error', 'Unknown error')}"
    )
    st.info("Please try refreshing the page or selecting a different stock symbol.")
    st.stop()

try:
    # Get financial statements from session state (now guaranteed to be loaded)
    dataframes = st.session_state.dataframes
    balance_sheet = dataframes.get("BalanceSheet", pd.DataFrame())
    income_statement = dataframes.get("IncomeStatement", pd.DataFrame())
    cash_flow = dataframes.get("CashFlow", pd.DataFrame())
    ratios = dataframes.get("Ratios", pd.DataFrame())

    # Data is already sorted by yearReport in ascending order from the service

    # Calculate effective tax rate from financial data
    effective_tax_rate_data = None
    calculated_tax_rate = DEFAULT_STATUTORY_TAX_RATE

    if not income_statement.empty and not cash_flow.empty:
        try:
            effective_tax_rate_data = calculate_effective_tax_rate(
                income_statement, cash_flow
            )
            if not effective_tax_rate_data.empty:
                # Use the most recent year's effective tax rate
                latest_effective_rate = effective_tax_rate_data.iloc[-1][
                    "Effective Tax Rate"
                ]
                calculated_tax_rate = (
                    latest_effective_rate * 100
                )  # Convert to percentage
        except Exception as e:
            st.warning(
                f"⚠️ Could not calculate effective tax rate: {str(e)}. Using statutory rate."
            )
            calculated_tax_rate = DEFAULT_STATUTORY_TAX_RATE

    # Sidebar for WACC parameters
    with st.sidebar:
        st.header("⚙️ WACC Parameters")

        st.subheader("Market Parameters")
        risk_free_rate = st.number_input(
            "Risk-free Rate (%)",
            min_value=0.0,
            max_value=15.0,
            value=3.0,
            step=0.1,
            help="Vietnamese government bond yield",
        )

        market_risk_premium = st.number_input(
            "Market Risk Premium (%)",
            min_value=0.0,
            max_value=15.0,
            value=5.0,
            step=0.1,
            help="Expected return above risk-free rate",
        )

        st.subheader("Debt Parameters")
        market_cost_of_debt = st.number_input(
            "Cost of Debt (%)",
            min_value=0.0,
            max_value=20.0,
            value=7.0,
            step=0.1,
            help="Company's borrowing cost",
        )

        tax_rate = st.number_input(
            "Tax Rate (%)",
            min_value=0.0,
            max_value=50.0,
            value=calculated_tax_rate,
            step=1.0,
            help="Effective tax rate calculated from financial data (override if needed)",
        )

    # Convert percentage inputs to decimals
    risk_free_rate_decimal = risk_free_rate / 100
    market_risk_premium_decimal = market_risk_premium / 100
    market_cost_of_debt_decimal = market_cost_of_debt / 100
    tax_rate_decimal = tax_rate / 100

    # Get global analysis dates
    start_date, end_date = get_analysis_dates()
    interval = "1D"

    # Get stock price data (loaded automatically by ensure_valuation_data_loaded)
    if (
        "stock_price_data" in st.session_state
        and not st.session_state.stock_price_data.empty
    ):
        stock_price = st.session_state.stock_price_data
        st.success("✅ Using cached stock price data")
    else:
        # Fallback: Load stock price data if not in session state
        st.info("Loading fresh stock price data for beta calculation...")
        with st.spinner("Loading price data for beta calculation..."):
            stock_price = fetch_stock_price_data(symbol, start_date, end_date)

    # Load VNINDEX data for beta calculation
    with st.spinner("Loading VNINDEX data for beta calculation..."):
        quote = Quote(symbol="VNINDEX", source="VCI")
        vnindex_data = quote.history(
            start=start_date.strftime("%Y-%m-%d"),
            end=end_date.strftime("%Y-%m-%d"),
            interval=interval,
        )

    # Create tabs for different analyses
    tab1, tab2, tab3 = st.tabs(
        ["📊 Beta Analysis", "💰 WACC Calculation", "🎯 Valuation Results"]
    )

    with tab1:
        st.header("📊 Beta Calculation & Market Correlation")

        if not stock_price.empty and not vnindex_data.empty:
            # 1. Prepare & align prices on common dates
            # Convert vnindex_data to have datetime index like stock_price
            vnindex_data["time"] = pd.to_datetime(vnindex_data["time"])
            vnindex_data = vnindex_data.set_index("time")

            # Align both dataframes on their datetime index
            aligned = pd.concat(
                [
                    stock_price[["close"]].rename(columns={"close": "stock_close"}),
                    vnindex_data[["close"]].rename(columns={"close": "index_close"}),
                ],
                axis=1,
                join="inner",
            ).dropna()

            if len(aligned) > 30:  # Ensure sufficient data points
                # 2. Compute daily percentage returns
                aligned["stock_ret"] = aligned["stock_close"].pct_change()
                aligned["index_ret"] = aligned["index_close"].pct_change()

                # 3. Drop the first NaN row produced by pct_change
                returns = aligned.dropna(subset=["stock_ret", "index_ret"])

                # 4. Covariance matrix (2×2) and beta calculation
                cov_matrix = np.cov(returns["stock_ret"], returns["index_ret"])
                beta = cov_matrix[0, 1] / cov_matrix[1, 1]

                # Calculate correlation coefficient
                correlation = np.corrcoef(returns["stock_ret"], returns["index_ret"])[
                    0, 1
                ]
                r_squared = correlation**2

                # Display beta metrics
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("📈 Stock Beta", f"{beta:.4f}")

                with col2:
                    st.metric("📊 R-squared", f"{r_squared:.4f}")

                with col3:
                    st.metric("🎯 Correlation", f"{correlation:.4f}")

                # Risk interpretation
                if beta < 0.8:
                    risk_level = "Low Risk (Defensive)"
                    risk_color = "green"
                elif beta < 1.2:
                    risk_level = "Market Risk"
                    risk_color = "blue"
                else:
                    risk_level = "High Risk (Aggressive)"
                    risk_color = "red"

                st.info(f"**Risk Level**: {risk_level}")

                # Display data summary
                st.subheader("📋 Beta Analysis Summary")
                st.write(f"- **Data Points**: {len(returns):,} trading days")
                st.write(
                    f"- **Period**: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
                )
                st.write(
                    f"- **Beta Interpretation**: Stock moves {abs(beta):.1f}x the market {'in same direction' if beta > 0 else 'in opposite direction'}"
                )

            else:
                st.error(
                    "❌ Insufficient data points for reliable beta calculation. Try extending the date range."
                )
        else:
            st.error(
                "❌ Unable to load stock price or market data for beta calculation."
            )

    with tab2:
        st.header("💰 WACC Analysis")

        # Add financial display options
        display_unit = render_financial_display_options(
            placement="main",
            unique_key="wacc_display",
            title="💰 Financial Display Options",
            help_text="Choose how financial values are displayed in Market Values section",
        )

        # Tax Rate Used in WACC
        is_using_effective_rate = (
            effective_tax_rate_data is not None
            and not effective_tax_rate_data.empty
            and abs(tax_rate - calculated_tax_rate) < 0.1
        )

        tax_rate_type = (
            "Effective Tax Rate" if is_using_effective_rate else "Statutory Tax Rate"
        )
        help_text = (
            "Calculated from financial statements"
            if is_using_effective_rate
            else "Manual override or fallback statutory rate"
        )

        st.metric(
            f"🔢 {tax_rate_type} Used in WACC", f"{tax_rate:.1f}%", help=help_text
        )

        # Historical effective tax rates table
        if effective_tax_rate_data is not None and not effective_tax_rate_data.empty:
            st.subheader("📋 Historical Effective Tax Rates")
            historical_tax_display = effective_tax_rate_data.copy()

            # Apply financial formatting to monetary columns
            historical_tax_display["Profit Before Tax (Bn. VND)"] = (
                historical_tax_display["Profit Before Tax (Bn. VND)"].apply(
                    lambda x: format_financial_display(x, display_unit, 0)
                )
            )

            historical_tax_display["Tax Paid (Bn. VND)"] = historical_tax_display[
                "Tax Paid (Bn. VND)"
            ].apply(lambda x: format_financial_display(x, display_unit, 0))

            # Convert effective tax rate to percentage
            historical_tax_display["Effective Tax Rate"] = (
                historical_tax_display["Effective Tax Rate"] * 100
            ).round(1)

            # Update column names to reflect formatting
            historical_tax_display = historical_tax_display.rename(
                columns={
                    "Profit Before Tax (Bn. VND)": f"Profit Before Tax ({display_unit.capitalize()})",
                    "Tax Paid (Bn. VND)": f"Tax Paid ({display_unit.capitalize()})",
                    "Effective Tax Rate": "Effective Tax Rate (%)",
                }
            )
            st.dataframe(
                historical_tax_display, use_container_width=True, hide_index=True
            )

        if not balance_sheet.empty and not ratios.empty and "beta" in locals():
            # Get latest financial data (data is already sorted by yearReport ascending)
            latest_balance_sheet = (
                balance_sheet.iloc[-1] if len(balance_sheet) > 0 else None
            )
            latest_ratios = ratios.iloc[-1] if len(ratios) > 0 else None

            if latest_balance_sheet is not None and latest_ratios is not None:
                # Ensure we're comparing data from the same year (data already sorted)
                balance_sheet_year = latest_balance_sheet.get("yearReport")
                ratios_year = latest_ratios.get("yearReport")

                if balance_sheet_year != ratios_year:
                    st.warning(
                        f"⚠️ Data alignment issue: Balance Sheet ({balance_sheet_year}) and Ratios ({ratios_year}) from different years"
                    )

                try:
                    # Step 1: Get book values from Balance Sheet
                    # Note: All dataframe values are in original scale (raw VND values)
                    short_term_debt = latest_balance_sheet.get(
                        "Short-term borrowings (Bn. VND)", 0
                    )
                    long_term_debt = latest_balance_sheet.get(
                        "Long-term borrowings (Bn. VND)", 0
                    )
                    # Values are already in raw VND scale
                    total_debt = short_term_debt + long_term_debt

                    # Extract current price from stock price data (needed for DCF calculation)
                    current_price = 0
                    actual_current_price = 0
                    if not stock_price.empty:
                        current_price = stock_price["close"].iloc[-1]
                        actual_current_price = (
                            current_price * 1000
                        )  # Convert to original scale

                    # Step 2: Calculate market cap using VnStock Company class (primary) with manual fallback
                    market_value_of_equity = 0
                    outstanding_shares = 0

                    try:
                        # PRIMARY METHOD: Use VnStock Company class for enterprise value
                        company = Company(symbol)
                        ev_data = company.ratio_summary()
                        market_value_of_equity = (
                            ev_data["ev"].iloc[0] if not ev_data.empty else 0
                        )

                        if market_value_of_equity > 0:
                            st.success(
                                "✅ Using VnStock Company Class (Enterprise Value)"
                            )

                            # Get shares data for DCF calculation
                            try:
                                # Try to get outstanding shares from the same Company instance
                                stock = Vnstock().stock(symbol=symbol, source="VCI")
                                overview = stock.company.overview()
                                if "issue_share" in overview.columns:
                                    outstanding_shares = (
                                        overview["issue_share"].iloc[0]
                                        if len(overview) > 0
                                        else 0
                                    )
                            except Exception:
                                outstanding_shares = 0
                        else:
                            raise ValueError(
                                "VnStock Company class returned zero or invalid enterprise value"
                            )

                    except Exception as primary_error:
                        st.warning(f"⚠️ Primary method failed: {str(primary_error)}")
                        st.info("🔄 Falling back to manual calculation...")

                        try:
                            # FALLBACK METHOD: Manual calculation using shares * price
                            stock = Vnstock().stock(symbol=symbol, source="VCI")
                            overview = stock.company.overview()

                            # Get outstanding shares
                            if "issue_share" in overview.columns:
                                outstanding_shares = (
                                    overview["issue_share"].iloc[0]
                                    if len(overview) > 0
                                    else 0
                                )
                            else:
                                raise KeyError(
                                    f"'issue_share' column not found in overview data. Available columns: {list(overview.columns)}"
                                )

                            # Calculate market cap manually using already extracted price data
                            market_value_of_equity = (
                                outstanding_shares * actual_current_price
                            )

                            if market_value_of_equity > 0:
                                st.success(
                                    "✅ Fallback successful: Manual Calculation (Shares × Price)"
                                )
                            else:
                                raise ValueError(
                                    "Manual calculation resulted in zero market cap"
                                )

                        except Exception as fallback_error:
                            st.error(f"❌ Both calculation methods failed:")
                            st.error(
                                f"   • Primary (VnStock Company): {str(primary_error)}"
                            )
                            st.error(f"   • Fallback (Manual): {str(fallback_error)}")
                            st.stop()

                    # Validate final result
                    if market_value_of_equity <= 0:
                        st.error(
                            "❌ Unable to calculate market cap. All methods failed."
                        )
                        st.stop()

                    market_value_of_debt = total_debt

                    # Calculate total market capital and weights
                    total_market_capital = market_value_of_equity + market_value_of_debt

                    if total_market_capital > 0:
                        market_weight_of_debt = (
                            market_value_of_debt / total_market_capital
                        )
                        market_weight_of_equity = (
                            market_value_of_equity / total_market_capital
                        )

                        # Calculate after-tax cost of debt
                        after_tax_cost_of_debt = market_cost_of_debt_decimal * (
                            1 - tax_rate_decimal
                        )

                        # Calculate cost of equity using CAPM
                        cost_of_equity = risk_free_rate_decimal + (
                            beta * market_risk_premium_decimal
                        )

                        # Calculate WACC
                        wacc = (market_weight_of_debt * after_tax_cost_of_debt) + (
                            market_weight_of_equity * cost_of_equity
                        )

                        # Display results in columns
                        col1, col2 = st.columns(2)

                        with col1:
                            st.subheader("📊 Capital Structure")

                            # Create pie chart data
                            capital_data = pd.DataFrame(
                                {
                                    "Component": ["Debt", "Equity"],
                                    "Weight": [
                                        market_weight_of_debt,
                                        market_weight_of_equity,
                                    ],
                                    "Value": [
                                        market_value_of_debt,
                                        market_value_of_equity,
                                    ],
                                }
                            )

                            # Create pie chart using Altair
                            pie_chart = (
                                alt.Chart(capital_data)
                                .mark_arc(
                                    innerRadius=40,
                                    outerRadius=100,
                                    stroke="white",
                                    strokeWidth=2,
                                )
                                .encode(
                                    theta=alt.Theta("Weight:Q"),
                                    color=alt.Color(
                                        "Component:N",
                                        scale=alt.Scale(range=["#76706C", "#56524D"]),
                                        legend=alt.Legend(title="Capital Components"),
                                    ),
                                    tooltip=[
                                        alt.Tooltip("Component:N", title="Component"),
                                        alt.Tooltip(
                                            "Weight:Q", title="Weight", format=".1%"
                                        ),
                                        alt.Tooltip(
                                            "Value:Q", title="Value", format=",.0f"
                                        ),
                                    ],
                                )
                                .properties(
                                    width=220, height=220, title="Capital Structure"
                                )
                            )

                            st.altair_chart(pie_chart, use_container_width=True)

                        with col2:
                            st.subheader("💎 Key Metrics")

                            st.metric(
                                "💰 WACC",
                                f"{wacc:.1%}",
                                help="Weighted Average Cost of Capital",
                            )
                            st.metric("📈 Cost of Equity", f"{cost_of_equity:.1%}")
                            st.metric(
                                "💳 After-tax Cost of Debt",
                                f"{after_tax_cost_of_debt:.1%}",
                            )

                        # Market values with user-selected formatting
                        st.subheader("📊 Market Values")
                        col3, col4, col5 = st.columns(3)

                        with col3:
                            st.metric(
                                "🏛️ Market Cap",
                                format_financial_display(
                                    market_value_of_equity, display_unit, 0
                                ),
                            )
                        with col4:
                            st.metric(
                                "💳 Total Debt",
                                format_financial_display(total_debt, display_unit, 0),
                            )
                        with col5:
                            st.metric(
                                "📊 Total Capital",
                                format_financial_display(
                                    total_market_capital, display_unit, 0
                                ),
                            )

                        # WACC breakdown table
                        st.subheader("🔢 WACC Calculation Breakdown")
                        breakdown_data = {
                            "Component": ["Debt", "Equity", "Total"],
                            f"Market Value ({display_unit.capitalize()})": [
                                format_financial_display(
                                    market_value_of_debt, display_unit, 0
                                ),
                                format_financial_display(
                                    market_value_of_equity, display_unit, 0
                                ),
                                format_financial_display(
                                    total_market_capital, display_unit, 0
                                ),
                            ],
                            "Weight": [
                                f"{market_weight_of_debt:.1%}",
                                f"{market_weight_of_equity:.1%}",
                                "100.0%",
                            ],
                            "Cost": [
                                f"{after_tax_cost_of_debt:.2%}",
                                f"{cost_of_equity:.2%}",
                                f"{wacc:.2%}",
                            ],
                            "Contribution": [
                                f"{market_weight_of_debt * after_tax_cost_of_debt:.2%}",
                                f"{market_weight_of_equity * cost_of_equity:.2%}",
                                f"{wacc:.2%}",
                            ],
                        }

                        breakdown_df = pd.DataFrame(breakdown_data)
                        st.dataframe(
                            breakdown_df, use_container_width=True, hide_index=True
                        )

                        # Share count comparison section
                        st.subheader("📊 Share Count Comparison")

                        try:
                            # Collect both share count values from overview data
                            issue_share_value = (
                                overview["issue_share"].iloc[0]
                                if "issue_share" in overview.columns
                                and len(overview) > 0
                                else "N/A"
                            )
                            financial_ratio_share_value = (
                                overview["financial_ratio_issue_share"].iloc[0]
                                if "financial_ratio_issue_share" in overview.columns
                                and len(overview) > 0
                                else "N/A"
                            )

                            # Calculate market caps for both methods using actual price (in VND)
                            if (
                                isinstance(
                                    issue_share_value,
                                    (int, float, np.integer, np.floating),
                                )
                                and issue_share_value > 0
                                and actual_current_price > 0
                            ):
                                market_cap_issue_share = (
                                    issue_share_value * actual_current_price
                                )
                            else:
                                market_cap_issue_share = "N/A"

                            if (
                                isinstance(
                                    financial_ratio_share_value,
                                    (int, float, np.integer, np.floating),
                                )
                                and financial_ratio_share_value > 0
                                and actual_current_price > 0
                            ):
                                market_cap_financial_ratio = (
                                    financial_ratio_share_value * actual_current_price
                                )
                            else:
                                market_cap_financial_ratio = "N/A"

                            # Calculate percentage difference if both values are valid
                            if (
                                isinstance(
                                    issue_share_value,
                                    (int, float, np.integer, np.floating),
                                )
                                and isinstance(
                                    financial_ratio_share_value,
                                    (int, float, np.integer, np.floating),
                                )
                                and issue_share_value > 0
                                and financial_ratio_share_value > 0
                            ):
                                percentage_diff = (
                                    (issue_share_value - financial_ratio_share_value)
                                    / financial_ratio_share_value
                                ) * 100
                                percentage_diff_str = f"{percentage_diff:+.2f}%"
                            else:
                                percentage_diff_str = "N/A"

                            # Create comparison DataFrame
                            comparison_data = {
                                "Metric": [
                                    "issue_share (used)",
                                    "financial_ratio_issue_share",
                                    "Difference (%)",
                                ],
                                "Share Count": [
                                    f"{issue_share_value:,.0f}"
                                    if isinstance(
                                        issue_share_value,
                                        (int, float, np.integer, np.floating),
                                    )
                                    else issue_share_value,
                                    f"{financial_ratio_share_value:,.0f}"
                                    if isinstance(
                                        financial_ratio_share_value,
                                        (int, float, np.integer, np.floating),
                                    )
                                    else financial_ratio_share_value,
                                    percentage_diff_str,
                                ],
                                f"Market Cap ({display_unit.capitalize()})": [
                                    format_financial_display(
                                        market_cap_issue_share, display_unit, 2
                                    )
                                    if isinstance(market_cap_issue_share, (int, float))
                                    else market_cap_issue_share,
                                    format_financial_display(
                                        market_cap_financial_ratio, display_unit, 2
                                    )
                                    if isinstance(
                                        market_cap_financial_ratio, (int, float)
                                    )
                                    else market_cap_financial_ratio,
                                    "-",
                                ],
                            }

                            comparison_df = pd.DataFrame(comparison_data)
                            st.dataframe(
                                comparison_df, use_container_width=True, hide_index=True
                            )

                        except Exception as e:
                            st.error(
                                f"❌ Error creating share count comparison: {str(e)}"
                            )

                    else:
                        st.error(
                            "❌ Unable to calculate market values. Check financial data availability."
                        )

                except Exception as e:
                    st.error(f"❌ Error in WACC calculation: {str(e)}")
        else:
            st.error("❌ Unable to load financial data or beta calculation failed.")

    with tab3:
        st.header("🎯 DCF Intrinsic Value")

        if (
            "wacc" in locals()
            and not cash_flow.empty
            and not balance_sheet.empty
            and "current_price" in locals()
            and current_price > 0
        ):
            # Calculate historical free cash flow using Vietnamese column names
            try:
                # Get historical cash flow data (already sorted by yearReport ascending)
                historical_fcf = []
                historical_years = []
                historical_ocf = []  # Store OCF components for display
                historical_capex = []  # Store Capex components for display

                # Use exact Vietnamese column names
                ocf_column = "Net cash inflows/outflows from operating activities"
                capex_column = "Purchase of fixed assets"

                # Validate required columns exist
                if ocf_column not in cash_flow.columns:
                    st.error(
                        f"❌ Required column '{ocf_column}' not found in cash flow data"
                    )
                    st.error(f"Available columns: {list(cash_flow.columns)}")
                    st.stop()

                if capex_column not in cash_flow.columns:
                    st.error(
                        f"❌ Required column '{capex_column}' not found in cash flow data"
                    )
                    st.error(f"Available columns: {list(cash_flow.columns)}")
                    st.stop()

                for _, row in cash_flow.iterrows():
                    year = row.get("yearReport")
                    operating_cash_flow = row.get(ocf_column, 0)
                    capex_value = row.get(capex_column, 0)

                    # Calculate free cash flow: Operating Cash Flow - Capital Expenditures
                    # Note: capex is typically negative, so we subtract it
                    free_cash_flow = operating_cash_flow - abs(capex_value)

                    if year and not pd.isna(free_cash_flow) and free_cash_flow != 0:
                        historical_fcf.append(free_cash_flow)
                        historical_years.append(year)
                        historical_ocf.append(operating_cash_flow)
                        historical_capex.append(capex_value)

                # Debug information - check data quality
                if len(historical_fcf) < 2:
                    st.error(
                        "❌ Insufficient cash flow data for DCF analysis. Need at least 2 years of data."
                    )
                    if len(historical_fcf) == 0:
                        st.error(
                            "🔍 Debug: No valid FCF data found. This could be due to:"
                        )
                        st.error("- All cash flow values are NaN or zero")
                        st.error("- Missing yearReport data")
                        st.error("- Data filtering conditions (line 762)")
                    elif len(historical_fcf) == 1:
                        st.error("🔍 Debug: Only 1 year of valid FCF data found.")
                        st.error(
                            f"Available year: {historical_years[0] if historical_years else 'Unknown'}"
                        )

                    # Show sample data for debugging
                    st.subheader("🔍 Cash Flow Data Debug")
                    debug_data = []
                    for _, row in cash_flow.head(3).iterrows():
                        debug_data.append(
                            {
                                "Year": row.get("yearReport", "N/A"),
                                "OCF": row.get(ocf_column, "N/A"),
                                "Capex": row.get(capex_column, "N/A"),
                                "FCF Raw": row.get(ocf_column, 0)
                                - abs(row.get(capex_column, 0)),
                            }
                        )
                    debug_df = pd.DataFrame(debug_data)
                    st.dataframe(debug_df, use_container_width=True, hide_index=True)

                    st.stop()

                # Time Series Analysis for FCF Forecasting

                # Create time series DataFrame
                fcf_ts = pd.DataFrame(
                    {"year": historical_years, "fcf": historical_fcf}
                ).sort_values("year")

                # Calculate various growth metrics for time series analysis
                growth_rates = []
                for i in range(1, len(historical_fcf)):
                    if historical_fcf[i - 1] != 0:
                        growth_rate = (historical_fcf[i] - historical_fcf[i - 1]) / abs(
                            historical_fcf[i - 1]
                        )
                        growth_rates.append(growth_rate)

                # Time series trend analysis
                if len(fcf_ts) >= 3:
                    # Linear trend analysis using numpy polyfit
                    years_numeric = np.array(fcf_ts["year"])
                    fcf_values = np.array(fcf_ts["fcf"])

                    # Fit linear trend
                    trend_coeffs = np.polyfit(years_numeric, fcf_values, 1)
                    trend_slope = trend_coeffs[0]
                    trend_intercept = trend_coeffs[1]

                    # Calculate R-squared for trend fit
                    fcf_trend = trend_slope * years_numeric + trend_intercept
                    ss_res = np.sum((fcf_values - fcf_trend) ** 2)
                    ss_tot = np.sum((fcf_values - np.mean(fcf_values)) ** 2)
                    trend_r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

                    # Calculate trend-based growth rate
                    if len(fcf_values) > 1:
                        avg_fcf = np.mean(fcf_values)
                        trend_growth_rate = (
                            (trend_slope / avg_fcf) if avg_fcf != 0 else 0
                        )
                    else:
                        trend_growth_rate = 0
                else:
                    trend_growth_rate = 0
                    trend_r_squared = 0

                # Volatility analysis
                if len(growth_rates) > 1:
                    growth_volatility = np.std(growth_rates)
                    growth_cv = (
                        growth_volatility / abs(np.mean(growth_rates))
                        if np.mean(growth_rates) != 0
                        else float("inf")
                    )
                else:
                    growth_volatility = 0
                    growth_cv = 0

                # Multiple forecasting methods
                forecasting_methods = {}

                # 1. Simple historical average
                avg_historical_growth = np.mean(growth_rates) if growth_rates else 0.10
                forecasting_methods["Historical Average"] = avg_historical_growth

                # 2. Median (more robust to outliers)
                median_historical_growth = (
                    np.median(growth_rates) if growth_rates else 0.10
                )
                forecasting_methods["Historical Median"] = median_historical_growth

                # 3. Trend-based forecast
                forecasting_methods["Linear Trend"] = trend_growth_rate

                # 4. Weighted recent years (give more weight to recent performance)
                if len(growth_rates) >= 2:
                    weights = np.linspace(
                        0.5, 1.0, len(growth_rates)
                    )  # More weight to recent years
                    weighted_growth = np.average(growth_rates, weights=weights)
                    forecasting_methods["Weighted Recent"] = weighted_growth
                else:
                    forecasting_methods["Weighted Recent"] = avg_historical_growth

                # 5. Conservative estimate (lower quartile for risk adjustment)
                if len(growth_rates) >= 4:
                    conservative_growth = np.percentile(growth_rates, 25)
                    forecasting_methods["Conservative (25th percentile)"] = (
                        conservative_growth
                    )
                else:
                    forecasting_methods["Conservative (25th percentile)"] = (
                        min(growth_rates) if growth_rates else 0.05
                    )

                # Select best forecasting method based on data quality and trend strength
                if trend_r_squared > 0.7 and len(fcf_ts) >= 4:
                    # Strong trend - use trend-based forecast
                    recommended_growth = trend_growth_rate
                    recommended_method = "Linear Trend"
                elif growth_cv < 0.5:  # Low volatility
                    # Stable growth - use weighted recent
                    recommended_growth = forecasting_methods["Weighted Recent"]
                    recommended_method = "Weighted Recent"
                else:
                    # High volatility - use conservative median
                    recommended_growth = median_historical_growth
                    recommended_method = "Historical Median"

                latest_fcf = (
                    historical_fcf[-1] if historical_fcf else 1000000000
                )  # Fallback

                # Enhanced Time Series Analysis Display
                st.subheader("📈 Time Series Analysis Results")

                # Display forecasting method analysis
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("📊 Recommended Method", recommended_method)
                    st.metric("🎯 Recommended Growth", f"{recommended_growth:.1%}")

                with col2:
                    if "trend_r_squared" in locals():
                        st.metric("📈 Trend R²", f"{trend_r_squared:.3f}")
                    if "growth_volatility" in locals():
                        st.metric("📊 Growth Volatility", f"{growth_volatility:.1%}")

                with col3:
                    st.metric("📋 Data Points", len(historical_fcf))
                    st.metric(
                        "📅 Years Analyzed",
                        f"{min(historical_years)}-{max(historical_years)}",
                    )

                # Display all forecasting methods comparison
                st.subheader("🔄 Forecasting Methods Comparison")
                methods_df = pd.DataFrame(
                    [
                        {
                            "Method": method,
                            "Growth Rate": f"{rate:.1%}",
                            "Selected": "✅" if method == recommended_method else "",
                        }
                        for method, rate in forecasting_methods.items()
                    ]
                )
                st.dataframe(methods_df, use_container_width=True, hide_index=True)

                # Multi-year FCF projections using different base years
                st.subheader("📊 Multi-Year Base Analysis")

                # Create projections from different historical starting points
                multi_year_projections = []

                # Use each historical year as a potential base for projection
                for i, (base_year, base_fcf) in enumerate(
                    zip(historical_years, historical_fcf)
                ):
                    # Calculate growth from this base year to latest year
                    if (
                        base_year != historical_years[-1]
                    ):  # Skip if it's the latest year
                        years_ahead = historical_years[-1] - base_year
                        if years_ahead > 0 and base_fcf != 0:
                            # Handle negative FCF values properly to avoid complex numbers
                            fcf_ratio = latest_fcf / base_fcf

                            if fcf_ratio > 0:
                                # Normal CAGR calculation for positive ratio
                                implied_cagr = (fcf_ratio ** (1 / years_ahead)) - 1
                            elif latest_fcf > 0 and base_fcf < 0:
                                # From negative to positive FCF - use absolute growth rate
                                implied_cagr = abs(fcf_ratio) ** (1 / years_ahead) - 1
                            elif latest_fcf < 0 and base_fcf > 0:
                                # From positive to negative FCF - negative growth
                                implied_cagr = (
                                    -(abs(fcf_ratio) ** (1 / years_ahead)) + 1
                                )
                            else:
                                # Both negative - calculate as if positive and make negative
                                implied_cagr = -(
                                    (abs(fcf_ratio) ** (1 / years_ahead)) - 1
                                )

                            # Only include if CAGR is reasonable (between -50% and +200%)
                            if -0.5 <= implied_cagr <= 2.0:
                                multi_year_projections.append(
                                    {
                                        "Base Year": base_year,
                                        "Base FCF": base_fcf,
                                        "Years to Latest": years_ahead,
                                        "Implied CAGR": implied_cagr,
                                        "Weight": 1.0
                                        / (
                                            len(historical_years) - i
                                        ),  # More weight to recent years
                                    }
                                )

                if multi_year_projections:
                    # Calculate weighted average CAGR from multiple base years
                    total_weight = sum(
                        proj["Weight"] for proj in multi_year_projections
                    )
                    weighted_cagr = (
                        sum(
                            proj["Implied CAGR"] * proj["Weight"]
                            for proj in multi_year_projections
                        )
                        / total_weight
                    )

                    # Display multi-year analysis
                    proj_df = pd.DataFrame(multi_year_projections)
                    proj_df["Base FCF"] = proj_df["Base FCF"].apply(
                        lambda x: format_financial_display(x, display_unit, 0)
                    )
                    proj_df["Implied CAGR"] = proj_df["Implied CAGR"].apply(
                        lambda x: f"{x:.1%}"
                    )
                    proj_df["Weight"] = proj_df["Weight"].apply(lambda x: f"{x:.2f}")

                    st.dataframe(proj_df, use_container_width=True, hide_index=True)
                    st.info(f"📊 **Multi-Year Weighted CAGR**: {weighted_cagr:.1%}")

                # DCF Parameters with sidebar controls
                with st.sidebar:
                    st.header("🎯 DCF Parameters")
                    st.subheader("Growth Assumptions")

                    # Enhanced historical context with time series insights
                    if growth_rates:
                        st.info(
                            f"📊 **Time Series Analysis**:\n"
                            f"• Recommended: {recommended_growth:.1%} ({recommended_method})\n"
                            f"• Historical Avg: {avg_historical_growth:.1%}\n"
                            f"• Historical Median: {median_historical_growth:.1%}\n"
                            f"• Volatility: {growth_volatility:.1%}\n"
                            f"• Range: {min(growth_rates):.1%} to {max(growth_rates):.1%}"
                        )

                        if "weighted_cagr" in locals():
                            st.info(f"📈 **Multi-Year CAGR**: {weighted_cagr:.1%}")

                    # Stage 1: High Growth Period
                    stage1_years = st.slider(
                        "Stage 1 Duration (years)",
                        min_value=3,
                        max_value=10,
                        value=5,
                        help="High growth period duration",
                    )

                    # Use recommended growth as intelligent default
                    default_stage1 = (
                        recommended_growth * 100 if recommended_growth > 0.05 else 10.0
                    )
                    stage1_growth = st.number_input(
                        "Stage 1 Growth Rate (%)",
                        min_value=-50.0,
                        max_value=100.0,
                        value=default_stage1,
                        step=1.0,
                        help=f"Default based on time series analysis: {recommended_method} = {recommended_growth:.1%}",
                    )

                    # Stage 2: Terminal Growth
                    terminal_growth = st.number_input(
                        "Terminal Growth Rate (%)",
                        min_value=0.0,
                        max_value=10.0,
                        value=3.0,
                        step=0.5,
                        help="Long-term sustainable growth rate (typically 2-4% for developed markets)",
                    )

                    # Advanced option: Use multi-year weighted FCF as base
                    if "weighted_cagr" in locals():
                        use_weighted_base = st.checkbox(
                            "Use Multi-Year Weighted Analysis",
                            value=True,
                            help="Use weighted analysis from all historical years instead of just latest year",
                        )

                # Convert percentages to decimals
                stage1_growth_rate = stage1_growth / 100
                terminal_growth_rate = terminal_growth / 100

                # Determine base FCF for projections
                if (
                    "use_weighted_base" in locals()
                    and use_weighted_base
                    and "weighted_cagr" in locals()
                ):
                    # Use multi-year weighted analysis
                    base_fcf_for_projection = latest_fcf
                    effective_growth_rate = (
                        weighted_cagr  # Use weighted CAGR from multi-year analysis
                    )
                    projection_method = (
                        f"Multi-Year Weighted CAGR ({weighted_cagr:.1%})"
                    )
                else:
                    # Use traditional single-year base
                    base_fcf_for_projection = latest_fcf
                    effective_growth_rate = stage1_growth_rate
                    projection_method = f"Single-Year Base ({stage1_growth_rate:.1%})"

                # DCF Calculations
                st.subheader("📊 DCF Model Results")
                st.info(f"**Projection Method**: {projection_method}")

                # Stage 1: High Growth Period Cash Flows
                stage1_fcf = []
                stage1_pv = []

                for year in range(1, stage1_years + 1):
                    if (
                        "use_weighted_base" in locals()
                        and use_weighted_base
                        and "weighted_cagr" in locals()
                    ):
                        # Use weighted CAGR for first few years, then transition to user-selected growth
                        transition_years = min(
                            3, stage1_years
                        )  # Transition over first 3 years

                        if year <= transition_years:
                            # Blend weighted CAGR with user growth rate over transition period
                            weight_historical = (
                                transition_years - year + 1
                            ) / transition_years
                            blended_growth = (weight_historical * weighted_cagr) + (
                                (1 - weight_historical) * stage1_growth_rate
                            )
                        else:
                            # Use user-selected growth rate after transition
                            blended_growth = stage1_growth_rate

                        projected_fcf = base_fcf_for_projection * (
                            (1 + blended_growth) ** year
                        )
                    else:
                        # Traditional approach: use user-selected growth rate
                        projected_fcf = base_fcf_for_projection * (
                            (1 + stage1_growth_rate) ** year
                        )

                    stage1_fcf.append(projected_fcf)

                    # Calculate present value
                    pv = projected_fcf / ((1 + wacc) ** year)
                    stage1_pv.append(pv)

                # Stage 2: Terminal Value
                terminal_fcf = stage1_fcf[-1] * (1 + terminal_growth_rate)
                terminal_value = terminal_fcf / (wacc - terminal_growth_rate)
                terminal_pv = terminal_value / ((1 + wacc) ** stage1_years)

                # Enterprise Value
                enterprise_value = sum(stage1_pv) + terminal_pv

                # Equity Value = Enterprise Value - Net Debt
                # Calculate net debt properly: Total Debt - Cash and Cash Equivalents
                cash_and_equivalents = latest_balance_sheet.get(
                    "Cash and cash equivalents (Bn. VND)", 0
                )
                short_term_investments = latest_balance_sheet.get(
                    "Short-term investments (Bn. VND)", 0
                )

                # Net debt = Total debt - (Cash + Short-term investments)
                net_debt = total_debt - (cash_and_equivalents + short_term_investments)
                equity_value = enterprise_value - net_debt

                # Intrinsic Value per Share (in original VND scale)
                intrinsic_value_per_share = (
                    equity_value / outstanding_shares if outstanding_shares > 0 else 0
                )

                # Current price comparison (convert current price to original VND scale)
                current_price_original_scale = (
                    current_price * 1000
                )  # Convert from thousands to original VND
                upside_downside = (
                    (intrinsic_value_per_share - current_price_original_scale)
                    / current_price_original_scale
                    if current_price_original_scale > 0
                    else 0
                )

                # Display key results
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric(
                        "🎯 Intrinsic Value",
                        f"{intrinsic_value_per_share:,.0f} VND",
                        help="DCF-based intrinsic value per share",
                    )

                with col2:
                    st.metric(
                        "💰 Current Price", f"{current_price_original_scale:,.0f} VND"
                    )

                with col3:
                    st.metric(
                        "📈 Upside/Downside",
                        f"{upside_downside:+.1%}",
                        delta=f"{upside_downside:+.1%}",
                    )

                with col4:
                    recommendation = (
                        "🟢 BUY"
                        if upside_downside > 0.20
                        else "🟡 HOLD"
                        if upside_downside > -0.10
                        else "🔴 SELL"
                    )
                    st.metric("📋 Recommendation", recommendation)

                # Detailed DCF breakdown
                st.subheader("🔢 DCF Calculation Breakdown")

                # Create detailed table
                dcf_data = []

                # Base year (Year 0)
                dcf_data.append(
                    {
                        "Year": "0",
                        "FCF": format_financial_display(latest_fcf, display_unit, 0),
                        "Growth Rate": "-",
                        "Discount Factor": "1.000",
                        "Present Value": "-",
                        "Type": "Base Year",
                    }
                )

                # Stage 1 projections
                for i, (fcf, pv) in enumerate(zip(stage1_fcf, stage1_pv), 1):
                    discount_factor = 1 / ((1 + wacc) ** i)
                    dcf_data.append(
                        {
                            "Year": str(i),
                            "FCF": format_financial_display(fcf, display_unit, 0),
                            "Growth Rate": f"{stage1_growth_rate:.1%}",
                            "Discount Factor": f"{discount_factor:.3f}",
                            "Present Value": format_financial_display(
                                pv, display_unit, 0
                            ),
                            "Type": "High Growth",
                        }
                    )

                # Terminal year
                terminal_discount_factor = 1 / ((1 + wacc) ** stage1_years)
                dcf_data.append(
                    {
                        "Year": "Terminal",
                        "FCF": format_financial_display(
                            terminal_value, display_unit, 0
                        ),
                        "Growth Rate": f"{terminal_growth_rate:.1%}",
                        "Discount Factor": f"{terminal_discount_factor:.3f}",
                        "Present Value": format_financial_display(
                            terminal_pv, display_unit, 0
                        ),
                        "Type": "Terminal Value",
                    }
                )

                dcf_df = pd.DataFrame(dcf_data)
                st.dataframe(dcf_df, use_container_width=True, hide_index=True)

                # Summary calculation table
                st.subheader("💎 Valuation Summary")
                summary_data = {
                    "Component": [
                        "PV of Stage 1 Cash Flows",
                        "Present Value of Terminal Value",
                        "Enterprise Value",
                        "Total Debt",
                        "Cash & Cash Equivalents",
                        "Short-term Investments",
                        "Net Debt (Total Debt - Cash - ST Investments)",
                        "Equity Value",
                        "Outstanding Shares",
                        "Intrinsic Value per Share",
                    ],
                    "Value": [
                        format_financial_display(sum(stage1_pv), display_unit, 0),
                        format_financial_display(terminal_pv, display_unit, 0),
                        format_financial_display(enterprise_value, display_unit, 0),
                        format_financial_display(total_debt, display_unit, 0),
                        format_financial_display(cash_and_equivalents, display_unit, 0),
                        format_financial_display(
                            short_term_investments, display_unit, 0
                        ),
                        format_financial_display(net_debt, display_unit, 0),
                        format_financial_display(equity_value, display_unit, 0),
                        f"{outstanding_shares:,.0f} shares",
                        f"{intrinsic_value_per_share:,.0f} VND",
                    ],
                }

                summary_df = pd.DataFrame(summary_data)
                st.dataframe(summary_df, use_container_width=True, hide_index=True)

                # Historical FCF context
                st.subheader("📊 Historical Free Cash Flow Context")
                historical_data = []
                for i, (year, fcf, ocf, capex) in enumerate(
                    zip(
                        historical_years,
                        historical_fcf,
                        historical_ocf,
                        historical_capex,
                    )
                ):
                    historical_data.append(
                        {
                            "Year": year,
                            "Operating Cash Flow": format_financial_display(
                                ocf, display_unit, 0
                            ),
                            "Capital Expenditures": format_financial_display(
                                capex, display_unit, 0
                            ),
                            "Free Cash Flow": format_financial_display(
                                fcf, display_unit, 0
                            ),
                            "YoY Growth": "N/A",
                        }
                    )

                # Add growth rates
                for i, growth_rate in enumerate(growth_rates, 1):
                    if i < len(historical_data):
                        historical_data[i]["YoY Growth"] = f"{growth_rate:+.1%}"

                historical_df = pd.DataFrame(historical_data)
                st.dataframe(historical_df, use_container_width=True, hide_index=True)

                # Download DCF results
                dcf_results = {
                    "Symbol": symbol,
                    "Analysis Date": datetime.now().strftime("%Y-%m-%d"),
                    "Current Price (VND)": current_price_original_scale,
                    "Intrinsic Value (VND)": intrinsic_value_per_share,
                    "Upside/Downside": f"{upside_downside:+.1%}",
                    "Enterprise Value": enterprise_value,
                    "Equity Value": equity_value,
                    "WACC": f"{wacc:.2%}",
                    "Stage 1 Growth": f"{stage1_growth_rate:.1%}",
                    "Terminal Growth": f"{terminal_growth_rate:.1%}",
                    "Stage 1 Years": stage1_years,
                }

                dcf_csv = pd.DataFrame([dcf_results]).to_csv(index=False)
                st.download_button(
                    label="📊 Download DCF Analysis (CSV)",
                    data=dcf_csv,
                    file_name=f"dcf_analysis_{symbol}_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                )

            except Exception as e:
                st.error(f"❌ Error in DCF calculation: {str(e)}")
                st.info(
                    "Ensure cash flow data is available with the required Vietnamese column names."
                )

        else:
            st.info(
                "💡 Complete the WACC calculation and ensure cash flow data is loaded to perform DCF analysis."
            )

            # Show required data status
            st.subheader("📋 Data Requirements Check")
            requirements = [
                ("WACC Calculation", "wacc" in locals()),
                ("Cash Flow Data", not cash_flow.empty),
                ("Balance Sheet Data", not balance_sheet.empty),
                ("Stock Price Data", not stock_price.empty),
                (
                    "Current Price Available",
                    "current_price" in locals() and current_price > 0,
                ),
            ]

            for requirement, status in requirements:
                status_icon = "✅" if status else "❌"
                st.write(f"{status_icon} {requirement}")

            if not all(status for _, status in requirements):
                st.info(
                    "💡 Visit previous tabs and Stock Price Analysis page to load required data. Ensure WACC calculation completes successfully."
                )

except Exception as e:
    st.error(f"❌ Error loading data: {str(e)}")
    st.info("Please ensure the selected stock has sufficient financial data available.")
