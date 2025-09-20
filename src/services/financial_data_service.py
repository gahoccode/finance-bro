"""
Financial Data Service Module

Centralized financial data loading for all pages, extracted from bro.py.
Provides cached, validated financial statement data for valuation and analysis.
"""

import streamlit as st
import pandas as pd
from vnstock import Vnstock, Listing
from vnstock.core.utils.transform import flatten_hierarchical_index
import warnings

warnings.filterwarnings("ignore")


@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_comprehensive_financial_data(symbol, period="year", source="VCI", company_source="TCBS"):
    """
    Load comprehensive financial data for a stock symbol.
    
    Extracted from bro.py lines 309-344 with enhanced error handling and validation.
    
    Args:
        symbol (str): Stock symbol (e.g., 'VIC', 'VNM')
        period (str): 'year' or 'quarter'
        source (str): Data source for financial statements ('VCI' or 'TCBS')
        company_source (str): Data source for company info ('TCBS' or 'VCI')
    
    Returns:
        dict: Contains both AI-optimized and display dataframes
            - 'dataframes': AI-optimized with Quarter columns
            - 'display_dataframes': Original format with lengthReport
            - 'metadata': Loading metadata and validation info
    """
    try:
        # Initialize Vnstock
        stock = Vnstock().stock(symbol=symbol, source=source)
        company = Vnstock().stock(symbol=symbol, source=company_source).company

        # Load financial data
        cash_flow = stock.finance.cash_flow(period=period)
        balance_sheet = stock.finance.balance_sheet(period=period, lang="en", dropna=True)
        income_statement = stock.finance.income_statement(period=period, lang="en", dropna=True)

        # Load and process Ratio data (multi-index columns)
        ratio_raw = stock.finance.ratio(period=period, lang="en", dropna=True)

        # Use vnstock's built-in flatten_hierarchical_index function
        ratios = flatten_hierarchical_index(
            ratio_raw, separator="_", handle_duplicates=True, drop_levels=0
        )

        # Load dividend schedule
        try:
            dividend_schedule = company.dividends()
        except Exception:
            dividend_schedule = pd.DataFrame()

        # Store original dataframes for display (keep original column names)
        display_dataframes = {
            "CashFlow": cash_flow,
            "BalanceSheet": balance_sheet,
            "IncomeStatement": income_statement,
            "Ratios": ratios,
            "Dividends": dividend_schedule,
        }

        # Create copies with renamed columns for PandasAI (better query compatibility)
        cash_flow_ai = cash_flow.copy()
        balance_sheet_ai = balance_sheet.copy()
        income_statement_ai = income_statement.copy()
        ratios_ai = ratios.copy()

        # Sort all financial statements by yearReport in ascending order for proper temporal alignment
        if not cash_flow_ai.empty and "yearReport" in cash_flow_ai.columns:
            cash_flow_ai = cash_flow_ai.sort_values("yearReport", ascending=True)
        if not balance_sheet_ai.empty and "yearReport" in balance_sheet_ai.columns:
            balance_sheet_ai = balance_sheet_ai.sort_values("yearReport", ascending=True)
        if not income_statement_ai.empty and "yearReport" in income_statement_ai.columns:
            income_statement_ai = income_statement_ai.sort_values("yearReport", ascending=True)
        if not ratios_ai.empty and "yearReport" in ratios_ai.columns:
            ratios_ai = ratios_ai.sort_values("yearReport", ascending=True)

        # Rename columns for quarterly data to improve AI query compatibility
        if period == "quarter":
            for df in [cash_flow_ai, balance_sheet_ai, income_statement_ai, ratios_ai]:
                if (
                    "lengthReport" in df.columns
                    and df["lengthReport"].isin([1, 2, 3, 4]).any()
                ):
                    df.rename(columns={"lengthReport": "Quarter"}, inplace=True)

        # Store AI-optimized dataframes for PandasAI
        ai_dataframes = {
            "CashFlow": cash_flow_ai,
            "BalanceSheet": balance_sheet_ai,
            "IncomeStatement": income_statement_ai,
            "Ratios": ratios_ai,
            "Dividends": dividend_schedule,
        }

        # Validation metadata
        metadata = {
            "symbol": symbol,
            "period": period,
            "source": source,
            "company_source": company_source,
            "loaded_at": pd.Timestamp.now(),
            "data_validation": {
                "cash_flow_rows": len(cash_flow),
                "balance_sheet_rows": len(balance_sheet),
                "income_statement_rows": len(income_statement),
                "ratios_rows": len(ratios),
                "dividends_rows": len(dividend_schedule),
                "has_quarterly_data": period == "quarter" and any(
                    df.get("lengthReport", pd.Series()).isin([1, 2, 3, 4]).any()
                    for df in [cash_flow, balance_sheet, income_statement, ratios]
                    if "lengthReport" in df.columns
                ),
            }
        }

        return {
            "dataframes": ai_dataframes,
            "display_dataframes": display_dataframes,
            "metadata": metadata,
        }

    except Exception as e:
        st.error(f"❌ Error loading financial data for {symbol}: {str(e)}")
        return {
            "dataframes": {},
            "display_dataframes": {},
            "metadata": {"error": str(e), "symbol": symbol},
        }


@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_valuation_essentials(symbol, start_date=None, end_date=None):
    """
    Load essential data required for valuation analysis.
    
    Combines financial statements with stock price data for comprehensive valuation.
    Optimized for fast loading of core valuation requirements.
    
    Args:
        symbol (str): Stock symbol
        start_date (datetime, optional): Start date for price data
        end_date (datetime, optional): End date for price data
    
    Returns:
        dict: Essential valuation data
            - 'financial_data': Comprehensive financial statements
            - 'price_data': Stock price data if dates provided
            - 'market_data': Market capitalization and shares outstanding
    """
    from .vnstock_api import fetch_stock_price_data

    # Default date range if not provided
    if start_date is None:
        start_date = pd.to_datetime("2024-01-01")
    if end_date is None:
        end_date = pd.to_datetime("today") - pd.Timedelta(days=1)

    # Load financial data
    financial_data = load_comprehensive_financial_data(symbol)

    result = {
        "financial_data": financial_data,
        "symbol": symbol,
        "loaded_at": pd.Timestamp.now(),
    }

    # Load price data if date range provided
    try:
        price_data = fetch_stock_price_data(symbol, start_date, end_date)
        result["price_data"] = price_data

        # Calculate returns if price data available
        if not price_data.empty and "close" in price_data.columns:
            clean_prices = price_data["close"].dropna()
            clean_prices = clean_prices[clean_prices > 0]
            if len(clean_prices) > 1:
                returns = clean_prices.pct_change().dropna()
                result["returns"] = returns

    except Exception as e:
        st.warning(f"⚠️ Could not load price data: {str(e)}")
        result["price_data"] = pd.DataFrame()

    return result


@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_stock_symbols_with_names():
    """
    Load stock symbols with company names for selection UI.
    
    Extracted from bro.py lines 191-213 with enhanced caching.
    
    Returns:
        dict: Contains symbols list and full DataFrame
    """
    try:
        symbols_df = Listing().all_symbols()
        symbols_list = sorted(symbols_df["symbol"].tolist())

        return {
            "symbols_list": symbols_list,
            "symbols_df": symbols_df,
            "loaded_at": pd.Timestamp.now(),
        }
    except Exception as e:
        st.warning(f"Could not load stock symbols from vnstock: {str(e)}")
        # Fallback symbols
        fallback_symbols = ["REE", "VIC", "VNM", "VCB", "BID", "HPG", "FPT", "FMC", "DHC"]
        return {
            "symbols_list": fallback_symbols,
            "symbols_df": None,
            "loaded_at": pd.Timestamp.now(),
            "error": str(e),
        }


def get_company_name_from_symbol(symbol, symbols_df=None):
    """
    Get company full name from stock symbol.
    
    Args:
        symbol (str): Stock symbol
        symbols_df (DataFrame, optional): Pre-loaded symbols DataFrame
    
    Returns:
        str: Company name or symbol if not found
    """
    if symbols_df is None:
        symbol_data = get_stock_symbols_with_names()
        symbols_df = symbol_data.get("symbols_df")

    if symbols_df is not None:
        try:
            matching_company = symbols_df[symbols_df["symbol"] == symbol]
            if not matching_company.empty and "organ_name" in symbols_df.columns:
                return matching_company["organ_name"].iloc[0]
        except Exception:
            pass

    return symbol


def validate_financial_data(dataframes):
    """
    Validate that financial data is complete for analysis.
    
    Args:
        dataframes (dict): Financial data dictionary
    
    Returns:
        dict: Validation results
    """
    validation = {
        "is_valid": True,
        "warnings": [],
        "errors": [],
        "data_summary": {},
    }

    required_statements = ["BalanceSheet", "IncomeStatement", "CashFlow", "Ratios"]

    for statement in required_statements:
        df = dataframes.get(statement, pd.DataFrame())
        if df.empty:
            validation["errors"].append(f"Missing {statement} data")
            validation["is_valid"] = False
        else:
            validation["data_summary"][statement] = {
                "rows": len(df),
                "columns": len(df.columns),
                "years_available": list(df.get("yearReport", []).unique()) if "yearReport" in df.columns else [],
            }

    return validation
