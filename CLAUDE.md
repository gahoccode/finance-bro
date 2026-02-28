# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Application

```bash
# With uv (recommended)
uv run streamlit run app.py
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

# Run tests (pytest available in dev dependencies)
uv run pytest

# Code formatting and linting (using ruff - replaces black and flake8)
uv run ruff format .    # Format code
uv run ruff check .     # Check for linting issues
uv run ruff check . --fix  # Auto-fix linting issues

# Type checking
uv run mypy .
```

### Key Technologies

- **Streamlit** - Web framework (v1.49.0+)
- **CrewAI** - Multi-agent AI system (v0.35.8+) for financial health analysis
- **vnstock** - Vietnamese stock market data (v3.2.6+)
- **OpenAI API** - LLM for natural language queries and agent communication
- **Google OAuth** - User authentication
- **SciPy** - Scientific computing for Fibonacci swing point detection
- **Plotly** - Professional financial charting with interactive candlestick charts (v5.17.0+)
- **Altair** - Interactive statistical visualizations with Finance Bro theming

**Standalone AI Component:**

- **PandasAI** - AI data analysis (v2.3.0 - stable, compatible with pandas 2.2.0+) now available as separate standalone application

### Critical Dependencies

**NEVER upgrade pandas, pandasai, or quantstats independently.** The app requires:

- **Python** - Version `3.12+` (specified in pyproject.toml) with NumPy 2.0 compatibility
- `pandas==2.2.0+` (compatible with NumPy 2.0)
- `quantstats==0.0.62` (compatible with pandas 2.2.0+ and NumPy 2.0)
- `crewai>=0.35.8` (multi-agent AI system for financial health analysis)
- Uses `uv` for dependency management (recommended over pip)

**Standalone PandasAI Component:**

- `pandasai==2.3.0` (stable) - Available as separate standalone application
- Compatible with pandas 2.2.0+ and NumPy 2.0
- Natural language financial analysis capabilities
- Can be run independently from main application

**Version Compatibility Notes:**

- PandasAI 3.x has breaking changes and requires different pandas versions
- QuantStats 0.0.62+ supports pandas 2.0+ frequency aliases (`ME`, `QE`, `YE`) compatible with pandas 2.2.0+
- Python 3.12+ provides enhanced performance and NumPy 2.0 compatibility for improved array operations
- **Standalone PandasAI**: Uses pandasai==2.3.0 for stability, separate from main app dependencies

### Session State Management

Key session variables:

- `api_key` - OpenAI API key
- `stock_data` - Cached financial data
- `selected_symbol` - Currently selected stock symbol
- `symbols_data` - All available symbols (cached)
- `agent` - CrewAI agent instance (note: PandasAI agent removed, now standalone)

### Performance Considerations

- Stock data is cached in `cache/` directory
- Charts exported to `exports/charts/`
- Symbol data loaded once per session
- Visit "Stock Analysis" page first for optimal loading

### Financial Data Alignment

- Financial statements have `yearReport` column for temporal alignment
- When working with multiple financial datasets (Balance Sheet, Income Statement, Cash Flow, Ratios), always align on the `yearReport` column to ensure data consistency
- Avoid mixing financial data from different years as this leads to meaningless analysis
- Use `yearReport` column to filter and align datasets before performing calculations like WACC
- Example: Ensure debt data (Balance Sheet) and market cap data (Ratios) are from the same year for accurate capital structure analysis

### Temporal Financial Data Alignment Pattern

**CRITICAL REQUIREMENT**: All financial statements must be sorted by `yearReport` in ascending order immediately after loading to ensure proper temporal alignment across Balance Sheet, Income Statement, Cash Flow, and Ratios.

**Required Implementation Pattern**:

```python
# Sort all financial statements by yearReport in ascending order for proper temporal alignment
if not balance_sheet.empty and 'yearReport' in balance_sheet.columns:
    balance_sheet = balance_sheet.sort_values('yearReport', ascending=True)
if not income_statement.empty and 'yearReport' in income_statement.columns:
    income_statement = income_statement.sort_values('yearReport', ascending=True)
if not cash_flow.empty and 'yearReport' in cash_flow.columns:
    cash_flow = cash_flow.sort_values('yearReport', ascending=True)
if not ratios.empty and 'yearReport' in ratios.columns:
    ratios = ratios.sort_values('yearReport', ascending=True)
```

**Benefits**:

- Guaranteed chronological alignment across all financial statements
- Reliable `iloc[-1]` for latest year data, `iloc[0]` for earliest year data
- Eliminates temporal misalignment issues in WACC and valuation calculations
- Sort once, use consistently throughout analysis
- Performance optimization: prevents multiple sorting operations

**Usage Guidelines**:

- Apply immediately after loading financial statements from session state
- Required for any page performing temporal financial analysis
- Enables consistent indexing patterns across the application
- Prevents data alignment bugs between different financial statement years

**Reference Implementation**: See Valuation.py lines 108-116 for correct pattern usage.

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

### Custom CSS Styling

The application uses a centralized CSS component system for consistent theming:

- **Success alerts**: Light gray background (`#D4D4D4`) with earth-tone text (`#56524D`)
- **Markdown containers**: Tertiary color background (`#76706C`)
- **Alert targeting**: Multiple CSS selectors ensure compatibility across Streamlit versions
- **Component-based**: Centralized in `src/components/ui_components.py` for reusability

**Reusable CSS Component:**

```python
from src.components.ui_components import inject_custom_success_styling

# Apply custom styling for all st.success() calls
inject_custom_success_styling()

# Now all st.success() calls will use consistent earth-tone styling
st.success("Success message with custom styling")
```

**Implementation Pattern:**

- Import the CSS component function from `src.components.ui_components`
- Call `inject_custom_success_styling()` after `st.set_page_config()` in pages
- For component functions, call before `st.success()` usage
- All success alerts across the application now use consistent styling

### Environment Variables

- `OPENAI_API_KEY` - Required for AI functionality
- Optional Docker environment variables in `.env`

### Chart Generation

Charts are generated via Plotly, Altair, and mplfinance with export capabilities. Standalone PandasAI application handles AI-generated charts separately.

### Error Handling

- API key validation on startup
- Graceful handling of vnstock API errors
- CrewAI error recovery with fallback responses
- Standalone PandasAI error handling managed separately

**Development Guidelines:**

- **API Functions**: Add new VnStock functions to `src/services/vnstock_api.py`
- **Charts**: Add new visualizations to `src/services/chart.py`
- **CrewAI Agents**: Add new financial analysis agents to `src/financial_health_crew/`
- **Configuration**: Update constants in `src/core/config.py`
- **UI Components**: Create reusable widgets in `src/components/`
- **Page Logic**: Focus pages on user interaction, import from services
- **No Code Duplication**: All repeated functionality centralized in src/

### Code Style and Architecture Guidelines

- **Function-first approach**: Prioritize functions over classes for simplicity
- **Import organization**: Always place imports at the top of files (never inside try-except blocks)
- **Try-except blocks**: Don't attempt to use try-except blocks when implementing new features on first try, add try-except blocks after the feature is implemented and has passed all tests, if bugs occur, add try-except blocks to fix the bug
- **Documentation requirement**: Document changes for every fix or feature before committing

- **Ruff for code quality**: Always use ruff for formatting and linting in this project
  - Run `ruff format .` to format code according to project standards
  - Run `ruff check --fix .` to automatically fix linting errors where possible
  - Attempt to fix all errors returned by ruff before committing code
  - Ruff replaces both flake8 (linting) and black (formatting) for this project

### Docker and CI/CD

- GitHub Actions automatically builds and publishes Docker images
- Multi-platform support (linux/amd64, linux/arm64)
- Images published to `ghcr.io/gahoccode/finance-bro`
- Use `docker-compose up --build` for local development
- Production images available at `ghcr.io/gahoccode/finance-bro:latest`

### VnStock Data Scale Conventions

**IMPORTANT**: VnStock API returns price data in thousands of VND, not individual VND.

**Price Data Scaling:**

- Stock prices from vnstock are in thousands of VND (e.g., 64.5 = 64,500 VND)
- **Always multiply by 1,000 to get original scale for calculations**
- Example: `actual_price = api_price * 1000`

**Financial Data Scaling:**

- Financial statement data (Balance Sheet, Income Statement, etc.) are in original scale (raw VND)
- Market cap calculations: `shares × (price_from_api × 1000)`

**Display Formatting:**

- Use `format_financial_display()` function for all display formatting
- Perform calculations with original scale values (raw VND)
- Apply formatting only for display purposes, never for calculations

### Data Sources and APIs

- **OpenAI API** - Required for AI functionality and CrewAI agent communication
- **Google OAuth** - Required for user authentication
- Stock data cached in `cache/` directory for performance
- Always include the scope of impact in your plan and CHANGELOG.md: what files and functions will be affected, specify which functions (new and old) belong to what impacted file
- Run ruff check and format to check python errors
- use @Reference/ as examples for the implementation. Do not check for errors or formatting issues in this directory
