import streamlit as st
import pandas as pd
import altair as alt
from src.components.ui_components import (
    inject_custom_success_styling,
    render_financial_display_options,
)
from src.services.financial_analysis import (
    create_dupont_analysis,
    calculate_capital_employed,
    calculate_degree_of_financial_leverage,
)
from src.services.data import (
    format_financial_display,
    convert_dataframe_for_display,
)

# Page configuration
st.set_page_config(
    page_title="DuPont Analysis - Finance Bro",
    page_icon="",
    layout="wide",
)

# Apply custom CSS styling for success alerts
inject_custom_success_styling()


# Get stock symbol from session state
if "stock_symbol" in st.session_state and st.session_state.stock_symbol:
    stock_symbol = st.session_state.stock_symbol
else:
    st.warning(
        "No stock symbol selected. Please go to the main Finance Bro page and select a stock symbol first."
    )
    st.stop()

# Page header
st.markdown("# DuPont Analysis")
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

st.subheader(f"Financial Analysis for {company_name}")

# Beautiful DuPont Formula Display
st.markdown("---")
st.markdown("### 🧮 The DuPont Formula")

# Main formula in LaTeX
st.latex(r"""
\boxed{
\begin{aligned}
\text{ROE} &= \text{Net Profit Margin} \times \text{Asset Turnover} \times \text{Financial Leverage} \\[0.5em]
&= \frac{\text{Net Income}}{\text{Revenue}} \times \frac{\text{Revenue}}{\text{Average Total Assets}} \times \frac{\text{Average Total Assets}}{\text{Average Equity}} \\[0.5em]
&= \frac{\text{Net Income}}{\text{Average Equity}}
\end{aligned}
}
""")

# Component explanations in a beautiful layout
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
    <div style="background-color: #76706C; padding: 15px; border-radius: 10px; text-align: center; margin: 10px 0;">
        <h4 style="color: white; margin: 0;">💰 Profitability</h4>
        <p style="color: white; margin: 5px 0; font-size: 14px;">Net Profit Margin</p>
        <p style="color: white; margin: 0; font-size: 12px;">How much profit per dollar of sales</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
    <div style="background-color: #56524D; padding: 15px; border-radius: 10px; text-align: center; margin: 10px 0;">
        <h4 style="color: white; margin: 0;">⚡ Efficiency</h4>
        <p style="color: white; margin: 5px 0; font-size: 14px;">Asset Turnover</p>
        <p style="color: white; margin: 0; font-size: 12px;">How effectively assets generate sales</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        """
    <div style="background-color: #2B2523; padding: 15px; border-radius: 10px; text-align: center; margin: 10px 0;">
        <h4 style="color: white; margin: 0;">📈 Leverage</h4>
        <p style="color: white; margin: 5px 0; font-size: 14px;">Financial Leverage</p>
        <p style="color: white; margin: 0; font-size: 12px;">How much debt finances assets</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

st.markdown("---")

# Check if financial data is available
if "dataframes" not in st.session_state:
    st.warning(
        "⚠️ No financial data loaded. Please go to the AI Chat Analysis page and click 'Analyze Stock' first."
    )
    st.stop()

# Add financial display options component (shared for both tabs)
display_unit = render_financial_display_options(
    placement="sidebar",
    unique_key="dupont_display",
    title="💰 Display Format",
    help_text="Choose how financial values are displayed in metrics and tables",
)

# Create tabs for different analyses
tab1, tab2, tab3 = st.tabs(
    ["📊 DuPont Analysis", "💰 Capital Employed", "📈 Degree of Financial Leverage"]
)

with tab1:
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
        required_dfs = ["IncomeStatement", "BalanceSheet", "CashFlow"]
        missing_dfs = [df for df in required_dfs if df not in dataframes]

        if missing_dfs:
            st.error(
                f"❌ Missing required financial statements: {', '.join(missing_dfs)}"
            )
            st.info(
                "Please ensure all financial data is loaded in the AI Chat Analysis page."
            )
            st.stop()

        # Create DuPont analysis
        with st.spinner("🔄 Calculating DuPont Analysis..."):
            dupont_analysis = create_dupont_analysis(
                dataframes["IncomeStatement"],
                dataframes["BalanceSheet"],
                dataframes["CashFlow"],
            )

        if dupont_analysis is not None and not dupont_analysis.empty:
            # Store the dataframe in session state
            st.session_state.dupont_analysis = dupont_analysis

            st.success("✅ DuPont Analysis completed successfully!")

            # Display the DuPont analysis dataframe
            st.subheader("📈 DuPont Analysis Results")

            # Create columns for metrics summary
            if len(dupont_analysis) > 0:
                latest_year = dupont_analysis["yearReport"].max()
                latest_data = dupont_analysis[
                    dupont_analysis["yearReport"] == latest_year
                ].iloc[0]

                # Add additional metrics showing the financial values with display formatting
                col1, col2, col3, col4 = st.columns(4)
                col5, col6, col7, col8 = st.columns(4)

                with col1:
                    st.metric(
                        "Net Profit Margin",
                        f"{latest_data['Net Profit Margin']:.2f}%",
                        help="Net Income / Revenue",
                    )

                with col2:
                    st.metric(
                        "Asset Turnover",
                        f"{latest_data['Asset Turnover']:.2f}x",
                        help="Revenue / Average Total Assets",
                    )

                with col3:
                    st.metric(
                        "Financial Leverage",
                        f"{latest_data['Financial Leverage']:.2f}x",
                        help="Average Total Assets / Average Equity",
                    )

                with col4:
                    st.metric(
                        "ROE (DuPont)",
                        f"{latest_data['ROE (DuPont)']:.2f}%",
                        help="Net Profit Margin × Asset Turnover × Financial Leverage",
                    )

                # Second row with financial values in formatted display units
                with col5:
                    st.metric(
                        "Net Income",
                        format_financial_display(
                            latest_data["Net Income (Bn. VND)"], display_unit, 0
                        ),
                        help="Net profit after all expenses",
                    )

                with col6:
                    st.metric(
                        "Revenue",
                        format_financial_display(
                            latest_data["Revenue (Bn. VND)"], display_unit, 0
                        ),
                        help="Total sales revenue",
                    )

                with col7:
                    st.metric(
                        "Avg Total Assets",
                        format_financial_display(
                            latest_data["Average Total Assets (Bn. VND)"],
                            display_unit,
                            0,
                        ),
                        help="Average total assets over the period",
                    )

                with col8:
                    st.metric(
                        "Avg Equity",
                        format_financial_display(
                            latest_data["Average Equity (Bn. VND)"], display_unit, 0
                        ),
                        help="Average shareholders' equity",
                    )

            # Display the complete dataframe with formatting
            st.markdown("### 📊 Complete DuPont Analysis Table")

            # Create display copy with formatted financial columns
            financial_columns = [
                "Net Income (Bn. VND)",
                "Revenue (Bn. VND)",
                "Average Total Assets (Bn. VND)",
                "Average Equity (Bn. VND)",
            ]

            dupont_analysis_display = convert_dataframe_for_display(
                dupont_analysis, financial_columns, display_unit, decimal_places=1
            )

            # Configure column display (financial columns now contain formatted strings)
            column_config = {
                "ticker": st.column_config.TextColumn("Ticker", width="small"),
                "yearReport": st.column_config.NumberColumn("Year", width="small"),
                "Net Income (Bn. VND)": st.column_config.TextColumn(
                    "Net Income (Bn. VND)"
                ),
                "Revenue (Bn. VND)": st.column_config.TextColumn("Revenue (Bn. VND)"),
                "Average Total Assets (Bn. VND)": st.column_config.TextColumn(
                    "Avg. Total Assets (Bn. VND)"
                ),
                "Average Equity (Bn. VND)": st.column_config.TextColumn(
                    "Avg. Equity (Bn. VND)"
                ),
                "Net Profit Margin": st.column_config.NumberColumn(
                    "Net Profit Margin (%)", format="%.2f"
                ),
                "Asset Turnover": st.column_config.NumberColumn(
                    "Asset Turnover (x)", format="%.2f"
                ),
                "Financial Leverage": st.column_config.NumberColumn(
                    "Financial Leverage (x)", format="%.2f"
                ),
                "ROE (DuPont)": st.column_config.NumberColumn(
                    "ROE - DuPont (%)", format="%.2f"
                ),
                "ROE (Direct)": st.column_config.NumberColumn(
                    "ROE - Direct (%)", format="%.2f"
                ),
            }

            # Sort dataframe by year in descending order (most recent first)
            dupont_analysis_sorted = dupont_analysis_display.sort_values(
                "yearReport", ascending=False
            )

            # Display dataframe with enhanced formatting
            st.dataframe(
                dupont_analysis_sorted,
                use_container_width=True,
                column_config=column_config,
                hide_index=True,
            )

            # Altair chart for DuPont components trend
            if len(dupont_analysis) > 1:
                st.markdown("### 📈 DuPont Components Trend")

                # Prepare data for Altair chart
                chart_data = dupont_analysis.copy()

                # Create the multi-line chart
                base = alt.Chart(chart_data).add_selection(
                    alt.selection_interval(bind="scales")
                )

                # Net Profit Margin line
                margin_line = base.mark_line(color="#76706C", strokeWidth=3).encode(
                    x=alt.X("yearReport:O", title="Year", axis=alt.Axis(labelAngle=0)),
                    y=alt.Y(
                        "Net Profit Margin:Q",
                        title="Net Profit Margin (%)",
                        scale=alt.Scale(zero=False),
                    ),
                    tooltip=["yearReport:O", "Net Profit Margin:Q"],
                )

                # Asset Turnover line
                turnover_line = (
                    base.mark_line(color="#76706C", strokeWidth=3)
                    .encode(
                        x=alt.X("yearReport:O", title="Year"),
                        y=alt.Y(
                            "Asset Turnover:Q",
                            title="Asset Turnover (x)",
                            scale=alt.Scale(zero=False),
                        ),
                        tooltip=["yearReport:O", "Asset Turnover:Q"],
                    )
                    .resolve_scale(y="independent")
                )

                # Financial Leverage line
                leverage_line = (
                    base.mark_line(color="#76706C", strokeWidth=3)
                    .encode(
                        x=alt.X("yearReport:O", title="Year"),
                        y=alt.Y(
                            "Financial Leverage:Q",
                            title="Financial Leverage (x)",
                            scale=alt.Scale(zero=False),
                        ),
                        tooltip=["yearReport:O", "Financial Leverage:Q"],
                    )
                    .resolve_scale(y="independent")
                )

                # Combine charts using layering with separate y-axes
                combined_chart = alt.vconcat(
                    margin_line.properties(
                        title="Net Profit Margin (%)", width=600, height=150
                    ),
                    turnover_line.properties(
                        title="Asset Turnover (x)", width=600, height=150
                    ),
                    leverage_line.properties(
                        title="Financial Leverage (x)", width=600, height=150
                    ),
                ).resolve_scale(x="shared")

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
                use_container_width=True,
            )

            # Interpretation and insights
            st.markdown("### 🔍 Analysis Insights")

            if len(dupont_analysis) > 1:
                # Trend analysis for multiple years
                years_sorted = dupont_analysis.sort_values("yearReport")
                latest = years_sorted.iloc[-1]
                previous = years_sorted.iloc[-2]

                roe_change = latest["ROE (DuPont)"] - previous["ROE (DuPont)"]
                margin_change = (
                    latest["Net Profit Margin"] - previous["Net Profit Margin"]
                )
                turnover_change = latest["Asset Turnover"] - previous["Asset Turnover"]
                leverage_change = (
                    latest["Financial Leverage"] - previous["Financial Leverage"]
                )

                st.markdown(f"""
                **Year-over-Year Changes ({previous["yearReport"]:.0f} to {latest["yearReport"]:.0f}):**
                
                - **ROE Change**: {roe_change:+.2f}% {"📈" if roe_change > 0 else "📉" if roe_change < 0 else "➡️"}
                - **Net Profit Margin**: {margin_change:+.2f}% {"📈" if margin_change > 0 else "📉" if margin_change < 0 else "➡️"}
                - **Asset Turnover**: {turnover_change:+.2f}x {"📈" if turnover_change > 0 else "📉" if turnover_change < 0 else "➡️"}
                - **Financial Leverage**: {leverage_change:+.2f}x {"📈" if leverage_change > 0 else "📉" if leverage_change < 0 else "➡️"}
                """)

                # Identify main driver of ROE change
                drivers = []
                if abs(margin_change) > 0.5:
                    drivers.append(
                        f"Profitability ({'improved' if margin_change > 0 else 'declined'})"
                    )
                if abs(turnover_change) > 0.05:
                    drivers.append(
                        f"Asset efficiency ({'improved' if turnover_change > 0 else 'declined'})"
                    )
                if abs(leverage_change) > 0.1:
                    drivers.append(
                        f"Financial leverage ({'increased' if leverage_change > 0 else 'decreased'})"
                    )

                if drivers:
                    st.info(f"**Key ROE drivers**: {', '.join(drivers)}")

            # Performance benchmarks
            latest_roe = dupont_analysis["ROE (DuPont)"].iloc[-1]
            latest_margin = dupont_analysis["Net Profit Margin"].iloc[-1]
            latest_turnover = dupont_analysis["Asset Turnover"].iloc[-1]

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
            - **Asset Efficiency**: {"🟢 Efficient" if latest_turnover > 1 else "🟡 Moderate" if latest_turnover > 0.5 else "🔴 Low"} (Asset Turnover: {latest_turnover:.2f}x)
            """)

        else:
            st.error(
                "❌ Could not calculate DuPont analysis. Please check the financial data."
            )

    except Exception as e:
        st.error(f"❌ Error performing DuPont analysis: {str(e)}")
        st.info("Please ensure financial data is properly loaded and try again.")

with tab2:
    # Capital Employed Analysis
    st.markdown("### 🧮 Capital Employed Formula")

    # Display the Capital Employed formula
    st.latex(r"""
    \boxed{
    \text{Capital Employed} = \text{Long-term Borrowings} + \text{Short-term Borrowings} + \text{Owner's Equity}
    }
    """)

    # Information about Capital Employed Analysis
    with st.expander("ℹ️ About Capital Employed Analysis", expanded=False):
        st.markdown("""
        **Capital Employed** represents the total amount of funds invested in a business by both equity holders and debt holders.
        
        **Formula: Capital Employed = Long-term Borrowings + Short-term Borrowings + Owner's Equity**
        
        **Key Insights:**
        - **Total Investment**: Shows the total capital resources available to the company
        - **Financing Mix**: Reveals the proportion of debt vs equity financing
        - **Capital Efficiency**: Can be used to calculate return on capital employed (ROCE)
        - **Growth Tracking**: Monitor how capital requirements change over time
        
        **Vietnamese Context:**
        - Includes both short-term and long-term borrowings from Vietnamese financial institutions
        - Owner's equity reflects shareholders' investment in VND billions
        - Useful for comparing capital intensity across Vietnamese companies
        """)

    # Perform Capital Employed Analysis
    try:
        dataframes = st.session_state.dataframes

        # Check if BalanceSheet data exists
        if "BalanceSheet" not in dataframes:
            st.error("❌ Balance Sheet data not available")
            st.info(
                "Please ensure all financial data is loaded in the AI Chat Analysis page."
            )
        else:
            # Calculate capital employed
            with st.spinner("🔄 Calculating Capital Employed..."):
                capital_employed_results = calculate_capital_employed(
                    dataframes["BalanceSheet"]
                )

            if (
                capital_employed_results is not None
                and not capital_employed_results.empty
            ):
                # Store in session state
                st.session_state.capital_employed = capital_employed_results

                # Create display copy with formatted strings for table
                financial_columns = [
                    "Long-term borrowings (Bn. VND)",
                    "Short-term borrowings (Bn. VND)",
                    "OWNER'S EQUITY(Bn.VND)",
                    "Capital Employed (Bn. VND)",
                ]

                capital_employed_display = convert_dataframe_for_display(
                    capital_employed_results,
                    financial_columns,
                    display_unit,
                    decimal_places=1,
                )

                st.success("✅ Capital Employed analysis completed successfully!")

                # Display metrics summary
                st.subheader("💰 Capital Employed Summary")

                if len(capital_employed_results) > 0:
                    latest_year = capital_employed_results["yearReport"].max()
                    latest_data = capital_employed_results[
                        capital_employed_results["yearReport"] == latest_year
                    ].iloc[0]

                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.metric(
                            "Long-term Borrowings",
                            format_financial_display(
                                latest_data["Long-term borrowings (Bn. VND)"],
                                display_unit,
                                0,
                            ),
                            help="Long-term debt obligations",
                        )

                    with col2:
                        st.metric(
                            "Short-term Borrowings",
                            format_financial_display(
                                latest_data["Short-term borrowings (Bn. VND)"],
                                display_unit,
                                0,
                            ),
                            help="Short-term debt obligations",
                        )

                    with col3:
                        owner_equity_col = "OWNER'S EQUITY(Bn.VND)"
                        st.metric(
                            "Owner's Equity",
                            format_financial_display(
                                latest_data[owner_equity_col], display_unit, 0
                            ),
                            help="Shareholders' equity",
                        )

                    with col4:
                        st.metric(
                            "Total Capital Employed",
                            format_financial_display(
                                latest_data["Capital Employed (Bn. VND)"],
                                display_unit,
                                0,
                            ),
                            help="Total capital invested in the business",
                        )

                # Display complete table
                st.markdown("### 📊 Capital Employed Analysis Table")

                # Configure column display (for comma-formatted strings)
                column_config = {
                    "ticker": st.column_config.TextColumn("Ticker", width="small"),
                    "yearReport": st.column_config.NumberColumn("Year", width="small"),
                    "Long-term borrowings (Bn. VND)": st.column_config.TextColumn(
                        "Long-term Borrowings (Bn. VND)"
                    ),
                    "Short-term borrowings (Bn. VND)": st.column_config.TextColumn(
                        "Short-term Borrowings (Bn. VND)"
                    ),
                    "OWNER'S EQUITY(Bn.VND)": st.column_config.TextColumn(
                        "Owner's Equity (Bn. VND)"
                    ),
                    "Capital Employed (Bn. VND)": st.column_config.TextColumn(
                        "Capital Employed (Bn. VND)"
                    ),
                }

                # Sort by year in descending order (use display copy)
                capital_employed_sorted = capital_employed_display.sort_values(
                    "yearReport", ascending=False
                )

                st.dataframe(
                    capital_employed_sorted,
                    use_container_width=True,
                    column_config=column_config,
                    hide_index=True,
                )

                # Trend visualization
                if len(capital_employed_results) > 1:
                    st.markdown("### 📈 Capital Employed Trend")

                    # Create stacked area chart
                    chart_data = capital_employed_results.copy()

                    # Create individual trend lines
                    base = alt.Chart(chart_data)

                    # Capital Employed trend line
                    capital_line = (
                        base.mark_line(color="#76706C", strokeWidth=4)
                        .encode(
                            x=alt.X(
                                "yearReport:O",
                                title="Year",
                                axis=alt.Axis(labelAngle=0),
                            ),
                            y=alt.Y(
                                "Capital Employed (Bn. VND):Q",
                                title="Capital Employed (Bn. VND)",
                                scale=alt.Scale(zero=False),
                            ),
                            tooltip=["yearReport:O", "Capital Employed (Bn. VND):Q"],
                        )
                        .properties(
                            title="Total Capital Employed Over Time",
                            width=600,
                            height=300,
                        )
                    )

                    st.altair_chart(capital_line, use_container_width=True)

                    # Component breakdown chart
                    st.markdown("### 📊 Capital Components Breakdown")

                    # Prepare data for stacked chart
                    melted_data = chart_data.melt(
                        id_vars=["yearReport"],
                        value_vars=[
                            "Long-term borrowings (Bn. VND)",
                            "Short-term borrowings (Bn. VND)",
                            "OWNER'S EQUITY(Bn.VND)",
                        ],
                        var_name="Component",
                        value_name="Amount",
                    )

                    # Clean component names for display
                    melted_data["Component"] = melted_data["Component"].replace(
                        {
                            "Long-term borrowings (Bn. VND)": "Long-term Debt",
                            "Short-term borrowings (Bn. VND)": "Short-term Debt",
                            "OWNER'S EQUITY(Bn.VND)": "Owner's Equity",
                        }
                    )

                    # Create stacked bar chart
                    stacked_chart = (
                        alt.Chart(melted_data)
                        .mark_bar()
                        .encode(
                            x=alt.X("yearReport:O", title="Year"),
                            y=alt.Y("Amount:Q", title="Amount (Bn. VND)"),
                            color=alt.Color(
                                "Component:N",
                                scale=alt.Scale(
                                    range=["#2B2523", "#56524D", "#76706C"]
                                ),
                                title="Capital Components",
                            ),
                            tooltip=["yearReport:O", "Component:N", "Amount:Q"],
                        )
                        .properties(
                            title="Capital Employed Components by Year",
                            width=600,
                            height=300,
                        )
                    )

                    st.altair_chart(stacked_chart, use_container_width=True)

                # Download button
                csv_data = capital_employed_results.to_csv(index=False)
                st.download_button(
                    label="📥 Download Capital Employed Analysis as CSV",
                    data=csv_data,
                    file_name=f"capital_employed_{stock_symbol}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

                # Analysis insights
                st.markdown("### 🔍 Capital Employed Insights")

                if len(capital_employed_results) > 1:
                    # Year-over-year analysis
                    years_sorted = capital_employed_results.sort_values("yearReport")
                    latest = years_sorted.iloc[-1]
                    previous = years_sorted.iloc[-2]

                    capital_change = (
                        latest["Capital Employed (Bn. VND)"]
                        - previous["Capital Employed (Bn. VND)"]
                    )
                    change_pct = (
                        capital_change / previous["Capital Employed (Bn. VND)"]
                    ) * 100

                    debt_total_latest = (
                        latest["Long-term borrowings (Bn. VND)"]
                        + latest["Short-term borrowings (Bn. VND)"]
                    )
                    debt_ratio_latest = (
                        debt_total_latest / latest["Capital Employed (Bn. VND)"]
                    ) * 100
                    equity_ratio_latest = (
                        latest["OWNER'S EQUITY(Bn.VND)"]
                        / latest["Capital Employed (Bn. VND)"]
                    ) * 100

                    st.markdown(f"""
                    **Year-over-Year Analysis ({previous["yearReport"]:.0f} to {latest["yearReport"]:.0f}):**
                    
                    - **Capital Employed Change**: {capital_change:+.1f}B VND ({change_pct:+.1f}%) {"📈" if capital_change > 0 else "📉" if capital_change < 0 else "➡️"}
                    - **Current Financing Mix**:
                      - Debt Financing: {debt_ratio_latest:.1f}% ({debt_total_latest:.1f}B VND)
                      - Equity Financing: {equity_ratio_latest:.1f}% ({latest["OWNER'S EQUITY(Bn.VND)"]:.1f}B VND)
                    """)

                # Performance assessment
                st.markdown("### 📊 Capital Structure Assessment")

                latest_data = capital_employed_results.iloc[-1]
                total_debt = (
                    latest_data["Long-term borrowings (Bn. VND)"]
                    + latest_data["Short-term borrowings (Bn. VND)"]
                )
                debt_to_capital = (
                    total_debt / latest_data["Capital Employed (Bn. VND)"]
                ) * 100

                if debt_to_capital > 70:
                    capital_assessment = "🔴 High leverage (>70% debt)"
                elif debt_to_capital > 50:
                    capital_assessment = "🟠 Moderate leverage (50-70% debt)"
                elif debt_to_capital > 30:
                    capital_assessment = "🟡 Balanced structure (30-50% debt)"
                else:
                    capital_assessment = "🟢 Conservative structure (<30% debt)"

                st.markdown(f"""
                - **Capital Structure**: {capital_assessment}
                - **Debt-to-Capital Ratio**: {debt_to_capital:.1f}%
                - **Total Capital Scale**: {latest_data["Capital Employed (Bn. VND)"]:.1f}B VND
                """)

            else:
                st.error(
                    "❌ Could not calculate Capital Employed. Please check the balance sheet data."
                )

    except Exception as e:
        st.error(f"❌ Error performing Capital Employed analysis: {str(e)}")
        st.info("Please ensure financial data is properly loaded and try again.")

with tab3:
    # Degree of Financial Leverage Analysis
    st.markdown("### 🧮 Degree of Financial Leverage Formula")

    # Display the DFL formula
    st.latex(r"""
    \boxed{
    \text{DFL} = \frac{\% \text{ Change in Net Income}}{\% \text{ Change in EBIT}}
    }
    """)

    # Information about DFL Analysis
    with st.expander("ℹ️ About Degree of Financial Leverage Analysis", expanded=False):
        st.markdown("""
        **Degree of Financial Leverage (DFL)** measures how sensitive a company's net income is to changes in its operating income (EBIT).
        
        **Formula: DFL = % Change in Net Income / % Change in EBIT**
        
        **Key Insights:**
        - **Financial Risk Measurement**: Higher DFL indicates greater financial risk due to fixed financial costs (interest)
        - **Leverage Impact**: Shows how financial leverage amplifies the effect of operating income changes on net income
        - **Year-over-Year Analysis**: Compares percentage changes between consecutive years
        - **Risk Assessment**: Helps evaluate the company's financial structure and interest burden
        
        **Interpretation:**
        - **DFL > 1**: Financial leverage amplifies earnings changes (both positive and negative)
        - **DFL = 1**: No financial leverage effect (no interest expense)
        - **DFL < 1**: Financial leverage dampens earnings changes (unusual, may indicate extraordinary items)
        - **High DFL**: Greater financial risk but potential for higher returns to equity holders
        - **Low DFL**: Lower financial risk, more stable earnings
        """)

    # Perform DFL Analysis
    try:
        dataframes = st.session_state.dataframes

        # Check if IncomeStatement data exists
        if "IncomeStatement" not in dataframes:
            st.error("❌ Income Statement data not available")
            st.info(
                "Please ensure all financial data is loaded in the AI Chat Analysis page."
            )
        else:
            # Calculate DFL
            with st.spinner("🔄 Calculating Degree of Financial Leverage..."):
                dfl_results = calculate_degree_of_financial_leverage(
                    dataframes["IncomeStatement"]
                )

            if dfl_results is not None and not dfl_results.empty:
                # Store in session state
                st.session_state.dfl_analysis = dfl_results

                st.success(
                    "✅ Degree of Financial Leverage analysis completed successfully!"
                )

                # Display metrics summary
                st.subheader("📈 DFL Analysis Summary")

                # Filter out rows with NaN DFL values for summary
                valid_dfl_data = dfl_results.dropna(subset=["DFL"])

                if len(valid_dfl_data) > 0:
                    latest_year = valid_dfl_data["yearReport"].max()
                    latest_data = valid_dfl_data[
                        valid_dfl_data["yearReport"] == latest_year
                    ].iloc[0]

                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.metric(
                            "EBIT",
                            format_financial_display(
                                latest_data["EBIT (Bn. VND)"], display_unit, 0
                            ),
                            help="Earnings Before Interest and Taxes",
                        )

                    with col2:
                        st.metric(
                            "Net Income",
                            format_financial_display(
                                latest_data["Net Income (Bn. VND)"], display_unit, 0
                            ),
                            help="Net profit after all expenses including taxes and interest",
                        )

                    with col3:
                        ebit_change = latest_data["EBIT % Change"]
                        st.metric(
                            "EBIT % Change",
                            f"{ebit_change:.2f}%"
                            if not pd.isna(ebit_change)
                            else "N/A",
                            help="Year-over-year percentage change in EBIT",
                        )

                    with col4:
                        net_income_change = latest_data["Net Income % Change"]
                        st.metric(
                            "Net Income % Change",
                            f"{net_income_change:.2f}%"
                            if not pd.isna(net_income_change)
                            else "N/A",
                            help="Year-over-year percentage change in Net Income",
                        )

                    # Second row with DFL metric
                    col5, col6, col7, col8 = st.columns(4)

                    with col5:
                        dfl_value = latest_data["DFL"]
                        dfl_display = (
                            f"{dfl_value:.2f}" if not pd.isna(dfl_value) else "N/A"
                        )

                        # Add color coding for DFL assessment
                        if not pd.isna(dfl_value):
                            if dfl_value > 2:
                                dfl_status = "🔴 High Financial Risk"
                            elif dfl_value > 1.5:
                                dfl_status = "🟠 Moderate Financial Risk"
                            elif dfl_value > 1:
                                dfl_status = "🟡 Low Financial Risk"
                            else:
                                dfl_status = "🟢 Minimal Financial Risk"
                        else:
                            dfl_status = "N/A"

                        st.metric(
                            "Degree of Financial Leverage",
                            dfl_display,
                            help="DFL = % Change in Net Income / % Change in EBIT",
                        )
                        st.caption(dfl_status)

                # Display complete table with formatting
                st.markdown("### 📊 Degree of Financial Leverage Analysis Table")

                # Create display copy with formatted financial columns
                financial_columns = ["EBIT (Bn. VND)", "Net Income (Bn. VND)"]

                dfl_results_display = convert_dataframe_for_display(
                    dfl_results, financial_columns, display_unit, decimal_places=1
                )

                # Configure column display
                column_config = {
                    "ticker": st.column_config.TextColumn("Ticker", width="small"),
                    "yearReport": st.column_config.NumberColumn("Year", width="small"),
                    "EBIT (Bn. VND)": st.column_config.TextColumn("EBIT (Bn. VND)"),
                    "Net Income (Bn. VND)": st.column_config.TextColumn(
                        "Net Income (Bn. VND)"
                    ),
                    "EBIT % Change": st.column_config.NumberColumn(
                        "EBIT % Change", format="%.2f"
                    ),
                    "Net Income % Change": st.column_config.NumberColumn(
                        "Net Income % Change", format="%.2f"
                    ),
                    "DFL": st.column_config.NumberColumn("DFL", format="%.2f"),
                }

                # Sort by year in descending order (use display copy)
                dfl_results_sorted = dfl_results_display.sort_values(
                    "yearReport", ascending=False
                )

                st.dataframe(
                    dfl_results_sorted,
                    use_container_width=True,
                    column_config=column_config,
                    hide_index=True,
                )

                # Trend visualization
                if len(valid_dfl_data) > 1:
                    st.markdown("### 📈 DFL Trend Analysis")

                    # Create trend charts
                    chart_data = valid_dfl_data.copy()

                    # DFL trend line
                    base = alt.Chart(chart_data)

                    dfl_line = (
                        base.mark_line(color="#76706C", strokeWidth=4)
                        .encode(
                            x=alt.X(
                                "yearReport:O",
                                title="Year",
                                axis=alt.Axis(labelAngle=0),
                            ),
                            y=alt.Y(
                                "DFL:Q",
                                title="Degree of Financial Leverage",
                                scale=alt.Scale(zero=False),
                            ),
                            tooltip=["yearReport:O", "DFL:Q"],
                        )
                        .properties(
                            title="Degree of Financial Leverage Over Time",
                            width=600,
                            height=300,
                        )
                    )

                    st.altair_chart(dfl_line, use_container_width=True)

                    # Percentage changes comparison chart
                    st.markdown("### 📊 EBIT vs Net Income Changes Comparison")

                    # Prepare data for comparison chart
                    comparison_data = chart_data.melt(
                        id_vars=["yearReport"],
                        value_vars=["EBIT % Change", "Net Income % Change"],
                        var_name="Metric",
                        value_name="Percentage Change",
                    )

                    comparison_chart = (
                        alt.Chart(comparison_data)
                        .mark_bar()
                        .encode(
                            x=alt.X("yearReport:O", title="Year"),
                            y=alt.Y(
                                "Percentage Change:Q", title="Percentage Change (%)"
                            ),
                            color=alt.Color(
                                "Metric:N",
                                scale=alt.Scale(range=["#56524D", "#76706C"]),
                                title="Financial Metrics",
                            ),
                            tooltip=["yearReport:O", "Metric:N", "Percentage Change:Q"],
                        )
                        .properties(
                            title="EBIT vs Net Income Percentage Changes",
                            width=600,
                            height=300,
                        )
                    )

                    st.altair_chart(comparison_chart, use_container_width=True)

                # Download button
                csv_data = dfl_results.to_csv(index=False)
                st.download_button(
                    label="📥 Download DFL Analysis as CSV",
                    data=csv_data,
                    file_name=f"dfl_analysis_{stock_symbol}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

                # Analysis insights
                st.markdown("### 🔍 DFL Analysis Insights")

                if len(valid_dfl_data) > 1:
                    # Year-over-year analysis
                    years_sorted = valid_dfl_data.sort_values("yearReport")
                    latest = years_sorted.iloc[-1]
                    previous = years_sorted.iloc[-2]

                    dfl_change = (
                        latest["DFL"] - previous["DFL"]
                        if not pd.isna(latest["DFL"]) and not pd.isna(previous["DFL"])
                        else None
                    )
                    ebit_volatility = valid_dfl_data["EBIT % Change"].std()
                    net_income_volatility = valid_dfl_data["Net Income % Change"].std()

                    st.markdown(f"""
                    **Year-over-Year Analysis ({previous["yearReport"]:.0f} to {latest["yearReport"]:.0f}):**
                    
                    - **DFL Change**: {f"{dfl_change:+.2f}" if dfl_change is not None else "N/A"} {"📈" if dfl_change and dfl_change > 0 else "📉" if dfl_change and dfl_change < 0 else "➡️" if dfl_change == 0 else ""}
                    - **EBIT Volatility**: {ebit_volatility:.2f}% (Standard Deviation)
                    - **Net Income Volatility**: {net_income_volatility:.2f}% (Standard Deviation)
                    """)

                    # Risk assessment
                    avg_dfl = valid_dfl_data["DFL"].mean()
                    if avg_dfl > 2:
                        risk_assessment = "🔴 High Financial Risk - Company has significant financial leverage"
                        risk_recommendation = (
                            "Consider reducing debt levels to lower financial risk"
                        )
                    elif avg_dfl > 1.5:
                        risk_assessment = (
                            "🟠 Moderate Financial Risk - Balanced financial leverage"
                        )
                        risk_recommendation = (
                            "Monitor interest coverage and debt levels carefully"
                        )
                    elif avg_dfl > 1:
                        risk_assessment = (
                            "🟡 Low Financial Risk - Conservative financial leverage"
                        )
                        risk_recommendation = (
                            "Opportunity to use more leverage for growth if needed"
                        )
                    else:
                        risk_assessment = (
                            "🟢 Minimal Financial Risk - Very low financial leverage"
                        )
                        risk_recommendation = (
                            "Company has room to take on debt for expansion"
                        )

                    st.markdown("### 📊 Financial Risk Assessment")
                    st.markdown(f"""
                    - **Average DFL**: {avg_dfl:.2f}
                    - **Risk Level**: {risk_assessment}
                    - **Recommendation**: {risk_recommendation}
                    """)

                    # Leverage interpretation
                    st.markdown("### 💡 DFL Interpretation Guide")
                    st.markdown("""
                    **Understanding Your DFL Values:**
                    - **DFL > 2.0**: High financial leverage - earnings are very sensitive to EBIT changes
                    - **DFL 1.5-2.0**: Moderate leverage - reasonable balance between risk and return
                    - **DFL 1.0-1.5**: Low leverage - conservative financial structure
                    - **DFL < 1.0**: Minimal leverage - very stable but potentially missing growth opportunities
                    
                    **Key Takeaways:**
                    - Higher DFL means more financial risk but potentially higher returns for shareholders
                    - Lower DFL indicates more stable earnings and lower financial risk
                    - DFL varies with business cycles - monitor trends over time
                    """)

            else:
                st.error(
                    "❌ Could not calculate Degree of Financial Leverage. Please check the income statement data."
                )

    except Exception as e:
        st.error(f"❌ Error performing DFL analysis: {str(e)}")
        st.info("Please ensure financial data is properly loaded and try again.")

# Footer
st.markdown("---")
st.markdown("""
**About DuPont Analysis**: This analysis provides insights into the key drivers of return on equity by decomposing 
ROE into profitability, efficiency, and leverage components. Use this to understand what drives your company's 
financial performance and compare with industry benchmarks.
""")
