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
    financial_leverage_data = financial_leverage_data.rename(columns={
        'Operating Profit/Loss': 'EBIT (Bn. VND)',
        'Net Profit For the Year': 'Net Income (Bn. VND)'
    })
    
    # Sort by ticker and year
    financial_leverage_data = financial_leverage_data.sort_values(['ticker', 'yearReport'])
    
    # Calculate year-over-year percentage changes for each ticker
    financial_leverage_data['EBIT % Change'] = financial_leverage_data.groupby('ticker')['EBIT (Bn. VND)'].pct_change() * 100
    financial_leverage_data['Net Income % Change'] = financial_leverage_data.groupby('ticker')['Net Income (Bn. VND)'].pct_change() * 100
    
    # Calculate DFL
    financial_leverage_data['DFL'] = financial_leverage_data['Net Income % Change'] / financial_leverage_data['EBIT % Change']
    
    # Handle infinite or NaN values (when EBIT % Change is near zero)
    financial_leverage_data['DFL'] = financial_leverage_data['DFL'].replace([np.inf, -np.inf], np.nan)
    
    # Select relevant columns
    dfl_results = financial_leverage_data[['ticker', 'yearReport', 
                                         'EBIT (Bn. VND)', 'Net Income (Bn. VND)', 
                                         'EBIT % Change', 'Net Income % Change', 
                                         'DFL']]
    
    return dfl_results

calculate_degree_of_financial_leverage(IncomeStatement)