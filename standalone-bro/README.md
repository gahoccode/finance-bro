# Standalone Finance Bro

A streamlined, standalone version of the Finance Bro AI chat interface for Vietnamese stock market analysis.

## Features

- 🤖 AI-powered financial analysis using PandasAI
- 📊 Real-time Vietnamese stock data via Vnstock API
- 📈 Chart generation and data visualization
- 🎯 Stock symbol selection and configuration
- 🔑 Direct OpenAI API key integration
- 🎨 Professional finance theme styling

## Requirements

- Python 3.10.11
- OpenAI API key

## Installation

1. Clone or extract the standalone-bro directory
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
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

## Configuration

- **Data Sources**: VCI (default) or TCBS for stock data
- **Period**: Annual or quarterly financial data
- **Chart Export**: Charts saved to `exports/charts/` directory

## Sample Questions

The app includes pre-loaded sample questions for common financial analysis:
- ROIC analysis
- Dividend schedule analysis
- Debt-to-equity ratios
- Profitability trends
- And more...

## File Structure

```
standalone-bro/
├── standalone_bro.py      # Main application
├── requirements.txt       # Dependencies
├── .streamlit/
│   └── config.toml       # Theme configuration
├── exports/charts/       # Generated charts
└── README.md             # This file
```

## Dependencies

- `streamlit==1.47.0` - Web framework
- `pandas==1.5.3` - Data processing
- `pandasai==2.3.0` - AI analysis
- `vnstock==3.2.5` - Vietnamese stock data
- `openai>=1.61.0` - LLM integration
- `altair>=5.5.0` - Visualizations

## Notes

- Requires internet connection for Vnstock API and OpenAI services
- All financial data is fetched in real-time, no local database
- Charts are temporarily saved and displayed in the chat interface