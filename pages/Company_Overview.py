import warnings

import altair as alt
import pandas as pd
import streamlit as st

# Import from modular utilities - preserves ALL caching and session state
from src.services.vnstock_api import (
    get_company_reports,
    get_foreign_trading_data,
    get_insider_deals_data,
    get_management_data,
    get_ownership_data,
    get_subsidiaries_data,
)


warnings.filterwarnings("ignore")


# Set page configuration
st.set_page_config(page_title="Company Profile Analysis", layout="wide")


# CSS loading removed

# Get stock symbol from session state (set in main app)
# If not available, show message to use main app first
if "stock_symbol" in st.session_state and st.session_state.stock_symbol:
    stock_symbol = st.session_state.stock_symbol
else:
    st.warning(
        "⚠️ No stock symbol selected. Please go to the main Finance Bro page and select a stock symbol first."
    )
    st.stop()

# Get company full name from cached symbols DataFrame
company_name = stock_symbol  # Default fallback
if "symbols_df" in st.session_state and st.session_state.symbols_df is not None:
    try:
        symbols_df = st.session_state.symbols_df
        matching_company = symbols_df[symbols_df["symbol"] == stock_symbol]
        if not matching_company.empty and "organ_name" in symbols_df.columns:
            company_name = matching_company["organ_name"].iloc[0]
    except Exception:
        # Keep using stock_symbol as fallback if anything fails
        pass
else:
    # If symbols not cached, user should visit any analysis page first for optimal experience
    st.info(
        "💡 For best experience with company names, visit the Stock Analysis page first to load stock symbols."
    )

# Title and description
st.title("Company Profile Analysis")
st.markdown("Analyze company ownership structure and management information")

if stock_symbol:
    try:
        # Get cached ownership data
        ownership_percentage = get_ownership_data(stock_symbol)

        if not ownership_percentage.empty:
            # Display ownership chart and metrics at the top
            st.header(f"{company_name} ({stock_symbol}) - Ownership Structure")

            # Create two columns for chart and summary
            col_chart, col_summary = st.columns([3, 1])

            with col_chart:
                # Sort by quantity for better visualization and convert percentage
                ownership_sorted = ownership_percentage.sort_values(
                    "quantity", ascending=True
                ).copy()
                ownership_sorted["share_own_percent"] = (
                    ownership_sorted["share_own_percent"] * 100
                )

                # Create base chart with quantity as x-axis
                base = alt.Chart(ownership_sorted).encode(
                    y=alt.Y("share_holder:N", title="Shareholder", sort="-x"),
                    x=alt.X("quantity:Q", title="Number of Shares"),
                )

                # Create bar chart
                bars = base.mark_bar(color="#56524D").encode(
                    tooltip=[
                        alt.Tooltip("share_holder:N", title="Shareholder"),
                        alt.Tooltip("quantity:Q", title="Shares", format=",.0f"),
                        alt.Tooltip(
                            "share_own_percent:Q", title="Ownership %", format=".1f"
                        ),
                    ]
                )

                # Create chart without text labels
                final_chart = (
                    bars.properties(
                        title=f"Ownership by Share Quantity - {company_name}",
                        width=600,
                        height=400,
                    )
                    .configure_axis(labelFontSize=10, titleFontSize=12)
                    .configure_title(fontSize=14, fontWeight="bold")
                )

                # Display the chart
                st.altair_chart(final_chart, use_container_width=True)

            with col_summary:
                st.subheader("Summary")
                st.metric("Total Shareholders", len(ownership_percentage))
                st.metric(
                    "Largest Shareholder",
                    f"{(ownership_percentage["share_own_percent"].max() * 100):.1f}%",
                )
                st.metric(
                    "Top 3 Combined",
                    f"{(ownership_percentage["share_own_percent"].nlargest(3).sum() * 100):.1f}%",
                )

                # Display raw data in expander
                with st.expander("View Raw Data"):
                    st.dataframe(ownership_percentage, width="stretch")

        else:
            st.info("No ownership data available for this symbol.")

        # Create tabs for additional information
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "Management Team",
            "Subsidiaries",
            "Insider Deals",
            "Foreign Transaction",
            "News",
            "Full Details",
        ])

        with tab1:
            st.header("Company Management")
            try:
                # Get cached management data
                management_team = get_management_data(stock_symbol)

                if not management_team.empty:
                    # Create management team ownership chart
                    st.subheader("Management Team Ownership")

                    # Filter for officers with quantity data
                    mgmt_with_shares = management_team[
                        management_team["quantity"].notna()
                        & management_team["officer_own_percent"].notna()
                        & (management_team["quantity"] > 0)
                    ].copy()

                    if not mgmt_with_shares.empty:
                        # Sort by quantity for better visualization and convert percentage
                        mgmt_sorted = mgmt_with_shares.sort_values(
                            "quantity", ascending=True
                        ).copy()
                        mgmt_sorted["officer_own_percent"] = (
                            mgmt_sorted["officer_own_percent"] * 100
                        )

                        # Create base chart
                        mgmt_base = alt.Chart(mgmt_sorted).encode(
                            y=alt.Y("officer_name:N", title="Officer Name", sort="-x"),
                            x=alt.X("quantity:Q", title="Number of Shares"),
                        )

                        # Create bars
                        mgmt_bars = mgmt_base.mark_bar(color="#56524D").encode(
                            tooltip=[
                                alt.Tooltip("officer_name:N", title="Officer"),
                                alt.Tooltip("position_short_name:N", title="Position"),
                                alt.Tooltip(
                                    "quantity:Q", title="Shares", format=",.0f"
                                ),
                                alt.Tooltip(
                                    "officer_own_percent:Q",
                                    title="Ownership %",
                                    format=".2f",
                                ),
                            ]
                        )

                        # Create text labels
                        mgmt_text = mgmt_base.mark_text(
                            align="left",
                            baseline="middle",
                            dx=3,
                            fontSize=9,
                            color="black",
                        ).encode(
                            x=alt.X("quantity:Q"),
                            text=alt.Text("officer_own_percent:Q", format=".2f"),
                        )

                        # Combine chart
                        mgmt_chart = (
                            (mgmt_bars + mgmt_text)
                            .properties(
                                title=f"Management Team Share Ownership - {company_name}",
                                width=600,
                                height=300,
                            )
                            .configure_axis(labelFontSize=9, titleFontSize=11)
                            .configure_title(fontSize=13, fontWeight="bold")
                        )

                        st.altair_chart(mgmt_chart, use_container_width=True)
                    else:
                        st.info("No management share ownership data available.")

                    st.dataframe(management_team, width="stretch")

                else:
                    st.info("No management information available for this symbol.")

            except Exception as e:
                st.error(f"Error loading management data: {str(e)}")

        with tab2:
            st.header("Company Subsidiaries")
            try:
                # Get cached subsidiaries data
                subsidiaries = get_subsidiaries_data(stock_symbol)

                if not subsidiaries.empty:
                    # Create ownership percentage visualization
                    st.subheader("Subsidiaries Ownership Distribution")

                    # Filter out subsidiaries with valid ownership data and convert to percentage
                    subs_with_ownership = subsidiaries[
                        subsidiaries["ownership_percent"].notna()
                        & (subsidiaries["ownership_percent"] > 0)
                    ].copy()
                    subs_with_ownership["ownership_percent"] = (
                        subs_with_ownership["ownership_percent"] * 100
                    )

                    if not subs_with_ownership.empty:
                        # Sort by ownership percentage for better visualization
                        subs_sorted = subs_with_ownership.sort_values(
                            "ownership_percent", ascending=True
                        )

                        # Create base chart
                        subs_base = alt.Chart(subs_sorted).encode(
                            y=alt.Y("organ_name:N", title="Subsidiary Name", sort="-x"),
                            x=alt.X(
                                "ownership_percent:Q", title="Ownership Percentage (%)"
                            ),
                        )

                        # Create bars
                        subs_bars = subs_base.mark_bar(color="#56524D").encode(
                            tooltip=[
                                alt.Tooltip("organ_name:N", title="Subsidiary"),
                                alt.Tooltip(
                                    "ownership_percent:Q",
                                    title="Ownership %",
                                    format=".1f",
                                ),
                                alt.Tooltip("type:N", title="Type"),
                            ]
                        )

                        # Create chart without text labels
                        subs_chart = (
                            subs_bars.properties(
                                title=f"Subsidiaries Ownership Percentage - {company_name}",
                                width=600,
                                height=max(300, len(subs_sorted) * 25),
                            )
                            .configure_axis(labelFontSize=10, titleFontSize=12)
                            .configure_title(fontSize=14, fontWeight="bold")
                        )

                        st.altair_chart(subs_chart, use_container_width=True)

                        # Summary metrics
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total Subsidiaries", len(subsidiaries))
                        with col2:
                            st.metric("With Ownership Data", len(subs_with_ownership))
                        with col3:
                            avg_ownership = subs_with_ownership[
                                "ownership_percent"
                            ].mean()
                            st.metric("Average Ownership", f"{avg_ownership:.1f}%")
                    else:
                        st.info(
                            "No subsidiaries with ownership percentage data available."
                        )

                    # Display subsidiaries table
                    st.subheader("Subsidiaries Overview")
                    # Convert ownership_percent to percentage for display
                    display_subs = subsidiaries[
                        ["organ_name", "ownership_percent", "type"]
                    ].copy()
                    display_subs["ownership_percent"] = (
                        display_subs["ownership_percent"] * 100
                    )
                    st.dataframe(display_subs, width="stretch")

                else:
                    st.info("No subsidiaries information available for this symbol.")

            except Exception as e:
                st.error(f"Error loading subsidiaries data: {str(e)}")

        with tab3:
            st.header("Insider Deals")
            try:
                # Get cached insider deals data
                insider_deals = get_insider_deals_data(stock_symbol)

                if not insider_deals.empty:
                    # Create timeline visualization
                    st.subheader("Insider Deals Timeline")

                    # Prepare data for visualization
                    deals_viz = insider_deals.copy()
                    deals_viz["deal_value"] = (
                        deals_viz["deal_quantity"] * deals_viz["deal_price"]
                    )

                    # Create scatter plot showing deals over time
                    scatter_chart = (
                        alt.Chart(deals_viz)
                        .mark_circle(size=100)
                        .encode(
                            x=alt.X("deal_announce_date:T", title="Deal Announce Date"),
                            y=alt.Y("deal_quantity:Q", title="Deal Quantity"),
                            color=alt.Color(
                                "deal_action:N",
                                title="Action",
                                scale=alt.Scale(range=["#d62728", "#2ca02c"]),
                            ),
                            size=alt.Size(
                                "deal_value:Q",
                                title="Deal Value",
                                scale=alt.Scale(range=[100, 400]),
                            ),
                            tooltip=[
                                alt.Tooltip("deal_announce_date:T", title="Date"),
                                alt.Tooltip("deal_action:N", title="Action"),
                                alt.Tooltip("deal_method:N", title="Method"),
                                alt.Tooltip(
                                    "deal_quantity:Q", title="Quantity", format=",.0f"
                                ),
                                alt.Tooltip(
                                    "deal_price:Q", title="Price", format=",.0f"
                                ),
                                alt.Tooltip(
                                    "deal_value:Q", title="Deal Value", format=",.0f"
                                ),
                                alt.Tooltip(
                                    "deal_ratio:Q", title="Deal Ratio", format=".2f"
                                ),
                            ],
                        )
                        .properties(
                            title=f"Insider Deals Timeline - {company_name}",
                            width=700,
                            height=400,
                        )
                        .configure_axis(labelFontSize=10, titleFontSize=12)
                        .configure_title(fontSize=14, fontWeight="bold")
                        .interactive()
                    )

                    st.altair_chart(scatter_chart, use_container_width=True)

                    # Summary metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Deals", len(insider_deals))
                    with col2:
                        buy_deals = len(
                            insider_deals[insider_deals["deal_action"] == "Mua"]
                        )
                        st.metric("Buy Deals", buy_deals)
                    with col3:
                        sell_deals = len(
                            insider_deals[insider_deals["deal_action"] == "Bán"]
                        )
                        st.metric("Sell Deals", sell_deals)

                    # Display insider deals table
                    st.subheader("Recent Insider Transactions")
                    st.dataframe(insider_deals, width="stretch")

                else:
                    st.info("No insider deals information available for this symbol.")

            except Exception as e:
                st.error(f"Error loading insider deals data: {str(e)}")

        with tab4:
            st.header("Foreign Transaction Analysis")
            try:
                # Get cached foreign trading data
                foreign_trading = get_foreign_trading_data(stock_symbol)

                if not foreign_trading.empty:
                    # Display EV metric
                    st.subheader("Enterprise Value")
                    if "ev" in foreign_trading.columns:
                        ev_value = (
                            foreign_trading["ev"].iloc[0]
                            if len(foreign_trading) > 0
                            else 0
                        )
                        st.metric("Enterprise Value", f"{ev_value:,.0f}")

                    # Create visualization for foreign holding rooms
                    st.subheader("Foreign Holding Room Analysis")

                    room_data = []
                    for col in [
                        "foreign_room",
                        "foreign_holding_room",
                        "current_holding_room",
                        "max_holding_room",
                    ]:
                        if col in foreign_trading.columns:
                            room_data.append({
                                "Room Type": col.replace("_", " ").title(),
                                "Value": foreign_trading[col].iloc[0],
                            })

                    if room_data:
                        room_df = pd.DataFrame(room_data)

                        # Create horizontal bar chart for room comparison
                        room_chart = (
                            alt.Chart(room_df)
                            .mark_bar(color="orange")
                            .encode(
                                y=alt.Y("Room Type:N", title="Room Type", sort="-x"),
                                x=alt.X("Value:Q", title="Room Value"),
                                tooltip=[
                                    alt.Tooltip("Room Type:N", title="Room Type"),
                                    alt.Tooltip(
                                        "Value:Q", title="Value", format=",.0f"
                                    ),
                                ],
                            )
                            .properties(
                                title=f"Foreign Holding Room Analysis - {company_name}",
                                width=600,
                                height=300,
                            )
                            .configure_axis(labelFontSize=10, titleFontSize=12)
                            .configure_title(fontSize=14, fontWeight="bold")
                        )

                        st.altair_chart(room_chart, use_container_width=True)

                    # Summary metrics
                    col1, col2, col3, col4, col5 = st.columns(5)
                    with col1:
                        if "foreign_volume" in foreign_trading.columns:
                            foreign_vol = foreign_trading["foreign_volume"].iloc[0]
                            st.metric("Foreign Volume", f"{foreign_vol:,.0f}")
                    with col2:
                        if "total_volume" in foreign_trading.columns:
                            total_vol = foreign_trading["total_volume"].iloc[0]
                            st.metric("Total Volume", f"{total_vol:,.0f}")
                    with col3:
                        if "foreign_room" in foreign_trading.columns:
                            foreign_room = foreign_trading["foreign_room"].iloc[0]
                            st.metric("Foreign Room", f"{foreign_room:,.0f}")
                    with col4:
                        if "current_holding_ratio" in foreign_trading.columns:
                            holding_ratio = foreign_trading[
                                "current_holding_ratio"
                            ].iloc[0]
                            st.metric("Current Holding Ratio", f"{holding_ratio:.2%}")
                    with col5:
                        if "max_holding_ratio" in foreign_trading.columns:
                            max_holding_ratio = foreign_trading[
                                "max_holding_ratio"
                            ].iloc[0]
                            st.metric("Max Holding Ratio", f"{max_holding_ratio:.2%}")

                    # Display complete foreign trading data
                    st.subheader("Complete Foreign Trading Data")
                    st.dataframe(foreign_trading, width="stretch")

                else:
                    st.info("No foreign trading information available for this symbol.")

            except Exception as e:
                st.error(f"Error loading foreign trading data: {str(e)}")

        with tab5:
            st.header("Company News & Reports")
            try:
                # Get cached company reports data
                company_reports = get_company_reports(stock_symbol)

                if not company_reports.empty:
                    # Display summary metrics
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.subheader("Latest Company News")
                    with col2:
                        st.metric("Total Reports", len(company_reports))

                    # Display each report
                    for _idx, report in company_reports.iterrows():
                        # Create container for each news item
                        with st.container():
                            # Title (description) in bold
                            st.markdown(f"**{report["description"]}**")

                            # Date formatting
                            if pd.notna(report["date"]):
                                formatted_date = report["date"].strftime("%B %d, %Y")
                                st.markdown(f"*{formatted_date}*")

                            # Article summary (name)
                            if pd.notna(report["name"]) and report["name"].strip():
                                st.markdown(f"{report["name"]}")

                            # Clickable link
                            if pd.notna(report["link"]) and report["link"].strip():
                                st.markdown(f"[🔗 Read Full Article]({report["link"]})")

                            # Add separator
                            st.markdown("---")

                else:
                    st.info("No news or reports available for this symbol.")

            except Exception as e:
                st.error(f"Error loading company reports: {str(e)}")

        with tab6:
            st.header("Detailed Information")
            if not ownership_percentage.empty:
                st.subheader("Complete Ownership Data")
                st.dataframe(ownership_percentage, width="stretch")

    except Exception as e:
        st.error(f"Error processing stock symbol '{stock_symbol}': {str(e)}")
        st.info("Please check if the stock symbol is correct and try again.")

else:
    st.info("Please enter a stock symbol to begin analysis.")

# Footer
st.markdown("---")
st.markdown("*Powered by Vnstock and Streamlit*")
