import pandas as pd


def calculate_effective_tax_rate(IncomeStatement, CashFlow):
    """
    Calculate the effective tax rate using Income Statement and Cash Flow data.

    Effective Tax Rate = Tax Expense / Profit Before Tax

    Parameters:
    -----------
    IncomeStatement : pandas DataFrame
        Income Statement data with columns: ticker, yearReport, etc.
    CashFlow : pandas DataFrame
        Cash Flow Statement data with columns: ticker, yearReport, 'Net Profit/Loss before tax', 'Business Income Tax paid'

    Returns:
    --------
    pandas DataFrame
        DataFrame with effective tax rate calculations
    """
    # Merge the necessary data from both financial statements
    tax_data_df = pd.merge(
        IncomeStatement[["ticker", "yearReport", "Profit before tax"]],
        CashFlow[
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
