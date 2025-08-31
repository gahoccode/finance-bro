import pandas as pd
import numpy as np
import streamlit as st


def create_dupont_analysis(IncomeStatement, BalanceSheet, CashFlow):
    """
    Create a 3-factor DuPont analysis based on the three financial statements.

    DuPont Analysis: ROE = Net Profit Margin × Asset Turnover × Financial Leverage

    Where:
    - Net Profit Margin = Net Income / Revenue
    - Asset Turnover = Revenue / Average Total Assets
    - Financial Leverage = Average Total Assets / Average Shareholders' Equity

    Returns:
    --------
    pandas DataFrame
        DataFrame with DuPont analysis results
    """
    try:
        # Step 1: Combine necessary data from all three statements
        # Start with Income Statement data for revenue and net income
        income_data = IncomeStatement[
            ["ticker", "yearReport", "Revenue (Bn. VND)", "Net Profit For the Year"]
        ].copy()

        # Rename for clarity
        income_data = income_data.rename(
            columns={"Net Profit For the Year": "Net Income (Bn. VND)"}
        )

        # Step 2: Add Balance Sheet data for assets and equity
        balance_data = BalanceSheet[
            ["ticker", "yearReport", "TOTAL ASSETS (Bn. VND)", "OWNER'S EQUITY(Bn.VND)"]
        ].copy()

        # Merge the dataframes
        dupont_df = pd.merge(
            income_data, balance_data, on=["ticker", "yearReport"], how="inner"
        )

        # Step 3: Sort by ticker and year for calculations
        dupont_df = dupont_df.sort_values(["ticker", "yearReport"])

        # Calculate average total assets and equity (current + previous year) / 2
        dupont_df["Prev_Assets"] = dupont_df.groupby("ticker")[
            "TOTAL ASSETS (Bn. VND)"
        ].shift(1)
        dupont_df["Prev_Equity"] = dupont_df.groupby("ticker")[
            "OWNER'S EQUITY(Bn.VND)"
        ].shift(1)

        # Calculate averages
        dupont_df["Average Total Assets (Bn. VND)"] = (
            dupont_df["TOTAL ASSETS (Bn. VND)"] + dupont_df["Prev_Assets"]
        ) / 2
        dupont_df["Average Equity (Bn. VND)"] = (
            dupont_df["OWNER'S EQUITY(Bn.VND)"] + dupont_df["Prev_Equity"]
        ) / 2

        # For the first year of each ticker, use current year values
        dupont_df["Average Total Assets (Bn. VND)"] = dupont_df[
            "Average Total Assets (Bn. VND)"
        ].fillna(dupont_df["TOTAL ASSETS (Bn. VND)"])
        dupont_df["Average Equity (Bn. VND)"] = dupont_df[
            "Average Equity (Bn. VND)"
        ].fillna(dupont_df["OWNER'S EQUITY(Bn.VND)"])

        # Step 4: Calculate the 3 DuPont components
        # Net Profit Margin = Net Income / Revenue
        dupont_df["Net Profit Margin"] = (
            dupont_df["Net Income (Bn. VND)"] / dupont_df["Revenue (Bn. VND)"]
        )

        # Asset Turnover = Revenue / Average Total Assets
        dupont_df["Asset Turnover"] = (
            dupont_df["Revenue (Bn. VND)"] / dupont_df["Average Total Assets (Bn. VND)"]
        )

        # Financial Leverage = Average Total Assets / Average Equity
        dupont_df["Financial Leverage"] = (
            dupont_df["Average Total Assets (Bn. VND)"]
            / dupont_df["Average Equity (Bn. VND)"]
        )

        # Step 5: Calculate ROE using DuPont formula
        dupont_df["ROE (DuPont)"] = (
            dupont_df["Net Profit Margin"]
            * dupont_df["Asset Turnover"]
            * dupont_df["Financial Leverage"]
        )

        # Step 6: Calculate ROE directly for validation
        dupont_df["ROE (Direct)"] = (
            dupont_df["Net Income (Bn. VND)"] / dupont_df["Average Equity (Bn. VND)"]
        )

        # Step 7: Clean up and select relevant columns
        dupont_analysis = dupont_df[
            [
                "ticker",
                "yearReport",
                "Net Income (Bn. VND)",
                "Revenue (Bn. VND)",
                "Average Total Assets (Bn. VND)",
                "Average Equity (Bn. VND)",
                "Net Profit Margin",
                "Asset Turnover",
                "Financial Leverage",
                "ROE (DuPont)",
                "ROE (Direct)",
            ]
        ]

        # Convert ratios to percentages for better readability
        dupont_analysis["Net Profit Margin"] = (
            dupont_analysis["Net Profit Margin"] * 100
        )
        dupont_analysis["ROE (DuPont)"] = dupont_analysis["ROE (DuPont)"] * 100
        dupont_analysis["ROE (Direct)"] = dupont_analysis["ROE (Direct)"] * 100

        # Round values for better display
        dupont_analysis = dupont_analysis.round(
            {
                "Net Profit Margin": 2,
                "Asset Turnover": 2,
                "Financial Leverage": 2,
                "ROE (DuPont)": 2,
                "ROE (Direct)": 2,
            }
        )

        return dupont_analysis

    except Exception as e:
        st.error(f"Error in DuPont analysis calculation: {str(e)}")
        return None


def calculate_capital_employed(BalanceSheet):
    """
    Calculate Capital Employed from Balance Sheet data.

    Capital Employed = Long-term borrowings + Short-term borrowings + Owner's equity

    Parameters:
    -----------
    BalanceSheet : pandas.DataFrame
        Balance sheet data with Vietnamese column names

    Returns:
    --------
    pandas.DataFrame
        DataFrame with capital employed breakdown and totals
    """
    balance_sheet_copy = BalanceSheet.copy()

    # 1️⃣ normalise header text (strip & replace Unicode dashes with ASCII "-")
    balance_sheet_copy.columns = balance_sheet_copy.columns.str.strip().str.replace(
        r"[\u2010-\u2015]", "-", regex=True
    )

    # 2️⃣ be sure the three columns exist and have no NaN
    for col in [
        "Long-term borrowings (Bn. VND)",
        "Short-term borrowings (Bn. VND)",
        "OWNER'S EQUITY(Bn.VND)",
    ]:
        if col not in balance_sheet_copy.columns:
            st.warning(f"Column '{col}' not found in balance sheet data")
            balance_sheet_copy[col] = 0
        else:
            balance_sheet_copy[col] = balance_sheet_copy[col].fillna(0)

    # 3️⃣ compute Capital Employed
    balance_sheet_copy["Capital Employed (Bn. VND)"] = (
        balance_sheet_copy["Long-term borrowings (Bn. VND)"]
        + balance_sheet_copy["Short-term borrowings (Bn. VND)"]
        + balance_sheet_copy["OWNER'S EQUITY(Bn.VND)"]
    )

    return balance_sheet_copy[
        [
            "ticker",
            "yearReport",
            "Long-term borrowings (Bn. VND)",
            "Short-term borrowings (Bn. VND)",
            "OWNER'S EQUITY(Bn.VND)",
            "Capital Employed (Bn. VND)",
        ]
    ]


def calculate_degree_of_financial_leverage(IncomeStatement):
    """
    Calculate Degree of Financial Leverage using percentage changes in Net Income and EBIT.

    DFL = % Change in Net Income / % Change in EBIT

    Parameters:
    -----------
    IncomeStatement : pandas DataFrame
        Income Statement data with columns including 'Operating Profit/Loss' and 'Attribute to parent company (Bn. VND)'

    Returns:
    --------
    pandas DataFrame
        DataFrame with DFL calculations
    """
    # Create a copy to avoid modifying the original dataframe
    financial_leverage_data = IncomeStatement.copy()

    # Rename for clarity
    financial_leverage_data = financial_leverage_data.rename(
        columns={
            "Operating Profit/Loss": "EBIT (Bn. VND)",
            "Net Profit For the Year": "Net Income (Bn. VND)",
        }
    )

    # Sort by ticker and year
    financial_leverage_data = financial_leverage_data.sort_values(
        ["ticker", "yearReport"]
    )

    # Calculate year-over-year percentage changes for each ticker
    financial_leverage_data["EBIT % Change"] = (
        financial_leverage_data.groupby("ticker")["EBIT (Bn. VND)"].pct_change() * 100
    )
    financial_leverage_data["Net Income % Change"] = (
        financial_leverage_data.groupby("ticker")["Net Income (Bn. VND)"].pct_change()
        * 100
    )

    # Calculate DFL
    financial_leverage_data["DFL"] = (
        financial_leverage_data["Net Income % Change"]
        / financial_leverage_data["EBIT % Change"]
    )

    # Handle infinite or NaN values (when EBIT % Change is near zero)
    financial_leverage_data["DFL"] = financial_leverage_data["DFL"].replace(
        [np.inf, -np.inf], np.nan
    )

    # Select relevant columns
    dfl_results = financial_leverage_data[
        [
            "ticker",
            "yearReport",
            "EBIT (Bn. VND)",
            "Net Income (Bn. VND)",
            "EBIT % Change",
            "Net Income % Change",
            "DFL",
        ]
    ]

    return dfl_results


@st.cache_data
def calculate_effective_tax_rate(income_statement, cash_flow):
    """
    Calculate the effective tax rate using Income Statement and Cash Flow data.

    Effective Tax Rate = Tax Expense / Profit Before Tax

    Parameters:
    -----------
    income_statement : pandas DataFrame
        Income Statement data with columns: ticker, yearReport, etc.
    cash_flow : pandas DataFrame
        Cash Flow Statement data with columns: ticker, yearReport, 'Net Profit/Loss before tax', 'Business Income Tax paid'

    Returns:
    --------
    pandas DataFrame
        DataFrame with effective tax rate calculations
    """
    # Handle empty dataframes
    if income_statement.empty or cash_flow.empty:
        return pd.DataFrame(columns=[
            "ticker", "yearReport", "Profit Before Tax (Bn. VND)", 
            "Tax Paid (Bn. VND)", "Effective Tax Rate"
        ])
    
    # Check for required columns
    required_income_cols = ["ticker", "yearReport", "Profit before tax"]
    required_cash_cols = ["ticker", "yearReport", "Business Income Tax paid", "Net Profit/Loss before tax"]
    
    if not all(col in income_statement.columns for col in required_income_cols):
        return pd.DataFrame(columns=[
            "ticker", "yearReport", "Profit Before Tax (Bn. VND)", 
            "Tax Paid (Bn. VND)", "Effective Tax Rate"
        ])
        
    if not all(col in cash_flow.columns for col in required_cash_cols):
        return pd.DataFrame(columns=[
            "ticker", "yearReport", "Profit Before Tax (Bn. VND)", 
            "Tax Paid (Bn. VND)", "Effective Tax Rate"
        ])

    # Merge the necessary data from both financial statements
    tax_data_df = pd.merge(
        income_statement[["ticker", "yearReport", "Profit before tax"]],
        cash_flow[
            [
                "ticker",
                "yearReport",
                "Business Income Tax paid",
                "Net Profit/Loss before tax",
            ]
        ],
        on=["ticker", "yearReport"],
        how="inner",
    )

    # Use Profit before tax from Income Statement if available, otherwise use from Cash Flow
    tax_data_df["Profit Before Tax (Bn. VND)"] = tax_data_df[
        "Profit before tax"
    ].fillna(tax_data_df["Net Profit/Loss before tax"])

    # Calculate effective tax rate with absolute value of tax paid (since it appears as negative in cash flow)
    tax_data_df["Tax Paid (Bn. VND)"] = tax_data_df["Business Income Tax paid"].abs()

    # Calculate effective tax rate
    tax_data_df["Effective Tax Rate"] = (
        tax_data_df["Tax Paid (Bn. VND)"] / tax_data_df["Profit Before Tax (Bn. VND)"]
    )

    # Handle edge cases (negative profits, zero profits, etc.)
    tax_data_df["Effective Tax Rate"] = tax_data_df["Effective Tax Rate"].clip(
        0, 1
    )  # Cap between 0 and 1

    # Select relevant columns
    tax_data_df = tax_data_df[
        [
            "ticker",
            "yearReport",
            "Profit Before Tax (Bn. VND)",
            "Tax Paid (Bn. VND)",
            "Effective Tax Rate",
        ]
    ]

    return tax_data_df
