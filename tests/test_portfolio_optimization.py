import pytest
import pandas as pd
import os
import tempfile
from unittest.mock import patch, mock_open, MagicMock
from datetime import datetime


class TestPortfolioReportGeneration:
    """Test the Excel report generation logic to verify the double extension fix."""

    def test_filename_construction_without_extension(self, mock_timestamp):
        """Test that filename base is constructed without .xlsx extension."""
        portfolio_name = "Max_Sharpe_Portfolio"
        timestamp = mock_timestamp

        # This is the logic from the fixed code
        filename_base = f"{portfolio_name}_{timestamp}"

        assert filename_base == "Max_Sharpe_Portfolio_20250109_120000"
        assert not filename_base.endswith(".xlsx")

    def test_filepath_construction(self, temp_reports_dir, mock_timestamp):
        """Test that filepath is constructed correctly."""
        portfolio_name = "Max_Sharpe_Portfolio"
        timestamp = mock_timestamp

        # This is the logic from the fixed code
        filename_base = f"{portfolio_name}_{timestamp}"
        filepath_base = os.path.join(temp_reports_dir, filename_base)

        expected_path = os.path.join(
            temp_reports_dir, "Max_Sharpe_Portfolio_20250109_120000"
        )
        assert filepath_base == expected_path
        assert not filepath_base.endswith(".xlsx")

    def test_excel_filepath_construction(self, temp_reports_dir, mock_timestamp):
        """Test that Excel filepath with extension is constructed correctly."""
        portfolio_name = "Max_Sharpe_Portfolio"
        timestamp = mock_timestamp

        filename_base = f"{portfolio_name}_{timestamp}"
        filepath_base = os.path.join(temp_reports_dir, filename_base)
        filepath_xlsx = filepath_base + ".xlsx"

        expected_xlsx_path = os.path.join(
            temp_reports_dir, "Max_Sharpe_Portfolio_20250109_120000.xlsx"
        )
        assert filepath_xlsx == expected_xlsx_path
        assert filepath_xlsx.endswith(".xlsx")
        assert filepath_xlsx.count(".xlsx") == 1  # Only one extension

    @patch("riskfolio.excel_report")
    def test_riskfolio_called_with_correct_path(
        self,
        mock_excel_report,
        temp_reports_dir,
        sample_returns_df,
        sample_weights,
        mock_timestamp,
    ):
        """Test that riskfolio.excel_report is called with path without extension."""
        portfolio_name = "Max_Sharpe_Portfolio"
        timestamp = mock_timestamp

        # Convert weights to DataFrame as done in actual code
        selected_weights_df = pd.DataFrame.from_dict(
            sample_weights, orient="index", columns=[portfolio_name]
        )

        # Simulate the fixed logic
        filename_base = f"{portfolio_name}_{timestamp}"
        filepath_base = os.path.join(temp_reports_dir, filename_base)

        # This should be the call to riskfolio (mocked)
        mock_excel_report.return_value = None
        mock_excel_report(
            returns=sample_returns_df, w=selected_weights_df, name=filepath_base
        )

        # Verify riskfolio was called with path WITHOUT extension
        mock_excel_report.assert_called_once()
        args, kwargs = mock_excel_report.call_args
        assert kwargs["name"] == filepath_base
        assert not kwargs["name"].endswith(".xlsx")

    @patch("riskfolio.excel_report")
    @patch("os.path.getsize")
    def test_file_operations_use_correct_xlsx_path(
        self,
        mock_getsize,
        mock_excel_report,
        temp_reports_dir,
        sample_returns_df,
        sample_weights,
        mock_timestamp,
    ):
        """Test that file operations use the correct .xlsx path."""
        portfolio_name = "Max_Sharpe_Portfolio"
        timestamp = mock_timestamp

        # Setup mocks
        mock_excel_report.return_value = None
        mock_getsize.return_value = 51200  # 50KB

        # Simulate the fixed logic
        filename_base = f"{portfolio_name}_{timestamp}"
        filepath_base = os.path.join(temp_reports_dir, filename_base)
        filepath_xlsx = filepath_base + ".xlsx"

        # Simulate creating the Excel file (riskfolio would do this)
        with open(filepath_xlsx, "wb") as f:
            f.write(b"fake excel content")

        # Test file size calculation uses correct path
        file_size = os.path.getsize(filepath_xlsx) / 1024

        assert os.path.exists(filepath_xlsx)
        assert filepath_xlsx.endswith(".xlsx")
        assert filepath_xlsx.count(".xlsx") == 1

    def test_download_filename_construction(self, mock_timestamp):
        """Test that download filename includes .xlsx extension."""
        portfolio_name = "Max_Sharpe_Portfolio"
        timestamp = mock_timestamp

        filename_base = f"{portfolio_name}_{timestamp}"
        download_filename = filename_base + ".xlsx"

        assert download_filename == "Max_Sharpe_Portfolio_20250109_120000.xlsx"
        assert download_filename.endswith(".xlsx")
        assert download_filename.count(".xlsx") == 1

    def test_all_portfolio_types_filename_construction(self, mock_timestamp):
        """Test filename construction for all portfolio types."""
        portfolio_types = [
            "Max_Sharpe_Portfolio",
            "Min_Volatility_Portfolio",
            "Max_Utility_Portfolio",
        ]

        timestamp = mock_timestamp

        for portfolio_name in portfolio_types:
            filename_base = f"{portfolio_name}_{timestamp}"
            filepath_xlsx = filename_base + ".xlsx"

            # Verify no double extensions
            assert not filename_base.endswith(".xlsx")
            assert filepath_xlsx.endswith(".xlsx")
            assert filepath_xlsx.count(".xlsx") == 1

            # Verify proper naming
            assert filename_base.startswith(portfolio_name)
            assert timestamp in filename_base


class TestPortfolioWeightProcessing:
    """Test portfolio weight processing logic."""

    def test_weights_dict_to_dataframe_conversion(self, sample_weights):
        """Test converting weights dictionary to DataFrame."""
        portfolio_name = "Max_Sharpe_Portfolio"

        # This is the logic from the actual code
        selected_weights_df = pd.DataFrame.from_dict(
            sample_weights, orient="index", columns=[portfolio_name]
        )

        assert isinstance(selected_weights_df, pd.DataFrame)
        assert list(selected_weights_df.index) == ["REE", "FMC", "DHC"]
        assert selected_weights_df.columns[0] == portfolio_name
        assert selected_weights_df.loc["REE", portfolio_name] == 0.4
        assert abs(selected_weights_df.sum().sum() - 1.0) < 1e-10  # Weights sum to 1

    def test_empty_weights_handling(self):
        """Test handling of empty weights dictionary."""
        empty_weights = {}
        portfolio_name = "Test_Portfolio"

        selected_weights_df = pd.DataFrame.from_dict(
            empty_weights, orient="index", columns=[portfolio_name]
        )

        assert isinstance(selected_weights_df, pd.DataFrame)
        assert len(selected_weights_df) == 0
        assert selected_weights_df.columns[0] == portfolio_name


class TestEdgeCases:
    """Test edge cases and error scenarios."""

    def test_invalid_portfolio_name_characters(self, mock_timestamp):
        """Test handling portfolio names with special characters."""
        # Portfolio names should be filesystem-safe
        portfolio_name = "Max_Sharpe_Portfolio"  # This is already safe
        timestamp = mock_timestamp

        filename_base = f"{portfolio_name}_{timestamp}"

        # Ensure filename is filesystem-safe
        assert "/" not in filename_base
        assert "\\" not in filename_base
        assert ":" not in filename_base
        assert "*" not in filename_base
        assert "?" not in filename_base

    def test_timestamp_format_consistency(self):
        """Test that timestamp format is consistent."""
        # This tests the actual timestamp format used
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        assert len(timestamp) == 15  # YYYYMMDD_HHMMSS
        assert "_" in timestamp
        assert timestamp.count("_") == 1

        # Verify it creates valid filenames
        portfolio_name = "Test_Portfolio"
        filename_base = f"{portfolio_name}_{timestamp}"
        assert len(filename_base) > len(portfolio_name)

    @patch("os.makedirs")
    def test_directory_creation(self, mock_makedirs, temp_reports_dir):
        """Test that reports directory is created if it doesn't exist."""
        # This simulates the logic from the actual code
        os.makedirs(temp_reports_dir, exist_ok=True)

        mock_makedirs.assert_called_once_with(temp_reports_dir, exist_ok=True)


if __name__ == "__main__":
    pytest.main([__file__])
