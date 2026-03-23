"""
VnStock API Module

Extracted cached data functions from existing pages.
PRESERVES ALL @st.cache_data decorators and vnstock API instantiation patterns exactly as they exist.
"""

import streamlit as st
import pandas as pd
from vnstock import Vnstock, Company, Quote


# ================================
# COMPANY DATA FUNCTIONS
# Extracted from Company_Overview.py
# ================================


@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_ownership_data(symbol):
    """Get ownership data with caching

    Extracted from Company_Overview.py lines 10-18 - EXACT same logic preserved.
    """
    try:
        stock = Vnstock().stock(symbol=symbol, source="VCI")
        company_info = stock.company
        return company_info.shareholders()
    except Exception as e:
        st.error(f"Error fetching ownership data: {str(e)}")
        return pd.DataFrame()


@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_management_data(symbol):
    """Get management data with caching

    Extracted from Company_Overview.py lines 21-28 - EXACT same logic preserved.
    Uses VCI source for consistent column names (quantity, officer_own_percent).
    """
    try:
        company = Company(symbol=symbol, source="VCI")
        return company.officers()
    except Exception as e:
        st.error(f"Error fetching management data: {str(e)}")
        return pd.DataFrame()


@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_subsidiaries_data(symbol):
    """Get subsidiaries data with caching

    Extracted from Company_Overview.py lines 31-38 - EXACT same logic preserved.
    """
    try:
        company = Company(symbol=symbol, source="VCI")
        return company.subsidiaries()
    except Exception as e:
        st.error(f"Error fetching subsidiaries data: {str(e)}")
        return pd.DataFrame()


@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_insider_deals_data(symbol):
    """Get insider deals data with caching

    Note: insider_deals() is not available from VCI source.
    Returns empty DataFrame with info message.
    """
    st.info(
        "Insider deals data is not available from VCI source. TCBS source (which has this data) is deprecated."
    )
    return pd.DataFrame()


@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_foreign_trading_data(symbol):
    """Get foreign trading data with caching

    Extracted from Company_Overview.py lines 51-58 - EXACT same logic preserved.
    """
    try:
        company = Company(symbol=symbol, source="VCI")
        return company.trading_stats()
    except Exception as e:
        st.error(f"Error fetching foreign trading data: {str(e)}")
        return pd.DataFrame()


# ================================
# STOCK PRICE DATA FUNCTIONS
# ================================


@st.cache_data(ttl=3600, show_spinner="Loading stock data...")
def fetch_stock_price_data(ticker, start_date, end_date):
    """Fetch stock data with caching to prevent repeated API calls.

    Extracted from Stock_Price_Analysis.py lines 247-264 - EXACT same logic preserved.
    PRESERVES session state assignment for cross-page access.
    """
    stock_quote = Quote(symbol=ticker, source="VCI")
    stock_price = stock_quote.history(
        start=start_date.strftime("%Y-%m-%d"),
        end=end_date.strftime("%Y-%m-%d"),
        interval="1D",
    )

    # Set time column as datetime index
    stock_price["time"] = pd.to_datetime(stock_price["time"])
    stock_price = stock_price.set_index("time")

    # Store in session state for cross-page access
    st.session_state.stock_price_data = stock_price

    return stock_price


@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_portfolio_stock_data(symbols, start_date_str, end_date_str, interval):
    """Cache stock data to avoid repeated API calls.

    Extracted from Portfolio_Optimization.py lines 140-164 - EXACT same logic preserved.
    """
    all_data = {}

    for symbol in symbols:
        try:
            quote = Quote(symbol=symbol)
            historical_data = quote.history(
                start=start_date_str, end=end_date_str, interval=interval, to_df=True
            )

            if not historical_data.empty:
                # Ensure we have the required columns
                if "time" not in historical_data.columns:
                    historical_data["time"] = historical_data.index

                all_data[symbol] = historical_data
        except Exception as e:
            st.error(f"Error fetching data for {symbol}: {e}")

    return all_data


# ================================
# UTILITY FUNCTIONS
# ================================


def clear_vnstock_cache():
    """Clear all vnstock-related cache.

    Convenience function to clear all cached API data.
    """
    st.cache_data.clear()


def get_cache_info():
    """Get information about cached functions.

    Returns metadata about the cached vnstock functions.
    """
    cached_functions = {
        "Company Data": [
            "get_ownership_data (1h TTL)",
            "get_management_data (1h TTL)",
            "get_subsidiaries_data (1h TTL)",
            "get_insider_deals_data (1h TTL)",
            "get_foreign_trading_data (1h TTL)",
        ],
        "Stock Price Data": [
            "fetch_stock_price_data (1h TTL)",
            "fetch_portfolio_stock_data (1h TTL)",
        ],
    }

    return cached_functions
