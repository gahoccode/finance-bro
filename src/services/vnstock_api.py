"""
VnStock API Module

Extracted cached data functions from existing pages.
PRESERVES ALL @st.cache_data decorators and vnstock API instantiation patterns exactly as they exist.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from vnstock import Vnstock, Company, Quote, Screener, Fund
import pandas_ta as ta

from ..components.ui_components import inject_custom_success_styling


# ================================
# COMPANY DATA FUNCTIONS
# Extracted from Company_Overview.py
# ================================


@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_ownership_data(symbol):
    """Get ownership data with caching

    Extracted from Company_Overview.py lines 10-18 - EXACT same logic preserved.
    """
    try:
        stock = Vnstock().stock(symbol=symbol, source="VCI")
        company_info = stock.company
        return company_info.shareholders()
    except Exception as e:
        st.error(f"Error fetching ownership data: {str(e)}")
        return pd.DataFrame()


@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_management_data(symbol):
    """Get management data with caching

    Extracted from Company_Overview.py lines 21-28 - EXACT same logic preserved.
    """
    try:
        company = Company(symbol=symbol)
        return company.officers()
    except Exception as e:
        st.error(f"Error fetching management data: {str(e)}")
        return pd.DataFrame()


@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_subsidiaries_data(symbol):
    """Get subsidiaries data with caching

    Extracted from Company_Overview.py lines 31-38 - EXACT same logic preserved.
    """
    try:
        company = Company(symbol=symbol)
        return company.subsidiaries()
    except Exception as e:
        st.error(f"Error fetching subsidiaries data: {str(e)}")
        return pd.DataFrame()


@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_insider_deals_data(symbol):
    """Get insider deals data with caching

    Extracted from Company_Overview.py lines 41-48 - EXACT same logic preserved.
    """
    try:
        stock = Vnstock().stock(symbol=symbol, source="TCBS")
        return stock.company.insider_deals()
    except Exception as e:
        st.error(f"Error fetching insider deals data: {str(e)}")
        return pd.DataFrame()


@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_foreign_trading_data(symbol):
    """Get foreign trading data with caching

    Extracted from Company_Overview.py lines 51-58 - EXACT same logic preserved.
    """
    try:
        company = Company(symbol=symbol)
        return company.trading_stats()
    except Exception as e:
        st.error(f"Error fetching foreign trading data: {str(e)}")
        return pd.DataFrame()


# ================================
# STOCK PRICE DATA FUNCTIONS
# ================================


@st.cache_data(ttl=3600, show_spinner="Loading stock data...")
def fetch_stock_price_data(ticker, start_date, end_date):
    """Fetch stock data with caching to prevent repeated API calls.

    Extracted from Stock_Price_Analysis.py lines 247-264 - EXACT same logic preserved.
    PRESERVES session state assignment for cross-page access.
    """
    stock = Vnstock().stock(symbol=ticker, source="VCI")
    stock_price = stock.quote.history(
        symbol=ticker,
        start=start_date.strftime("%Y-%m-%d"),
        end=end_date.strftime("%Y-%m-%d"),
        interval="1D",
    )

    # Set time column as datetime index
    stock_price["time"] = pd.to_datetime(stock_price["time"])
    stock_price = stock_price.set_index("time")

    # Store in session state for cross-page access
    st.session_state.stock_price_data = stock_price

    return stock_price


@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_portfolio_stock_data(symbols, start_date_str, end_date_str, interval):
    """Cache stock data to avoid repeated API calls.

    Extracted from Portfolio_Optimization.py lines 140-164 - EXACT same logic preserved.
    """
    all_data = {}

    for symbol in symbols:
        try:
            quote = Quote(symbol=symbol)
            historical_data = quote.history(
                start=start_date_str, end=end_date_str, interval=interval, to_df=True
            )

            if not historical_data.empty:
                # Ensure we have the required columns
                if "time" not in historical_data.columns:
                    historical_data["time"] = historical_data.index

                all_data[symbol] = historical_data
        except Exception as e:
            st.error(f"Error fetching data for {symbol}: {e}")

    return all_data


# ================================
# TECHNICAL ANALYSIS FUNCTIONS
# Extracted from Technical_Analysis.py
# ================================


@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_heating_up_stocks():
    """Get stocks with heating_up indicator

    Extracted from Technical_Analysis.py lines 17-58 - EXACT same logic preserved.
    """
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
def get_technical_stock_data(ticker, interval="1D"):
    """Get historical stock data based on interval parameter

    Extracted from Technical_Analysis.py lines 62-115 - EXACT same logic preserved.
    """
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
def calculate_technical_indicators(data: pd.DataFrame) -> dict:
    """Calculate technical indicators using pandas-ta with comprehensive error handling

    Extracted from Technical_Analysis.py lines 120-243 - EXACT same logic preserved.
    """
    indicators = {}
    warnings = []

    # Validate data sufficiency
    if len(data) < 20:
        st.warning(
            f"⚠️ **Insufficient data for technical indicators**: Only {len(data)} data points available. "
            f"Most indicators require minimum 20 points. Try selecting '1W' or '1M' interval for more data."
        )
        return {}

    # Validate required columns
    required_columns = ["Open", "High", "Low", "Close", "Volume"]
    missing_columns = [col for col in required_columns if col not in data.columns]
    if missing_columns:
        st.warning(
            f"⚠️ **Missing required data columns**: {missing_columns}. Cannot calculate technical indicators."
        )
        return {}

    # Calculate RSI with error handling
    try:
        rsi_result = ta.rsi(data["Close"], length=14)
        if rsi_result is not None and not rsi_result.empty:
            indicators["rsi"] = rsi_result
        else:
            warnings.append(
                "RSI calculation returned empty result - insufficient price variation"
            )
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
                warnings.append(
                    "MACD calculation succeeded but missing expected columns"
                )
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
                warnings.append(
                    "Bollinger Bands calculation succeeded but missing expected columns"
                )
        else:
            warnings.append(
                "Bollinger Bands calculation returned empty result - need minimum 20 data points"
            )
    except Exception as e:
        warnings.append(f"Bollinger Bands calculation failed: {str(e)}")

    # Calculate OBV with error handling
    try:
        obv_result = ta.obv(data["Close"], data["Volume"])
        if obv_result is not None and not obv_result.empty:
            indicators["obv"] = obv_result
        else:
            warnings.append(
                "OBV calculation returned empty result - volume data may be insufficient"
            )
    except Exception as e:
        warnings.append(f"OBV calculation failed: {str(e)}")

    # Calculate ADX with enhanced error handling and data validation
    try:
        # ADX requires significant data for proper calculation
        if len(data) < 30:  # ADX needs more data than just the length parameter
            warnings.append(
                "ADX calculation skipped - need minimum 30 data points for reliable calculation"
            )
        else:
            # Validate High/Low/Close data quality
            high_low_valid = (data["High"] >= data["Low"]).all()
            price_range_valid = (
                (data["High"] > 0).all()
                and (data["Low"] > 0).all()
                and (data["Close"] > 0).all()
            )

            if not high_low_valid:
                warnings.append(
                    "ADX calculation failed - High prices must be >= Low prices"
                )
            elif not price_range_valid:
                warnings.append(
                    "ADX calculation failed - All price values must be positive"
                )
            else:
                # Check for sufficient price variation
                high_range = data["High"].max() - data["High"].min()
                low_range = data["Low"].max() - data["Low"].min()

                if high_range == 0 or low_range == 0:
                    warnings.append(
                        "ADX calculation failed - insufficient price variation in High/Low data"
                    )
                else:
                    adx_result = ta.adx(
                        data["High"], data["Low"], data["Close"], length=14
                    )
                    if adx_result is not None and not adx_result.empty:
                        # Verify expected columns exist
                        expected_cols = ["ADX_14", "DMP_14", "DMN_14"]
                        if all(col in adx_result.columns for col in expected_cols):
                            # Additional check for valid ADX values (should be 0-100)
                            adx_values = adx_result["ADX_14"].dropna()
                            if len(adx_values) > 0 and not adx_values.isna().all():
                                indicators["adx"] = adx_result
                            else:
                                warnings.append(
                                    "ADX calculation returned invalid values - all NaN results"
                                )
                        else:
                            warnings.append(
                                "ADX calculation succeeded but missing expected columns"
                            )
                    else:
                        warnings.append(
                            "ADX calculation returned empty result - insufficient data quality"
                        )
    except ValueError as e:
        if "zero-size array" in str(e):
            warnings.append(
                "ADX calculation failed - zero-size array error (insufficient valid data points)"
            )
        else:
            warnings.append(f"ADX calculation failed with ValueError: {str(e)}")
    except Exception as e:
        warnings.append(f"ADX calculation failed: {str(e)}")

    # Display warnings to user
    if warnings:
        warning_text = "⚠️ **Technical Indicator Issues:**\n" + "\n".join(
            f"• {w}" for w in warnings
        )
        st.warning(warning_text)

    # Show success summary
    if indicators:
        # Apply custom CSS styling for success alerts
        inject_custom_success_styling()

        success_indicators = list(indicators.keys())
        st.success(
            f"✅ **Successfully calculated indicators**: {', '.join(success_indicators).upper()}"
        )

    return indicators


# ================================
# SCREENER DATA FUNCTIONS
# Extracted from Screener.py
# ================================


@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_screener_data(params, source="TCBS", limit=1700):
    """Get screener data with caching

    Extracted from Screener.py lines 49-58 - EXACT same logic preserved.
    """
    try:
        screener = Screener(source=source)
        result = screener.stock(params=params, limit=limit, lang="en")
        return result
    except Exception as e:
        st.error(f"Error fetching screener data: {str(e)}")
        st.error(f"API parameters used: {params}")
        return pd.DataFrame()


# ================================
# UTILITY FUNCTIONS
# ================================


def clear_vnstock_cache():
    """Clear all vnstock-related cache.

    Convenience function to clear all cached API data.
    """
    st.cache_data.clear()


def get_cache_info():
    """Get information about cached functions.

    Returns metadata about the cached vnstock functions.
    """
    cached_functions = {
        "Company Data": [
            "get_ownership_data (1h TTL)",
            "get_management_data (1h TTL)",
            "get_subsidiaries_data (1h TTL)",
            "get_insider_deals_data (1h TTL)",
            "get_foreign_trading_data (1h TTL)",
        ],
        "Stock Price Data": [
            "fetch_stock_price_data (1h TTL)",
            "fetch_portfolio_stock_data (1h TTL)",
        ],
        "Technical Analysis": [
            "get_heating_up_stocks (5min TTL)",
            "get_technical_stock_data (5min TTL)",
            "calculate_technical_indicators (5min TTL)",
        ],
        "Screener Data": ["get_screener_data (1h TTL)"],
    }

    return cached_functions


# ================================
# FUND DATA FUNCTIONS
# Based on Reference/funds.md
# ================================


@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_fund_listing():
    """Get list of all funds with caching

    Based on Reference/funds.md lines 1-4
    """
    try:
        fund = Fund()
        fund_list = fund.listing()
        return fund_list
    except Exception as e:
        st.error(f"Error fetching fund listing: {str(e)}")
        return pd.DataFrame()


@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_fund_nav_report(fund_code):
    """Get NAV report for specific fund with caching

    Based on Reference/funds.md lines 22-26
    """
    try:
        fund = Fund()
        fund_details = fund.details.nav_report(fund_code)
        if not fund_details.empty:
            fund_details["date"] = pd.to_datetime(fund_details["date"])
        return fund_details
    except Exception as e:
        st.error(f"Error fetching NAV report for {fund_code}: {str(e)}")
        return pd.DataFrame()


@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_fund_asset_allocation(fund_code):
    """Get asset allocation for specific fund with caching

    Based on Reference/funds.md lines 82
    """
    try:
        fund = Fund()
        asset_allocation = fund.details.asset_holding(fund_code)
        return asset_allocation
    except Exception as e:
        st.error(f"Error fetching asset allocation for {fund_code}: {str(e)}")
        return pd.DataFrame()


@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_fund_industry_allocation(fund_code):
    """Get industry allocation for specific fund with caching

    Based on Reference/funds.md lines 85
    """
    try:
        fund = Fund()
        industry_allocation = fund.details.industry_holding(fund_code)
        return industry_allocation
    except Exception as e:
        st.error(f"Error fetching industry allocation for {fund_code}: {str(e)}")
        return pd.DataFrame()
