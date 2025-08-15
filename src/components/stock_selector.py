"""
Stock symbol selector component for Finance Bro application.
Provides reusable stock selection UI that integrates with session state.

CRITICAL: All session state variables remain exactly the same.
This component works WITH existing session state patterns.
"""
import streamlit as st
from typing import List, Optional, Dict, Any

from ..utils.session_utils import get_stock_symbol, get_symbols_list
from ..utils.validation import validate_stock_symbol
from ..core.config import DEFAULT_STOCK_SYMBOLS
from .ui_components import inject_custom_success_styling


def render_stock_selector(
    symbols_list: Optional[List[str]] = None,
    key: str = "stock_selector",
    help_text: str = "Search and select one stock symbol to analyze"
) -> str:
    """
    Render stock symbol selector component.
    
    PRESERVES ALL SESSION STATE VARIABLES:
    - st.session_state.stock_symbol (unchanged)
    - st.session_state.stock_symbols_list (unchanged)
    
    Args:
        symbols_list: Optional list of symbols (uses session state if not provided)
        key: Unique key for the selectbox component
        help_text: Help text for the selector
        
    Returns:
        Selected stock symbol
    """
    # Use provided symbols list or get from session state
    if symbols_list is None:
        symbols_list = get_symbols_list()
    
    current_symbol = get_stock_symbol()
    
    # Determine default index
    default_index = 0
    if current_symbol and current_symbol in symbols_list:
        default_index = symbols_list.index(current_symbol)
    elif "REE" in symbols_list:
        default_index = symbols_list.index("REE")
    
    # Render the selector
    selected_symbol = st.selectbox(
        "Search and select a stock symbol:",
        options=symbols_list,
        index=default_index,
        placeholder="Type to search for stock symbols...",
        help=help_text,
        key=key
    )
    
    return selected_symbol


def render_stock_status_display(show_navigation_buttons: bool = True) -> None:
    """
    Render current stock selection status display.
    
    PRESERVES ALL SESSION STATE VARIABLES:
    - st.session_state.stock_symbol (read-only access)
    
    Args:
        show_navigation_buttons: Whether to show quick navigation buttons
    """
    current_symbol = get_stock_symbol()
    
    if current_symbol:
        st.markdown("---")
        st.markdown("### 📈 Current Selection")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Selected Symbol", current_symbol)
        with col2:
            st.metric("Status", "✅ Ready")
        with col3:
            if st.button("Clear Selection", type="secondary"):
                symbols_list = get_symbols_list()
                # Reset to default symbol instead of deleting (preserves existing logic)
                st.session_state.stock_symbol = "REE" if "REE" in symbols_list else symbols_list[0]
                st.rerun()
        
        if show_navigation_buttons:
            render_navigation_buttons()


def render_navigation_buttons() -> None:
    """
    Render quick navigation buttons to analysis pages.
    Uses existing page navigation patterns.
    """
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
    
    with col2:
        if st.button("📊 Technical Analysis", use_container_width=True):
            st.switch_page("pages/Technical_Analysis.py")


def handle_stock_selection(selected_symbol: str) -> None:
    """
    Handle stock symbol selection logic.
    
    PRESERVES ALL SESSION STATE VARIABLES:
    - st.session_state.stock_symbol (updated using existing pattern)
    
    Args:
        selected_symbol: The newly selected symbol
    """
    if selected_symbol:
        # Apply custom CSS styling for success alerts
        inject_custom_success_styling()
        
        # Use exact same logic as existing code
        if 'stock_symbol' not in st.session_state or st.session_state.stock_symbol != selected_symbol:
            st.session_state.stock_symbol = selected_symbol
            st.success(f"✅ Selected stock symbol: **{selected_symbol}**")
            st.info("📊 You can now navigate to other pages to analyze this stock!")
            st.rerun()  # Force immediate rerun to update sidebar


def render_symbol_validation(symbol: str, available_symbols: List[str]) -> bool:
    """
    Render validation feedback for stock symbol selection.
    
    Args:
        symbol: Symbol to validate
        available_symbols: List of available symbols
        
    Returns:
        True if valid, False otherwise
    """
    # Apply custom CSS styling for success alerts
    inject_custom_success_styling()
    
    validation_result = validate_stock_symbol(symbol, available_symbols)
    
    if validation_result["valid"]:
        st.success(validation_result["message"])
        return True
    else:
        st.error(validation_result["message"])
        return False


def render_compact_stock_selector(
    symbols_list: Optional[List[str]] = None,
    key: str = "compact_stock_selector"
) -> str:
    """
    Render compact stock selector for sidebar or limited space.
    
    PRESERVES ALL SESSION STATE VARIABLES:
    - st.session_state.stock_symbol (unchanged)
    
    Args:
        symbols_list: Optional list of symbols
        key: Unique key for the component
        
    Returns:
        Selected stock symbol
    """
    if symbols_list is None:
        symbols_list = get_symbols_list()
    
    current_symbol = get_stock_symbol()
    
    # Show current selection
    if current_symbol:
        st.metric("Current Symbol", current_symbol)
    
    # Compact selector
    selected_symbol = st.selectbox(
        "Select Symbol:",
        options=symbols_list,
        index=symbols_list.index(current_symbol) if current_symbol and current_symbol in symbols_list else 0,
        key=key
    )
    
    return selected_symbol


def render_stock_info_card(symbol: str) -> None:
    """
    Render information card for selected stock.
    
    Args:
        symbol: Stock symbol to display info for
    """
    # Import here to avoid circular imports
    from ..utils.session_utils import get_company_name_from_symbol
    
    company_name = get_company_name_from_symbol(symbol)
    
    with st.expander(f"📈 {symbol} - Stock Information", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Symbol:** {symbol}")
            st.write(f"**Company:** {company_name}")
        
        with col2:
            st.write("**Exchange:** HOSE/HNX/UPCOM")
            st.write("**Market:** Vietnamese Stock Market")


def render_multi_symbol_selector(
    max_selections: int = 10,
    min_selections: int = 1,
    key: str = "multi_symbol_selector",
    default_symbols: Optional[List[str]] = None,
    preserve_session_state: bool = True
) -> List[str]:
    """
    Render multi-symbol selector for portfolio construction.
    
    PRESERVES EXISTING PATTERNS:
    - Uses st.multiselect exactly as in existing pages
    - Supports both default selection and session state integration
    - Maintains all validation patterns from Portfolio Optimization page
    
    Args:
        max_selections: Maximum number of symbols to select
        min_selections: Minimum number of symbols to select  
        key: Unique key for the component
        default_symbols: Optional list of default symbols (uses current symbol if None)
        preserve_session_state: Whether to integrate with current stock selection
        
    Returns:
        List of selected symbols
    """
    symbols_list = get_symbols_list()
    current_symbol = get_stock_symbol()
    
    # Determine default selection
    if default_symbols is not None:
        default_selection = [s for s in default_symbols if s in symbols_list]
    elif preserve_session_state and current_symbol:
        default_selection = [current_symbol]
    else:
        default_selection = ["REE"] if "REE" in symbols_list else [symbols_list[0]]
    
    # Ensure default selection is valid
    default_selection = [s for s in default_selection if s in symbols_list]
    
    selected_symbols = st.multiselect(
        f"Select {min_selections}-{max_selections} stock symbols:",
        options=symbols_list,
        default=default_selection,
        max_selections=max_selections,
        help=f"Select between {min_selections} and {max_selections} symbols for analysis",
        key=key
    )
    
    # Validation feedback (matching existing patterns)
    # Apply custom CSS styling for success alerts
    inject_custom_success_styling()
    
    if len(selected_symbols) < min_selections:
        st.warning(f"Please select at least {min_selections} symbol(s)")
    elif len(selected_symbols) > max_selections:
        st.warning(f"Please select at most {max_selections} symbols")
    else:
        st.success(f"Selected {len(selected_symbols)} symbol(s)")
    
    return selected_symbols


def render_portfolio_symbol_selector(
    selected_symbols: Optional[List[str]] = None,
    key: str = "portfolio_symbols"
) -> List[str]:
    """
    Render symbol selector specifically for portfolio optimization.
    Matches the EXACT pattern from Portfolio_Optimization.py.
    
    PRESERVES EXISTING PATTERNS:
    - st.session_state.stock_symbol integration
    - st.session_state.stock_symbols_list usage
    - Exact multiselect configuration from existing page
    
    Args:
        selected_symbols: Optional pre-selected symbols
        key: Unique key for the component
        
    Returns:
        List of selected symbols
    """
    # Get data from session state (preserving existing pattern)
    main_stock_symbol = None
    if 'stock_symbol' in st.session_state and st.session_state.stock_symbol:
        main_stock_symbol = st.session_state.stock_symbol
    
    stock_symbols_list = []
    if 'stock_symbols_list' in st.session_state:
        stock_symbols_list = st.session_state.stock_symbols_list
    else:
        # Fallback to default symbols
        stock_symbols_list = DEFAULT_STOCK_SYMBOLS
    
    # Default selection logic (matching Portfolio_Optimization.py)
    if selected_symbols is not None:
        default_selection = selected_symbols
    else:
        default_selection = [main_stock_symbol] if main_stock_symbol else ["REE"]
    
    # Filter valid symbols
    default_selection = [s for s in default_selection if s in stock_symbols_list]
    
    # Render multiselect (matching exact pattern from Portfolio_Optimization.py)
    selected_symbols = st.multiselect(
        "Select stock symbols for portfolio:",
        options=stock_symbols_list,
        default=default_selection,
        max_selections=10,
        help="Select 2-10 stock symbols to build your portfolio",
        key=key
    )
    
    return selected_symbols