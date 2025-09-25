"""Tests for effective tax rate calculation function."""

import numpy as np
import pandas as pd

from src.services.financial_analysis import calculate_effective_tax_rate


class TestEffectiveTaxRateCalculation:
    """Test cases for effective tax rate calculation."""

    def test_calculate_effective_tax_rate_basic(self):
        """Test basic effective tax rate calculation."""
        # Create sample Income Statement data
        income_statement = pd.DataFrame({
            "ticker": ["VIC", "VIC", "VIC"],
            "yearReport": [2021, 2022, 2023],
            "Profit before tax": [1000, 1200, 1500],  # Billions VND
        })

        # Create sample Cash Flow data
        cash_flow = pd.DataFrame({
            "ticker": ["VIC", "VIC", "VIC"],
            "yearReport": [2021, 2022, 2023],
            "Business Income Tax paid": [
                -200,
                -240,
                -300,
            ],  # Negative values (typical in cash flow)
            "Net Profit/Loss before tax": [1000, 1200, 1500],  # Fallback values
        })

        # Calculate effective tax rate
        result = calculate_effective_tax_rate(income_statement, cash_flow)

        # Verify structure
        assert not result.empty
        assert len(result) == 3
        assert all(
            col in result.columns
            for col in [
                "ticker",
                "yearReport",
                "Profit Before Tax (Bn. VND)",
                "Tax Paid (Bn. VND)",
                "Effective Tax Rate",
            ]
        )

        # Verify calculations
        # 2021: 200 / 1000 = 0.20 (20%)
        # 2022: 240 / 1200 = 0.20 (20%)
        # 2023: 300 / 1500 = 0.20 (20%)
        expected_rates = [0.20, 0.20, 0.20]
        actual_rates = result["Effective Tax Rate"].tolist()

        for expected, actual in zip(expected_rates, actual_rates, strict=False):
            assert abs(actual - expected) < 0.001

    def test_calculate_effective_tax_rate_with_missing_income_statement_data(self):
        """Test effective tax rate calculation when Income Statement data is missing."""
        # Income Statement with missing "Profit before tax" values
        income_statement = pd.DataFrame({
            "ticker": ["VIC", "VIC"],
            "yearReport": [2022, 2023],
            "Profit before tax": [np.nan, 1500],  # Missing data for 2022
        })

        # Cash Flow with complete data
        cash_flow = pd.DataFrame({
            "ticker": ["VIC", "VIC"],
            "yearReport": [2022, 2023],
            "Business Income Tax paid": [-240, -300],
            "Net Profit/Loss before tax": [1200, 1500],  # Fallback values
        })

        result = calculate_effective_tax_rate(income_statement, cash_flow)

        # Verify that fallback values from Cash Flow are used
        assert not result.empty
        assert len(result) == 2

        # 2022: Should use 1200 from Cash Flow fallback -> 240/1200 = 0.20
        # 2023: Should use 1500 from Income Statement -> 300/1500 = 0.20
        expected_rates = [0.20, 0.20]
        actual_rates = result["Effective Tax Rate"].tolist()

        for expected, actual in zip(expected_rates, actual_rates, strict=False):
            assert abs(actual - expected) < 0.001

    def test_calculate_effective_tax_rate_edge_cases(self):
        """Test effective tax rate calculation with edge cases."""
        # Test with zero and negative profits
        income_statement = pd.DataFrame({
            "ticker": ["VIC", "VIC", "VIC", "VIC"],
            "yearReport": [2020, 2021, 2022, 2023],
            "Profit before tax": [
                0,
                -500,
                1000,
                2000,
            ],  # Zero, negative, positive profits
        })

        cash_flow = pd.DataFrame({
            "ticker": ["VIC", "VIC", "VIC", "VIC"],
            "yearReport": [2020, 2021, 2022, 2023],
            "Business Income Tax paid": [
                -50,
                -100,
                -200,
                -600,
            ],  # Various tax payments
            "Net Profit/Loss before tax": [0, -500, 1000, 2000],
        })

        result = calculate_effective_tax_rate(income_statement, cash_flow)

        # Verify structure
        assert not result.empty
        assert len(result) == 4

        # Verify that effective tax rates are clipped between 0 and 1
        effective_rates = result["Effective Tax Rate"].tolist()
        for rate in effective_rates:
            assert 0 <= rate <= 1

        # Verify specific calculations
        # 2020: 50/0 -> inf, clipped to 1.0
        # 2021: 100/(-500) -> negative, clipped to 0.0
        # 2022: 200/1000 = 0.20
        # 2023: 600/2000 = 0.30
        assert result.iloc[0]["Effective Tax Rate"] == 1.0  # Clipped
        assert result.iloc[1]["Effective Tax Rate"] == 0.0  # Clipped
        assert abs(result.iloc[2]["Effective Tax Rate"] - 0.20) < 0.001
        assert abs(result.iloc[3]["Effective Tax Rate"] - 0.30) < 0.001

    def test_calculate_effective_tax_rate_multiple_companies(self):
        """Test effective tax rate calculation with multiple companies."""
        # Multiple tickers
        income_statement = pd.DataFrame({
            "ticker": ["VIC", "VIC", "REE", "REE"],
            "yearReport": [2022, 2023, 2022, 2023],
            "Profit before tax": [1000, 1200, 800, 900],
        })

        cash_flow = pd.DataFrame({
            "ticker": ["VIC", "VIC", "REE", "REE"],
            "yearReport": [2022, 2023, 2022, 2023],
            "Business Income Tax paid": [-200, -240, -160, -225],
            "Net Profit/Loss before tax": [1000, 1200, 800, 900],
        })

        result = calculate_effective_tax_rate(income_statement, cash_flow)

        # Verify structure
        assert not result.empty
        assert len(result) == 4
        assert set(result["ticker"].unique()) == {"VIC", "REE"}

        # Verify calculations for each company
        vic_data = result[result["ticker"] == "VIC"].sort_values("yearReport")
        ree_data = result[result["ticker"] == "REE"].sort_values("yearReport")

        # VIC: 2022: 200/1000=0.20, 2023: 240/1200=0.20
        assert abs(vic_data.iloc[0]["Effective Tax Rate"] - 0.20) < 0.001
        assert abs(vic_data.iloc[1]["Effective Tax Rate"] - 0.20) < 0.001

        # REE: 2022: 160/800=0.20, 2023: 225/900=0.25
        assert abs(ree_data.iloc[0]["Effective Tax Rate"] - 0.20) < 0.001
        assert abs(ree_data.iloc[1]["Effective Tax Rate"] - 0.25) < 0.001

    def test_calculate_effective_tax_rate_empty_dataframes(self):
        """Test effective tax rate calculation with empty dataframes."""
        income_statement = pd.DataFrame()
        cash_flow = pd.DataFrame()

        result = calculate_effective_tax_rate(income_statement, cash_flow)

        # Should return empty DataFrame
        assert result.empty

    def test_calculate_effective_tax_rate_no_matching_years(self):
        """Test effective tax rate calculation when years don't match between statements."""
        income_statement = pd.DataFrame({
            "ticker": ["VIC"],
            "yearReport": [2022],
            "Profit before tax": [1000],
        })

        cash_flow = pd.DataFrame({
            "ticker": ["VIC"],
            "yearReport": [2023],  # Different year
            "Business Income Tax paid": [-200],
            "Net Profit/Loss before tax": [1200],
        })

        result = calculate_effective_tax_rate(income_statement, cash_flow)

        # Should return empty DataFrame due to inner join with no matching years
        assert result.empty
