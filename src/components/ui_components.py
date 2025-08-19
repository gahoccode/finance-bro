"""
General UI Components Module

Provides reusable UI components used across multiple pages.
All components preserve existing session state variables and patterns.
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
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


def clear_progress_indicator(progress_bar, status_text) -> None:
    """Clear progress indicators.

    Extracted from Portfolio_Optimization.py - EXACT same pattern preserved.
    """
    progress_bar.empty()
    status_text.empty()


def create_pie_chart_visualization(
    weights_dict: Dict[str, float], title: str, colors: List[str] = None
) -> Optional:
    """Create pie chart for portfolio weights using Bokeh.

    Extracted from Portfolio_Optimization.py lines 370-413 - EXACT same logic preserved.
    """
    try:
        from bokeh.plotting import figure
        from bokeh.transform import cumsum
        from math import pi
        import pandas as pd

        if colors is None:
            colors = ["#56524D", "#76706C", "#AAA39F"]

        # Filter out zero weights and prepare data
        data = pd.DataFrame(list(weights_dict.items()), columns=["Symbol", "Weight"])
        data = data[data["Weight"] > 0.01]  # Filter out very small weights
        data = data.sort_values("Weight", ascending=False)

        if len(data) == 0:
            return None

        # Calculate angles for pie chart
        data["angle"] = data["Weight"] / data["Weight"].sum() * 2 * pi
        data["color"] = (
            colors[: len(data)]
            if len(data) <= len(colors)
            else colors + ["#D3D3D3"] * (len(data) - len(colors))
        )

        # Create pie chart with increased height for better visibility
        p = figure(
            height=400,
            width=350,
            title=title,
            toolbar_location=None,
            tools="hover",
            tooltips="@Symbol: @Weight{0.00%}",
            x_range=(-0.5, 0.5),
            y_range=(-0.5, 0.5),
            sizing_mode="scale_both",
        )

        p.wedge(
            x=0,
            y=0,
            radius=0.35,
            start_angle=cumsum("angle", include_zero=True),
            end_angle=cumsum("angle"),
            line_color="white",
            fill_color="color",
            legend_field="Symbol",
            source=data,
        )

        p.axis.axis_label = None
        p.axis.visible = False
        p.grid.grid_line_color = None
        p.title.text_font_size = "12pt"
        p.legend.label_text_font_size = "10pt"

        return p

    except ImportError:
        st.warning("Bokeh not available for pie chart visualization")
        return None
    except Exception as e:
        st.error(f"Error creating pie chart: {str(e)}")
        return None


def render_weights_comparison_table(weights_data: Dict[str, Dict[str, float]]) -> None:
    """Render portfolio weights comparison table.

    Used in Portfolio_Optimization.py for comparing different portfolio strategies.
    """
    if not weights_data:
        st.warning("No weights data available")
        return

    columns = st.columns(len(weights_data))

    for i, (strategy_name, weights) in enumerate(weights_data.items()):
        with columns[i]:
            st.write(f"**{strategy_name}**")
            weights_df = pd.DataFrame(
                list(weights.items()), columns=["Symbol", "Weight"]
            )
            weights_df["Weight"] = weights_df["Weight"].apply(lambda x: f"{x:.2%}")
            st.dataframe(weights_df, hide_index=True)


def create_trading_value_metrics(
    data: pd.DataFrame, columns_config: Dict[str, str]
) -> None:
    """Create trading value metrics display.

    Extracted from Technical_Analysis.py sidebar metrics - EXACT same logic preserved.
    """
    col1, col2 = st.columns(2)

    with col1:
        if columns_config.get("avg_trading_value_col") in data.columns:
            mean_trading_value = data[columns_config["avg_trading_value_col"]].mean()
            if not pd.isna(mean_trading_value):
                st.metric(
                    columns_config.get(
                        "avg_trading_label", "📊 Average 5-Day Trading Value"
                    ),
                    f"{mean_trading_value:,.0f}",
                    help=columns_config.get(
                        "avg_trading_help", "Mean trading value calculation"
                    ),
                )
            else:
                st.metric(
                    columns_config.get("avg_trading_label", "📊 Average Trading Value"),
                    "N/A",
                )

    with col2:
        if columns_config.get("total_trading_value_col") in data.columns:
            mean_total_trading_value = data[
                columns_config["total_trading_value_col"]
            ].mean()
            if not pd.isna(mean_total_trading_value):
                st.metric(
                    columns_config.get(
                        "total_trading_label", "📈 Average Total Trading Value"
                    ),
                    f"{mean_total_trading_value:,.0f}",
                    help=columns_config.get(
                        "total_trading_help", "Mean total trading value calculation"
                    ),
                )
            else:
                st.metric(
                    columns_config.get(
                        "total_trading_label", "📈 Average Total Trading Value"
                    ),
                    "N/A",
                )


def render_filter_status_info(filter_messages: List[str], original_count: int) -> None:
    """Render filter status information.

    Extracted from Technical_Analysis.py filter status display - EXACT same logic preserved.
    """
    if filter_messages:
        st.info(
            f"📊 **Filters Applied**: {' | '.join(filter_messages)} (from {original_count} original stocks)"
        )


def create_indicator_toggle_metrics(indicators_config: Dict[str, bool]) -> None:
    """Create indicator toggle metrics display.

    Extracted from Technical_Analysis.py indicator summary - EXACT same logic preserved.
    """
    num_indicators = len(indicators_config)
    columns = st.columns(num_indicators)

    for i, (indicator_name, is_enabled) in enumerate(indicators_config.items()):
        with columns[i]:
            display_name = indicator_name.replace("show_", "").replace("_", " ").title()
            st.metric(display_name, "ON" if is_enabled else "OFF")


def render_file_download_interface(
    filepath: str, filename: str, label: str, mime_type: str, help_text: str = None
) -> None:
    """Render file download interface.

    Extracted from Portfolio_Optimization.py Excel report download - EXACT same logic preserved.
    """
    try:
        with open(filepath, "rb") as file:
            st.download_button(
                label=label,
                data=file.read(),
                file_name=filename,
                mime=mime_type,
                help=help_text,
            )

        # Show file details
        import os

        file_size = os.path.getsize(filepath) / 1024  # Size in KB
        st.caption(f"File: {filename} ({file_size:.1f} KB)")

    except FileNotFoundError:
        st.error(f"File not found: {filepath}")
    except Exception as e:
        st.error(f"Error preparing download: {str(e)}")


def create_investment_summary_info(summary_data: Dict[str, Any]) -> None:
    """Create investment summary information box.

    Extracted from Portfolio_Optimization.py investment summary - EXACT same logic preserved.
    """
    st.subheader("Investment Summary")

    portfolio_value = summary_data.get("portfolio_value", 0)
    allocated_value = summary_data.get("allocated_value", 0)
    leftover = summary_data.get("leftover", 0)
    total_stocks = summary_data.get("total_stocks", 0)
    portfolio_label = summary_data.get("portfolio_label", "Portfolio")

    st.info(f"""
    **Portfolio Strategy**: {portfolio_label}  
    **Total Investment**: {portfolio_value:,.0f} VND  
    **Allocated**: {allocated_value:,.0f} VND ({(allocated_value / portfolio_value * 100):.1f}%)  
    **Remaining Cash**: {leftover:,.0f} VND ({(leftover / portfolio_value * 100):.1f}%)  
    **Number of Stocks**: {total_stocks} stocks
    """)


def render_allocation_summary_metrics(
    allocated_value: float, leftover: float, portfolio_value: float, total_stocks: int
) -> None:
    """Render allocation summary metrics in columns.

    Extracted from Portfolio_Optimization.py allocation metrics - EXACT same logic preserved.
    """
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Allocated Amount",
            f"{allocated_value:,.0f} VND",
            f"{(allocated_value / portfolio_value * 100):.1f}% of portfolio",
        )

    with col2:
        st.metric(
            "Leftover Cash",
            f"{leftover:,.0f} VND",
            f"{(leftover / portfolio_value * 100):.1f}% of portfolio",
        )

    with col3:
        st.metric("Stocks to Buy", total_stocks)


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
