import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from src.components.ui_components import inject_custom_success_styling

# Page configuration
st.set_page_config(
    page_title="DuPont Analysis - Finance Bro",
    page_icon="📊",
    layout="wide",
)

# Apply custom CSS styling for success alerts
inject_custom_success_styling()

def create_dupont_analysis(IncomeStatement, BalanceSheet, CashFlow):
    """
    Create a 3-factor DuPont analysis based on the three financial statements.
    
    DuPont Analysis: ROE = Net Profit Margin × Asset Turnover × Financial Leverage
    
    Where:
    - Net Profit Margin = Net Income / Revenue
    - Asset Turnover = Revenue / Average Total Assets
    - Financial Leverage = Average Total Assets / Average Shareholders' Equity
    
    Returns:
    --------
    pandas DataFrame
        DataFrame with DuPont analysis results
    """
    try:
        # Step 1: Identify correct column names for Vietnamese financial data
        # Common variations in Vietnamese financial statements
        revenue_cols = ['Revenue (Bn. VND)', 'Net sales (Bn. VND)', 'Revenue', 'Net sales']
        net_income_cols = ['Attribute to parent company (Bn. VND)', 'Net Income (Bn. VND)', 'Net profit (Bn. VND)', 'Profit after tax (Bn. VND)']
        assets_cols = ['TOTAL ASSETS (Bn. VND)', 'Total assets (Bn. VND)', 'TOTAL ASSETS', 'Total assets']
        equity_cols = ["OWNER'S EQUITY(Bn.VND)", "Owner's equity (Bn. VND)", "OWNER'S EQUITY", "Owner's equity", "Shareholders' equity (Bn. VND)"]
        
        # Find matching columns
        revenue_col = None
        for col in revenue_cols:
            if col in IncomeStatement.columns:
                revenue_col = col
                break
        
        net_income_col = None
        for col in net_income_cols:
            if col in IncomeStatement.columns:
                net_income_col = col
                break
        
        assets_col = None
        for col in assets_cols:
            if col in BalanceSheet.columns:
                assets_col = col
                break
        
        equity_col = None
        for col in equity_cols:
            if col in BalanceSheet.columns:
                equity_col = col
                break
        
        # Validate required columns exist
        if not all([revenue_col, net_income_col, assets_col, equity_col]):
            missing_cols = []
            if not revenue_col: missing_cols.append("Revenue")
            if not net_income_col: missing_cols.append("Net Income") 
            if not assets_col: missing_cols.append("Total Assets")
            if not equity_col: missing_cols.append("Owner's Equity")
            
            raise ValueError(f"Missing required columns: {', '.join(missing_cols)}")
        
        # Step 2: Combine necessary data from financial statements
        income_data = IncomeStatement[['ticker', 'yearReport', revenue_col, net_income_col]].copy()
        income_data = income_data.rename(columns={
            revenue_col: 'Revenue (Bn. VND)',
            net_income_col: 'Net Income (Bn. VND)'
        })
        
        # Add Balance Sheet data for assets and equity
        balance_data = BalanceSheet[['ticker', 'yearReport', assets_col, equity_col]].copy()
        balance_data = balance_data.rename(columns={
            assets_col: 'TOTAL ASSETS (Bn. VND)',
            equity_col: "OWNER'S EQUITY(Bn.VND)"
        })
        
        # Merge the dataframes
        dupont_df = pd.merge(income_data, balance_data, on=['ticker', 'yearReport'], how='inner')
        
        # Step 3: Sort by ticker and year for calculations
        dupont_df = dupont_df.sort_values(['ticker', 'yearReport'])
        
        # Calculate average total assets and equity (current + previous year) / 2
        dupont_df['Prev_Assets'] = dupont_df.groupby('ticker')['TOTAL ASSETS (Bn. VND)'].shift(1)
        dupont_df['Prev_Equity'] = dupont_df.groupby('ticker')["OWNER'S EQUITY(Bn.VND)"].shift(1)
        
        # Calculate averages
        dupont_df['Average Total Assets (Bn. VND)'] = (dupont_df['TOTAL ASSETS (Bn. VND)'] + dupont_df['Prev_Assets']) / 2
        dupont_df['Average Equity (Bn. VND)'] = (dupont_df["OWNER'S EQUITY(Bn.VND)"] + dupont_df['Prev_Equity']) / 2
        
        # For the first year of each ticker, use current year values
        dupont_df['Average Total Assets (Bn. VND)'] = dupont_df['Average Total Assets (Bn. VND)'].fillna(
            dupont_df['TOTAL ASSETS (Bn. VND)'])
        dupont_df['Average Equity (Bn. VND)'] = dupont_df['Average Equity (Bn. VND)'].fillna(
            dupont_df["OWNER'S EQUITY(Bn.VND)"])
        
        # Step 4: Calculate the 3 DuPont components
        # Net Profit Margin = Net Income / Revenue
        dupont_df['Net Profit Margin'] = dupont_df['Net Income (Bn. VND)'] / dupont_df['Revenue (Bn. VND)']
        
        # Asset Turnover = Revenue / Average Total Assets
        dupont_df['Asset Turnover'] = dupont_df['Revenue (Bn. VND)'] / dupont_df['Average Total Assets (Bn. VND)']
        
        # Financial Leverage = Average Total Assets / Average Equity
        dupont_df['Financial Leverage'] = dupont_df['Average Total Assets (Bn. VND)'] / dupont_df['Average Equity (Bn. VND)']
        
        # Step 5: Calculate ROE using DuPont formula
        dupont_df['ROE (DuPont)'] = dupont_df['Net Profit Margin'] * dupont_df['Asset Turnover'] * dupont_df['Financial Leverage']
        
        # Step 6: Calculate ROE directly for validation
        dupont_df['ROE (Direct)'] = dupont_df['Net Income (Bn. VND)'] / dupont_df['Average Equity (Bn. VND)']
        
        # Step 7: Clean up and select relevant columns
        dupont_analysis = dupont_df[[
            'ticker', 'yearReport', 
            'Net Income (Bn. VND)', 'Revenue (Bn. VND)',
            'Average Total Assets (Bn. VND)', 'Average Equity (Bn. VND)',
            'Net Profit Margin', 'Asset Turnover', 'Financial Leverage',
            'ROE (DuPont)', 'ROE (Direct)'
        ]]
        
        # Convert ratios to percentages for better readability
        dupont_analysis['Net Profit Margin'] = dupont_analysis['Net Profit Margin'] * 100
        dupont_analysis['ROE (DuPont)'] = dupont_analysis['ROE (DuPont)'] * 100
        dupont_analysis['ROE (Direct)'] = dupont_analysis['ROE (Direct)'] * 100
        
        # Round values for better display
        dupont_analysis = dupont_analysis.round({
            'Net Profit Margin': 2,
            'Asset Turnover': 2,
            'Financial Leverage': 2,
            'ROE (DuPont)': 2,
            'ROE (Direct)': 2
        })
        
        return dupont_analysis
        
    except Exception as e:
        st.error(f"Error in DuPont analysis calculation: {str(e)}")
        return None

# Get stock symbol from session state
if "stock_symbol" in st.session_state and st.session_state.stock_symbol:
    stock_symbol = st.session_state.stock_symbol
else:
    st.warning(
        "⚠️ No stock symbol selected. Please go to the main Finance Bro page and select a stock symbol first."
    )
    st.stop()

# Page header
st.markdown("# 📊 DuPont Analysis")
st.markdown(f"**Stock Symbol:** {stock_symbol}")

# Get company full name from cached symbols DataFrame
company_name = stock_symbol
if "symbols_df" in st.session_state and st.session_state.symbols_df is not None:
    try:
        symbols_df = st.session_state.symbols_df
        matching_company = symbols_df[symbols_df["symbol"] == stock_symbol]
        if not matching_company.empty and "organ_name" in symbols_df.columns:
            company_name = matching_company["organ_name"].iloc[0]
    except Exception:
        company_name = stock_symbol

st.subheader(f"DuPont Analysis for {company_name}")

# Check if financial data is available
if "dataframes" not in st.session_state:
    st.warning("⚠️ No financial data loaded. Please go to the AI Chat Analysis page and click 'Analyze Stock' first.")
    st.stop()

# Information about DuPont Analysis
with st.expander("ℹ️ About DuPont Analysis", expanded=False):
    st.markdown("""
    **DuPont Analysis** breaks down Return on Equity (ROE) into three key components:
    
    **ROE = Net Profit Margin × Asset Turnover × Financial Leverage**
    
    Where:
    - **Net Profit Margin** = Net Income / Revenue (Profitability)
    - **Asset Turnover** = Revenue / Average Total Assets (Efficiency) 
    - **Financial Leverage** = Average Total Assets / Average Equity (Leverage)
    
    This analysis helps identify the key drivers of a company's profitability and provides insights into:
    - **Profitability**: How much profit the company generates per dollar of sales
    - **Efficiency**: How effectively the company uses its assets to generate sales
    - **Leverage**: How much debt the company uses to finance its assets
    """)

# Perform DuPont Analysis
try:
    dataframes = st.session_state.dataframes
    
    # Check if required dataframes exist
    required_dfs = ['IncomeStatement', 'BalanceSheet', 'CashFlow']
    missing_dfs = [df for df in required_dfs if df not in dataframes]
    
    if missing_dfs:
        st.error(f"❌ Missing required financial statements: {', '.join(missing_dfs)}")
        st.info("Please ensure all financial data is loaded in the AI Chat Analysis page.")
        st.stop()
    
    # Create DuPont analysis
    with st.spinner("🔄 Calculating DuPont Analysis..."):
        dupont_analysis = create_dupont_analysis(
            dataframes['IncomeStatement'],
            dataframes['BalanceSheet'], 
            dataframes['CashFlow']
        )
    
    if dupont_analysis is not None and not dupont_analysis.empty:
        st.success("✅ DuPont Analysis completed successfully!")
        
        # Display the DuPont analysis dataframe
        st.subheader("📈 DuPont Analysis Results")
        
        # Create columns for metrics summary
        if len(dupont_analysis) > 0:
            latest_year = dupont_analysis['yearReport'].max()
            latest_data = dupont_analysis[dupont_analysis['yearReport'] == latest_year].iloc[0]
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Net Profit Margin", 
                    f"{latest_data['Net Profit Margin']:.2f}%",
                    help="Net Income / Revenue"
                )
            
            with col2:
                st.metric(
                    "Asset Turnover", 
                    f"{latest_data['Asset Turnover']:.2f}x",
                    help="Revenue / Average Total Assets"
                )
            
            with col3:
                st.metric(
                    "Financial Leverage", 
                    f"{latest_data['Financial Leverage']:.2f}x",
                    help="Average Total Assets / Average Equity"
                )
            
            with col4:
                st.metric(
                    "ROE (DuPont)", 
                    f"{latest_data['ROE (DuPont)']:.2f}%",
                    help="Net Profit Margin × Asset Turnover × Financial Leverage"
                )
        
        # Display the complete dataframe with formatting
        st.markdown("### 📊 Complete DuPont Analysis Table")
        
        # Configure column display
        column_config = {
            "ticker": st.column_config.TextColumn("Ticker", width="small"),
            "yearReport": st.column_config.NumberColumn("Year", width="small"),
            "Net Income (Bn. VND)": st.column_config.NumberColumn("Net Income (Bn. VND)", format="%.1f"),
            "Revenue (Bn. VND)": st.column_config.NumberColumn("Revenue (Bn. VND)", format="%.1f"),
            "Average Total Assets (Bn. VND)": st.column_config.NumberColumn("Avg. Total Assets (Bn. VND)", format="%.1f"),
            "Average Equity (Bn. VND)": st.column_config.NumberColumn("Avg. Equity (Bn. VND)", format="%.1f"),
            "Net Profit Margin": st.column_config.NumberColumn("Net Profit Margin (%)", format="%.2f"),
            "Asset Turnover": st.column_config.NumberColumn("Asset Turnover (x)", format="%.2f"),
            "Financial Leverage": st.column_config.NumberColumn("Financial Leverage (x)", format="%.2f"),
            "ROE (DuPont)": st.column_config.NumberColumn("ROE - DuPont (%)", format="%.2f"),
            "ROE (Direct)": st.column_config.NumberColumn("ROE - Direct (%)", format="%.2f")
        }
        
        # Sort dataframe by year in descending order (most recent first)
        dupont_analysis_sorted = dupont_analysis.sort_values('yearReport', ascending=False)
        
        # Display dataframe with enhanced formatting
        st.dataframe(
            dupont_analysis_sorted,
            use_container_width=True,
            column_config=column_config,
            hide_index=True
        )
        
        # Altair chart for DuPont components trend
        if len(dupont_analysis) > 1:
            st.markdown("### 📈 DuPont Components Trend")
            
            # Prepare data for Altair chart
            chart_data = dupont_analysis.copy()
            
            # Create the multi-line chart
            base = alt.Chart(chart_data).add_selection(
                alt.selection_interval(bind='scales')
            )
            
            # Net Profit Margin line
            margin_line = base.mark_line(
                color='#76706C',
                strokeWidth=3
            ).encode(
                x=alt.X('yearReport:O', title='Year', axis=alt.Axis(labelAngle=0)),
                y=alt.Y('Net Profit Margin:Q', title='Net Profit Margin (%)', scale=alt.Scale(zero=False)),
                tooltip=['yearReport:O', 'Net Profit Margin:Q']
            )
            
            # Asset Turnover line
            turnover_line = base.mark_line(
                color='#76706C',
                strokeWidth=3
            ).encode(
                x=alt.X('yearReport:O', title='Year'),
                y=alt.Y('Asset Turnover:Q', 
                       title='Asset Turnover (x)', 
                       scale=alt.Scale(zero=False)),
                tooltip=['yearReport:O', 'Asset Turnover:Q']
            ).resolve_scale(y='independent')
            
            # Financial Leverage line
            leverage_line = base.mark_line(
                color='#76706C',
                strokeWidth=3
            ).encode(
                x=alt.X('yearReport:O', title='Year'),
                y=alt.Y('Financial Leverage:Q', 
                       title='Financial Leverage (x)', 
                       scale=alt.Scale(zero=False)),
                tooltip=['yearReport:O', 'Financial Leverage:Q']
            ).resolve_scale(y='independent')
            
            # Combine charts using layering with separate y-axes
            combined_chart = alt.vconcat(
                margin_line.properties(
                    title="Net Profit Margin (%)",
                    width=600,
                    height=150
                ),
                turnover_line.properties(
                    title="Asset Turnover (x)",
                    width=600, 
                    height=150
                ),
                leverage_line.properties(
                    title="Financial Leverage (x)",
                    width=600,
                    height=150
                )
            ).resolve_scale(
                x='shared'
            )
            
            st.altair_chart(combined_chart, use_container_width=True)
            
            # Legend explanation
            st.markdown("""
            **Chart Information:**
            - **Net Profit Margin (%)** - Top panel
            - **Asset Turnover (x)** - Middle panel
            - **Financial Leverage (x)** - Bottom panel
            
            *Each component is displayed in its own panel for better visualization of trends.*
            """)

        # Download button for CSV export
        csv_data = dupont_analysis.to_csv(index=False)
        st.download_button(
            label="📥 Download DuPont Analysis as CSV",
            data=csv_data,
            file_name=f"dupont_analysis_{stock_symbol}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        # Interpretation and insights
        st.markdown("### 🔍 Analysis Insights")
        
        if len(dupont_analysis) > 1:
            # Trend analysis for multiple years
            years_sorted = dupont_analysis.sort_values('yearReport')
            latest = years_sorted.iloc[-1]
            previous = years_sorted.iloc[-2]
            
            roe_change = latest['ROE (DuPont)'] - previous['ROE (DuPont)']
            margin_change = latest['Net Profit Margin'] - previous['Net Profit Margin']
            turnover_change = latest['Asset Turnover'] - previous['Asset Turnover']
            leverage_change = latest['Financial Leverage'] - previous['Financial Leverage']
            
            st.markdown(f"""
            **Year-over-Year Changes ({previous['yearReport']:.0f} to {latest['yearReport']:.0f}):**
            
            - **ROE Change**: {roe_change:+.2f}% {'📈' if roe_change > 0 else '📉' if roe_change < 0 else '➡️'}
            - **Net Profit Margin**: {margin_change:+.2f}% {'📈' if margin_change > 0 else '📉' if margin_change < 0 else '➡️'}
            - **Asset Turnover**: {turnover_change:+.2f}x {'📈' if turnover_change > 0 else '📉' if turnover_change < 0 else '➡️'}
            - **Financial Leverage**: {leverage_change:+.2f}x {'📈' if leverage_change > 0 else '📉' if leverage_change < 0 else '➡️'}
            """)
            
            # Identify main driver of ROE change
            drivers = []
            if abs(margin_change) > 0.5:
                drivers.append(f"Profitability ({'improved' if margin_change > 0 else 'declined'})")
            if abs(turnover_change) > 0.05:
                drivers.append(f"Asset efficiency ({'improved' if turnover_change > 0 else 'declined'})")
            if abs(leverage_change) > 0.1:
                drivers.append(f"Financial leverage ({'increased' if leverage_change > 0 else 'decreased'})")
            
            if drivers:
                st.info(f"**Key ROE drivers**: {', '.join(drivers)}")
        
        # Performance benchmarks
        latest_roe = dupont_analysis['ROE (DuPont)'].iloc[-1]
        latest_margin = dupont_analysis['Net Profit Margin'].iloc[-1]
        latest_turnover = dupont_analysis['Asset Turnover'].iloc[-1]
        
        st.markdown("### 📊 Performance Assessment")
        
        # ROE assessment
        if latest_roe > 15:
            roe_assessment = "🟢 Excellent ROE (>15%)"
        elif latest_roe > 10:
            roe_assessment = "🟡 Good ROE (10-15%)"
        elif latest_roe > 5:
            roe_assessment = "🟠 Average ROE (5-10%)"
        else:
            roe_assessment = "🔴 Low ROE (<5%)"
        
        # Margin assessment
        if latest_margin > 20:
            margin_assessment = "🟢 High profitability (>20%)"
        elif latest_margin > 10:
            margin_assessment = "🟡 Good profitability (10-20%)"
        elif latest_margin > 5:
            margin_assessment = "🟠 Average profitability (5-10%)"
        else:
            margin_assessment = "🔴 Low profitability (<5%)"
        
        st.markdown(f"""
        - **ROE Performance**: {roe_assessment}
        - **Profitability**: {margin_assessment}
        - **Asset Efficiency**: {'🟢 Efficient' if latest_turnover > 1 else '🟡 Moderate' if latest_turnover > 0.5 else '🔴 Low'} (Asset Turnover: {latest_turnover:.2f}x)
        """)
    
    else:
        st.error("❌ Could not calculate DuPont analysis. Please check the financial data.")

except Exception as e:
    st.error(f"❌ Error performing DuPont analysis: {str(e)}")
    st.info("Please ensure financial data is properly loaded and try again.")

# Footer
st.markdown("---")
st.markdown("""
**About DuPont Analysis**: This analysis provides insights into the key drivers of return on equity by decomposing 
ROE into profitability, efficiency, and leverage components. Use this to understand what drives your company's 
financial performance and compare with industry benchmarks.
""")