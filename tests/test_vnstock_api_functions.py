"""
Test VnStock API Company Functions

Comprehensive tests for all company data fetching functions in src/services/vnstock_api.py
to ensure reliability and data consistency for Company_Overview.py page.
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock

from src.services.vnstock_api import (
    get_ownership_data,
    get_management_data,
    get_subsidiaries_data,
    get_insider_deals_data,
    get_foreign_trading_data,
    get_company_reports,
)


class TestVnStockCompanyFunctions:
    """Test all vnstock company data functions for reliability and data consistency."""

    def test_get_ownership_data_success(self, mock_ownership_data):
        """Test successful ownership data retrieval with proper structure."""
        with patch("src.services.vnstock_api.Vnstock") as mock_vnstock:
            # Setup mock
            mock_stock = MagicMock()
            mock_company = MagicMock()
            mock_company.shareholders.return_value = mock_ownership_data
            mock_stock.company = mock_company
            mock_vnstock.return_value.stock.return_value = mock_stock

            # Test function
            result = get_ownership_data("REE")

            # Assertions
            assert not result.empty
            assert "share_holder" in result.columns
            assert "quantity" in result.columns
            assert "share_own_percent" in result.columns
            assert len(result) == 3  # Based on mock data

    def test_get_ownership_data_empty_response(self):
        """Test ownership data function with empty API response."""
        with patch("src.services.vnstock_api.Vnstock") as mock_vnstock:
            # Setup mock to return empty DataFrame
            mock_stock = MagicMock()
            mock_company = MagicMock()
            mock_company.shareholders.return_value = pd.DataFrame()
            mock_stock.company = mock_company
            mock_vnstock.return_value.stock.return_value = mock_stock

            # Test function
            result = get_ownership_data("INVALID")

            # Assertions
            assert result.empty
            assert isinstance(result, pd.DataFrame)

    @patch("src.services.vnstock_api.st.cache_data.clear")
    @patch("src.services.vnstock_api.st.error")
    def test_get_ownership_data_api_error(self, mock_error, mock_cache_clear):
        """Test ownership data function handles API errors gracefully."""
        with patch("src.services.vnstock_api.Vnstock") as mock_vnstock:
            # Setup mock to raise exception
            mock_vnstock.return_value.stock.side_effect = Exception("API Error")

            # Clear cache to ensure fresh test
            mock_cache_clear()

            # Test function with unique symbol to avoid cache
            result = get_ownership_data("ERROR_TEST_SYMBOL")

            # Assertions
            assert result.empty
            mock_error.assert_called_once()

    def test_get_management_data_success(self, mock_management_data):
        """Test successful management data retrieval."""
        with patch("src.services.vnstock_api.Company") as mock_company_class:
            # Setup mock
            mock_company = MagicMock()
            mock_company.officers.return_value = mock_management_data
            mock_company_class.return_value = mock_company

            # Test function
            result = get_management_data("REE")

            # Assertions
            assert not result.empty
            assert "officer_name" in result.columns
            assert "position_short_name" in result.columns
            assert "quantity" in result.columns
            assert "officer_own_percent" in result.columns

    def test_get_subsidiaries_data_success(self, mock_subsidiaries_data):
        """Test successful subsidiaries data retrieval."""
        with patch("src.services.vnstock_api.Company") as mock_company_class:
            # Setup mock
            mock_company = MagicMock()
            mock_company.subsidiaries.return_value = mock_subsidiaries_data
            mock_company_class.return_value = mock_company

            # Test function
            result = get_subsidiaries_data("REE")

            # Assertions
            assert not result.empty
            assert "organ_name" in result.columns
            assert "ownership_percent" in result.columns
            assert "type" in result.columns

    def test_get_insider_deals_data_success(self, mock_insider_deals_data):
        """Test successful insider deals data retrieval."""
        with patch("src.services.vnstock_api.Vnstock") as mock_vnstock:
            # Setup mock
            mock_stock = MagicMock()
            mock_company = MagicMock()
            mock_company.insider_deals.return_value = mock_insider_deals_data
            mock_stock.company = mock_company
            mock_vnstock.return_value.stock.return_value = mock_stock

            # Test function
            result = get_insider_deals_data("REE")

            # Assertions
            assert not result.empty
            assert "deal_announce_date" in result.columns
            assert "deal_action" in result.columns
            assert "deal_quantity" in result.columns
            assert "deal_price" in result.columns

    def test_get_foreign_trading_data_success(self, mock_foreign_trading_data):
        """Test successful foreign trading data retrieval."""
        with patch("src.services.vnstock_api.Company") as mock_company_class:
            # Setup mock
            mock_company = MagicMock()
            mock_company.trading_stats.return_value = mock_foreign_trading_data
            mock_company_class.return_value = mock_company

            # Test function
            result = get_foreign_trading_data("REE")

            # Assertions
            assert not result.empty
            assert "foreign_volume" in result.columns
            assert "total_volume" in result.columns
            assert "foreign_room" in result.columns

    def test_get_company_reports_success(self, mock_company_reports_data):
        """Test successful company reports retrieval with proper date sorting."""
        with patch("src.services.vnstock_api.Company") as mock_company_class:
            # Setup mock
            mock_company = MagicMock()
            mock_company.reports.return_value = mock_company_reports_data
            mock_company_class.return_value = mock_company

            # Test function
            result = get_company_reports("REE")

            # Assertions
            assert not result.empty
            assert "date" in result.columns
            assert "description" in result.columns
            assert "link" in result.columns
            assert "name" in result.columns

            # Verify date conversion and sorting
            assert pd.api.types.is_datetime64_any_dtype(result["date"])
            # Check if sorted by date descending (newest first)
            dates = result["date"].tolist()
            assert dates == sorted(dates, reverse=True)

    def test_get_company_reports_empty_response(self):
        """Test company reports function with empty API response."""
        with patch("src.services.vnstock_api.Company") as mock_company_class:
            # Setup mock to return empty DataFrame
            mock_company = MagicMock()
            mock_company.reports.return_value = pd.DataFrame()
            mock_company_class.return_value = mock_company

            # Test function
            result = get_company_reports("INVALID")

            # Assertions
            assert result.empty
            assert isinstance(result, pd.DataFrame)

    def test_get_company_reports_date_processing(self):
        """Test company reports date conversion and sorting logic."""
        # Create mock data with unsorted dates
        mock_data = pd.DataFrame(
            {
                "date": ["2024-01-15", "2024-01-20", "2024-01-10"],
                "description": ["Report 1", "Report 2", "Report 3"],
                "link": ["link1", "link2", "link3"],
                "name": ["News 1", "News 2", "News 3"],
            }
        )

        with patch("src.services.vnstock_api.Company") as mock_company_class:
            # Setup mock
            mock_company = MagicMock()
            mock_company.reports.return_value = mock_data
            mock_company_class.return_value = mock_company

            # Test function
            result = get_company_reports("REE")

            # Assertions
            assert pd.api.types.is_datetime64_any_dtype(result["date"])
            # Verify sorting (newest first)
            expected_order = ["2024-01-20", "2024-01-15", "2024-01-10"]
            actual_dates = result["date"].dt.strftime("%Y-%m-%d").tolist()
            assert actual_dates == expected_order

    @patch("src.services.vnstock_api.st.error")
    def test_all_functions_error_handling(self, mock_error):
        """Test that all functions handle exceptions gracefully."""
        functions_to_test = [
            get_ownership_data,
            get_management_data,
            get_subsidiaries_data,
            get_insider_deals_data,
            get_foreign_trading_data,
            get_company_reports,
        ]

        for func in functions_to_test:
            # Reset mock
            mock_error.reset_mock()

            # Test with exception-raising mock
            with (
                patch("src.services.vnstock_api.Company") as mock_company_class,
                patch("src.services.vnstock_api.Vnstock") as mock_vnstock,
            ):
                mock_company_class.side_effect = Exception("Test error")
                mock_vnstock.side_effect = Exception("Test error")

                # Test function
                result = func("TEST")

                # Assertions
                assert result.empty
                assert isinstance(result, pd.DataFrame)
                mock_error.assert_called_once()

    def test_caching_decorators_present(self):
        """Test that all functions have caching decorators."""
        functions_to_check = [
            get_ownership_data,
            get_management_data,
            get_subsidiaries_data,
            get_insider_deals_data,
            get_foreign_trading_data,
            get_company_reports,
        ]

        for func in functions_to_check:
            # Check if function has been decorated with cache
            assert hasattr(
                func, "__wrapped__"
            ), f"{func.__name__} should have caching decorator"

    @pytest.mark.parametrize("symbol", ["TEST_REE", "TEST_FMC", "TEST_DHC"])
    def test_functions_with_multiple_symbols(self, symbol, mock_ownership_data):
        """Test functions work with different stock symbols."""
        with patch("src.services.vnstock_api.Vnstock") as mock_vnstock:
            # Setup mock
            mock_stock = MagicMock()
            mock_company = MagicMock()
            mock_company.shareholders.return_value = mock_ownership_data
            mock_stock.company = mock_company
            mock_vnstock.return_value.stock.return_value = mock_stock

            # Test function with unique symbols to avoid cache interference
            result = get_ownership_data(symbol)

            # Assertions
            assert not result.empty
            assert isinstance(result, pd.DataFrame)
            mock_vnstock.assert_called()


class TestVnStockDataConsistency:
    """Test data consistency and structure validation across all functions."""

    def test_ownership_data_structure_consistency(self, mock_ownership_data):
        """Test that ownership data maintains consistent structure."""
        with patch("src.services.vnstock_api.Vnstock") as mock_vnstock:
            # Setup mock
            mock_stock = MagicMock()
            mock_company = MagicMock()
            mock_company.shareholders.return_value = mock_ownership_data
            mock_stock.company = mock_company
            mock_vnstock.return_value.stock.return_value = mock_stock

            result = get_ownership_data("REE")

            # Check required columns
            required_columns = ["share_holder", "quantity", "share_own_percent"]
            for col in required_columns:
                assert col in result.columns, f"Missing required column: {col}"

            # Check data types
            assert result["quantity"].dtype in [np.int64, np.float64]
            assert result["share_own_percent"].dtype in [np.float64]

    def test_reports_data_structure_consistency(self, mock_company_reports_data):
        """Test that company reports maintain consistent structure."""
        with patch("src.services.vnstock_api.Company") as mock_company_class:
            mock_company = MagicMock()
            mock_company.reports.return_value = mock_company_reports_data
            mock_company_class.return_value = mock_company

            result = get_company_reports("REE")

            # Check required columns
            required_columns = ["date", "description", "link", "name"]
            for col in required_columns:
                assert col in result.columns, f"Missing required column: {col}"

            # Check data types
            assert pd.api.types.is_datetime64_any_dtype(result["date"])
            assert result["description"].dtype == object
            assert result["link"].dtype == object
            assert result["name"].dtype == object
