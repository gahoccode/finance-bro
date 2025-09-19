import streamlit as st
import pandas as pd
import altair as alt
import warnings
from vnstock import Listing
from src.services.vnstock_api import get_screener_data

warnings.filterwarnings("ignore")

# Title and header
st.markdown("# 🔍 Stock Screener")
st.markdown("Filter and analyze Vietnamese stocks based on various financial metrics")


# Load stock symbols and cache in session state if not already loaded (for consistent experience across app)
if "stock_symbols_list" not in st.session_state:
    try:
        with st.spinner("Loading stock symbols..."):
            symbols_df = Listing().all_symbols()
            st.session_state.stock_symbols_list = sorted(symbols_df["symbol"].tolist())
            st.session_state.symbols_df = symbols_df
    except Exception as e:
        st.warning(f"Could not load stock symbols from vnstock: {str(e)}")
        st.session_state.stock_symbols_list = [
            "REE",
            "VIC",
            "VNM",
            "VCB",
            "BID",
            "HPG",
            "FPT",
            "FMC",
            "DHC",
        ]
        st.session_state.symbols_df = None

# Industry list from reference
industry_list = [
    "Personal & Household Goods",
    "Chemicals",
    "Basic Resources",
    "Food & Beverage",
    "Financial Services",
    "Real Estate",
    "Industrial Goods & Services",
    "Banks",
    "Telecommunications",
    "Insurance",
    "Construction & Materials",
    "Media",
    "Retail",
    "Health Care",
    "Utilities",
    "Travel & Leisure",
    "Oil & Gas",
    "Technology",
    "Automobiles & Parts",
]

# Cache data to reduce API calls


def create_scatter_chart(df, x_col, y_col, title, y_scale=None):
    """Create scatter plot with Altair"""
    # Configure y-axis scale based on the column
    if y_col == "ev_ebitda" and y_scale is None:
        y_scale = alt.Scale(
            domain=[0, 30]
        )  # EV/EBITDA typically ranges 0-30, with most stocks 5-20
    elif y_scale is None:
        y_scale = alt.Scale()

    chart = (
        alt.Chart(df)
        .mark_circle(size=100, opacity=0.7)
        .add_selection(alt.selection_interval())
        .encode(
            x=alt.X(f"{x_col}:Q", title=x_col.replace("_", " ").title()),
            y=alt.Y(f"{y_col}:Q", title=y_col.replace("_", " ").title(), scale=y_scale),
            color=alt.Color("industry:N", legend=alt.Legend(title="Industry")),
            tooltip=[
                alt.Tooltip("ticker:N", title="Ticker"),
                alt.Tooltip("industry:N", title="Industry"),
                alt.Tooltip(
                    f"{x_col}:Q", title=x_col.replace("_", " ").title(), format=".2f"
                ),
                alt.Tooltip(
                    f"{y_col}:Q", title=y_col.replace("_", " ").title(), format=".2f"
                ),
                alt.Tooltip("market_cap:Q", title="Market Cap", format=".0f"),
            ],
        )
        .properties(width=600, height=400, title=title)
        .interactive()
    )

    return chart


def create_histogram(df, col, title):
    """Create histogram with Altair"""
    chart = (
        alt.Chart(df)
        .mark_bar(opacity=0.7)
        .encode(
            x=alt.X(
                f"{col}:Q",
                bin=alt.Bin(maxbins=20),
                title=col.replace("_", " ").title(),
                axis=alt.Axis(grid=False),
            ),
            y=alt.Y("count()", title="Count", axis=alt.Axis(grid=False)),
            color=alt.value("#AAA39F"),
        )
        .properties(width=400, height=300, title=title)
    )

    return chart


# Current stock symbol is available in sidebar for context - no need for notification

# Quick filter presets
st.subheader("⚡ Quick Filter Presets")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button(
        "🏦 High Quality Banks", help="Banks with ROE > 15%, Market Cap > 50B"
    ):
        # Clear all previous preset values
        for key in list(st.session_state.keys()):
            if key.startswith("preset_"):
                del st.session_state[key]
        # Set new preset values
        st.session_state.preset_industries = ["Banks"]
        st.session_state.preset_roe = True
        st.session_state.preset_market_cap = True
        st.session_state.auto_run_screener = True
        st.rerun()

with col2:
    if st.button(
        "🛡️ Low Risk Quality",
        help="High financial health > 7, Low beta < 1.2, High stock rating > 6",
    ):
        # Clear all previous preset values
        for key in list(st.session_state.keys()):
            if key.startswith("preset_"):
                del st.session_state[key]
        # Set new preset values
        st.session_state.preset_financial_health = True
        st.session_state.preset_beta = True
        st.session_state.preset_stock_rating = True
        st.session_state.auto_run_screener = True
        st.rerun()

with col3:
    if st.button("📈 Growth Stocks", help="All industries with ROE > 20%, ROA > 10%"):
        # Clear all previous preset values
        for key in list(st.session_state.keys()):
            if key.startswith("preset_"):
                del st.session_state[key]
        # Set new preset values
        st.session_state.preset_roe = True
        st.session_state.preset_roa = True
        st.session_state.auto_run_screener = True
        st.rerun()

with col4:
    if st.button("🔄 Clear All Filters", help="Reset all filters"):
        for key in list(st.session_state.keys()):
            if key.startswith("preset_"):
                del st.session_state[key]
        if "screener_data" in st.session_state:
            del st.session_state["screener_data"]
        st.rerun()

# Sidebar controls
st.sidebar.header("🎛️ Screening Filters")

# Fixed data source
source = "TCBS"  # Using TCBS as the only data source

# Industry filter
default_industries = st.session_state.get("preset_industries", [])
selected_industries = st.sidebar.multiselect(
    "Select Industries",
    industry_list,
    default=default_industries,
    help="Filter stocks by industry sectors",
)

# Exchange filter
exchanges = st.sidebar.multiselect(
    "Select Exchanges",
    ["HOSE", "HNX", "UPCOM"],
    default=["HOSE", "HNX", "UPCOM"],
    help="Filter by stock exchanges",
)

# Financial filters
st.sidebar.subheader("📊 Financial Filters")
st.sidebar.markdown("*Toggle filters on/off and adjust ranges as needed*")

# Market Cap filter
use_market_cap = st.sidebar.checkbox(
    "Enable Market Cap Filter",
    value=st.session_state.get("preset_market_cap", False),
    help="Enable to filter by market capitalization",
)
if use_market_cap:
    market_cap_range = st.sidebar.slider(
        "Market Cap (Billion VND)",
        min_value=0,
        max_value=1000000,
        value=(10000, 500000),
        step=10000,
        help="Filter by market capitalization",
    )
else:
    market_cap_range = None

# ROE filter
use_roe = st.sidebar.checkbox(
    "Enable ROE Filter",
    value=st.session_state.get("preset_roe", False),
    help="Enable to filter by Return on Equity",
)
if use_roe:
    default_roe = (
        (15.0, 50.0) if st.session_state.get("preset_roe", False) else (5.0, 50.0)
    )
    roe_range = st.sidebar.slider(
        "ROE (%)",
        min_value=-50.0,
        max_value=100.0,
        value=default_roe,
        step=1.0,
        help="Filter by Return on Equity",
    )
else:
    roe_range = None

# ROA filter
use_roa = st.sidebar.checkbox(
    "Enable ROA Filter",
    value=st.session_state.get("preset_roa", False),
    help="Enable to filter by Return on Assets",
)
if use_roa:
    default_roa = (
        (10.0, 30.0) if st.session_state.get("preset_roa", False) else (1.0, 30.0)
    )
    roa_range = st.sidebar.slider(
        "ROA (%)",
        min_value=-20.0,
        max_value=50.0,
        value=default_roa,
        step=0.5,
        help="Filter by Return on Assets",
    )
else:
    roa_range = None

# Dividend Yield filter
use_dividend_yield = st.sidebar.checkbox(
    "Enable Dividend Yield Filter",
    value=st.session_state.get("preset_dividend", False),
    help="Enable to filter by dividend yield",
)
if use_dividend_yield:
    default_dividend = (
        (5.0, 15.0) if st.session_state.get("preset_dividend", False) else (0.0, 15.0)
    )
    dividend_yield_range = st.sidebar.slider(
        "Dividend Yield (%)",
        min_value=0.0,
        max_value=20.0,
        value=default_dividend,
        step=0.5,
        help="Filter by dividend yield",
    )
else:
    dividend_yield_range = None

# EV/EBITDA filter
use_ev_ebitda = st.sidebar.checkbox(
    "Enable EV/EBITDA Filter", value=False, help="Enable to filter by EV/EBITDA ratio"
)
if use_ev_ebitda:
    ev_ebitda_range = st.sidebar.slider(
        "EV/EBITDA",
        min_value=0.0,
        max_value=50.0,
        value=(0.0, 25.0),
        step=1.0,
        help="Filter by Enterprise Value to EBITDA ratio",
    )
else:
    ev_ebitda_range = None

# Beta filter
use_beta = st.sidebar.checkbox(
    "Enable Beta Filter",
    value=st.session_state.get("preset_beta", False),
    help="Enable to filter by stock's volatility relative to market",
)
if use_beta:
    default_beta = (
        (0.0, 1.2) if st.session_state.get("preset_beta", False) else (0.5, 2.0)
    )
    beta_range = st.sidebar.slider(
        "Beta",
        min_value=0.0,
        max_value=3.0,
        value=default_beta,
        step=0.1,
        help="Filter by market beta coefficient (1.0 = market average)",
    )
else:
    beta_range = None

# Alpha filter
use_alpha = st.sidebar.checkbox(
    "Enable Alpha Filter",
    value=False,
    help="Enable to filter by stock's performance vs market",
)
if use_alpha:
    alpha_range = st.sidebar.slider(
        "Alpha (%)",
        min_value=-50.0,
        max_value=50.0,
        value=(-10.0, 10.0),
        step=0.5,
        help="Filter by performance vs market (positive = outperforming)",
    )
else:
    alpha_range = None

# Financial Health filter
use_financial_health = st.sidebar.checkbox(
    "Enable Financial Health Filter",
    value=st.session_state.get("preset_financial_health", False),
    help="Enable to filter by overall financial health score",
)
if use_financial_health:
    default_health = (
        (7.0, 10.0)
        if st.session_state.get("preset_financial_health", False)
        else (5.0, 10.0)
    )
    financial_health_range = st.sidebar.slider(
        "Financial Health Score",
        min_value=0.0,
        max_value=10.0,
        value=default_health,
        step=0.1,
        help="Filter by overall financial health score",
    )
else:
    financial_health_range = None

# Business Model filter
use_business_model = st.sidebar.checkbox(
    "Enable Business Model Filter",
    value=False,
    help="Enable to filter by business model quality score",
)
if use_business_model:
    business_model_range = st.sidebar.slider(
        "Business Model Score",
        min_value=0.0,
        max_value=10.0,
        value=(5.0, 10.0),
        step=0.1,
        help="Filter by business model quality score",
    )
else:
    business_model_range = None

# Business Operation filter
use_business_operation = st.sidebar.checkbox(
    "Enable Business Operation Filter",
    value=False,
    help="Enable to filter by operational efficiency score",
)
if use_business_operation:
    business_operation_range = st.sidebar.slider(
        "Business Operation Score",
        min_value=0.0,
        max_value=10.0,
        value=(5.0, 10.0),
        step=0.1,
        help="Filter by operational efficiency score",
    )
else:
    business_operation_range = None

# Stock Rating filter
use_stock_rating = st.sidebar.checkbox(
    "Enable Stock Rating Filter",
    value=st.session_state.get("preset_stock_rating", False),
    help="Enable to filter by overall stock rating",
)
if use_stock_rating:
    default_rating = (
        (6.0, 10.0)
        if st.session_state.get("preset_stock_rating", False)
        else (5.0, 10.0)
    )
    stock_rating_range = st.sidebar.slider(
        "Stock Rating",
        min_value=0.0,
        max_value=10.0,
        value=default_rating,
        step=0.1,
        help="Filter by overall stock rating",
    )
else:
    stock_rating_range = None

# Show active filters summary
active_filters = []
if selected_industries:
    active_filters.append(f"Industries: {len(selected_industries)}")
if use_market_cap:
    active_filters.append("Market Cap")
if use_roe:
    active_filters.append("ROE")
if use_roa:
    active_filters.append("ROA")
if use_dividend_yield:
    active_filters.append("Dividend Yield")
if use_ev_ebitda:
    active_filters.append("EV/EBITDA")
if use_beta:
    active_filters.append("Beta")
if use_alpha:
    active_filters.append("Alpha")
if use_financial_health:
    active_filters.append("Financial Health")
if use_business_model:
    active_filters.append("Business Model")
if use_business_operation:
    active_filters.append("Business Operation")
if use_stock_rating:
    active_filters.append("Stock Rating")

# Active filters are visually indicated by enabled checkboxes - no need for additional notification


# Load data button or auto-run from preset
run_screener = st.sidebar.button(
    "🔍 Run Screener", type="primary"
) or st.session_state.get("auto_run_screener", False)

if run_screener:
    # Clear the auto-run flag
    if "auto_run_screener" in st.session_state:
        del st.session_state.auto_run_screener
    # Build parameters - only include enabled filters
    params = {"exchangeName": ",".join(exchanges)}

    # Add industry filter if selected
    if selected_industries:
        params["industryName"] = ",".join(selected_industries)

    # IMPORTANT: Based on vnstock documentation, the screener API only supports:
    # - exchangeName (exchanges)
    # - industryName (industries)
    # Financial filters will be applied POST-PROCESSING after getting all data

    # We'll store the financial filters for client-side filtering
    financial_filters = {}
    if use_market_cap and market_cap_range:
        financial_filters["market_cap"] = market_cap_range
    if use_roe and roe_range:
        financial_filters["roe"] = roe_range
    if use_roa and roa_range:
        financial_filters["roa"] = roa_range
    if use_dividend_yield and dividend_yield_range:
        financial_filters["dividend_yield"] = dividend_yield_range
    if use_ev_ebitda and ev_ebitda_range:
        financial_filters["ev_ebitda"] = ev_ebitda_range
    if use_beta and beta_range:
        financial_filters["beta"] = beta_range
    if use_alpha and alpha_range:
        financial_filters["alpha"] = alpha_range
    if use_financial_health and financial_health_range:
        financial_filters["financial_health"] = financial_health_range
    if use_business_model and business_model_range:
        financial_filters["business_model"] = business_model_range
    if use_business_operation and business_operation_range:
        financial_filters["business_operation"] = business_operation_range
    if use_stock_rating and stock_rating_range:
        financial_filters["stock_rating"] = stock_rating_range

    with st.spinner("Screening stocks..."):
        screener_data = get_screener_data(params, source=source)

    if not screener_data.empty:
        # Apply client-side financial filtering if any filters are enabled
        if financial_filters:
            filtered_data = screener_data.copy()
            original_count = len(filtered_data)

            # Track filtering progress for visualization
            filtering_steps = [
                {"Step": "Initial", "Count": original_count, "Filter": "Base data"}
            ]

            for column, (min_val, max_val) in financial_filters.items():
                if column in filtered_data.columns:
                    # Remove rows where the column value is outside the range or is NaN
                    before_count = len(filtered_data)
                    filtered_data = filtered_data[
                        (filtered_data[column].notna())
                        & (filtered_data[column] >= min_val)
                        & (filtered_data[column] <= max_val)
                    ]
                    after_count = len(filtered_data)

                    # Add step to tracking
                    filter_name = column.replace("_", " ").title()
                    filtering_steps.append(
                        {
                            "Step": f"After {filter_name}",
                            "Count": after_count,
                            "Filter": f"{filter_name} ({min_val}-{max_val})",
                        }
                    )
                else:
                    st.warning(
                        f"⚠️ Column '{column}' not found in data. Skipping this filter."
                    )

            # Create filtering visualization if we have multiple steps
            if len(filtering_steps) > 1:
                st.subheader("🔍 Filtering Breakdown")

                # Create DataFrame for visualization
                filter_df = pd.DataFrame(filtering_steps)

                # Create funnel chart showing stock count reduction
                funnel_chart = (
                    alt.Chart(filter_df)
                    .mark_bar(color="#AAA39F", opacity=0.8)
                    .encode(
                        x=alt.X("Count:Q", title="Number of Stocks"),
                        y=alt.Y("Step:N", title="Filtering Step", sort="-x"),
                        tooltip=[
                            alt.Tooltip("Step:N", title="Step"),
                            alt.Tooltip("Count:Q", title="Stock Count", format=",.0f"),
                            alt.Tooltip("Filter:N", title="Filter Applied"),
                        ],
                    )
                    .properties(
                        width=600,
                        height=min(400, len(filtering_steps) * 60),
                        title=f"Stock Filtering Process: {original_count} → {len(filtered_data)} stocks",
                    )
                )

                # Add text labels showing count
                text_chart = (
                    alt.Chart(filter_df)
                    .mark_text(
                        align="left",
                        baseline="middle",
                        dx=5,
                        fontSize=11,
                        fontWeight="bold",
                    )
                    .encode(
                        x=alt.X("Count:Q"),
                        y=alt.Y("Step:N", sort="-x"),
                        text=alt.Text("Count:Q", format=",.0f"),
                    )
                )

                # Combine charts
                combined_chart = (funnel_chart + text_chart).resolve_scale(
                    color="independent"
                )

                st.altair_chart(combined_chart, use_container_width=True)

                # Show reduction percentage
                reduction_pct = (
                    (original_count - len(filtered_data)) / original_count
                ) * 100
                st.caption(
                    f"📊 Filtering reduced dataset by {reduction_pct:.1f}% ({original_count - len(filtered_data):,} stocks removed)"
                )

            screener_data = filtered_data

        if not screener_data.empty:
            st.session_state["screener_data"] = screener_data
        else:
            st.warning(
                "No stocks found after applying financial filters. Try relaxing the filter ranges."
            )
    else:
        st.warning(
            "No stocks found from the API. Try adjusting the industry/exchange filters."
        )
        st.info("""
        **Troubleshooting Tips:**
        1. Try using the 'Test Basic API' button first to verify the connection
        2. Start with just Industry + Exchange filters (financial filters are applied after data retrieval)
        3. Try different industry combinations if no results are found
        """)

# Display results if data is available
if "screener_data" in st.session_state and not st.session_state["screener_data"].empty:
    df = st.session_state["screener_data"]

    # Display summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Stocks", len(df))
    with col2:
        if "beta" in df.columns and not df["beta"].isna().all():
            beta_min = df["beta"].min()
            beta_max = df["beta"].max()
            st.metric("Beta Range", f"{beta_min:.2f} - {beta_max:.2f}")
        else:
            avg_roe = df["roe"].mean() if "roe" in df.columns else 0
            st.metric("Avg ROE", f"{avg_roe:.1f}%")
    with col3:
        if "financial_health" in df.columns and not df["financial_health"].isna().all():
            health_min = df["financial_health"].min()
            health_max = df["financial_health"].max()
            st.metric("Health Range", f"{health_min:.1f} - {health_max:.1f}")
        else:
            avg_div_yield = (
                df["dividend_yield"].mean() if "dividend_yield" in df.columns else 0
            )
            st.metric("Avg Dividend Yield", f"{avg_div_yield:.1f}%")
    with col4:
        if "stock_rating" in df.columns and not df["stock_rating"].isna().all():
            rating_min = df["stock_rating"].min()
            rating_max = df["stock_rating"].max()
            st.metric("Rating Range", f"{rating_min:.1f} - {rating_max:.1f}")
        else:
            total_market_cap = (
                df["market_cap"].sum() if "market_cap" in df.columns else 0
            )
            st.metric("Total Market Cap", f"{total_market_cap / 1000:.0f}B VND")

    # Visualizations (moved above data table)
    st.subheader("📊 Visualizations")

    # Create tabs for different visualizations
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        [
            "ROE Analysis",
            "Market Cap vs Dividend Yield",
            "Value vs Quality",
            "Risk Analysis",
            "Quality Scores",
            "Distribution Charts",
        ]
    )

    with tab1:
        if "roe" in df.columns and "market_cap" in df.columns:
            # Filter out rows with missing ROE or market_cap data
            viz_df = df.dropna(subset=["roe", "market_cap"])
            if not viz_df.empty:
                chart = create_scatter_chart(
                    viz_df, "market_cap", "roe", "Market Cap vs ROE"
                )
                st.altair_chart(chart, use_container_width=True)
            else:
                st.info("No data available for ROE visualization")

    with tab2:
        if "market_cap" in df.columns and "dividend_yield" in df.columns:
            viz_df = df.dropna(subset=["market_cap", "dividend_yield"])
            if not viz_df.empty:
                chart = create_scatter_chart(
                    viz_df,
                    "market_cap",
                    "dividend_yield",
                    "Market Cap vs Dividend Yield",
                )
                st.altair_chart(chart, use_container_width=True)
            else:
                st.info("No data available for dividend yield visualization")

    with tab3:
        if "ev_ebitda" in df.columns and "roe" in df.columns:
            # Use ROE vs EV/EBITDA with hard-coded y-axis range
            viz_df = df.dropna(subset=["ev_ebitda", "roe"])
            if not viz_df.empty:
                chart = create_scatter_chart(
                    viz_df,
                    "roe",
                    "ev_ebitda",
                    "ROE vs EV/EBITDA (Quality vs Valuation)",
                )
                st.altair_chart(chart, use_container_width=True)
                st.caption(
                    "💡 **Sweet Spot**: High ROE (>15%) + Low EV/EBITDA (<12) = Quality stocks at reasonable valuations"
                )

                # Add reference lines explanation
                st.markdown("""
                **EV/EBITDA Guidelines:**
                - **< 8**: Potentially undervalued or distressed
                - **8-12**: Fair valuation range  
                - **12-18**: Premium valuation (justify with growth/quality)
                - **> 18**: Expensive (needs exceptional growth prospects)
                """)
            else:
                st.info("No stocks have both ROE and EV/EBITDA data available")
        else:
            st.info(
                "Value vs Quality analysis requires both ROE and EV/EBITDA data. These metrics may not be available in the current dataset."
            )

    with tab4:
        # Risk Analysis - Beta vs Alpha
        if "beta" in df.columns and "alpha" in df.columns:
            viz_df = df.dropna(subset=["beta", "alpha"])
            if not viz_df.empty:
                chart = create_scatter_chart(
                    viz_df, "beta", "alpha", "Risk Analysis: Beta vs Alpha"
                )
                st.altair_chart(chart, use_container_width=True)
                st.caption(
                    "💡 **Sweet Spot**: Low Beta (<1.0) + High Alpha (>0) = Low risk with market outperformance"
                )

                # Add reference guidelines
                st.markdown("""
                **Beta Guidelines:**
                - **< 0.8**: Defensive stocks (less volatile than market)
                - **0.8-1.2**: Market-like volatility
                - **> 1.2**: High volatility (amplified market moves)
                
                **Alpha Guidelines:**  
                - **Positive**: Outperforming the market
                - **Negative**: Underperforming the market
                """)
            else:
                st.info("No stocks have both Beta and Alpha data available")
        else:
            st.info(
                "Risk analysis requires both Beta and Alpha data. These metrics may not be available in the current dataset."
            )

    with tab5:
        # Quality Scores - Financial Health vs Business Model
        if "financial_health" in df.columns and "business_model" in df.columns:
            viz_df = df.dropna(subset=["financial_health", "business_model"])
            if not viz_df.empty:
                chart = create_scatter_chart(
                    viz_df,
                    "financial_health",
                    "business_model",
                    "Quality Scores: Financial Health vs Business Model",
                )
                st.altair_chart(chart, use_container_width=True)
                st.caption(
                    "💡 **Quality Leaders**: High Financial Health (>7) + High Business Model (>7) = Strong fundamentals"
                )

                # Add quality score guidelines
                st.markdown("""
                **Score Guidelines (0-10 scale):**
                - **8-10**: Excellent quality
                - **6-8**: Good quality  
                - **4-6**: Average quality
                - **< 4**: Below average quality
                """)
            else:
                st.info(
                    "No stocks have both Financial Health and Business Model scores available"
                )
        else:
            st.info(
                "Quality analysis requires both Financial Health and Business Model data. These metrics may not be available in the current dataset."
            )

    with tab6:
        # Distribution charts in a 2x3 grid
        col1, col2 = st.columns(2)

        with col1:
            if "roe" in df.columns:
                viz_df = df.dropna(subset=["roe"])
                if not viz_df.empty:
                    hist_chart = create_histogram(viz_df, "roe", "ROE Distribution")
                    st.altair_chart(hist_chart, use_container_width=True)

            if "beta" in df.columns:
                viz_df = df.dropna(subset=["beta"])
                if not viz_df.empty:
                    hist_chart = create_histogram(viz_df, "beta", "Beta Distribution")
                    st.altair_chart(hist_chart, use_container_width=True)

            if "financial_health" in df.columns:
                viz_df = df.dropna(subset=["financial_health"])
                if not viz_df.empty:
                    hist_chart = create_histogram(
                        viz_df, "financial_health", "Financial Health Distribution"
                    )
                    st.altair_chart(hist_chart, use_container_width=True)

        with col2:
            if "dividend_yield" in df.columns:
                viz_df = df.dropna(subset=["dividend_yield"])
                if not viz_df.empty:
                    hist_chart = create_histogram(
                        viz_df, "dividend_yield", "Dividend Yield Distribution"
                    )
                    st.altair_chart(hist_chart, use_container_width=True)

            if "alpha" in df.columns:
                viz_df = df.dropna(subset=["alpha"])
                if not viz_df.empty:
                    hist_chart = create_histogram(viz_df, "alpha", "Alpha Distribution")
                    st.altair_chart(hist_chart, use_container_width=True)

            if "stock_rating" in df.columns:
                viz_df = df.dropna(subset=["stock_rating"])
                if not viz_df.empty:
                    hist_chart = create_histogram(
                        viz_df, "stock_rating", "Stock Rating Distribution"
                    )
                    st.altair_chart(hist_chart, use_container_width=True)

    # Data table (moved below visualizations)
    st.subheader("📋 Screened Stocks")

    # Select columns to display
    display_columns = [
        "ticker",
        "exchange",
        "industry",
        "market_cap",
        "roe",
        "roa",
        "dividend_yield",
        "ev_ebitda",
        "pe",
        "pb",
        "beta",
        "alpha",
        "financial_health",
        "business_model",
        "business_operation",
        "stock_rating",
    ]
    available_columns = [col for col in display_columns if col in df.columns]

    # Format the dataframe for display
    display_df = df[available_columns].copy()

    # Format numeric columns
    numeric_cols = [
        "market_cap",
        "roe",
        "roa",
        "dividend_yield",
        "ev_ebitda",
        "pe",
        "pb",
        "beta",
        "alpha",
        "financial_health",
        "business_model",
        "business_operation",
        "stock_rating",
    ]
    for col in numeric_cols:
        if col in display_df.columns:
            if col == "market_cap":
                display_df[col] = display_df[col].apply(
                    lambda x: f"{x:,.0f}" if pd.notna(x) else "N/A"
                )
            elif col in ["beta", "alpha"]:
                # 3 decimal places for beta and alpha for precision
                display_df[col] = display_df[col].apply(
                    lambda x: f"{x:.3f}" if pd.notna(x) else "N/A"
                )
            elif col in [
                "financial_health",
                "business_model",
                "business_operation",
                "stock_rating",
            ]:
                # 1 decimal place for quality scores
                display_df[col] = display_df[col].apply(
                    lambda x: f"{x:.1f}" if pd.notna(x) else "N/A"
                )
            else:
                # 2 decimal places for other metrics
                display_df[col] = display_df[col].apply(
                    lambda x: f"{x:.2f}" if pd.notna(x) else "N/A"
                )

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    # Export functionality - Download PNG visualization
    st.subheader("📥 Export Visualization")

    def create_matplotlib_charts_for_download(data):
        """Create matplotlib charts for PNG download"""
        import matplotlib.pyplot as plt
        import numpy as np
        from datetime import datetime
        import io

        # Set up the figure with subplots
        fig_height = 12
        num_charts = 0

        # Count available charts
        if "roe" in data.columns and "market_cap" in data.columns:
            num_charts += 1
        if "market_cap" in data.columns and "dividend_yield" in data.columns:
            num_charts += 1
        if "ev_ebitda" in data.columns and "roe" in data.columns:
            num_charts += 1

        if num_charts == 0:
            return None, None

        fig, axes = plt.subplots(num_charts, 1, figsize=(12, fig_height))
        if num_charts == 1:
            axes = [axes]

        chart_idx = 0

        # ROE vs Market Cap
        if "roe" in data.columns and "market_cap" in data.columns:
            viz_df = data.dropna(subset=["roe", "market_cap"])
            if not viz_df.empty:
                ax = axes[chart_idx]

                # Create scatter plot with industry colors
                industries = (
                    viz_df["industry"].unique()
                    if "industry" in viz_df.columns
                    else ["Unknown"]
                )
                colors = plt.cm.Set3(np.linspace(0, 1, len(industries)))

                for i, industry in enumerate(industries):
                    if "industry" in viz_df.columns:
                        industry_data = viz_df[viz_df["industry"] == industry]
                    else:
                        industry_data = viz_df

                    ax.scatter(
                        industry_data["market_cap"],
                        industry_data["roe"],
                        alpha=0.7,
                        s=100,
                        c=[colors[i]],
                        label=industry,
                    )

                ax.set_xlabel("Market Cap", fontsize=12)
                ax.set_ylabel("ROE (%)", fontsize=12)
                ax.set_title("Market Cap vs ROE", fontsize=14, fontweight="bold")
                ax.grid(True, alpha=0.3)
                if len(industries) <= 10:  # Only show legend if not too many industries
                    ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")

                chart_idx += 1

        # Market Cap vs Dividend Yield
        if "market_cap" in data.columns and "dividend_yield" in data.columns:
            viz_df = data.dropna(subset=["market_cap", "dividend_yield"])
            if not viz_df.empty:
                ax = axes[chart_idx]

                industries = (
                    viz_df["industry"].unique()
                    if "industry" in viz_df.columns
                    else ["Unknown"]
                )
                colors = plt.cm.Set3(np.linspace(0, 1, len(industries)))

                for i, industry in enumerate(industries):
                    if "industry" in viz_df.columns:
                        industry_data = viz_df[viz_df["industry"] == industry]
                    else:
                        industry_data = viz_df

                    ax.scatter(
                        industry_data["market_cap"],
                        industry_data["dividend_yield"],
                        alpha=0.7,
                        s=100,
                        c=[colors[i]],
                        label=industry,
                    )

                ax.set_xlabel("Market Cap", fontsize=12)
                ax.set_ylabel("Dividend Yield (%)", fontsize=12)
                ax.set_title(
                    "Market Cap vs Dividend Yield", fontsize=14, fontweight="bold"
                )
                ax.grid(True, alpha=0.3)
                if len(industries) <= 10:
                    ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")

                chart_idx += 1

        # ROE vs EV/EBITDA (Value vs Quality)
        if "ev_ebitda" in data.columns and "roe" in data.columns:
            viz_df = data.dropna(subset=["ev_ebitda", "roe"])
            if not viz_df.empty:
                ax = axes[chart_idx]

                industries = (
                    viz_df["industry"].unique()
                    if "industry" in viz_df.columns
                    else ["Unknown"]
                )
                colors = plt.cm.Set3(np.linspace(0, 1, len(industries)))

                for i, industry in enumerate(industries):
                    if "industry" in viz_df.columns:
                        industry_data = viz_df[viz_df["industry"] == industry]
                    else:
                        industry_data = viz_df

                    ax.scatter(
                        industry_data["roe"],
                        industry_data["ev_ebitda"],
                        alpha=0.7,
                        s=100,
                        c=[colors[i]],
                        label=industry,
                    )

                ax.set_xlabel("ROE (%)", fontsize=12)
                ax.set_ylabel("EV/EBITDA", fontsize=12)
                ax.set_title(
                    "ROE vs EV/EBITDA (Quality vs Valuation)",
                    fontsize=14,
                    fontweight="bold",
                )
                ax.set_ylim(0, 30)  # Hard-coded range for EV/EBITDA
                ax.grid(True, alpha=0.3)
                if len(industries) <= 10:
                    ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")

                chart_idx += 1

        plt.tight_layout()

        # Save to bytes
        img_buffer = io.BytesIO()
        plt.savefig(
            img_buffer, format="png", dpi=300, bbox_inches="tight", facecolor="white"
        )
        img_buffer.seek(0)
        plt.close()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screener_visualization_{timestamp}.png"

        return img_buffer.getvalue(), filename

    # Create and offer PNG download
    try:
        png_data, filename = create_matplotlib_charts_for_download(df)

        if png_data:
            st.download_button(
                label="📊 Download Visualization as PNG",
                data=png_data,
                file_name=filename,
                mime="image/png",
                help="Downloads all visualizations as a PNG file",
            )
        else:
            st.warning("No visualizations available to download")

    except Exception as e:
        st.error(f"Error creating PNG download: {str(e)}")
        st.info("💡 **Alternative:** Take a screenshot of the visualizations above.")

else:
    # Initial state - show instructions
    st.info("""
    ### 📋 How to use the Stock Screener:
    
    1. **Select Industries**: Choose one or more industry sectors from the sidebar
    2. **Set Exchanges**: Select which Vietnamese stock exchanges to include
    3. **Configure Filters**: Toggle and adjust the financial metric filters:
       - Market Cap: Company size filter (applied after data retrieval)
       - ROE: Return on Equity (profitability)
       - ROA: Return on Assets (efficiency)
       - Dividend Yield: Dividend return percentage
       - EV/EBITDA: Valuation multiple
    4. **Run Screener**: Click the "Run Screener" button to find matching stocks
    5. **Analyze Results**: View the filtered stocks and interactive visualizations
    
    The screener uses TCBS data and applies financial filters after data retrieval.
    """)

    # Show sample metrics
    st.subheader("📊 Sample Visualization Preview")
    st.info(
        "Run the screener to see interactive charts comparing ROE, dividend yield, EV/EBITDA, and market cap across Vietnamese stocks."
    )
