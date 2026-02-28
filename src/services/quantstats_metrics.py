"""
QuantStats metrics calculation service for Finance Bro application.

Centralized metrics calculation with uniform formatting (1 decimal place).
Extracted from pages/Stock_Price_Analysis.py for reusability.
"""

import quantstats as qs


def get_metric_categories() -> dict[str, list[str]]:
    """Return available metric categories organized by analysis type.

    Returns:
        Dictionary with category names as keys and lists of metric names as values.
    """
    return {
        "All Metrics": [
            "adjusted_sortino",
            "autocorr_penalty",
            "avg_loss",
            "avg_return",
            "avg_win",
            "best",
            "cagr",
            "calmar",
            "common_sense_ratio",
            "comp",
            "conditional_value_at_risk",
            "consecutive_losses",
            "consecutive_wins",
            "cpc_index",
            "cvar",
            "expected_return",
            "expected_shortfall",
            "exposure",
            "gain_to_pain_ratio",
            "geometric_mean",
            "ghpr",
            "information_ratio",
            "kelly_criterion",
            "kurtosis",
            "max_drawdown",
            "omega",
            "outlier_loss_ratio",
            "outlier_win_ratio",
            "payoff_ratio",
            "pct_rank",
            "probabilistic_adjusted_sortino_ratio",
            "probabilistic_ratio",
            "probabilistic_sharpe_ratio",
            "probabilistic_sortino_ratio",
            "profit_factor",
            "profit_ratio",
            "r2",
            "r_squared",
            "rar",
            "recovery_factor",
            "risk_of_ruin",
            "risk_return_ratio",
            "rolling_sharpe",
            "rolling_sortino",
            "rolling_volatility",
            "serenity_index",
            "sharpe",
            "skew",
            "smart_sharpe",
            "smart_sortino",
            "sortino",
            "tail_ratio",
            "treynor_ratio",
            "ulcer_index",
            "ulcer_performance_index",
            "upi",
            "value_at_risk",
            "var",
            "volatility",
            "win_loss_ratio",
            "win_rate",
            "worst",
        ],
        "Core Performance": [
            "sharpe",
            "sortino",
            "calmar",
            "cagr",
            "max_drawdown",
            "volatility",
        ],
        "Risk Analysis": [
            "value_at_risk",
            "conditional_value_at_risk",
            "expected_shortfall",
            "ulcer_index",
            "risk_of_ruin",
            "tail_ratio",
            "skew",
            "kurtosis",
            "autocorr_penalty",
            "serenity_index",
            "omega",
            "treynor_ratio",
        ],
        "Return Analysis": [
            "avg_return",
            "expected_return",
            "geometric_mean",
            "win_rate",
            "avg_win",
            "avg_loss",
            "best",
            "worst",
        ],
        "Advanced Ratios": [
            "information_ratio",
            "gain_to_pain_ratio",
            "profit_factor",
            "kelly_criterion",
            "common_sense_ratio",
            "recovery_factor",
            "payoff_ratio",
            "profit_ratio",
            "win_loss_ratio",
            "outlier_win_ratio",
            "outlier_loss_ratio",
            "r_squared",
            "probabilistic_sharpe_ratio",
            "smart_sharpe",
            "adjusted_sortino",
        ],
        "Rolling Metrics": [
            "rolling_sharpe",
            "rolling_sortino",
            "rolling_volatility",
        ],
        "Specialized": [
            "consecutive_wins",
            "consecutive_losses",
            "exposure",
            "cpc_index",
            "upi",
            "pct_rank",
            "rar",
        ],
    }


def format_metric_name(metric_name: str) -> str:
    """Convert snake_case metric names to readable format.

    Args:
        metric_name: The metric name in snake_case format.

    Returns:
        Formatted metric name with special cases handled.
    """
    special_cases = {
        "cagr": "CAGR",
        "var": "VaR",
        "cvar": "CVaR",
        "conditional_value_at_risk": "Conditional VaR (CVaR)",
        "value_at_risk": "Value at Risk (VaR)",
        "expected_shortfall": "Expected Shortfall (ES)",
        "r_squared": "R-Squared",
        "r2": "R²",
        "upi": "UPI",
        "cpc_index": "CPC Index",
        "rar": "RAR",
        "ghpr": "GHPR",
        "probabilistic_sharpe_ratio": "Probabilistic Sharpe",
        "probabilistic_sortino_ratio": "Probabilistic Sortino",
        "probabilistic_adjusted_sortino_ratio": "Probabilistic Adjusted Sortino",
        "smart_sharpe": "Smart Sharpe",
        "smart_sortino": "Smart Sortino",
        "ulcer_performance_index": "Ulcer Performance Index",
    }

    if metric_name in special_cases:
        return special_cases[metric_name]

    return metric_name.replace("_", " ").title()


def get_metric_descriptions() -> dict[str, str]:
    """Return descriptions for common metrics.

    Returns:
        Dictionary mapping metric names to their descriptions.
    """
    return {
        "sharpe": "Risk-adjusted return measure",
        "sortino": "Downside risk-adjusted return",
        "calmar": "Return to max drawdown ratio",
        "cagr": "Compound Annual Growth Rate",
        "max_drawdown": "Largest peak-to-trough decline",
        "volatility": "Standard deviation of returns",
        "value_at_risk": "Potential loss at 95% confidence",
        "conditional_value_at_risk": "Expected loss beyond VaR",
        "expected_shortfall": "Average loss in worst scenarios",
        "ulcer_index": "Measure of downside volatility",
        "win_rate": "Percentage of positive returns",
        "avg_return": "Average periodic return",
        "best": "Best single period return",
        "worst": "Worst single period return",
        "information_ratio": "Active return per unit of tracking error",
        "kelly_criterion": "Optimal bet size for growth",
        "profit_factor": "Gross profit to gross loss ratio",
        "recovery_factor": "Net profit to max drawdown ratio",
        "tail_ratio": "Right tail to left tail ratio",
        "skew": "Asymmetry of return distribution",
        "kurtosis": "Fat-tailedness of distribution",
        "consecutive_wins": "Max consecutive positive periods",
        "consecutive_losses": "Max consecutive negative periods",
        "exposure": "Percentage of time invested",
    }


def calculate_custom_metrics(
    returns_data, selected_metrics: list[str], include_descriptions: bool = False
) -> dict[str, dict]:
    """Calculate selected QuantStats metrics with uniform formatting.

    All numeric values are rounded to 1 decimal place for consistency.

    Args:
        returns_data: Pandas Series of returns data.
        selected_metrics: List of metric names to calculate.
        include_descriptions: Whether to include metric descriptions.

    Returns:
        Dictionary mapping metric names to dicts with keys: name, value, description.
    """
    if not selected_metrics:
        return {}

    results = {}
    descriptions = get_metric_descriptions() if include_descriptions else {}

    for metric in selected_metrics:
        try:
            metric_func = getattr(qs.stats, metric, None)
            if metric_func and callable(metric_func):
                value = metric_func(returns_data)

                formatted_name = format_metric_name(metric)

                # Uniform formatting: all numeric values to 1 decimal place
                if isinstance(value, int | float):
                    formatted_value = f"{value:.1f}"
                else:
                    formatted_value = str(value)

                results[metric] = {
                    "name": formatted_name,
                    "value": formatted_value,
                    "description": descriptions.get(metric, "")
                    if include_descriptions
                    else "",
                }
        except Exception:
            # Skip metrics that fail to calculate
            continue

    return results


def get_available_metrics() -> list[str]:
    """Return all available QuantStats metric function names.

    Excludes non-metric functions like compare, distribution, warn, etc.

    Returns:
        List of available metric function names from QuantStats.
    """
    excluded_functions = {
        "compare",
        "distribution",
        "warn",
        "group_returns",
        "information_ratio_rank",
        "r2_rank",
        "r_squared_rank",
        "sharpe_rank",
        "sortino_rank",
    }

    return [f for f in dir(qs.stats) if f[0] != "_" and f not in excluded_functions]
