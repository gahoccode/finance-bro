"""
Comprehensive tests for financial formatting functionality.

Tests the flexible financial formatting system including:
- Helper functions in src/services/data_service.py
- Configuration constants in src/core/config.py  
- Reusable UI components in src/components/ui_components.py
"""

import pandas as pd
import pytest

from src.core.config import FINANCIAL_DISPLAY_OPTIONS, DEFAULT_FINANCIAL_DISPLAY
from src.services.data_service import format_financial_display, convert_dataframe_for_display


class TestFormatFinancialDisplay:
    """Test cases for format_financial_display function."""

    def test_format_billions_with_zero_decimals(self):
        """Test billions formatting with zero decimal places."""
        result = format_financial_display(1500000000, "billions", 0)
        assert result == "2B VND"

    def test_format_billions_with_decimals(self):
        """Test billions formatting with decimal places."""
        result = format_financial_display(1500000000, "billions", 1)
        assert result == "1.5B VND"

    def test_format_millions_with_zero_decimals(self):
        """Test millions formatting with zero decimal places."""
        result = format_financial_display(1500000000, "millions", 0)
        assert result == "1,500M VND"

    def test_format_millions_with_decimals(self):
        """Test millions formatting with decimal places."""
        result = format_financial_display(1500000000, "millions", 1)
        assert result == "1,500.0M VND"

    def test_format_original_scale(self):
        """Test original scale formatting."""
        result = format_financial_display(1500000000, "original", 0)
        assert result == "1,500,000,000 VND"

    def test_format_original_scale_with_decimals(self):
        """Test original scale formatting with decimals."""
        result = format_financial_display(1500000.75, "original", 2)
        assert result == "1,500,000.75 VND"

    def test_format_small_numbers_billions(self):
        """Test formatting small numbers in billions."""
        result = format_financial_display(500000000, "billions", 2)
        assert result == "0.50B VND"

    def test_format_small_numbers_millions(self):
        """Test formatting small numbers in millions."""
        result = format_financial_display(500000, "millions", 1)
        assert result == "0.5M VND"

    def test_format_negative_numbers(self):
        """Test formatting negative numbers."""
        result = format_financial_display(-1500000000, "billions", 1)
        assert result == "-1.5B VND"

    def test_format_zero_value(self):
        """Test formatting zero values."""
        result = format_financial_display(0, "billions", 0)
        assert result == "0B VND"

    def test_format_none_value(self):
        """Test handling None values."""
        result = format_financial_display(None, "billions", 0)
        assert result == "N/A"

    def test_format_invalid_value_string(self):
        """Test handling invalid string values."""
        result = format_financial_display("invalid", "billions", 0)
        assert result == "N/A"

    def test_format_invalid_unit_defaults_to_original(self):
        """Test invalid display unit defaults to original scale."""
        result = format_financial_display(1500000000, "invalid_unit", 0)
        assert result == "1,500,000,000 VND"

    def test_format_pd_nan_value(self):
        """Test handling pandas NaN values."""
        result = format_financial_display(pd.NA, "billions", 0)
        assert result == "N/A"


class TestConvertDataframeForDisplay:
    """Test cases for convert_dataframe_for_display function."""

    def setup_method(self):
        """Set up test dataframe for each test."""
        self.test_df = pd.DataFrame({
            'Symbol': ['REE', 'VIC', 'VNM'],
            'Long-term borrowings (Bn. VND)': [1500000000, 2500000000, 800000000],
            'Short-term borrowings (Bn. VND)': [500000000, 750000000, 200000000],
            'Capital Employed (Bn. VND)': [2000000000, 3250000000, 1000000000],
            'Year': [2024, 2024, 2024]
        })

    def test_convert_single_column_billions(self):
        """Test converting single column to billions display."""
        columns_to_format = ['Long-term borrowings (Bn. VND)']
        result = convert_dataframe_for_display(
            self.test_df, columns_to_format, "billions", 1
        )

        expected_values = ["1.5", "2.5", "0.8"]
        assert result['Long-term borrowings (Bn. VND)'].tolist() == expected_values

    def test_convert_multiple_columns_millions(self):
        """Test converting multiple columns to millions display."""
        columns_to_format = [
            'Long-term borrowings (Bn. VND)',
            'Short-term borrowings (Bn. VND)'
        ]
        result = convert_dataframe_for_display(
            self.test_df, columns_to_format, "millions", 0
        )

        assert result['Long-term borrowings (Bn. VND)'].iloc[0] == "1,500"
        assert result['Short-term borrowings (Bn. VND)'].iloc[0] == "500"

    def test_convert_original_scale_with_commas(self):
        """Test converting to original scale with comma separators."""
        columns_to_format = ['Capital Employed (Bn. VND)']
        result = convert_dataframe_for_display(
            self.test_df, columns_to_format, "original", 1
        )

        expected_values = ["2,000,000,000.0", "3,250,000,000.0", "1,000,000,000.0"]
        assert result['Capital Employed (Bn. VND)'].tolist() == expected_values

    def test_convert_preserves_original_dataframe(self):
        """Test that original dataframe is not modified."""
        original_values = self.test_df['Long-term borrowings (Bn. VND)'].copy()
        columns_to_format = ['Long-term borrowings (Bn. VND)']

        convert_dataframe_for_display(
            self.test_df, columns_to_format, "billions", 1
        )

        # Original dataframe should be unchanged
        pd.testing.assert_series_equal(
            self.test_df['Long-term borrowings (Bn. VND)'],
            original_values
        )

    def test_convert_nonexistent_column_ignored(self):
        """Test that non-existent columns are ignored gracefully."""
        columns_to_format = ['Nonexistent Column', 'Long-term borrowings (Bn. VND)']
        result = convert_dataframe_for_display(
            self.test_df, columns_to_format, "billions", 1
        )

        # Should process existing column, ignore non-existent one
        assert result['Long-term borrowings (Bn. VND)'].iloc[0] == "1.5"

    def test_convert_empty_dataframe(self):
        """Test handling empty dataframes."""
        empty_df = pd.DataFrame()
        result = convert_dataframe_for_display(empty_df, [], "billions", 1)
        assert result.empty

    def test_convert_none_dataframe(self):
        """Test handling None dataframe."""
        result = convert_dataframe_for_display(None, [], "billions", 1)
        assert result is None

    def test_convert_with_nan_values(self):
        """Test handling dataframes with NaN values."""
        df_with_nan = self.test_df.copy()
        df_with_nan.iloc[0, df_with_nan.columns.get_loc('Long-term borrowings (Bn. VND)')] = pd.NA

        columns_to_format = ['Long-term borrowings (Bn. VND)']
        result = convert_dataframe_for_display(
            df_with_nan, columns_to_format, "billions", 1
        )

        assert result['Long-term borrowings (Bn. VND)'].iloc[0] == "N/A"
        assert result['Long-term borrowings (Bn. VND)'].iloc[1] == "2.5"

    def test_convert_all_columns_formatted(self):
        """Test converting all financial columns at once."""
        financial_columns = [
            'Long-term borrowings (Bn. VND)',
            'Short-term borrowings (Bn. VND)',
            'Capital Employed (Bn. VND)'
        ]
        result = convert_dataframe_for_display(
            self.test_df, financial_columns, "billions", 2
        )

        # Check that all financial columns are formatted as strings
        for column in financial_columns:
            assert all(isinstance(x, str) for x in result[column])

        # Non-financial columns should remain unchanged
        assert result['Symbol'].iloc[0] == 'REE'
        assert result['Year'].iloc[0] == 2024

    def test_convert_edge_case_zero_values(self):
        """Test conversion with zero values."""
        df_with_zeros = self.test_df.copy()
        df_with_zeros.iloc[0, df_with_zeros.columns.get_loc('Long-term borrowings (Bn. VND)')] = 0

        columns_to_format = ['Long-term borrowings (Bn. VND)']
        result = convert_dataframe_for_display(
            df_with_zeros, columns_to_format, "billions", 1
        )

        assert result['Long-term borrowings (Bn. VND)'].iloc[0] == "0.0"


class TestFinancialDisplayConfiguration:
    """Test cases for financial display configuration constants."""

    def test_financial_display_options_structure(self):
        """Test that FINANCIAL_DISPLAY_OPTIONS has correct structure."""
        required_keys = ["BILLIONS", "MILLIONS", "ORIGINAL"]

        # Check all required top-level keys exist
        for key in required_keys:
            assert key in FINANCIAL_DISPLAY_OPTIONS

        # Check each option has required sub-keys
        required_sub_keys = ["key", "label", "divisor", "suffix"]
        for option in FINANCIAL_DISPLAY_OPTIONS.values():
            for sub_key in required_sub_keys:
                assert sub_key in option

    def test_billions_configuration(self):
        """Test billions configuration values."""
        billions_config = FINANCIAL_DISPLAY_OPTIONS["BILLIONS"]

        assert billions_config["key"] == "billions"
        assert billions_config["divisor"] == 1_000_000_000
        assert "B VND" in billions_config["suffix"]

    def test_millions_configuration(self):
        """Test millions configuration values."""
        millions_config = FINANCIAL_DISPLAY_OPTIONS["MILLIONS"]

        assert millions_config["key"] == "millions"
        assert millions_config["divisor"] == 1_000_000
        assert "M VND" in millions_config["suffix"]

    def test_original_configuration(self):
        """Test original scale configuration values."""
        original_config = FINANCIAL_DISPLAY_OPTIONS["ORIGINAL"]

        assert original_config["key"] == "original"
        assert original_config["divisor"] == 1
        assert "VND" in original_config["suffix"]

    def test_default_financial_display_structure(self):
        """Test DEFAULT_FINANCIAL_DISPLAY has correct structure."""
        required_keys = ["unit", "decimal_places", "session_key"]

        for key in required_keys:
            assert key in DEFAULT_FINANCIAL_DISPLAY

    def test_default_configuration_consistency(self):
        """Test that default configuration values are consistent with options."""
        default_unit = DEFAULT_FINANCIAL_DISPLAY["unit"]

        # Default unit should exist in one of the option keys
        valid_units = [opt["key"] for opt in FINANCIAL_DISPLAY_OPTIONS.values()]
        assert default_unit in valid_units


class TestFinancialFormattingIntegration:
    """Integration tests combining helper functions and configuration."""

    def setup_method(self):
        """Set up integration test data."""
        self.sample_data = pd.DataFrame({
            'Company': ['REE Corp', 'VIC Group', 'VNM Ltd'],
            'Revenue (Bn. VND)': [50000000000, 75000000000, 25000000000],
            'Assets (Bn. VND)': [100000000000, 150000000000, 60000000000],
            'Year': [2024, 2024, 2024]
        })

    def test_full_workflow_billions(self):
        """Test complete workflow using billions format."""
        # Test individual value formatting
        revenue_formatted = format_financial_display(
            self.sample_data.iloc[0]['Revenue (Bn. VND)'],
            "billions",
            1
        )
        assert revenue_formatted == "50.0B VND"

        # Test dataframe conversion
        financial_columns = ['Revenue (Bn. VND)', 'Assets (Bn. VND)']
        display_df = convert_dataframe_for_display(
            self.sample_data, financial_columns, "billions", 0
        )

        assert display_df['Revenue (Bn. VND)'].iloc[0] == "50"
        assert display_df['Assets (Bn. VND)'].iloc[0] == "100"

        # Non-financial columns preserved
        assert display_df['Company'].iloc[0] == 'REE Corp'

    def test_full_workflow_millions(self):
        """Test complete workflow using millions format."""
        # Test dataframe conversion to millions
        financial_columns = ['Revenue (Bn. VND)', 'Assets (Bn. VND)']
        display_df = convert_dataframe_for_display(
            self.sample_data, financial_columns, "millions", 0
        )

        assert display_df['Revenue (Bn. VND)'].iloc[0] == "50,000"
        assert display_df['Assets (Bn. VND)'].iloc[0] == "100,000"

    def test_mixed_format_requirements(self):
        """Test handling mixed formatting requirements."""
        # Some metrics in billions, some in original scale
        revenue_billions = format_financial_display(
            self.sample_data.iloc[0]['Revenue (Bn. VND)'],
            "billions", 2
        )

        revenue_original = format_financial_display(
            self.sample_data.iloc[0]['Revenue (Bn. VND)'],
            "original", 0
        )

        assert revenue_billions == "50.00B VND"
        assert revenue_original == "50,000,000,000 VND"

    def test_configuration_driven_formatting(self):
        """Test that formatting uses configuration constants correctly."""
        # Use configuration constants to format
        for config_key, config_value in FINANCIAL_DISPLAY_OPTIONS.items():
            unit_key = config_value["key"]

            result = format_financial_display(
                1000000000,  # 1 billion VND
                unit_key,
                1
            )

            if unit_key == "billions":
                assert result == "1.0B VND"
            elif unit_key == "millions":
                assert result == "1,000.0M VND"
            elif unit_key == "original":
                assert result == "1,000,000,000.0 VND"


class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error handling scenarios."""

    def test_very_large_numbers(self):
        """Test formatting very large numbers."""
        very_large = 1e15  # 1 quadrillion
        result = format_financial_display(very_large, "billions", 0)
        assert result == "1,000,000B VND"

    def test_very_small_numbers(self):
        """Test formatting very small numbers."""
        very_small = 1  # 1 VND
        result = format_financial_display(very_small, "billions", 3)
        assert result == "0.000B VND"

    def test_scientific_notation_input(self):
        """Test handling scientific notation input."""
        scientific = 1.5e9  # 1.5 billion
        result = format_financial_display(scientific, "billions", 1)
        assert result == "1.5B VND"

    def test_string_numeric_input(self):
        """Test handling string numeric input."""
        string_number = "1500000000"
        result = format_financial_display(string_number, "billions", 1)
        # Should convert string to float successfully
        assert result == "1.5B VND"

    def test_dataframe_with_mixed_types(self):
        """Test dataframe conversion with mixed column types."""
        mixed_df = pd.DataFrame({
            'Company': ['REE', 'VIC'],
            'Revenue': [1.5e9, 2.5e9],  # Scientific notation
            'Revenue_Str': ['1500000000', '2500000000'],  # String numbers
            'Invalid': ['N/A', None],  # Invalid values
            'Year': [2024, 2024]
        })

        result = convert_dataframe_for_display(
            mixed_df, ['Revenue', 'Revenue_Str'], "billions", 1
        )

        assert result['Revenue'].iloc[0] == "1.5"
        assert result['Revenue_Str'].iloc[0] == "1.5"

    def test_empty_columns_list(self):
        """Test conversion with empty columns list."""
        df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
        result = convert_dataframe_for_display(df, [], "billions", 1)

        # Should return unchanged dataframe
        pd.testing.assert_frame_equal(result, df)

    def test_all_invalid_values_column(self):
        """Test handling column with all invalid values."""
        invalid_df = pd.DataFrame({
            'Valid': [1000000000, 2000000000],
            'Invalid': ['N/A', None]
        })

        result = convert_dataframe_for_display(
            invalid_df, ['Invalid'], "billions", 1
        )

        assert all(x == "N/A" for x in result['Invalid'])


if __name__ == "__main__":
    # Run tests if script executed directly
    pytest.main([__file__, "-v"])
