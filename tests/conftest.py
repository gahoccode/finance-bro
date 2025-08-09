import pytest
import pandas as pd
import numpy as np
import tempfile
import os
from datetime import datetime, timedelta


@pytest.fixture
def sample_stock_data():
    """Generate sample stock price data for testing."""
    symbols = ['REE', 'FMC', 'DHC']
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    
    # Remove weekends (simple approximation)
    dates = [d for d in dates if d.weekday() < 5][:250]  # ~1 year of trading days
    
    data = {}
    np.random.seed(42)  # For reproducible tests
    
    for symbol in symbols:
        # Generate realistic stock prices with some volatility
        base_price = np.random.uniform(20000, 50000)  # VND thousands
        returns = np.random.normal(0.0008, 0.02, len(dates))  # Daily returns
        prices = [base_price]
        
        for r in returns[1:]:
            new_price = prices[-1] * (1 + r)
            prices.append(max(new_price, 1000))  # Prevent negative prices
        
        data[symbol] = {
            'time': dates,
            'close': prices,
            'volume': np.random.randint(1000, 100000, len(dates))
        }
    
    return data


@pytest.fixture
def sample_returns_df(sample_stock_data):
    """Generate returns DataFrame from stock data."""
    prices_df = pd.DataFrame({
        symbol: data['close'] for symbol, data in sample_stock_data.items()
    })
    prices_df.index = sample_stock_data['REE']['time']  # Use dates as index
    
    returns = prices_df.pct_change().dropna()
    return returns


@pytest.fixture
def sample_weights():
    """Sample portfolio weights for testing."""
    return {
        'REE': 0.4,
        'FMC': 0.35,
        'DHC': 0.25
    }


@pytest.fixture
def temp_reports_dir():
    """Create a temporary directory for test reports."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        reports_dir = os.path.join(tmp_dir, 'exports', 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        yield reports_dir


@pytest.fixture
def mock_timestamp():
    """Fixed timestamp for consistent test results."""
    return "20250109_120000"