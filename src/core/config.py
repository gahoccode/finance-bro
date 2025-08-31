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
    "Calculate EPS growth in 2024 and compare to the Net Profit Margin percentage in 2024? Convert the Net Profit Margin from decimal to percentage. Answer by concluding whether EPS growth is tracking ahead or behind profitability",
    "Analyze the dividend yield trend",
    "What is the company's debt-to-equity ratio?",
    "What's 2024 revenue growth?",
    "What's the ROE in 2024?",
    "Plot a line chart of OCF and Sales over the years?",
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

# Financial display formatting options
FINANCIAL_DISPLAY_OPTIONS = {
    "BILLIONS": {
        "key": "billions",
        "label": "Billions (B VND)",
        "divisor": 1_000_000_000,
        "suffix": "B VND",
    },
    "MILLIONS": {
        "key": "millions",
        "label": "Millions (M VND)",
        "divisor": 1_000_000,
        "suffix": "M VND",
    },
    "ORIGINAL": {
        "key": "original",
        "label": "Original Scale (VND)",
        "divisor": 1,
        "suffix": "VND",
    },
}

# Default financial display settings
DEFAULT_FINANCIAL_DISPLAY = {
    "unit": "billions",
    "decimal_places": 0,
    "session_key": "financial_display_unit",
}

# Tax rate constants
DEFAULT_STATUTORY_TAX_RATE = 20.0  # Vietnamese corporate tax rate (%)
