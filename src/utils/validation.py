"""
Input validation utilities for Finance Bro application.
Provides validation functions for user inputs and data integrity checks.
"""

import pandas as pd
from datetime import datetime
from typing import List, Dict, Any


def validate_stock_symbol(symbol: str, available_symbols: List[str]) -> Dict[str, Any]:
    """
    Validate stock symbol against available symbols list.

    Returns:
        Dict with 'valid' boolean and 'message' string
    """
    if not symbol:
        return {"valid": False, "message": "Stock symbol cannot be empty"}

    if not isinstance(symbol, str):
        return {"valid": False, "message": "Stock symbol must be a string"}

    symbol = symbol.strip().upper()

    if len(symbol) < 2 or len(symbol) > 5:
        return {"valid": False, "message": "Stock symbol must be 2-5 characters long"}

    if symbol not in available_symbols:
        return {
            "valid": False,
            "message": f"Stock symbol '{symbol}' not found in available symbols",
        }

    return {"valid": True, "message": "Valid stock symbol"}


def validate_date_range(start_date: datetime, end_date: datetime) -> Dict[str, Any]:
    """
    Validate date range for analysis.

    Returns:
        Dict with 'valid' boolean and 'message' string
    """
    if not isinstance(start_date, datetime) or not isinstance(end_date, datetime):
        return {"valid": False, "message": "Dates must be datetime objects"}

    if start_date >= end_date:
        return {"valid": False, "message": "Start date must be before end date"}

    # Check if date range is reasonable (not too far in the past or future)
    now = datetime.now()
    max_past_days = 365 * 10  # 10 years
    max_future_days = 30  # 30 days in future

    days_from_start = (now - start_date).days
    days_to_end = (end_date - now).days

    if days_from_start > max_past_days:
        return {
            "valid": False,
            "message": f"Start date cannot be more than {max_past_days // 365} years in the past",
        }

    if days_to_end > max_future_days:
        return {
            "valid": False,
            "message": f"End date cannot be more than {max_future_days} days in the future",
        }

    # Check minimum range (at least 7 days)
    range_days = (end_date - start_date).days
    if range_days < 7:
        return {"valid": False, "message": "Date range must be at least 7 days"}

    return {"valid": True, "message": "Valid date range"}


def validate_api_key(api_key: str) -> Dict[str, Any]:
    """
    Validate OpenAI API key format.

    Returns:
        Dict with 'valid' boolean and 'message' string
    """
    if not api_key:
        return {"valid": False, "message": "API key cannot be empty"}

    if not isinstance(api_key, str):
        return {"valid": False, "message": "API key must be a string"}

    api_key = api_key.strip()

    if not api_key.startswith("sk-"):
        return {"valid": False, "message": "OpenAI API key must start with 'sk-'"}

    if len(api_key) < 20:
        return {"valid": False, "message": "API key appears too short"}

    # Basic format check (sk- followed by alphanumeric characters)
    import re

    if not re.match(r"^sk-[a-zA-Z0-9]+$", api_key):
        return {"valid": False, "message": "API key contains invalid characters"}

    return {"valid": True, "message": "Valid API key format"}


def validate_dataframe(df: pd.DataFrame, required_columns: List[str]) -> Dict[str, Any]:
    """
    Validate that DataFrame has required columns and data.

    Returns:
        Dict with 'valid' boolean and 'message' string
    """
    if df is None:
        return {"valid": False, "message": "DataFrame cannot be None"}

    if not isinstance(df, pd.DataFrame):
        return {"valid": False, "message": "Input must be a pandas DataFrame"}

    if df.empty:
        return {"valid": False, "message": "DataFrame cannot be empty"}

    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        return {
            "valid": False,
            "message": f"Missing required columns: {', '.join(missing_columns)}",
        }

    # Check for all-null columns
    null_columns = [col for col in required_columns if df[col].isnull().all()]
    if null_columns:
        return {
            "valid": False,
            "message": f"All values are null in columns: {', '.join(null_columns)}",
        }

    return {"valid": True, "message": "Valid DataFrame"}


def validate_ohlcv_data(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Validate OHLCV (Open, High, Low, Close, Volume) data for stock analysis.

    Returns:
        Dict with 'valid' boolean and 'message' string
    """
    required_columns = ["Open", "High", "Low", "Close", "Volume"]

    # First validate basic DataFrame structure
    basic_validation = validate_dataframe(df, required_columns)
    if not basic_validation["valid"]:
        return basic_validation

    # Validate OHLCV data integrity
    try:
        # Check that High >= Low for all rows
        invalid_hl = df[df["High"] < df["Low"]]
        if not invalid_hl.empty:
            return {
                "valid": False,
                "message": f"High price is less than Low price in {len(invalid_hl)} rows",
            }

        # Check that Open and Close are within High-Low range
        invalid_open = df[(df["Open"] > df["High"]) | (df["Open"] < df["Low"])]
        if not invalid_open.empty:
            return {
                "valid": False,
                "message": f"Open price is outside High-Low range in {len(invalid_open)} rows",
            }

        invalid_close = df[(df["Close"] > df["High"]) | (df["Close"] < df["Low"])]
        if not invalid_close.empty:
            return {
                "valid": False,
                "message": f"Close price is outside High-Low range in {len(invalid_close)} rows",
            }

        # Check for negative values
        price_columns = ["Open", "High", "Low", "Close"]
        for col in price_columns:
            if (df[col] <= 0).any():
                return {
                    "valid": False,
                    "message": f"Negative or zero values found in {col} column",
                }

        # Check volume (should be non-negative)
        if (df["Volume"] < 0).any():
            return {"valid": False, "message": "Negative volume values found"}

    except Exception as e:
        return {"valid": False, "message": f"Error validating OHLCV data: {str(e)}"}

    return {"valid": True, "message": "Valid OHLCV data"}


def validate_portfolio_symbols(
    symbols: List[str], available_symbols: List[str], min_symbols: int = 2
) -> Dict[str, Any]:
    """
    Validate portfolio symbol selection.

    Returns:
        Dict with 'valid' boolean and 'message' string
    """
    if not symbols:
        return {"valid": False, "message": "Portfolio must contain at least one symbol"}

    if len(symbols) < min_symbols:
        return {
            "valid": False,
            "message": f"Portfolio must contain at least {min_symbols} symbols",
        }

    # Check for duplicates
    if len(symbols) != len(set(symbols)):
        return {"valid": False, "message": "Portfolio contains duplicate symbols"}

    # Validate each symbol
    invalid_symbols = [s for s in symbols if s not in available_symbols]
    if invalid_symbols:
        return {
            "valid": False,
            "message": f"Invalid symbols: {', '.join(invalid_symbols)}",
        }

    return {"valid": True, "message": "Valid portfolio symbols"}


def validate_numeric_range(
    value: float, min_val: float, max_val: float, field_name: str
) -> Dict[str, Any]:
    """
    Validate that numeric value is within specified range.

    Returns:
        Dict with 'valid' boolean and 'message' string
    """
    try:
        value = float(value)
    except (TypeError, ValueError):
        return {"valid": False, "message": f"{field_name} must be a number"}

    if value < min_val:
        return {"valid": False, "message": f"{field_name} must be at least {min_val}"}

    if value > max_val:
        return {"valid": False, "message": f"{field_name} must be at most {max_val}"}

    return {"valid": True, "message": f"Valid {field_name}"}


def validate_screener_filters(filters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate screener filter parameters.

    Returns:
        Dict with 'valid' boolean and 'message' string
    """
    validation_rules = {
        "market_cap": {"min": 0, "max": 1000000, "unit": "billion VND"},
        "roe": {"min": -100, "max": 200, "unit": "%"},
        "roa": {"min": -100, "max": 100, "unit": "%"},
        "dividend_yield": {"min": 0, "max": 50, "unit": "%"},
        "beta": {"min": 0, "max": 10, "unit": "ratio"},
        "financial_health": {"min": 0, "max": 10, "unit": "score"},
        "stock_rating": {"min": 0, "max": 10, "unit": "score"},
    }

    for filter_name, filter_value in filters.items():
        if filter_name in validation_rules:
            rules = validation_rules[filter_name]

            # Handle range filters (tuple of min, max)
            if isinstance(filter_value, (tuple, list)) and len(filter_value) == 2:
                min_val, max_val = filter_value

                # Validate min value
                min_validation = validate_numeric_range(
                    min_val, rules["min"], rules["max"], f"{filter_name} minimum"
                )
                if not min_validation["valid"]:
                    return min_validation

                # Validate max value
                max_validation = validate_numeric_range(
                    max_val, rules["min"], rules["max"], f"{filter_name} maximum"
                )
                if not max_validation["valid"]:
                    return max_validation

                # Validate range order
                if min_val >= max_val:
                    return {
                        "valid": False,
                        "message": f"{filter_name} minimum must be less than maximum",
                    }

            # Handle single value filters
            elif isinstance(filter_value, (int, float)):
                validation = validate_numeric_range(
                    filter_value, rules["min"], rules["max"], filter_name
                )
                if not validation["valid"]:
                    return validation

    return {"valid": True, "message": "Valid screener filters"}


def validate_file_upload(uploaded_file) -> Dict[str, Any]:
    """
    Validate uploaded file for data analysis.

    Returns:
        Dict with 'valid' boolean and 'message' string
    """
    if uploaded_file is None:
        return {"valid": False, "message": "No file uploaded"}

    # Check file size (max 50MB)
    if hasattr(uploaded_file, "size") and uploaded_file.size > 50 * 1024 * 1024:
        return {"valid": False, "message": "File size cannot exceed 50MB"}

    # Check file type
    allowed_extensions = [".csv", ".xlsx", ".xls"]
    file_extension = None

    if hasattr(uploaded_file, "name"):
        file_extension = "." + uploaded_file.name.split(".")[-1].lower()
        if file_extension not in allowed_extensions:
            return {
                "valid": False,
                "message": f"File type not supported. Allowed types: {', '.join(allowed_extensions)}",
            }

    return {"valid": True, "message": "Valid file upload"}
