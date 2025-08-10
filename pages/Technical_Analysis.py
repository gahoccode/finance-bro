import streamlit as st
import pandas as pd
import numpy as np
from vnstock import Screener, Vnstock
import mplfinance as mpf
import pandas_ta as ta
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import io
import base64

st.set_page_config(
    page_title="Technical Analysis - Finance Bro", page_icon="📊", layout="wide"
)


@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_heating_up_stocks():
    """Get stocks with heating_up indicator"""

    # Initialize screener and get data
    screener = Screener(show_log=False)
    screener_df = screener.stock(
        params={"exchangeName": "HOSE,HNX,UPCOM"}, limit=1700, lang="en"
    )

    # Filter for heating_up condition only
    filtered_stocks = screener_df[
        screener_df["heating_up"] == "Overheated in previous trading session"
    ]

    # Select only required columns
    result_columns = [
        "ticker",
        "industry",
        "exchange",
        "heating_up",
        "uptrend",
        "breakout",
        "tcbs_buy_sell_signal",
        "pct_1y_from_peak",
        "pct_away_from_hist_peak",
        "pct_1y_from_bottom",
        "pct_off_hist_bottom",
        "active_buy_pct",
        "strong_buy_pct",
        "market_cap",
        "avg_trading_value_5d",
        "total_trading_value",
        "foreign_transaction",
        "num_increase_continuous_day",
    ]

    # Only include columns that exist in the DataFrame
    available_columns = [
        col for col in result_columns if col in filtered_stocks.columns
    ]

    return filtered_stocks[available_columns]


@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_stock_data(ticker, interval="1D"):
    """Get historical stock data based on interval parameter"""
    try:
        # Calculate days based on interval (optimized for technical indicators)
        if interval == "1D":
            days = 90  # ~3 months (sufficient for ADX and all indicators)
        elif interval == "1W":
            days = 180  # ~6 months
        elif interval == "1M":
            days = 730  # ~2 years

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Use the same pattern as Stock_Price_Analysis.py
        stock = Vnstock().stock(symbol=ticker, source="VCI")
        data = stock.quote.history(
            symbol=ticker,
            start=start_date.strftime("%Y-%m-%d"),
            end=end_date.strftime("%Y-%m-%d"),
            interval=interval,
        )

        if data is not None and not data.empty:
            # Prepare data for mplfinance
            data = data.copy()

            # Set time column as datetime index
            if "time" in data.columns:
                data["time"] = pd.to_datetime(data["time"])
                data = data.set_index("time")

            # mplfinance expects specific column names (capitalize first letter)
            column_mapping = {
                "open": "Open",
                "high": "High",
                "low": "Low",
                "close": "Close",
                "volume": "Volume",
            }

            # Rename columns to match mplfinance expectations
            data = data.rename(columns=column_mapping)
            required_columns = ["Open", "High", "Low", "Close", "Volume"]

            # Check if all required columns exist and return them
            if all(col in data.columns for col in required_columns):
                return data[required_columns]

        return pd.DataFrame()

    except Exception as e:
        st.error(f"Error fetching data for {ticker}: {str(e)}")
        return pd.DataFrame()


@st.cache_data(ttl=300)  # Cache for 5 minutes
def calculate_indicators(data: pd.DataFrame) -> dict:
    """Calculate technical indicators using pandas-ta with comprehensive error handling"""
    indicators = {}
    warnings = []
    
    # Validate data sufficiency
    if len(data) < 20:
        st.warning(f"⚠️ **Insufficient data for technical indicators**: Only {len(data)} data points available. "
                  f"Most indicators require minimum 20 points. Try selecting '1W' or '1M' interval for more data.")
        return {}
    
    # Validate required columns
    required_columns = ["Open", "High", "Low", "Close", "Volume"]
    missing_columns = [col for col in required_columns if col not in data.columns]
    if missing_columns:
        st.warning(f"⚠️ **Missing required data columns**: {missing_columns}. Cannot calculate technical indicators.")
        return {}
    
    # Calculate RSI with error handling
    try:
        rsi_result = ta.rsi(data["Close"], length=14)
        if rsi_result is not None and not rsi_result.empty:
            indicators["rsi"] = rsi_result
        else:
            warnings.append("RSI calculation returned empty result - insufficient price variation")
    except Exception as e:
        warnings.append(f"RSI calculation failed: {str(e)}")
    
    # Calculate MACD with error handling  
    try:
        macd_result = ta.macd(data["Close"])
        if macd_result is not None and not macd_result.empty:
            # Verify expected columns exist
            expected_cols = ["MACD_12_26_9", "MACDs_12_26_9", "MACDh_12_26_9"]
            if all(col in macd_result.columns for col in expected_cols):
                indicators["macd"] = macd_result
            else:
                warnings.append("MACD calculation succeeded but missing expected columns")
        else:
            warnings.append("MACD calculation returned empty result")
    except Exception as e:
        warnings.append(f"MACD calculation failed: {str(e)}")
    
    # Calculate Bollinger Bands with error handling
    try:
        bb_result = ta.bbands(data["Close"], length=20)
        if bb_result is not None and not bb_result.empty:
            # Verify expected columns exist
            expected_cols = ["BBL_20_2.0", "BBM_20_2.0", "BBU_20_2.0"]
            if all(col in bb_result.columns for col in expected_cols):
                indicators["bbands"] = bb_result
            else:
                warnings.append("Bollinger Bands calculation succeeded but missing expected columns")
        else:
            warnings.append("Bollinger Bands calculation returned empty result - need minimum 20 data points")
    except Exception as e:
        warnings.append(f"Bollinger Bands calculation failed: {str(e)}")
    
    # Calculate OBV with error handling
    try:
        obv_result = ta.obv(data["Close"], data["Volume"])
        if obv_result is not None and not obv_result.empty:
            indicators["obv"] = obv_result
        else:
            warnings.append("OBV calculation returned empty result - volume data may be insufficient")
    except Exception as e:
        warnings.append(f"OBV calculation failed: {str(e)}")
    
    # Calculate ADX with enhanced error handling and data validation
    try:
        # ADX requires significant data for proper calculation
        if len(data) < 30:  # ADX needs more data than just the length parameter
            warnings.append("ADX calculation skipped - need minimum 30 data points for reliable calculation")
        else:
            # Validate High/Low/Close data quality
            high_low_valid = (data["High"] >= data["Low"]).all()
            price_range_valid = (data["High"] > 0).all() and (data["Low"] > 0).all() and (data["Close"] > 0).all()
            
            if not high_low_valid:
                warnings.append("ADX calculation failed - High prices must be >= Low prices")
            elif not price_range_valid:
                warnings.append("ADX calculation failed - All price values must be positive")
            else:
                # Check for sufficient price variation
                high_range = data["High"].max() - data["High"].min()
                low_range = data["Low"].max() - data["Low"].min()
                
                if high_range == 0 or low_range == 0:
                    warnings.append("ADX calculation failed - insufficient price variation in High/Low data")
                else:
                    adx_result = ta.adx(data["High"], data["Low"], data["Close"], length=14)
                    if adx_result is not None and not adx_result.empty:
                        # Verify expected columns exist
                        expected_cols = ["ADX_14", "DMP_14", "DMN_14"]
                        if all(col in adx_result.columns for col in expected_cols):
                            # Additional check for valid ADX values (should be 0-100)
                            adx_values = adx_result["ADX_14"].dropna()
                            if len(adx_values) > 0 and not adx_values.isna().all():
                                indicators["adx"] = adx_result
                            else:
                                warnings.append("ADX calculation returned invalid values - all NaN results")
                        else:
                            warnings.append("ADX calculation succeeded but missing expected columns")
                    else:
                        warnings.append("ADX calculation returned empty result - insufficient data quality")
    except ValueError as e:
        if "zero-size array" in str(e):
            warnings.append("ADX calculation failed - zero-size array error (insufficient valid data points)")
        else:
            warnings.append(f"ADX calculation failed with ValueError: {str(e)}")
    except Exception as e:
        warnings.append(f"ADX calculation failed: {str(e)}")
    
    # Display warnings to user
    if warnings:
        warning_text = "⚠️ **Technical Indicator Issues:**\n" + "\n".join(f"• {w}" for w in warnings)
        st.warning(warning_text)
    
    # Show success summary
    if indicators:
        success_indicators = list(indicators.keys())
        st.success(f"✅ **Successfully calculated indicators**: {', '.join(success_indicators).upper()}")
    
    return indicators


def create_technical_chart(
    ticker: str, data: pd.DataFrame, indicators: dict, config: dict
) -> plt.Figure:
    """Create technical analysis chart with indicators using mplfinance with safe validation"""

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
                            mpf.make_addplot(bb["BBL_20_2.0"], color="green", width=0.7),
                        ]
                    )
                except Exception as e:
                    skipped_indicators.append(f"Bollinger Bands: {str(e)}")
            else:
                skipped_indicators.append("Bollinger Bands: Missing required columns")
        else:
            skipped_indicators.append("Bollinger Bands: Calculation failed or unavailable")

    # RSI Panel - Safe validation
    if config.get("show_rsi", True):
        if "rsi" in indicators and indicators["rsi"] is not None:
            rsi = indicators["rsi"]
            if not rsi.empty:
                try:
                    addplots.append(
                        mpf.make_addplot(rsi, panel=panels, color="purple", ylabel="RSI")
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
                                macd["MACD_12_26_9"], panel=panels, color="blue", ylabel="MACD"
                            ),
                            mpf.make_addplot(macd["MACDs_12_26_9"], panel=panels, color="red"),
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
                        mpf.make_addplot(obv, panel=panels, color="orange", ylabel="OBV")
                    )
                    panels += 1
                except Exception as e:
                    skipped_indicators.append(f"OBV: {str(e)}")
            else:
                skipped_indicators.append("OBV: Empty data")
        else:
            skipped_indicators.append("OBV: Calculation failed or unavailable")

    # ADX Panel - Safe validation
    if config.get("show_adx", True):
        if "adx" in indicators and indicators["adx"] is not None:
            adx = indicators["adx"]
            required_cols = ["ADX_14", "DMP_14", "DMN_14"]
            if all(col in adx.columns for col in required_cols):
                try:
                    addplots.extend(
                        [
                            mpf.make_addplot(
                                adx["ADX_14"], panel=panels, color="brown", ylabel="ADX"
                            ),
                            mpf.make_addplot(adx["DMP_14"], panel=panels, color="green"),
                            mpf.make_addplot(adx["DMN_14"], panel=panels, color="red"),
                        ]
                    )
                    panels += 1
                except Exception as e:
                    skipped_indicators.append(f"ADX: {str(e)}")
            else:
                skipped_indicators.append("ADX: Missing required columns")
        else:
            skipped_indicators.append("ADX: Calculation failed or unavailable")
    
    # Show warning for skipped indicators
    if skipped_indicators:
        warning_text = "⚠️ **Skipped indicators in chart:**\n" + "\n".join(f"• {s}" for s in skipped_indicators)
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


def main():
    st.title("📊 Technical Analysis")
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
        st.subheader("📊 Chart Configuration")

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
        st.subheader("📈 Technical Indicators")
        show_bb = st.checkbox("Bollinger Bands", value=True)
        show_rsi = st.checkbox("RSI", value=True)
        show_macd = st.checkbox("MACD", value=True)
        show_obv = st.checkbox("OBV", value=False)
        show_adx = st.checkbox("ADX", value=False)

        # Indicator parameters
        bb_period = st.slider("BB Period", 10, 50, 20)
        rsi_period = st.slider("RSI Period", 5, 30, 14)
        adx_period = st.slider("ADX Period", 5, 30, 14)

        # Store in session state for persistence
        if "ta_interval" not in st.session_state:
            st.session_state.ta_interval = "1D"

        # Add a button to clear cache if needed
        if st.button("🔄 Refresh Data", help="Clear cached data and reload"):
            st.cache_data.clear()
            st.rerun()

    # Load heating up stocks
    with st.spinner("🔍 Scanning market for heating up stocks..."):
        try:
            heating_stocks = get_heating_up_stocks()
        except Exception as e:
            st.error(f"Error loading heating up stocks: {str(e)}")
            st.stop()

    if heating_stocks.empty:
        st.info(
            "🔥 No stocks showing 'Overheated in previous trading session' signal today."
        )
        st.stop()

    # Display results summary
    st.success(f"🔥 Found **{len(heating_stocks)}** stocks with heating up signals!")

    # Display the heating stocks DataFrame
    st.subheader("📋 Heating Up Stocks Summary")
    st.dataframe(heating_stocks, use_container_width=True, height=300)

    # Technical indicators summary
    st.subheader("📊 Technical Indicators Summary")

    # Create columns for indicator toggles
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Bollinger Bands", "ON" if show_bb else "OFF")
    with col2:
        st.metric("RSI", "ON" if show_rsi else "OFF")
    with col3:
        st.metric("MACD", "ON" if show_macd else "OFF")
    with col4:
        st.metric("OBV", "ON" if show_obv else "OFF")
    with col5:
        st.metric("ADX", "ON" if show_adx else "OFF")

    # Charts section with technical indicators
    st.subheader("📈 Advanced Technical Analysis Charts")

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
        "show_adx": show_adx,
    }

    # Create tabs for better organization if many stocks
    tickers = heating_stocks["ticker"].tolist()

    if len(tickers) <= 5:
        # Display all charts directly if 5 or fewer stocks
        for ticker in tickers:
            with st.expander(f"📊 {ticker} - Technical Analysis", expanded=True):
                with st.spinner(
                    f"Loading technical analysis for {ticker} ({current_interval})..."
                ):
                    stock_data = get_stock_data(ticker, interval=current_interval)

                    if not stock_data.empty:
                        indicators = calculate_indicators(stock_data)
                        if indicators:
                            fig = create_technical_chart(
                                ticker, stock_data, indicators, indicator_config
                            )
                            if fig:
                                st.pyplot(fig)
                                plt.close(fig)

                                # Display indicator values with safe validation
                                st.subheader("📊 Indicator Values")
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    if "rsi" in indicators and indicators["rsi"] is not None and not indicators["rsi"].empty:
                                        try:
                                            rsi_value = indicators["rsi"].iloc[-1]
                                            st.metric("RSI", f"{rsi_value:.2f}")
                                        except Exception:
                                            st.metric("RSI", "N/A")
                                    else:
                                        st.metric("RSI", "N/A")
                                        st.caption("⚠️ RSI calculation failed")
                                        
                                with col2:
                                    if "macd" in indicators and indicators["macd"] is not None and not indicators["macd"].empty:
                                        try:
                                            if "MACD_12_26_9" in indicators["macd"].columns:
                                                macd_value = indicators["macd"]["MACD_12_26_9"].iloc[-1]
                                                st.metric("MACD", f"{macd_value:.2f}")
                                            else:
                                                st.metric("MACD", "N/A")
                                        except Exception:
                                            st.metric("MACD", "N/A")
                                    else:
                                        st.metric("MACD", "N/A")
                                        st.caption("⚠️ MACD calculation failed")
                                        
                                with col3:
                                    if "adx" in indicators and indicators["adx"] is not None and not indicators["adx"].empty:
                                        try:
                                            if "ADX_14" in indicators["adx"].columns:
                                                adx_value = indicators["adx"]["ADX_14"].iloc[-1]
                                                st.metric("ADX", f"{adx_value:.2f}")
                                            else:
                                                st.metric("ADX", "N/A")
                                        except Exception:
                                            st.metric("ADX", "N/A")
                                    else:
                                        st.metric("ADX", "N/A")
                                        st.caption("⚠️ ADX calculation failed")
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
                    with st.expander(
                        f"📊 {ticker} - Technical Analysis", expanded=False
                    ):
                        with st.spinner(
                            f"Loading technical analysis for {ticker} ({current_interval})..."
                        ):
                            stock_data = get_stock_data(
                                ticker, interval=current_interval
                            )

                            if not stock_data.empty:
                                indicators = calculate_indicators(stock_data)
                                if indicators:
                                    fig = create_technical_chart(
                                        ticker, stock_data, indicators, indicator_config
                                    )
                                    if fig:
                                        st.pyplot(fig)
                                        plt.close(fig)

                                        # Display indicator values with safe validation
                                        st.subheader("📊 Indicator Values")
                                        col1, col2, col3 = st.columns(3)
                                        
                                        with col1:
                                            if "rsi" in indicators and indicators["rsi"] is not None and not indicators["rsi"].empty:
                                                try:
                                                    rsi_value = indicators["rsi"].iloc[-1]
                                                    st.metric("RSI", f"{rsi_value:.2f}")
                                                except Exception:
                                                    st.metric("RSI", "N/A")
                                            else:
                                                st.metric("RSI", "N/A")
                                                st.caption("⚠️ RSI calculation failed")
                                                
                                        with col2:
                                            if "macd" in indicators and indicators["macd"] is not None and not indicators["macd"].empty:
                                                try:
                                                    if "MACD_12_26_9" in indicators["macd"].columns:
                                                        macd_value = indicators["macd"]["MACD_12_26_9"].iloc[-1]
                                                        st.metric("MACD", f"{macd_value:.2f}")
                                                    else:
                                                        st.metric("MACD", "N/A")
                                                except Exception:
                                                    st.metric("MACD", "N/A")
                                            else:
                                                st.metric("MACD", "N/A")
                                                st.caption("⚠️ MACD calculation failed")
                                                
                                        with col3:
                                            if "adx" in indicators and indicators["adx"] is not None and not indicators["adx"].empty:
                                                try:
                                                    if "ADX_14" in indicators["adx"].columns:
                                                        adx_value = indicators["adx"]["ADX_14"].iloc[-1]
                                                        st.metric("ADX", f"{adx_value:.2f}")
                                                    else:
                                                        st.metric("ADX", "N/A")
                                                except Exception:
                                                    st.metric("ADX", "N/A")
                                            else:
                                                st.metric("ADX", "N/A")
                                                st.caption("⚠️ ADX calculation failed")
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
    - **RSI**: Relative Strength Index (momentum oscillator)
    - **MACD**: Moving Average Convergence Divergence (trend-following)
    - **Bollinger Bands**: Price volatility and potential reversal points
    - **OBV**: On-Balance Volume (volume flow indicator)
    - **ADX**: Average Directional Index (trend strength)
    """)


if __name__ == "__main__":
    main()
