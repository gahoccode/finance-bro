# Phase 2: Technical Analysis Enhancement Plan

## Overview
This document outlines the plan to enhance the Technical Analysis page by adding interval parameter selection ('1D', '1W', '1M') to provide users with flexible time-based chart viewing options.

## Current State Analysis
After reviewing the Technical Analysis page (`pages/Technical_Analysis.py`), the current implementation:
- Uses fixed 30-day historical data range
- Uses hardcoded '1D' interval in data fetching
- Does not provide user control over data granularity

## Enhancement Plan

### 1. Parameter Enhancement
**Update `get_stock_data()` function:**
- Add `interval` parameter with default to '1D'
- Add `days` parameter calculation based on interval:
  - '1D': 30 days (current)
  - '1W': ~6 months (180-200 days)  
  - '1M': ~2 years (730 days)
- Update vnstock API call to use dynamic interval

### 2. Sidebar Implementation
**Add sidebar controls:**
- Interval selection dropdown with options: 
  - "Daily (1D)"
  - "Weekly (1W)" 
  - "Monthly (1M)"
- Store selection in session state for persistence
- Update all data retrieval calls to use selected interval

### 3. Chart Display Updates
**Update candlestick chart generation:**
- Dynamic title suffix showing selected interval
- Adjust chart styling if needed for different intervals
- Ensure proper data scaling for weekly/monthly views

### 4. User Experience Flow
1. User lands on Technical Analysis page
2. Sidebar displays interval selection (default: 1D)
3. Charts update automatically based on selection
4. Data range adjusts to show meaningful timeframe for selected interval

### 5. Technical Implementation

#### Updated Function Signature
```python
def get_stock_data(ticker, interval='1D'):
    """Get historical stock data based on interval parameter"""
    # days parameter calculation:
    if interval == '1D':
        days = 30  # 1 month
    elif interval == '1W':
        days = 180  # ~6 months
    elif interval == '1M':
        days = 730  # ~2 years
    
    # Update vnstock API call
    data = stock.quote.history(interval=interval, ...)
```

#### Sidebar Implementation
```python
# Add to main() function
with st.sidebar:
    st.subheader("Chart Configuration")
    interval = st.selectbox(
        "Select Interval",
        options=['1D', '1W', '1M'],
        format_func=lambda x: {'1D': 'Daily', '1W': 'Weekly', '1M': 'Monthly'}[x],
        key='ta_interval'
    )
```

### 6. Testing Requirements
- Verify all three intervals work correctly
- Check data range accuracy for each interval
- Confirm charts render properly at different granularities
- Test sidebar persistence across page refreshes

### 7. Backward Compatibility
- Default behavior unchanged (1D selection)
- No breaking changes to existing functionality
- Enhanced user experience without disrupting existing workflows

## Implementation Timeline
1. Update `get_stock_data()` with interval parameter
2. Add sidebar interval selection controls
3. Update all data retrieval calls to use dynamic interval
4. Update chart titles and formatting
5. Final testing and validation

## Expected Outcome
Users will have full control over time granularity in technical analysis charts, providing more detailed insights for different trading strategies and time horizons.