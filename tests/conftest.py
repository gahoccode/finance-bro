import os
import pathlib
import tempfile

import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def sample_stock_data():
    """Generate sample stock price data for testing."""
    symbols = ["REE", "FMC", "DHC"]
    dates = pd.date_range(start="2024-01-01", end="2024-12-31", freq="D")

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
            "time": dates,
            "close": prices,
            "volume": np.random.randint(1000, 100000, len(dates)),
        }

    return data


@pytest.fixture
def sample_returns_df(sample_stock_data):
    """Generate returns DataFrame from stock data."""
    prices_df = pd.DataFrame({
        symbol: data["close"] for symbol, data in sample_stock_data.items()
    })
    prices_df.index = sample_stock_data["REE"]["time"]  # Use dates as index

    returns = prices_df.pct_change().dropna()
    return returns


@pytest.fixture
def sample_weights():
    """Sample portfolio weights for testing."""
    return {"REE": 0.4, "FMC": 0.35, "DHC": 0.25}


@pytest.fixture
def temp_reports_dir():
    """Create a temporary directory for test reports."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        reports_dir = os.path.join(tmp_dir, "exports", "reports")
        pathlib.Path(reports_dir).mkdir(exist_ok=True, parents=True)
        yield reports_dir


@pytest.fixture
def mock_timestamp():
    """Fixed timestamp for consistent test results."""
    return "20250109_120000"


# Company Overview Data Fixtures for VnStock API Testing


@pytest.fixture
def mock_ownership_data():
    """Mock ownership data matching vnstock API structure."""
    return pd.DataFrame({
        "share_holder": [
            "State Capital Investment Corporation",
            "Individual Investors",
            "Foreign Investors",
        ],
        "quantity": [150000000, 200000000, 100000000],
        "share_own_percent": [0.30, 0.40, 0.20],
    })


@pytest.fixture
def mock_management_data():
    """Mock management data matching vnstock API structure."""
    return pd.DataFrame({
        "officer_name": ["Nguyen Van A", "Tran Thi B", "Le Van C"],
        "position_short_name": ["CEO", "CFO", "CTO"],
        "quantity": [1000000, 500000, 300000],
        "officer_own_percent": [0.002, 0.001, 0.0006],
    })


@pytest.fixture
def mock_subsidiaries_data():
    """Mock subsidiaries data matching vnstock API structure."""
    return pd.DataFrame({
        "organ_name": [
            "REE Power Company",
            "REE Construction Ltd",
            "REE Services JSC",
        ],
        "ownership_percent": [0.95, 0.80, 0.60],
        "type": ["Subsidiary", "Subsidiary", "Associated Company"],
    })


@pytest.fixture
def mock_insider_deals_data():
    """Mock insider deals data matching vnstock API structure."""
    return pd.DataFrame({
        "deal_announce_date": pd.to_datetime([
            "2024-01-15",
            "2024-01-10",
            "2024-01-05",
        ]),
        "deal_action": ["Mua", "Bán", "Mua"],
        "deal_method": ["Thỏa thuận", "Khớp lệnh", "Thỏa thuận"],
        "deal_quantity": [100000, 50000, 75000],
        "deal_price": [65000, 64500, 64000],
        "deal_ratio": [0.01, 0.005, 0.0075],
    })


@pytest.fixture
def mock_foreign_trading_data():
    """Mock foreign trading data matching vnstock API structure."""
    return pd.DataFrame({
        "foreign_volume": [1500000],
        "total_volume": [15000000],
        "foreign_room": [250000000],
        "foreign_holding_room": [200000000],
        "current_holding_room": [180000000],
        "max_holding_room": [250000000],
        "current_holding_ratio": [0.36],
        "max_holding_ratio": [0.49],
        "ev": [45000000000],
    })


@pytest.fixture
def mock_company_reports_data():
    """Mock company reports data with unsorted dates to test sorting functionality."""
    return pd.DataFrame({
        "date": [
            "2024-01-15",
            "2024-01-20",
            "2024-01-10",
        ],  # Intentionally unsorted
        "description": [
            "REE announces Q4 2023 financial results",
            "REE Board meeting resolution",
            "REE dividend distribution announcement",
        ],
        "link": [
            "https://example.com/ree-q4-results",
            "https://example.com/ree-board-meeting",
            "https://example.com/ree-dividend",
        ],
        "name": [
            "REE Corporation reported strong Q4 performance with revenue growth of 15%",
            "Board approved strategic initiatives for 2024 expansion plans",
            "Dividend of 1,500 VND per share announced for shareholders",
        ],
    })
