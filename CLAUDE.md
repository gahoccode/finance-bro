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
  - **Technical_Analysis.py** - Advanced technical indicators with pandas-ta integration
  - **Portfolio_Optimization.py** - Modern Portfolio Theory optimization
  - **Screener.py** - Stock screening and filtering functionality
- **static/** - CSS styling with custom theme configuration
- **cache/** - Data caching for performance
- **exports/charts/** - Generated chart storage
- **tests/** - Test suite with pytest framework

### Key Technologies
- **Streamlit** - Web framework (v1.47.0)
- **PandasAI** - AI data analysis (v2.3.0 - stable, compatible with pandas 1.5.3)
- **vnstock** - Vietnamese stock market data (v3.2.5)
- **OpenAI API** - LLM for natural language queries
- **Google OAuth** - User authentication

### Data Flow
1. Authentication via Google OAuth (required)
2. Stock symbol selection (shared across pages via session state)
3. Data loading from vnstock API with caching
4. AI analysis through PandasAI agent
5. Chart generation and export

### Critical Dependencies
**NEVER upgrade pandas, pandasai, or quantstats independently.** The app requires:
- **Python** - Exact version `3.10.11` (specified in pyproject.toml)
- `pandasai==2.3.0` (stable)
- `pandas==1.5.3` (compatible with pandasai 2.x)
- `quantstats==0.0.59` (last version compatible with pandas 1.5.3)
- Uses `uv` for dependency management (recommended over pip)

**Version Compatibility Notes:**
- PandasAI 3.x has breaking changes and requires different pandas versions
- QuantStats 0.0.60+ uses pandas 2.0+ frequency aliases (`ME`, `QE`, `YE`) incompatible with pandas 1.5.3
- QuantStats 0.0.59 uses legacy frequency aliases (`M`, `Q`, `A`) compatible with pandas 1.5.3

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

### Authentication Setup
Requires Google OAuth configuration in `.streamlit/secrets.toml`:
```toml
[auth]
client_id = "your-google-client-id"
client_secret = "your-google-client-secret"
redirect_uri = "http://localhost:8501/oauth2callback"
cookie_secret = "your-random-secret-string"
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"
```

### Theme Configuration
Custom theme is configured in `.streamlit/config.toml` with:
- Earth-toned color palette (`#56524D`, `#2B2523`, `#76706C`)
- Custom chart colors for financial data visualization
- Sequential colors for data progression charts
- Serif font for professional appearance

### Environment Variables
- `OPENAI_API_KEY` - Required for AI functionality
- Optional Docker environment variables in `.env`

### Chart Generation
Charts are generated via PandasAI and saved to `exports/charts/temp_chart.png`. The app detects the latest chart file for display.

### Error Handling
- API key validation on startup
- Graceful handling of vnstock API errors
- PandasAI error recovery with fallback responses

### Development Workflow
- Use **uv** for dependency management over pip (faster and more reliable)
- **Critical**: Never upgrade pandas/pandasai without checking compatibility
- Python exact version `3.10.11` required (no newer versions supported)
- Run `uv sync` after pulling changes to ensure dependency consistency

### Code Style and Architecture Guidelines
- **Function-first approach**: Prioritize functions over classes for simplicity
- **Import organization**: Always place imports at the top of files (never inside try-except blocks)
- **Try-except blocks**: Don't attempt to use try-except blocks when implementing new features on first try, add try-except blocks after the feature is implemented and has passed all tests, if bugs occur, add try-except blocks to fix the bug
- **Documentation requirement**: Document changes for every fix or feature before committing
- **Complex problem solving**: Use sequential thinking for multi-step problems

**NO Conditional Imports**: 
  - Never use try/except blocks for imports of required packages
  - If a package is in pyproject.toml, import it directly at the top of the file
  - Handle specific errors during usage, not during import
 

### Version Management
- Uses semantic versioning (MAJOR.MINOR.PATCH) starting from 0.1.0 (pyproject.toml)
- Patch increment only on actual changes (features/fixes/improvements)
- Date-based versioning with chronological organization
- No empty increments - skip dates without actual changes

### Testing and Quality Assurance
```bash
# Run all quality checks before committing
uv run pytest          # Run tests
uv run black .          # Format code  
uv run flake8           # Lint code
uv run mypy .           # Type checking

# Run single test file/function
uv run pytest tests/test_portfolio_optimization.py
uv run pytest tests/test_portfolio_optimization.py::test_function_name

# Available test files
# - tests/test_portfolio_optimization.py - Portfolio optimization tests
# - tests/conftest.py - Test configuration and fixtures
```

### Docker and CI/CD
- GitHub Actions automatically builds and publishes Docker images
- Multi-platform support (linux/amd64, linux/arm64)
- Images published to `ghcr.io/gahoccode/finance-bro` 
- Use `docker-compose up --build` for local development
- Production images available at `ghcr.io/gahoccode/finance-bro:latest`

### Data Sources and APIs
- **vnstock** v3.2.5 - Vietnamese stock data (VCI/TCBS sources)  
- **OpenAI API** - Required for AI functionality
- **Google OAuth** - Required for user authentication
- Stock data cached in `cache/` directory for performance