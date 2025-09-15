# Standalone Finance Bro

A streamlined, standalone version of the Finance Bro AI chat interface for Vietnamese stock market analysis.

## Features

- 🤖 AI-powered financial analysis using PandasAI
- 📊 Real-time Vietnamese stock data via Vnstock API
- 📈 Chart generation with Altair visualizations
- 🎯 Stock symbol selection and configuration
- 🔑 Direct OpenAI API key integration
- 🎨 Professional finance theme styling
- 📋 Pre-loaded sample questions for common analysis

## Requirements

- Python 3.10.11 or higher
- OpenAI API key

## Installation

1. Clone or extract the standalone-bro directory
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   Or use UV for faster installation:
   ```bash
   uv sync
   ```

## Usage

1. Set your OpenAI API key:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```
   Or enter it directly in the app interface

2. Run the application:
   ```bash
   streamlit run standalone_bro.py
   ```

3. Open your browser and navigate to `http://localhost:8501`

## Key Differences from Main App

- **No authentication required** - Works standalone without Google OAuth
- **Self-contained** - All dependencies inlined, no external module imports
- **Direct API key input** - Enter OpenAI API key in the sidebar
- **Simplified stock selection** - Choose from available Vietnamese stock symbols
- **Essential features only** - Focused on AI chat analysis without extra pages
- **Python 3.10.11+ compatibility** - Uses stable pandas 1.5.3 and pandasai 2.3.0

## Configuration

- **Data Sources**: VCI (default) or TCBS for stock data
- **Period**: Annual or quarterly financial data
- **Chart Export**: Charts saved to `exports/charts/` directory
- **Theme**: Professional finance theme with earth-tone styling

## Sample Questions

The app includes pre-loaded sample questions for common financial analysis:
- EPS growth vs Net Profit Margin analysis
- Dividend yield trend analysis
- Debt-to-equity ratio calculation
- Revenue growth analysis
- ROE calculation and trends
- Operating Cash Flow vs Sales analysis
- Profitability trend analysis
- Balance sheet health indicators

## File Structure

```
standalone-bro/
├── standalone_bro.py      # Main application with inlined dependencies
├── requirements.txt       # Dependencies
├── .streamlit/
│   └── config.toml       # Theme configuration
├── exports/charts/       # Generated charts
└── README.md             # This file
```

## Dependencies

- `streamlit==1.47.0` - Web framework
- `pandas==1.5.3` - Data processing (stable version)
- `numpy>=1.26.4,<2.0.0` - Numerical computing
- `pandasai==2.3.0` - AI analysis (stable version)
- `vnstock==3.2.5` - Vietnamese stock data
- `openai>=1.61.0` - LLM integration
- `altair>=5.5.0` - Statistical visualizations
- `vl-convert-python>=1.6.0` - Chart export
- `python-dotenv==1.0.1` - Environment variables

## Technology Stack

The standalone app uses a focused technology stack optimized for AI-powered financial analysis:

- **AI Engine**: PandasAI 2.3.0 with OpenAI GPT models
- **Data Processing**: Pandas 1.5.3 with NumPy backend
- **Financial Data**: VnStock 3.2.5 for Vietnamese market data
- **Visualization**: Altair for interactive statistical charts
- **Framework**: Streamlit 1.47.0 for web interface

## Notes

- Requires internet connection for Vnstock API and OpenAI services
- All financial data is fetched in real-time, no local database
- Charts are temporarily saved and displayed in the chat interface
- Uses pandas 1.5.3 for compatibility with pandasai 2.3.0
- Supports both VCI and TCBS data sources for comprehensive market coverage