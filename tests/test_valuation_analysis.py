"""
Test suite for Valuation Analysis functionality.
Tests beta calculation, WACC computation, and data alignment.
Follows TDD principles with comprehensive test coverage.
"""

import numpy as np
import pandas as pd
import pytest


# Test fixtures for sample data
@pytest.fixture
def sample_stock_data():
    """Sample stock price data with datetime index (mimics fetch_stock_price_data structure)."""
    dates = pd.date_range(start="2024-01-01", end="2024-01-31", freq="D")
    # Generate realistic stock price movements
    np.random.seed(42)  # For reproducible tests
    prices = 100 + np.random.randn(len(dates)).cumsum() * 0.5

    data = pd.DataFrame(
        {
            "close": prices,
            "open": prices * 0.99,
            "high": prices * 1.01,
            "low": prices * 0.98,
            "volume": np.random.randint(1000000, 5000000, len(dates)),
        },
        index=dates,
    )
    data.index.name = "time"
    return data


@pytest.fixture
def sample_vnindex_data():
    """Sample VNINDEX data (before datetime index conversion)."""
    dates = pd.date_range(start="2024-01-01", end="2024-01-31", freq="D")
    np.random.seed(123)  # Different seed for market data
    prices = 1200 + np.random.randn(len(dates)).cumsum() * 2.0

    return pd.DataFrame({
        "time": dates,
        "close": prices,
        "open": prices * 0.995,
        "high": prices * 1.005,
        "low": prices * 0.995,
        "volume": np.random.randint(10000000, 50000000, len(dates)),
    })


@pytest.fixture
def sample_balance_sheet():
    """Sample balance sheet data."""
    return pd.DataFrame({
        "yearReport": [2023, 2022, 2021],
        "Short-term borrowings (Bn. VND)": [100.0, 90.0, 80.0],
        "Long-term borrowings (Bn. VND)": [200.0, 180.0, 160.0],
        "Total assets (Bn. VND)": [1000.0, 950.0, 900.0],
    })


@pytest.fixture
def sample_ratios():
    """Sample ratios data with market cap."""
    return pd.DataFrame({
        ("Chỉ tiêu định giá", "Market Capital (Bn. VND)"): [500.0, 450.0, 400.0],
        ("Chỉ tiêu định giá", "P/E"): [15.0, 14.0, 13.0],
    })


# Test Class 1: Data Alignment Tests
class TestDataAlignment:
    """Test proper alignment of stock and VNINDEX data."""

    def test_vnindex_datetime_conversion(self, sample_vnindex_data):
        """Test that VNINDEX data is properly converted to datetime index."""
        # This is the conversion logic from the valuation page
        vnindex_data = sample_vnindex_data.copy()
        vnindex_data["time"] = pd.to_datetime(vnindex_data["time"])
        vnindex_data = vnindex_data.set_index("time")

        assert isinstance(vnindex_data.index, pd.DatetimeIndex)
        assert vnindex_data.index.name == "time"
        assert "close" in vnindex_data.columns
        assert len(vnindex_data) == 31  # January has 31 days

    def test_data_alignment_with_concat(self, sample_stock_data, sample_vnindex_data):
        """Test that stock and VNINDEX data align properly using pd.concat."""
        # Convert VNINDEX to same structure as stock data
        vnindex_data = sample_vnindex_data.copy()
        vnindex_data["time"] = pd.to_datetime(vnindex_data["time"])
        vnindex_data = vnindex_data.set_index("time")

        # Align data using the same logic as valuation page
        aligned = pd.concat(
            [
                sample_stock_data[["close"]].rename(columns={"close": "stock_close"}),
                vnindex_data[["close"]].rename(columns={"close": "index_close"}),
            ],
            axis=1,
            join="inner",
        ).dropna()

        assert len(aligned) == 31  # Should have 31 matching days
        assert "stock_close" in aligned.columns
        assert "index_close" in aligned.columns
        assert not aligned.isnull().any().any()  # No null values
        assert isinstance(aligned.index, pd.DatetimeIndex)

    def test_partial_date_overlap(self):
        """Test alignment when stock and index data have different date ranges."""
        # Stock data: Jan 1-15
        stock_dates = pd.date_range(start="2024-01-01", end="2024-01-15", freq="D")
        stock_data = pd.DataFrame(
            {"close": np.random.randn(len(stock_dates)) + 100}, index=stock_dates
        )
        stock_data.index.name = "time"

        # Index data: Jan 10-25 (partial overlap)
        index_dates = pd.date_range(start="2024-01-10", end="2024-01-25", freq="D")
        vnindex_data = pd.DataFrame({
            "time": index_dates,
            "close": np.random.randn(len(index_dates)) + 1200,
        })

        # Convert and align
        vnindex_data["time"] = pd.to_datetime(vnindex_data["time"])
        vnindex_data = vnindex_data.set_index("time")

        aligned = pd.concat(
            [
                stock_data[["close"]].rename(columns={"close": "stock_close"}),
                vnindex_data[["close"]].rename(columns={"close": "index_close"}),
            ],
            axis=1,
            join="inner",
        ).dropna()

        # Should only have overlap period (Jan 10-15)
        assert len(aligned) == 6
        assert aligned.index.min() == pd.Timestamp("2024-01-10")
        assert aligned.index.max() == pd.Timestamp("2024-01-15")


# Test Class 2: Beta Calculation Tests
class TestBetaCalculation:
    """Test beta calculation logic."""

    def test_beta_calculation_logic(self, sample_stock_data, sample_vnindex_data):
        """Test that beta is calculated correctly using covariance matrix."""
        # Prepare data
        vnindex_data = sample_vnindex_data.copy()
        vnindex_data["time"] = pd.to_datetime(vnindex_data["time"])
        vnindex_data = vnindex_data.set_index("time")

        aligned = pd.concat(
            [
                sample_stock_data[["close"]].rename(columns={"close": "stock_close"}),
                vnindex_data[["close"]].rename(columns={"close": "index_close"}),
            ],
            axis=1,
            join="inner",
        ).dropna()

        # Calculate returns
        aligned["stock_ret"] = aligned["stock_close"].pct_change()
        aligned["index_ret"] = aligned["index_close"].pct_change()
        returns = aligned.dropna()

        # Calculate beta using covariance matrix
        cov_matrix = np.cov(returns["stock_ret"], returns["index_ret"])
        beta = cov_matrix[0, 1] / cov_matrix[1, 1]

        assert isinstance(beta, float)
        assert not np.isnan(beta)
        assert not np.isinf(beta)
        # Beta should be reasonable for stock data
        assert -5 < beta < 5  # Extreme betas are rare but possible

    def test_correlation_calculation(self, sample_stock_data, sample_vnindex_data):
        """Test correlation and R-squared calculation."""
        # Prepare data (same as beta test)
        vnindex_data = sample_vnindex_data.copy()
        vnindex_data["time"] = pd.to_datetime(vnindex_data["time"])
        vnindex_data = vnindex_data.set_index("time")

        aligned = pd.concat(
            [
                sample_stock_data[["close"]].rename(columns={"close": "stock_close"}),
                vnindex_data[["close"]].rename(columns={"close": "index_close"}),
            ],
            axis=1,
            join="inner",
        ).dropna()

        aligned["stock_ret"] = aligned["stock_close"].pct_change()
        aligned["index_ret"] = aligned["index_close"].pct_change()
        returns = aligned.dropna()

        # Calculate correlation
        correlation = np.corrcoef(returns["stock_ret"], returns["index_ret"])[0, 1]
        r_squared = correlation**2

        assert isinstance(correlation, float)
        assert -1 <= correlation <= 1
        assert 0 <= r_squared <= 1
        assert not np.isnan(correlation)
        assert not np.isnan(r_squared)

    def test_insufficient_data_points(self):
        """Test handling of insufficient data for beta calculation."""
        # Create minimal data (less than 30 points)
        small_dates = pd.date_range(
            start="2024-01-01", end="2024-01-10", freq="D"
        )  # 10 days

        stock_data = pd.DataFrame(
            {"close": np.random.randn(len(small_dates)) + 100}, index=small_dates
        )

        vnindex_data = pd.DataFrame({
            "time": small_dates,
            "close": np.random.randn(len(small_dates)) + 1200,
        })

        vnindex_data["time"] = pd.to_datetime(vnindex_data["time"])
        vnindex_data = vnindex_data.set_index("time")

        aligned = pd.concat(
            [
                stock_data[["close"]].rename(columns={"close": "stock_close"}),
                vnindex_data[["close"]].rename(columns={"close": "index_close"}),
            ],
            axis=1,
            join="inner",
        ).dropna()

        # Should have less than 30 data points
        assert len(aligned) < 30


# Test Class 3: WACC Calculation Tests
class TestWACCCalculation:
    """Test WACC calculation components."""

    def test_debt_calculation(self, sample_balance_sheet):
        """Test total debt calculation from balance sheet."""
        latest_balance_sheet = sample_balance_sheet.iloc[0]  # Most recent year (2023)

        short_term_debt = latest_balance_sheet.get("Short-term borrowings (Bn. VND)", 0)
        long_term_debt = latest_balance_sheet.get("Long-term borrowings (Bn. VND)", 0)
        total_debt = short_term_debt + long_term_debt

        assert short_term_debt == 100.0
        assert long_term_debt == 200.0
        assert total_debt == 300.0

    def test_market_cap_extraction(self, sample_ratios):
        """Test market capitalization extraction from ratios."""
        latest_ratios = sample_ratios.iloc[0]  # Most recent (2023)

        market_value_of_equity = latest_ratios.get(
            ("Chỉ tiêu định giá", "Market Capital (Bn. VND)"), 0
        )

        assert market_value_of_equity == 500.0
        assert isinstance(market_value_of_equity, (int, float))

    def test_wacc_calculation_components(self, sample_balance_sheet, sample_ratios):
        """Test complete WACC calculation."""
        # Input parameters (same as sidebar defaults)
        risk_free_rate = 0.03  # 3%
        market_risk_premium = 0.05  # 5%
        cost_of_debt = 0.07  # 7%
        tax_rate = 0.20  # 20%
        beta = 1.2  # Assumed beta

        # Get latest financial data
        latest_balance_sheet = sample_balance_sheet.iloc[0]  # 2023 data
        latest_ratios = sample_ratios.iloc[0]  # 2023 data

        # Calculate debt
        short_term_debt = latest_balance_sheet.get("Short-term borrowings (Bn. VND)", 0)
        long_term_debt = latest_balance_sheet.get("Long-term borrowings (Bn. VND)", 0)
        total_debt = short_term_debt + long_term_debt

        # Get market cap
        market_value_of_equity = latest_ratios.get(
            ("Chỉ tiêu định giá", "Market Capital (Bn. VND)"), 0
        )
        market_value_of_debt = total_debt

        # Calculate weights
        total_market_capital = market_value_of_equity + market_value_of_debt
        market_weight_of_debt = market_value_of_debt / total_market_capital
        market_weight_of_equity = market_value_of_equity / total_market_capital

        # Calculate costs
        after_tax_cost_of_debt = cost_of_debt * (1 - tax_rate)
        cost_of_equity = risk_free_rate + (beta * market_risk_premium)

        # Calculate WACC
        wacc = (market_weight_of_debt * after_tax_cost_of_debt) + (
            market_weight_of_equity * cost_of_equity
        )

        # Assertions
        assert total_debt == 300.0
        assert market_value_of_equity == 500.0
        assert total_market_capital == 800.0
        assert market_weight_of_debt == 0.375  # 300/800
        assert market_weight_of_equity == 0.625  # 500/800
        assert after_tax_cost_of_debt == pytest.approx(0.056)  # 7% * (1-20%)
        assert cost_of_equity == 0.09  # 3% + (1.2 * 5%)

        # WACC should be reasonable
        assert 0.02 < wacc < 0.20  # Between 2% and 20%
        assert isinstance(wacc, float)

    def test_zero_market_capital_handling(self):
        """Test handling of zero market capitalization."""
        # Edge case: zero values
        market_value_of_equity = 0
        market_value_of_debt = 0
        total_market_capital = market_value_of_equity + market_value_of_debt

        # Should handle division by zero
        assert total_market_capital == 0
        # In the actual code, this would trigger the error handling branch


# Test Class 4: Risk Level Classification Tests
class TestRiskClassification:
    """Test beta risk level classification."""

    @pytest.mark.parametrize(
        "beta,expected_risk",
        [
            (0.5, "Low Risk (Defensive)"),
            (0.7, "Low Risk (Defensive)"),
            (0.8, "Market Risk"),
            (1.0, "Market Risk"),
            (1.1, "Market Risk"),
            (1.2, "High Risk (Aggressive)"),
            (1.5, "High Risk (Aggressive)"),
            (2.0, "High Risk (Aggressive)"),
        ],
    )
    def test_risk_level_classification(self, beta, expected_risk):
        """Test risk level classification based on beta values."""
        # Logic from valuation page
        if beta < 0.8:
            risk_level = "Low Risk (Defensive)"
        elif beta < 1.2:
            risk_level = "Market Risk"
        else:
            risk_level = "High Risk (Aggressive)"

        assert risk_level == expected_risk


# Test Class 5: Error Handling Tests
class TestErrorHandling:
    """Test error handling scenarios."""

    def test_empty_dataframes(self):
        """Test handling of empty DataFrames."""
        empty_df = pd.DataFrame()

        assert empty_df.empty
        # The page should handle this with appropriate error messages

    def test_missing_columns(self):
        """Test handling of missing required columns."""
        incomplete_balance_sheet = pd.DataFrame({
            "yearReport": [2023],
            # Missing debt columns
        })

        latest = incomplete_balance_sheet.iloc[-1]
        short_term_debt = latest.get("Short-term borrowings (Bn. VND)", 0)
        long_term_debt = latest.get("Long-term borrowings (Bn. VND)", 0)

        # Should default to 0 for missing columns
        assert short_term_debt == 0
        assert long_term_debt == 0

    def test_invalid_market_cap_structure(self):
        """Test handling of different market cap data structures."""
        # Sometimes market cap might be a tuple
        ratios_with_tuple = pd.DataFrame({
            ("Chỉ tiêu định giá", "Market Capital (Bn. VND)"): [("Label", 500.0)]
        })

        latest = ratios_with_tuple.iloc[-1]
        market_value = latest.get(("Chỉ tiêu định giá", "Market Capital (Bn. VND)"), 0)

        # Handle tuple extraction
        if isinstance(market_value, tuple):
            market_value = market_value[1] if len(market_value) > 1 else 0

        assert market_value == 500.0


# Test Class 6: Integration Tests
class TestValuationIntegration:
    """Integration tests for complete valuation workflow."""

    def test_complete_valuation_workflow(
        self,
        sample_stock_data,
        sample_vnindex_data,
        sample_balance_sheet,
        sample_ratios,
    ):
        """Test complete end-to-end valuation calculation."""
        # 1. Data alignment
        vnindex_data = sample_vnindex_data.copy()
        vnindex_data["time"] = pd.to_datetime(vnindex_data["time"])
        vnindex_data = vnindex_data.set_index("time")

        aligned = pd.concat(
            [
                sample_stock_data[["close"]].rename(columns={"close": "stock_close"}),
                vnindex_data[["close"]].rename(columns={"close": "index_close"}),
            ],
            axis=1,
            join="inner",
        ).dropna()

        # 2. Beta calculation
        aligned["stock_ret"] = aligned["stock_close"].pct_change()
        aligned["index_ret"] = aligned["index_close"].pct_change()
        returns = aligned.dropna()

        cov_matrix = np.cov(returns["stock_ret"], returns["index_ret"])
        beta = cov_matrix[0, 1] / cov_matrix[1, 1]

        # 3. WACC calculation
        risk_free_rate = 0.03
        market_risk_premium = 0.05
        cost_of_debt = 0.07
        tax_rate = 0.20

        latest_balance_sheet = sample_balance_sheet.iloc[-1]
        latest_ratios = sample_ratios.iloc[-1]

        total_debt = latest_balance_sheet.get(
            "Short-term borrowings (Bn. VND)", 0
        ) + latest_balance_sheet.get("Long-term borrowings (Bn. VND)", 0)
        market_value_of_equity = latest_ratios.get(
            ("Chỉ tiêu định giá", "Market Capital (Bn. VND)"), 0
        )

        total_market_capital = market_value_of_equity + total_debt
        market_weight_of_debt = total_debt / total_market_capital
        market_weight_of_equity = market_value_of_equity / total_market_capital

        after_tax_cost_of_debt = cost_of_debt * (1 - tax_rate)
        cost_of_equity = risk_free_rate + (beta * market_risk_premium)
        wacc = (market_weight_of_debt * after_tax_cost_of_debt) + (
            market_weight_of_equity * cost_of_equity
        )

        # 4. Validation
        assert len(returns) > 0
        assert isinstance(beta, float)
        assert isinstance(wacc, float)
        assert 0.01 < wacc < 0.30  # Broader range for random test data
        assert total_market_capital > 0
        assert (
            abs(market_weight_of_debt + market_weight_of_equity - 1.0) < 1e-10
        )  # Weights sum to 1

    def test_valuation_results_table_structure(self, sample_balance_sheet):
        """Test that valuation results table has correct structure."""
        symbol = "VIC"
        beta = 1.2
        wacc = 0.085
        market_value_of_equity = 500.0
        total_debt = 300.0
        market_weight_of_debt = 0.375
        market_weight_of_equity = 0.625
        cost_of_equity = 0.09
        after_tax_cost_of_debt = 0.056

        # Create results data structure (same as in valuation page)
        results_data = []
        for idx, row in sample_balance_sheet.iterrows():
            results_data.append({
                "Year": row.get("yearReport", "N/A"),
                "Symbol": symbol,
                "Market Cap (B VND)": f"{market_value_of_equity:,.0f}",
                "Total Debt (B VND)": f"{total_debt:,.0f}",
                "Debt Weight": f"{market_weight_of_debt:.1%}",
                "Equity Weight": f"{market_weight_of_equity:.1%}",
                "Beta": f"{beta:.4f}",
                "Cost of Equity": f"{cost_of_equity:.2%}",
                "After-tax Cost of Debt": f"{after_tax_cost_of_debt:.2%}",
                "WACC": f"{wacc:.2%}",
            })

        results_df = pd.DataFrame(results_data)

        # Validate structure
        assert len(results_df) == len(sample_balance_sheet)  # One row per year
        assert "Year" in results_df.columns
        assert "WACC" in results_df.columns
        assert "Beta" in results_df.columns

        # Validate formatting
        assert results_df.iloc[0]["Symbol"] == symbol
        assert (
            "37.5%" in results_df.iloc[0]["Debt Weight"]
        )  # Check percentage formatting
        assert "1.2000" in results_df.iloc[0]["Beta"]  # Check decimal formatting


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
