"""
Chart generation utilities for Finance Bro application.
Centralized chart creation functions extracted from various pages.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
import altair as alt
import os
import glob
from bokeh.plotting import figure
from bokeh.layouts import column
from bokeh.models import HoverTool
from typing import Dict, Optional

# Technical Analysis Chart Functions


def create_technical_chart(
    ticker: str,
    data: pd.DataFrame,
    indicators: dict,
    config: dict,
    fibonacci_config: Optional[Dict] = None,
) -> plt.Figure:
    """Create technical analysis chart with indicators using mplfinance with safe validation

    Extracted from Technical_Analysis.py lines 22-168 - EXACT same logic preserved.
    """

    addplots = []
    panels = 1  # Start with price panel
    skipped_indicators = []

    # Bollinger Bands - Safe validation
    if config.get("show_bb", True):
        if "bbands" in indicators and indicators["bbands"] is not None:
            bb = indicators["bbands"]
            required_cols = ["BBU_20_2.0", "BBM_20_2.0", "BBL_20_2.0"]
            if all(col in bb.columns for col in required_cols):
                try:
                    addplots.extend(
                        [
                            mpf.make_addplot(bb["BBU_20_2.0"], color="red", width=0.7),
                            mpf.make_addplot(bb["BBM_20_2.0"], color="blue", width=0.7),
                            mpf.make_addplot(
                                bb["BBL_20_2.0"], color="green", width=0.7
                            ),
                        ]
                    )
                except Exception as e:
                    skipped_indicators.append(f"Bollinger Bands: {str(e)}")
            else:
                skipped_indicators.append("Bollinger Bands: Missing required columns")
        else:
            skipped_indicators.append(
                "Bollinger Bands: Calculation failed or unavailable"
            )

    # RSI Panel - Safe validation with reference levels
    if config.get("show_rsi", True):
        if "rsi" in indicators and indicators["rsi"] is not None:
            rsi = indicators["rsi"]
            if not rsi.empty:
                try:
                    # Create RSI reference levels as horizontal lines
                    overbought_line = pd.Series([70] * len(rsi), index=rsi.index)
                    midline = pd.Series([50] * len(rsi), index=rsi.index)
                    oversold_line = pd.Series([30] * len(rsi), index=rsi.index)

                    addplots.extend(
                        [
                            # RSI actual values
                            mpf.make_addplot(
                                rsi, panel=panels, color="purple", ylabel="RSI", width=2
                            ),
                            # Overbought level (70)
                            mpf.make_addplot(
                                overbought_line,
                                panel=panels,
                                color="red",
                                linestyle="--",
                                alpha=0.7,
                                width=1,
                            ),
                            # Midline (50)
                            mpf.make_addplot(
                                midline,
                                panel=panels,
                                color="gray",
                                linestyle="--",
                                alpha=0.5,
                                width=1,
                            ),
                            # Oversold level (30)
                            mpf.make_addplot(
                                oversold_line,
                                panel=panels,
                                color="green",
                                linestyle="--",
                                alpha=0.7,
                                width=1,
                            ),
                        ]
                    )
                    panels += 1
                except Exception as e:
                    skipped_indicators.append(f"RSI: {str(e)}")
            else:
                skipped_indicators.append("RSI: Empty data")
        else:
            skipped_indicators.append("RSI: Calculation failed or unavailable")

    # MACD Panel - Safe validation with histogram
    if config.get("show_macd", True):
        if "macd" in indicators and indicators["macd"] is not None:
            macd = indicators["macd"]
            required_cols = ["MACD_12_26_9", "MACDs_12_26_9", "MACDh_12_26_9"]
            if all(col in macd.columns for col in required_cols):
                try:
                    addplots.extend(
                        [
                            # MACD Line
                            mpf.make_addplot(
                                macd["MACD_12_26_9"],
                                panel=panels,
                                color="blue",
                                ylabel="MACD",
                                width=2,
                            ),
                            # Signal Line
                            mpf.make_addplot(
                                macd["MACDs_12_26_9"],
                                panel=panels,
                                color="red",
                                width=2,
                            ),
                            # Histogram
                            mpf.make_addplot(
                                macd["MACDh_12_26_9"],
                                panel=panels,
                                type="bar",
                                color="gray",
                                alpha=0.6,
                            ),
                        ]
                    )
                    panels += 1
                except Exception as e:
                    skipped_indicators.append(f"MACD: {str(e)}")
            else:
                skipped_indicators.append("MACD: Missing required columns")
        else:
            skipped_indicators.append("MACD: Calculation failed or unavailable")

    # OBV Panel - Safe validation
    if config.get("show_obv", True):
        if "obv" in indicators and indicators["obv"] is not None:
            obv = indicators["obv"]
            if not obv.empty:
                try:
                    addplots.append(
                        mpf.make_addplot(
                            obv, panel=panels, color="orange", ylabel="OBV"
                        )
                    )
                    panels += 1
                except Exception as e:
                    skipped_indicators.append(f"OBV: {str(e)}")
            else:
                skipped_indicators.append("OBV: Empty data")
        else:
            skipped_indicators.append("OBV: Calculation failed or unavailable")

    # Chart service supports 4 core technical indicators: RSI, MACD, Bollinger Bands, OBV

    # Add Fibonacci retracement levels if provided
    if fibonacci_config and fibonacci_config.get("show_fibonacci", False):
        fib_plots = _create_fibonacci_overlays(data, fibonacci_config)
        if fib_plots:
            addplots.extend(fib_plots)

    # Show warning for skipped indicators
    if skipped_indicators:
        warning_text = "⚠️ **Skipped indicators in chart:**\n" + "\n".join(
            f"• {s}" for s in skipped_indicators
        )
        st.warning(warning_text)

    # Create chart with Finance Bro theme
    marketcolors = mpf.make_marketcolors(
        up="#76706C",
        down="#2B2523",
        edge="inherit",
        wick={"up": "#76706C", "down": "#2B2523"},
        volume="in",
    )

    style = mpf.make_mpf_style(
        marketcolors=marketcolors,
        gridstyle="",
        y_on_right=True,
        facecolor="white",
        figcolor="white",
    )

    fig, axes = mpf.plot(
        data,
        type="candle",
        style=style,
        title=f"{ticker} - Technical Analysis",
        ylabel="Price (VND)",
        volume=True,
        addplot=addplots,
        figsize=(15, 4 * panels),
        panel_ratios=[6] + [2] * (panels - 1),
        returnfig=True,
    )

    return fig


# Stock Price Analysis Chart Functions


def create_altair_line_chart(chart_data: pd.DataFrame, ticker: str) -> alt.Chart:
    """Create Altair line chart for stock price analysis

    Extracted from Stock_Price_Analysis.py lines 447-464.
    """
    stock_chart = (
        alt.Chart(chart_data)
        .mark_line(color="black", strokeWidth=2)
        .encode(
            x=alt.X("date:T", title="Date"),
            y=alt.Y(
                "price:Q",
                title="Close Price (in thousands)",
                axis=alt.Axis(format=",.0f"),
            ),
            tooltip=[
                alt.Tooltip("date:T", title="Date"),
                alt.Tooltip("price:Q", title="Close Price", format=",.0f"),
            ],
        )
        .properties(width="container", height=400, title=f"{ticker}")
        .interactive()
    )

    return stock_chart


def create_altair_area_chart(chart_data: pd.DataFrame, ticker: str) -> alt.Chart:
    """Create Altair area chart with gradient for stock price analysis

    Extracted from Stock_Price_Analysis.py lines 465-489.
    """
    stock_chart = (
        alt.Chart(chart_data)
        .mark_area(
            line={"color": "#3C3C3C", "strokeWidth": 2},
            color=alt.Gradient(
                gradient="linear",
                stops=[
                    alt.GradientStop(color="#3C3C3C", offset=0),
                    alt.GradientStop(color="#807F80", offset=1),
                ],
                x1=1,
                x2=1,
                y1=1,
                y2=0,
            ),
        )
        .encode(
            x=alt.X("date:T", title="Date"),
            y=alt.Y(
                "price:Q",
                title="Close Price (in thousands)",
                axis=alt.Axis(format=",.0f"),
            ),
            tooltip=[
                alt.Tooltip("date:T", title="Date"),
                alt.Tooltip("price:Q", title="Close Price", format=",.0f"),
            ],
        )
        .properties(width="container", height=400, title=f"{ticker}")
        .interactive()
    )

    return stock_chart


def create_bokeh_candlestick_chart(stock_price_bokeh: pd.DataFrame, ticker: str):
    """Create Bokeh candlestick chart with volume for stock price analysis

    Extracted from Stock_Price_Analysis.py lines 494-606.
    """
    # Calculate candlestick properties
    stock_price_bokeh["color"] = [
        "green" if close >= open_price else "red"
        for close, open_price in zip(
            stock_price_bokeh["close"], stock_price_bokeh["open"]
        )
    ]

    # Calculate min/max values for consistent scaling
    min_date = stock_price_bokeh.index.min()
    max_date = stock_price_bokeh.index.max()
    max_volume = stock_price_bokeh["volume"].max()

    # Price chart - use responsive sizing
    price = figure(
        x_axis_type="datetime",
        title=f"{ticker} - Candlestick Chart",
        height=400,
        tools="pan,wheel_zoom,box_zoom,reset,save",
        toolbar_location="above",
        x_range=(min_date, max_date),
        sizing_mode="stretch_width",
    )

    # Add segments for high-low range
    price.segment(
        x0="date",
        y0="high",
        x1="date",
        y1="low",
        source=stock_price_bokeh,
        color="black",
        line_width=1,
    )

    # Add rectangles for open-close range
    price.vbar(
        x="date",
        width=12 * 60 * 60 * 1000,  # 12 hours in milliseconds
        top="open",
        bottom="close",
        source=stock_price_bokeh,
        fill_color="color",
        line_color="black",
        line_width=1,
    )

    # Customize price plot
    price.yaxis.axis_label = "Price (in thousands)"
    price.grid.grid_line_alpha = 0.3
    price.xaxis.visible = False  # Hide x-axis labels on price chart

    # Volume chart - use same responsive sizing
    volume = figure(
        x_axis_type="datetime",
        height=200,
        tools="pan,wheel_zoom,box_zoom,reset,save",
        toolbar_location=None,
        x_range=price.x_range,  # Link x-axis with price chart
        sizing_mode="stretch_width",
    )

    # Add volume bars
    volume.vbar(
        x="date",
        width=12 * 60 * 60 * 1000,
        top="volume",
        bottom=0,
        source=stock_price_bokeh,
        fill_color="color",
        line_color="black",
        line_width=0.5,
        alpha=0.7,
    )

    # Customize volume plot
    volume.yaxis.axis_label = "Volume"
    volume.grid.grid_line_alpha = 0.3
    volume.xaxis.axis_label = "Date"

    # Add hover tools for both charts
    hover_price = HoverTool(
        tooltips=[
            ("Date", "@date{%F}"),
            ("Open", "@open{0,0}"),
            ("High", "@high{0,0}"),
            ("Low", "@low{0,0}"),
            ("Close", "@close{0,0}"),
            ("Volume", "@volume{0,0}"),
        ],
        formatters={"@date": "datetime"},
        mode="vline",
    )
    price.add_tools(hover_price)

    hover_volume = HoverTool(
        tooltips=[("Date", "@date{%F}"), ("Volume", "@volume{0,0}")],
        formatters={"@date": "datetime"},
        mode="vline",
    )
    volume.add_tools(hover_volume)

    # Combine charts vertically with proper alignment
    combined_chart = column(price, volume, sizing_mode="stretch_width")

    return combined_chart


# Chart Detection Functions (from bro.py)


def detect_latest_chart():
    """Detect the most recently generated chart file

    Extracted from bro.py lines 45-59 - EXACT same logic preserved.
    """
    try:
        chart_dir = "exports/charts/"
        if os.path.exists(chart_dir):
            chart_files = glob.glob(os.path.join(chart_dir, "*.png"))
            if chart_files:
                latest_chart = max(chart_files, key=os.path.getctime)
                return {"type": "image", "path": latest_chart}
    except Exception:
        pass
    return None


# Chart Theme Functions


def get_finance_bro_theme():
    """Get Finance Bro standard chart theme colors and styling"""
    return {
        "primary_colors": {
            "up": "#76706C",
            "down": "#2B2523",
            "neutral": "#3C3C3C",
            "accent": "#807F80",
        },
        "gradients": {
            "area_chart": [
                {"color": "#3C3C3C", "offset": 0},
                {"color": "#807F80", "offset": 1},
            ]
        },
        "mplfinance": {
            "up": "#76706C",
            "down": "#2B2523",
            "wick": {"up": "#76706C", "down": "#2B2523"},
            "facecolor": "white",
            "figcolor": "white",
        },
    }


def create_mplfinance_style():
    """Create mplfinance style with Finance Bro theme"""
    theme = get_finance_bro_theme()

    marketcolors = mpf.make_marketcolors(
        up=theme["mplfinance"]["up"],
        down=theme["mplfinance"]["down"],
        edge="inherit",
        wick=theme["mplfinance"]["wick"],
        volume="in",
    )

    style = mpf.make_mpf_style(
        marketcolors=marketcolors,
        gridstyle="",
        y_on_right=True,
        facecolor=theme["mplfinance"]["facecolor"],
        figcolor=theme["mplfinance"]["figcolor"],
    )

    return style


# Fibonacci Overlay Functions


def _create_fibonacci_overlays(data: pd.DataFrame, fibonacci_config: Dict) -> list:
    """
    Create Fibonacci retracement level overlays for mplfinance charts.

    Args:
        data: OHLCV DataFrame
        fibonacci_config: Configuration dictionary with Fibonacci settings

    Returns:
        List of mplfinance addplot objects for Fibonacci levels
    """
    try:
        from src.services.fibonacci import (
            get_recent_swing_fibonacci,
            get_fibonacci_colors,
        )

        # Get Fibonacci analysis
        fib_data = get_recent_swing_fibonacci(
            data,
            lookback_bars=fibonacci_config.get("lookback_bars", 50),
            swing_order=fibonacci_config.get("swing_order", 5),
            include_extensions=fibonacci_config.get("include_extensions", False),
        )

        if not fib_data or "fibonacci_levels" not in fib_data:
            return []

        fibonacci_levels = fib_data["fibonacci_levels"]
        fibonacci_colors = get_fibonacci_colors()

        # Create horizontal line overlays for each Fibonacci level
        addplots = []

        for level_name, price in fibonacci_levels.items():
            # Skip extension levels if not requested
            if (
                not fibonacci_config.get("include_extensions", False)
                and float(level_name.replace("%", "")) > 100
            ):
                continue

            # Create horizontal line data (same price across all time points)
            fib_line = pd.Series([price] * len(data), index=data.index)

            # Get color for this level
            color = fibonacci_colors.get(level_name, "#56524D")

            # Create line style based on importance
            line_style = "solid"
            line_width = 1.5
            alpha = 0.7

            # Emphasize key levels
            if level_name in ["38.2%", "50.0%", "61.8%"]:
                line_width = 2.0
                alpha = 0.9
            elif level_name in ["0.0%", "100.0%"]:
                line_style = "dashed"
                line_width = 1.8
                alpha = 0.8

            # Create addplot for this Fibonacci level
            addplots.append(
                mpf.make_addplot(
                    fib_line,
                    color=color,
                    width=line_width,
                    alpha=alpha,
                    secondary_y=False,
                    panel=0,  # Main price panel
                )
            )

        # Store Fibonacci data for summary display
        if "fibonacci_summary" not in st.session_state:
            st.session_state.fibonacci_summary = {}
        st.session_state.fibonacci_summary[data.index[-1].strftime("%Y-%m-%d")] = (
            fib_data
        )

        return addplots

    except Exception as e:
        st.warning(f"Error creating Fibonacci overlays: {str(e)}")
        return []


def display_fibonacci_summary(fibonacci_config: Dict, ticker: str) -> None:
    """
    Display Fibonacci retracement summary information.

    Args:
        fibonacci_config: Fibonacci configuration
        ticker: Stock ticker symbol
    """
    try:
        if not fibonacci_config.get("show_fibonacci", False):
            return

        # Get stored Fibonacci summary from session state
        if (
            "fibonacci_summary" in st.session_state
            and st.session_state.fibonacci_summary
        ):
            latest_date = max(st.session_state.fibonacci_summary.keys())
            fib_data = st.session_state.fibonacci_summary[latest_date]

            if fib_data:
                from src.services.fibonacci import format_fibonacci_summary

                st.subheader(f"📈 Fibonacci Analysis - {ticker}")

                # Display summary
                summary = format_fibonacci_summary(fib_data)
                st.markdown(summary)

                # Display current price context if available
                current_price = fib_data.get("current_price")
                if current_price:
                    swing_high = fib_data["swing_high"]
                    swing_low = fib_data["swing_low"]

                    # Calculate where current price sits relative to Fibonacci levels
                    fib_levels = fib_data["fibonacci_levels"]

                    closest_level = None
                    min_distance = float("inf")

                    for level_name, level_price in fib_levels.items():
                        distance = abs(current_price - level_price)
                        if distance < min_distance:
                            min_distance = distance
                            closest_level = (level_name, level_price)

                    if closest_level:
                        level_name, level_price = closest_level
                        distance_pct = (min_distance / level_price) * 100

                        st.info(
                            f"""
                        **Current Price Context:**
                        - Current: {current_price:,.2f}
                        - Nearest Fib Level: {level_name} at {level_price:,.2f}
                        - Distance: {distance_pct:.1f}%
                        """
                        )

    except Exception as e:
        st.error(f"Error displaying Fibonacci summary: {str(e)}")


def get_fibonacci_level_alerts(data: pd.DataFrame, fibonacci_config: Dict) -> list:
    """
    Check if current price is near any Fibonacci levels and return alerts.

    Args:
        data: OHLCV DataFrame
        fibonacci_config: Fibonacci configuration

    Returns:
        List of alert messages
    """
    try:
        if not fibonacci_config.get("show_fibonacci", False) or data.empty:
            return []

        from src.services.fibonacci import get_recent_swing_fibonacci

        # Get current Fibonacci analysis
        fib_data = get_recent_swing_fibonacci(
            data,
            lookback_bars=fibonacci_config.get("lookback_bars", 50),
            swing_order=fibonacci_config.get("swing_order", 5),
            include_extensions=fibonacci_config.get("include_extensions", False),
        )

        if not fib_data:
            return []

        # Handle both lowercase and capitalized column names
        close_col = "Close" if "Close" in data.columns else "close"
        current_price = data[close_col].iloc[-1]
        fibonacci_levels = fib_data["fibonacci_levels"]
        alerts = []

        # Check proximity to each level (within 2% by default)
        proximity_threshold = fibonacci_config.get("alert_threshold_pct", 2.0) / 100

        for level_name, level_price in fibonacci_levels.items():
            distance_pct = abs(current_price - level_price) / level_price

            if distance_pct <= proximity_threshold:
                direction = "above" if current_price > level_price else "below"
                alerts.append(
                    f"Price near {level_name} Fibonacci level ({level_price:,.2f}) - currently {direction}"
                )

        return alerts

    except Exception as e:
        st.warning(f"Error checking Fibonacci alerts: {str(e)}")
        return []


# Fund Analysis Chart Functions


def create_fund_nav_line_chart(nav_data: pd.DataFrame, fund_name: str) -> alt.Chart:
    """Create NAV performance line chart for fund analysis

    Args:
        nav_data: DataFrame with 'date' and 'nav_per_unit' columns
        fund_name: Name of the fund for chart title

    Returns:
        Altair Chart object with Finance Bro theming
    """
    from src.core.config import THEME_COLORS

    nav_chart = (
        alt.Chart(nav_data)
        .mark_line(color=THEME_COLORS["primary"], strokeWidth=3)
        .add_params(alt.selection_interval(bind="scales"))
        .encode(
            x=alt.X("date:T", title="Date", axis=alt.Axis(format="%Y-%m")),
            y=alt.Y(
                "nav_per_unit:Q", title="NAV per Unit", scale=alt.Scale(zero=False)
            ),
            tooltip=[
                alt.Tooltip("date:T", title="Date", format="%Y-%m-%d"),
                alt.Tooltip("nav_per_unit:Q", title="NAV per Unit", format=".2f"),
            ],
        )
        .properties(width=700, height=400, title=f"NAV Performance - {fund_name}")
        .resolve_scale(color="independent")
    )

    return nav_chart


def create_fund_comparison_bar_chart(
    fund_data: pd.DataFrame, limit: int = None
) -> alt.Chart:
    """Create fund performance comparison bar chart

    Args:
        fund_data: DataFrame with fund performance data
        limit: Number of top funds to display (default: None for all funds)

    Returns:
        Altair Chart object with Finance Bro theming
    """
    from src.core.config import THEME_COLORS

    # Filter funds with valid 36m data
    valid_funds = fund_data.dropna(subset=["nav_change_36m_annualized"])

    if len(valid_funds) == 0:
        return (
            alt.Chart(pd.DataFrame())
            .mark_text()
            .encode(text=alt.value("No data available"))
        )

    # Sort funds by performance (show all funds or apply limit if specified)
    if limit is not None:
        display_funds = valid_funds.nlargest(limit, "nav_change_36m_annualized")
    else:
        display_funds = valid_funds.sort_values(
            "nav_change_36m_annualized", ascending=False
        )

    comparison_chart = (
        alt.Chart(display_funds)
        .mark_bar(
            color=THEME_COLORS["tertiary"],
            stroke=THEME_COLORS["primary"],
            strokeWidth=1,
        )
        .encode(
            x=alt.X(
                "short_name:N", title="Fund Name", sort="-y", axis=alt.Axis(grid=False)
            ),
            y=alt.Y(
                "nav_change_36m_annualized:Q",
                title="36-Month Annualized Return (%)",
                axis=alt.Axis(grid=False),
            ),
            tooltip=[
                alt.Tooltip("short_name:N", title="Fund Name"),
                alt.Tooltip(
                    "nav_change_36m_annualized:Q", title="36M Return (%)", format=".2f"
                ),
                alt.Tooltip("fund_type:N", title="Fund Type"),
                alt.Tooltip("fund_owner_name:N", title="Fund Owner"),
            ],
        )
        .properties(
            width=max(
                800, len(display_funds) * 15
            ),  # Dynamic width based on number of funds
            height=400,
            title=f"All Funds - 36-Month Annualized Returns ({len(display_funds)} funds)",
        )
    )

    return comparison_chart


def create_fund_asset_pie_chart(asset_data: pd.DataFrame, fund_name: str) -> alt.Chart:
    """Create asset allocation pie chart for fund analysis

    Args:
        asset_data: DataFrame with 'asset_type' and 'net_asset_percent' columns
        fund_name: Name of the fund for chart title

    Returns:
        Altair Chart object with Finance Bro theming
    """
    from src.core.config import THEME_COLORS

    if asset_data.empty:
        return (
            alt.Chart(pd.DataFrame())
            .mark_text()
            .encode(text=alt.value("No asset allocation data available"))
        )

    # Handle different column name formats
    percent_col = (
        "asset_percent"
        if "asset_percent" in asset_data.columns
        else "net_asset_percent"
    )

    asset_chart = (
        alt.Chart(asset_data)
        .mark_arc(innerRadius=50, stroke="white", strokeWidth=2)
        .encode(
            theta=alt.Theta(f"{percent_col}:Q", title="Percentage"),
            color=alt.Color(
                "asset_type:N",
                scale=alt.Scale(
                    range=[
                        THEME_COLORS["primary"],
                        THEME_COLORS["secondary"],
                        THEME_COLORS["tertiary"],
                        "#8B7D7B",
                        "#A59B96",
                    ]
                ),
            ),
            tooltip=[
                alt.Tooltip("asset_type:N", title="Asset Type"),
                alt.Tooltip(f"{percent_col}:Q", title="Percentage (%)", format=".2f"),
            ],
        )
        .properties(width=300, height=300, title=f"Asset Allocation - {fund_name}")
    )

    return asset_chart


def create_fund_industry_pie_chart(
    industry_data: pd.DataFrame, fund_name: str
) -> alt.Chart:
    """Create industry allocation pie chart for fund analysis

    Args:
        industry_data: DataFrame with 'industry' and allocation percentage columns
        fund_name: Name of the fund for chart title

    Returns:
        Altair Chart object with Finance Bro theming
    """
    from src.core.config import THEME_COLORS

    if industry_data.empty:
        return (
            alt.Chart(pd.DataFrame())
            .mark_text()
            .encode(text=alt.value("No industry allocation data available"))
        )

    # Handle different column name formats
    percent_col = (
        "industry_percent"
        if "industry_percent" in industry_data.columns
        else "net_asset_percent"
    )

    industry_chart = (
        alt.Chart(industry_data)
        .mark_arc(innerRadius=50, stroke="white", strokeWidth=2)
        .encode(
            theta=alt.Theta(f"{percent_col}:Q", title="Percentage"),
            color=alt.Color(
                "industry:N",
                scale=alt.Scale(
                    range=[
                        THEME_COLORS["primary"],
                        THEME_COLORS["secondary"],
                        THEME_COLORS["tertiary"],
                        "#8B7D7B",
                        "#A59B96",
                        "#6B6B6B",
                        "#9A9A9A",
                        "#B5B5B5",
                    ]
                ),
            ),
            tooltip=[
                alt.Tooltip("industry:N", title="Industry"),
                alt.Tooltip(f"{percent_col}:Q", title="Allocation (%)", format=".2f"),
            ],
        )
        .properties(width=300, height=300, title=f"Industry Allocation - {fund_name}")
    )

    return industry_chart


def generate_fund_charts_2x2_png(
    nav_chart: alt.Chart,
    comparison_chart: alt.Chart,
    asset_chart: alt.Chart,
    industry_chart: alt.Chart,
    fund_name: str,
    fund_code: str,
) -> bytes:
    """
    Generate all fund charts in a 2x2 layout as PNG data

    Args:
        nav_chart: NAV performance line chart
        comparison_chart: Fund comparison bar chart
        asset_chart: Asset allocation pie chart
        industry_chart: Industry allocation pie chart
        fund_name: Name of the fund for chart title
        fund_code: Fund code for chart title

    Returns:
        PNG data as bytes for direct download
    """
    import altair as alt
    import io

    # Create 2x2 layout
    # Top row: NAV Performance and Fund Comparison
    top_row = alt.hconcat(
        nav_chart.resolve_scale(color="independent").properties(width=400, height=300),
        comparison_chart.resolve_scale(color="independent").properties(
            width=400, height=300
        ),
        spacing=20,
    )

    # Bottom row: Asset Allocation and Industry Allocation
    bottom_row = alt.hconcat(
        asset_chart.resolve_scale(color="independent").properties(
            width=400, height=300
        ),
        industry_chart.resolve_scale(color="independent").properties(
            width=400, height=300
        ),
        spacing=20,
    )

    # Combine into 2x2 grid
    combined_chart = (
        alt.vconcat(top_row, bottom_row, spacing=20)
        .resolve_scale(color="independent")
        .properties(title=f"Fund Analysis Dashboard - {fund_name} ({fund_code})")
    )

    # Generate PNG data directly in memory
    try:
        # Save to memory buffer
        png_buffer = io.BytesIO()
        combined_chart.save(png_buffer, format="png", scale_factor=2.0)
        png_buffer.seek(0)
        return png_buffer.getvalue()
    except ImportError as e:
        if "vl-convert-python" in str(e):
            st.error(
                "📦 Missing required package for PNG export. Please install vl-convert-python."
            )
            st.info(
                "Run: `pip install vl-convert-python` or `uv add vl-convert-python`"
            )
        else:
            st.error(f"Import error generating chart: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Error generating chart: {str(e)}")
        return None
