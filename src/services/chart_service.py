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

# Technical Analysis Chart Functions


def create_technical_chart(
    ticker: str, data: pd.DataFrame, indicators: dict, config: dict
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

    # RSI Panel - Safe validation
    if config.get("show_rsi", True):
        if "rsi" in indicators and indicators["rsi"] is not None:
            rsi = indicators["rsi"]
            if not rsi.empty:
                try:
                    addplots.append(
                        mpf.make_addplot(
                            rsi, panel=panels, color="purple", ylabel="RSI"
                        )
                    )
                    panels += 1
                except Exception as e:
                    skipped_indicators.append(f"RSI: {str(e)}")
            else:
                skipped_indicators.append("RSI: Empty data")
        else:
            skipped_indicators.append("RSI: Calculation failed or unavailable")

    # MACD Panel - Safe validation
    if config.get("show_macd", True):
        if "macd" in indicators and indicators["macd"] is not None:
            macd = indicators["macd"]
            required_cols = ["MACD_12_26_9", "MACDs_12_26_9"]
            if all(col in macd.columns for col in required_cols):
                try:
                    addplots.extend(
                        [
                            mpf.make_addplot(
                                macd["MACD_12_26_9"],
                                panel=panels,
                                color="blue",
                                ylabel="MACD",
                            ),
                            mpf.make_addplot(
                                macd["MACDs_12_26_9"], panel=panels, color="red"
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
