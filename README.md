# Finance Bro - AI Stock Analysis

🚀 **Natural language interface for Vietnamese stock market analysis** Interact with your financial statements in natural language. Get answers to your questions about any financial statement of listed stocks in Vietnam with a friendly finance bro. He's an introvert so please make your questions short and to the point. 

## Features

- 📊 **Vietnamese Stock Data** - Load financial data using Vnstock (VCI/TCBS sources)
- 🤖 **AI Chat Interface** - Natural language queries about financial metrics with PandasAI integration
- 💬 **Interactive Analysis** - Real-time conversation with AI analyst including file upload support
- 📈 **Advanced Technical Analysis** - Interactive price charts with 75+ QuantStats metrics, professional tearsheets, and comprehensive technical indicators (RSI, MACD, Bollinger Bands, OBV, ADX) with robust error handling
- 🎯 **Intelligent Stock Screener** - Multi-criteria filtering with 6 advanced filters (Beta, Alpha, Financial Health, etc.)
- 💼 **Portfolio Optimization** - Modern Portfolio Theory, Hierarchical Risk Parity, and risk analysis with riskfolio-lib
- 🏢 **Comprehensive Company Analysis** - Ownership structure, management team, subsidiaries, and foreign transaction analysis
- 📊 **Professional Visualizations** - Interactive charts with Plotly, Altair, and custom styling
- 🔐 **Secure Authentication** - Google OAuth integration with API key management

## Quick Start

### Prerequisites

- Python >= 3.12
- OpenAI API key
- Google Cloud Console account (for OAuth setup)

### Google OAuth Setup (Required)

Before running the app, you need to set up Google OAuth authentication:

1. **Create Google OAuth Credentials:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable Google+ API
   - Go to Credentials → Create Credentials → OAuth 2.0 Client IDs
   - Configure OAuth consent screen
   - Add authorized redirect URI: `http://localhost:8501/oauth2callback` or 'https://your-app-domain.com/oauth2callback' if you are deploying to production with a custom domain
   - Download credentials JSON file

2. **Configure authentication:**
   ```bash
   # Copy the example secrets file
   cp .streamlit/secrets.example.toml .streamlit/secrets.toml
   
   # Edit .streamlit/secrets.toml and add your Google OAuth credentials
   # Replace the placeholder values with your actual credentials
   ```

3. **Update secrets.toml with your credentials:**
   ```toml
   [auth]
   redirect_uri = "http://localhost:8501/oauth2callback"
   cookie_secret = "your-random-secret-string-here"
   client_id = "your-google-client-id.apps.googleusercontent.com"
   client_secret = "your-google-client-secret"
   server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"
   ```

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/finance-bro.git
cd finance-bro
```

2. **Install dependencies using uv (recommended):**
```bash
uv sync
```

Or using pip:
```bash
pip install -r requirements.txt
```

3. **Set your OpenAI API key:**
```bash
export OPENAI_API_KEY="your-openai-api-key"
```

4. **Run the application:**
```bash
uv run streamlit run app.py
```

Or:
```bash
streamlit run app.py
```

5. **Open your browser** and navigate to `http://localhost:8501`

## User Flow

### Optimal User Experience Flow

**Finance Bro** is designed with a specific user flow for the best experience. Follow these steps to get the most out of the application:

### Step 1: Authentication & Homepage
1. **🔐 Google Login**: Start by logging in with your Google account on the authentication page
2. **🏠 Homepage Navigation**: After login, you'll be directed to the Finance Bro homepage
3. **📊 Stock Symbol Selection**: On the homepage, use the searchable dropdown to select a Vietnamese stock symbol
   - **Critical Step**: This stock symbol selection is essential - it will be shared across all analysis pages
   - **Search Feature**: Type to search through all available Vietnamese stock symbols
   - **Persistence**: Your selected symbol will be available throughout your session

### Step 2: Direct Navigation to Any Analysis Page (New Enhanced Flow)

**Enhanced Experience (v0.2.22+)**: With smart data loading, you can now navigate directly to any analysis page without dependencies:

4. **🚀 Choose Your Analysis Path**: From the homepage, you can now directly access any analysis tool:
   - **📊 Stock Analysis**: AI chat interface with natural language financial queries
   - **💰 Valuation**: Comprehensive valuation analysis with pre-loaded data
   - **📈 Price Analysis**: Interactive price charts with 75+ QuantStats metrics
   - **📊 Technical Analysis**: Advanced technical indicators with heating stock discovery
   - **🏢 Company Overview**: Company profiles with ownership structure analysis
   - **💼 Portfolio Optimization**: Modern Portfolio Theory and risk analysis
   - **🎯 Stock Screener**: Multi-criteria stock filtering with advanced metrics

5. **⚡ Smart Data Loading**: Each page now intelligently loads required data with progress feedback:
   - **Automatic Pre-loading**: Data loads progressively with real-time status updates
   - **No Page Dependencies**: Each page works independently without requiring visits to other pages
   - **Intelligent Caching**: Data is cached smartly to optimize performance across sessions
   - **Error Handling**: Graceful degradation with informative error messages

### Step 3: Traditional Stock Analysis Page (Optional)
6. **📈 Enhanced Stock Analysis**: The Stock Analysis page remains available for:
   - **AI Chat Interface**: Natural language queries about financial metrics
   - **Sample Questions**: Quick access to common analysis questions
   - **File Upload Support**: Upload your own financial data for analysis
   - **Comprehensive Data Loading**: Still the best place to load all data for optimal performance

### Step 4: Explore Advanced Analysis Tools
7. **🎯 Specialized Analysis**: Access sophisticated analysis tools:
   - **📊 Technical Analysis**: Professional technical indicators with automatic stock discovery
   - **💼 Portfolio Optimization**: Hierarchical Risk Parity and Modern Portfolio Theory
   - **🏢 Company Overview**: Ownership structure, management team, and foreign transaction analysis
   - **🎯 Stock Screener**: Multi-criteria filtering with quick presets and advanced metrics

### Recommended Setup for Best Experience

**🎨 Custom Theme for Best Appearance**: This app is designed with a custom color scheme for optimal visual experience.

**How to enable custom theme:**
1. Click the hamburger menu (☰) in the top-right corner
2. Select "Settings"
3. Under "Theme", choose "Custom"
4. The app will display with the optimized color scheme and chart styling

**Alternative**: Light mode is also supported if you prefer standard Streamlit styling.

### Why This Enhanced Flow Matters

**🎯 Smart Data Loading (v0.2.22+)**: 
- **Progressive Loading**: Data loads in stages with real-time progress feedback
- **No Page Dependencies**: Each page works independently without requiring users to visit other pages first
- **Intelligent Caching**: Smart cache invalidation and reuse strategies optimize performance
- **Graceful Degradation**: Error handling with informative messages when data loading fails

**📊 Enhanced User Experience**: 
- **Direct Navigation**: Users can go directly to any analysis page from the homepage
- **Real-time Feedback**: Progress bars and status messages keep users informed during data loading
- **Flexible Workflow**: No mandatory path - users choose their preferred analysis approach
- **Consistent Performance**: Smart caching ensures fast loading regardless of navigation path

**🚀 Technical Benefits**:
- **Modular Architecture**: Clean separation between data loading and presentation logic
- **Scalable Design**: Easy to add new analysis pages without dependencies
- **Maintainable Code**: Centralized data services reduce code duplication
- **Better Error Recovery**: Individual page failures don't affect other parts of the application

**🔄 Backwards Compatibility**: 
- **Existing Flow Preserved**: Traditional users can still follow the original Stock Analysis → Other Pages flow
- **Progressive Enhancement**: New features enhance rather than replace existing functionality
- **Performance Improvements**: Even users following the traditional flow benefit from smart loading optimizations

## Example Questions

- "What is the return on invested capital (ROIC) trend?"
- "Analyze the dividend yield and payout ratio trends"
- "What is the company's debt-to-equity ratio?"
- "Compare revenue growth across years"
- "What are the key financial strengths and weaknesses?"

## 📊 Technical Analysis Features

**Finance Bro** includes a comprehensive Technical Analysis page that automatically discovers and analyzes "heating up" stocks from the Vietnamese market using advanced technical indicators.

### Key Features

**🔥 Automatic Stock Discovery**
- Scans entire Vietnamese stock market (HOSE, HNX, UPCOM exchanges)
- Identifies stocks with "Overheated in previous trading session" signals
- Displays comprehensive market data including industry, market cap, and trading metrics

**📈 Advanced Technical Indicators**
- **RSI (Relative Strength Index)**: Momentum oscillator for overbought/oversold conditions
- **MACD (Moving Average Convergence Divergence)**: Trend-following momentum indicator
- **Bollinger Bands**: Volatility bands for price channel analysis
- **OBV (On-Balance Volume)**: Volume flow indicator for price movement validation
- **ADX (Average Directional Index)**: Trend strength measurement

**🎯 Interactive Candlestick Charts**
- Professional mplfinance integration with custom Finance Bro theme
- Multi-panel layouts with synchronized indicators
- Configurable time intervals (Daily, Weekly, Monthly)
- Earth-toned color scheme for professional analysis

**⚙️ Robust Error Handling**
- Comprehensive pandas-ta integration with graceful error recovery
- Individual indicator validation with specific failure explanations
- Enhanced data validation for optimal ADX calculation (30+ data points required)
- Transparent warning system explaining exactly why indicators might fail
- Optimized date ranges (90 days for daily analysis) for reliable calculations

### Technical Implementation Highlights

**Production-Ready Error Handling**
- Fixed `TypeError: 'NoneType' object is not subscriptable` from pandas-ta None returns
- Resolved `ValueError: zero-size array to reduction operation maximum` in ADX calculations
- Safe chart creation with fallback mechanisms for partial indicator availability
- Professional user feedback with success/failure indicator reporting

**Performance Optimizations**
- Intelligent data validation before indicator calculation
- Graceful degradation when indicators fail while maintaining core functionality
- Date range optimization for sufficient technical analysis data
- Cached indicator calculations with TTL for better performance

### Usage Notes

**Data Requirements**
- Minimum 20 data points required for most indicators
- ADX requires 30+ data points for reliable calculation
- Daily interval provides 90 days of data for comprehensive analysis
- Weekly and monthly intervals provide extended historical coverage

**Error Recovery**
- App continues functioning with available indicators if some calculations fail
- Clear warnings explain specific reasons for any indicator failures
- Comprehensive fallback system maintains professional user experience
- All error handling designed for production stability

## ⚠️ Critical: Package Compatibility

**IMPORTANT:** This project uses specific versions of pandas and pandasai that are carefully matched for compatibility. **DO NOT** upgrade these packages independently without testing.

### Why Version Compatibility Matters

- **pandasai v2.3.0** requires **pandas v2.2.0+** (compatible with NumPy 2.0)
- **pandasai v3.x** (beta) has breaking changes and schema issues
- Mismatched versions cause:
  - `TypeError: sequence item 0: expected str instance, tuple found`
  - `'DataFrame' object has no attribute 'schema'`
  - Agent initialization failures

### Tested Compatible Versions

✅ **WORKING COMBINATION:**
- `pandasai==2.3.0` (stable)
- `pandas>=2.2.0,<3.0.0` (compatible with pandasai 2.x and NumPy 2.0)
- `numpy>=2.0.0,<3.0.0` (enhanced performance with NumPy 2.0)
- `quantstats>=0.0.77` (compatible with pandas 2.2.0+ and NumPy 2.0)
- Built-in OpenAI LLM (no separate extension needed)

❌ **AVOID:**
- `pandasai>=3.0.0` (beta, unstable)
- `pandas<2.2.0` (incompatible with NumPy 2.0 and current dependencies)
- `numpy<2.0.0` (missing performance improvements and compatibility)
- `quantstats<0.0.77` (incompatible with pandas 2.2.0+)
- `pandasai-openai` extension (not needed in v2.3.0)

### Critical QuantStats Compatibility
**NEVER upgrade quantstats independently.** The app uses:
- **QuantStats v0.0.77+** - Compatible with pandas 2.2.0+ and NumPy 2.0 frequency aliases (`ME`, `QE`, `YE`)
- **Python 3.12+ Benefits**: Enhanced performance, better error handling, and NumPy 2.0 compatibility
- **Solution**: Versions pinned in pyproject.toml and requirements.txt to maintain compatibility

### If You Need to Upgrade

1. **Test in a separate environment first**
2. **Check pandasai release notes** for breaking changes
3. **Update both packages together**, not individually
4. **Run the app thoroughly** before deploying

## Technology Stack

- **Frontend:** Streamlit v1.49.0+ with Google OAuth authentication
- **AI Engine:** PandasAI v2.3.0 (stable) with OpenAI GPT integration
- **Stock Data:** Vnstock v3.2.6+ (VCI/TCBS sources for Vietnamese market)
- **Data Processing:** Pandas v2.2.0+ with NumPy v2.0.0+ (enhanced performance)
- **Financial Analysis:** QuantStats v0.0.77+ (75+ performance metrics and tearsheets)
- **Portfolio Optimization:** PyPortfolioOpt (Modern Portfolio Theory, Efficient Frontier)
- **Risk Analysis:** riskfolio-lib v7.0.1+ (Hierarchical Risk Parity, advanced risk metrics)
- **Technical Analysis:** pandas-ta for 150+ technical indicators with robust error handling
- **Visualizations:** Plotly v5.17.0+ (professional financial charts), Altair v5.5.0+, mplfinance for interactive charts
- **Multi-Agent AI:** CrewAI v0.35.8+ for collaborative financial analysis
- **Authentication:** Authlib v1.3.2+ for Google OAuth integration

## Future Refactor: PandasAI 3.x Migration

### Target Dependencies (PandasAI 3.x)
For future migration to PandasAI 3.x, the following dependencies will be required:

```toml
dependencies = [
    "numpy>=1.26.4",
    "pandasai>=3.0.0b2",
    "pandasai-openai>=0.1.6",
    "streamlit>=1.47.1",
    "vnstock>=3.2.6",
]
```

### Migration Considerations
- **Breaking Changes**: PandasAI 3.x has significant API changes from 2.x
- **Schema Changes**: New dataframe schema handling required
- **Extension System**: Separate pandasai-openai package needed
- **Testing Required**: Full regression testing needed before migration
- **Compatibility**: Verify vnstock integration with new pandas versions

## Session State Management

Finance Bro uses Streamlit's `st.session_state` for comprehensive data sharing and persistence across pages. This ensures a seamless user experience where data, settings, and user interactions are maintained throughout the session.

### Global Session State Variables

**Authentication & API**
- `api_key` - OpenAI API key for AI functionality
- `stock_symbol` - Currently selected stock symbol (shared across all pages)

**Data Caching & Performance**
- `stock_symbols_list` - Cached list of all available Vietnamese stock symbols
- `symbols_df` - Full DataFrame with stock symbols and company names for performance
- `last_period` - Previously selected period (year/quarter) for change detection

**Date Range Management**
- `analysis_start_date` - Global start date for data analysis (default: 2024-01-01), shared across all analysis pages
- `analysis_end_date` - Global end date for data analysis (default: today-1), shared across all analysis pages  
- `date_range_changed` - Boolean flag to trigger cache invalidation when date range changes

### Page-Specific Session State Variables

#### Stock Analysis Page (bro.py)
**Data Storage**
- `dataframes` - AI-optimized financial dataframes with Quarter column names for better PandasAI queries
- `display_dataframes` - Original financial dataframes with lengthReport for proper display formatting
- `uploaded_dataframes` - User-uploaded CSV/Excel files for AI analysis
- `messages` - Chat message history for conversation continuity

**AI Agent Management**
- `agent` - PandasAI agent instance for financial analysis
- `agent_key` - Cache key for intelligent agent recreation when data changes
- `pending_question` - Queued question from sidebar for processing

#### Stock Price Analysis Page
**Price & Returns Data**
- `stock_price_data` - Historical stock price data with caching
- `stock_returns` - Calculated stock returns for QuantStats analysis

#### Portfolio Optimization Page
**Portfolio Data**
- `portfolio_returns` - Stock returns data shared across all portfolio tabs
- `weights_max_sharpe` - Max Sharpe portfolio weights for cross-tab sharing
- `weights_min_vol` - Min Volatility portfolio weights
- `weights_max_utility` - Max Utility portfolio weights

**Portfolio Strategy Selection**
- `portfolio_strategy_choice` - Master control for portfolio strategy selection across all tabs (new in v0.2.16)

#### Technical Analysis Page
**Analysis Configuration**
- `ta_interval` - Selected time interval for technical analysis (1D, 1W, 1M)

#### DuPont Analysis Page
**Financial Analysis Data**
- `dupont_analysis` - Stored DuPont analysis results for persistence across page interactions
- `capital_employed` - Capital employed calculation results
- `dfl_analysis` - Degree of Financial Leverage analysis results

#### Financial Health Report Page  
**Report Management**
- `health_report` - Generated financial health report content from CrewAI system
- `generate_report` - Boolean flag to trigger report generation

#### Chart & Visualization Services
**Chart State Management**
- `fibonacci_summary` - Fibonacci retracement analysis results keyed by date
- `stock_price_data` - Historical stock price data cached from vnstock API

#### UI Components (Dynamic Keys)
**Financial Display Options**
- `{unique_key}_financial_display_unit` - Display unit selection for financial formatting (billions/millions/original)
  - Examples: `dupont_display_financial_display_unit`, `portfolio_display_financial_display_unit`

**Date Picker Components (Dynamic Keys)**
- `{key_prefix}_start_date` - Start date for date range pickers
- `{key_prefix}_end_date` - End date for date range pickers  
- `{key_prefix}_date_range_changed` - Boolean flag for date range change detection
  - Examples: `analysis_start_date`, `portfolio_start_date`, `screener_start_date`

#### Screener Page
**Screening Data**
- `screener_data` - Filtered stock results from screening criteria

**Filter Presets (Dynamic Keys)**
- `preset_industries` - Selected industries for quick filter presets
- `preset_market_cap` - Market cap filter preset activation
- `preset_roe` - ROE filter preset activation
- `preset_roa` - ROA filter preset activation
- `preset_dividend` - Dividend yield filter preset activation
- `preset_beta` - Beta risk filter preset activation
- `preset_financial_health` - Financial health filter preset activation
- `preset_stock_rating` - Stock rating filter preset activation
- `auto_run_screener` - Automatic screener execution trigger

### Session State Architecture Benefits

**Data Consistency**
- Single source of truth for stock symbol selection across all pages
- **Consistent date ranges**: Global start/end dates (today-1 default) shared across Stock Price Analysis and Portfolio Optimization pages
- Portfolio strategy selection shared between Dollar Allocation, Report, and Risk Analysis tabs
- Financial data loaded once and reused across different analysis tools

**Performance Optimization**
- Stock symbols loaded once in Stock Analysis page and cached for entire session
- Financial dataframes cached to avoid repeated API calls
- **Smart cache invalidation**: Automatic cache refresh when date ranges change across pages
- Agent recreation only when data actually changes

**User Experience**
- Seamless navigation between pages without data loss
- **Synchronized date selection**: Date changes in one page automatically apply to all analysis pages
- Chat history persistence during analysis sessions
- Filter presets remember user preferences across screening sessions

**Memory Management**
- Intelligent caching with change detection to prevent unnecessary data reloading
- Cleanup mechanisms for dynamic preset keys to prevent memory bloat

### Session State Flow

1. **App Entry (app.py)**: Loads API key, stock symbols list, and handles symbol selection
2. **Stock Analysis (bro.py)**: Creates comprehensive data cache and AI agent
3. **Other Pages**: Access shared data from session state for analysis
4. **Cross-Page Navigation**: All data persists seamlessly across page switches

This architecture ensures optimal performance while maintaining a professional user experience comparable to institutional financial analysis tools.

## Project Structure

```
finance-bro/
├── app.py                     # Main entry point with auth & navigation
├── pages/                     # Multi-page Streamlit application
│   ├── bro.py                # Main AI chat interface (Stock Analysis)
│   ├── Stock_Price_Analysis.py  # Price charts & QuantStats tearsheets
│   ├── Technical_Analysis.py # Advanced technical indicators with heating stocks
│   ├── Company_Overview.py   # Company profiles & ownership
│   ├── Portfolio_Optimization.py # Modern Portfolio Theory & HRP
│   ├── Screener.py           # Stock screening & filtering
│   └── Fund_Analysis.py      # Vietnamese investment fund analysis
├── src/                      # Modular utilities and services
│   ├── core/
│   │   └── config.py         # Centralized app configuration
│   ├── services/
│   │   ├── vnstock_api.py    # VnStock API functions (30+ functions)
│   │   ├── chart_service.py  # Chart generation utilities (10+ functions)
│   │   ├── data_service.py   # Data transformation utilities
│   │   ├── fibonacci_service.py # Fibonacci retracement analysis
│   │   ├── crewai_service.py # CrewAI financial health analysis
│   │   ├── financial_analysis_service.py # Advanced financial analysis
│   │   ├── session_state_service.py # Smart session state management
│   │   └── financial_data_service.py # Centralized financial data loading
│   ├── financial_health_crew/ # CrewAI multi-agent system
│   │   ├── crew.py          # Multi-agent coordination
│   │   ├── main.py          # Entry point for analysis
│   │   ├── config/           # Agent and task definitions
│   │   └── tools/           # Custom analysis tools
│   ├── components/
│   │   ├── stock_selector.py # Stock selection UI component
│   │   ├── date_picker.py    # Date range picker component
│   │   └── ui_components.py  # Reusable UI components
│   └── utils/
│       ├── session_utils.py  # Session state management
│       └── validation.py     # Data validation utilities
├── static/
│   └── style.css            # Custom CSS styling
├── .streamlit/              # Streamlit configuration
│   ├── config.toml          # Custom theme & colors
│   └── secrets.example.toml # OAuth configuration template
├── cache/                   # Data caching for performance
├── exports/                 # Chart and file exports
│   └── charts/              # Generated chart storage
├── tests/                   # Test suite with pytest framework
│   ├── conftest.py          # Test configuration and fixtures
│   └── test_portfolio_optimization.py # Portfolio optimization tests
├── .github/
│   └── workflows/
│       └── docker-publish.yml # CI/CD Docker publishing
├── .claude/                 # Claude Code configuration
│   ├── commands/            # Custom commands
│   └── settings.local.json  # Local Claude settings
├── requirements.txt         # Python dependencies
├── pyproject.toml          # Project configuration (Python 3.12+)
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose configuration
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore patterns
├── CHANGELOG.md            # Version history
├── CLAUDE.md               # AI assistant instructions
└── README.md               # Project documentation
```

## Docker Deployment

### Using Pre-built Image from GitHub Container Registry

**Pull and run the latest image:**

**macOS/Linux:**
```bash
docker run -p 8501:8501 \
  -e OPENAI_API_KEY=your_openai_api_key \
  -v $(pwd)/exports:/app/exports \
  -v $(pwd)/cache:/app/cache \
  -v $(pwd)/.streamlit:/app/.streamlit \
  ghcr.io/gahoccode/finance-bro:latest
```

**Windows Command Prompt:**
```cmd
docker run -p 8501:8501 -e OPENAI_API_KEY=your_openai_api_key -v %cd%/exports:/app/exports -v %cd%/cache:/app/cache -v %cd%/.streamlit:/app/.streamlit ghcr.io/gahoccode/finance-bro:latest
```

**Windows PowerShell:**
```powershell
docker run -p 8501:8501 `
  -e OPENAI_API_KEY=your_openai_api_key `
  -v ${PWD}/exports:/app/exports `
  -v ${PWD}/cache:/app/cache `
  -v ${PWD}/.streamlit:/app/.streamlit `
  ghcr.io/gahoccode/finance-bro:latest
```

**Note:** The `$(pwd)`, `%cd%`, and `${PWD}` commands automatically get your current working directory. For example, if you're in `/home/user/finance-bro`, these resolve to that path.

**Or use with docker-compose:**
```yaml
services:
  finance-bro:
    image: ghcr.io/gahoccode/finance-bro:latest
    ports:
      - "8501:8501"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./exports:/app/exports
      - ./cache:/app/cache
    env_file:
      - .env
```

### Quick Start with Docker

#### Using Docker Compose (Recommended)

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/finance-bro.git
cd finance-bro
```

2. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

3. **Build and run with Docker Compose:**
```bash
docker-compose up --build
```

4. **Access the application:**
Open your browser and navigate to `http://localhost:8501`

#### Using Docker CLI

1. **Build the Docker image:**
```bash
docker build -t finance-bro .
```

2. **Run the container:**
```bash
docker run -p 8501:8501 \
  -e OPENAI_API_KEY=your_openai_api_key \
  -v $(pwd)/exports:/app/exports \
  -v $(pwd)/cache:/app/cache \
  finance-bro
```

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# Copy the template
cp .env.example .env

# Edit .env and add your OpenAI API key
# Required - Get from https://platform.openai.com/api-keys
OPENAI_API_KEY=your_openai_api_key_here

# Optional - Usually not needed for local development
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
LOG_LEVEL=INFO
```

**Important:** You must set your `OPENAI_API_KEY` in the `.env` file before running Docker. The application won't work without it.

### Docker Commands Reference

```bash
# Build the image
docker build -t finance-bro .

# Run in development mode
docker-compose up

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop containers
docker-compose down

# Remove containers and volumes
docker-compose down -v
```

### Volume Mounting

The Docker setup includes volume mounting for:
- `./exports:/app/exports` - Persistent storage for generated charts and exports
- `./cache:/app/cache` - Persistent cache for faster data loading

### Production Considerations

For production deployment:

1. **Use a reverse proxy** (nginx, traefik) for SSL termination
2. **Set resource limits** in docker-compose.yml
3. **Use environment-specific configurations**
4. **Monitor container health** with the built-in health check

Example production docker-compose.yml additions:
```yaml
# Add to services.finance-bro in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 1G
      cpus: "1.0"
  restart_policy:
    condition: on-failure
    delay: 5s
    max_attempts: 3
```

### Automated Publishing with GitHub Actions

This project includes automated Docker image publishing to GitHub Container Registry (GHCR) via GitHub Actions.

#### How It Works

- **On push to main/master**: Builds and publishes `latest` tag
- **On version tags** (e.g., `v1.0.0`): Builds and publishes versioned tags
- **On pull requests**: Builds image for testing (doesn't publish)
- **Multi-platform**: Builds for both `linux/amd64` and `linux/arm64`

#### Available Image Tags

- `ghcr.io/gahoccode/finance-bro:latest` - Latest stable version
- `ghcr.io/gahoccode/finance-bro:main` - Latest from main branch
- `ghcr.io/gahoccode/finance-bro:v1.0.0` - Specific version tags

#### Manual Publishing

To manually publish a new version:

```bash
# Create and push a version tag
git tag v1.0.0
git push origin v1.0.0

# GitHub Actions will automatically build and publish
```

#### Local Development vs Production

**For local development:**
```bash
# Build locally
docker-compose up --build
```

**For production deployment:**
```bash
# Use pre-built image
docker run -p 8501:8501 -e OPENAI_API_KEY=your_key ghcr.io/gahoccode/finance-bro:latest
```

## Dependencies

### Core Dependencies
- `pandasai==2.3.0` - AI-powered data analysis
- `pandas>=2.2.0,<3.0.0` - Data manipulation with NumPy 2.0 compatibility
- `numpy>=2.0.0,<3.0.0` - Enhanced numerical computing with NumPy 2.0
- `vnstock>=3.2.6` - Vietnamese stock data (VCI/TCBS sources)
- `openai>=1.61.0` - OpenAI API client
- `streamlit>=1.49.0` - Web application framework with OAuth support
- `python-dotenv==1.0.1` - Environment variable management

### Financial Analysis
- `quantstats>=0.0.77` - Performance analytics and tearsheets (75+ metrics)
- `pyportfolioopt>=1.5.6` - Modern Portfolio Theory optimization
- `riskfolio-lib>=7.0.1` - Advanced risk analysis and HRP
- `mplfinance>=0.12.10b0` - Financial data visualization

### Visualization & UI
- `plotly>=5.17.0` - Professional financial charting with interactive candlestick charts
- `altair>=5.5.0` - Interactive statistical visualizations  
- `vl-convert-python>=1.6.0` - Chart conversion and export
- `Authlib>=1.3.2` - Google OAuth authentication

### Multi-Agent AI
- `crewai>=0.35.8` - Collaborative AI system for financial health analysis

### Technical Analysis
- `pandas-ta==0.4.71b0` - 150+ technical indicators
- `scipy>=1.11.0` - Scientific computing for technical analysis

### System Dependencies (Docker)
- `osqp>=0.6.3` - Quadratic programming solver (specific version for stability)

## Contributing

We welcome contributions! Here are ways you can help improve Finance Bro:

### Theme Contributions
**🎨 Custom Themes Wanted**: We're looking for contributors to help create custom themes for the app. If you have design skills and want to contribute:
- Create custom CSS themes (light/dark variants)
- Design responsive layouts
- Improve accessibility features
- Submit theme proposals via pull requests

### General Contributions
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Contribution Guidelines
- Follow PEP8 style guidelines
- Add appropriate documentation
- Test your changes thoroughly
- Include screenshots for UI changes
- Update README if adding new features

## License

This project is open source and available under the [MIT License](LICENSE).

## Support

If you encounter any issues or have questions, please open an issue on GitHub.

---

**Built with ❤️ using Streamlit, PandasAI, and Vnstock**
