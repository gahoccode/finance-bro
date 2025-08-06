import streamlit as st
import os
from dotenv import load_dotenv
from vnstock import Listing

# Load environment variables from .env file
load_dotenv()

# Set page configuration - this must be called first
st.set_page_config(
    page_title="Finance Bro",
    page_icon="📈",
    layout="wide"
)

# Load custom CSS
with open('static/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Authentication handling
if not st.user.is_logged_in:
    st.title("🔒 Authentication Required")
    st.markdown("Please authenticate with Google to access Finance Bro")
    
    # Create a clean login interface
    st.button("Login with Google", on_click=st.login)
    
    # Show helpful information
    st.markdown("---")
    st.info("After logging in, you'll be redirected back to the app automatically.")
    
    st.stop()

# API Key handling
if 'api_key' not in st.session_state:
    st.session_state.api_key = os.environ.get("OPENAI_API_KEY", "")

if not st.session_state.api_key:
    st.warning("OpenAI API Key Required")
    
    with st.expander("Enter API Key", expanded=True):
        api_key_input = st.text_input(
            "OpenAI API Key:",
            type="password",
            placeholder="sk-...",
            help="Enter your OpenAI API key to enable AI analysis"
        )
        
        if st.button("Save API Key", type="primary"):
            if api_key_input.startswith("sk-"):
                st.session_state.api_key = api_key_input
                os.environ["OPENAI_API_KEY"] = api_key_input
                st.success("✅ API Key saved successfully!")
                st.rerun()
            else:
                st.error("❌ Invalid API key format. Please check your key.")
    
    st.stop()

# Function to create the main Finance Bro page content
def main_page():
    """Main Finance Bro page - serves as the hub for stock symbol selection"""
    st.markdown('<h1 class="main-header">📈 Finance Bro</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666; font-size: 1.1rem; margin-top: -0.5rem; margin-bottom: 2rem;">Select a stock symbol to analyze across all pages</p>', unsafe_allow_html=True)
    
    # Stock symbol selection with searchable dropdown
    st.subheader("🔍 Stock Symbol Selection")
    
    # Load stock symbols using Listing().all_symbols() since this is the entry point
    if 'stock_symbols_list' not in st.session_state:
        try:
            with st.spinner("Loading stock symbols..."):
                symbols_df = Listing().all_symbols()
                st.session_state.stock_symbols_list = sorted(symbols_df['symbol'].tolist())
                st.session_state.symbols_df = symbols_df  # Cache the full DataFrame for organ_name access
                st.success("✅ Stock symbols loaded!")
        except Exception as e:
            st.warning(f"Could not load stock symbols: {str(e)}")
            st.session_state.stock_symbols_list = ["REE", "VIC", "VNM", "VCB", "BID", "HPG", "FPT", "FMC", "DHC"]
            st.session_state.symbols_df = None
    
    stock_symbols_list = st.session_state.stock_symbols_list
    
    # Use selectbox for single selection
    current_symbol = st.selectbox(
        "Search and select a stock symbol:",
        options=stock_symbols_list,
        index=stock_symbols_list.index(st.session_state.stock_symbol) if 'stock_symbol' in st.session_state and st.session_state.stock_symbol in stock_symbols_list else stock_symbols_list.index("REE") if "REE" in stock_symbols_list else 0,
        placeholder="Type to search for stock symbols...",
        help="Search and select one stock symbol to analyze"
    )
    
    # Store the selected symbol in session state
    if current_symbol:
        if 'stock_symbol' not in st.session_state or st.session_state.stock_symbol != current_symbol:
            st.session_state.stock_symbol = current_symbol
            st.success(f"✅ Selected stock symbol: **{current_symbol}**")
            st.info("📊 You can now navigate to other pages to analyze this stock!")
            st.rerun()  # Force immediate rerun to update sidebar
    
    # Display current selection status
    if 'stock_symbol' in st.session_state:
        st.markdown("---")
        st.markdown("### 📈 Current Selection")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Selected Symbol", st.session_state.stock_symbol)
        with col2:
            st.metric("Status", "✅ Ready")
        with col3:
            if st.button("Clear Selection", type="secondary"):
                if 'stock_symbol' in st.session_state:
                    # Reset to default symbol instead of deleting
                    st.session_state.stock_symbol = "REE" if "REE" in stock_symbols_list else stock_symbols_list[0]
                st.rerun()
        
        # Quick navigation to analysis pages
        st.markdown("### 🚀 Quick Navigation")
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
    
    # Instructions and app information
    st.markdown("---")
    st.markdown("### 📋 How to Use Finance Bro")
    
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
    st.markdown(
        """
        <div style='text-align: center; color: #666; padding: 1rem;'>
            <p>🚀 <strong>Finance Bro</strong> - AI Stock Analysis for Vietnamese Market</p>
            <p>Built with <a href="https://streamlit.io" target="_blank">Streamlit</a>, <a href="https://pandas-ai.com" target="_blank">PandasAI</a>, and <a href="https://github.com/thinh-vu/vnstock" target="_blank">Vnstock</a></p>
        </div>
        """,
        unsafe_allow_html=True
    )

# Define pages using st.Page
pages = {
    "Home": [
        st.Page(main_page, title="📈 Finance Bro", icon="🏠"),
    ],
    "Analysis": [
        st.Page("pages/bro.py", title="Stock Analysis", icon="📊"),
        st.Page("pages/Stock_Price_Analysis.py", title="Price Analysis", icon="📈"),
        st.Page("pages/Company_Overview.py", title="Company Overview", icon="🏢"),
        st.Page("pages/Portfolio_Optimization.py", title="Portfolio Optimization", icon="💼"),
        st.Page("pages/Screener.py", title="Stock Screener", icon="🔍"),
    ]
}

# Sidebar for user controls
with st.sidebar:
    st.header("🔧 Controls")
    
    # Show current stock symbol if available
    if 'stock_symbol' in st.session_state:
        st.success(f"📊 Current Symbol: **{st.session_state.stock_symbol}**")
    else:
        st.warning("⚠️ No symbol selected")
    
    st.markdown("---")
    
    # User logout option
    if st.button("🚪 Logout", use_container_width=True):
        st.logout()
    
    # GitHub link
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; padding: 0.25rem 0;'>
            <a href="https://github.com/gahoccode/finance-bro" target="_blank" style="text-decoration: none; display: flex; flex-direction: column; align-items: center; gap: 0.25rem;">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="vertical-align: middle;">
                    <circle cx="12" cy="12" r="9" stroke="#0366d6" stroke-width="1" fill="none"/>
                    <path d="M12 2C6.477 2 2 6.477 2 12C2 16.418 4.865 20.166 8.839 21.489C9.339 21.582 9.521 21.291 9.521 21.042C9.521 20.82 9.512 20.192 9.508 19.391C6.726 19.924 6.139 17.955 6.139 17.955C5.685 16.812 5.029 16.523 5.029 16.523C4.121 15.938 5.097 15.951 5.097 15.951C6.101 16.023 6.629 16.927 6.629 16.927C7.521 18.445 8.97 17.988 9.546 17.749C9.642 17.131 9.889 16.696 10.167 16.419C7.945 16.137 5.615 15.276 5.615 11.469C5.615 10.365 6.003 9.463 6.649 8.761C6.543 8.48 6.207 7.479 6.749 6.124C6.749 6.124 7.586 5.869 9.499 7.159C10.329 6.921 11.179 6.802 12.029 6.798C12.879 6.802 13.729 6.921 14.559 7.159C16.472 5.869 17.309 6.124 17.309 6.124C17.851 7.479 17.515 8.48 17.409 8.761C18.055 9.463 18.443 10.365 18.443 11.469C18.443 15.286 16.111 16.134 13.883 16.408C14.223 16.748 14.523 17.42 14.523 18.438C14.523 19.849 14.509 20.985 14.509 21.42C14.509 21.769 14.679 22.149 15.179 22.041C19.142 20.709 22 16.972 22 12C22 6.477 17.523 2 12 2Z" fill="#000000"/>
                </svg>
                <div style='font-size: 0.8rem; color: #000000; font-weight: 600; line-height: 1;'>Finance Bro</div>
                <div style='font-size: 0.7rem; color: #000000; line-height: 1;'>by Tam Le</div>
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )

# Set up navigation at the top
pg = st.navigation(pages, position="top")

# Run the selected page
pg.run()