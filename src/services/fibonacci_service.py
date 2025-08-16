"""
Fibonacci Retracement Service for Finance Bro application.
Provides swing detection using SciPy and Fibonacci level calculations.
"""

import pandas as pd
import numpy as np
from scipy.signal import argrelextrema
from typing import Dict, Tuple, Optional
import streamlit as st


@st.cache_data(ttl=300)  # 5-minute cache for fibonacci calculations
def find_swing_points(
    data: pd.Series, order: int = 5, min_distance: int = 10
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Find swing highs and lows using SciPy's argrelextrema.

    Args:
        data: Price series (typically close prices)
        order: Number of points on each side to compare for extrema detection
        min_distance: Minimum bars between swing points

    Returns:
        Tuple of (swing_high_indices, swing_low_indices)
    """
    try:
        if len(data) < order * 3:
            return np.array([]), np.array([])

        # Convert to numpy array for processing
        prices = data.values

        # Find swing highs and lows
        swing_high_idx = argrelextrema(prices, np.greater, order=order)[0]
        swing_low_idx = argrelextrema(prices, np.less, order=order)[0]

        # Filter by minimum distance if specified
        if min_distance > 0:
            swing_high_idx = _filter_by_distance(swing_high_idx, min_distance)
            swing_low_idx = _filter_by_distance(swing_low_idx, min_distance)

        return swing_high_idx, swing_low_idx

    except Exception as e:
        st.warning(f"Error in swing point detection: {str(e)}")
        return np.array([]), np.array([])


def _filter_by_distance(indices: np.ndarray, min_distance: int) -> np.ndarray:
    """
    Filter swing points to maintain minimum distance between them.

    Args:
        indices: Array of swing point indices
        min_distance: Minimum bars between points

    Returns:
        Filtered indices array
    """
    if len(indices) <= 1:
        return indices

    filtered = [indices[0]]  # Always keep first point

    for idx in indices[1:]:
        if idx - filtered[-1] >= min_distance:
            filtered.append(idx)

    return np.array(filtered)


def calculate_fibonacci_levels(
    high: float, low: float, include_extensions: bool = False
) -> Dict[str, float]:
    """
    Calculate Fibonacci retracement and extension levels.

    Args:
        high: Swing high price
        low: Swing low price
        include_extensions: Whether to include Fibonacci extension levels

    Returns:
        Dictionary mapping level names to prices
    """
    if high <= low:
        return {}

    diff = high - low

    # Standard Fibonacci retracement levels
    levels = {
        "0.0%": high,
        "23.6%": high - (diff * 0.236),
        "38.2%": high - (diff * 0.382),
        "50.0%": high - (diff * 0.500),
        "61.8%": high - (diff * 0.618),
        "78.6%": high - (diff * 0.786),
        "100.0%": low,
    }

    # Add extension levels if requested
    if include_extensions:
        extension_levels = {
            "138.2%": high - (diff * 1.382),
            "161.8%": high - (diff * 1.618),
            "200.0%": high - (diff * 2.000),
            "261.8%": high - (diff * 2.618),
        }
        levels.update(extension_levels)

    return levels


def get_recent_swing_fibonacci(
    data: pd.DataFrame,
    lookback_bars: int = 50,
    swing_order: int = 5,
    include_extensions: bool = False,
) -> Optional[Dict]:
    """
    Calculate Fibonacci levels based on most recent significant swing.

    Args:
        data: OHLCV DataFrame with 'high', 'low', 'close' columns (supports both lowercase and capitalized)
        lookback_bars: Number of recent bars to analyze
        swing_order: Sensitivity for swing detection (lower = more sensitive)
        include_extensions: Whether to include extension levels

    Returns:
        Dictionary with swing points and Fibonacci levels, or None if insufficient data
    """
    try:
        if len(data) < lookback_bars:
            lookback_bars = len(data)

        if lookback_bars < swing_order * 3:
            return None

        # Get recent data
        recent_data = data.tail(lookback_bars).copy()

        # Determine column format (vnstock uses capitalized, our tests use lowercase)
        high_col = "High" if "High" in recent_data.columns else "high"
        low_col = "Low" if "Low" in recent_data.columns else "low"
        close_col = "Close" if "Close" in recent_data.columns else "close"

        # Validate required columns exist
        if not all(
            col in recent_data.columns for col in [high_col, low_col, close_col]
        ):
            return None

        # Find swing points using high and low prices
        high_swings, low_swings = find_swing_points(
            recent_data[high_col], order=swing_order
        )

        low_high_swings, low_low_swings = find_swing_points(
            recent_data[low_col], order=swing_order
        )

        # Combine and get most recent significant swing
        if len(high_swings) == 0 or len(low_low_swings) == 0:
            return None

        # Find most recent swing high and corresponding swing low
        recent_high_idx = high_swings[-1] if len(high_swings) > 0 else None
        recent_low_idx = low_low_swings[-1] if len(low_low_swings) > 0 else None

        if recent_high_idx is None or recent_low_idx is None:
            return None

        # Use the most significant swing range
        swing_high = recent_data[high_col].iloc[recent_high_idx]
        swing_low = recent_data[low_col].iloc[recent_low_idx]

        # Ensure we have a valid range
        if swing_high <= swing_low:
            return None

        # Calculate Fibonacci levels
        fib_levels = calculate_fibonacci_levels(
            swing_high, swing_low, include_extensions=include_extensions
        )

        if not fib_levels:
            return None

        return {
            "swing_high": swing_high,
            "swing_low": swing_low,
            "swing_high_date": recent_data.index[recent_high_idx],
            "swing_low_date": recent_data.index[recent_low_idx],
            "fibonacci_levels": fib_levels,
            "range_percent": ((swing_high - swing_low) / swing_low) * 100,
        }

    except Exception as e:
        st.warning(f"Error calculating Fibonacci levels: {str(e)}")
        return None


def get_fibonacci_colors() -> Dict[str, str]:
    """
    Get color mapping for Fibonacci levels using Finance Bro theme.

    Returns:
        Dictionary mapping level names to colors
    """
    # Finance Bro theme colors
    primary = "#56524D"
    secondary = "#2B2523"
    tertiary = "#76706C"
    accent = "#3C3C3C"

    return {
        "0.0%": primary,
        "23.6%": tertiary,
        "38.2%": accent,
        "50.0%": secondary,  # Most important level
        "61.8%": tertiary,  # Golden ratio - important
        "78.6%": accent,
        "100.0%": primary,
        # Extension levels with modified opacity/transparency
        "138.2%": f"{tertiary}80",  # 50% transparency
        "161.8%": f"{accent}80",
        "200.0%": f"{secondary}80",
        "261.8%": f"{primary}80",
    }


def validate_fibonacci_data(data: pd.DataFrame) -> bool:
    """
    Validate that DataFrame has required columns for Fibonacci analysis.

    Args:
        data: DataFrame to validate

    Returns:
        True if data is valid, False otherwise
    """
    # Support both lowercase and capitalized column names (vnstock uses capitalized)
    required_columns = ["high", "low", "close"]
    required_columns_cap = ["High", "Low", "Close"]

    if data.empty:
        return False

    # Check if either lowercase or capitalized columns exist
    has_lowercase = all(col in data.columns for col in required_columns)
    has_capitalized = all(col in data.columns for col in required_columns_cap)

    if not (has_lowercase or has_capitalized):
        return False

    # Check for sufficient data points
    if len(data) < 20:  # Minimum bars for meaningful analysis
        return False

    # Check for valid price data (use whichever column format exists)
    columns_to_check = required_columns if has_lowercase else required_columns_cap
    if data[columns_to_check].isnull().all().any():
        return False

    return True


def format_fibonacci_summary(fib_data: Dict) -> str:
    """
    Format Fibonacci analysis summary for display.

    Args:
        fib_data: Dictionary from get_recent_swing_fibonacci

    Returns:
        Formatted summary string
    """
    if not fib_data:
        return "No Fibonacci levels calculated"

    swing_high = fib_data["swing_high"]
    swing_low = fib_data["swing_low"]
    range_pct = fib_data["range_percent"]

    summary = f"""
    **Fibonacci Analysis Summary**
    - Swing High: {swing_high:,.2f} (on {fib_data["swing_high_date"].strftime("%Y-%m-%d")})
    - Swing Low: {swing_low:,.2f} (on {fib_data["swing_low_date"].strftime("%Y-%m-%d")})
    - Range: {range_pct:.1f}%
    
    **Key Retracement Levels:**
    """

    # Show only key levels for summary
    key_levels = ["38.2%", "50.0%", "61.8%"]
    levels = fib_data["fibonacci_levels"]

    for level in key_levels:
        if level in levels:
            summary += f"\n    - {level}: {levels[level]:,.2f}"

    return summary
