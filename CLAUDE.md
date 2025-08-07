# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Application
```bash
# With uv (recommended)
uv run streamlit run app.py

# With pip/python
streamlit run app.py
```

### Docker Commands
```bash
# Build and run with Docker Compose
docker-compose up --build

# Build Docker image
docker build -t finance-bro .

# Run container
docker run -p 8501:8501 -e OPENAI_API_KEY=your_key finance-bro
```

### Development Tools
```bash
# Install dependencies with uv
uv sync

# Install with pip
pip install -r requirements.txt

# Run tests (pytest available in dev dependencies)
uv run pytest

# Code formatting
uv run black .

# Linting
uv run flake8

# Type checking
uv run mypy .
```

## Architecture Overview

This is a Streamlit-based AI financial analysis application for Vietnamese stock market data.

### Core Structure
- **app.py** - Main entry point with authentication and API key setup
- **pages/** - Multi-page Streamlit app structure:
  - **bro.py** - Main AI chat interface with PandasAI integration
  - **Company_Overview.py** - Company profile and ownership analysis
  - **Stock_Price_Analysis.py** - Price charts and technical analysis
  - **Portfolio_Optimization.py** - Modern Portfolio Theory optimization
- **static/** - CSS styling
- **cache/** - Data caching for performance
- **exports/charts/** - Generated chart storage

### Key Technologies
- **Streamlit** - Web framework (v1.47.0)
- **PandasAI** - AI data analysis (v2.3.0 - stable, compatible with pandas 1.5.3)
- **vnstock** - Vietnamese stock market data (v3.2.5)
- **OpenAI API** - LLM for natural language queries

### Data Flow
1. Stock symbol selection (shared across pages via session state)
2. Data loading from vnstock API with caching
3. AI analysis through PandasAI agent
4. Chart generation and export

### Critical Dependencies
**NEVER upgrade pandas or pandasai independently.** The app uses:
- `pandasai==2.3.0` (stable)
- `pandas==1.5.3` (compatible with pandasai 2.x)

PandasAI 3.x has breaking changes and requires different pandas versions.

### Session State Management
Key session variables:
- `api_key` - OpenAI API key
- `stock_data` - Cached financial data
- `selected_symbol` - Currently selected stock symbol
- `symbols_data` - All available symbols (cached)
- `agent` - PandasAI agent instance

### Performance Considerations
- Stock data is cached in `cache/` directory
- Charts exported to `exports/charts/`
- Symbol data loaded once per session
- Visit "Stock Analysis" page first for optimal loading

### Environment Variables
- `OPENAI_API_KEY` - Required for AI functionality
- Optional Docker environment variables in `.env`

### Chart Generation
Charts are generated via PandasAI and saved to `exports/charts/temp_chart.png`. The app detects the latest chart file for display.

### Error Handling
- API key validation on startup
- Graceful handling of vnstock API errors
- PandasAI error recovery with fallback responses