"""
Configuration constants and settings for Finance Bro application.
Centralizes all constants used across the application.
"""

# Default stock symbols fallback list
DEFAULT_STOCK_SYMBOLS = ["REE", "VIC", "VNM", "VCB", "BID", "HPG", "FPT", "FMC", "DHC"]

# Data source configurations
VNSTOCK_SOURCES = {"PRIMARY": "VCI", "SECONDARY": "TCBS"}

# Cache TTL settings (in seconds)
CACHE_TTL = {
    "COMPANY_DATA": 3600,  # 1 hour
    "STOCK_DATA": 3600,  # 1 hour
    "TECHNICAL_DATA": 300,  # 5 minutes
    "SCREENER_DATA": 3600,  # 1 hour
}

# Date range defaults
DEFAULT_ANALYSIS_START_DATE = "2024-01-01"

# Technical analysis intervals
TECHNICAL_INTERVALS = {
    "1D": {"days": 90, "label": "Daily (3 months)"},
    "1W": {"days": 180, "label": "Weekly (6 months)"},
    "1M": {"days": 730, "label": "Monthly (2 years)"},
}

# Chart configuration
CHART_EXPORT_PATH = "exports/charts/"
CHART_DEFAULT_FILENAME = "temp_chart.png"

# Model configuration
DEFAULT_OPENAI_MODEL = "gpt-4o-mini"

# Screener preset configurations
SCREENER_PRESETS = {
    "banking": {"industries": ["Banks"], "roe": True, "market_cap": True},
    "quality": {"financial_health": True, "beta": True, "stock_rating": True},
    "profitability": {"roe": True, "roa": True},
}

# Sample questions for AI analysis
SAMPLE_QUESTIONS = [
    "What is the return on invested capital (ROIC) trend?",
    "Analyze the dividend yield trend",
    "What is the company's debt-to-equity ratio?",
    "What's 2024 revenue growth?",
    "What's the ROE in 2024?",
    "How has cash flow evolved over time?",
    "What is the company's profitability trend?",
    "Analyze the balance sheet health indicators",
]

# Portfolio optimization strategies
PORTFOLIO_STRATEGIES = {
    "max_sharpe": "Maximum Sharpe Ratio",
    "min_vol": "Minimum Volatility",
    "max_utility": "Maximum Utility",
}

# Column mappings for mplfinance
MPLFINANCE_COLUMN_MAPPING = {
    "open": "Open",
    "high": "High",
    "low": "Low",
    "close": "Close",
    "volume": "Volume",
}

# Required columns for financial charts
REQUIRED_OHLCV_COLUMNS = ["Open", "High", "Low", "Close", "Volume"]

# Theme colors (matching existing Streamlit theme)
THEME_COLORS = {"primary": "#56524D", "secondary": "#2B2523", "tertiary": "#76706C"}

# Vnstock API configuration
VNSTOCK_API_KEY_ENV = "VNSTOCK_API_KEY"
