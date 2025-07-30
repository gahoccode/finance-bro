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

# Set page configuration
st.set_page_config(
    page_title="Company Profile Analysis",
    page_icon="📊",
    layout="wide"
)

# Title and description
st.title("📈 Company Profile Analysis")
st.markdown("Analyze company ownership structure and management information")

# User input for ticker symbol
stock_symbol = st.text_input("Enter Stock Symbol (e.g., REE, VIC, VNM):", value="REE").upper()

if stock_symbol:
    try:
        # Get cached ownership data
        ownership_percentage = get_ownership_data(stock_symbol)
        
        if not ownership_percentage.empty:
            # Display ownership chart and metrics at the top
            st.header(f"🏢 {stock_symbol} - Ownership Structure")
            
            # Create two columns for chart and summary
            col_chart, col_summary = st.columns([3, 1])
            
            with col_chart:
                # Sort by quantity for better visualization
                ownership_sorted = ownership_percentage.sort_values('quantity', ascending=True)
                
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
                    text=alt.Text('share_own_percent:Q', format='.1f%')
                )
                
                # Combine chart and text labels
                final_chart = (bars + text).properties(
                    title=f'Ownership by Share Quantity - {stock_symbol}',
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
                st.subheader("📊 Summary")
                st.metric("Total Shareholders", len(ownership_percentage))
                st.metric("Largest Shareholder", f"{ownership_percentage['share_own_percent'].max():.1f}%")
                st.metric("Top 3 Combined", f"{ownership_percentage['share_own_percent'].nlargest(3).sum():.1f}%")
                
                # Display raw data in expander
                with st.expander("View Raw Data"):
                    st.dataframe(ownership_percentage, use_container_width=True)
        
        else:
            st.info("No ownership data available for this symbol.")
        
        # Create tabs for additional information
        tab1, tab2 = st.tabs(["👥 Management Team", "📋 Full Details"])
        
        with tab1:
            st.header("Company Management")
            try:
                # Get cached management data
                management_team = get_management_data(stock_symbol)
                
                if not management_team.empty:
                    st.dataframe(management_team, use_container_width=True)
                else:
                    st.info("No management information available for this symbol.")
                    
            except Exception as e:
                st.error(f"Error loading management data: {str(e)}")
        
        with tab2:
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
