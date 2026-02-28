import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from src.services.vnstock_api import (
    get_heating_up_stocks,
    get_technical_stock_data,
)
from src.services.technical_indicators import calculate_technical_indicators
from src.services.chart_service import create_technical_chart

st.set_page_config(
    page_title="Technical Analysis - Finance Bro", page_icon="", layout="wide"
)


def main():
    st.title("Technical analysis")

    # Page description
    st.caption(
        "Discover stocks showing technical heating signals and analyze their price patterns. "
        "This page identifies Vietnamese stocks that are overheated in the previous trading session "
        "according to vnstock technical indicators, then displays their candlestick charts with advanced technical indicators."
    )

    # Sidebar configuration
    with st.sidebar:
        st.subheader("Chart configuration")

        # Interval selection
        st.selectbox(
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
        st.subheader("Technical indicators")
        show_bb = st.toggle("Bollinger Bands", value=True)
        show_rsi = st.toggle("RSI", value=True)
        show_macd = st.toggle("MACD", value=True)
        show_obv = st.toggle("OBV", value=False)

        # Note: Indicator parameters are fixed in manual implementation
        st.caption(
            "Indicator parameters: RSI(14), MACD(12,26,9), BB(20,2), OBV — optimized for reliable signals"
        )

        # Store in session state for persistence
        if "ta_interval" not in st.session_state:
            st.session_state.ta_interval = "1D"

        # Foreign Transaction Filter
        st.subheader("Data filters")
        show_foreign_buy_only = st.toggle(
            "Foreign Buy > Sell only",
            value=False,
            help="Filter stocks where foreign investors are net buyers (Buy > Sell)",
        )

        show_strong_buy_only = st.toggle(
            "Strong Buy signal only",
            value=False,
            help="Filter stocks with TCBS Strong Buy recommendation",
        )

        show_buy_only = st.toggle(
            "Buy signal only",
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
                    border=True,
                )
            else:
                st.metric("Average 5-Day Trading Value", "N/A", border=True)

    with col2:
        if "total_trading_value" in heating_stocks.columns:
            mean_total_trading_value = heating_stocks["total_trading_value"].mean()
            if not pd.isna(mean_total_trading_value):
                st.metric(
                    "Average Total Trading Value",
                    f"{mean_total_trading_value:,.0f}",
                    help="Mean of total_trading_value across all filtered heating stocks",
                    border=True,
                )
            else:
                st.metric("Average Total Trading Value", "N/A", border=True)

    # Display the heating stocks DataFrame
    st.subheader("Heating up stocks summary")
    st.dataframe(heating_stocks, use_container_width=True, height=300, hide_index=True)

    # Technical indicators summary
    st.subheader("Technical indicators summary")

    # Create columns for indicator toggles
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Bollinger Bands", "ON" if show_bb else "OFF", border=True)
    with col2:
        st.metric("RSI", "ON" if show_rsi else "OFF", border=True)
    with col3:
        st.metric("MACD", "ON" if show_macd else "OFF", border=True)
    with col4:
        st.metric("OBV", "ON" if show_obv else "OFF", border=True)

    # Charts section with technical indicators
    st.subheader("Advanced technical analysis charts")

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
                        indicators = calculate_technical_indicators(stock_data)
                        if indicators:
                            fig = create_technical_chart(
                                ticker, stock_data, indicators, indicator_config
                            )
                            if fig:
                                st.pyplot(fig)
                                plt.close(fig)

                                # Display indicator values with safe validation
                                st.subheader("Indicator Values")
                                col1, col2 = st.columns(2)

                                with col1:
                                    if (
                                        "rsi" in indicators
                                        and indicators["rsi"] is not None
                                        and not indicators["rsi"].empty
                                    ):
                                        try:
                                            rsi_value = indicators["rsi"].iloc[-1]
                                            st.metric(
                                                "RSI", f"{rsi_value:.2f}", border=True
                                            )
                                        except Exception:
                                            st.metric("RSI", "N/A", border=True)
                                    else:
                                        st.metric("RSI", "N/A", border=True)
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
                                                    "MACD",
                                                    f"{macd_value:.2f}",
                                                    border=True,
                                                )
                                            else:
                                                st.metric("MACD", "N/A", border=True)
                                        except Exception:
                                            st.metric("MACD", "N/A", border=True)
                                    else:
                                        st.metric("MACD", "N/A", border=True)
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
                                indicators = calculate_technical_indicators(stock_data)
                                if indicators:
                                    fig = create_technical_chart(
                                        ticker, stock_data, indicators, indicator_config
                                    )
                                    if fig:
                                        st.pyplot(fig)
                                        plt.close(fig)

                                        # Display indicator values with safe validation
                                        st.subheader("Indicator Values")
                                        col1, col2 = st.columns(2)

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
                                                    st.metric(
                                                        "RSI",
                                                        f"{rsi_value:.2f}",
                                                        border=True,
                                                    )
                                                except Exception:
                                                    st.metric("RSI", "N/A", border=True)
                                            else:
                                                st.metric("RSI", "N/A", border=True)
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
                                                            "MACD",
                                                            f"{macd_value:.2f}",
                                                            border=True,
                                                        )
                                                    else:
                                                        st.metric(
                                                            "MACD", "N/A", border=True
                                                        )
                                                except Exception:
                                                    st.metric(
                                                        "MACD", "N/A", border=True
                                                    )
                                            else:
                                                st.metric("MACD", "N/A", border=True)
                                                st.caption("MACD calculation failed")

                                else:
                                    st.warning(
                                        "Could not calculate technical indicators"
                                    )
                            else:
                                st.warning(f"No data available for {ticker}")

    # Footer information
    st.caption(
        f"Charts show the {interval_info[current_interval]} of trading data based on your selected interval ({current_interval}). "
        "Heating up signals are based on vnstock technical indicators that identify stocks overheated in the previous trading session."
    )


if __name__ == "__main__":
    main()
