# Finance Bro - AI Stock Analysis

🚀 **Experimental front-end vibe coding project for Vietnamese stock market analysis** 

This project is an **experiment in front-end vibe coding** - exploring how intuitive, design-first development approaches can be used to assist analysts' backend work and transform it into a well-rounded full-stack data analysis platform with compelling visuals.

**What is Front-End Vibe Coding?**
- Design-first development approach prioritizing user experience and visual appeal
- Rapid prototyping with immediate visual feedback
- Intuitive interface design that makes complex data analysis accessible
- Focus on creating engaging, interactive data visualizations

**Project Goals:**
- Bridge the gap between backend financial analysis and frontend user experience
- Demonstrate how front-end vibe coding can enhance traditional data analysis workflows
- Create a comprehensive financial analysis platform that's both powerful and visually appealing
- Show how modern web technologies can make complex financial data more accessible

**Natural Language Interface:** Interact with your financial statements in natural language. Get answers to your questions about any financial statement of listed stocks in Vietnam with a friendly finance bro. He's an introvert so please make your questions short and to the point. 

## Features

- 📊 **Vietnamese Stock Data** - Load financial data using Vnstock (VCI/TCBS sources)
- 🤖 **AI Chat Interface** - Natural language queries about financial metrics with PandasAI integration
- 💬 **Interactive Analysis** - Real-time conversation with AI analyst including file upload support
- 📈 **Advanced Technical Analysis** - Interactive price charts with 75+ QuantStats metrics, professional tearsheets, and comprehensive technical indicators (RSI, MACD, Bollinger Bands, OBV, ADX) with robust error handling
- 🎯 **Intelligent Stock Screener** - Multi-criteria filtering with 6 advanced filters (Beta, Alpha, Financial Health, etc.)
- 💼 **Portfolio Optimization** - Modern Portfolio Theory, Hierarchical Risk Parity, and risk analysis with riskfolio-lib
- 🏢 **Comprehensive Company Analysis** - Ownership structure, management team, subsidiaries, and foreign transaction analysis
- 📊 **Professional Visualizations** - Interactive charts with Altair, Bokeh, and custom styling
- 🔐 **Secure Authentication** - Google OAuth integration with API key management

## Quick Start

### Prerequisites

- Python >= 3.10.11
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

### Step 2: Stock Analysis Page (Essential First Stop)
4. **📈 Navigate to Stock Analysis**: From the homepage, click the "📊 Stock Analysis" quick navigation button
   - **Why This Matters**: The Stock Analysis page loads and caches essential data for optimal performance
   - **Data Loading**: This page loads all stock symbols and company information for the entire app
   - **Performance**: Visiting this page first ensures faster loading on all other pages

5. **⚙️ Configure Analysis Settings**: In the Stock Analysis page:
   - Select period (year/quarter)
   - Choose data source (VCI/TCBS)
   - Click "Analyze Stock" to load financial data

6. **💬 AI Interaction**: Once data is loaded:
   - Use the chat interface to ask financial questions
   - Try sample questions from the sidebar
   - Explore AI-generated insights and charts

### Step 3: Explore Other Analysis Tools
7. **🚀 Navigate to Other Pages**: Now you can efficiently use other analysis tools:
   - **📈 Price Analysis**: Interactive price charts with 75+ QuantStats metrics and professional tearsheets
   - **📊 Technical Analysis**: Advanced technical indicators with heating stock discovery and robust error handling
   - **🏢 Company Overview**: Company profile with ownership structure, management team, subsidiaries, and foreign transaction analysis
   - **💼 Portfolio Optimization**: Modern Portfolio Theory, Hierarchical Risk Parity, and comprehensive risk analysis
   - **🎯 Stock Screener**: Multi-criteria stock filtering with advanced metrics (Beta, Alpha, Financial Health) and quick presets

### Recommended Setup for Best Experience

**🎨 Custom Theme for Best Appearance**: This app is designed with a custom color scheme for optimal visual experience.

**How to enable custom theme:**
1. Click the hamburger menu (☰) in the top-right corner
2. Select "Settings"
3. Under "Theme", choose "Custom"
4. The app will display with the optimized color scheme and chart styling

**Alternative**: Light mode is also supported if you prefer standard Streamlit styling.

### Why This Flow Matters

**🎯 Performance Optimization**: 
- Stock Analysis page loads and caches symbols data once for the entire session
- All other pages benefit from this cached data for faster loading
- Company names display properly across all pages

**📊 Data Consistency**: 
- Your selected stock symbol persists across all pages
- Financial data is loaded once and shared across analysis tools
- Seamless navigation between different analysis perspectives

**🚀 Best User Experience**:
- No need to re-enter stock symbols on each page
- Faster page loads after initial data caching
- Professional company name display instead of just stock symbols

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

- **pandasai v2.3.0** requires **pandas v1.5.3** (not v2.x)
- **pandasai v3.x** (beta) has breaking changes and schema issues
- Mismatched versions cause:
  - `TypeError: sequence item 0: expected str instance, tuple found`
  - `'DataFrame' object has no attribute 'schema'`
  - Agent initialization failures

### Tested Compatible Versions

✅ **WORKING COMBINATION:**
- `pandasai==2.3.0` (stable)
- `pandas==1.5.3` (exact version required for compatibility)
- `quantstats==0.0.59` (last version compatible with pandas 1.5.3)
- Built-in OpenAI LLM (no separate extension needed)

❌ **AVOID:**
- `pandasai>=3.0.0` (beta, unstable)
- `pandas>=2.0.0` (incompatible with pandasai 2.3.0)
- `quantstats>=0.0.60` (requires pandas 2.0+ frequency aliases)
- `pandasai-openai` extension (not needed in v2.3.0)

### Critical QuantStats Compatibility
**NEVER upgrade quantstats independently.** The app uses:
- **QuantStats v0.0.59** - Last version compatible with pandas 1.5.3 legacy frequency aliases (`M`, `Q`, `A`)
- **Issue with newer versions**: QuantStats 0.0.60+ uses pandas 2.0+ frequency aliases (`ME`, `QE`, `YE`) causing "Invalid frequency" errors
- **Solution**: Version pinned in requirements.txt to maintain compatibility

### If You Need to Upgrade

1. **Test in a separate environment first**
2. **Check pandasai release notes** for breaking changes
3. **Update both packages together**, not individually
4. **Run the app thoroughly** before deploying

## Technology Stack

- **Frontend:** Streamlit v1.47.0 with Google OAuth authentication
- **AI Engine:** PandasAI v2.3.0 (stable) with OpenAI GPT integration
- **Stock Data:** Vnstock v3.2.5 (VCI/TCBS sources for Vietnamese market)
- **Data Processing:** Pandas v1.5.3 (compatible with pandasai 2.3.0)
- **Financial Analysis:** QuantStats v0.0.59 (75+ performance metrics and tearsheets)
- **Portfolio Optimization:** PyPortfolioOpt (Modern Portfolio Theory, Efficient Frontier)
- **Risk Analysis:** riskfolio-lib v5.0.1+ (Hierarchical Risk Parity, advanced risk metrics)
- **Technical Analysis:** pandas-ta for 150+ technical indicators with robust error handling
- **Visualizations:** Altair v5.5.0+, Bokeh v2.4.3, mplfinance for interactive charts
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
│   └── Screener.py           # Stock screening & filtering
├── static/style.css          # Custom CSS styling
├── .streamlit/               # Streamlit configuration
│   ├── config.toml          # Custom theme & colors
│   └── secrets.example.toml # OAuth configuration template
├── requirements.txt          # Python dependencies
├── pyproject.toml           # Project configuration (Python 3.10.11)
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker Compose configuration
├── .env.example             # Environment variables template
├── CHANGELOG.md             # Version history
├── CLAUDE.md                # AI assistant instructions
└── Reference/               # Legacy code & documentation
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
- `pandas==1.5.3` - Data manipulation (exact version for compatibility)
- `vnstock==3.2.5` - Vietnamese stock data (VCI/TCBS sources)
- `openai>=1.61.0` - OpenAI API client
- `streamlit==1.47.0` - Web application framework with OAuth support
- `python-dotenv==1.0.1` - Environment variable management

### Financial Analysis
- `quantstats==0.0.59` - Performance analytics and tearsheets (75+ metrics)
- `pyportfolioopt>=1.5.6` - Modern Portfolio Theory optimization
- `riskfolio-lib>=5.0.1` - Advanced risk analysis and HRP
- `mplfinance>=0.12.10b0` - Financial data visualization

### Visualization & UI
- `altair>=5.5.0` - Interactive statistical visualizations  
- `bokeh==2.4.3` - Interactive web plots
- `Authlib>=1.3.2` - Google OAuth authentication

### System Dependencies (Docker)
- `osqp==0.6.2.post8` - Quadratic programming solver (specific version for stability)

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
