"""
Session state utility functions for Finance Bro application.
These are HELPER functions that work WITH existing session state patterns,
not replacements for direct st.session_state access.

CRITICAL: All session state variables remain exactly the same.
These utilities just provide convenient helpers for common patterns.
"""

from datetime import datetime
from typing import Any, Dict, List, Tuple

import pandas as pd
import streamlit as st

from ..core.config import DEFAULT_ANALYSIS_START_DATE, DEFAULT_STOCK_SYMBOLS


def get_stock_symbol() -> str | None:
    """
    Helper to get current stock symbol from session state.
    Does NOT replace direct st.session_state.stock_symbol access.
    """
    return st.session_state.get("stock_symbol")


def has_stock_symbol() -> bool:
    """Helper to check if stock symbol is set and not empty."""
    return "stock_symbol" in st.session_state and st.session_state.stock_symbol


def get_symbols_list() -> List[str]:
    """
    Helper to get stock symbols list with fallback.
    Does NOT replace direct st.session_state.stock_symbols_list access.
    """
    return st.session_state.get("stock_symbols_list", DEFAULT_STOCK_SYMBOLS)


def get_symbols_dataframe() -> pd.DataFrame | None:
    """
    Helper to get symbols DataFrame.
    Does NOT replace direct st.session_state.symbols_df access.
    """
    return st.session_state.get("symbols_df")


def get_company_name_from_symbol(symbol: str) -> str:
    """
    Get company name from symbol using cached symbols DataFrame.
    Falls back to symbol if name not found.
    """
    symbols_df = get_symbols_dataframe()
    if symbols_df is not None:
        try:
            matching_company = symbols_df[symbols_df["symbol"] == symbol]
            if not matching_company.empty and "organ_name" in symbols_df.columns:
                return matching_company["organ_name"].iloc[0]
        except Exception:
            pass
    return symbol


def get_analysis_dates() -> Tuple[datetime, datetime]:
    """
    Helper to get analysis date range from session state.
    Does NOT replace direct st.session_state access.
    """
    start_date = st.session_state.get(
        "analysis_start_date", pd.to_datetime(DEFAULT_ANALYSIS_START_DATE)
    )
    end_date = st.session_state.get(
        "analysis_end_date", pd.to_datetime("today") - pd.Timedelta(days=1)
    )
    return start_date, end_date


def has_date_range_changed() -> bool:
    """Helper to check if date range has changed."""
    return st.session_state.get("date_range_changed", False)


def get_api_key() -> str | None:
    """
    Helper to get API key from session state.
    Does NOT replace direct st.session_state.api_key access.
    """
    return st.session_state.get("api_key")


def has_api_key() -> bool:
    """Helper to check if API key is set and not empty."""
    api_key = get_api_key()
    return api_key is not None and len(api_key.strip()) > 0


def get_chat_messages() -> List[Dict[str, Any]]:
    """
    Helper to get chat messages from session state.
    Does NOT replace direct st.session_state.messages access.
    """
    return st.session_state.get("messages", [])


def has_dataframes() -> bool:
    """Helper to check if financial dataframes are loaded."""
    return "dataframes" in st.session_state


def get_portfolio_returns() -> pd.DataFrame | None:
    """
    Helper to get portfolio returns from session state.
    Does NOT replace direct st.session_state.portfolio_returns access.
    """
    return st.session_state.get("portfolio_returns")


def has_portfolio_data() -> bool:
    """Helper to check if portfolio optimization data is available."""
    return "portfolio_returns" in st.session_state


def get_portfolio_strategy_choice() -> str | None:
    """
    Helper to get portfolio strategy choice.
    Does NOT replace direct st.session_state.portfolio_strategy_choice access.
    """
    return st.session_state.get("portfolio_strategy_choice")


def get_screener_preset_value(preset_name: str, default_value: Any = False) -> Any:
    """
    Helper to get screener preset value.
    Does NOT replace direct st.session_state.get() calls.
    """
    return st.session_state.get(f"preset_{preset_name}", default_value)


def has_screener_data() -> bool:
    """Helper to check if screener data is available."""
    return (
        "screener_data" in st.session_state
        and not st.session_state["screener_data"].empty
    )


def should_auto_run_screener() -> bool:
    """Helper to check if screener should auto-run."""
    return st.session_state.get("auto_run_screener", False)


def get_technical_interval() -> str:
    """
    Helper to get technical analysis interval.
    Does NOT replace direct st.session_state.ta_interval access.
    """
    return st.session_state.get("ta_interval", "1D")


def has_stock_price_data() -> bool:
    """Helper to check if stock price data is cached."""
    return "stock_price_data" in st.session_state


def has_stock_returns() -> bool:
    """Helper to check if stock returns data is available."""
    return (
        "stock_returns" in st.session_state and len(st.session_state.stock_returns) > 0
    )


# Validation helpers
def validate_date_range(start_date: datetime, end_date: datetime) -> bool:
    """Validate that start date is before end date."""
    return start_date < end_date


def validate_stock_symbol(symbol: str, available_symbols: List[str]) -> bool:
    """Validate that stock symbol is in available symbols list."""
    return symbol in available_symbols


def validate_api_key(api_key: str) -> bool:
    """Validate OpenAI API key format."""
    return api_key.startswith("sk-") and len(api_key) > 10


# Status display helpers
def format_stock_status() -> Dict[str, str]:
    """Format current stock selection status for display."""
    symbol = get_stock_symbol()
    if symbol:
        return {
            "symbol": symbol,
            "company_name": get_company_name_from_symbol(symbol),
            "status": "✅ Ready",
        }
    else:
        return {
            "symbol": "None",
            "company_name": "Please select a stock",
            "status": "⚠️ Not selected",
        }


def format_date_range_status() -> Dict[str, str]:
    """Format current date range for display."""
    start_date, end_date = get_analysis_dates()
    return {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "range": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
    }


def format_data_status() -> Dict[str, str]:
    """Format current data availability status for display."""
    status = {
        "stock_data": "✅ Loaded" if has_stock_price_data() else "❌ Not loaded",
        "portfolio_data": "✅ Loaded" if has_portfolio_data() else "❌ Not loaded",
        "screener_data": "✅ Loaded" if has_screener_data() else "❌ Not loaded",
        "financial_data": "✅ Loaded" if has_dataframes() else "❌ Not loaded",
    }
    return status
