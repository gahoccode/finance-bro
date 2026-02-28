#!/usr/bin/env python3
"""
VnStock Data Validation Script

Manual validation script to test all vnstock company data functions with real API calls.
This script helps verify that the functions work correctly with actual data from the vnstock API.

Usage:
    python scripts/validate_vnstock_data.py

    # Or with custom symbol:
    python scripts/validate_vnstock_data.py --symbol REE
"""

import argparse
import pathlib
import sys
from datetime import datetime

import pandas as pd


# Add project root to Python path
project_root = pathlib.Path(
    pathlib.Path(pathlib.Path(__file__).resolve()).parent
).parent
sys.path.insert(0, project_root)

from src.services.vnstock_api import (
    get_company_reports,
    get_foreign_trading_data,
    get_insider_deals_data,
    get_management_data,
    get_ownership_data,
    get_subsidiaries_data,
)


class VnStockDataValidator:
    """Validator for vnstock company data functions."""

    def __init__(self, symbol="REE"):
        self.symbol = symbol
        self.results = {}
        self.errors = {}

    def validate_function(self, func_name, func, expected_columns=None):
        """Validate a single vnstock function."""
        print(f"\n{'=' * 60}")
        print(f"Testing {func_name} with symbol: {self.symbol}")
        print(f"{'=' * 60}")

        try:
            # Call the function
            start_time = datetime.now()
            data = func(self.symbol)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            # Basic validation
            if data is None:
                raise ValueError("Function returned None")

            if not isinstance(data, pd.DataFrame):
                raise ValueError(f"Expected DataFrame, got {type(data)}")

            # Store results
            self.results[func_name] = {
                "success": True,
                "data_shape": data.shape,
                "columns": list(data.columns),
                "duration_seconds": duration,
                "has_data": not data.empty,
            }

            # Display results
            print(f"✅ SUCCESS: {func_name}")
            print(f"   Duration: {duration:.2f} seconds")
            print(f"   Data shape: {data.shape}")
            print(f"   Has data: {'Yes' if not data.empty else 'No'}")

            if not data.empty:
                print(f"   Columns: {list(data.columns)}")

                # Check expected columns if provided
                if expected_columns:
                    missing_cols = set(expected_columns) - set(data.columns)
                    if missing_cols:
                        print(f"   ⚠️  Missing expected columns: {missing_cols}")
                    else:
                        print("   ✅ All expected columns present")

                # Show sample data
                print("\n   Sample data (first 3 rows):")
                print(data.head(3).to_string(index=False))
            else:
                print("   ℹ️  No data returned (empty DataFrame)")

        except Exception as e:
            # Store error
            self.errors[func_name] = str(e)
            self.results[func_name] = {
                "success": False,
                "error": str(e),
                "duration_seconds": 0,
                "has_data": False,
            }

            print(f"❌ ERROR: {func_name}")
            print(f"   Error: {str(e)}")

    def validate_all_functions(self):
        """Validate all company data functions."""
        print("🚀 Starting VnStock Data Validation")
        print(f"Symbol: {self.symbol}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Define functions and their expected columns
        functions_to_test = [
            (
                "get_ownership_data",
                get_ownership_data,
                ["share_holder", "quantity", "share_own_percent"],
            ),
            (
                "get_management_data",
                get_management_data,
                [
                    "officer_name",
                    "position_short_name",
                    "quantity",
                    "officer_own_percent",
                ],
            ),
            (
                "get_subsidiaries_data",
                get_subsidiaries_data,
                ["organ_name", "ownership_percent", "type"],
            ),
            (
                "get_insider_deals_data",
                get_insider_deals_data,
                ["deal_announce_date", "deal_action", "deal_quantity", "deal_price"],
            ),
            (
                "get_foreign_trading_data",
                get_foreign_trading_data,
                ["foreign_volume", "total_volume", "foreign_room"],
            ),
            (
                "get_company_reports",
                get_company_reports,
                ["date", "description", "link", "name"],
            ),
        ]

        # Test each function
        for func_name, func, expected_columns in functions_to_test:
            self.validate_function(func_name, func, expected_columns)

        # Generate summary report
        self.generate_summary_report()

    def validate_reports_date_sorting(self):
        """Special validation for company reports date sorting."""
        print(f"\n{'=' * 60}")
        print("Special Test: Company Reports Date Sorting")
        print(f"{'=' * 60}")

        try:
            reports = get_company_reports(self.symbol)

            if not reports.empty and "date" in reports.columns:
                dates = reports["date"].tolist()
                is_sorted_desc = dates == sorted(dates, reverse=True)

                print("✅ Date sorting test:")
                print(f"   Total reports: {len(reports)}")
                print(f"   Date column type: {reports['date'].dtype}")
                print(f"   Sorted descending: {'Yes' if is_sorted_desc else 'No'}")

                if len(reports) >= 2:
                    print(f"   Newest date: {dates[0]}")
                    print(f"   Oldest date: {dates[-1]}")

                return is_sorted_desc
            else:
                print("   ⚠️  No reports data or missing date column")
                return None

        except Exception as e:
            print(f"❌ Date sorting test failed: {str(e)}")
            return False

    def generate_summary_report(self):
        """Generate summary validation report."""
        print(f"\n{'=' * 60}")
        print("VALIDATION SUMMARY REPORT")
        print(f"{'=' * 60}")

        successful_functions = [
            name
            for name, result in self.results.items()
            if result.get("success", False)
        ]
        failed_functions = [
            name
            for name, result in self.results.items()
            if not result.get("success", False)
        ]
        functions_with_data = [
            name
            for name, result in self.results.items()
            if result.get("has_data", False)
        ]

        print(f"Symbol tested: {self.symbol}")
        print(f"Total functions tested: {len(self.results)}")
        print(f"✅ Successful: {len(successful_functions)}")
        print(f"❌ Failed: {len(failed_functions)}")
        print(f"📊 Functions with data: {len(functions_with_data)}")

        if successful_functions:
            print("\n✅ Successful functions:")
            for func_name in successful_functions:
                result = self.results[func_name]
                data_info = (
                    f"({result['data_shape'][0]} rows)"
                    if result.get("has_data")
                    else "(no data)"
                )
                duration = result.get("duration_seconds", 0)
                print(f"   - {func_name} {data_info} - {duration:.2f}s")

        if failed_functions:
            print("\n❌ Failed functions:")
            for func_name in failed_functions:
                error = self.results[func_name].get("error", "Unknown error")
                print(f"   - {func_name}: {error}")

        # Performance summary
        total_duration = sum(
            r.get("duration_seconds", 0) for r in self.results.values()
        )
        print(f"\n⏱️  Total execution time: {total_duration:.2f} seconds")

        # Special validations
        print("\n🔍 Special Validations:")
        date_sorting_result = self.validate_reports_date_sorting()
        if date_sorting_result is True:
            print("   ✅ Company reports date sorting: PASSED")
        elif date_sorting_result is False:
            print("   ❌ Company reports date sorting: FAILED")
        else:
            print("   ⚠️  Company reports date sorting: NOT TESTABLE")

        # Overall status
        overall_success = len(failed_functions) == 0
        status_icon = "✅" if overall_success else "⚠️"
        print(
            f"\n{status_icon} Overall Status: {'PASSED' if overall_success else 'PARTIAL SUCCESS'}"
        )

        return overall_success


def main():
    """Main function to run validation."""
    parser = argparse.ArgumentParser(
        description="Validate VnStock company data functions"
    )
    parser.add_argument(
        "--symbol", default="REE", help="Stock symbol to test (default: REE)"
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    # Create validator and run tests
    validator = VnStockDataValidator(symbol=args.symbol)
    success = validator.validate_all_functions()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
