import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from src.services.vnstock_api import (
    get_heating_up_stocks,
    get_technical_stock_data,
)
from src.services.technical_indicators import (
    calculate_technical_indicators,
    display_indicators_status,
)
from src.services.chart import (
    create_technical_chart,
    display_fibonacci_summary,
    get_fibonacci_level_alerts,
)
from src.components.ui_components import inject_custom_success_styling

st.set_page_config(
    page_title="Technical Analysis - Finance Bro", page_icon="", layout="wide"
)

# Apply custom CSS styling for success alerts
inject_custom_success_styling()


def main():
    st.title("Technical Analysis")
    st.markdown("---")

    # Page description
    st.markdown("""
    **Technical Analysis** - Discover stocks showing technical heating signals and analyze their price patterns.
    
    This page identifies Vietnamese stocks that are "**Overheated in previous trading session**" according to vnstock technical indicators,
    then displays their candlestick charts with advanced technical indicators for comprehensive analysis.
    """)

    st.markdown("---")

    # Sidebar configuration
    with st.sidebar:
        st.subheader("Chart Configuration")

        # Interval selection
        interval = st.selectbox(
            "Select Interval",
            options=["1D", "1W", "1M"],
            format_func=lambda x: {
                "1D": "Daily (1D)",
                "1W": "Weekly (1W)",
                "1M": "Monthly (1M)",
            }[x],
            key="ta_interval",
            help="Choose the time interval for chart data",
        )

        # Technical indicators toggles
        st.subheader("Technical Indicators")
        show_bb = st.checkbox("Bollinger Bands", value=True)
        show_rsi = st.checkbox("RSI", value=True)
        show_macd = st.checkbox("MACD", value=True)
        show_obv = st.checkbox("OBV", value=False)

        # Indicator parameters
        bb_period = st.slider("BB Period", 10, 50, 20)
        rsi_period = st.slider("RSI Period", 5, 30, 14)

        # Fibonacci Retracement Controls
        st.subheader("Fibonacci Retracement")
        show_fibonacci = st.checkbox("Show Fibonacci Retracements", value=False)

        if show_fibonacci:
            fib_lookback = st.slider(
                "Swing Lookback Period",
                20,
                100,
                50,
                help="Number of bars to analyze for swing detection",
            )
            fib_sensitivity = st.slider(
                "Swing Sensitivity",
                3,
                15,
                5,
                help="Lower values = more sensitive swing detection",
            )
            show_extensions = st.checkbox(
                "Include Extension Levels",
                value=False,
                help="Show 138.2%, 161.8%, 200%, 261.8% levels",
            )

            # Alert threshold for price proximity to Fibonacci levels
            alert_threshold = st.slider(
                "Price Alert Threshold (%)",
                1.0,
                5.0,
                2.0,
                help="Alert when price is within this % of a Fibonacci level",
            )

        # Store in session state for persistence
        if "ta_interval" not in st.session_state:
            st.session_state.ta_interval = "1D"

        # Foreign Transaction Filter
        st.subheader("Data Filters")
        show_foreign_buy_only = st.checkbox(
            "Foreign Buy > Sell Only",
            value=False,
            help="Filter stocks where foreign investors are net buyers (Buy > Sell)",
        )

        show_strong_buy_only = st.checkbox(
            "Strong Buy Signal Only",
            value=False,
            help="Filter stocks with TCBS Strong Buy recommendation",
        )

        show_buy_only = st.checkbox(
            "Buy Signal Only",
            value=False,
            help="Filter stocks with TCBS Buy recommendation",
        )

        # Add a button to clear cache if needed
        if st.button("Refresh Data", help="Clear cached data and reload"):
            st.cache_data.clear()
            st.rerun()

    # Load heating up stocks
    with st.spinner("Scanning market for heating up stocks..."):
        try:
            heating_stocks = get_heating_up_stocks()
        except Exception as e:
            st.error(f"Error loading heating up stocks: {str(e)}")
            st.stop()

    if heating_stocks.empty:
        st.info(
            "No stocks showing 'Overheated in previous trading session' signal today."
        )
        st.stop()

    # Apply filters if enabled
    original_count = len(heating_stocks)
    filter_messages = []

    # Foreign transaction filter
    if show_foreign_buy_only and "foreign_transaction" in heating_stocks.columns:
        foreign_buy_mask = heating_stocks["foreign_transaction"] == "Buy > Sell"
        heating_stocks = heating_stocks[foreign_buy_mask].copy()
        filtered_count = len(heating_stocks)
        if filtered_count < original_count:
            filter_messages.append(f"Foreign Buy > Sell: {filtered_count} stocks")

    # TCBS Strong Buy filter
    if show_strong_buy_only and "tcbs_buy_sell_signal" in heating_stocks.columns:
        before_strong_buy = len(heating_stocks)
        strong_buy_mask = heating_stocks["tcbs_buy_sell_signal"] == "Strong buy"
        heating_stocks = heating_stocks[strong_buy_mask].copy()
        final_count = len(heating_stocks)
        if final_count < before_strong_buy or not filter_messages:
            filter_messages.append(f"Strong Buy Signal: {final_count} stocks")

    # TCBS Buy filter
    if show_buy_only and "tcbs_buy_sell_signal" in heating_stocks.columns:
        before_buy = len(heating_stocks)
        buy_mask = heating_stocks["tcbs_buy_sell_signal"] == "Buy"
        heating_stocks = heating_stocks[buy_mask].copy()
        final_count = len(heating_stocks)
        if final_count < before_buy or not filter_messages:
            filter_messages.append(f"Buy Signal: {final_count} stocks")

    # Show combined filter results
    if filter_messages:
        st.info(
            f"**Filters Applied**: {' | '.join(filter_messages)} (from {original_count} original stocks)"
        )

    # Check if any stocks remain after filtering
    if heating_stocks.empty:
        if show_foreign_buy_only or show_strong_buy_only or show_buy_only:
            active_filters = []
            if show_foreign_buy_only:
                active_filters.append("Foreign Buy > Sell")
            if show_strong_buy_only:
                active_filters.append("Strong Buy Signal")
            if show_buy_only:
                active_filters.append("Buy Signal")
            st.warning(
                f"No heating stocks found matching: {' + '.join(active_filters)}. Try disabling some filters."
            )
        else:
            st.info(
                "No stocks showing 'Overheated in previous trading session' signal today."
            )
        st.stop()

    # Display results summary
    st.success(f"Found **{len(heating_stocks)}** stocks with heating up signals!")

    # Display trading value metrics
    col1, col2 = st.columns(2)

    with col1:
        if "avg_trading_value_5d" in heating_stocks.columns:
            mean_trading_value = heating_stocks["avg_trading_value_5d"].mean()
            if not pd.isna(mean_trading_value):
                st.metric(
                    "Average 5-Day Trading Value",
                    f"{mean_trading_value:,.0f}",
                    help="Mean of avg_trading_value_5d across all filtered heating stocks",
                )
            else:
                st.metric("Average 5-Day Trading Value", "N/A")

    with col2:
        if "total_trading_value" in heating_stocks.columns:
            mean_total_trading_value = heating_stocks["total_trading_value"].mean()
            if not pd.isna(mean_total_trading_value):
                st.metric(
                    "Average Total Trading Value",
                    f"{mean_total_trading_value:,.0f}",
                    help="Mean of total_trading_value across all filtered heating stocks",
                )
            else:
                st.metric("Average Total Trading Value", "N/A")

    # Display the heating stocks DataFrame
    st.subheader("Heating Up Stocks Summary")
    st.dataframe(heating_stocks, use_container_width=True, height=300, hide_index=True)

    # Technical indicators summary
    st.subheader("Technical Indicators Summary")

    # Create columns for indicator toggles
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Bollinger Bands", "ON" if show_bb else "OFF")
    with col2:
        st.metric("RSI", "ON" if show_rsi else "OFF")
    with col3:
        st.metric("MACD", "ON" if show_macd else "OFF")
    with col4:
        st.metric("OBV", "ON" if show_obv else "OFF")

    # Charts section with technical indicators
    st.subheader("Advanced Technical Analysis Charts")

    # Get current interval from session state
    current_interval = st.session_state.ta_interval

    # Display interval info
    interval_info = {"1D": "last 3 months", "1W": "last 6 months", "1M": "last 2 years"}

    st.markdown(
        f"Advanced technical analysis charts for each heating up stock ({interval_info[current_interval]})"
    )

    # Create configuration for indicators
    indicator_config = {
        "show_bb": show_bb,
        "show_rsi": show_rsi,
        "show_macd": show_macd,
        "show_obv": show_obv,
    }

    # Create Fibonacci configuration
    fibonacci_config = {
        "show_fibonacci": show_fibonacci,
        "lookback_bars": fib_lookback if show_fibonacci else 50,
        "swing_order": fib_sensitivity if show_fibonacci else 5,
        "include_extensions": show_extensions if show_fibonacci else False,
        "alert_threshold_pct": alert_threshold if show_fibonacci else 2.0,
    }

    # Create tabs for better organization if many stocks
    tickers = heating_stocks["ticker"].tolist()

    if len(tickers) <= 5:
        # Display all charts directly if 5 or fewer stocks
        for ticker in tickers:
            with st.expander(f"{ticker} - Technical Analysis", expanded=True):
                with st.spinner(
                    f"Loading technical analysis for {ticker} ({current_interval})..."
                ):
                    stock_data = get_technical_stock_data(
                        ticker, interval=current_interval
                    )

                    if not stock_data.empty:
                        indicators, warnings, has_success = (
                            calculate_technical_indicators(stock_data)
                        )
                        display_indicators_status(
                            warnings, has_success, list(indicators.keys())
                        )
                        if indicators:
                            fig = create_technical_chart(
                                ticker,
                                stock_data,
                                indicators,
                                indicator_config,
                                fibonacci_config,
                            )
                            if fig:
                                st.pyplot(fig)
                                plt.close(fig)

                                # Display Fibonacci summary if enabled
                                display_fibonacci_summary(fibonacci_config, ticker)

                                # Show Fibonacci level alerts if enabled
                                if show_fibonacci:
                                    alerts = get_fibonacci_level_alerts(
                                        stock_data, fibonacci_config
                                    )
                                    for alert in alerts:
                                        st.info(f"{alert}")

                                # Display indicator values with safe validation
                                st.subheader("Indicator Values")
                                col1, col2, col3 = st.columns(3)

                                with col1:
                                    if (
                                        "rsi" in indicators
                                        and indicators["rsi"] is not None
                                        and not indicators["rsi"].empty
                                    ):
                                        try:
                                            rsi_value = indicators["rsi"].iloc[-1]
                                            st.metric("RSI", f"{rsi_value:.2f}")
                                        except Exception:
                                            st.metric("RSI", "N/A")
                                    else:
                                        st.metric("RSI", "N/A")
                                        st.caption("RSI calculation failed")

                                with col2:
                                    if (
                                        "macd" in indicators
                                        and indicators["macd"] is not None
                                        and not indicators["macd"].empty
                                    ):
                                        try:
                                            if (
                                                "MACD_12_26_9"
                                                in indicators["macd"].columns
                                            ):
                                                macd_value = indicators["macd"][
                                                    "MACD_12_26_9"
                                                ].iloc[-1]
                                                st.metric("MACD", f"{macd_value:.2f}")
                                            else:
                                                st.metric("MACD", "N/A")
                                        except Exception:
                                            st.metric("MACD", "N/A")
                                    else:
                                        st.metric("MACD", "N/A")
                                        st.caption("MACD calculation failed")

                        else:
                            st.warning("Could not calculate technical indicators")
                    else:
                        st.warning(f"No data available for {ticker}")
    else:
        # Use tabs for many stocks
        tab_chunks = [tickers[i : i + 5] for i in range(0, len(tickers), 5)]
        tab_names = [
            f"Stocks {i * 5 + 1}-{min((i + 1) * 5, len(tickers))}"
            for i in range(len(tab_chunks))
        ]

        tabs = st.tabs(tab_names)

        for tab_idx, tab in enumerate(tabs):
            with tab:
                current_tickers = tab_chunks[tab_idx]
                for ticker in current_tickers:
                    with st.expander(f"{ticker} - Technical Analysis", expanded=False):
                        with st.spinner(
                            f"Loading technical analysis for {ticker} ({current_interval})..."
                        ):
                            stock_data = get_technical_stock_data(
                                ticker, interval=current_interval
                            )

                            if not stock_data.empty:
                                indicators, warnings, has_success = (
                                    calculate_technical_indicators(stock_data)
                                )
                                display_indicators_status(
                                    warnings, has_success, list(indicators.keys())
                                )
                                if indicators:
                                    fig = create_technical_chart(
                                        ticker,
                                        stock_data,
                                        indicators,
                                        indicator_config,
                                        fibonacci_config,
                                    )
                                    if fig:
                                        st.pyplot(fig)
                                        plt.close(fig)

                                        # Display Fibonacci summary if enabled
                                        display_fibonacci_summary(
                                            fibonacci_config, ticker
                                        )

                                        # Show Fibonacci level alerts if enabled
                                        if show_fibonacci:
                                            alerts = get_fibonacci_level_alerts(
                                                stock_data, fibonacci_config
                                            )
                                            for alert in alerts:
                                                st.info(f"{alert}")

                                        # Display indicator values with safe validation
                                        st.subheader("Indicator Values")
                                        col1, col2, col3 = st.columns(3)

                                        with col1:
                                            if (
                                                "rsi" in indicators
                                                and indicators["rsi"] is not None
                                                and not indicators["rsi"].empty
                                            ):
                                                try:
                                                    rsi_value = indicators["rsi"].iloc[
                                                        -1
                                                    ]
                                                    st.metric("RSI", f"{rsi_value:.2f}")
                                                except Exception:
                                                    st.metric("RSI", "N/A")
                                            else:
                                                st.metric("RSI", "N/A")
                                                st.caption("RSI calculation failed")

                                        with col2:
                                            if (
                                                "macd" in indicators
                                                and indicators["macd"] is not None
                                                and not indicators["macd"].empty
                                            ):
                                                try:
                                                    if (
                                                        "MACD_12_26_9"
                                                        in indicators["macd"].columns
                                                    ):
                                                        macd_value = indicators["macd"][
                                                            "MACD_12_26_9"
                                                        ].iloc[-1]
                                                        st.metric(
                                                            "MACD", f"{macd_value:.2f}"
                                                        )
                                                    else:
                                                        st.metric("MACD", "N/A")
                                                except Exception:
                                                    st.metric("MACD", "N/A")
                                            else:
                                                st.metric("MACD", "N/A")
                                                st.caption("MACD calculation failed")

                                else:
                                    st.warning(
                                        "Could not calculate technical indicators"
                                    )
                            else:
                                st.warning(f"No data available for {ticker}")

    # Footer information
    st.markdown("---")
    st.info(f"""
    **Note:** Charts show the {interval_info[current_interval]} of trading data based on your selected interval ({current_interval}). 
    Heating up signals are based on vnstock technical indicators that identify stocks "Overheated in previous trading session".
    
    **Technical Indicators:**
    - **RSI**: Relative Strength Index (momentum oscillator) with 30/50/70 reference levels
    - **MACD**: Moving Average Convergence Divergence (trend-following) with histogram
    - **Bollinger Bands**: Price volatility and potential reversal points
    - **OBV**: On-Balance Volume (volume flow indicator)
    - **Fibonacci Retracements**: Support/resistance levels at 23.6%, 38.2%, 50%, 61.8%, 78.6%
    
    **Fibonacci Features:**
    - Automatic swing high/low detection using SciPy algorithms
    - Configurable lookback period and sensitivity
    - Optional extension levels (138.2%, 161.8%, 200%, 261.8%)
    - Price proximity alerts when near Fibonacci levels
    """)


if __name__ == "__main__":
    main()
