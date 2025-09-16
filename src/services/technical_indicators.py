"""
Technical Analysis Indicators Module

Contains technical analysis functions that depend on pandas-ta.
Isolated from vnstock_api.py to prevent import failures when pandas-ta is unavailable.
"""

import streamlit as st
import pandas as pd

try:
    import pandas_ta as ta

    PANDAS_TA_AVAILABLE = True
except ImportError:
    ta = None
    PANDAS_TA_AVAILABLE = False

from ..components.ui_components import inject_custom_success_styling


@st.cache_data(ttl=300)  # Cache for 5 minutes
def calculate_technical_indicators(data: pd.DataFrame) -> tuple:
    """Calculate technical indicators using pandas-ta with comprehensive error handling

    Extracted from vnstock_api.py lines 288-457 - EXACT same logic preserved.
    """
    if not PANDAS_TA_AVAILABLE:
        return {}, ["pandas-ta library is not installed or compatible"], False

    indicators = {}
    warnings = []

    # Validate data sufficiency
    if len(data) < 20:
        warnings.append(
            f"Insufficient data for technical indicators: Only {len(data)} data points available. Most indicators require minimum 20 points."
        )
        return {}, warnings, False

    # Validate required columns
    required_columns = ["Open", "High", "Low", "Close", "Volume"]
    missing_columns = [col for col in required_columns if col not in data.columns]
    if missing_columns:
        warnings.append(
            f"Missing required data columns: {missing_columns}. Cannot calculate technical indicators."
        )
        return {}, warnings, False

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

    # Return indicators, warnings, and success status
    has_success = bool(indicators)
    return indicators, warnings, has_success


def display_indicators_status(
    warnings: list, has_success: bool, indicator_keys: list
) -> None:
    """Display technical indicator status messages to user

    Args:
        warnings: List of warning messages from indicator calculations
        has_success: Boolean indicating if any indicators were successfully calculated
        indicator_keys: List of successfully calculated indicator names
    """
    # Display warnings to user
    if warnings:
        warning_text = "⚠️ **Technical Indicator Issues:**\n" + "\n".join(
            f"• {w}" for w in warnings
        )
        st.warning(warning_text)

    # Show success summary
    if has_success and indicator_keys:
        # Apply custom CSS styling for success alerts
        inject_custom_success_styling()

        success_indicators = [key.upper() for key in indicator_keys]
        st.success(
            f"✅ **Successfully calculated indicators**: {', '.join(success_indicators)}"
        )
