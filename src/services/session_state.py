"""
Session State Management Service

Centralized session state initialization and smart dependency resolution.
Provides intelligent data loading with progress feedback and cache management.
"""

import streamlit as st
import pandas as pd
from typing import Optional, Dict, Any
import warnings

from .financial_data import (
    load_comprehensive_financial_data,
    get_stock_symbols_with_names,
    get_company_name_from_symbol,
    validate_financial_data,
)

warnings.filterwarnings("ignore")


def init_global_session_state():
    """
    Initialize global session state variables with default values.

    Sets up core application state that should be available across all pages.
    This function is safe to call multiple times.
    """
    # Core navigation variables
    if "stock_symbol" not in st.session_state:
        st.session_state.stock_symbol = None

    # Date range management (shared across analysis pages)
    if "analysis_start_date" not in st.session_state:
        st.session_state.analysis_start_date = pd.to_datetime("2024-01-01")

    if "analysis_end_date" not in st.session_state:
        st.session_state.analysis_end_date = pd.to_datetime("today") - pd.Timedelta(
            days=1
        )

    if "date_range_changed" not in st.session_state:
        st.session_state.date_range_changed = False

    # API key management
    if "api_key" not in st.session_state:
        import os

        st.session_state.api_key = os.environ.get("OPENAI_API_KEY", "")


def ensure_stock_symbols_loaded() -> Dict[str, Any]:
    """
    Ensure stock symbols are loaded and cached in session state.

    Returns:
        dict: Symbol data with validation info
    """
    if (
        "stock_symbols_list" not in st.session_state
        or "symbols_df" not in st.session_state
    ):
        with st.spinner("Loading stock symbols..."):
            symbols_data = get_stock_symbols_with_names()
            st.session_state.stock_symbols_list = symbols_data["symbols_list"]
            st.session_state.symbols_df = symbols_data["symbols_df"]

            # Show success message only once
            if "symbols_loaded_message_shown" not in st.session_state:
                st.success("✅ Stock symbols loaded and cached!")
                st.session_state.symbols_loaded_message_shown = True

            return symbols_data

    # Return cached data
    return {
        "symbols_list": st.session_state.stock_symbols_list,
        "symbols_df": st.session_state.symbols_df,
        "loaded_at": "cached",
    }


def ensure_financial_data_loaded(
    symbol: str,
    period: str = "year",
    source: str = "VCI",
    company_source: str = "TCBS",
    force_reload: bool = False,
) -> Dict[str, Any]:
    """
    Ensure financial data is loaded for the specified symbol and parameters.

    Args:
        symbol (str): Stock symbol
        period (str): 'year' or 'quarter'
        source (str): Data source for financial statements
        company_source (str): Data source for company info
        force_reload (bool): Force reload even if data exists

    Returns:
        dict: Financial data with validation info
    """
    # Create cache key based on parameters
    cache_key = f"{symbol}_{period}_{source}_{company_source}"

    # Check if data needs loading
    needs_loading = (
        force_reload
        or "dataframes" not in st.session_state
        or "display_dataframes" not in st.session_state
        or st.session_state.get("financial_data_cache_key") != cache_key
    )

    if needs_loading:
        with st.spinner(f"Loading financial data for {symbol}..."):
            financial_data = load_comprehensive_financial_data(
                symbol, period, source, company_source
            )

            if financial_data["dataframes"]:  # Success
                # Store in session state with cache key
                st.session_state.dataframes = financial_data["dataframes"]
                st.session_state.display_dataframes = financial_data[
                    "display_dataframes"
                ]
                st.session_state.financial_data_metadata = financial_data["metadata"]
                st.session_state.financial_data_cache_key = cache_key
                st.session_state.stock_symbol = symbol  # Ensure symbol is set

                # Validate data
                validation = validate_financial_data(financial_data["dataframes"])

                if validation["is_valid"]:
                    st.success(f"✅ Financial data loaded for {symbol}")
                else:
                    for error in validation["errors"]:
                        st.error(f"❌ {error}")

                return {
                    "success": True,
                    "data": financial_data,
                    "validation": validation,
                }
            else:
                error_msg = financial_data["metadata"].get("error", "Unknown error")
                st.error(f"❌ Failed to load financial data: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "validation": {"is_valid": False},
                }

    # Return cached data
    return {
        "success": True,
        "data": {
            "dataframes": st.session_state.dataframes,
            "display_dataframes": st.session_state.display_dataframes,
            "metadata": st.session_state.get("financial_data_metadata", {}),
        },
        "validation": {"is_valid": True},
        "cached": True,
    }


def ensure_valuation_data_loaded(
    symbol: str,
    start_date: Optional[pd.Timestamp] = None,
    end_date: Optional[pd.Timestamp] = None,
    force_reload: bool = False,
) -> Dict[str, Any]:
    """
    Ensure all data required for valuation analysis is loaded.

    This is the main function for the valuation page to get all required data
    without depending on other pages being visited first.

    Args:
        symbol (str): Stock symbol
        start_date (pd.Timestamp, optional): Start date for price data
        end_date (pd.Timestamp, optional): End date for price data
        force_reload (bool): Force reload even if data exists

    Returns:
        dict: Complete valuation data package
    """
    # Use session state dates if not provided
    if start_date is None:
        start_date = st.session_state.get(
            "analysis_start_date", pd.to_datetime("2024-01-01")
        )
    if end_date is None:
        end_date = st.session_state.get(
            "analysis_end_date", pd.to_datetime("today") - pd.Timedelta(days=1)
        )

    # Progressive loading with UI feedback
    progress_container = st.container()

    with progress_container:
        progress_bar = st.progress(0)
        status_text = st.empty()

        result = {"success": True, "components": {}}

        try:
            # Step 1: Load financial data (60% of progress)
            status_text.text("Loading financial statements...")
            financial_result = ensure_financial_data_loaded(
                symbol, force_reload=force_reload
            )
            progress_bar.progress(0.6)

            if not financial_result["success"]:
                return financial_result

            result["components"]["financial"] = financial_result

            # Step 2: Load price data and returns (40% of progress)
            status_text.text("Loading price data and calculating returns...")

            # Load price data using existing service
            from .vnstock_api import fetch_stock_price_data

            try:
                price_data = fetch_stock_price_data(symbol, start_date, end_date)

                # Calculate returns and store in session state
                if not price_data.empty and "close" in price_data.columns:
                    clean_prices = price_data["close"].dropna()
                    clean_prices = clean_prices[clean_prices > 0]

                    if len(clean_prices) > 1:
                        returns = clean_prices.pct_change().dropna()
                        st.session_state.stock_returns = returns
                        st.session_state.stock_price_data = price_data

                        result["components"]["price"] = {
                            "success": True,
                            "data": price_data,
                            "returns": returns,
                        }
                    else:
                        result["components"]["price"] = {
                            "success": False,
                            "error": "Insufficient price data",
                        }
                else:
                    result["components"]["price"] = {
                        "success": False,
                        "error": "No price data available",
                    }
            except Exception as e:
                st.warning(f"⚠️ Could not load price data: {str(e)}")
                result["components"]["price"] = {
                    "success": False,
                    "error": str(e),
                }

            progress_bar.progress(1.0)
            status_text.text("✅ Data loading complete!")

            # Clear progress indicators after a short delay
            import time

            time.sleep(1)
            progress_container.empty()

            return result

        except Exception as e:
            progress_container.empty()
            st.error(f"❌ Error during data loading: {str(e)}")
            return {
                "success": False,
                "error": str(e),
            }


def clear_financial_data_cache():
    """Clear cached financial data to force reload."""
    keys_to_remove = [
        "dataframes",
        "display_dataframes",
        "financial_data_metadata",
        "financial_data_cache_key",
        "stock_price_data",
        "stock_returns",
    ]

    for key in keys_to_remove:
        if key in st.session_state:
            del st.session_state[key]


def get_current_company_name() -> str:
    """
    Get the current company name based on selected symbol.

    Returns:
        str: Company name or symbol if not available
    """
    symbol = st.session_state.get("stock_symbol")
    if not symbol:
        return "No stock selected"

    symbols_df = st.session_state.get("symbols_df")
    return get_company_name_from_symbol(symbol, symbols_df)


def validate_valuation_prerequisites() -> Dict[str, Any]:
    """
    Validate that all prerequisites for valuation analysis are met.

    Returns:
        dict: Validation results with specific checks
    """
    validation = {
        "is_ready": True,
        "checks": {},
        "missing": [],
        "warnings": [],
    }

    # Check 1: Stock symbol selected
    symbol = st.session_state.get("stock_symbol")
    validation["checks"]["symbol_selected"] = bool(symbol)
    if not symbol:
        validation["missing"].append("Stock symbol not selected")
        validation["is_ready"] = False

    # Check 2: Financial data available
    has_financial_data = (
        "dataframes" in st.session_state
        and st.session_state.dataframes
        and any(not df.empty for df in st.session_state.dataframes.values())
    )
    validation["checks"]["financial_data"] = has_financial_data
    if not has_financial_data:
        validation["missing"].append("Financial statements not loaded")
        validation["is_ready"] = False

    # Check 3: Price data available (optional but recommended)
    has_price_data = (
        "stock_price_data" in st.session_state
        and not st.session_state.stock_price_data.empty
    )
    validation["checks"]["price_data"] = has_price_data
    if not has_price_data:
        validation["warnings"].append(
            "Price data not available - some calculations may be limited"
        )

    # Check 4: Returns data for beta calculation
    has_returns = (
        "stock_returns" in st.session_state and len(st.session_state.stock_returns) > 0
    )
    validation["checks"]["returns_data"] = has_returns
    if not has_returns:
        validation["warnings"].append(
            "Returns data not available - beta calculation may be limited"
        )

    return validation


def smart_load_for_page(page_name: str, symbol: str = None) -> Dict[str, Any]:
    """
    Smart data loading based on page requirements.

    Args:
        page_name (str): Name of the page ('valuation', 'analysis', 'portfolio', etc.)
        symbol (str, optional): Stock symbol to load data for

    Returns:
        dict: Loading results
    """
    # Initialize global state
    init_global_session_state()

    # Use symbol from session state if not provided
    if symbol is None:
        symbol = st.session_state.get("stock_symbol")

    if not symbol:
        return {
            "success": False,
            "error": "No stock symbol available",
        }

    # Load symbols if needed
    ensure_stock_symbols_loaded()

    # Page-specific loading
    if page_name == "valuation":
        return ensure_valuation_data_loaded(symbol)
    elif page_name == "analysis":
        return ensure_financial_data_loaded(symbol)
    elif page_name in ["portfolio", "price_analysis"]:
        # These pages primarily need price data
        financial_result = ensure_financial_data_loaded(symbol)
        return financial_result
    else:
        # Default: load financial data
        return ensure_financial_data_loaded(symbol)
