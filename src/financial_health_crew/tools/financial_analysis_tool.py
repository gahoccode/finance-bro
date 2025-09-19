from typing import Dict, List, Type

import pandas as pd
import streamlit as st
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class FinancialAnalysisToolInput(BaseModel):
    """Input schema for FinancialAnalysisTool."""

    analysis_type: str = Field(
        default="overview",
        description="Type of analysis to perform: 'overview', 'ratios', or 'trends'",
    )


class FinancialAnalysisTool(BaseTool):
    name: str = "Financial Analysis Tool"
    description: str = (
        "Access and analyze financial dataframes from Streamlit session state"
    )
    args_schema: Type[BaseModel] = FinancialAnalysisToolInput

    def _run(self, analysis_type: str = "overview") -> str:
        """
        Access financial dataframes from session state and return ACTUAL DATA for agent context

        Args:
            analysis_type: Type of analysis to perform ('overview', 'ratios', 'trends', 'detailed')
        """
        try:
            # Check if dataframes exist in session state
            if "dataframes" not in st.session_state:
                return "No financial dataframes found in session state. Please load financial data first."

            dataframes = st.session_state.dataframes
            if not dataframes:
                return (
                    "Financial dataframes are empty. Please load financial data first."
                )

            # Return comprehensive financial data based on analysis type
            if analysis_type == "overview":
                return self._get_comprehensive_financial_context(dataframes)
            elif analysis_type == "ratios":
                return self._get_detailed_ratios_context(dataframes)
            elif analysis_type == "trends":
                return self._get_trend_analysis_context(dataframes)
            elif analysis_type == "detailed":
                return self._get_complete_financial_data(dataframes)
            else:
                return self._get_comprehensive_financial_context(dataframes)

        except Exception as e:
            return f"Error accessing financial data: {str(e)}"

    def _get_overview_analysis(self, dataframes: Dict[str, pd.DataFrame]) -> str:
        """Get comprehensive overview analysis of financial dataframes with actual data"""
        analysis = "COMPREHENSIVE FINANCIAL DATA ANALYSIS:\n"
        analysis += "=" * 60 + "\n\n"

        # Identify the most recent year for current year analysis
        current_year = None
        latest_data = {}
        all_years = set()

        # First pass: collect all available years and latest data
        for key, df in dataframes.items():
            if not df.empty and "yearReport" in df.columns:
                years = df["yearReport"].unique()
                all_years.update(years)
                current_year = (
                    max(years) if not current_year else max(current_year, max(years))
                )

                # Get latest year data
                latest_year_data = df[df["yearReport"] == max(years)]
                if not latest_year_data.empty:
                    latest_data[key] = latest_year_data.iloc[-1]

        # Sort years for trend analysis
        sorted_years = sorted(list(all_years)) if all_years else []

        analysis += "DATA COVERAGE SUMMARY:\n"
        analysis += f"- Available years: {", ".join(map(str, sorted_years))}\n"
        analysis += f"- Current/Latest year: {current_year}\n"
        analysis += f"- Historical coverage: {len(sorted_years)} years\n\n"

        # Detailed analysis for each statement
        for key, df in dataframes.items():
            analysis += f"{key.upper()} STATEMENT DETAILED ANALYSIS:\n"
            analysis += "-" * 50 + "\n"
            analysis += f"Shape: {df.shape[0]} rows × {df.shape[1]} columns\n"

            if not df.empty:
                # Show column structure
                columns = df.columns.tolist()
                analysis += f"Available metrics: {len(columns)} total\n"

                # Show key financial metrics with actual values for current year
                if current_year and "yearReport" in df.columns:
                    current_data = df[df["yearReport"] == current_year]
                    if not current_data.empty:
                        analysis += f"\n{current_year} KEY FIGURES ({key}):\n"

                        # Get key line items with actual values
                        key_items = self._identify_key_line_items_with_values(
                            current_data, key
                        )
                        for metric_name, value in key_items.items():
                            if pd.notna(value) and value != 0:
                                analysis += f"  • {metric_name}: {self._format_financial_number(value)}\n"

                # Multi-year trend analysis for key metrics
                if len(sorted_years) > 1 and "yearReport" in df.columns:
                    analysis += f"\nMULTI-YEAR TRENDS ({key}):\n"
                    trend_metrics = self._get_trend_analysis_for_statement(
                        df, sorted_years, key
                    )
                    analysis += trend_metrics

                # Data quality assessment
                numeric_cols = df.select_dtypes(include=["number"]).columns
                non_zero_data = (
                    df[numeric_cols].replace(0, pd.NA).dropna(how="all", axis=1)
                )
                analysis += "\nDATA QUALITY:\n"
                analysis += f"  • Numeric metrics: {len(numeric_cols)}\n"
                analysis += f"  • Non-zero metrics: {len(non_zero_data.columns)}\n"
                analysis += f"  • Completeness: {((1 - df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100):.1f}%\n"

            analysis += "\n"

        # Cross-statement analysis summary
        if latest_data:
            analysis += "INTEGRATED FINANCIAL HEALTH INDICATORS:\n"
            analysis += "=" * 50 + "\n"

            # Extract key ratios and indicators
            health_indicators = self._calculate_financial_health_indicators(
                latest_data, current_year
            )
            analysis += health_indicators

        return analysis

    def _extract_key_metrics(
        self, df: pd.DataFrame, statement_type: str, analysis: str
    ) -> None:
        """Extract key metrics from financial statements"""
        # This is a helper method to identify important columns
        # Implementation would depend on the actual column names in the data
        pass

    def _identify_key_line_items_with_values(
        self, data: pd.DataFrame, statement_type: str
    ) -> Dict[str, float]:
        """Identify key line items from financial statements with actual values"""
        key_items = {}

        # Get the latest row of data
        if data.empty:
            return key_items

        latest_row = data.iloc[-1] if len(data) > 1 else data.iloc[0]

        # Exact column names from Vietnamese stock data (vnstock API)
        income_patterns = {
            "Net Profit Before Tax": ["Net Profit/Loss before tax"],
            "Interest Expense": ["Interest Expense"],
            "Depreciation and Amortisation": ["Depreciation and Amortisation"],
            "Operating Profit (Before WC Changes)": [
                "Operating profit before changes in working capital"
            ],
            "Interest Paid": ["Interest paid"],
            "Business Income Tax Paid": ["Business Income Tax paid"],
            # Fallback patterns for other income statement columns
            "Total Revenue": [
                "revenue",
                "net_sales",
                "sales",
                "total_revenue",
                "doanh_thu",
                "netsales",
            ],
            "Gross Profit": [
                "gross_profit",
                "gross_income",
                "loi_nhuan_gop",
                "grossprofit",
            ],
            "Net Income": [
                "net_income",
                "net_profit",
                "profit_after_tax",
                "loi_nhuan_rong",
                "netincome",
            ],
            "EPS": ["eps", "earnings_per_share", "thu_nhap_co_phieu", "basiceps"],
        }

        balance_patterns = {
            "Total Assets": ["TOTAL ASSETS (Bn. VND)"],
            "Current Assets": ["CURRENT ASSETS (Bn. VND)"],
            "Cash and Cash Equivalents": ["Cash and cash equivalents (Bn. VND)"],
            "Short-term Investments": ["Short-term investments (Bn. VND)"],
            "Accounts Receivable": ["Accounts receivable (Bn. VND)"],
            "Net Inventories": ["Net Inventories", "Inventories, Net (Bn. VND)"],
            "Long-term Assets": ["LONG-TERM ASSETS (Bn. VND)"],
            "Fixed Assets": ["Fixed assets (Bn. VND)"],
            "Long-term Investments": ["Long-term investments (Bn. VND)"],
            "Total Liabilities": ["LIABILITIES (Bn. VND)"],
            "Current Liabilities": ["Current liabilities (Bn. VND)"],
            "Long-term Liabilities": ["Long-term liabilities (Bn. VND)"],
            "Short-term Borrowings": ["Short-term borrowings (Bn. VND)"],
            "Long-term Borrowings": ["Long-term borrowings (Bn. VND)"],
            "Shareholders Equity": ["OWNER'S EQUITY(Bn.VND)"],
            "Capital and Reserves": ["Capital and reserves (Bn. VND)"],
            "Undistributed Earnings": ["Undistributed earnings (Bn. VND)"],
            "Paid-in Capital": ["Paid-in capital (Bn. VND)"],
            "Quick Ratio": ["Quick Ratio"],
        }

        cashflow_patterns = {
            "Operating Cash Flow": [
                "Net cash inflows/outflows from operating activities"
            ],
            "Investing Cash Flow": ["Net Cash Flows from Investing Activities"],
            "Financing Cash Flow": ["Cash flows from financial activities"],
            "Net Profit Before Tax": ["Net Profit/Loss before tax"],
            "Interest Expense": ["Interest Expense"],
            "Interest Paid": ["Interest paid"],
            "Purchase of Fixed Assets": ["Purchase of fixed assets"],
            "Proceeds from Asset Disposal": ["Proceeds from disposal of fixed assets"],
            "Proceeds from Borrowings": ["Proceeds from borrowings"],
            "Repayment of Borrowings": ["Repayment of borrowings"],
            "Dividends Paid": ["Dividends paid"],
            "Net Cash Change": ["Net increase/decrease in cash and cash equivalents"],
            "Cash at End of Period": ["Cash and Cash Equivalents at the end of period"],
        }

        ratio_patterns = {
            "ROE": ["roe", "return_on_equity", "returnonequity"],
            "ROA": ["roa", "return_on_assets", "returnonassets"],
            "Current Ratio": ["current_ratio", "currentratio"],
            "Debt to Equity": ["debt_to_equity", "debttoequity", "debt_equity"],
            "P/E Ratio": ["pe_ratio", "price_earnings", "peratio"],
            "Gross Margin": ["gross_margin", "grossmargin"],
            "Net Margin": ["net_margin", "netmargin", "profit_margin"],
        }

        # Select appropriate patterns based on statement type
        patterns = {}
        if "income" in statement_type.lower() or "profit" in statement_type.lower():
            patterns = income_patterns
        elif "balance" in statement_type.lower() or "sheet" in statement_type.lower():
            patterns = balance_patterns
        elif "cash" in statement_type.lower() or "flow" in statement_type.lower():
            patterns = cashflow_patterns
        elif "ratio" in statement_type.lower():
            patterns = ratio_patterns

        # Match patterns with actual column names (case insensitive)
        for display_name, search_patterns in patterns.items():
            for pattern in search_patterns:
                matching_cols = [
                    col for col in latest_row.index if pattern.lower() in col.lower()
                ]
                if matching_cols:
                    # Use the first matching column
                    value = latest_row[matching_cols[0]]
                    if pd.notna(value):
                        key_items[display_name] = float(value)
                    break

        return key_items

    def _format_financial_number(self, value: float) -> str:
        """Format financial numbers for display"""
        try:
            if abs(value) >= 1e12:
                return f"{value / 1e12:.2f}T VND"
            elif abs(value) >= 1e9:
                return f"{value / 1e9:.2f}B VND"
            elif abs(value) >= 1e6:
                return f"{value / 1e6:.2f}M VND"
            elif abs(value) >= 1e3:
                return f"{value / 1e3:.2f}K VND"
            else:
                return f"{value:.2f} VND"
        except:
            return str(value)

    def _get_comprehensive_financial_context(
        self, dataframes: Dict[str, pd.DataFrame]
    ) -> str:
        """Provide comprehensive financial data context for agents"""
        context = "=== COMPREHENSIVE FINANCIAL DATA CONTEXT ===\n\n"

        # Get current year and multi-year data
        current_year = None
        all_years = set()

        # First pass: identify years
        for key, df in dataframes.items():
            if not df.empty and "yearReport" in df.columns:
                years = df["yearReport"].unique()
                all_years.update(years)
                current_year = (
                    max(years) if not current_year else max(current_year, max(years))
                )

        sorted_years = sorted(list(all_years)) if all_years else []
        context += f"ANALYSIS PERIOD: {min(sorted_years)} - {max(sorted_years)} ({len(sorted_years)} years)\n"
        context += f"CURRENT YEAR: {current_year}\n\n"

        # Provide actual financial data for each statement
        for statement_name, df in dataframes.items():
            if df.empty:
                continue

            context += f"=== {statement_name.upper()} DATA ===\n"

            # Current year detailed data
            if current_year and "yearReport" in df.columns:
                current_data = df[df["yearReport"] == current_year]
                if not current_data.empty:
                    context += f"\n{current_year} KEY FIGURES:\n"

                    # Get all numeric columns with actual values
                    numeric_cols = current_data.select_dtypes(
                        include=["number"]
                    ).columns
                    latest_row = current_data.iloc[-1]

                    for col in numeric_cols:
                        if (
                            col != "yearReport"
                            and pd.notna(latest_row[col])
                            and latest_row[col] != 0
                        ):
                            value = latest_row[col]
                            context += (
                                f"• {col}: {self._format_financial_number(value)}\n"
                            )

                # Multi-year comparison for key metrics
                if len(sorted_years) >= 2:
                    context += f"\nMULTI-YEAR COMPARISON ({statement_name}):\n"
                    key_metrics = self._get_key_metrics_for_statement(
                        df, statement_name
                    )

                    for metric in key_metrics:
                        if metric in df.columns:
                            context += f"\n{metric} by Year:\n"
                            for year in sorted_years[-3:]:  # Last 3 years
                                year_data = df[df["yearReport"] == year]
                                if not year_data.empty:
                                    value = (
                                        year_data[metric].iloc[-1]
                                        if not pd.isna(year_data[metric].iloc[-1])
                                        else 0
                                    )
                                    context += f"  {year}: {self._format_financial_number(value)}\n"

            context += "\n"

        return context

    def _get_detailed_ratios_context(self, dataframes: Dict[str, pd.DataFrame]) -> str:
        """Provide detailed financial ratios context"""
        if "Ratios" not in dataframes or dataframes["Ratios"].empty:
            return "No ratio data available for analysis."

        df = dataframes["Ratios"]
        context = "=== DETAILED FINANCIAL RATIOS CONTEXT ===\n\n"

        # Get current year ratios
        if "yearReport" in df.columns:
            current_year = df["yearReport"].max()
            current_ratios = df[df["yearReport"] == current_year]

            if not current_ratios.empty:
                context += f"{current_year} FINANCIAL RATIOS:\n"

                # Categorize ratios
                ratio_categories = {
                    "Profitability": [
                        "roe",
                        "roa",
                        "gross_margin",
                        "net_margin",
                        "operating_margin",
                    ],
                    "Liquidity": ["current_ratio", "quick_ratio", "cash_ratio"],
                    "Leverage": ["debt_equity", "debt_ratio", "interest_coverage"],
                    "Efficiency": [
                        "asset_turnover",
                        "inventory_turnover",
                        "receivables_turnover",
                    ],
                    "Valuation": ["pe_ratio", "pb_ratio", "ev_ebitda"],
                }

                latest_row = current_ratios.iloc[-1]
                numeric_cols = current_ratios.select_dtypes(include=["number"]).columns

                for category, ratio_patterns in ratio_categories.items():
                    category_ratios = []
                    for col in numeric_cols:
                        if any(pattern in col.lower() for pattern in ratio_patterns):
                            if pd.notna(latest_row[col]) and latest_row[col] != 0:
                                category_ratios.append(
                                    f"  • {col}: {latest_row[col]:.2f}"
                                )

                    if category_ratios:
                        context += (
                            f"\n{category} Ratios:\n"
                            + "\n".join(category_ratios)
                            + "\n"
                        )

        return context

    def _get_trend_analysis_context(self, dataframes: Dict[str, pd.DataFrame]) -> str:
        """Provide trend analysis context with actual data"""
        context = "=== FINANCIAL TRENDS ANALYSIS CONTEXT ===\n\n"

        for statement_name, df in dataframes.items():
            if df.empty or "yearReport" not in df.columns:
                continue

            years = sorted(df["yearReport"].unique())
            if len(years) < 2:
                continue

            context += f"{statement_name.upper()} TRENDS:\n"
            key_metrics = self._get_key_metrics_for_statement(df, statement_name)

            for metric in key_metrics[:5]:  # Top 5 key metrics
                if metric in df.columns:
                    trend_data = []
                    for year in years:
                        year_data = df[df["yearReport"] == year]
                        if not year_data.empty and not pd.isna(
                            year_data[metric].iloc[-1]
                        ):
                            value = year_data[metric].iloc[-1]
                            trend_data.append((year, value))

                    if len(trend_data) >= 2:
                        context += f"\n{metric}:\n"
                        for year, value in trend_data:
                            context += (
                                f"  {year}: {self._format_financial_number(value)}\n"
                            )

                        # Calculate growth rate
                        if trend_data[-1][1] != 0 and trend_data[0][1] != 0:
                            growth_rate = (
                                (trend_data[-1][1] / trend_data[0][1]) - 1
                            ) * 100
                            context += f"  Growth: {growth_rate:.1f}% over period\n"

            context += "\n"

        return context

    def _get_complete_financial_data(self, dataframes: Dict[str, pd.DataFrame]) -> str:
        """Provide complete financial dataset for detailed analysis"""
        context = "=== COMPLETE FINANCIAL DATASET ===\n\n"

        for statement_name, df in dataframes.items():
            if df.empty:
                continue

            context += f"{statement_name.upper()} - COMPLETE DATA:\n"
            context += f"Columns: {", ".join(df.columns.tolist())}\n"
            context += f"Records: {len(df)} rows\n"

            # Show recent data (last 3 years if available)
            if "yearReport" in df.columns:
                recent_years = sorted(df["yearReport"].unique())[-3:]
                context += (
                    f"\nRecent Years Data ({", ".join(map(str, recent_years))}):\n"
                )

                recent_data = df[df["yearReport"].isin(recent_years)]
                numeric_cols = recent_data.select_dtypes(include=["number"]).columns

                for _, row in recent_data.iterrows():
                    year = row.get("yearReport", "Unknown")
                    context += f"\n{year}:\n"
                    for col in numeric_cols:
                        if col != "yearReport" and pd.notna(row[col]) and row[col] != 0:
                            context += (
                                f"  {col}: {self._format_financial_number(row[col])}\n"
                            )

            context += "\n" + "=" * 50 + "\n"

        return context

    def _get_key_metrics_for_statement(
        self, df: pd.DataFrame, statement_name: str
    ) -> List[str]:
        """Get key metrics based on statement type"""
        all_cols = df.columns.tolist()

        if "income" in statement_name.lower():
            patterns = [
                "revenue",
                "sales",
                "gross",
                "operating",
                "net_income",
                "profit",
                "ebit",
            ]
        elif "balance" in statement_name.lower():
            patterns = ["assets", "liabilities", "equity", "cash", "debt", "inventory"]
        elif "cash" in statement_name.lower():
            patterns = ["operating", "investing", "financing", "free_cash", "capex"]
        elif "ratio" in statement_name.lower():
            patterns = ["roe", "roa", "current_ratio", "debt", "margin", "turnover"]
        else:
            patterns = ["total", "net", "gross", "operating"]

        key_metrics = []
        for col in all_cols:
            if any(pattern in col.lower() for pattern in patterns):
                key_metrics.append(col)

        return key_metrics[:10]  # Return top 10 matches

    def _calculate_financial_health_indicators(
        self, latest_data: Dict[str, pd.Series], current_year: int
    ) -> str:
        """Calculate key financial health indicators from latest data"""
        indicators = f"FINANCIAL HEALTH INDICATORS ({current_year}):\n"
        indicators += "-" * 40 + "\n"

        try:
            # Extract data from different statements
            income_data = latest_data.get("IncomeStatement")
            balance_data = latest_data.get("BalanceSheet")
            cashflow_data = latest_data.get("CashFlow")
            ratio_data = latest_data.get("Ratios")

            # Revenue and profitability analysis
            if income_data is not None:
                revenue_metrics = self._identify_key_line_items_with_values(
                    pd.DataFrame([income_data]), "IncomeStatement"
                )
                if revenue_metrics:
                    indicators += "\nREVENUE & PROFITABILITY:\n"
                    for metric, value in revenue_metrics.items():
                        indicators += (
                            f"• {metric}: {self._format_financial_number(value)}\n"
                        )

            # Balance sheet strength
            if balance_data is not None:
                balance_metrics = self._identify_key_line_items_with_values(
                    pd.DataFrame([balance_data]), "BalanceSheet"
                )
                if balance_metrics:
                    indicators += "\nBALANCE SHEET STRENGTH:\n"
                    for metric, value in balance_metrics.items():
                        indicators += (
                            f"• {metric}: {self._format_financial_number(value)}\n"
                        )

            # Cash flow health
            if cashflow_data is not None:
                cashflow_metrics = self._identify_key_line_items_with_values(
                    pd.DataFrame([cashflow_data]), "CashFlow"
                )
                if cashflow_metrics:
                    indicators += "\nCASH FLOW HEALTH:\n"
                    for metric, value in cashflow_metrics.items():
                        indicators += (
                            f"• {metric}: {self._format_financial_number(value)}\n"
                        )

            # Key financial ratios
            if ratio_data is not None:
                ratio_metrics = self._identify_key_line_items_with_values(
                    pd.DataFrame([ratio_data]), "Ratios"
                )
                if ratio_metrics:
                    indicators += "\nKEY FINANCIAL RATIOS:\n"
                    for metric, value in ratio_metrics.items():
                        indicators += f"• {metric}: {value:.2f}\n"

        except Exception as e:
            indicators += f"\nError calculating indicators: {str(e)}\n"

        return indicators

    def _get_ratio_analysis(self, dataframes: Dict[str, pd.DataFrame]) -> str:
        """Get comprehensive financial ratio analysis with actual data"""
        if "Ratios" not in dataframes or dataframes["Ratios"].empty:
            return "No ratio data available for comprehensive analysis."

        return self._get_detailed_ratios_context(dataframes)

    def _get_trend_analysis(self, dataframes: Dict[str, pd.DataFrame]) -> str:
        """Get comprehensive trend analysis with actual financial data"""
        return self._get_trend_analysis_context(dataframes)
