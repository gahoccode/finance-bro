import streamlit as st
import pandas as pd
import altair as alt
import os
from datetime import datetime, timedelta

# Import from modular services
from src.services.vnstock_api import (
    get_fund_listing,
    get_fund_nav_report,
    get_fund_asset_allocation,
    get_fund_industry_allocation,
)
from src.services.chart_service import (
    create_fund_nav_line_chart,
    create_fund_comparison_bar_chart,
    create_fund_asset_pie_chart,
    create_fund_industry_pie_chart,
    generate_fund_charts_2x2_png,
)
from src.components.ui_components import inject_custom_success_styling

st.set_page_config(page_title="Fund Analysis", layout="wide")

# Apply custom CSS styling for success alerts
inject_custom_success_styling()

st.title("🏦 Vietnamese Fund Analysis")

# Main content
with st.container():
    st.header("Investment Fund Performance Analysis")
    st.write(
        "Comprehensive analysis of Vietnamese investment funds with NAV performance, asset allocation, and industry distribution."
    )

# Load fund data
with st.spinner("Loading fund data..."):
    fund_list = get_fund_listing()

if fund_list.empty:
    st.error("❌ Unable to load fund data. Please try again later.")
    st.stop()

# Fund selection section
st.subheader("📊 Fund Selection & Overview")

col1, col2 = st.columns([2, 1])

with col1:
    # Display fund listing with key metrics
    st.write("**Available Investment Funds**")

    # Sort by NAV and display top funds
    if "nav" in fund_list.columns:
        sorted_funds = fund_list.sort_values("nav", ascending=False)

        # Display metrics for highest NAV fund
        if len(sorted_funds) > 0:
            highest_nav_fund = sorted_funds.iloc[0]

            st.success(
                f"**Highest NAV Fund**: {highest_nav_fund['short_name']} ({highest_nav_fund['fund_code']})"
            )

            # Display key metrics in columns
            metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

            with metric_col1:
                st.metric("NAV", f"{highest_nav_fund['nav']:,.0f}")

            with metric_col2:
                if pd.notna(highest_nav_fund.get("nav_change_inception")):
                    st.metric(
                        "Since Inception",
                        f"{highest_nav_fund['nav_change_inception']:,.0f}%",
                    )
                else:
                    st.metric("Since Inception", "N/A")

            with metric_col3:
                if pd.notna(highest_nav_fund.get("nav_change_36m_annualized")):
                    st.metric(
                        "3Y Annualized",
                        f"{highest_nav_fund['nav_change_36m_annualized']:,.0f}%",
                    )
                else:
                    st.metric("3Y Annualized", "N/A")

            with metric_col4:
                if pd.notna(highest_nav_fund.get("management_fee")):
                    st.metric(
                        "Management Fee", f"{highest_nav_fund['management_fee']:,.0f}%"
                    )
                else:
                    st.metric("Management Fee", "N/A")

with col2:
    # Fund selection dropdown
    fund_options = fund_list[["short_name", "fund_code"]].copy()
    fund_options["display"] = (
        fund_options["short_name"] + " (" + fund_options["fund_code"] + ")"
    )

    selected_fund_display = st.selectbox(
        "Select Fund for Detailed Analysis", fund_options["display"].tolist(), index=0
    )

    # Extract fund code from selection
    selected_fund_code = fund_options[fund_options["display"] == selected_fund_display][
        "fund_code"
    ].iloc[0]
    selected_fund_name = fund_options[fund_options["display"] == selected_fund_display][
        "short_name"
    ].iloc[0]

# Performance Charts Section
st.subheader("📈 Fund Performance Analysis")

# NAV Performance Chart
nav_data = get_fund_nav_report(selected_fund_name)

if not nav_data.empty:
    # Create NAV Performance Line Chart using chart service
    nav_chart = create_fund_nav_line_chart(nav_data, selected_fund_name)
    st.altair_chart(nav_chart, use_container_width=True)

    # Display additional performance metrics
    if len(nav_data) > 1:
        latest_nav = nav_data["nav_per_unit"].iloc[-1]
        first_nav = nav_data["nav_per_unit"].iloc[0]
        total_return = ((latest_nav - first_nav) / first_nav) * 100

        perf_col1, perf_col2, perf_col3 = st.columns(3)

        with perf_col1:
            st.metric("Latest NAV", f"{latest_nav:,.0f}")

        with perf_col2:
            st.metric("First NAV", f"{first_nav:,.0f}")

        with perf_col3:
            st.metric("Total Return", f"{total_return:,.0f}%")

else:
    st.warning(f"⚠️ NAV data not available for {selected_fund_name}")

# Fund Performance Comparison Chart
st.subheader("📊 Fund Performance Comparison")

# Create comparison chart for 36-month annualized returns
if "nav_change_36m_annualized" in fund_list.columns:
    # Filter funds with valid 36m data
    valid_funds = fund_list.dropna(subset=["nav_change_36m_annualized"])

    if len(valid_funds) > 0:
        # Create comparison chart for all funds
        comparison_chart = create_fund_comparison_bar_chart(valid_funds)

        st.altair_chart(comparison_chart, use_container_width=True)

# Asset and Industry Allocation Section
st.subheader("🎯 Fund Allocation Analysis")

allocation_col1, allocation_col2 = st.columns(2)

with allocation_col1:
    st.write("**Asset Allocation**")
    asset_data = get_fund_asset_allocation(selected_fund_name)

    if not asset_data.empty:
        # Create asset allocation pie chart using chart service
        asset_chart = create_fund_asset_pie_chart(asset_data, selected_fund_name)

        st.altair_chart(asset_chart, use_container_width=True)

        # Display asset allocation table - handle different column names
        percent_col = (
            "asset_percent"
            if "asset_percent" in asset_data.columns
            else "net_asset_percent"
        )
        if "asset_type" in asset_data.columns and percent_col in asset_data.columns:
            asset_display = asset_data[["asset_type", percent_col]].copy()
            asset_display.columns = ["Asset Type", "Allocation (%)"]
            asset_display["Allocation (%)"] = asset_display["Allocation (%)"].round(2)
            st.dataframe(asset_display, hide_index=True)
    else:
        st.warning("⚠️ Asset allocation data not available")

with allocation_col2:
    st.write("**Industry Allocation**")
    industry_data = get_fund_industry_allocation(selected_fund_name)

    if not industry_data.empty:
        # Create industry allocation pie chart using chart service
        industry_chart = create_fund_industry_pie_chart(
            industry_data, selected_fund_name
        )

        st.altair_chart(industry_chart, use_container_width=True)

        # Display industry allocation table
        if (
            "industry" in industry_data.columns
            and "net_asset_percent" in industry_data.columns
        ):
            industry_display = industry_data[["industry", "net_asset_percent"]].copy()
            industry_display.columns = ["Industry", "Allocation (%)"]
            industry_display["Allocation (%)"] = industry_display[
                "Allocation (%)"
            ].round(2)
            st.dataframe(industry_display, hide_index=True)
    else:
        st.warning("⚠️ Industry allocation data not available")

# Fund Details Section
st.subheader("📋 Fund Details")

selected_fund_info = fund_list[fund_list["fund_code"] == selected_fund_code]

if len(selected_fund_info) > 0:
    fund_info = selected_fund_info.iloc[0]

    detail_col1, detail_col2, detail_col3 = st.columns(3)

    with detail_col1:
        st.write("**Basic Information**")
        st.write(f"**Full Name**: {fund_info.get('name', 'N/A')}")
        st.write(f"**Fund Type**: {fund_info.get('fund_type', 'N/A')}")
        st.write(f"**Fund Owner**: {fund_info.get('fund_owner_name', 'N/A')}")
        st.write(f"**Inception Date**: {fund_info.get('inception_date', 'N/A')}")

    with detail_col2:
        st.write("**Performance Metrics**")
        st.write(
            f"**Current NAV**: {fund_info.get('nav', 'N/A'):,.2f}"
            if pd.notna(fund_info.get("nav"))
            else "**Current NAV**: N/A"
        )
        st.write(
            f"**Previous Change**: {fund_info.get('nav_change_previous', 'N/A'):.2f}%"
            if pd.notna(fund_info.get("nav_change_previous"))
            else "**Previous Change**: N/A"
        )
        st.write(
            f"**1 Month**: {fund_info.get('nav_change_1m', 'N/A'):.2f}%"
            if pd.notna(fund_info.get("nav_change_1m"))
            else "**1 Month**: N/A"
        )
        st.write(
            f"**6 Month**: {fund_info.get('nav_change_6m', 'N/A'):.2f}%"
            if pd.notna(fund_info.get("nav_change_6m"))
            else "**6 Month**: N/A"
        )

    with detail_col3:
        st.write("**Extended Performance**")
        st.write(
            f"**12 Month**: {fund_info.get('nav_change_12m', 'N/A'):.2f}%"
            if pd.notna(fund_info.get("nav_change_12m"))
            else "**12 Month**: N/A"
        )
        st.write(
            f"**24 Month**: {fund_info.get('nav_change_24m', 'N/A'):.2f}%"
            if pd.notna(fund_info.get("nav_change_24m"))
            else "**24 Month**: N/A"
        )
        st.write(
            f"**36 Month**: {fund_info.get('nav_change_36m', 'N/A'):.2f}%"
            if pd.notna(fund_info.get("nav_change_36m"))
            else "**36 Month**: N/A"
        )
        st.write(
            f"**Management Fee**: {fund_info.get('management_fee', 'N/A'):.2f}%"
            if pd.notna(fund_info.get("management_fee"))
            else "**Management Fee**: N/A"
        )

# Data Export Section
st.subheader("💾 Data Export")

export_col1, export_col2, export_col3, export_col4 = st.columns(4)

with export_col1:
    # Prepare fund list CSV data
    csv_data = fund_list.to_csv(index=False)
    st.download_button(
        label="📊 Download Fund List CSV",
        data=csv_data,
        file_name=f"vietnamese_funds_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )

with export_col2:
    # Prepare NAV data CSV (only show if data exists)
    if not nav_data.empty:
        nav_csv = nav_data.to_csv(index=False)
        st.download_button(
            label="📈 Download NAV Data CSV",
            data=nav_csv,
            file_name=f"nav_data_{selected_fund_code}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )
    else:
        st.write("📈 NAV Data (Not Available)")

with export_col3:
    # Prepare allocation data CSV (only show if data exists)
    if not industry_data.empty or not asset_data.empty:
        allocation_data = pd.concat(
            [
                asset_data.assign(type="Asset")
                if not asset_data.empty
                else pd.DataFrame(),
                industry_data.assign(type="Industry")
                if not industry_data.empty
                else pd.DataFrame(),
            ]
        )
        if not allocation_data.empty:
            allocation_csv = allocation_data.to_csv(index=False)
            st.download_button(
                label="🏭 Download Allocations CSV",
                data=allocation_csv,
                file_name=f"allocations_{selected_fund_code}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
            )
        else:
            st.write("🏭 Allocations (Not Available)")
    else:
        st.write("🏭 Allocations (Not Available)")

with export_col4:
    # Check if all charts are available for download
    charts_available = (
        not nav_data.empty
        and "nav_change_36m_annualized" in fund_list.columns
        and len(fund_list.dropna(subset=["nav_change_36m_annualized"])) > 0
        and (not asset_data.empty or not industry_data.empty)
    )

    if charts_available:
        # Generate chart data for download
        try:
            # Create all charts
            nav_chart = create_fund_nav_line_chart(nav_data, selected_fund_name)

            valid_funds = fund_list.dropna(subset=["nav_change_36m_annualized"])
            comparison_chart = create_fund_comparison_bar_chart(valid_funds)

            asset_chart = create_fund_asset_pie_chart(asset_data, selected_fund_name)
            industry_chart = create_fund_industry_pie_chart(
                industry_data, selected_fund_name
            )

            # Generate PNG data directly for download
            png_data = generate_fund_charts_2x2_png(
                nav_chart,
                comparison_chart,
                asset_chart,
                industry_chart,
                selected_fund_name,
                selected_fund_code,
            )

            if png_data:
                # Generate download filename
                download_filename = f"fund_dashboard_{selected_fund_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

                # Single download button that generates and downloads immediately
                st.download_button(
                    label="📊 Download Charts PNG",
                    data=png_data,
                    file_name=download_filename,
                    mime="image/png",
                    type="primary",
                )
            else:
                st.error("❌ Error generating chart dashboard")

        except Exception as e:
            st.error(f"❌ Error creating charts: {str(e)}")
    else:
        st.write("📊 Charts (Insufficient Data)")

# Footer
st.markdown("---")
st.markdown("""
**About Fund Analysis**: This page provides comprehensive analysis of Vietnamese investment funds using vnstock data. 
Key metrics include Net Asset Value (NAV) performance, asset allocation, industry distribution, and historical returns. 
All data is cached for performance and updated regularly.

**Note**: Fund data availability may vary. Some funds might not have complete historical data or allocation details.
""")
