import streamlit as st
import os
from dotenv import load_dotenv
from vnstock import Listing, register_user
from src.core.config import VNSTOCK_API_KEY_ENV

# Load environment variables from .env file
load_dotenv()

# Register vnstock API key globally (once per process, before any vnstock calls)
_vnstock_api_key = os.environ.get(VNSTOCK_API_KEY_ENV, "")
if _vnstock_api_key:
    try:
        register_user(_vnstock_api_key)
    except Exception:
        pass

# Set page configuration - this must be called first
st.set_page_config(page_title="Finance Bro", page_icon="📈", layout="wide")

# CSS loading removed


# API Key handling
if "api_key" not in st.session_state:
    st.session_state.api_key = os.environ.get("OPENAI_API_KEY", "")

if not st.session_state.api_key:
    st.info(
        "AI chat features require an OpenAI API key. Set it on the Stock Analysis page."
    )


# Function to create the main Finance Bro page content
def main_page():
    """Main Finance Bro page - serves as the hub for stock symbol selection"""
    st.markdown("# 📈 Finance Bro")
    st.markdown("Select a stock symbol to analyze across all pages")

    # Stock symbol selection with searchable dropdown
    st.subheader("🔍 Stock symbol selection")

    # Load stock symbols using Listing().all_symbols() since this is the entry point
    if "stock_symbols_list" not in st.session_state:
        try:
            with st.spinner("Loading stock symbols..."):
                symbols_df = Listing().all_symbols()
                st.session_state.stock_symbols_list = sorted(
                    symbols_df["symbol"].tolist()
                )
                st.session_state.symbols_df = (
                    symbols_df  # Cache the full DataFrame for organ_name access
                )
                st.success("✅ Stock symbols loaded!")
        except Exception as e:
            st.warning(f"Could not load stock symbols: {str(e)}")
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

    stock_symbols_list = st.session_state.stock_symbols_list

    # Use selectbox for single selection
    current_symbol = st.selectbox(
        "Search and select a stock symbol:",
        options=stock_symbols_list,
        index=stock_symbols_list.index(st.session_state.stock_symbol)
        if "stock_symbol" in st.session_state
        and st.session_state.stock_symbol in stock_symbols_list
        else stock_symbols_list.index("REE")
        if "REE" in stock_symbols_list
        else 0,
        placeholder="Type to search for stock symbols...",
        help="Search and select one stock symbol to analyze",
    )

    # Store the selected symbol in session state
    if current_symbol:
        if (
            "stock_symbol" not in st.session_state
            or st.session_state.stock_symbol != current_symbol
        ):
            st.session_state.stock_symbol = current_symbol
            st.success(f"✅ Selected stock symbol: **{current_symbol}**")
            st.caption("You can now navigate to other pages to analyze this stock.")
            st.rerun()  # Force immediate rerun to update sidebar

    # Display current selection status
    if "stock_symbol" in st.session_state:
        st.markdown("### 📈 Current selection")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Selected symbol", st.session_state.stock_symbol, border=True)
        with col2:
            st.metric("Status", "✅ Ready", border=True)
        with col3:
            if st.button("Clear Selection", type="secondary"):
                if "stock_symbol" in st.session_state:
                    # Reset to default symbol instead of deleting
                    st.session_state.stock_symbol = (
                        "REE" if "REE" in stock_symbols_list else stock_symbols_list[0]
                    )
                st.rerun()

        # Quick navigation to analysis pages
        st.markdown("### 🚀 Quick navigation")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("📊 Stock Analysis", use_container_width=True):
                st.switch_page("pages/bro.py")

        with col2:
            if st.button("📈 Price Analysis", use_container_width=True):
                st.switch_page("pages/Stock_Price_Analysis.py")

        with col3:
            if st.button("🏢 Company Overview", use_container_width=True):
                st.switch_page("pages/Company_Overview.py")

        with col4:
            if st.button("💼 Portfolio Optimization", use_container_width=True):
                st.switch_page("pages/Portfolio_Optimization.py")

        # Second row of navigation buttons
        st.markdown("")  # Add some spacing
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("🔍 Stock Screener", use_container_width=True):
                st.switch_page("pages/Screener.py")

        with col2:
            if st.button("📊 Technical Analysis", use_container_width=True):
                st.switch_page("pages/Technical_Analysis.py")

    # Instructions and app information
    st.markdown("### 📋 How to use Finance Bro")

    with st.expander("📖 Instructions", expanded=False):
        st.markdown("""
        **Finance Bro** is your AI-powered financial analysis companion for Vietnamese stock market data.
        
        **Getting Started:**
        1. **Select a Stock Symbol** - Use the searchable dropdown above to find and select a Vietnamese stock symbol
        2. **Navigate to Analysis Pages** - Use the navigation menu or quick buttons to explore different analysis tools
        3. **Stock Symbol Persistence** - Your selected symbol will be available across all pages
        
        **Available Analysis Tools:**
        - **📊 Stock Analysis (Main Bro)** - AI-powered chat interface for comprehensive financial analysis
        - **📈 Price Analysis** - Interactive price charts and technical analysis
        - **📊 Technical Analysis** - Candlestick charts for stocks with heating up technical signals
        - **🏢 Company Overview** - Company profile, ownership structure, and management team
        - **💼 Portfolio Optimization** - Modern Portfolio Theory-based portfolio optimization
        - **🔍 Stock Screener** - Filter and analyze stocks by financial metrics across industries
        
        **Tips:**
        - Your selected stock symbol persists across all pages
        - Each page has specialized tools for different types of analysis
        - The main Stock Analysis page offers the most comprehensive AI-powered insights
        """)

    # Footer
    st.markdown("---")
    st.markdown("🚀 **Finance Bro** - AI Stock Analysis for Vietnamese Market")
    st.markdown(
        "Built with [Streamlit](https://streamlit.io), [PandasAI](https://pandas-ai.com), and [Vnstock](https://github.com/thinh-vu/vnstock)"
    )


# Define pages using st.Page
pages = {
    "Home": [
        st.Page(main_page, title="📈 Finance Bro", icon="🏠"),
    ],
    "Analysis": [
        st.Page("pages/bro.py", title="Stock Analysis", icon="📊"),
        st.Page("pages/Stock_Price_Analysis.py", title="Price Analysis", icon="📈"),
        st.Page("pages/Technical_Analysis.py", title="Technical Analysis", icon="📊"),
        st.Page("pages/Company_Overview.py", title="Company Overview", icon="🏢"),
        st.Page(
            "pages/Portfolio_Optimization.py", title="Portfolio Optimization", icon="💼"
        ),
        st.Page("pages/Screener.py", title="Stock Screener", icon="🔍"),
    ],
}

# Sidebar for user controls
with st.sidebar:
    st.header("🔧 Controls")
    # GitHub link
    st.markdown(
        "[Finance Bro on GitHub](https://github.com/gahoccode/finance-bro) by Tam Le"
    )

# Set up navigation at the top
pg = st.navigation(pages, position="top")

# Run the selected page
pg.run()
