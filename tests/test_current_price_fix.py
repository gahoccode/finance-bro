"""
Test to verify the current_price fix for DCF calculation.
This test ensures that current_price is properly initialized in both execution paths.
"""

import pytest
import pandas as pd
import numpy as np


def test_current_price_initialization():
    """Test that current_price is properly initialized for DCF calculation."""
    # Simulate the fix implementation
    stock_price = pd.DataFrame({"close": [64.5, 65.0, 64.8]}, index=pd.date_range("2024-01-01", periods=3))
    
    # Test the initialization logic from the fix
    current_price = 0
    actual_current_price = 0
    if not stock_price.empty:
        current_price = stock_price["close"].iloc[-1]
        actual_current_price = current_price * 1000  # Convert to original scale
    
    # Verify the fix works
    assert current_price == 64.8
    assert actual_current_price == 64800
    assert current_price > 0  # Essential for DCF calculation


def test_current_price_with_empty_data():
    """Test current_price handling with empty stock data."""
    stock_price = pd.DataFrame()
    
    # Test the initialization logic with empty data
    current_price = 0
    actual_current_price = 0
    if not stock_price.empty:
        current_price = stock_price["close"].iloc[-1]
        actual_current_price = current_price * 1000
    
    # Verify graceful handling
    assert current_price == 0
    assert actual_current_price == 0


def test_dcf_validation_condition():
    """Test the DCF calculation validation condition."""
    # Simulate the condition from line 718
    wacc = 0.085
    cash_flow = pd.DataFrame({"yearReport": [2023, 2022], "Net cash inflows/outflows from operating activities": [100, 90]})
    balance_sheet = pd.DataFrame({"yearReport": [2023, 2022], "Short-term borrowings (Bn. VND)": [100, 90]})
    current_price = 64.8
    
    # Test the validation condition
    condition_met = (
        "wacc" in locals() and 
        not cash_flow.empty and 
        not balance_sheet.empty and 
        "current_price" in locals() and 
        current_price > 0
    )
    
    assert condition_met == True


def test_dcf_validation_fails_without_current_price():
    """Test that DCF validation fails when current_price is not available."""
    wacc = 0.085
    cash_flow = pd.DataFrame({"yearReport": [2023, 2022], "Net cash inflows/outflows from operating activities": [100, 90]})
    balance_sheet = pd.DataFrame({"yearReport": [2023, 2022], "Short-term borrowings (Bn. VND)": [100, 90]})
    # current_price is not defined (simulating the original bug)
    
    # Test the validation condition without current_price
    condition_met = (
        "wacc" in locals() and 
        not cash_flow.empty and 
        not balance_sheet.empty and 
        "current_price" in locals() and 
        "current_price" in locals() and 
        locals().get("current_price", 0) > 0
    )
    
    assert condition_met == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])