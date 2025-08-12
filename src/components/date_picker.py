"""
Date range picker component for Finance Bro application.
Provides reusable date selection UI that integrates with session state.

CRITICAL: All session state variables remain exactly the same.
This component works WITH existing session state patterns.
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Tuple, Optional

from ..utils.session_utils import get_analysis_dates, has_date_range_changed
from ..utils.validation import validate_date_range
from ..core.config import DEFAULT_ANALYSIS_START_DATE


def render_date_range_picker(
    key_prefix: str = "analysis",
    show_validation: bool = True,
    label: str = "Analysis Date Range"
) -> Tuple[datetime, datetime]:
    """
    Render date range picker component.
    
    PRESERVES ALL SESSION STATE VARIABLES:
    - st.session_state.analysis_start_date (unchanged)
    - st.session_state.analysis_end_date (unchanged)
    - st.session_state.date_range_changed (unchanged)
    
    Args:
        key_prefix: Prefix for component keys (e.g., "analysis", "portfolio")
        show_validation: Whether to show validation feedback
        label: Label for the date range section
        
    Returns:
        Tuple of (start_date, end_date)
    """
    st.subheader(label)
    
    # Initialize session state if not exists (preserving existing pattern)
    if f'{key_prefix}_start_date' not in st.session_state:
        st.session_state[f'{key_prefix}_start_date'] = pd.to_datetime(DEFAULT_ANALYSIS_START_DATE)
    
    if f'{key_prefix}_end_date' not in st.session_state:
        st.session_state[f'{key_prefix}_end_date'] = pd.to_datetime("today") - pd.Timedelta(days=1)
    
    if f'{key_prefix}_date_range_changed' not in st.session_state:
        st.session_state[f'{key_prefix}_date_range_changed'] = False
    
    # Date input columns
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input(
            "Start Date:",
            value=st.session_state[f'{key_prefix}_start_date'],
            key=f"{key_prefix}_start_input"
        )
    
    with col2:
        end_date = st.date_input(
            "End Date:",
            value=st.session_state[f'{key_prefix}_end_date'],
            key=f"{key_prefix}_end_input"
        )
    
    # Convert to datetime for consistency
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    
    # Check for changes and update session state (preserving existing pattern)
    if (start_date != st.session_state[f'{key_prefix}_start_date'] or 
        end_date != st.session_state[f'{key_prefix}_end_date']):
        st.session_state[f'{key_prefix}_start_date'] = start_date
        st.session_state[f'{key_prefix}_end_date'] = end_date
        st.session_state[f'{key_prefix}_date_range_changed'] = True
    
    # Validation
    if show_validation:
        render_date_validation(start_date, end_date)
    
    return start_date, end_date


def render_date_validation(start_date: datetime, end_date: datetime) -> bool:
    """
    Render validation feedback for date range.
    
    Args:
        start_date: Start date to validate
        end_date: End date to validate
        
    Returns:
        True if valid, False otherwise
    """
    validation_result = validate_date_range(start_date, end_date)
    
    if validation_result["valid"]:
        st.success(f"✅ {validation_result['message']}")
        return True
    else:
        st.error(f"❌ {validation_result['message']}")
        return False


def render_date_range_status(
    key_prefix: str = "analysis",
    show_details: bool = True
) -> None:
    """
    Render current date range status display.
    
    Args:
        key_prefix: Prefix for session state keys
        show_details: Whether to show detailed information
    """
    start_date = st.session_state.get(f'{key_prefix}_start_date')
    end_date = st.session_state.get(f'{key_prefix}_end_date')
    
    if start_date and end_date:
        if show_details:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Start Date", start_date.strftime('%Y-%m-%d'))
            
            with col2:
                st.metric("End Date", end_date.strftime('%Y-%m-%d'))
            
            with col3:
                days = (end_date - start_date).days
                st.metric("Days", f"{days}")
        else:
            st.info(f"📅 {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")


def render_preset_date_ranges(
    key_prefix: str = "analysis",
    show_custom: bool = True
) -> None:
    """
    Render preset date range buttons.
    
    PRESERVES ALL SESSION STATE VARIABLES:
    Updates the same session state variables as manual date selection.
    
    Args:
        key_prefix: Prefix for session state keys
        show_custom: Whether to show custom range option
    """
    st.subheader("📅 Quick Date Ranges")
    
    col1, col2, col3, col4 = st.columns(4)
    
    today = pd.to_datetime("today")
    
    with col1:
        if st.button("Last Month", key=f"{key_prefix}_last_month"):
            start_date = today - pd.Timedelta(days=30)
            end_date = today - pd.Timedelta(days=1)
            _update_date_range(key_prefix, start_date, end_date)
    
    with col2:
        if st.button("Last 3 Months", key=f"{key_prefix}_last_3months"):
            start_date = today - pd.Timedelta(days=90)
            end_date = today - pd.Timedelta(days=1)
            _update_date_range(key_prefix, start_date, end_date)
    
    with col3:
        if st.button("Last 6 Months", key=f"{key_prefix}_last_6months"):
            start_date = today - pd.Timedelta(days=180)
            end_date = today - pd.Timedelta(days=1)
            _update_date_range(key_prefix, start_date, end_date)
    
    with col4:
        if st.button("Last Year", key=f"{key_prefix}_last_year"):
            start_date = today - pd.Timedelta(days=365)
            end_date = today - pd.Timedelta(days=1)
            _update_date_range(key_prefix, start_date, end_date)
    
    # Second row for more options
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("YTD", key=f"{key_prefix}_ytd"):
            start_date = pd.to_datetime(f"{today.year}-01-01")
            end_date = today - pd.Timedelta(days=1)
            _update_date_range(key_prefix, start_date, end_date)
    
    with col2:
        if st.button("Last 2 Years", key=f"{key_prefix}_last_2years"):
            start_date = today - pd.Timedelta(days=730)
            end_date = today - pd.Timedelta(days=1)
            _update_date_range(key_prefix, start_date, end_date)
    
    with col3:
        if st.button("2024 Full Year", key=f"{key_prefix}_2024"):
            start_date = pd.to_datetime("2024-01-01")
            end_date = pd.to_datetime("2024-12-31")
            _update_date_range(key_prefix, start_date, end_date)
    
    with col4:
        if st.button("2023 Full Year", key=f"{key_prefix}_2023"):
            start_date = pd.to_datetime("2023-01-01")
            end_date = pd.to_datetime("2023-12-31")
            _update_date_range(key_prefix, start_date, end_date)


def _update_date_range(key_prefix: str, start_date: datetime, end_date: datetime) -> None:
    """
    Internal helper to update date range in session state.
    
    Args:
        key_prefix: Prefix for session state keys
        start_date: New start date
        end_date: New end date
    """
    st.session_state[f'{key_prefix}_start_date'] = start_date
    st.session_state[f'{key_prefix}_end_date'] = end_date
    st.session_state[f'{key_prefix}_date_range_changed'] = True
    st.rerun()


def render_compact_date_picker(
    key_prefix: str = "analysis",
    key: str = "compact_date"
) -> Tuple[datetime, datetime]:
    """
    Render compact date picker for sidebar or limited space.
    
    Args:
        key_prefix: Prefix for session state keys
        key: Unique key for the component
        
    Returns:
        Tuple of (start_date, end_date)
    """
    # Show current date range
    start_date, end_date = get_analysis_dates()
    
    st.write("**Date Range:**")
    st.write(f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    # Quick preset buttons in compact layout
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📅 Last Month", key=f"{key}_month", use_container_width=True):
            today = pd.to_datetime("today")
            start = today - pd.Timedelta(days=30)
            end = today - pd.Timedelta(days=1)
            _update_date_range(key_prefix, start, end)
    
    with col2:
        if st.button("📅 Last 3M", key=f"{key}_3months", use_container_width=True):
            today = pd.to_datetime("today")
            start = today - pd.Timedelta(days=90)
            end = today - pd.Timedelta(days=1)
            _update_date_range(key_prefix, start, end)
    
    return start_date, end_date


def get_date_range_summary(start_date: datetime, end_date: datetime) -> str:
    """
    Get a formatted summary of the date range.
    
    Args:
        start_date: Start date
        end_date: End date
        
    Returns:
        Formatted date range summary string
    """
    days = (end_date - start_date).days
    
    if days <= 31:
        period = "Short-term"
    elif days <= 90:
        period = "Medium-term"
    elif days <= 365:
        period = "Long-term"
    else:
        period = "Extended"
    
    return f"{period} analysis ({days} days)"


def check_weekend_adjustment(date: datetime) -> datetime:
    """
    Adjust date to avoid weekends for market data.
    
    Args:
        date: Date to check
        
    Returns:
        Adjusted date (previous Friday if weekend)
    """
    # If Saturday (5) or Sunday (6), go back to Friday
    if date.weekday() == 5:  # Saturday
        return date - timedelta(days=1)
    elif date.weekday() == 6:  # Sunday
        return date - timedelta(days=2)
    
    return date


def validate_market_hours_date(date: datetime) -> bool:
    """
    Validate that date is appropriate for market data.
    
    Args:
        date: Date to validate
        
    Returns:
        True if valid market date
    """
    # Check if it's a weekend
    if date.weekday() >= 5:  # Saturday or Sunday
        return False
    
    # Check if it's too far in the future
    today = datetime.now()
    if date > today:
        return False
    
    # Check if it's too far in the past (more than 10 years)
    ten_years_ago = today - timedelta(days=365 * 10)
    if date < ten_years_ago:
        return False
    
    return True