import streamlit as st
import pandas as pd
import altair as alt
from vnstock import Company, Vnstock
import warnings
warnings.filterwarnings('ignore')

# Cache data to reduce API calls
@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_ownership_data(symbol):
    """Get ownership data with caching"""
    try:
        stock = Vnstock().stock(symbol=symbol, source='VCI')
        company_info = stock.company
        return company_info.shareholders()
    except Exception as e:
        st.error(f"Error fetching ownership data: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_management_data(symbol):
    """Get management data with caching"""
    try:
        company = Company(symbol=symbol)
        return company.officers(lang='en')
    except Exception as e:
        st.error(f"Error fetching management data: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_subsidiaries_data(symbol):
    """Get subsidiaries data with caching"""
    try:
        company = Company(symbol=symbol)
        return company.subsidiaries()
    except Exception as e:
        st.error(f"Error fetching subsidiaries data: {str(e)}")
        return pd.DataFrame()

# Set page configuration
st.set_page_config(
    page_title="Company Profile Analysis",
    layout="wide"
)

import os

# Load custom CSS
with open('static/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Get stock symbol from session state (set in main app)
# If not available, show message to use main app first
if 'stock_symbol' in st.session_state and st.session_state.stock_symbol:
    stock_symbol = st.session_state.stock_symbol
    st.info(f"📊 Analyzing stock: **{stock_symbol}** (from main app)")
else:
    st.warning("⚠️ No stock symbol selected. Please go to the main Finance Bro page and select a stock symbol first.")
    st.stop()

# Get company full name from cached symbols DataFrame
company_name = stock_symbol  # Default fallback
if 'symbols_df' in st.session_state and st.session_state.symbols_df is not None:
    try:
        symbols_df = st.session_state.symbols_df
        matching_company = symbols_df[symbols_df['symbol'] == stock_symbol]
        if not matching_company.empty and 'organ_name' in symbols_df.columns:
            company_name = matching_company['organ_name'].iloc[0]
    except Exception:
        # Keep using stock_symbol as fallback if anything fails
        pass
else:
    # If symbols not cached, user should visit bro.py first for optimal experience
    st.info("💡 For best experience with company names, visit the Stock Analysis page first to load stock symbols.")

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
                ownership_sorted = ownership_percentage.sort_values('quantity', ascending=True).copy()
                ownership_sorted['share_own_percent'] = ownership_sorted['share_own_percent'] * 100
                
                # Create base chart with quantity as x-axis
                base = alt.Chart(ownership_sorted).encode(
                    y=alt.Y('share_holder:N', title='Shareholder', sort='-x'),
                    x=alt.X('quantity:Q', title='Number of Shares')
                )
                
                # Create bar chart
                bars = base.mark_bar(color='black').encode(
                    tooltip=[
                        alt.Tooltip('share_holder:N', title='Shareholder'),
                        alt.Tooltip('quantity:Q', title='Shares', format=',.0f'),
                        alt.Tooltip('share_own_percent:Q', title='Ownership %', format='.1f')
                    ]
                )
                
                # Create text labels for share_own_percent
                text = base.mark_text(
                    align='left',
                    baseline='middle',
                    dx=3,  # Nudge text to right of bars
                    fontSize=10
                ).encode(
                    x=alt.X('quantity:Q'),
                    text=alt.Text('share_own_percent:Q', format='.1f')
                )
                
                # Combine chart and text labels
                final_chart = (bars + text).properties(
                    title=f'Ownership by Share Quantity - {company_name}',
                    width=600,
                    height=400
                ).configure_axis(
                    labelFontSize=10,
                    titleFontSize=12
                ).configure_title(
                    fontSize=14,
                    fontWeight='bold'
                )
                
                # Display the chart
                st.altair_chart(final_chart, use_container_width=True)
            
            with col_summary:
                st.subheader("Summary")
                st.metric("Total Shareholders", len(ownership_percentage))
                st.metric("Largest Shareholder", f"{(ownership_percentage['share_own_percent'].max() * 100):.1f}%")
                st.metric("Top 3 Combined", f"{(ownership_percentage['share_own_percent'].nlargest(3).sum() * 100):.1f}%")
                
                # Display raw data in expander
                with st.expander("View Raw Data"):
                    st.dataframe(ownership_percentage, use_container_width=True)
        
        else:
            st.info("No ownership data available for this symbol.")
        
        # Create tabs for additional information
        tab1, tab2, tab3 = st.tabs(["Management Team", "Subsidiaries", "Full Details"])
        
        with tab1:
            st.header("Company Management")
            try:
                # Get cached management data
                management_team = get_management_data(stock_symbol)
                
                if not management_team.empty:
                    st.dataframe(management_team, use_container_width=True)
                    
                    # Create management team ownership chart
                    st.subheader("Management Team Ownership")
                    
                    # Filter for officers with quantity data
                    mgmt_with_shares = management_team[
                        management_team['quantity'].notna() & 
                        management_team['officer_own_percent'].notna() &
                        (management_team['quantity'] > 0)
                    ].copy()
                    
                    if not mgmt_with_shares.empty:
                        # Sort by quantity for better visualization and convert percentage
                        mgmt_sorted = mgmt_with_shares.sort_values('quantity', ascending=True).copy()
                        mgmt_sorted['officer_own_percent'] = mgmt_sorted['officer_own_percent'] * 100
                        
                        # Create base chart
                        mgmt_base = alt.Chart(mgmt_sorted).encode(
                            y=alt.Y('officer_name:N', title='Officer Name', sort='-x'),
                            x=alt.X('quantity:Q', title='Number of Shares')
                        )
                        
                        # Create bars
                        mgmt_bars = mgmt_base.mark_bar(color='black').encode(
                            tooltip=[
                                alt.Tooltip('officer_name:N', title='Officer'),
                                alt.Tooltip('position_short_name:N', title='Position'),
                                alt.Tooltip('quantity:Q', title='Shares', format=',.0f'),
                                alt.Tooltip('officer_own_percent:Q', title='Ownership %', format='.2f')
                            ]
                        )
                        
                        # Create text labels
                        mgmt_text = mgmt_base.mark_text(
                            align='left',
                            baseline='middle',
                            dx=3,
                            fontSize=9,
                            color='black'
                        ).encode(
                            x=alt.X('quantity:Q'),
                            text=alt.Text('officer_own_percent:Q', format='.2f')
                        )
                        
                        # Combine chart
                        mgmt_chart = (mgmt_bars + mgmt_text).properties(
                            title=f'Management Team Share Ownership - {company_name}',
                            width=600,
                            height=300
                        ).configure_axis(
                            labelFontSize=9,
                            titleFontSize=11
                        ).configure_title(
                            fontSize=13,
                            fontWeight='bold'
                        )
                        
                        st.altair_chart(mgmt_chart, use_container_width=True)
                    else:
                        st.info("No management share ownership data available.")
                        
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
                    # Display subsidiaries table
                    st.subheader("Subsidiaries Overview")
                    # Convert ownership_percent to percentage for display
                    display_subs = subsidiaries[['organ_name', 'ownership_percent', 'type']].copy()
                    display_subs['ownership_percent'] = display_subs['ownership_percent'] * 100
                    st.dataframe(display_subs, use_container_width=True)
                    
                    # Create ownership percentage visualization
                    st.subheader("Subsidiaries Ownership Distribution")
                    
                    # Filter out subsidiaries with valid ownership data and convert to percentage
                    subs_with_ownership = subsidiaries[
                        subsidiaries['ownership_percent'].notna() & 
                        (subsidiaries['ownership_percent'] > 0)
                    ].copy()
                    subs_with_ownership['ownership_percent'] = subs_with_ownership['ownership_percent'] * 100
                    
                    if not subs_with_ownership.empty:
                        # Sort by ownership percentage for better visualization
                        subs_sorted = subs_with_ownership.sort_values('ownership_percent', ascending=True)
                        
                        # Create base chart
                        subs_base = alt.Chart(subs_sorted).encode(
                            y=alt.Y('organ_name:N', title='Subsidiary Name', sort='-x'),
                            x=alt.X('ownership_percent:Q', title='Ownership Percentage (%)')
                        )
                        
                        # Create bars
                        subs_bars = subs_base.mark_bar(color='steelblue').encode(
                            tooltip=[
                                alt.Tooltip('organ_name:N', title='Subsidiary'),
                                alt.Tooltip('ownership_percent:Q', title='Ownership %', format='.1f'),
                                alt.Tooltip('type:N', title='Type')
                            ]
                        )
                        
                        # Create text labels
                        subs_text = subs_base.mark_text(
                            align='left',
                            baseline='middle',
                            dx=3,
                            fontSize=10,
                            color='black'
                        ).encode(
                            x=alt.X('ownership_percent:Q'),
                            text=alt.Text('ownership_percent:Q', format='.1f')
                        )
                        
                        # Combine chart
                        subs_chart = (subs_bars + subs_text).properties(
                            title=f'Subsidiaries Ownership Percentage - {company_name}',
                            width=600,
                            height=max(300, len(subs_sorted) * 25)
                        ).configure_axis(
                            labelFontSize=10,
                            titleFontSize=12
                        ).configure_title(
                            fontSize=14,
                            fontWeight='bold'
                        )
                        
                        st.altair_chart(subs_chart, use_container_width=True)
                        
                        # Summary metrics
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total Subsidiaries", len(subsidiaries))
                        with col2:
                            st.metric("With Ownership Data", len(subs_with_ownership))
                        with col3:
                            avg_ownership = subs_with_ownership['ownership_percent'].mean()
                            st.metric("Average Ownership", f"{avg_ownership:.1f}%")
                    else:
                        st.info("No subsidiaries with ownership percentage data available.")
                        
                else:
                    st.info("No subsidiaries information available for this symbol.")
                    
            except Exception as e:
                st.error(f"Error loading subsidiaries data: {str(e)}")
        
        with tab3:
            st.header("Detailed Information")
            if not ownership_percentage.empty:
                st.subheader("Complete Ownership Data")
                st.dataframe(ownership_percentage, use_container_width=True)
    
    except Exception as e:
        st.error(f"Error processing stock symbol '{stock_symbol}': {str(e)}")
        st.info("Please check if the stock symbol is correct and try again.")

else:
    st.info("Please enter a stock symbol to begin analysis.")

# Footer
st.markdown("---")
st.markdown("*Powered by Vnstock and Streamlit*")
