# Technical Analysis Screener

## Overview
This module provides functionality to screen stocks based on technical analysis indicators, specifically focusing on stocks that are showing "heating up" signals.

## Function: `get_heating_up_stocks()`

### Description
Fetches and filters stocks that have the "heating_up" indicator showing "Overheated in previous trading session".

### Parameters
- None (function takes no parameters)

### Returns
- `pandas.DataFrame`: Filtered DataFrame containing stocks with heating up indicators

### Implementation

```python
from vnstock import Screener

def get_heating_up_stocks():
    """Get stocks with heating_up indicator"""
    
    # Initialize screener and get data
    screener = Screener(show_log=False)
    screener_df = screener.stock(
        params={"exchangeName": "HOSE,HNX,UPCOM"},
        limit=1700,
        lang="en"
    )
    
    # Filter for heating_up condition only
    filtered_stocks = screener_df[
        screener_df['heating_up'] == 'Overheated in previous trading session'
    ]
    
    # Select only required columns
    result_columns = [
        'ticker', 'industry', 'exchange', 'heating_up', 'uptrend', 'breakout', 
        'tcbs_buy_sell_signal', 'pct_1y_from_peak', 'pct_away_from_hist_peak', 
        'pct_1y_from_bottom', 'pct_off_hist_bottom', 'active_buy_pct', 'strong_buy_pct', 'market_cap',
        'avg_trading_value_5d', 'total_trading_value', 'foreign_transaction', 'num_increase_continuous_day'
    ]
    
    # Only include columns that exist in the DataFrame
    available_columns = [col for col in result_columns if col in filtered_stocks.columns]
    
    return filtered_stocks[available_columns]
```

## Usage Example

```python
# Execute the function
heating_stocks = get_heating_up_stocks()
```

## Next Steps

Use the `get_heating_up_stocks()` function to fetch data and pass the `heating_stocks['ticker']` to loop through all returned tickers and fetch OHLCV data from those tickers. Display the candlesticks charts of those tickers.

### Acceptance Criteria
- Display all candlesticks charts of fetched tickers in a separate manner
- Display the dataframe `heating_stocks` 
