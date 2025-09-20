"""
Technical Analysis Indicators Module

Manual implementation of technical indicators to replace pandas-ta dependency.
Provides RSI, MACD, Bollinger Bands, and OBV with comprehensive error handling.
"""

import streamlit as st
import pandas as pd

from ..components.ui_components import inject_custom_success_styling


def manual_obv(close_prices: pd.Series, volume: pd.Series) -> pd.Series:
    """
    Calculate On-Balance Volume (OBV) manually.
    
    OBV = Previous OBV + Volume (if Close > Previous Close)
    OBV = Previous OBV - Volume (if Close < Previous Close)  
    OBV = Previous OBV (if Close = Previous Close)
    
    Args:
        close_prices: Series of closing prices
        volume: Series of volume data
        
    Returns:
        Series with OBV values, indexed same as input
    """
    if len(close_prices) != len(volume):
        raise ValueError("Close prices and volume must have same length")

    if len(close_prices) < 2:
        raise ValueError("Need at least 2 data points for OBV calculation")

    # Calculate price direction: 1 for up, -1 for down, 0 for unchanged
    price_direction = pd.Series(index=close_prices.index, dtype=float)
    price_direction.iloc[0] = 0  # First value has no previous price

    for i in range(1, len(close_prices)):
        if close_prices.iloc[i] > close_prices.iloc[i-1]:
            price_direction.iloc[i] = 1
        elif close_prices.iloc[i] < close_prices.iloc[i-1]:
            price_direction.iloc[i] = -1
        else:
            price_direction.iloc[i] = 0

    # Calculate OBV
    obv = pd.Series(index=close_prices.index, dtype=float)
    obv.iloc[0] = volume.iloc[0]  # First OBV value equals first volume

    for i in range(1, len(close_prices)):
        volume_change = price_direction.iloc[i] * volume.iloc[i]
        obv.iloc[i] = obv.iloc[i-1] + volume_change

    return obv


def manual_bollinger_bands(close_prices: pd.Series, period: int = 20, std_dev: float = 2.0) -> pd.DataFrame:
    """
    Calculate Bollinger Bands manually.
    
    Middle Band = Simple Moving Average (SMA)
    Upper Band = SMA + (std_dev * Standard Deviation)
    Lower Band = SMA - (std_dev * Standard Deviation)
    
    Args:
        close_prices: Series of closing prices
        period: Number of periods for moving average (default: 20)
        std_dev: Number of standard deviations (default: 2.0)
        
    Returns:
        DataFrame with columns: BBL_20_2.0, BBM_20_2.0, BBU_20_2.0
    """
    if len(close_prices) < period:
        raise ValueError(f"Need at least {period} data points for Bollinger Bands calculation")

    # Calculate Simple Moving Average (Middle Band)
    sma = close_prices.rolling(window=period).mean()

    # Calculate Rolling Standard Deviation
    rolling_std = close_prices.rolling(window=period).std()

    # Calculate Upper and Lower Bands
    upper_band = sma + (std_dev * rolling_std)
    lower_band = sma - (std_dev * rolling_std)

    # Create DataFrame with pandas-ta compatible column names
    result = pd.DataFrame({
        'BBL_20_2.0': lower_band,
        'BBM_20_2.0': sma,
        'BBU_20_2.0': upper_band
    }, index=close_prices.index)

    return result


def manual_rsi(close_prices: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate Relative Strength Index (RSI) manually using exponential moving average.
    
    RSI = 100 - (100 / (1 + RS))
    RS = Average Gain / Average Loss
    
    Args:
        close_prices: Series of closing prices
        period: Number of periods for calculation (default: 14)
        
    Returns:
        Series with RSI values (0-100 scale)
    """
    if len(close_prices) < period + 1:
        raise ValueError(f"Need at least {period + 1} data points for RSI calculation")

    # Calculate price changes
    price_changes = close_prices.diff()

    # Separate gains and losses
    gains = price_changes.where(price_changes > 0, 0)
    losses = -price_changes.where(price_changes < 0, 0)

    # Calculate exponential moving averages
    # Use alpha = 1/period for EMA (same as pandas-ta default)
    alpha = 1.0 / period

    avg_gains = gains.ewm(alpha=alpha, adjust=False).mean()
    avg_losses = losses.ewm(alpha=alpha, adjust=False).mean()

    # Calculate RS and RSI
    rs = avg_gains / avg_losses
    rsi = 100 - (100 / (1 + rs))

    # Set name for compatibility
    rsi.name = 'RSI_14'

    return rsi


def manual_macd(close_prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    """
    Calculate MACD (Moving Average Convergence Divergence) manually.
    
    MACD Line = EMA(fast) - EMA(slow)
    Signal Line = EMA(MACD Line, signal periods)
    Histogram = MACD Line - Signal Line
    
    Args:
        close_prices: Series of closing prices
        fast: Fast EMA period (default: 12)
        slow: Slow EMA period (default: 26)
        signal: Signal line EMA period (default: 9)
        
    Returns:
        DataFrame with columns: MACD_12_26_9, MACDs_12_26_9, MACDh_12_26_9
    """
    if len(close_prices) < slow + signal:
        raise ValueError(f"Need at least {slow + signal} data points for MACD calculation")

    # Calculate EMAs
    ema_fast = close_prices.ewm(span=fast, adjust=False).mean()
    ema_slow = close_prices.ewm(span=slow, adjust=False).mean()

    # Calculate MACD line
    macd_line = ema_fast - ema_slow

    # Calculate Signal line (EMA of MACD line)
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()

    # Calculate Histogram
    histogram = macd_line - signal_line

    # Create DataFrame with pandas-ta compatible column names
    result = pd.DataFrame({
        'MACD_12_26_9': macd_line,
        'MACDs_12_26_9': signal_line,
        'MACDh_12_26_9': histogram
    }, index=close_prices.index)

    return result


@st.cache_data(ttl=300)  # Cache for 5 minutes
def calculate_technical_indicators(data: pd.DataFrame) -> tuple[dict, list, bool]:
    """Calculate technical indicators using manual implementations.
    
    Provides RSI, MACD, Bollinger Bands, and OBV with comprehensive error handling.
    
    Args:
        data: DataFrame with OHLCV columns
        
    Returns:
        tuple: (indicators_dict, warnings_list, has_success)
            - indicators_dict: Dictionary of calculated indicators
            - warnings_list: List of warning messages to display
            - has_success: Boolean indicating if any indicators were calculated successfully
    """
    indicators = {}
    warnings = []

    # Validate data sufficiency
    if len(data) < 20:
        warnings.append(
            f"⚠️ **Insufficient data for technical indicators**: Only {len(data)} data points available. "
            f"Most indicators require minimum 20 points. Try selecting '1W' or '1M' interval for more data."
        )
        return {}, warnings, False

    # Validate required columns
    required_columns = ["Open", "High", "Low", "Close", "Volume"]
    missing_columns = [col for col in required_columns if col not in data.columns]
    if missing_columns:
        warnings.append(
            f"⚠️ **Missing required data columns**: {missing_columns}. Cannot calculate technical indicators."
        )
        return {}, warnings, False

    # Calculate OBV with error handling
    try:
        obv_result = manual_obv(data["Close"], data["Volume"])
        if obv_result is not None and not obv_result.empty:
            indicators["obv"] = obv_result
        else:
            warnings.append(
                "OBV calculation returned empty result - volume data may be insufficient"
            )
    except Exception as e:
        warnings.append(f"OBV calculation failed: {str(e)}")

    # Calculate Bollinger Bands with error handling
    try:
        bb_result = manual_bollinger_bands(data["Close"], period=20, std_dev=2.0)
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

    # Calculate RSI with error handling
    try:
        rsi_result = manual_rsi(data["Close"], period=14)
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
        macd_result = manual_macd(data["Close"], fast=12, slow=26, signal=9)
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

    # Manual implementation provides 4 core technical indicators

    # Return indicators data along with warnings and success status
    has_success = len(indicators) > 0
    return indicators, warnings, has_success


def display_indicators_status(warnings: list, has_success: bool, indicator_names: list) -> None:
    """Display technical indicators status messages to the user.
    
    Handles all Streamlit UI display logic that was moved out of the cached 
    calculate_technical_indicators function to fix caching compatibility.
    
    Args:
        warnings: List of warning messages to display
        has_success: Whether any indicators were calculated successfully  
        indicator_names: List of successfully calculated indicator names
    """
    # Display warnings to user
    if warnings:
        # Handle both single warning strings and lists of warnings
        if len(warnings) == 1 and not warnings[0].startswith("⚠️ **Technical Indicator Issues:**"):
            # Single validation error (insufficient data or missing columns)
            st.warning(warnings[0])
        else:
            # Multiple indicator calculation warnings
            warning_text = "⚠️ **Technical Indicator Issues:**\n" + "\n".join(
                f"• {w}" for w in warnings
            )
            st.warning(warning_text)

    # Show success summary
    if has_success and indicator_names:
        # Apply custom CSS styling for success alerts
        inject_custom_success_styling()

        st.success(
            f"✅ **Successfully calculated indicators**: {', '.join(indicator_names).upper()}"
        )
