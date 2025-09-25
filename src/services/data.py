"""
Data transformation utilities for Finance Bro application.
Extracts reusable data processing logic from pages while preserving functionality.

CRITICAL: All session state variables remain exactly the same.
These utilities work WITH existing data processing patterns.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Tuple


def transpose_financial_dataframe(
    df: pd.DataFrame, name: str, period: str
) -> pd.DataFrame:
    """
    Transpose financial dataframes from long to wide format.
    Extracted from bro.py - EXACT same logic preserved.

    PRESERVES EXISTING FUNCTIONALITY:
    - Exact same transposition logic as bro.py
    - Handles quarterly vs annual data
    - Supports all financial statement types

    Args:
        df: Financial dataframe to transpose
        name: Name of the dataframe (CashFlow, BalanceSheet, IncomeStatement, Ratios)
        period: Period type ('year' or 'quarter')

    Returns:
        Transposed dataframe in wide format
    """
    try:
        if name in ["CashFlow", "BalanceSheet", "IncomeStatement"]:
            if "yearReport" in df.columns:
                df_clean = df.drop("ticker", axis=1, errors="ignore")

                # Handle quarterly vs annual data
                if (
                    "lengthReport" in df.columns
                    and period == "quarter"
                    and df["lengthReport"].isin([1, 2, 3, 4]).any()
                ):
                    # Quarterly data
                    df_clean = df_clean.rename(columns={"lengthReport": "Quarter"})
                    df_clean["period_id"] = (
                        df_clean["yearReport"].astype(str)
                        + "-Q"
                        + df_clean["Quarter"].astype(str)
                    )
                    df_wide = df_clean.set_index("period_id").T
                    df_wide = df_wide.drop(
                        ["yearReport", "Quarter"], axis=0, errors="ignore"
                    )
                else:
                    # Annual data
                    df_wide = df_clean.set_index("yearReport").T
                    df_wide = df_wide.drop(["lengthReport"], axis=0, errors="ignore")

                df_wide = df_wide.reset_index()
                df_wide = df_wide.rename(columns={"index": "Metric"})
                return df_wide

        elif name == "Ratios":
            if hasattr(df, "columns") and len(df.columns) > 0:
                # Check if years are already in columns
                year_cols = [
                    str(col)
                    for col in df.columns
                    if str(col).isdigit() and len(str(col)) == 4
                ]

                if len(year_cols) > 1:
                    # Years already in columns
                    return df
                elif "yearReport" in df.columns:
                    # Standard long format, transpose to wide
                    df_clean = df.drop("ticker", axis=1, errors="ignore")

                    if (
                        "lengthReport" in df.columns
                        and period == "quarter"
                        and df["lengthReport"].isin([1, 2, 3, 4]).any()
                    ):
                        # Quarterly data
                        df_clean = df_clean.rename(columns={"lengthReport": "Quarter"})
                        df_clean["period_id"] = (
                            df_clean["yearReport"].astype(str)
                            + "-Q"
                            + df_clean["Quarter"].astype(str)
                        )
                        df_wide = df_clean.set_index("period_id").T
                        df_wide = df_wide.drop(
                            ["yearReport", "Quarter"], axis=0, errors="ignore"
                        )
                    else:
                        # Annual data
                        df_wide = df_clean.set_index("yearReport").T
                        df_wide = df_wide.drop(
                            ["lengthReport"], axis=0, errors="ignore"
                        )

                    df_wide = df_wide.reset_index()
                    df_wide = df_wide.rename(columns={"index": "Metric"})
                    return df_wide
                else:
                    # Multi-index or other format
                    df_transposed = df.T
                    df_transposed = df_transposed.reset_index()
                    df_transposed = df_transposed.rename(columns={"index": "Metric"})
                    return df_transposed

        # For other dataframes, return as-is
        return df

    except Exception:
        # If transposition fails, return original dataframe
        return df


def prepare_ohlcv_data(data: pd.DataFrame, for_mplfinance: bool = True) -> pd.DataFrame:
    """
    Prepare stock data for charting libraries (especially mplfinance).
    Extracted from Technical_Analysis.py - preserves exact functionality.

    Args:
        data: Raw stock data from vnstock
        for_mplfinance: Whether to format for mplfinance library

    Returns:
        Formatted dataframe ready for charting
    """
    if data is None or data.empty:
        return pd.DataFrame()

    try:
        # Make a copy to avoid modifying original data
        data = data.copy()

        # Set time column as datetime index
        if "time" in data.columns:
            data["time"] = pd.to_datetime(data["time"])
            data = data.set_index("time")

        if for_mplfinance:
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

        return data

    except Exception:
        return pd.DataFrame()


def calculate_stock_returns(
    prices: pd.DataFrame, return_type: str = "simple"
) -> pd.Series:
    """
    Calculate stock returns from price data.
    Used in Stock_Price_Analysis.py and Portfolio_Optimization.py.

    Args:
        prices: DataFrame with price data (must have 'Close' or 'close' column)
        return_type: Type of returns ('simple', 'log', 'percentage')

    Returns:
        Series of calculated returns
    """
    try:
        # Find price column (case-insensitive)
        price_col = None
        for col in prices.columns:
            if col.lower() in ["close", "adj close", "adjusted_close"]:
                price_col = col
                break

        if price_col is None:
            return pd.Series(dtype=float)

        prices_series = prices[price_col]

        if return_type == "simple":
            returns = prices_series.pct_change().dropna()
        elif return_type == "log":
            returns = np.log(prices_series / prices_series.shift(1)).dropna()
        elif return_type == "percentage":
            returns = (prices_series.pct_change() * 100).dropna()
        else:
            returns = prices_series.pct_change().dropna()

        return returns

    except Exception:
        return pd.Series(dtype=float)


def calculate_portfolio_returns(prices_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate portfolio returns from price data.

    Extracted from Portfolio_Optimization.py line 247 - EXACT same logic preserved.
    """
    returns = prices_df.pct_change().dropna()
    return returns


def process_portfolio_price_data(
    all_historical_data: Dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """Process historical data from multiple stocks into combined price dataframe.

    Extracted from Portfolio_Optimization.py lines 185-216 - EXACT same logic preserved.
    """
    combined_prices = pd.DataFrame()

    for symbol, data in all_historical_data.items():
        if not data.empty:
            # Ensure we have a 'time' column
            if "time" not in data.columns:
                if hasattr(data.index, "name") and data.index.name is None:
                    data = data.reset_index()
                data = data.rename(columns={data.columns[0]: "time"})

            # Extract time and close price
            temp_df = data[["time", "close"]].copy()
            temp_df.rename(columns={"close": f"{symbol}_close"}, inplace=True)

            if combined_prices.empty:
                combined_prices = temp_df
            else:
                combined_prices = pd.merge(
                    combined_prices, temp_df, on="time", how="outer"
                )

    if combined_prices.empty:
        return combined_prices

    combined_prices = combined_prices.sort_values("time")
    combined_prices.set_index("time", inplace=True)

    # Extract close prices
    close_price_columns = [col for col in combined_prices.columns if "_close" in col]
    prices_df = combined_prices[close_price_columns]
    prices_df.columns = [col.replace("_close", "") for col in close_price_columns]
    prices_df = prices_df.dropna()

    return prices_df


def prepare_portfolio_symbol_defaults(main_stock_symbol: str) -> List[str]:
    """Prepare default symbols for portfolio selection.

    Extracted from Portfolio_Optimization.py lines 50-54 - EXACT same logic preserved.
    """
    # Set default symbols to include the main symbol from session state
    default_symbols = (
        [main_stock_symbol, "FMC", "DHC"]
        if main_stock_symbol not in ["FMC", "DHC"]
        else [main_stock_symbol, "REE", "VNM"]
    )
    # Remove duplicates and ensure main symbol is first
    default_symbols = list(dict.fromkeys(default_symbols))
    return default_symbols


def create_weights_dataframe(
    weights_dict: Dict[str, float], column_name: str
) -> pd.DataFrame:
    """Convert weights dictionary to DataFrame format for riskfolio-lib.

    Extracted from Portfolio_Optimization.py lines 612, 691 - EXACT same logic preserved.
    """
    return pd.DataFrame.from_dict(weights_dict, orient="index", columns=[column_name])


def format_allocation_dataframe(
    allocation: Dict[str, int], latest_prices_actual: pd.Series, portfolio_value: float
) -> pd.DataFrame:
    """Format allocation data for display.

    Extracted from Portfolio_Optimization.py lines 523-530 - EXACT same logic preserved.
    """
    allocation_df = pd.DataFrame(list(allocation.items()), columns=["Symbol", "Shares"])
    allocation_df["Latest Price (VND)"] = allocation_df["Symbol"].map(
        latest_prices_actual
    )
    allocation_df["Total Value (VND)"] = (
        allocation_df["Shares"] * allocation_df["Latest Price (VND)"]
    )
    allocation_df["Weight %"] = (
        allocation_df["Total Value (VND)"] / portfolio_value * 100
    ).round(2)

    # Format numbers for display
    allocation_df["Latest Price (VND)"] = allocation_df["Latest Price (VND)"].apply(
        lambda x: f"{x:,.0f}"
    )
    allocation_df["Total Value (VND)"] = allocation_df["Total Value (VND)"].apply(
        lambda x: f"{x:,.0f}"
    )

    return allocation_df


def validate_technical_data_sufficiency(data: pd.DataFrame) -> bool:
    """Validate if data is sufficient for technical analysis.

    Extracted from Technical_Analysis.py calculate_indicators function - validation logic preserved.
    """
    if len(data) < 20:
        return False

    # Validate required columns
    required_columns = ["Open", "High", "Low", "Close", "Volume"]
    missing_columns = [col for col in required_columns if col not in data.columns]
    return len(missing_columns) == 0


def prepare_technical_chart_data(data: pd.DataFrame, indicators: dict) -> List:
    """Prepare addplot data for mplfinance technical charts.

    Extracted from Technical_Analysis.py create_technical_chart function - EXACT logic preserved.
    This function prepares the addplot list that mplfinance uses to overlay indicators.
    """
    addplots = []
    panels = 1  # Start with price panel
    skipped_indicators = []

    # Bollinger Bands - Safe validation
    if "bbands" in indicators and indicators["bbands"] is not None:
        bb = indicators["bbands"]
        required_cols = ["BBU_20_2.0", "BBM_20_2.0", "BBL_20_2.0"]
        if all(col in bb.columns for col in required_cols):
            try:
                import mplfinance as mpf

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

    return addplots, panels, skipped_indicators


def clean_and_validate_ohlcv_data(data: pd.DataFrame) -> pd.DataFrame:
    """Clean and validate OHLCV data for technical analysis.

    Enhanced validation for technical indicator calculations.
    """
    if data.empty:
        return data

    # Ensure High >= Low for all rows
    if "High" in data.columns and "Low" in data.columns:
        valid_high_low = data["High"] >= data["Low"]
        if not valid_high_low.all():
            data = data[valid_high_low].copy()

    # Ensure all price values are positive
    price_cols = ["Open", "High", "Low", "Close"]
    for col in price_cols:
        if col in data.columns:
            data = data[data[col] > 0].copy()

    # Remove any remaining NaN values
    data = data.dropna()

    return data


def create_performance_summary_dataframe(performance_data: List[Dict]) -> pd.DataFrame:
    """Create performance summary DataFrame from portfolio performance data.

    Used across Portfolio_Optimization.py for performance comparisons.
    """
    performance_df = pd.DataFrame(performance_data)

    # Format numeric columns to 4 decimal places
    numeric_cols = ["Expected Return", "Volatility", "Sharpe Ratio"]
    for col in numeric_cols:
        if col in performance_df.columns:
            performance_df[col] = performance_df[col].apply(
                lambda x: f"{float(x):.4f}" if isinstance(x, (int, float)) else x
            )

    return performance_df


def prepare_portfolio_data(
    stock_data_dict: Dict[str, pd.DataFrame],
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Prepare portfolio data for optimization.
    Extracted from Portfolio_Optimization.py logic.

    Args:
        stock_data_dict: Dictionary mapping symbols to their price DataFrames

    Returns:
        Tuple of (price_data, returns_data) DataFrames
    """
    try:
        all_prices = {}

        for symbol, data in stock_data_dict.items():
            if data is not None and not data.empty:
                # Get close price column
                price_col = None
                for col in data.columns:
                    if col.lower() in ["close", "adj close", "adjusted_close"]:
                        price_col = col
                        break

                if price_col is not None:
                    all_prices[symbol] = data[price_col]

        if not all_prices:
            return pd.DataFrame(), pd.DataFrame()

        # Combine into single DataFrame
        price_data = pd.DataFrame(all_prices)

        # Calculate returns
        returns_data = price_data.pct_change().dropna()

        return price_data, returns_data

    except Exception:
        return pd.DataFrame(), pd.DataFrame()


def clean_financial_data(
    df: pd.DataFrame, remove_null_rows: bool = True
) -> pd.DataFrame:
    """
    Clean financial data for analysis.
    Handles common data quality issues.

    Args:
        df: Financial dataframe to clean
        remove_null_rows: Whether to remove rows with all null values

    Returns:
        Cleaned dataframe
    """
    if df is None or df.empty:
        return df

    try:
        df_clean = df.copy()

        # Remove rows where all values (except index/identifier columns) are null
        if remove_null_rows:
            # Identify likely identifier columns
            id_columns = []
            for col in df_clean.columns:
                if col.lower() in [
                    "ticker",
                    "symbol",
                    "metric",
                    "index",
                    "yearreport",
                    "lengthreport",
                ]:
                    id_columns.append(col)

            # Get numeric columns
            numeric_columns = [col for col in df_clean.columns if col not in id_columns]

            if numeric_columns:
                # Remove rows where all numeric columns are null
                df_clean = df_clean.dropna(subset=numeric_columns, how="all")

        # Convert numeric columns to appropriate types
        for col in df_clean.columns:
            if col not in ["ticker", "symbol", "metric"]:  # Skip text columns
                df_clean[col] = pd.to_numeric(df_clean[col], errors="ignore")

        return df_clean

    except Exception:
        return df


def format_financial_metrics(value: Any, metric_type: str = "default") -> str:
    """
    Format financial metrics for display.

    Args:
        value: Value to format
        metric_type: Type of metric ('currency', 'percentage', 'ratio', 'default')

    Returns:
        Formatted string
    """
    if pd.isna(value) or value is None:
        return "N/A"

    try:
        numeric_value = float(value)

        if metric_type == "currency":
            if abs(numeric_value) >= 1e12:
                return f"{numeric_value / 1e12:.2f}T VND"
            elif abs(numeric_value) >= 1e9:
                return f"{numeric_value / 1e9:.2f}B VND"
            elif abs(numeric_value) >= 1e6:
                return f"{numeric_value / 1e6:.2f}M VND"
            else:
                return f"{numeric_value:,.0f} VND"

        elif metric_type == "percentage":
            return f"{numeric_value:.2f}%"

        elif metric_type == "ratio":
            return f"{numeric_value:.2f}"

        else:  # default
            if abs(numeric_value) >= 1e9:
                return f"{numeric_value / 1e9:.2f}B"
            elif abs(numeric_value) >= 1e6:
                return f"{numeric_value / 1e6:.2f}M"
            elif abs(numeric_value) >= 1e3:
                return f"{numeric_value / 1e3:.2f}K"
            else:
                return f"{numeric_value:.2f}"

    except (ValueError, TypeError):
        return str(value)


def validate_financial_dataframe(
    df: pd.DataFrame, required_columns: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Validate financial dataframe structure and content.

    Args:
        df: Dataframe to validate
        required_columns: List of required column names

    Returns:
        Dict with validation results
    """
    if df is None:
        return {"valid": False, "message": "DataFrame is None"}

    if df.empty:
        return {"valid": False, "message": "DataFrame is empty"}

    if required_columns:
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return {
                "valid": False,
                "message": f"Missing columns: {', '.join(missing_columns)}",
            }

    # Check for all-null columns
    null_columns = [col for col in df.columns if df[col].isnull().all()]
    if null_columns:
        return {
            "valid": False,
            "message": f"All-null columns: {', '.join(null_columns)}",
        }

    return {"valid": True, "message": "Valid financial dataframe"}


def merge_financial_dataframes(
    dataframes: Dict[str, pd.DataFrame], on_column: str = "yearReport"
) -> pd.DataFrame:
    """
    Merge multiple financial dataframes on a common column.

    Args:
        dataframes: Dictionary of dataframes to merge
        on_column: Column to merge on

    Returns:
        Merged dataframe
    """
    if not dataframes:
        return pd.DataFrame()

    try:
        # Start with first valid dataframe
        merged_df = None

        for name, df in dataframes.items():
            if df is not None and not df.empty and on_column in df.columns:
                if merged_df is None:
                    merged_df = df.copy()
                    merged_df.columns = [
                        f"{name}_{col}" if col != on_column else col
                        for col in merged_df.columns
                    ]
                else:
                    df_renamed = df.copy()
                    df_renamed.columns = [
                        f"{name}_{col}" if col != on_column else col
                        for col in df_renamed.columns
                    ]
                    merged_df = merged_df.merge(df_renamed, on=on_column, how="outer")

        return merged_df if merged_df is not None else pd.DataFrame()

    except Exception:
        return pd.DataFrame()


def calculate_financial_ratios(
    income_statement: pd.DataFrame, balance_sheet: pd.DataFrame
) -> pd.DataFrame:
    """
    Calculate additional financial ratios from financial statements.

    Args:
        income_statement: Income statement dataframe
        balance_sheet: Balance sheet dataframe

    Returns:
        Dataframe with calculated ratios
    """
    # This is a placeholder for custom ratio calculations
    # Can be extended based on specific requirements
    ratios = pd.DataFrame()

    try:
        # Basic ratio calculations can be added here
        # For example: ROA, ROE, Debt-to-Equity, etc.
        pass
    except Exception:
        pass

    return ratios


def aggregate_portfolio_metrics(returns_data: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate aggregate portfolio metrics.

    Args:
        returns_data: Portfolio returns dataframe

    Returns:
        Dict with portfolio metrics
    """
    if returns_data is None or returns_data.empty:
        return {}

    try:
        metrics = {}

        # Calculate basic portfolio metrics
        metrics["total_return"] = (returns_data.mean() * 252).mean()  # Annualized
        metrics["volatility"] = (returns_data.std() * np.sqrt(252)).mean()  # Annualized
        metrics["sharpe_ratio"] = (
            metrics["total_return"] / metrics["volatility"]
            if metrics["volatility"] > 0
            else 0
        )

        # Correlation matrix
        correlation_matrix = returns_data.corr()
        metrics["avg_correlation"] = correlation_matrix.mean().mean()

        return metrics

    except Exception:
        return {}


def format_financial_display(
    value: float, display_unit: str = "billions", decimal_places: int = 0
) -> str:
    """
    Format financial values for display with proper scaling and comma separators.

    Used for metrics display in financial analysis pages to provide consistent
    formatting across the application.

    Args:
        value: The numeric value to format
        display_unit: The target unit ('billions', 'millions', 'original')
        decimal_places: Number of decimal places to show

    Returns:
        Formatted string with unit suffix and comma separators

    Examples:
        format_financial_display(1500000000, 'billions', 0) -> '2B VND'
        format_financial_display(1500000000, 'millions', 1) -> '1,500.0M VND'
    """
    if pd.isna(value) or value is None:
        return "N/A"

    try:
        numeric_value = float(value)

        if display_unit == "billions":
            converted_value = numeric_value / 1_000_000_000
            format_str = f"{{:,.{decimal_places}f}}B VND"
            return format_str.format(converted_value)
        elif display_unit == "millions":
            converted_value = numeric_value / 1_000_000
            format_str = f"{{:,.{decimal_places}f}}M VND"
            return format_str.format(converted_value)
        else:  # original
            format_str = f"{{:,.{decimal_places}f}} VND"
            return format_str.format(numeric_value)

    except (ValueError, TypeError):
        return "N/A"


def convert_dataframe_for_display(
    df: pd.DataFrame,
    columns_to_format: List[str],
    display_unit: str = "original",
    decimal_places: int = 1,
) -> pd.DataFrame:
    """
    Convert dataframe columns to formatted strings for display while preserving original data.

    Creates a display copy with comma-formatted strings for table presentation
    without modifying the original data structure.

    Args:
        df: Original dataframe to format
        columns_to_format: List of column names to apply formatting to
        display_unit: Target unit for display ('billions', 'millions', 'original')
        decimal_places: Number of decimal places for display

    Returns:
        Copy of dataframe with specified columns formatted as strings

    Examples:
        # Format capital employed columns for display
        display_df = convert_dataframe_for_display(
            capital_employed_df,
            ['Long-term borrowings (Bn. VND)', 'Capital Employed (Bn. VND)'],
            display_unit='original',
            decimal_places=1
        )
    """
    if df is None or df.empty:
        return df

    try:
        # Create display copy
        display_df = df.copy()

        for column in columns_to_format:
            if column in display_df.columns:
                # Apply formatting function to each value in the column
                def format_value(x):
                    try:
                        if pd.isna(x) or x is None:
                            return "N/A"
                        # Handle string values that might not be convertible to float
                        if isinstance(x, str) and x in ["N/A", "n/a", "NA", ""]:
                            return "N/A"

                        numeric_value = float(x)

                        if display_unit == "billions":
                            return (
                                f"{numeric_value / 1_000_000_000:,.{decimal_places}f}"
                            )
                        elif display_unit == "millions":
                            return f"{numeric_value / 1_000_000:,.{decimal_places}f}"
                        else:  # original
                            return f"{numeric_value:,.{decimal_places}f}"
                    except (ValueError, TypeError):
                        return "N/A"

                display_df[column] = display_df[column].apply(format_value)

        return display_df

    except Exception:
        # Return original dataframe if formatting fails
        return df
