"""Vnstock v4 financial statement helpers."""

from dataclasses import dataclass
from typing import Mapping

import pandas as pd
from vnstock import Finance


FINANCE_METADATA_COLUMNS: frozenset[str] = frozenset(
    {
        "item",
        "item_id",
        "ticker",
        "organ_code",
        "model_type",
        "source",
        "period",
        "period_type",
        "quarter",
        "year",
        "report_type",
    }
)


@dataclass(frozen=True)
class FinanceClient:
    """Fetch financial statements through vnstock v4 top-level Finance."""

    symbol: str
    source: str
    period: str

    def _finance(self) -> Finance:
        """Create a vnstock Finance adapter for the configured symbol."""
        return Finance(
            source=self.source,
            symbol=self.symbol,
            period=self.period,
            get_all=True,
            show_log=False,
        )

    def fetch_statements(self) -> dict[str, pd.DataFrame]:
        """Return cash flow, balance sheet, income statement, and ratios."""
        finance = self._finance()
        ratios = finance.ratio(period=self.period)

        if ratios.empty and self.source.upper() == "VCI":
            ratios = Finance(
                source="KBS",
                symbol=self.symbol,
                period=self.period,
                get_all=True,
                show_log=False,
            ).ratio(period=self.period)

        return {
            "CashFlow": finance.cash_flow(period=self.period),
            "BalanceSheet": finance.balance_sheet(period=self.period),
            "IncomeStatement": finance.income_statement(period=self.period),
            "Ratios": ratios,
            "Dividends": pd.DataFrame(),
        }


def get_period_columns(df: pd.DataFrame) -> list[object]:
    """Return vnstock v4 period columns from an item-row dataframe."""
    return [
        column
        for column in df.columns
        if str(column).lower() not in FINANCE_METADATA_COLUMNS
        and str(column) != "Metric"
    ]


def prepare_financial_dataframe_for_ai(df: pd.DataFrame) -> pd.DataFrame:
    """Add PandasAI-friendly metric labels while preserving vnstock v4 IDs."""
    if df.empty:
        return df.copy()

    prepared = df.copy()
    if "Metric" not in prepared.columns:
        if "item" in prepared.columns:
            prepared.insert(0, "Metric", prepared["item"])
        elif "item_id" in prepared.columns:
            prepared.insert(0, "Metric", prepared["item_id"])

    return prepared


def prepare_finance_dataframes(
    dataframes: Mapping[str, pd.DataFrame],
) -> dict[str, pd.DataFrame]:
    """Create PandasAI-ready copies of vnstock financial dataframes."""
    return {
        name: prepare_financial_dataframe_for_ai(df)
        for name, df in dataframes.items()
    }


def format_financial_dataframe_for_display(df: pd.DataFrame) -> pd.DataFrame:
    """Return a readable display dataframe for vnstock v4 item-row data."""
    if df.empty:
        return df.copy()

    display_df = prepare_financial_dataframe_for_ai(df)
    period_columns = get_period_columns(display_df)
    leading_columns = [
        column
        for column in ["Metric", "item_id"]
        if column in display_df.columns
    ]
    remaining_columns = [
        column
        for column in display_df.columns
        if column not in leading_columns and column not in period_columns
    ]

    return display_df[leading_columns + period_columns + remaining_columns]
