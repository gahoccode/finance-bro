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

# Code formatting and linting (using ruff - replaces black and flake8)
uv run ruff format .    # Format code
uv run ruff check .     # Check for linting issues
uv run ruff check . --fix  # Auto-fix linting issues

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
  - **Fund_Analysis.py** - Vietnamese investment fund analysis with NAV performance and allocation charts
- **src/** - Modular utilities and services (NEW):
  - **core/config.py** - Centralized app configuration and constants
  - **services/vnstock_api.py** - All VnStock API functions (30 centralized, including fund data)
  - **services/chart_service.py** - Chart generation utilities (10 functions, including Fibonacci overlays)
  - **services/data_service.py** - Data transformation utilities
  - **services/fibonacci_service.py** - Fibonacci retracement analysis with SciPy swing detection
  - **services/crewai_service.py** - CrewAI financial health analysis orchestration with multi-agent system
  - **services/financial_analysis_service.py** - Advanced financial analysis functions (DuPont analysis, capital employed, financial leverage)
  - **services/session_state_service.py** - Smart session state management with progressive data loading (v0.2.22+)
  - **services/financial_data_service.py** - Centralized financial data loading with validation and caching (v0.2.22+)
  - **financial_health_crew/** - CrewAI multi-agent financial health analysis system:
    - **crew.py** - Multi-agent crew configuration with 3 specialized agents (data analyst, risk specialist, report writer)
    - **config/agents.yaml** - Agent roles and expertise definitions for Vietnamese market analysis
    - **config/tasks.yaml** - Task definitions for comprehensive financial health assessment
    - **tools/financial_analysis_tool.py** - Custom CrewAI tools for financial data analysis
    - **main.py** - CrewAI crew execution entry point
  - **components/** - Reusable UI components (stock_selector.py, date_picker.py, ui_components.py)
  - **utils/** - General utilities (session_utils.py, validation.py)
- **static/** - CSS styling with custom theme configuration
- **cache/** - Data caching for performance
- **exports/charts/** - Generated chart storage
- **tests/** - Test suite with pytest framework
- **docs/architecture/** - Comprehensive architecture documentation with C4 Model diagrams

### Key Technologies
- **Streamlit** - Web framework (v1.47.0)
- **PandasAI** - AI data analysis (v2.3.0 - stable, compatible with pandas 1.5.3)
- **CrewAI** - Multi-agent AI system (v0.35.8+) for financial health analysis
- **vnstock** - Vietnamese stock market data (v3.2.5)
- **OpenAI API** - LLM for natural language queries and agent communication
- **Google OAuth** - User authentication
- **SciPy** - Scientific computing for Fibonacci swing point detection
- **Altair** - Interactive statistical visualizations with Finance Bro theming

### Data Flow
1. Authentication via Google OAuth (required)
2. Stock symbol selection (shared across pages via session state)
3. Data loading from vnstock API with caching
4. AI analysis through PandasAI agent or CrewAI multi-agent system
5. Chart generation and export

### Critical Dependencies
**NEVER upgrade pandas, pandasai, or quantstats independently.** The app requires:
- **Python** - Exact version `3.10.11` (specified in pyproject.toml)
- `pandasai==2.3.0` (stable)
- `pandas==1.5.3` (compatible with pandasai 2.x)
- `quantstats==0.0.59` (last version compatible with pandas 1.5.3)
- `crewai>=0.35.8` (multi-agent AI system for financial health analysis)
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
st.success("✅ Success message with custom styling")
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

### Modular Architecture (Version 0.2.20+)
The codebase follows a modular architecture pattern with centralized services:

**Import Patterns:**
```python
# Pages import from services
from src.services.vnstock_api import get_stock_data, get_company_overview
from src.services.chart_service import create_technical_chart, create_altair_line_chart
from src.core.config import DEFAULT_SYMBOLS, CACHE_TTL_SETTINGS

# Services are self-contained with @st.cache_data decorators
# Components can be reused across pages
from src.components.stock_selector import render_stock_selector
```

**Development Guidelines:**
- **API Functions**: Add new VnStock functions to `src/services/vnstock_api.py`
- **Charts**: Add new visualizations to `src/services/chart_service.py`
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
- **Complex problem solving**: Use sequential thinking for multi-step problems
- **Ruff for code quality**: Always use ruff for formatting and linting in this project
  - Run `ruff format .` to format code according to project standards
  - Run `ruff check --fix .` to automatically fix linting errors where possible
  - Attempt to fix all errors returned by ruff before committing code
  - Ruff replaces both flake8 (linting) and black (formatting) for this project

**NO Conditional Imports**: 
  - Never use try/except blocks for imports of required packages
  - If a package is in pyproject.toml, import it directly at the top of the file
  - Handle specific errors during usage, not during import

**Download Button Pattern**:
  - Always use single `st.download_button()` for file downloads
  - Never create multi-step processes (generate → download buttons)
  - Generate data directly in memory and pass to download button
  - Example pattern:
    ```python
    # Generate data for download
    data = generate_data_function()
    
    # Single download button - no intermediate steps
    st.download_button(
        label="📊 Download File",
        data=data,
        file_name="filename.png",
        mime="image/png"
    )
    ```
  - Users expect immediate download when clicking download buttons

**Chart Styling Guidelines**:
  - **Clean Line Charts**: Never include `point=True` parameter in Altair line charts
  - Use clean line visualizations without data point markers for professional appearance
  - Consistent with earth-tone styling theme (`#76706C`, `#56524D`, `#2B2523`)
  - Example pattern:
    ```python
    # Correct - clean line without points
    chart = alt.Chart(data).mark_line(
        color='#76706C',
        strokeWidth=2
    )
    
    # Incorrect - avoid point markers
    chart = alt.Chart(data).mark_line(
        point=True  # DO NOT USE
    )
    ```

### Version Management
- Uses semantic versioning (MAJOR.MINOR.PATCH) starting from 0.1.0 (pyproject.toml)
- Patch increment only on actual changes (features/fixes/improvements)
- Date-based versioning with chronological organization
- No empty increments - skip dates without actual changes

### Testing and Quality Assurance
```bash
# Run all quality checks before committing
uv run pytest          # Run tests
uv run ruff check .     # Lint code (replaces flake8)
uv run ruff format .    # Format code (can replace black)
uv run mypy .           # Type checking

# Ruff commands for code quality
uv run ruff check .              # Check for linting issues
uv run ruff check . --fix        # Auto-fix issues where possible
uv run ruff format .             # Apply code formatting
uv run ruff check . --verbose    # Detailed linting output

# Run single test file/function
uv run pytest tests/test_portfolio_optimization.py
uv run pytest tests/test_portfolio_optimization.py::test_function_name

# Available test files
# - tests/test_portfolio_optimization.py - Portfolio optimization tests
# - tests/test_financial_formatting.py - Financial data formatting tests  
# - tests/conftest.py - Test configuration and fixtures
```

### Docker and CI/CD
- GitHub Actions automatically builds and publishes Docker images
- Multi-platform support (linux/amd64, linux/arm64)
- Images published to `ghcr.io/gahoccode/finance-bro` 
- Use `docker-compose up --build` for local development
- Production images available at `ghcr.io/gahoccode/finance-bro:latest`

### CrewAI Financial Health Analysis System

The application includes a sophisticated multi-agent AI system for comprehensive financial health analysis:

**Multi-Agent Architecture:**
- **Financial Data Analyst Agent** - 15+ years experience analyzing Vietnamese public companies, specialized in financial statements analysis
- **Risk Assessment Specialist Agent** - Expert in Vietnamese market dynamics and comprehensive risk evaluation  
- **Report Writer Agent** - Professional financial communications expert for executive-level reports

**Analysis Capabilities:**
- **Current Year Analysis** - Key line items from Income Statement, Balance Sheet, and Cash Flow Statement
- **Multi-Year Trends** - 3-5 year holistic analysis of financial trajectory and patterns
- **Comprehensive Risk Assessment** - Liquidity, leverage, operational, and strategic risk evaluation
- **Executive Reporting** - Professional financial health reports with specific recommendations

**Integration:**
- Seamless integration with session state and financial dataframes
- Cached results for 5-minute TTL to optimize performance
- Vietnamese market-specific expertise and benchmarking

### Architecture Documentation
Comprehensive architecture documentation is available in `docs/architecture/` following C4 Model methodology:
- **System Context** - High-level boundaries and external interactions
- **Container Architecture** - Service boundaries and deployment view  
- **Component Architecture** - Internal module structure and relationships
- **Data Architecture** - Data models, flow, and storage strategies
- **Security Architecture** - Authentication, authorization, and security patterns
- **Quality Attributes** - Performance, scalability, and reliability characteristics

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

### Smart Data Loading Architecture (v0.2.22+)

The application implements a sophisticated smart data loading system that eliminates page dependencies and provides progressive loading with user feedback.

**Core Services:**
- **`src/services/session_state_service.py`** - Centralized session state management with intelligent dependency resolution
- **`src/services/financial_data_service.py`** - Comprehensive financial data loading with validation and caching

**Key Features:**
- **Progressive Loading**: Data loads in stages with real-time progress feedback
- **Dependency Resolution**: Automatic loading of prerequisite data without page dependencies
- **Cache Management**: Intelligent cache invalidation and reuse strategies
- **Error Handling**: Graceful degradation with informative error messages
- **Standalone Pages**: Each page can work independently without requiring users to visit other pages first

**Usage Patterns:**
```python
# For valuation pages - load all required data progressively
loading_result = ensure_valuation_data_loaded(symbol)
if not loading_result["success"]:
    st.error(f"❌ Failed to load valuation data: {loading_result.get('error', 'Unknown error')}")

# For financial analysis pages - load financial statements
financial_result = ensure_financial_data_loaded(symbol, period="year", source="VCI")

# For any page - smart loading based on requirements
result = smart_load_for_page(page_name="valuation", symbol=symbol)
```

**Progressive Loading Best Practices:**
- Always use the appropriate `ensure_*` function for your page type
- Provide user feedback through progress bars and status messages
- Handle loading errors gracefully with fallback options
- Cache data appropriately to minimize API calls
- Use `force_reload=True` parameter when fresh data is required

**Session State Management:**
- Global session state initialization via `init_global_session_state()`
- Stock symbols caching with `ensure_stock_symbols_loaded()`
- Financial data validation via `validate_financial_data()`
- Cache management via `clear_financial_data_cache()`

**Cache Management Strategy:**
- Financial data cached for 5 minutes (TTL) via `@st.cache_data(ttl=300)`
- Stock symbols cached for 1 hour (TTL) via `@st.cache_data(ttl=3600)`
- Smart cache key generation based on parameters (symbol, period, source)
- Manual cache clearing available via `clear_financial_data_cache()`

### Data Sources and APIs
- **vnstock** v3.2.5 - Vietnamese stock data (VCI/TCBS sources)  
  - Stock price data, company information, technical indicators
  - Investment fund data (NAV reports, asset/industry allocations)
  - 57+ Vietnamese investment funds with historical performance
- **OpenAI API** - Required for AI functionality and CrewAI agent communication
- **Google OAuth** - Required for user authentication
- Stock data cached in `cache/` directory for performance
- Do not mix user interface logic with cached or memoized functions; cached functions should only perform pure data computations.
- Always include the scope of impact in your plan: what files and functions will be affected, specify which functions (new and old) belong to what impacted file 