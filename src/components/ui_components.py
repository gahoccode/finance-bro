"""
General UI Components Module

Provides reusable UI components used across multiple pages.
All components preserve existing session state variables and patterns.
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Any, Tuple
from src.core.config import FINANCIAL_DISPLAY_OPTIONS, DEFAULT_FINANCIAL_DISPLAY


def render_performance_metrics_columns(metrics_data: List[Dict[str, Any]]) -> None:
    """Render performance metrics in columns layout.

    Used across Portfolio_Optimization.py and other performance analysis pages.
    """
    if len(metrics_data) == 3:
        col1, col2, col3 = st.columns(3)
        columns = [col1, col2, col3]
    elif len(metrics_data) == 2:
        col1, col2 = st.columns(2)
        columns = [col1, col2]
    else:
        columns = [st.columns(1)[0] for _ in metrics_data]

    for i, (col, metric) in enumerate(zip(columns, metrics_data)):
        with col:
            st.metric(
                metric.get("label", f"Metric {i + 1}"),
                metric.get("value", "N/A"),
                metric.get("delta", None),
            )


def create_financial_summary_expander(
    data: pd.DataFrame, title: str = "View Financial Data"
) -> None:
    """Create expandable financial data viewer.

    Extracted from Portfolio_Optimization.py and other financial analysis pages - EXACT same pattern.
    """
    with st.expander(title):
        view_option = st.radio(
            "Display option:",
            ["First 5 rows", "Last 5 rows"],
            horizontal=True,
            key=f"financial_data_view_{title.replace(' ', '_').lower()}",
        )

        if view_option == "First 5 rows":
            st.dataframe(data.head())
        else:
            st.dataframe(data.tail())

        st.write(f"Shape: {data.shape}")


def render_progress_indicator(progress_value: float, status_message: str) -> Tuple:
    """Render progress bar and status message.

    Extracted from Portfolio_Optimization.py - EXACT same pattern preserved.
    """
    progress_bar = st.progress(progress_value)
    status_text = st.empty()
    status_text.text(status_message)

    return progress_bar, status_text


def render_financial_display_options(
    placement: str = "sidebar",
    unique_key: str = "financial_display",
    title: str = "💰 Financial Display Options",
    help_text: str = None,
) -> str:
    """
    Render reusable financial display options selector.

    Provides a consistent interface for users to choose how financial values
    are displayed across different pages. Manages session state persistence
    and returns the selected display unit for use in formatting functions.

    Args:
        placement: Where to render ('sidebar', 'main', 'columns')
        unique_key: Unique key for session state (allows multiple instances)
        title: Title for the selector widget
        help_text: Optional help text for the selector

    Returns:
        Selected display unit key ('billions', 'millions', 'original')

    Example:
        # In page header or sidebar
        display_unit = render_financial_display_options(
            placement="sidebar",
            unique_key="dupont_display",
            title="📊 Display Format"
        )

        # Use with helper functions
        formatted_value = format_financial_display(value, display_unit)
        display_df = convert_dataframe_for_display(df, columns, display_unit)
    """
    # Initialize session state key with default
    session_key = f"{unique_key}_{DEFAULT_FINANCIAL_DISPLAY['session_key']}"

    if session_key not in st.session_state:
        st.session_state[session_key] = DEFAULT_FINANCIAL_DISPLAY["unit"]

    # Create options list from configuration
    options = []
    option_keys = []

    for config_key, config_value in FINANCIAL_DISPLAY_OPTIONS.items():
        options.append(config_value["label"])
        option_keys.append(config_value["key"])

    # Default help text if not provided
    if help_text is None:
        help_text = (
            "Choose how financial values are displayed across metrics and tables"
        )

    # Render based on placement
    if placement == "sidebar":
        with st.sidebar:
            st.markdown(f"### {title}")
            selected_option = st.selectbox(
                "Format:",
                options=options,
                index=option_keys.index(st.session_state[session_key]),
                help=help_text,
                key=f"{unique_key}_selectbox",
            )

    elif placement == "columns":
        # For use within column layouts - more compact
        selected_option = st.selectbox(
            title,
            options=options,
            index=option_keys.index(st.session_state[session_key]),
            help=help_text,
            key=f"{unique_key}_selectbox",
        )

    else:  # main
        st.markdown(f"#### {title}")
        selected_option = st.selectbox(
            "Display Format:",
            options=options,
            index=option_keys.index(st.session_state[session_key]),
            help=help_text,
            key=f"{unique_key}_selectbox",
        )

    # Update session state and return key
    selected_key = option_keys[options.index(selected_option)]
    st.session_state[session_key] = selected_key

    return selected_key


def inject_custom_success_styling():
    """
    Inject custom CSS styling for Streamlit success alerts.

    This function applies the Finance Bro earth-tone theme to all st.success() elements:
    - Background color: #D4D4D4 (light gray)
    - Text color: #56524D (earth tone)
    - Also styles markdown containers with tertiary color: #76706C

    Should be called after st.set_page_config() and before any st.success() usage.
    """
    st.html("""
<style>

/* Target success alerts - try multiple approaches */
div[data-testid="stAlert"][data-baseweb="notification"] {
    background-color: #D4D4D4 !important;
    border-color: #D4D4D4 !important;
    color: #56524D !important;
}

.stAlert {
    background-color: #D4D4D4 !important;
    border-color: #D4D4D4 !important;
    color: #56524D !important;
}

/* Success alert specific targeting */
.stSuccess, .st-success {
    background-color: #D4D4D4 !important;
    border-color: #D4D4D4 !important;
    color: #56524D !important;
}

/* Target the alert content */
div[data-testid="stAlert"] > div {
    background-color: #D4D4D4 !important;
    color: #56524D !important;
}

/* Target the markdown content inside alerts */
div[data-testid="stAlert"] .stMarkdown {
    color: #56524D !important;
}

/* Target alert content more specifically */
div[data-testid="stAlert"] p {
    color: #56524D !important;
}

.stMarkdownContainer {
    background-color: #76706C !important;
}
</style>
""")
