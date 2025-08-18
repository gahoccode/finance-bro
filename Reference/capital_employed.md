def calculate_capital_employed(BalanceSheet):
    """
    Capital Employed = Long-term borrowings + Short-term borrowings + Owner’s equity
    """
    balance_sheet_copy = BalanceSheet.copy()

    # 1️⃣ normalise header text (strip & replace Unicode dashes with ASCII “-”)
    balance_sheet_copy.columns = (
        balance_sheet_copy.columns
            .str.strip()
            .str.replace(r'[\u2010-\u2015]', '-', regex=True)
    )

    # 2️⃣ be sure the three columns exist and have no NaN
    for col in ['Long-term borrowings (Bn. VND)',
                'Short-term borrowings (Bn. VND)',
                "OWNER'S EQUITY(Bn.VND)"]:
        if col not in balance_sheet_copy.columns:
            balance_sheet_copy[col] = 0
        else:
            balance_sheet_copy[col] = balance_sheet_copy[col].fillna(0)

    # 3️⃣ compute Capital Employed
    balance_sheet_copy['Capital Employed (Bn. VND)'] = (
        balance_sheet_copy['Long-term borrowings (Bn. VND)'] +
        balance_sheet_copy['Short-term borrowings (Bn. VND)'] +
        balance_sheet_copy["OWNER'S EQUITY(Bn.VND)"]
    )

    return balance_sheet_copy[['ticker', 'yearReport',
                               'Long-term borrowings (Bn. VND)',
                               'Short-term borrowings (Bn. VND)',
                               "OWNER'S EQUITY(Bn.VND)",
                               'Capital Employed (Bn. VND)']]

# Example usage (commented out):
capital_employed_df = calculate_capital_employed(BalanceSheet)