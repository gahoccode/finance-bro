import pandas as pd
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
        # Step 1: Identify correct column names for Vietnamese financial data
        # Common variations in Vietnamese financial statements
        revenue_cols = [
            "Revenue (Bn. VND)",
            "Net sales (Bn. VND)",
            "Revenue",
            "Net sales",
        ]
        net_income_cols = [
            "Attribute to parent company (Bn. VND)",
            "Net Income (Bn. VND)",
            "Net profit (Bn. VND)",
            "Profit after tax (Bn. VND)",
        ]
        assets_cols = [
            "TOTAL ASSETS (Bn. VND)",
            "Total assets (Bn. VND)",
            "TOTAL ASSETS",
            "Total assets",
        ]
        equity_cols = [
            "OWNER'S EQUITY(Bn.VND)",
            "Owner's equity (Bn. VND)",
            "OWNER'S EQUITY",
            "Owner's equity",
            "Shareholders' equity (Bn. VND)",
        ]

        # Find matching columns
        revenue_col = None
        for col in revenue_cols:
            if col in IncomeStatement.columns:
                revenue_col = col
                break

        net_income_col = None
        for col in net_income_cols:
            if col in IncomeStatement.columns:
                net_income_col = col
                break

        assets_col = None
        for col in assets_cols:
            if col in BalanceSheet.columns:
                assets_col = col
                break

        equity_col = None
        for col in equity_cols:
            if col in BalanceSheet.columns:
                equity_col = col
                break

        # Validate required columns exist
        if not all([revenue_col, net_income_col, assets_col, equity_col]):
            missing_cols = []
            if not revenue_col:
                missing_cols.append("Revenue")
            if not net_income_col:
                missing_cols.append("Net Income")
            if not assets_col:
                missing_cols.append("Total Assets")
            if not equity_col:
                missing_cols.append("Owner's Equity")

            raise ValueError(f"Missing required columns: {', '.join(missing_cols)}")

        # Step 2: Combine necessary data from financial statements
        income_data = IncomeStatement[
            ["ticker", "yearReport", revenue_col, net_income_col]
        ].copy()
        income_data = income_data.rename(
            columns={
                revenue_col: "Revenue (Bn. VND)",
                net_income_col: "Net Income (Bn. VND)",
            }
        )

        # Add Balance Sheet data for assets and equity
        balance_data = BalanceSheet[
            ["ticker", "yearReport", assets_col, equity_col]
        ].copy()
        balance_data = balance_data.rename(
            columns={
                assets_col: "TOTAL ASSETS (Bn. VND)",
                equity_col: "OWNER'S EQUITY(Bn.VND)",
            }
        )

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
    try:
        balance_sheet_copy = BalanceSheet.copy()

        # Step 1: Normalize header text (strip & replace Unicode dashes with ASCII "-")
        balance_sheet_copy.columns = balance_sheet_copy.columns.str.strip().str.replace(
            r"[\u2010-\u2015]", "-", regex=True
        )

        # Step 2: Define column variations for Vietnamese financial data
        long_term_cols = [
            "Long-term borrowings (Bn. VND)",
            "Long-term debt (Bn. VND)",
            "Long term borrowings (Bn. VND)",
        ]
        short_term_cols = [
            "Short-term borrowings (Bn. VND)",
            "Short-term debt (Bn. VND)",
            "Short term borrowings (Bn. VND)",
        ]
        equity_cols = [
            "OWNER'S EQUITY(Bn.VND)",
            "Owner's equity (Bn. VND)",
            "OWNER'S EQUITY",
            "Owner's equity",
            "Shareholders' equity (Bn. VND)",
        ]

        # Find matching columns
        long_term_col = None
        for col in long_term_cols:
            if col in balance_sheet_copy.columns:
                long_term_col = col
                break

        short_term_col = None
        for col in short_term_cols:
            if col in balance_sheet_copy.columns:
                short_term_col = col
                break

        equity_col = None
        for col in equity_cols:
            if col in balance_sheet_copy.columns:
                equity_col = col
                break

        # Step 3: Ensure the columns exist and handle missing values
        if long_term_col is None:
            balance_sheet_copy["Long-term borrowings (Bn. VND)"] = 0
            long_term_col = "Long-term borrowings (Bn. VND)"
        else:
            balance_sheet_copy[long_term_col] = balance_sheet_copy[
                long_term_col
            ].fillna(0)

        if short_term_col is None:
            balance_sheet_copy["Short-term borrowings (Bn. VND)"] = 0
            short_term_col = "Short-term borrowings (Bn. VND)"
        else:
            balance_sheet_copy[short_term_col] = balance_sheet_copy[
                short_term_col
            ].fillna(0)

        if equity_col is None:
            raise ValueError("Owner's equity column not found in Balance Sheet")
        else:
            balance_sheet_copy[equity_col] = balance_sheet_copy[equity_col].fillna(0)

        # Step 4: Standardize column names for output
        balance_sheet_copy = balance_sheet_copy.rename(
            columns={
                long_term_col: "Long-term borrowings (Bn. VND)",
                short_term_col: "Short-term borrowings (Bn. VND)",
                equity_col: "OWNER'S EQUITY(Bn.VND)",
            }
        )

        # Step 5: Calculate Capital Employed
        balance_sheet_copy["Capital Employed (Bn. VND)"] = (
            balance_sheet_copy["Long-term borrowings (Bn. VND)"]
            + balance_sheet_copy["Short-term borrowings (Bn. VND)"]
            + balance_sheet_copy["OWNER'S EQUITY(Bn.VND)"]
        )

        # Step 6: Calculate percentages for component analysis
        total_capital = balance_sheet_copy["Capital Employed (Bn. VND)"]
        balance_sheet_copy["Long-term borrowings (%)"] = (
            balance_sheet_copy["Long-term borrowings (Bn. VND)"] / total_capital * 100
        ).fillna(0)
        balance_sheet_copy["Short-term borrowings (%)"] = (
            balance_sheet_copy["Short-term borrowings (Bn. VND)"] / total_capital * 100
        ).fillna(0)
        balance_sheet_copy["Owner's equity (%)"] = (
            balance_sheet_copy["OWNER'S EQUITY(Bn.VND)"] / total_capital * 100
        ).fillna(0)

        # Step 7: Return relevant columns
        return balance_sheet_copy[
            [
                "ticker",
                "yearReport",
                "Long-term borrowings (Bn. VND)",
                "Short-term borrowings (Bn. VND)",
                "OWNER'S EQUITY(Bn.VND)",
                "Capital Employed (Bn. VND)",
                "Long-term borrowings (%)",
                "Short-term borrowings (%)",
                "Owner's equity (%)",
            ]
        ].round(2)

    except Exception as e:
        st.error(f"Error in Capital Employed calculation: {str(e)}")
        return None
