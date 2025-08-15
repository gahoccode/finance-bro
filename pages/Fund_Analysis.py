import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta

# Import from modular services
from src.services.vnstock_api import (
    get_fund_listing,
    get_fund_nav_report,
    get_fund_asset_allocation,
    get_fund_industry_allocation
)
from src.core.config import THEME_COLORS

st.set_page_config(page_title="Fund Analysis", layout="wide")

st.title("🏦 Vietnamese Fund Analysis")

# Main content
with st.container():
    st.header("Investment Fund Performance Analysis")
    st.write("Comprehensive analysis of Vietnamese investment funds with NAV performance, asset allocation, and industry distribution.")

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
    if 'nav' in fund_list.columns:
        sorted_funds = fund_list.sort_values('nav', ascending=False)
        
        # Display metrics for highest NAV fund
        if len(sorted_funds) > 0:
            highest_nav_fund = sorted_funds.iloc[0]
            
            st.success(f"**Highest NAV Fund**: {highest_nav_fund['short_name']} ({highest_nav_fund['fund_code']})")
            
            # Display key metrics in columns
            metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
            
            with metric_col1:
                st.metric("NAV", f"{highest_nav_fund['nav']:,.2f}")
            
            with metric_col2:
                if pd.notna(highest_nav_fund.get('nav_change_inception')):
                    st.metric("Since Inception", f"{highest_nav_fund['nav_change_inception']:.2f}%")
                else:
                    st.metric("Since Inception", "N/A")
            
            with metric_col3:
                if pd.notna(highest_nav_fund.get('nav_change_36m_annualized')):
                    st.metric("3Y Annualized", f"{highest_nav_fund['nav_change_36m_annualized']:.2f}%")
                else:
                    st.metric("3Y Annualized", "N/A")
            
            with metric_col4:
                if pd.notna(highest_nav_fund.get('management_fee')):
                    st.metric("Management Fee", f"{highest_nav_fund['management_fee']:.2f}%")
                else:
                    st.metric("Management Fee", "N/A")

with col2:
    # Fund selection dropdown
    fund_options = fund_list[['short_name', 'fund_code']].copy()
    fund_options['display'] = fund_options['short_name'] + ' (' + fund_options['fund_code'] + ')'
    
    selected_fund_display = st.selectbox(
        "Select Fund for Detailed Analysis",
        fund_options['display'].tolist(),
        index=0
    )
    
    # Extract fund code from selection
    selected_fund_code = fund_options[fund_options['display'] == selected_fund_display]['fund_code'].iloc[0]
    selected_fund_name = fund_options[fund_options['display'] == selected_fund_display]['short_name'].iloc[0]

# Performance Charts Section
st.subheader("📈 Fund Performance Analysis")

# NAV Performance Chart
nav_data = get_fund_nav_report(selected_fund_name)

if not nav_data.empty:
    # Prepare NAV chart data
    nav_chart_data = nav_data.copy()
    
    # Create NAV Performance Line Chart with Finance Bro colors
    nav_chart = alt.Chart(nav_chart_data).mark_line(
        color=THEME_COLORS["primary"],
        strokeWidth=3
    ).add_selection(
        alt.selection_interval(bind='scales')
    ).encode(
        x=alt.X('date:T', title='Date', axis=alt.Axis(format='%Y-%m')),
        y=alt.Y('nav_per_unit:Q', title='NAV per Unit', scale=alt.Scale(zero=False)),
        tooltip=[
            alt.Tooltip('date:T', title='Date', format='%Y-%m-%d'),
            alt.Tooltip('nav_per_unit:Q', title='NAV per Unit', format='.2f')
        ]
    ).properties(
        width=700,
        height=400,
        title=f"NAV Performance - {selected_fund_name}"
    ).resolve_scale(
        color='independent'
    )
    
    st.altair_chart(nav_chart, use_container_width=True)
    
    # Display additional performance metrics
    if len(nav_data) > 1:
        latest_nav = nav_data['nav_per_unit'].iloc[-1]
        first_nav = nav_data['nav_per_unit'].iloc[0]
        total_return = ((latest_nav - first_nav) / first_nav) * 100
        
        perf_col1, perf_col2, perf_col3 = st.columns(3)
        
        with perf_col1:
            st.metric("Latest NAV", f"{latest_nav:.2f}")
        
        with perf_col2:
            st.metric("First NAV", f"{first_nav:.2f}")
        
        with perf_col3:
            st.metric("Total Return", f"{total_return:.2f}%")

else:
    st.warning(f"⚠️ NAV data not available for {selected_fund_name}")

# Fund Performance Comparison Chart
st.subheader("📊 Fund Performance Comparison")

# Create comparison chart for 36-month annualized returns
if 'nav_change_36m_annualized' in fund_list.columns:
    # Filter funds with valid 36m data
    valid_funds = fund_list.dropna(subset=['nav_change_36m_annualized'])
    
    if len(valid_funds) > 0:
        # Sort and take top 15 funds for readability
        top_funds = valid_funds.nlargest(15, 'nav_change_36m_annualized')
        
        comparison_chart = alt.Chart(top_funds).mark_bar(
            color=THEME_COLORS["tertiary"],
            stroke=THEME_COLORS["primary"],
            strokeWidth=1
        ).encode(
            x=alt.X('nav_change_36m_annualized:Q', title='36-Month Annualized Return (%)'),
            y=alt.Y('short_name:N', title='Fund Name', sort='-x'),
            tooltip=[
                alt.Tooltip('short_name:N', title='Fund Name'),
                alt.Tooltip('nav_change_36m_annualized:Q', title='36M Return (%)', format='.2f'),
                alt.Tooltip('fund_type:N', title='Fund Type'),
                alt.Tooltip('fund_owner_name:N', title='Fund Owner')
            ]
        ).properties(
            width=700,
            height=400,
            title="Top 15 Funds - 36-Month Annualized Returns"
        )
        
        st.altair_chart(comparison_chart, use_container_width=True)

# Asset and Industry Allocation Section
st.subheader("🎯 Fund Allocation Analysis")

allocation_col1, allocation_col2 = st.columns(2)

with allocation_col1:
    st.write("**Asset Allocation**")
    asset_data = get_fund_asset_allocation(selected_fund_name)
    
    if not asset_data.empty:
        # Create pie chart for asset allocation
        asset_chart = alt.Chart(asset_data).mark_arc(
            innerRadius=50,
            stroke='white',
            strokeWidth=2
        ).encode(
            theta=alt.Theta('net_asset_percent:Q', title='Percentage'),
            color=alt.Color('asset_type:N', 
                          scale=alt.Scale(range=[THEME_COLORS["primary"], 
                                               THEME_COLORS["secondary"], 
                                               THEME_COLORS["tertiary"], 
                                               "#8B7D7B", "#A59B96"])),
            tooltip=[
                alt.Tooltip('asset_type:N', title='Asset Type'),
                alt.Tooltip('net_asset_percent:Q', title='Percentage (%)', format='.2f')
            ]
        ).properties(
            width=300,
            height=300,
            title=f"Asset Allocation - {selected_fund_name}"
        )
        
        st.altair_chart(asset_chart, use_container_width=True)
        
        # Display asset allocation table
        if 'asset_type' in asset_data.columns and 'net_asset_percent' in asset_data.columns:
            asset_display = asset_data[['asset_type', 'net_asset_percent']].copy()
            asset_display.columns = ['Asset Type', 'Allocation (%)']
            asset_display['Allocation (%)'] = asset_display['Allocation (%)'].round(2)
            st.dataframe(asset_display, hide_index=True)
    else:
        st.warning("⚠️ Asset allocation data not available")

with allocation_col2:
    st.write("**Industry Allocation**")
    industry_data = get_fund_industry_allocation(selected_fund_name)
    
    if not industry_data.empty:
        # Create horizontal bar chart for industry allocation
        industry_chart = alt.Chart(industry_data).mark_bar(
            color=THEME_COLORS["tertiary"],
            stroke=THEME_COLORS["primary"],
            strokeWidth=1
        ).encode(
            x=alt.X('net_asset_percent:Q', title='Allocation (%)'),
            y=alt.Y('industry:N', title='Industry', sort='-x'),
            tooltip=[
                alt.Tooltip('industry:N', title='Industry'),
                alt.Tooltip('net_asset_percent:Q', title='Allocation (%)', format='.2f')
            ]
        ).properties(
            width=300,
            height=300,
            title=f"Industry Allocation - {selected_fund_name}"
        )
        
        st.altair_chart(industry_chart, use_container_width=True)
        
        # Display industry allocation table
        if 'industry' in industry_data.columns and 'net_asset_percent' in industry_data.columns:
            industry_display = industry_data[['industry', 'net_asset_percent']].copy()
            industry_display.columns = ['Industry', 'Allocation (%)']
            industry_display['Allocation (%)'] = industry_display['Allocation (%)'].round(2)
            st.dataframe(industry_display, hide_index=True)
    else:
        st.warning("⚠️ Industry allocation data not available")

# Fund Details Section
st.subheader("📋 Fund Details")

selected_fund_info = fund_list[fund_list['fund_code'] == selected_fund_code]

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
        st.write(f"**Current NAV**: {fund_info.get('nav', 'N/A'):,.2f}" if pd.notna(fund_info.get('nav')) else "**Current NAV**: N/A")
        st.write(f"**Previous Change**: {fund_info.get('nav_change_previous', 'N/A'):.2f}%" if pd.notna(fund_info.get('nav_change_previous')) else "**Previous Change**: N/A")
        st.write(f"**1 Month**: {fund_info.get('nav_change_1m', 'N/A'):.2f}%" if pd.notna(fund_info.get('nav_change_1m')) else "**1 Month**: N/A")
        st.write(f"**6 Month**: {fund_info.get('nav_change_6m', 'N/A'):.2f}%" if pd.notna(fund_info.get('nav_change_6m')) else "**6 Month**: N/A")
    
    with detail_col3:
        st.write("**Extended Performance**")
        st.write(f"**12 Month**: {fund_info.get('nav_change_12m', 'N/A'):.2f}%" if pd.notna(fund_info.get('nav_change_12m')) else "**12 Month**: N/A")
        st.write(f"**24 Month**: {fund_info.get('nav_change_24m', 'N/A'):.2f}%" if pd.notna(fund_info.get('nav_change_24m')) else "**24 Month**: N/A")
        st.write(f"**36 Month**: {fund_info.get('nav_change_36m', 'N/A'):.2f}%" if pd.notna(fund_info.get('nav_change_36m')) else "**36 Month**: N/A")
        st.write(f"**Management Fee**: {fund_info.get('management_fee', 'N/A'):.2f}%" if pd.notna(fund_info.get('management_fee')) else "**Management Fee**: N/A")

# Data Export Section
st.subheader("💾 Data Export")

export_col1, export_col2, export_col3 = st.columns(3)

with export_col1:
    if st.button("📊 Export Fund List"):
        csv_data = fund_list.to_csv(index=False)
        st.download_button(
            label="Download Fund List CSV",
            data=csv_data,
            file_name=f"vietnamese_funds_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

with export_col2:
    if not nav_data.empty and st.button("📈 Export NAV Data"):
        nav_csv = nav_data.to_csv(index=False)
        st.download_button(
            label="Download NAV Data CSV",
            data=nav_csv,
            file_name=f"nav_data_{selected_fund_code}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

with export_col3:
    if not industry_data.empty and st.button("🏭 Export Allocations"):
        allocation_data = pd.concat([
            asset_data.assign(type='Asset') if not asset_data.empty else pd.DataFrame(),
            industry_data.assign(type='Industry') if not industry_data.empty else pd.DataFrame()
        ])
        if not allocation_data.empty:
            allocation_csv = allocation_data.to_csv(index=False)
            st.download_button(
                label="Download Allocation CSV",
                data=allocation_csv,
                file_name=f"allocations_{selected_fund_code}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

# Footer
st.markdown("---")
st.markdown("""
**About Fund Analysis**: This page provides comprehensive analysis of Vietnamese investment funds using vnstock data. 
Key metrics include Net Asset Value (NAV) performance, asset allocation, industry distribution, and historical returns. 
All data is cached for performance and updated regularly.

**Note**: Fund data availability may vary. Some funds might not have complete historical data or allocation details.
""")