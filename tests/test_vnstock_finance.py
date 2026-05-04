import pandas as pd

from src.services.vnstock_finance import (
    format_financial_dataframe_for_display,
    get_period_columns,
    prepare_finance_dataframes,
    prepare_financial_dataframe_for_ai,
)


def test_get_period_columns_detects_v4_annual_period_columns() -> None:
    df = pd.DataFrame(
        {
            "item": ["Net revenue"],
            "item_id": ["n_3.net_revenue"],
            "2025": [1200],
            "2024": [1000],
            "source": ["KBS"],
        }
    )

    assert get_period_columns(df) == ["2025", "2024"]


def test_prepare_financial_dataframe_for_ai_adds_metric_from_item() -> None:
    df = pd.DataFrame(
        {
            "item": ["ROE"],
            "item_id": ["roe"],
            "2025": [0.21],
            "2024": [0.18],
        }
    )

    prepared = prepare_financial_dataframe_for_ai(df)

    assert prepared.columns.tolist() == ["Metric", "item", "item_id", "2025", "2024"]
    assert prepared.loc[0, "Metric"] == "ROE"
    assert prepared.loc[0, "item_id"] == "roe"


def test_prepare_financial_dataframe_for_ai_falls_back_to_item_id() -> None:
    df = pd.DataFrame({"item_id": ["roe"], "2025": [0.21]})

    prepared = prepare_financial_dataframe_for_ai(df)

    assert prepared.loc[0, "Metric"] == "roe"


def test_prepare_finance_dataframes_preserves_empty_dividends_dataframe() -> None:
    dataframes = {
        "Ratios": pd.DataFrame({"item": ["ROE"], "item_id": ["roe"], "2025": [0.21]}),
        "Dividends": pd.DataFrame(),
    }

    prepared = prepare_finance_dataframes(dataframes)

    assert prepared["Ratios"].loc[0, "Metric"] == "ROE"
    assert prepared["Dividends"].empty


def test_format_financial_dataframe_for_display_orders_metric_id_and_periods() -> None:
    df = pd.DataFrame(
        {
            "item": ["Net revenue"],
            "item_id": ["n_3.net_revenue"],
            "source": ["KBS"],
            "2025": [1200],
            "2024": [1000],
        }
    )

    display_df = format_financial_dataframe_for_display(df)

    assert display_df.columns.tolist() == [
        "Metric",
        "item_id",
        "2025",
        "2024",
        "item",
        "source",
    ]
