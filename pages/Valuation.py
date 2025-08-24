import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
from datetime import datetime, timedelta

# Import project components and services
from src.components.ui_components import inject_custom_success_styling
from src.services.vnstock_api import fetch_stock_price_data
from src.utils.session_utils import get_analysis_dates
from vnstock import Quote

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
        help="Vietnamese government bond yield"
    )
    
    market_risk_premium = st.number_input(
        "Market Risk Premium (%)", 
        min_value=0.0, 
        max_value=15.0, 
        value=5.0, 
        step=0.1,
        help="Expected return above risk-free rate"
    )
    
    st.subheader("Debt Parameters")
    market_cost_of_debt = st.number_input(
        "Cost of Debt (%)", 
        min_value=0.0, 
        max_value=20.0, 
        value=7.0, 
        step=0.1,
        help="Company's borrowing cost"
    )
    
    tax_rate = st.number_input(
        "Tax Rate (%)", 
        min_value=0.0, 
        max_value=50.0, 
        value=20.0, 
        step=1.0,
        help="Vietnamese corporate tax rate"
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
        st.warning("⚠️ Financial data not loaded. Please visit the Stock Price Analysis page first to load data.")
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
        st.warning("⚠️ Stock price data not found. Please visit Stock Price Analysis page first to load data.")
        st.info("Loading fresh stock price data for beta calculation...")
        # Fallback: Load stock price data if not in session state
        with st.spinner("Loading price data for beta calculation..."):
            stock_price = fetch_stock_price_data(symbol, start_date, end_date)
    
    # Load VNINDEX data for beta calculation
    with st.spinner("Loading VNINDEX data for beta calculation..."):
        quote = Quote(symbol='VNINDEX', source='VCI')
        vnindex_data = quote.history(
            start=start_date.strftime("%Y-%m-%d"),
            end=end_date.strftime("%Y-%m-%d"),
            interval=interval
        )
    
    # Create tabs for different analyses
    tab1, tab2, tab3 = st.tabs(["📊 Beta Analysis", "💰 WACC Calculation", "🎯 Valuation Results"])
    
    with tab1:
        st.header("📊 Beta Calculation & Market Correlation")
        
        if not stock_price.empty and not vnindex_data.empty:
            # 1. Prepare & align prices on common dates
            # Reset index to get 'time' as a regular column since fetch_stock_price_data sets it as index
            stock_data_with_time = stock_price.reset_index()[["time", "close"]]
            aligned = (
                stock_data_with_time
                .rename(columns={"close": "stock_close"})
                .merge(
                    vnindex_data[["time", "close"]].rename(columns={"close": "index_close"}),
                    on="time",
                    how="inner",
                )
                .sort_values("time")
            )
            
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
                correlation = np.corrcoef(returns["stock_ret"], returns["index_ret"])[0, 1]
                r_squared = correlation ** 2
                
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
                st.write(f"- **Period**: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
                st.write(f"- **Beta Interpretation**: Stock moves {abs(beta):.1f}x the market {'in same direction' if beta > 0 else 'in opposite direction'}")
                
            else:
                st.error("❌ Insufficient data points for reliable beta calculation. Try extending the date range.")
        else:
            st.error("❌ Unable to load stock price or market data for beta calculation.")
    
    with tab2:
        st.header("💰 WACC Analysis")
        
        if not balance_sheet.empty and not ratios.empty and 'beta' in locals():
            # Get latest financial data
            latest_balance_sheet = balance_sheet.iloc[-1] if len(balance_sheet) > 0 else None
            latest_ratios = ratios.iloc[-1] if len(ratios) > 0 else None
            
            if latest_balance_sheet is not None and latest_ratios is not None:
                try:
                    # Step 1: Get book values from Balance Sheet
                    short_term_debt = latest_balance_sheet.get('Short-term borrowings (Bn. VND)', 0)
                    long_term_debt = latest_balance_sheet.get('Long-term borrowings (Bn. VND)', 0)
                    total_debt = short_term_debt + long_term_debt
                    
                    # Step 2: Get market values
                    market_value_of_equity = latest_ratios.get(('Chỉ tiêu định giá', 'Market Capital (Bn. VND)'), 0)
                    if isinstance(market_value_of_equity, tuple):
                        market_value_of_equity = market_value_of_equity[1] if len(market_value_of_equity) > 1 else 0
                    
                    market_value_of_debt = total_debt
                    
                    # Calculate total market capital and weights
                    total_market_capital = market_value_of_equity + market_value_of_debt
                    
                    if total_market_capital > 0:
                        market_weight_of_debt = market_value_of_debt / total_market_capital
                        market_weight_of_equity = market_value_of_equity / total_market_capital
                        
                        # Calculate after-tax cost of debt
                        after_tax_cost_of_debt = market_cost_of_debt_decimal * (1 - tax_rate_decimal)
                        
                        # Calculate cost of equity using CAPM
                        cost_of_equity = risk_free_rate_decimal + (beta * market_risk_premium_decimal)
                        
                        # Calculate WACC
                        wacc = (market_weight_of_debt * after_tax_cost_of_debt) + (market_weight_of_equity * cost_of_equity)
                        
                        # Display results in columns
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.subheader("📊 Capital Structure")
                            
                            # Create simple pie chart data
                            capital_data = pd.DataFrame({
                                'Component': ['Debt', 'Equity'],
                                'Weight': [market_weight_of_debt, market_weight_of_equity],
                                'Value': [market_value_of_debt, market_value_of_equity]
                            })
                            
                            # Display as metrics instead of chart for now
                            st.metric("💳 Debt Weight", f"{market_weight_of_debt:.1%}")
                            st.metric("🏛️ Equity Weight", f"{market_weight_of_equity:.1%}")
                            
                        with col2:
                            st.subheader("💎 Key Metrics")
                            
                            st.metric("💰 WACC", f"{wacc:.2%}", help="Weighted Average Cost of Capital")
                            st.metric("📈 Cost of Equity", f"{cost_of_equity:.2%}")
                            st.metric("💳 After-tax Cost of Debt", f"{after_tax_cost_of_debt:.2%}")
                        
                        # Market values
                        st.subheader("📊 Market Values")
                        col3, col4, col5 = st.columns(3)
                        
                        with col3:
                            st.metric("🏛️ Market Cap", f"{market_value_of_equity:,.0f}B VND")
                        with col4:
                            st.metric("💳 Total Debt", f"{total_debt:,.0f}B VND")
                        with col5:
                            st.metric("📊 Total Capital", f"{total_market_capital:,.0f}B VND")
                        
                        # WACC breakdown table
                        st.subheader("🔢 WACC Calculation Breakdown")
                        breakdown_data = {
                            'Component': ['Debt', 'Equity', 'Total'],
                            'Market Value (B VND)': [f"{market_value_of_debt:,.0f}", f"{market_value_of_equity:,.0f}", f"{total_market_capital:,.0f}"],
                            'Weight': [f"{market_weight_of_debt:.1%}", f"{market_weight_of_equity:.1%}", "100.0%"],
                            'Cost': [f"{after_tax_cost_of_debt:.2%}", f"{cost_of_equity:.2%}", f"{wacc:.2%}"],
                            'Contribution': [f"{market_weight_of_debt * after_tax_cost_of_debt:.2%}", f"{market_weight_of_equity * cost_of_equity:.2%}", f"{wacc:.2%}"]
                        }
                        
                        breakdown_df = pd.DataFrame(breakdown_data)
                        st.dataframe(breakdown_df, use_container_width=True)
                        
                    else:
                        st.error("❌ Unable to calculate market values. Check financial data availability.")
                        
                except Exception as e:
                    st.error(f"❌ Error in WACC calculation: {str(e)}")
                    st.write("Available balance sheet columns:", list(balance_sheet.columns) if not balance_sheet.empty else "No data")
                    st.write("Available ratios columns:", list(ratios.columns) if not ratios.empty else "No data")
        else:
            st.error("❌ Unable to load financial data or beta calculation failed.")
    
    with tab3:
        st.header("🎯 Valuation Summary")
        
        if 'wacc' in locals() and not balance_sheet.empty:
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
                    results_data.append({
                        'Year': row.get('yearReport', 'N/A'),
                        'Symbol': symbol,
                        'Market Cap (B VND)': f"{market_value_of_equity:,.0f}",
                        'Total Debt (B VND)': f"{total_debt:,.0f}",
                        'Debt Weight': f"{market_weight_of_debt:.1%}",
                        'Equity Weight': f"{market_weight_of_equity:.1%}",
                        'Beta': f"{beta:.4f}",
                        'Cost of Equity': f"{cost_of_equity:.2%}",
                        'After-tax Cost of Debt': f"{after_tax_cost_of_debt:.2%}",
                        'WACC': f"{wacc:.2%}"
                    })
                
                results_df = pd.DataFrame(results_data)
                st.dataframe(results_df, use_container_width=True)
                
                # Download button
                csv_data = results_df.to_csv(index=False)
                st.download_button(
                    label="📊 Download Valuation Results (CSV)",
                    data=csv_data,
                    file_name=f"valuation_analysis_{symbol}_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        else:
            st.info("Complete the WACC calculation to view summary results.")
    
except Exception as e:
    st.error(f"❌ Error loading data: {str(e)}")
    st.info("Please ensure the selected stock has sufficient financial data available.")