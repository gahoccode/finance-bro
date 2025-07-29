import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from vnstock import Company, Vnstock
import warnings
warnings.filterwarnings('ignore')

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
        # Get ownership data first (to display at top)
        stock = Vnstock().stock(symbol=stock_symbol, source='VCI')
        company_info = stock.company
        ownership_percentage = company_info.shareholders()
        
        if not ownership_percentage.empty:
            # Display ownership chart and metrics at the top
            st.header(f"🏢 {stock_symbol} - Ownership Structure")
            
            # Create two columns for chart and summary
            col_chart, col_summary = st.columns([3, 1])
            
            with col_chart:
                # Create horizontal bar chart
                fig, ax = plt.subplots(figsize=(12, 8))
                
                # Sort by ownership percentage for better visualization
                ownership_sorted = ownership_percentage.sort_values('share_own_percent', ascending=True)
                
                # Create horizontal bar chart
                sns.barplot(
                    data=ownership_sorted,
                    y='share_holder',
                    x='share_own_percent',
                    palette='viridis',
                    ax=ax
                )
                
                # Customize the plot
                ax.set_xlabel('Ownership Percentage (%)', fontsize=12)
                ax.set_ylabel('Shareholder', fontsize=12)
                ax.set_title(f'Ownership Distribution - {stock_symbol}', fontsize=14, fontweight='bold')
                
                # Add percentage labels on bars
                for i, (idx, row) in enumerate(ownership_sorted.iterrows()):
                    ax.text(
                        row['share_own_percent'] + 0.5,
                        i,
                        f'{row["share_own_percent"]:.1f}%',
                        va='center',
                        fontsize=10
                    )
                
                plt.tight_layout()
                st.pyplot(fig)
            
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
                # Get company officers
                company = Company(symbol=stock_symbol)
                management_team = company.officers(lang='en')
                
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
