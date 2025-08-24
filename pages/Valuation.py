import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
from datetime import datetime, timedelta

# Import project components and services
from src.components.ui_components import (
    inject_custom_success_styling,
    render_financial_display_options,
)
from src.services.vnstock_api import fetch_stock_price_data
from src.services.data_service import format_financial_display
from src.utils.session_utils import get_analysis_dates
from vnstock import Quote, Vnstock

# Page configuration
st.set_page_config(page_title="📊 Stock Valuation Analysis", layout="wide")
inject_custom_success_styling()

# Initialize global session state for dates
if "analysis_start_date" not in st.session_state:
    st.session_state.analysis_start_date = pd.to_datetime("2024-01-01")
if "analysis_end_date" not in st.session_state:
    st.session_state.analysis_end_date = pd.to_datetime("today") - pd.Timedelta(days=1)

# Page header
st.title("📊 Stock Valuation Analysis")
st.markdown(
    "Comprehensive WACC (Weighted Average Cost of Capital) and Beta analysis for Vietnamese stocks"
)

# Check if stock is selected from homepage
if "stock_symbol" not in st.session_state or st.session_state.stock_symbol is None:
    st.warning("⚠️ Please select a stock from the homepage first")
    st.stop()

symbol = st.session_state.stock_symbol
st.success(f"✅ Analyzing valuation for **{symbol}**")

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
        value=20.0,
        step=1.0,
        help="Vietnamese corporate tax rate",
    )

# Convert percentage inputs to decimals
risk_free_rate_decimal = risk_free_rate / 100
market_risk_premium_decimal = market_risk_premium / 100
market_cost_of_debt_decimal = market_cost_of_debt / 100
tax_rate_decimal = tax_rate / 100

# Get global analysis dates
start_date, end_date = get_analysis_dates()
interval = "1D"

try:
    # Check if financial data is available in session state
    if "dataframes" not in st.session_state:
        st.warning(
            "⚠️ Financial data not loaded. Please visit the Stock Price Analysis page first to load data."
        )
        st.stop()

    # Get financial statements from session state
    dataframes = st.session_state.dataframes
    balance_sheet = dataframes.get("BalanceSheet", pd.DataFrame())
    income_statement = dataframes.get("IncomeStatement", pd.DataFrame())
    cash_flow = dataframes.get("CashFlow", pd.DataFrame())
    ratios = dataframes.get("Ratios", pd.DataFrame())

    # Check if stock price data exists in session state from Stock Price Analysis page
    if "stock_price_data" in st.session_state:
        stock_price = st.session_state.stock_price_data
        st.success("✅ Using stock price data from Stock Price Analysis page")
    else:
        st.warning(
            "⚠️ Stock price data not found. Please visit Stock Price Analysis page first to load data."
        )
        st.info("Loading fresh stock price data for beta calculation...")
        # Fallback: Load stock price data if not in session state
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

        if not balance_sheet.empty and not ratios.empty and "beta" in locals():
            # Get latest financial data
            latest_balance_sheet = (
                balance_sheet.iloc[-1] if len(balance_sheet) > 0 else None
            )
            latest_ratios = ratios.iloc[-1] if len(ratios) > 0 else None

            if latest_balance_sheet is not None and latest_ratios is not None:
                # Ensure we're comparing data from the same year
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

                    # Step 2: Calculate market cap using Vnstock company overview and current price
                    try:
                        # Get company overview data for outstanding shares using newer Vnstock approach
                        stock = Vnstock().stock(symbol=symbol, source='VCI')
                        overview = stock.company.overview()
                        
                        # Use issue_share as the correct column name for outstanding shares
                        if "issue_share" in overview.columns:
                            outstanding_shares = overview["issue_share"].iloc[0] if len(overview) > 0 else 0
                        else:
                            raise KeyError(f"'issue_share' column not found in overview data. Available columns: {list(overview.columns)}")

                        # Get current stock price from the latest price data
                        current_price = (
                            stock_price["close"].iloc[-1]
                            if not stock_price.empty
                            else 0
                        )

                        # Convert price to original scale: vnstock returns prices in thousands of VND
                        actual_current_price = current_price * 1000

                        # Calculate market cap: outstanding shares * actual price (in VND)
                        # Note: issue_share is actual share count, current_price needs to be converted from thousands
                        market_value_of_equity = outstanding_shares * actual_current_price

                        if market_value_of_equity <= 0:
                            st.error(
                                "❌ Unable to calculate market cap. Invalid outstanding shares or current price."
                            )
                            st.stop()

                    except Exception as e:
                        st.error(
                            f"❌ Error calculating market cap from company overview: {str(e)}"
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

                            # Create simple pie chart data
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

                            # Display as metrics instead of chart for now
                            st.metric("💳 Debt Weight", f"{market_weight_of_debt:.1%}")
                            st.metric(
                                "🏛️ Equity Weight", f"{market_weight_of_equity:.1%}"
                            )

                        with col2:
                            st.subheader("💎 Key Metrics")

                            st.metric(
                                "💰 WACC",
                                f"{wacc:.2%}",
                                help="Weighted Average Cost of Capital",
                            )
                            st.metric("📈 Cost of Equity", f"{cost_of_equity:.2%}")
                            st.metric(
                                "💳 After-tax Cost of Debt",
                                f"{after_tax_cost_of_debt:.2%}",
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
                                format_financial_display(market_value_of_debt, display_unit, 0),
                                format_financial_display(market_value_of_equity, display_unit, 0),
                                format_financial_display(total_market_capital, display_unit, 0),
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
                        st.dataframe(breakdown_df, use_container_width=True)

                        # Share count comparison section
                        st.subheader("📊 Share Count Comparison")
                        
                        try:
                            # Collect both share count values from overview data
                            issue_share_value = overview["issue_share"].iloc[0] if "issue_share" in overview.columns and len(overview) > 0 else "N/A"
                            financial_ratio_share_value = overview["financial_ratio_issue_share"].iloc[0] if "financial_ratio_issue_share" in overview.columns and len(overview) > 0 else "N/A"
                            
                            # Calculate market caps for both methods using actual price (in VND)
                            if isinstance(issue_share_value, (int, float, np.integer, np.floating)) and issue_share_value > 0 and actual_current_price > 0:
                                market_cap_issue_share = issue_share_value * actual_current_price
                            else:
                                market_cap_issue_share = "N/A"
                                
                            if isinstance(financial_ratio_share_value, (int, float, np.integer, np.floating)) and financial_ratio_share_value > 0 and actual_current_price > 0:
                                market_cap_financial_ratio = financial_ratio_share_value * actual_current_price
                            else:
                                market_cap_financial_ratio = "N/A"
                            
                            # Calculate percentage difference if both values are valid
                            if (isinstance(issue_share_value, (int, float, np.integer, np.floating)) and 
                                isinstance(financial_ratio_share_value, (int, float, np.integer, np.floating)) and 
                                issue_share_value > 0 and financial_ratio_share_value > 0):
                                percentage_diff = ((issue_share_value - financial_ratio_share_value) / financial_ratio_share_value) * 100
                                percentage_diff_str = f"{percentage_diff:+.2f}%"
                            else:
                                percentage_diff_str = "N/A"
                            
                            # Create comparison DataFrame
                            comparison_data = {
                                "Metric": [
                                    "issue_share (used)",
                                    "financial_ratio_issue_share", 
                                    "Difference (%)"
                                ],
                                "Share Count": [
                                    f"{issue_share_value:,.0f}" if isinstance(issue_share_value, (int, float, np.integer, np.floating)) else issue_share_value,
                                    f"{financial_ratio_share_value:,.0f}" if isinstance(financial_ratio_share_value, (int, float, np.integer, np.floating)) else financial_ratio_share_value,
                                    percentage_diff_str
                                ],
                                f"Market Cap ({display_unit.capitalize()})": [
                                    format_financial_display(market_cap_issue_share, display_unit, 2) if isinstance(market_cap_issue_share, (int, float)) else market_cap_issue_share,
                                    format_financial_display(market_cap_financial_ratio, display_unit, 2) if isinstance(market_cap_financial_ratio, (int, float)) else market_cap_financial_ratio,
                                    "-"
                                ]
                            }
                            
                            comparison_df = pd.DataFrame(comparison_data)
                            st.dataframe(comparison_df, use_container_width=True)
                            
                            # Add explanation
                            st.info(
                                "**Note**: The `issue_share` column represents the current outstanding shares and is used for market cap calculation. "
                                "The `financial_ratio_issue_share` may represent shares used in financial ratio calculations and could differ from current outstanding shares."
                            )
                            
                        except Exception as e:
                            st.error(f"❌ Error creating share count comparison: {str(e)}")
                            st.write("Available overview columns:", list(overview.columns) if 'overview' in locals() else "No overview data")

                    else:
                        st.error(
                            "❌ Unable to calculate market values. Check financial data availability."
                        )

                except Exception as e:
                    st.error(f"❌ Error in WACC calculation: {str(e)}")
                    st.write(
                        "Available balance sheet columns:",
                        list(balance_sheet.columns)
                        if not balance_sheet.empty
                        else "No data",
                    )
                    st.write(
                        "Available ratios columns:",
                        list(ratios.columns) if not ratios.empty else "No data",
                    )
        else:
            st.error("❌ Unable to load financial data or beta calculation failed.")

    with tab3:
        st.header("🎯 Valuation Summary")

        if "wacc" in locals() and not balance_sheet.empty:
            # Create results summary
            st.subheader("📋 Valuation Analysis Results")

            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("📊 Stock Symbol", symbol)
            with col2:
                st.metric("💰 WACC", f"{wacc:.2%}")
            with col3:
                st.metric("📈 Beta", f"{beta:.4f}")
            with col4:
                st.metric("🎯 Analysis Date", datetime.now().strftime("%Y-%m-%d"))

            # Create detailed results table
            if len(balance_sheet) > 0:
                results_data = []

                for idx, row in balance_sheet.iterrows():
                    results_data.append(
                        {
                            "Year": row.get("yearReport", "N/A"),
                            "Symbol": symbol,
                            "Market Cap (B VND)": f"{market_value_of_equity:,.0f}",
                            "Total Debt (B VND)": f"{total_debt:,.0f}",
                            "Debt Weight": f"{market_weight_of_debt:.1%}",
                            "Equity Weight": f"{market_weight_of_equity:.1%}",
                            "Beta": f"{beta:.4f}",
                            "Cost of Equity": f"{cost_of_equity:.2%}",
                            "After-tax Cost of Debt": f"{after_tax_cost_of_debt:.2%}",
                            "WACC": f"{wacc:.2%}",
                        }
                    )

                results_df = pd.DataFrame(results_data)
                st.dataframe(results_df, use_container_width=True)

                # Download button
                csv_data = results_df.to_csv(index=False)
                st.download_button(
                    label="📊 Download Valuation Results (CSV)",
                    data=csv_data,
                    file_name=f"valuation_analysis_{symbol}_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                )
        else:
            st.info("Complete the WACC calculation to view summary results.")

except Exception as e:
    st.error(f"❌ Error loading data: {str(e)}")
    st.info("Please ensure the selected stock has sufficient financial data available.")
