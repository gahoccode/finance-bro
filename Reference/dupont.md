import pandas as pd
import numpy as np

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
    # Step 1: Combine necessary data from all three statements
    # Start with Income Statement data for revenue and net income
    income_data = IncomeStatement[['ticker', 'yearReport', 'Revenue (Bn. VND)', 'Attribute to parent company (Bn. VND)']].copy()
    
    # Rename for clarity
    income_data = income_data.rename(columns={'Attribute to parent company (Bn. VND)': 'Net Income (Bn. VND)'})
    
    # Step 2: Add Balance Sheet data for assets and equity
    balance_data = BalanceSheet[['ticker', 'yearReport', 'TOTAL ASSETS (Bn. VND)', "OWNER'S EQUITY(Bn.VND)"]].copy()
    
    # Merge the dataframes
    dupont_df = pd.merge(income_data, balance_data, on=['ticker', 'yearReport'], how='inner')
    
    # Step 3: Group by ticker to calculate year-over-year values and averages
    # Sort by ticker and year
    dupont_df = dupont_df.sort_values(['ticker', 'yearReport'])
    
    # Calculate average total assets and equity for each year (current + previous year) / 2
    # First create shifted columns for previous year's values
    dupont_df['Prev_Assets'] = dupont_df.groupby('ticker')['TOTAL ASSETS (Bn. VND)'].shift(1)
    dupont_df['Prev_Equity'] = dupont_df.groupby('ticker')["OWNER'S EQUITY(Bn.VND)"].shift(1)
    
    # Calculate averages
    dupont_df['Average Total Assets (Bn. VND)'] = (dupont_df['TOTAL ASSETS (Bn. VND)'] + dupont_df['Prev_Assets']) / 2
    dupont_df['Average Equity (Bn. VND)'] = (dupont_df["OWNER'S EQUITY(Bn.VND)"] + dupont_df['Prev_Equity']) / 2
    
    # For the first year of each ticker, we don't have previous year data, so use current year
    dupont_df['Average Total Assets (Bn. VND)'] = dupont_df['Average Total Assets (Bn. VND)'].fillna(
        dupont_df['TOTAL ASSETS (Bn. VND)'])
    dupont_df['Average Equity (Bn. VND)'] = dupont_df['Average Equity (Bn. VND)'].fillna(
        dupont_df["OWNER'S EQUITY(Bn.VND)"])
    
    # Step 4: Calculate the 3 DuPont components
    # Net Profit Margin = Net Income / Revenue
    dupont_df['Net Profit Margin'] = dupont_df['Net Income (Bn. VND)'] / dupont_df['Revenue (Bn. VND)']
    
    # Asset Turnover = Revenue / Average Total Assets
    dupont_df['Asset Turnover'] = dupont_df['Revenue (Bn. VND)'] / dupont_df['Average Total Assets (Bn. VND)']
    
    # Financial Leverage = Average Total Assets / Average Equity
    dupont_df['Financial Leverage'] = dupont_df['Average Total Assets (Bn. VND)'] / dupont_df['Average Equity (Bn. VND)']
    
    # Step 5: Calculate ROE using DuPont formula
    dupont_df['ROE (DuPont)'] = dupont_df['Net Profit Margin'] * dupont_df['Asset Turnover'] * dupont_df['Financial Leverage']
    
    # Step 6: Calculate ROE directly for validation
    dupont_df['ROE (Direct)'] = dupont_df['Net Income (Bn. VND)'] / dupont_df['Average Equity (Bn. VND)']
    
    # Step 7: Clean up the DataFrame and select relevant columns
    dupont_analysis = dupont_df[[
        'ticker', 'yearReport', 
        'Net Income (Bn. VND)', 'Revenue (Bn. VND)',
        'Average Total Assets (Bn. VND)', 'Average Equity (Bn. VND)',
        'Net Profit Margin', 'Asset Turnover', 'Financial Leverage',
        'ROE (DuPont)', 'ROE (Direct)'
    ]]
    
    # Convert ratios to percentages for better readability
    dupont_analysis['Net Profit Margin'] = dupont_analysis['Net Profit Margin'] * 100
    dupont_analysis['ROE (DuPont)'] = dupont_analysis['ROE (DuPont)'] * 100
    dupont_analysis['ROE (Direct)'] = dupont_analysis['ROE (Direct)'] * 100
    
    # Round values for better display
    dupont_analysis = dupont_analysis.round({
        'Net Profit Margin': 2,
        'Asset Turnover': 2,
        'Financial Leverage': 2,
        'ROE (DuPont)': 2,
        'ROE (Direct)': 2
    })
    
    return dupont_analysis

# Usage:
dupont_analysis = create_dupont_analysis(IncomeStatement, BalanceSheet, CashFlow)
dupont_analysis