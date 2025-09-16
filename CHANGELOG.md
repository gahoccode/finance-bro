# Changelog

All notable changes to the Finance Bro AI Stock Analysis application will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.32] - 2025-09-16

### Fixed  
- [2025-09-16] **Bollinger Bands Complete Fix**: Fixed pandas-ta Bollinger Bands calculation and chart display issues
  - **Root Cause**: pandas-ta `bbands()` function returns columns with format `BBL_20_2.0_2.0`, `BBM_20_2.0_2.0`, `BBU_20_2.0_2.0` but code expected `BBL_20_2.0`, `BBM_20_2.0`, `BBU_20_2.0`
  - **Solution**: Updated column references across all technical analysis services to match actual pandas-ta output format
  - **Impact**: Eliminates "missing expected columns" warning and "Skipped indicators in chart" messages, enables proper Bollinger Bands display
  - **Scope of Impact** (3 files, chart display functions): 
    - **src/services/technical_indicators.py**: Updated expected column names in Bollinger Bands validation logic
    - **src/services/chart_service.py**: Updated chart plotting references to use correct column names
    - **src/services/data_service.py**: Updated chart preparation references for mplfinance integration
  - **Testing Confirmed**: pandas-ta consistently returns `_2.0_2.0` format regardless of input column case
- [2025-09-16] **Streamlit Caching Error**: Resolved `CacheReplayClosureError` in technical indicators calculation by implementing clean separation of concerns
  - **Root Cause**: `calculate_technical_indicators()` was calling `st.warning()` and `st.success()` directly inside the cached function
  - **Solution**: Split into two functions - `calculate_technical_indicators()` for pure calculation logic and `display_indicators_status()` for UI display
  - **Performance**: Caching now works correctly without UI element conflicts, improving indicator calculation performance
  - **Architecture**: Follows Streamlit best practices for cached functions (pure data computations only)
  - **Scope of Impact** (2 files, 3 functions):
    - **src/services/technical_indicators.py**: Modified `calculate_technical_indicators()` to return tuple `(dict, list, bool)` instead of `dict`, removed all UI calls, added new `display_indicators_status()` function
    - **pages/Technical_Analysis.py** (2 call sites): Updated function calls to use new tuple return signature and added calls to `display_indicators_status()` for UI display
  - **ADX Functionality Preserved**: Unlike dev branch, this fix maintains full ADX (Average Directional Index) functionality with enhanced data validation

## [0.2.31] - 2025-09-16

### Changed
- [2025-09-16] **Streamlit API Partial Support Update**: Refined implementation of Streamlit's `use_container_width` parameter replacement based on actual function compatibility
  - **Limited Parameter Support**: Discovered that `width` parameter is not universally supported across all Streamlit chart functions
  - **Altair Chart Compatibility**: Reverted all `st.altair_chart()` calls back to `use_container_width=True` due to VegaChartsMixin incompatibility
  - **Plotly Chart Compatibility**: Maintained `use_container_width=True` for `st.plotly_chart()` functions as they don't support `width` parameter yet
  - **Successful Implementation**: Preserved `width='stretch'` for `st.button()` and `st.dataframe()` functions which fully support the new parameter
  - **Error Resolution**: Fixed "VegaChartsMixin.altair_chart() got an unexpected keyword argument 'width'" error across all chart functions

### Technical Implementation Details
- [2025-09-16] **Selective Parameter Strategy**: Implemented conditional approach based on Streamlit function compatibility
  - **Chart Functions**: Altair and Plotly charts maintain `use_container_width=True` until Streamlit adds `width` parameter support
  - **UI Components**: Buttons and dataframes successfully migrated to `width='stretch'` for future compatibility
  - **Version Preparedness**: Application now properly positioned for Streamlit's 2025-12-31 deprecation deadline where supported

### Fixed
- [2025-09-16] **Variable Scoping Issue**: Resolved `NameError: name 'ticker' is not defined` in Stock_Price_Analysis.py
  - **Root Cause**: `ticker` variable was defined inside conditional block but used outside that scope
  - **Solution**: Moved variable initialization outside conditional logic to ensure accessibility throughout the module
  - **Impact**: Fixed import errors that prevented proper module loading in Stock_Price_Analysis.py

## [0.2.30] - 2025-09-16

### Changed
- [2025-09-16] **Streamlit API Update**: Replaced deprecated `use_container_width` parameter with new `width` parameter where supported
  - **Future Compatibility**: Updated 17 occurrences for buttons and dataframes to prepare for Streamlit's 2025-12-31 deprecation deadline
  - **Compatibility Fix**: Reverted 28 chart function calls back to `use_container_width=True` due to Streamlit version compatibility issues
  - **Selective Implementation**: Applied `width='stretch'` for buttons/dataframes and kept `use_container_width=True` for chart functions
  - **Scope**: Updated all main application files (app.py, pages/, src/components/, src/services/) while preserving standalone-bro/ directory
  - **Files Updated**: 13 main application files including all analysis pages, components, and services

### Enhanced
- [2025-09-15] **Superior Candlestick Charts**: Migrated from Altair to Plotly for optimal OHLCV visualization in stock price analysis
  - **Native Candlestick Support**: Replaced manual Altair rule+bar construction with Plotly's native `go.Candlestick()` implementation
  - **Professional Financial Charting**: Enhanced interactivity with zoom, pan, and hover features specifically designed for financial data
  - **Interactive Range Selectors**: Added professional range selector buttons (7d, 30d, 3m, 6m, 1y, All) for quick time period navigation
  - **Synchronized Subplots**: Price and volume charts are perfectly synchronized with shared x-axis for comprehensive OHLCV analysis
  - **Finance Bro Theming**: Maintained consistent color scheme (#76706C bullish, #2B2523 bearish) across the new Plotly implementation

### Technical Implementation
- [2025-09-15] **New Chart Service Function**: Added `create_plotly_candlestick_chart()` to centralized chart service
  - **Plotly Integration**: Added plotly>=5.17.0 dependency for professional financial charting capabilities
  - **Dual Chart Layout**: Implemented 2-row subplot layout with 70% price chart and 30% volume chart
  - **Enhanced Styling**: Professional grid styling, hover templates, and Finance Bro color coordination
  - **Performance Optimized**: Direct chart rendering without intermediate file generation

### User Experience Improvements
- [2025-09-15] **Enhanced Stock Analysis**: Stock Price Analysis page now features professional-grade candlestick charts
  - **Superior Visualization**: Cleaner, more professional OHLCV chart presentation
  - **Better Interactivity**: Native financial chart controls and navigation
  - **Consistent Theming**: Maintained Finance Bro visual identity with improved chart quality

## [0.2.28] - 2025-09-15

### Added
- [2025-09-15] **Smart Data Loading Architecture**: Implemented comprehensive smart data loading system that eliminates page dependencies and provides progressive loading with user feedback
  - **Progressive Loading**: Data loads in stages with real-time progress feedback and status messages
  - **No Page Dependencies**: Each page now works independently without requiring users to visit other pages first
  - **Intelligent Caching**: Smart cache invalidation and reuse strategies optimize performance across sessions
  - **Graceful Degradation**: Enhanced error handling with informative messages when data loading fails

### Enhanced
- [2025-09-15] **Enhanced Valuation Flow**: Added pre-loading system with real-time data status indicator and progressive feedback
  - **Homepage Integration**: Added "⚡ Load & Analyze Valuation" button on homepage for direct valuation access
  - **Real-time Status**: Dynamic data availability indicator shows current loading state across all pages
  - **User Experience**: Eliminated mandatory "Stock Analysis" page visit - users can now navigate directly to any analysis page
  - **Performance**: Smart loading reduces redundant API calls and improves overall application responsiveness

### Technical Implementation
- [2025-09-15] **New Service Architecture**: Created modular service layer for centralized data management
  - **Session State Service** (`src/services/session_state_service.py`): Centralized session state management with intelligent dependency resolution
  - **Financial Data Service** (`src/services/financial_data_service.py`): Comprehensive financial data loading with validation and caching
  - **Smart Loading Functions**: Implemented `ensure_valuation_data_loaded()`, `ensure_financial_data_loaded()`, and `smart_load_for_page()` functions
  - **Cache Management**: Enhanced TTL-based caching with smart cache key generation and manual cache clearing capabilities

### User Experience Improvements
- [2025-09-15] **Streamlined User Flow**: Redesigned user journey for enhanced flexibility and performance
  - **Direct Navigation**: Users can now navigate directly from homepage to any analysis page
  - **Flexible Workflow**: No mandatory path - users choose their preferred analysis approach
  - **Progress Feedback**: Real-time progress bars and status messages during data loading
  - **Backwards Compatibility**: Existing users can still follow traditional flow while benefiting from new optimizations

### Documentation Updates
- [2025-09-15] **Comprehensive Documentation**: Updated all documentation to reflect new smart data loading architecture
  - **Architecture Overview**: Updated with new service layer components and smart data loading design principles
  - **Data Architecture**: Enhanced with smart loading patterns and progressive data flow diagrams
  - **Architecture Decisions**: Added ADR-013 documenting the smart data loading architecture decision
  - **Development Guide**: Updated CLAUDE.md with new best practices and service usage patterns
  - **User Documentation**: Updated README.md with enhanced user flow and new feature descriptions

## [0.2.27] - 2025-09-15

### Fixed
- [2025-09-15] **DCF Calculation Variable Scope Error**: Fixed NameError for 'current_price' in valuation analysis
  - **Variable Initialization**: Added proper initialization of `current_price` and `actual_current_price` variables at the beginning of WACC calculation section (lines 345-350)
  - **Cross-Tab Variable Dependency**: Resolved variable scope issue where `current_price` was only defined in fallback method execution path but used in DCF calculation (Tab 3) regardless of which method succeeded
  - **Early Price Extraction**: Moved price data extraction before method selection logic to ensure availability in both execution paths (primary VnStock Company class and fallback manual calculation)
  - **Proper Scaling**: Ensured correct VnStock API data scaling by converting thousands of VND to original scale (multiplying by 1000)
  - **Enhanced Validation**: Added `current_price > 0` validation to DCF calculation condition (line 718) to prevent calculations with invalid price data
  - **User Experience**: Updated data requirements display to include "Current Price Available" status for better user feedback

### Technical Implementation
- [2025-09-15] **Valuation.py Variable Scope Fix**: Enhanced DCF calculation reliability in `pages/Valuation.py`
  - **Code Quality**: Applied ruff formatting and passed all code quality checks
  - **Comprehensive Testing**: Created test suite in `tests/test_current_price_fix.py` to verify fix works in both execution paths
  - **Error Prevention**: Eliminated potential NameError when primary market cap calculation method succeeds
  - **Execution Path Consistency**: Ensured both primary and fallback methods provide required variables for downstream DCF calculations
  - **Maintainability**: Removed duplicate code and centralized price extraction logic

## [0.2.26] - 2025-09-01

### Added
- [2025-09-01] **Company News Tab**: Added comprehensive news and reports tab to Company Overview page
  - **News Integration**: Integrated vnstock Company.reports() API to fetch latest company news and reports
  - **Interactive Links**: Added clickable links that redirect users to full news articles
  - **Chronological Display**: Reports automatically sorted by date (most recent first) with proper datetime formatting
  - **Rich Content Display**: Shows article title (description), publication date, summary (name), and direct article links
  - **Performance Optimized**: Implemented 5-minute caching for news data using @st.cache_data decorator
  - **User Experience**: Added summary metrics showing total number of available reports

### Technical Implementation
- [2025-09-01] **News Tab Infrastructure**: Added news functionality to Company Overview analysis system
  - **Service Layer**: Created `get_company_reports()` function in `src/services/vnstock_api.py` following existing patterns
  - **Data Processing**: Proper datetime conversion and sorting for chronological news display
  - **UI Enhancement**: Extended tab structure from 5 to 6 tabs with News positioned before Full Details
  - **Error Handling**: Comprehensive error handling for missing data and API failures
  - **Code Standards**: Follows Finance Bro coding conventions with ruff formatting and modular architecture

## [0.2.25] - 2025-08-31

### Enhanced
- [2025-08-31] **DCF Net Debt Calculation Accuracy**: Improved net debt calculation in Valuation page for more accurate DCF analysis
  - **Proper Net Debt Formula**: Replaced oversimplified `net_debt = total_debt` with accurate calculation: `Total Debt - Cash & Cash Equivalents - Short-term Investments`
  - **Exact Column Names**: Used precise Balance Sheet column names from Reference/fin_col.md: "Cash and cash equivalents (Bn. VND)" and "Short-term investments (Bn. VND)"
  - **Enhanced Transparency**: Added detailed breakdown in valuation summary table showing Total Debt, Cash, Short-term Investments, and calculated Net Debt
  - **Improved DCF Accuracy**: More precise equity valuation calculation by properly accounting for company's liquid assets that offset debt obligations
  - **Financial Best Practices**: Follows standard DCF methodology where Enterprise Value minus Net Debt equals Equity Value

### Technical Implementation
- [2025-08-31] **Valuation.py Net Debt Logic**: Enhanced DCF calculation methodology in `pages/Valuation.py`
  - **Balance Sheet Integration**: Proper extraction of cash and short-term investment values from latest balance sheet data
  - **Summary Table Enhancement**: Expanded valuation summary to show debt calculation components for user transparency
  - **Error Prevention**: Eliminated potential undervaluation bias from not accounting for company's liquid asset positions
  - **Column Name Accuracy**: Direct mapping to exact vnstock API column names for reliable data extraction

## [0.2.24] - 2025-08-18

### Enhanced
- [2025-08-18] **DuPont Analysis Financial Formatting**: Applied consistent financial display formatting to DuPont analysis tab
  - **Financial Display Options**: Added user-controlled display format selection (billions, millions, original VND) using `render_financial_display_options()` function from `src/components/ui_components.py`
  - **Metrics Formatting**: Applied `format_financial_display()` function from `src/services/data_service.py` to all financial metrics (Net Income, Revenue, Total Assets, Equity) with proper comma separators and unit displays
  - **Table Formatting**: Used `convert_dataframe_for_display()` function from `src/services/data_service.py` to format DuPont analysis table columns with consistent number formatting while preserving original data
  - **Shared UI Components**: Implemented shared `render_financial_display_options()` component to eliminate code duplication between DuPont and Capital Employed tabs
  - **Professional Presentation**: Consistent formatting across metrics and tables matching Finance Bro application standards

### Technical Implementation  
- [2025-08-18] **DuPont Analysis Page Updates**: Enhanced `pages/dupont_analysis.py` with modular formatting system
  - **Reusable Components**: Leveraged existing `render_financial_display_options()` component from `src/components/ui_components.py`
  - **Display Formatting**: Applied `format_financial_display()` and `convert_dataframe_for_display()` functions from `src/services/data_service.py`
  - **Session State Integration**: Proper session state management for display format preferences with unique keys for `render_financial_display_options()`
  - **Column Configuration**: Updated Streamlit column configuration to handle formatted string columns as TextColumn type for `convert_dataframe_for_display()` output
  - **Code Deduplication**: Moved `render_financial_display_options()` component outside tab structure to be shared between DuPont and Capital Employed tabs

## [0.2.23] - 2025-08-18

### Added
- [2025-08-18] **DuPont Analysis Session State Management**: Enhanced DuPont analysis functionality with persistent data storage
  - **Session State Integration**: DuPont analysis dataframe now stored in `st.session_state.dupont_analysis` for persistence across page interactions
  - **Data Consistency**: Ensures calculated DuPont metrics remain available throughout user session for cross-page analysis
  - **Navigation Continuity**: Maintains analysis results when users navigate between different analysis pages

### Enhanced
- [2025-08-18] **DuPont Analysis Page**: Improved data flow and user experience
  - **Persistent Results**: Analysis results now persist in session state for better data accessibility
  - **Consistent Data Management**: Follows application patterns for dataframe storage and retrieval
  - **Cross-Page Integration**: Enables potential future integration with other analysis tools

## [0.2.22] - 2025-08-15

### Added
- [2025-08-15] **CrewAI Financial Health Analysis System**: Multi-agent AI system for comprehensive financial health reporting
  - **Multi-Agent Architecture**: Three specialized agents (Senior Financial Analyst, Risk & Sustainability Expert, Executive Report Writer) with collaborative workflow
  - **Comprehensive Financial Analysis**: Deep analysis of Income Statement, Balance Sheet, and Cash Flow Statement with multi-year trends
  - **Vietnamese Market Integration**: Exact column name matching for vnstock API data with precise financial metrics extraction
  - **Current Year Focus**: Detailed analysis of current year line items across all three financial statements
  - **Holistic Multi-Year Analysis**: Trend analysis and opinions spanning multiple years of financial data
  - **Interactive Streamlit Interface**: User-friendly Financial Health Report page with data validation and progress tracking

### Technical Implementation
- [2025-08-15] **CrewAI Framework Integration**: Added `crewai>=0.35.8` dependency with YAML configuration system
  - **Agent Configuration**: `src/financial_health_crew/config/agents.yaml` with detailed roles, goals, and backstories
  - **Task Configuration**: `src/financial_health_crew/config/tasks.yaml` with comprehensive analysis requirements
  - **Crew Orchestration**: `src/financial_health_crew/crew.py` with sequential processing and proper verbose configuration

- [2025-08-15] **Enhanced Financial Analysis Tool**: `src/financial_health_crew/tools/financial_analysis_tool.py`
  - **Exact Column Matching**: Precise mapping of Vietnamese stock data column names from vnstock API
  - **Multi-Analysis Types**: Support for 'overview', 'ratios', 'trends', and 'detailed' analysis modes
  - **Real Financial Data**: Direct access to actual financial values instead of metadata
  - **Comprehensive Context**: Detailed financial data extraction with current year specifics and multi-year comparisons
  - **Vietnamese Column Names**: Exact patterns for `'TOTAL ASSETS (Bn. VND)'`, `'Net cash inflows/outflows from operating activities'`, `"OWNER'S EQUITY(Bn.VND)"`

- [2025-08-15] **Streamlit Integration**: New Financial Health Report page and navigation updates
  - **Page Implementation**: `pages/Financial_Health_Report.py` with session state validation and user-friendly interface
  - **Navigation Integration**: Added to app.py navigation menu and quick buttons
  - **Service Wrapper**: `src/services/crewai_service.py` for session state management and caching

### Bug Fixes
- [2025-08-15] **Import Error Fixes**: Corrected CrewAI tool imports from `crewai_tools` to `crewai.tools`
- [2025-08-15] **Validation Error Fix**: Changed verbose parameter from integer `2` to boolean `True` for CrewAI compliance
- [2025-08-15] **Type Import Fix**: Added `List` to typing imports for proper type annotations

### Key Learning and Documentation
- [2025-08-15] **Context7 Integration**: Learned CrewAI `allow_delegation` parameter functionality for agent collaboration
- [2025-08-15] **Column Name Precision**: User-provided exact column names from Vietnamese stock data for 100% matching accuracy
- [2025-08-15] **Multi-Agent Workflow**: Implemented sequential task processing with specialized financial analysis agents

## [0.2.21] - 2025-08-14

### Changed
- [2025-08-31] **Replace hard-coded statutory tax rate with calculated effective tax rate in Valuation page for more accurate WACC calculations**

### Added
- [2025-08-14] **Fibonacci Retracement Analysis**: Comprehensive Fibonacci retracement feature with SciPy-based swing detection
  - **Professional Swing Detection**: Uses `scipy.signal.argrelextrema` for accurate swing high/low identification
  - **Complete Fibonacci Levels**: Standard retracement levels (0%, 23.6%, 38.2%, 50%, 61.8%, 78.6%, 100%) with optional extensions (138.2%, 161.8%, 200%, 261.8%)
  - **Visual Integration**: Horizontal Fibonacci lines overlaid on mplfinance candlestick charts with Finance Bro theme colors
  - **Interactive Controls**: Sidebar controls for swing lookback period (20-100 bars), sensitivity (3-15), extension levels toggle, and price alert threshold (1-5%)
  - **Price Proximity Alerts**: Real-time notifications when current price approaches Fibonacci levels within configurable threshold
  - **Analysis Summary**: Detailed swing point analysis with date stamps, price ranges, and key retracement level displays
  - **Chart Integration**: Seamless integration with existing Technical Analysis charts without disrupting existing indicators

### Technical Implementation
- [2025-08-14] **New Service Module**: Created `src/services/fibonacci_service.py` with professional Fibonacci analysis tools
  - **Swing Detection Functions**: `find_swing_points()` using SciPy's `argrelextrema` with configurable order and minimum distance filtering
  - **Level Calculations**: `calculate_fibonacci_levels()` for both retracement and extension level computation
  - **Main Analysis**: `get_recent_swing_fibonacci()` for comprehensive swing analysis with column format compatibility
  - **Data Validation**: `validate_fibonacci_data()` supporting both lowercase and capitalized OHLCV columns
  - **Theme Integration**: `get_fibonacci_colors()` using Finance Bro color scheme for consistent visual styling
  - **Display Formatting**: `format_fibonacci_summary()` for user-friendly analysis presentation

- [2025-08-14] **Chart Service Enhancement**: Extended `src/services/chart_service.py` with Fibonacci overlay capabilities
  - **Chart Function Update**: Enhanced `create_technical_chart()` with optional `fibonacci_config` parameter
  - **Overlay Creation**: `_create_fibonacci_overlays()` generates mplfinance addplot objects for horizontal Fibonacci lines
  - **Summary Display**: `display_fibonacci_summary()` shows detailed swing analysis and key retracement levels
  - **Alert System**: `get_fibonacci_level_alerts()` provides price proximity notifications with column format compatibility
  - **Session State Integration**: Fibonacci data stored in session state for cross-function access and summary displays

- [2025-08-14] **Technical Analysis Page Integration**: Enhanced `pages/Technical_Analysis.py` with comprehensive Fibonacci controls
  - **UI Controls**: Added Fibonacci retracement section with checkbox, lookback period slider, sensitivity slider, extensions toggle, and alert threshold configuration
  - **Chart Integration**: Updated chart generation calls to include `fibonacci_config` parameter for overlay rendering
  - **Display Integration**: Added Fibonacci summary display and alert notifications below charts
  - **Documentation Update**: Enhanced footer documentation with Fibonacci features and SciPy algorithm details

- [2025-08-14] **Dependency Management**: Added `scipy>=1.11.0,<1.12.0` to `pyproject.toml` for swing detection compatibility
  - **Version Compatibility**: Carefully selected SciPy version compatible with existing pandas==1.5.3 and numpy constraints
  - **Signal Processing**: Access to `scipy.signal.argrelextrema` for professional swing point identification
  - **Performance Optimization**: 5-minute caching with `@st.cache_data` for Fibonacci calculations

### Column Format Compatibility
- [2025-08-14] **Dual Format Support**: Robust handling of both lowercase and capitalized OHLCV column formats
  - **vnstock Integration**: Handles capitalized columns (`'Open', 'High', 'Low', 'Close', 'Volume'`) from vnstock API after mplfinance conversion
  - **Test Compatibility**: Supports lowercase columns (`'open', 'high', 'low', 'close', 'volume'`) for development testing
  - **Dynamic Detection**: Automatic column format detection in all Fibonacci functions
  - **Error Prevention**: Fixed column name errors that were causing "Error calculating Fibonacci levels: 'high'" and "Error checking Fibonacci alerts: 'close'" issues

### User Experience Enhancements
- [2025-08-14] **Professional Analysis Tools**: Advanced technical analysis capabilities matching institutional trading platforms
  - **Configurable Parameters**: Users control swing detection sensitivity and lookback periods for different market conditions
  - **Visual Feedback**: Fibonacci levels rendered as horizontal lines with varying thickness and transparency based on importance
  - **Educational Content**: Comprehensive documentation explaining Fibonacci features, SciPy algorithms, and optimal settings
  - **Price Context**: Real-time price proximity analysis showing distance to nearest Fibonacci levels
  - **Clean Integration**: Fibonacci controls seamlessly integrated into existing Technical Analysis workflow

### Performance & Quality
- [2025-08-14] **Comprehensive Testing**: Complete test suite validating all Fibonacci functionality
  - **Unit Tests**: Validated swing detection, level calculation, chart integration, and alert generation
  - **Integration Tests**: Confirmed compatibility with vnstock data pipeline and mplfinance charts
  - **Column Format Tests**: Verified support for both lowercase and capitalized OHLCV formats
  - **Error Handling Tests**: Validated graceful handling of insufficient data and edge cases
  - **Type Checking**: MyPy validation successful with proper typing throughout codebase

### Files Modified
- `pyproject.toml`: Added SciPy dependency with version constraints
- `src/services/fibonacci_service.py`: New comprehensive Fibonacci analysis service (288 lines)
- `src/services/chart_service.py`: Enhanced with Fibonacci overlay functions (+203 lines)
- `pages/Technical_Analysis.py`: Added Fibonacci UI controls and integration (+50 lines)

## [0.2.20] - 2025-08-12

### Added
- [2025-08-12] **Complete Modular Refactoring**: Implemented comprehensive codebase modularization with centralized utilities and services
  - **Phase 1: Core Infrastructure** - Created `src/` directory structure with core utilities:
    - `src/core/config.py`: Centralized configuration constants (cache TTL, default symbols, colors)
    - `src/utils/session_utils.py`: Session state helper functions that work WITH existing patterns
    - `src/utils/validation.py`: Input validation utilities for stock symbols and data integrity
    - `src/components/stock_selector.py`: Reusable stock selector supporting both selectbox and multiselect patterns
    - `src/components/date_picker.py`: Date range picker with session state integration
    - `src/services/data_service.py`: Data transformation utilities (financial DataFrame transposition)
  
  - **Phase 2: API Centralization** - Extracted all @st.cache_data functions to `src/services/vnstock_api.py`:
    - **26 cached functions** moved from individual pages to centralized module
    - All Company Overview functions: `get_ownership_data`, `get_management_data`, `get_subsidiaries_data`, `get_insider_deals_data`, `get_foreign_trading_data`
    - Stock price functions: `fetch_stock_price_data`, `fetch_portfolio_stock_data`
    - Technical analysis functions: `get_heating_up_stocks`, `get_technical_stock_data`, `calculate_technical_indicators`
    - Screener function: `get_screener_data`
    - **Preserved exact caching patterns** and TTL values from original implementation
  
  - **Phase 3: Chart Generation Service** - Created `src/services/chart_service.py` with centralized chart utilities:
    - **Technical Analysis Charts**: `create_technical_chart()` with mplfinance and Finance Bro theme
    - **Stock Price Charts**: `create_altair_line_chart()`, `create_altair_area_chart()`, `create_bokeh_candlestick_chart()`
    - **Chart Detection**: `detect_latest_chart()` for PandasAI generated charts
    - **Theme Management**: `get_finance_bro_theme()`, `create_mplfinance_style()` for consistent styling
  
  - **Phase 4: Page Integration** - Updated all pages to use new modular structure:
    - **Company_Overview.py**: Replaced 5 local functions with vnstock_api imports
    - **Stock_Price_Analysis.py**: Replaced local function and integrated chart_service functions
    - **Technical_Analysis.py**: Replaced 3 local functions with vnstock_api/chart_service imports
    - **Portfolio_Optimization.py**: Replaced local function with vnstock_api import
    - **Screener.py**: Replaced local function with vnstock_api import
    - **bro.py**: Integrated chart_service for chart detection

### Technical Architecture
- **Zero Breaking Changes**: All existing functionality preserved exactly as implemented
- **Session State Preservation**: All 30+ session state variables maintained with exact naming and behavior
- **Import Consolidation**: Eliminated code duplication across pages while maintaining individual page functionality
- **Performance Optimization**: Centralized caching reduces memory usage and improves data consistency
- **Maintainable Structure**: Single source of truth for API calls, chart generation, and utility functions

### Code Organization Benefits
- **Developer Experience**: Clear separation of concerns with logical module structure
- **Consistency**: Unified approach to API calls, caching, and chart generation across all pages
- **Scalability**: New features can leverage existing utilities and follow established patterns
- **Theme Management**: Single location for all Finance Bro styling and color schemes
- **Error Handling**: Centralized error handling and validation patterns

### Project Structure Changes
- **NEW**: Created `src/` directory with modular architecture
  - `src/core/config.py`: Centralized configuration constants
  - `src/utils/`: Session state helpers and validation utilities  
  - `src/components/`: Reusable UI components (stock selector, date picker)
  - `src/services/`: Business logic services (vnstock_api.py, chart_service.py, data_service.py)
- **UPDATED**: All pages/ now import from centralized modules instead of local functions
- **PRESERVED**: All existing directories (cache/, exports/, static/, tests/) unchanged

### New Project Structure
```
finance-bro/
├── src/                          # NEW: Modular utilities and services
│   ├── core/                    # Core configuration and constants
│   │   └── config.py           # Centralized app configuration
│   ├── utils/                   # General utility functions
│   │   ├── session_utils.py    # Session state management helpers
│   │   └── validation.py       # Input validation and data integrity
│   ├── components/              # Reusable UI components
│   │   ├── stock_selector.py   # Stock selection widgets
│   │   └── date_picker.py      # Date range selection components
│   └── services/                # Business logic and data services
│       ├── vnstock_api.py      # Centralized VnStock API functions (26 functions)
│       ├── data_service.py     # Data transformation utilities
│       └── chart_service.py    # Chart generation and theming (7 functions)
├── pages/                        # Streamlit multi-page application (updated)
├── cache/                        # Data caching directory for performance
├── exports/                      # Generated files and outputs
├── static/                       # Static assets and styling
├── tests/                        # Test suite (pytest)
└── [existing files...]          # Configuration and deployment files
```

### Module Import Hierarchy
- **pages/**: All pages import from `src/services/vnstock_api.py` for data functions
- **Technical Analysis & Stock Price**: Import from `src/services/chart_service.py` for visualizations
- **Reusable Components**: Available from `src/components/` for consistent UI elements
- **Configuration**: Centralized in `src/core/config.py` for app-wide settings
- **Utilities**: Session state and validation helpers in `src/utils/`

## [0.2.19] - 2025-08-10

### Added
- [2025-08-10] **Triple Filter System for Technical Analysis**: Implemented comprehensive filtering system for heating stocks with data metrics
  - **Foreign Transaction Filter**: "Foreign Buy > Sell Only" checkbox filters for `foreign_transaction == 'Buy > Sell'`
  - **Strong Buy Signal Filter**: "Strong Buy Signal Only" checkbox filters for `tcbs_buy_sell_signal == 'Strong buy'`
  - **Buy Signal Filter**: "Buy Signal Only" checkbox filters for `tcbs_buy_sell_signal == 'Buy'`
  - **Independent Toggles**: All three filters can be used independently or in combination for precise stock selection
  - **Dynamic Filter Feedback**: Real-time filter results with stock counts showing progressive filtering effects
  - **Intelligent Warning Messages**: Context-aware warnings when no stocks match selected filter criteria
  - **Sequential Filter Logic**: Filters applied in sequence (Foreign → Strong Buy → Buy) with transparent progress tracking
  - **Smart UI Integration**: All filters integrated in sidebar "📈 Data Filters" section with helpful tooltips

### Added
- [2025-08-10] **Dual Trading Value Metrics Display**: Added comprehensive trading volume analytics with side-by-side metrics layout
  - **Average 5-Day Trading Value**: Displays mean of `avg_trading_value_5d` across all filtered heating stocks
  - **Average Total Trading Value**: Displays mean of `total_trading_value` across all filtered heating stocks
  - **Raw Value Display**: Shows actual trading values with comma formatting (no conversion to billions)
  - **Dynamic Updates**: Both metrics automatically recalculate when filters are applied/removed
  - **Responsive Layout**: Two-column layout (`st.columns(2)`) for optimal space utilization
  - **Error Handling**: Shows "N/A" for missing or invalid data with column existence validation
  - **Filter Responsive**: Trading metrics reflect only the stocks that match current filter criteria

### Changed
- [2025-08-10] **DataFrame Display Enhancement**: Removed index column from heating stocks DataFrame for cleaner presentation
  - **Clean Display**: Added `hide_index=True` parameter to `st.dataframe()` for heating stocks summary table
  - **Focus on Data**: Eliminates distracting row numbers to focus attention on actual stock information
  - **Consistent Styling**: Maintains full width (`use_container_width=True`) and fixed height (`height=300`) for optimal viewing

### Technical Implementation
- **Filter Architecture**: Simple string comparison filters with boolean masking for optimal performance
  - `heating_stocks['foreign_transaction'] == 'Buy > Sell'` for foreign investor filter
  - `heating_stocks['tcbs_buy_sell_signal'] == 'Strong buy'` for TCBS strong buy filter  
  - `heating_stocks['tcbs_buy_sell_signal'] == 'Buy'` for TCBS buy filter
- **Progressive Filtering**: Each filter operates on the results of previous filters with count tracking at each stage
- **User Feedback System**: Comprehensive messaging system showing active filters and stock counts
- **Session State Integration**: Filter states persist across page interactions using Streamlit session state
- **Trading Metrics Calculation**: Uses pandas `.mean()` with null value handling and comma formatting

### User Experience Improvements
- **Precision Filtering**: Users can find exact stocks matching their investment criteria using multiple filter combinations
- **Visual Feedback**: Clear indication of how many stocks match each filter combination with original stock count reference
- **Professional Interface**: Clean, institutional-grade filtering system with professional tooltips and descriptions
- **Trading Volume Insights**: Immediate understanding of average trading liquidity across filtered stock selections
- **Streamlined Display**: Clean DataFrame presentation focuses attention on stock data rather than technical details

### Files Modified
- `pages/Technical_Analysis.py`: Added triple filter system, trading value metrics, and DataFrame display enhancements with comprehensive filter logic and UI improvements

## [0.2.18] - 2025-08-10

### Fixed
- [2025-08-10] **Technical Analysis TypeError and ValueError Fixes**: Comprehensive error handling implementation for pandas-ta integration
  - **Primary Issue**: `TypeError: 'NoneType' object is not subscriptable` when pandas-ta functions returned None instead of DataFrames
  - **Secondary Issue**: `ValueError: zero-size array to reduction operation maximum` when turning on ADX indicator
  - **Root Causes**: 
    - pandas-ta functions returning None for insufficient data, then code attempting subscript access
    - ADX calculation requiring more data than other indicators (30+ points vs 14-20)
    - Daily interval (1D) only providing 30 days of data, insufficient for reliable ADX calculation
  - **Solution Implementation**:
    - **Enhanced `calculate_indicators()` function**: Individual None checks for all 5 indicators (RSI, MACD, Bollinger Bands, OBV, ADX)
    - **Specific ADX Validation**: Minimum 30 data points, High/Low consistency checks, sufficient price variation validation
    - **Safe Chart Creation**: Protected `create_technical_chart()` with comprehensive indicator validation
    - **Protected Display Sections**: Safe metric display with "N/A" values and explanatory captions instead of crashes
    - **Optimized Date Ranges**: Daily (1D) increased from 30 to 90 days for sufficient ADX calculation data
    - **Transparent Error Handling**: Clear warning messages explaining why indicators failed with specific reasons
  - **Files Modified**: 
    - `pages/Technical_Analysis.py` - comprehensive error handling for all indicators and chart creation
  - **User Experience**: Graceful degradation with clear feedback, app continues working with available indicators
  - **Technical Result**: Production-ready Technical Analysis page with robust pandas-ta integration

## [0.2.17] - 2025-08-10

### Added
- [2025-08-10] **Single Source of Truth for Date Consistency**: Implemented centralized date management across all analysis pages
  - **Issue**: Inconsistent date defaults between Stock Price Analysis (hardcoded 2024-12-31) and Portfolio Optimization (today-1)
  - **Root Cause**: Each page had independent date selection with different default values, causing data inconsistency
  - **Solution**: Centralized date management in session state with synchronized sidebar date selection
  - **Implementation Changes**:
    - **Global Date Session State**: Added `analysis_start_date`, `analysis_end_date`, and `date_range_changed` variables
    - **Standardized today-1 Default**: All pages now use `pd.to_datetime("today") - pd.Timedelta(days=1)` as end_date default
    - **Smart Cache Invalidation**: Automatic cache refresh when date ranges change to ensure data consistency
    - **Synchronized Sidebar Selection**: Date changes in any page automatically apply to all analysis pages
  - **Files Modified**: 
    - `pages/Stock_Price_Analysis.py` - replaced hardcoded dates with session state management
    - `pages/Portfolio_Optimization.py` - connected existing date inputs to session state
    - `README.md` - documented new date-related session state variables
  - **Result**: Consistent date ranges across all pages ensure comparable analysis and eliminate data mismatch issues

## [0.2.16] - 2025-08-10

### Fixed
- [2025-08-10] **Portfolio Strategy Consistency Issue**: Fixed confusing UX where users had to repeatedly select portfolio strategies across 3 different tabs
  - **Issue**: Users encountered 3 separate portfolio selection widgets (Tab 3, Tab 4, Tab 5) causing confusion and inconsistent analysis
  - **Root Cause**: Each analysis tab (Dollar Allocation, Report, Risk Analysis) had independent strategy selection widgets
  - **Solution**: Implemented two-level single source of truth hierarchy:
    - **Level 1**: Sidebar multiselect for symbol selection (already perfect)
    - **Level 2**: Tab 4 (Report) radio button as master control for portfolio strategy selection
  - **Implementation Changes**:
    - **Tab 4 Enhancement** (lines 550-559): Enhanced radio button as master control center with session state storage
    - **Tab 3 Refactor** (lines 462-472): Removed selectbox, reads strategy from session state with user guidance
    - **Tab 5 Refactor** (lines 646-656): Removed selectbox, reads strategy from session state with user guidance
  - **User Guidance**: Added informational messages directing users to Report tab for strategy selection
  - **Session State Integration**: `st.session_state.portfolio_strategy_choice` provides consistent strategy across all tabs
  - **Files Modified**: `pages/Portfolio_Optimization.py` - updated portfolio strategy selection logic across all three tabs
  - **Result**: Single strategy selection workflow eliminates confusion and ensures consistent analysis across all tabs

### Changed
- [2025-08-10] **Portfolio Analysis Workflow Enhancement**: Streamlined user experience with clear hierarchy and guidance
  - **Two-Level Hierarchy**: **symbols → strategy → analysis** creates logical progression through portfolio optimization
  - **Master Control**: Tab 4 (Report) serves as strategy selection hub for all strategy-dependent analysis tabs
  - **User Navigation**: Clear guidance messages help users understand the selection flow and current strategy
  - **Consistent Analysis**: All tabs (Dollar Allocation, Report, Risk Analysis) use identical portfolio strategy ensuring comparable results
  - **Session Persistence**: Strategy selection persists across tab navigation maintaining user context

### Session State Architecture Enhancement
Finance Bro's comprehensive session state management enables seamless data sharing and persistence across all pages and tabs:

**New Portfolio Strategy Variable**
- **Added**: `st.session_state.portfolio_strategy_choice` - Master control for portfolio strategy selection across all analysis tabs
- **Scope**: Shared between Tab 3 (Dollar Allocation), Tab 4 (Report), and Tab 5 (Risk Analysis)
- **Pattern**: Master-slave architecture where Tab 4 writes, other tabs read from session state

**Existing Session State Variables Used**
- `st.session_state.stock_symbol` - Current stock symbol shared across all pages
- `st.session_state.portfolio_returns` - Stock returns data shared across portfolio tabs  
- `st.session_state.weights_max_sharpe` - Max Sharpe portfolio weights
- `st.session_state.weights_min_vol` - Min Volatility portfolio weights
- `st.session_state.weights_max_utility` - Max Utility portfolio weights

**Cross-Tab Communication Pattern**
- **Master Control**: Tab 4 radio button stores selection in `st.session_state.portfolio_strategy_choice`
- **Slave Tabs**: Tab 3 and Tab 5 read strategy from session state instead of having independent widgets
- **Fallback Logic**: Default to "Max Sharpe Portfolio" when session state unavailable
- **User Guidance**: Clear messages directing users to Report tab for strategy selection

### Technical Implementation
- **Session State Management**: Centralized portfolio strategy storage in `st.session_state.portfolio_strategy_choice`
- **User Interface**: Enhanced radio button with help text explaining master control functionality
- **Code Cleanup**: Removed redundant selection widgets while maintaining all existing functionality
- **State Persistence**: Strategy selection persists across tab navigation and page refreshes

### User Experience Improvements
- **Elimination of Confusion**: Single strategy selection point removes need to remember and synchronize choices across tabs
- **Clear Information Flow**: Logical progression from symbol selection to strategy selection to analysis results
- **Reduced Cognitive Load**: Users focus on analysis rather than managing multiple selection interfaces
- **Consistent Results**: All analysis tabs guaranteed to use same strategy ensuring meaningful comparisons
- **Professional Workflow**: Streamlined interface matches institutional portfolio analysis tools

## [0.2.15] - 2025-08-09

### Fixed
- [2025-08-09] **Portfolio Optimization Excel Report Double Extension Bug**: Fixed critical Excel report generation issue causing download failures
  - **Issue**: Excel reports generated with double extensions (.xlsx.xlsx) due to riskfolio-lib automatically adding .xlsx to filenames
  - **Root Cause**: `rp.excel_report()` function automatically appends .xlsx extension, but code was providing filenames already containing .xlsx
  - **Symptoms**: 
    - Report generation appeared successful with success message
    - Actual files created with double extension in exports/reports/ directory
    - Download button failed with "No such file or directory" error
    - Page jumping back to "Efficient Frontier & Weights" tab due to Streamlit error handling
  - **Solution**: Modified filename construction logic in Report tab (lines 582-612):
    - Changed `filename = f"{portfolio_name}_{timestamp}.xlsx"` to `filename_base = f"{portfolio_name}_{timestamp}"`
    - Pass `filepath_base` (without extension) to `rp.excel_report()`
    - Construct `filepath_xlsx = filepath_base + ".xlsx"` for file operations
    - Updated download button and file size calculation to use correct .xlsx path
  - **Files Modified**: `pages/Portfolio_Optimization.py` - updated Excel report generation logic in tab4
  - **Result**: Excel reports now generate with single .xlsx extension, downloads work correctly, no page jumping

### Added
- [2025-08-09] **Comprehensive Test Suite for Portfolio Optimization**: Created automated testing framework for terminal-based validation
  - **Test Infrastructure**: Created `tests/` directory with pytest-based testing framework
  - **Test Coverage**: 12 comprehensive tests covering filename construction, file path management, Excel report generation workflow
  - **Mock Integration**: Added pytest-mock for testing riskfolio-lib integration without external dependencies  
  - **Sample Data**: Created realistic stock data fixtures for testing portfolio optimization logic
  - **Dependencies**: Added pytest, pytest-cov, pytest-mock to development dependencies
  - **Demo Script**: Created `tests/demo_fix.py` to demonstrate fix functionality without running Streamlit app
  - **Files Created**: 
    - `tests/__init__.py`, `tests/conftest.py`, `tests/test_portfolio_optimization.py`
    - `tests/demo_fix.py` - standalone demonstration script
  - **Test Execution**: Run with `uv run pytest tests/` for complete validation

### Technical Implementation
- **Filename Construction**: Separated base filename (without extension) from display filename (with extension)
- **API Integration**: Proper integration with riskfolio-lib expecting filenames without extensions
- **Error Prevention**: Eliminated double extension creation while maintaining all existing functionality  
- **Test Validation**: All 12 tests pass with 99% code coverage, confirming fix effectiveness
- **Backward Compatibility**: Maintains all existing report features and user interface elements

### User Experience Improvements
- **Reliable Downloads**: Excel report downloads now work consistently without errors
- **No Interface Disruption**: Report generation stays on Report tab without unexpected navigation
- **Professional Output**: Generated Excel files have proper single .xlsx extension
- **Validation Confidence**: Comprehensive test suite ensures fix reliability and prevents regression

## [0.2.14] - 2025-08-08

### Added
- [2025-08-08] **Comprehensive QuantStats Custom Metrics Selector**: Implemented advanced custom metrics interface with 75 QuantStats metrics
  - **Organized Categories**: 7 logical metric categories (Core Performance, Risk Analysis, Return Analysis, Advanced Ratios, Rolling Metrics, Specialized)
  - **Smart Multi-Select Interface**: Category-based dropdown with intelligent defaults for Core Performance metrics
  - **Professional Metric Formatting**: Custom `format_metric_name()` function converts snake_case to readable names with special cases (CAGR, VaR, CVaR, etc.)
  - **Responsive Grid Layout**: User-configurable grid columns (2, 3, or 4 columns) for optimal metric display
  - **Educational Descriptions**: Optional metric descriptions via `get_metric_descriptions()` with hover help tooltips
  - **Advanced Calculations**: `calculate_custom_metrics()` function with error handling and appropriate number formatting
  - **Performance-Based Formatting**: Intelligent formatting based on metric type (percentages, ratios, decimals)
  - **Session State Integration**: Seamlessly uses existing `st.session_state.stock_returns` data
  - **User Control Features**: Include descriptions toggle, customizable grid layout, category-based filtering

### Fixed
- [2025-08-08] **QuantStats Pandas Compatibility Issue**: Fixed "Invalid frequency: ME" error by downgrading to compatible QuantStats version
  - **Issue**: QuantStats latest versions use pandas 2.0+ frequency aliases (`ME`, `QE`, `YE`) incompatible with pandas 1.5.3
  - **Root Cause**: App uses pandas 1.5.3 for PandasAI compatibility, but newer QuantStats expects pandas 2.0+ frequency conventions
  - **Solution**: Downgraded to QuantStats 0.0.59, the last version compatible with pandas 1.5.3 legacy frequency aliases
  - **Implementation**: 
    - Added `quantstats==0.0.59` to requirements.txt for version pinning
    - Removed broken pandas compatibility patches from Stock_Price_Analysis.py (lines 13-28)
    - Added fallback logic for QuantStats file export path handling
  - **Chart Rendering Fix**: Replaced `st.html()` with `streamlit.components.v1.html()` for proper tearsheet visualization
    - **Issue**: Charts in QuantStats tearsheets were not visible, only performance metrics displayed
    - **Solution**: Used iframe rendering with `components.html(html_content, height=2000, scrolling=True)` for better JavaScript/CSS support
    - **Result**: Full tearsheet now displays with all charts, graphs, and performance analytics visible

### Changed
- [2025-08-08] **Dependency Management Enhancement**: Updated critical dependencies documentation
  - **CLAUDE.md**: Added quantstats to critical dependencies list with version compatibility notes
  - **Version Constraints**: Documented that QuantStats 0.0.60+ requires pandas 2.0+ and is incompatible with app's pandas 1.5.3
  - **Compatibility Notes**: Added explanation of frequency alias changes between pandas versions
  - **Warning Enhancement**: Updated dependency upgrade warning to include quantstats alongside pandas and pandasai

### Technical Implementation
- **Version Pinning**: `quantstats==0.0.59` ensures compatibility with pandas 1.5.3 legacy frequency aliases (`M`, `Q`, `A`)
- **File Path Handling**: Added fallback logic to handle QuantStats 0.0.59's behavior of exporting to project root with default filename
- **Chart Rendering**: Iframe-based HTML display provides proper JavaScript execution environment for embedded charts
- **Code Cleanup**: Removed 15 lines of broken pandas compatibility patches and warning suppressions

### User Experience Improvements
- **Advanced Metrics Analysis**: Users can select from 75 professional-grade QuantStats metrics organized by category
- **Customizable Display**: Flexible grid layout and optional descriptions for personalized analytics experience
- **Intelligent Defaults**: Smart metric preselection for common performance analysis workflows
- **Reliable Tearsheet Generation**: QuantStats tearsheets now generate without pandas frequency errors
- **Complete Visualization**: All charts, performance metrics, and analytical plots display correctly in tearsheets
- **Professional Output**: Full-featured tearsheets with comprehensive portfolio analytics comparable to institutional tools
- **Download Functionality**: Generated HTML tearsheets available for download with proper formatting

### Files Modified
- `requirements.txt`: Added quantstats version pin
- `pages/Stock_Price_Analysis.py`: Removed compatibility patches, added file path fallback, improved chart rendering, implemented comprehensive custom metrics selector
- `CLAUDE.md`: Updated critical dependencies documentation with quantstats compatibility notes

## [0.2.13] - 2025-08-08

### Added
- [2025-08-08] **Comprehensive Riskfolio-lib Risk Analysis Suite**: Expanded Risk Analysis tab with three comprehensive risk visualization tools
  - **Risk Analysis Table**: Uses `rp.plot_table()` for comprehensive risk metrics table (Expected Return, Volatility, Sharpe Ratio, VaR, CVaR, Max Drawdown, Calmar Ratio)
  - **Portfolio Drawdown Analysis**: Added `rp.plot_drawdown()` visualization showing cumulative returns and drawdown periods with recovery analysis
  - **Portfolio Returns Risk Measures**: Implemented `rp.plot_range()` for histogram and risk range analysis with return distributions, VaR, and CVaR visualizations
  - **Unified Data Integration**: All three analyses use same session state returns and weights for consistent portfolio analysis
  - **Multi-Portfolio Support**: Portfolio selection dropdown allows risk analysis for Max Sharpe, Min Volatility, and Max Utility portfolios
  - **Professional Visualization**: Each analysis uses proper matplotlib figure sizing and styling for publication-quality outputs

### Changed
- [2025-08-08] **Risk Analysis Tab Enhancement**: Expanded from single risk table to comprehensive three-analysis suite
  - **Sequential Layout**: Risk metrics table → Drawdown analysis → Returns risk measures for logical analysis flow
  - **Consistent Parameters**: All analyses use alpha=0.05 for 95% confidence intervals and standardized riskfolio parameters
  - **Educational Content**: Maintained informational expander explaining risk metrics for user understanding

### Technical Implementation
- **Riskfolio Integration**: Three riskfolio functions integrated with consistent parameter handling:
  - `rp.plot_table()`: MAR=0, alpha=0.05 for risk metrics table
  - `rp.plot_drawdown()`: alpha=0.05, kappa=0.3, solver='CLARABEL', height_ratios=[2,3] for drawdown visualization
  - `rp.plot_range()`: alpha=0.05, a_sim=100, bins=50 for return distribution analysis
- **Session State Reuse**: All analyses leverage existing `st.session_state.portfolio_returns` and portfolio weights
- **DataFrame Consistency**: Same `weights_df` DataFrame format used across all three analyses for data consistency
- **Figure Management**: Separate matplotlib figures for each analysis (fig, fig_drawdown, fig_range) to prevent conflicts

### User Experience Improvements
- **Complete Risk Assessment**: Users get comprehensive risk analysis suite covering metrics, drawdowns, and return distributions
- **Visual Progression**: Logical flow from tabular metrics to visual drawdown analysis to statistical distributions
- **Portfolio Flexibility**: Any optimized portfolio can be analyzed with all three risk visualization tools
- **Professional Output**: Publication-quality risk analysis charts suitable for investment presentations
- **Educational Value**: Combined risk metrics provide deep insights into portfolio risk characteristics

### Files Modified
- `pages/Portfolio_Optimization.py`: Expanded Risk Analysis tab with drawdown and range analysis implementations

## [0.2.12] - 2025-08-08

### Added
- [2025-08-08] **Riskfolio-lib Risk Analysis Table**: Added comprehensive risk analysis visualization to Portfolio Optimization page
  - **New Tab**: Added "📋 Risk Analysis" as 5th tab alongside existing portfolio analysis tabs
  - **Risk Metrics Table**: Integrated `rp.plot_table()` function from riskfolio-lib for comprehensive risk assessment
  - **Data Integration**: Uses session state `portfolio_returns` and all three portfolio weights for seamless data flow
  - **DataFrame Conversion**: Automatic conversion of weights dictionary to DataFrame format required by riskfolio-lib
  - **Matplotlib Integration**: Professional risk analysis table displayed via matplotlib with proper figure sizing (12x8)
  - **Session State Management**: Stores `weights_max_sharpe` dictionary in session state for cross-tab access
  - **User Education**: Informational expander explaining risk metrics (VaR, CVaR, Calmar Ratio, Max Drawdown, etc.)
  - **Error-Free Debugging**: Removed try-except blocks to allow on-screen error display for development

### Changed
- [2025-08-08] **Portfolio Optimization Tab Structure**: Expanded from 4 to 5 tabs for better analysis organization
  - **Tab Layout**: Updated tab definition to include Risk Analysis as 5th tab
  - **Tab Names**: "📈 Efficient Frontier & Weights", "🌳 Hierarchical Risk Parity", "💰 Dollars Allocation", "📊 Report", "📋 Risk Analysis"
  - **Session State Storage**: Simplified weights storage from Series conversion to direct dictionary storage
  - **Data Requirements**: Risk Analysis tab validates both `portfolio_returns` and `weights_max_sharpe` availability

### Technical Implementation
- **Riskfolio Integration**: Uses `rp.plot_table()` with parameters: returns, weights DataFrame, MAR=0, alpha=0.05
- **Weight Processing**: Converts weights dictionary to DataFrame using `pd.DataFrame.from_dict()` with `orient='index'`
- **Variable Naming**: Clear variable naming with `weights_max_sharpe_df` for DataFrame representation
- **Session State Efficiency**: Direct dictionary storage eliminates unnecessary Series intermediate conversion
- **Error Handling**: Removed try-except blocks for transparent error display during development

### User Experience Improvements
- **Multi-Portfolio Risk Analysis**: Users can analyze risk metrics for any portfolio strategy (Max Sharpe, Min Volatility, Max Utility)
- **Portfolio Selection Interface**: Intuitive dropdown to choose which optimized portfolio to analyze
- **Professional Risk Table**: Industry-standard risk analysis table with multiple risk measures for selected portfolio
- **Dynamic Context**: Educational content updates to reflect the selected portfolio (e.g., "your Min Volatility portfolio")
- **Seamless Integration**: Risk analysis automatically available after portfolio optimization completion
- **Visual Consistency**: Risk table maintains consistent styling with existing portfolio analysis

### Files Modified
- `pages/Portfolio_Optimization.py`: Added riskfolio risk analysis tab, session state management, and DataFrame conversion logic

## [0.2.11] - 2025-08-08

### Added
- [2025-08-08] **Hierarchical Risk Parity (HRP) Portfolio Optimization**: Added comprehensive HRP analysis with dendrogram visualization
  - **HRP Implementation**: Integrated `pypfopt.HRPOpt` for hierarchical risk parity portfolio optimization using clustering-based approach
  - **Dendrogram Visualization**: Added interactive dendrogram chart using `plotting.plot_dendrogram()` with ticker symbols display
  - **Portfolio Weights Display**: HRP portfolio weights shown in formatted table with percentage values
  - **Tab-Based Interface**: Added dedicated "🌳 Hierarchical Risk Parity" tab alongside existing "📈 Efficient Frontier & Weights" tab
  - **Session State Integration**: Returns data stored in `st.session_state.portfolio_returns` for cross-tab data sharing
  - **Separation of Concerns**: HRP analysis cleanly separated from Modern Portfolio Theory content in dedicated tab
  - **Real Data Testing**: Designed for testing with actual Vietnamese stock market data via vnstock API

- [2025-08-08] **Discrete Portfolio Allocation**: Added comprehensive discrete allocation functionality with Vietnamese market integration
  - **DiscreteAllocation Implementation**: Integrated `pypfopt.discrete_allocation.DiscreteAllocation` for realistic portfolio allocation
  - **Portfolio Value Input**: User-configurable portfolio value with Vietnamese Dong (VND) denomination and sensible defaults
  - **Strategy Selection**: Dropdown to choose allocation strategy from Max Sharpe, Min Volatility, or Max Utility portfolios
  - **Latest Prices Integration**: Uses `get_latest_prices()` with proper Vietnamese market price conversion (multiply by 1000)
  - **Greedy Allocation Algorithm**: Implements `greedy_portfolio()` method for optimal share allocation within budget constraints
  - **Comprehensive Results Display**: Shows allocation table with shares, prices, total values, and weight percentages
  - **Summary Metrics**: Three-column layout displaying allocated amount, leftover cash, and number of stocks
  - **Investment Summary**: Professional overview with strategy details and allocation breakdown
  - **Vietnamese Market Formatting**: Proper VND currency formatting with thousand separators for professional presentation

### Changed
- [2025-08-08] **Portfolio Optimization Page Restructuring**: Reorganized content into tab-based layout for better user experience
  - **Tab Architecture**: Split single-page content into two focused tabs:
    - **Tab 1**: "📈 Efficient Frontier & Weights" - Contains all existing MPT analysis (efficient frontier plot, portfolio weights tables, pie charts, performance analysis)
    - **Tab 2**: "🌳 Hierarchical Risk Parity" - Contains HRP optimization and dendrogram visualization
  - **Content Organization**: Moved efficient frontier, weights comparison, pie charts, and performance tables to first tab
  - **Main Page Preservation**: Data summary and performance metrics remain in main content area above tabs
  - **User Workflow**: Users can easily switch between traditional MPT analysis and modern HRP approach

### Technical Implementation
- **Import Enhancement**: Added `HRPOpt` to existing pypfopt imports for hierarchical clustering functionality
- **Session State Management**: Portfolio returns calculated once and stored for reuse across analysis methods
- **Error Handling**: Basic validation with user-friendly warnings when returns data unavailable
- **Data Flow**: Seamless integration with existing portfolio optimization workflow and caching system
- **Chart Integration**: Dendrogram uses matplotlib with consistent styling and responsive design

### User Experience Improvements
- **Progressive Analysis**: Users can perform traditional MPT analysis first, then explore HRP approach using same data
- **Visual Insights**: Dendrogram provides intuitive visualization of asset clustering and hierarchical relationships
- **Comparative Analysis**: Easy switching between MPT and HRP approaches for comprehensive portfolio analysis
- **Professional Interface**: Clean tab separation maintains focus while providing access to different optimization strategies

### Files Modified
- `pages/Portfolio_Optimization.py`: Added HRP import, session state storage, tab structure, and HRP implementation

## [0.2.10] - 2025-08-06

### Changed
- [2025-08-06] **Chart Color Scheme Unification**: Updated visualization colors across Screener and Company Overview pages for consistent branding
  - **Screener Page**: Updated Distribution Charts tab histograms to use `#AAA39F` color (previously steelblue)
  - **Screener Page**: Updated Filtering Breakdown chart to use `#AAA39F` color (previously steelblue)
  - **Company Overview**: Updated "Ownership by Share Quantity" chart to use `#56524D` color (previously black)
  - **Company Overview**: Updated "Management Team Share Ownership" chart to use `#56524D` color (previously black)
  - **Grid Removal**: Removed grid lines from Distribution Charts histograms by setting `axis=alt.Axis(grid=False)` on both x and y axes
  - **Visual Consistency**: All ownership and distribution charts now follow unified color scheme across the application
  - **Files Modified**: `pages/Screener.py`, `pages/Company_Overview.py`
  - **Result**: More cohesive visual branding and cleaner chart appearance without grid distractions

### Fixed
- [2025-08-06] **Sidebar UI Cleanup**: Removed redundant "Current Symbol" display from main app sidebar
  - **Issue**: Sidebar showed current stock symbol status, which was redundant since symbol selection is prominently displayed on main page
  - **Solution**: Removed "Current Symbol" check and display section from app.py sidebar
  - **Files Modified**: `app.py` lines 194-197 - removed stock symbol status display from sidebar controls
  - **Result**: Cleaner sidebar interface without redundant information display

## [0.2.9] - 2025-08-06

### Changed
- [2025-08-06] **Stock Symbol Selection Interface Enhancement**: Replaced multiselect with selectbox for cleaner single selection UX
  - **UI Component Change**: Replaced `st.multiselect` with `st.selectbox` for more intuitive single stock selection
    ```python
    # Before: Multiselect with max_selections=1
    selected_symbols = st.multiselect(
        "Search and select a stock symbol:",
        options=stock_symbols_list,
        default=[st.session_state.stock_symbol] if 'stock_symbol' in st.session_state else ["REE"],
        max_selections=1
    )
    
    # After: Clean selectbox implementation
    current_symbol = st.selectbox(
        "Search and select a stock symbol:",
        options=stock_symbols_list,
        index=stock_symbols_list.index(st.session_state.stock_symbol) if 'stock_symbol' in st.session_state else 0
    )
    ```
  - **Index-Based Selection**: Uses proper index parameter to maintain current selection state
  - **Clear Button Update**: Modified clear selection to reset to default symbol instead of deletion
  - **Files Modified**: `app.py` lines 85-99, 115 - replaced multiselect with selectbox and updated clear logic
  - **Result**: More intuitive stock selection interface with native single-selection behavior

### Fixed
- [2025-08-06] **Company Officers API Parameter Error**: Fixed `Company.officers()` unexpected keyword argument error
  - **Issue**: `Company.officers()` method was being called with `lang='en'` parameter causing API errors
  - **Root Cause**: vnstock `Company.officers()` method doesn't accept language parameter
  - **Solution**: Removed `lang='en'` parameter from `company.officers()` call
    ```python
    # Before: Caused "unexpected keyword argument 'lang'" error
    return company.officers(lang='en')
    
    # After: Clean method call without parameters
    return company.officers()
    ```
  - **Files Modified**: `pages/Company_Overview.py` line 26 - updated get_management_data function
  - **Result**: Management Team tab now loads successfully without API parameter errors

### Technical Implementation
- **Selectbox Integration**: Proper index calculation for maintaining selection state across page refreshes
- **Session State Handling**: Simplified session state management with direct value assignment from selectbox
- **Clear Selection Logic**: Modified to reset to default symbol rather than clearing state entirely
- **API Compatibility**: Ensured vnstock Company class method calls match actual API signatures

### User Experience Improvements
- **Native Selection UX**: Selectbox provides standard dropdown behavior users expect for single selection
- **Faster Selection**: No need for complex multiselect configuration or selection extraction logic
- **Error Elimination**: Removed Company Officers API errors that were blocking Management Team data
- **Consistent Behavior**: Clear button now maintains consistent selection state rather than empty state
- **Cleaner Chart Visuals**: Removed data labels from ownership charts for less cluttered visualization

### Changed
- [2025-08-06] **Company Overview Chart Simplification**: Removed percentage data labels from ownership bar charts
  - **Main Ownership Chart**: Removed text labels showing percentage values next to bars in "Ownership by Share Quantity" chart
  - **Subsidiaries Chart**: Removed text labels showing percentage values next to bars in "Subsidiaries Ownership Percentage" chart
  - **Tooltip Preservation**: Percentage information still accessible via interactive tooltips on hover
  - **Visual Improvement**: Charts now display cleaner with less visual clutter while maintaining data accessibility
  - **Files Modified**: `pages/Company_Overview.py` lines 133-134, 276-277 - removed text label creation and combination
  - **Result**: More professional and readable ownership visualization charts

## [0.2.8] - 2025-08-06

### Added
- [2025-08-06] **Advanced Stock Screening Filters**: Added 6 new sophisticated filters for comprehensive stock analysis
  - **Beta Filter** (0.0-3.0): Market volatility coefficient with smart defaults (0.5-2.0) for risk assessment
  - **Alpha Filter** (-50 to +50): Performance vs market benchmark with intelligent range selection (-10 to +10)
  - **Financial Health Filter** (0-10): Overall financial health score for company stability analysis
  - **Business Model Filter** (0-10): Business model quality score for strategic assessment
  - **Business Operation Filter** (0-10): Operational efficiency score for performance evaluation
  - **Stock Rating Filter** (0-10): Overall stock rating for investment grade classification
  - **Client-Side Processing**: All new filters use efficient client-side filtering with same performance as existing filters
  - **Preset Integration**: New filters fully integrated with existing preset system and session state management

### Changed
- [2025-08-06] **Enhanced Quick Filter Presets**: Replaced "High Dividend Stocks" with sophisticated "Low Risk Quality" preset
  - **🛡️ Low Risk Quality**: Targets conservative investors seeking quality stocks
    - Financial Health > 7.0 (strong fundamentals)
    - Beta < 1.2 (lower volatility than market)  
    - Stock Rating > 6.0 (investment grade)
  - **Smart Defaults**: Preset automatically configures optimal ranges for risk-averse investors
  - **Immediate Execution**: Auto-runs screener with preset parameters for instant results

- [2025-08-06] **Revolutionary Summary Metrics**: Replaced traditional averages with impactful range-based metrics
  - **Beta Range**: Shows portfolio risk spectrum (e.g., "0.5 - 2.1") for immediate risk assessment
  - **Health Range**: Displays quality spectrum (e.g., "4.2 - 9.8") showing company health diversity
  - **Rating Range**: Shows investment grade spread (e.g., "3.1 - 8.9") for quality distribution
  - **Smart Fallbacks**: Automatically falls back to original metrics when new data isn't available
  - **Instant Insights**: Users immediately understand portfolio diversity and risk/quality characteristics

- [2025-08-06] **Comprehensive Visualization Enhancement**: Added 2 new analysis tabs with professional insights
  - **Risk Analysis Tab**: Beta vs Alpha scatter plot with market performance insights
    - Sweet spot identification: Low Beta (<1.0) + High Alpha (>0) = Low risk with market outperformance
    - Beta guidelines: Defensive (<0.8), Market-like (0.8-1.2), High volatility (>1.2)
    - Alpha interpretation: Positive (outperforming), Negative (underperforming)
  - **Quality Scores Tab**: Financial Health vs Business Model analysis
    - Quality leader identification: High Financial Health (>7) + High Business Model (>7) = Strong fundamentals
    - Score guidelines: Excellent (8-10), Good (6-8), Average (4-6), Below average (<4)
  - **Enhanced Distribution Charts**: Added 3 new histograms (Beta, Alpha, Financial Health, Stock Rating)
    - 2x3 grid layout showing comprehensive metric distributions
    - Professional styling with consistent color schemes

### Technical Implementation
- **Filter Architecture**: All 6 new filters follow existing client-side pattern for consistency
  - Checkbox activation → Slider range selection → Dictionary storage → Loop processing
  - Same filtering visualization with new metrics in funnel breakdown chart
  - Identical performance characteristics to existing filters
- **Active Filters Integration**: Updated active filters summary to include all new filter types
- **Data Table Enhancement**: Added new columns with appropriate formatting
  - Beta/Alpha: 3 decimal places for precision in risk metrics
  - Quality scores: 1 decimal place for readability in business metrics
  - Maintains 2 decimal places for existing financial metrics
- **Visualization Framework**: Extended existing Altair charts to handle new risk and quality dimensions
- **Session State Management**: Seamless integration with existing preset system and filter persistence

### User Experience Improvements
- **Advanced Risk Analysis**: Users can now screen for specific risk profiles using beta and alpha metrics
- **Quality Assessment**: Comprehensive evaluation of business fundamentals through health and operation scores
- **Sophisticated Presets**: One-click access to professionally configured filter combinations
- **Visual Storytelling**: Range-based metrics immediately communicate portfolio characteristics
- **Professional Insights**: Expert guidance provided for interpreting risk, quality, and rating metrics
- **Intuitive Interface**: New filters seamlessly integrate with familiar screening workflow

### Performance & Compatibility
- **Filter Order Independence**: Final results identical regardless of filter application sequence
- **Efficient Processing**: Client-side filtering maintains fast performance with larger datasets
- **Backward Compatibility**: All existing functionality preserved while adding advanced capabilities
- **Data Availability**: Graceful handling when new metrics unavailable, falling back to traditional metrics
- **Memory Efficiency**: Reuses existing filtering infrastructure without additional memory overhead

## [0.2.7] - 2025-08-06

### Fixed
- [2025-08-06] **Quick Filter Preset Isolation**: Fixed filter preset buttons accumulating parameters from previous selections
  - **Issue**: Clicking "High Dividend Stocks" then "Growth Stocks" would apply both sets of filters instead of replacing them
  - **Root Cause**: Preset buttons were only adding new session state variables without clearing previous preset values
  - **Solution**: Each preset button now clears all previous preset parameters before setting new ones
  - **Implementation**: Added preset cleanup loop (`for key in list(st.session_state.keys()): if key.startswith('preset_'): del st.session_state[key]`) to each preset button
  - **Files Modified**: `pages/Screener.py` - updated all Quick Filter Preset buttons (High Quality Banks, High Dividend Stocks, Growth Stocks)
  - **Result**: Each preset button now provides clean, isolated filtering without parameter accumulation from previous selections

### Changed
- [2025-08-06] **Stock Screener UI Enhancements**: Improved user experience with better layout and export functionality
  - **Visualization Priority**: Moved all visualizations above the screened stocks data table for immediate visual insights
  - **Layout Optimization**: Users now see charts and metrics first, followed by detailed stock data
  - **Export Enhancement**: Replaced CSV download with PNG visualization export functionality
  - **Direct Download**: Implemented single-click PNG download without popup confirmation dialogs
  - **Professional Charts**: Added matplotlib-based PNG generation with high-quality 300 DPI output
  - **Combined Visualization**: Creates single PNG file containing all available charts (ROE vs Market Cap, Market Cap vs Dividend Yield, Value vs Quality)
  - **Industry Color Coding**: Maintains industry-based color schemes with legends in exported PNG files
  - **Timestamped Files**: Automatic filename generation with timestamps to prevent download conflicts

### Technical Implementation
- **PNG Generation**: Custom matplotlib chart creation function for downloadable visualizations
  - High-quality 300 DPI output for professional presentation
  - Industry-based color coding with Set3 colormap
  - Hard-coded EV/EBITDA y-axis scaling (0-30) for consistent visualization
  - Automatic legend management (shows legends only for ≤10 industries)
  - Responsive subplot layout with proper spacing and grid styling
- **Direct Download**: Uses `st.download_button` with `image/png` MIME type for immediate file download
- **Error Handling**: Comprehensive error handling with fallback to screenshot recommendations
- **Layout Restructure**: Moved visualization tabs above data table in screener results display

### User Experience Improvements
- **Visual First**: Charts and insights appear immediately when screening results are available
- **Export Convenience**: Single-click download of professional-quality visualization files
- **No Popups**: Eliminated multi-step download process for better user flow
- **Professional Output**: High-resolution charts suitable for presentations and reports
- **Consistent Branding**: Maintained application color scheme and styling in exported files

### Fixed
- [2025-08-06] **Duplicate Login Button Issue**: Removed redundant authentication check in Stock Analysis page
  - **Issue**: Users were seeing two login buttons - one from main app and one from Stock Analysis page
  - **Root Cause**: Duplicate authentication handling in `pages/bro.py` lines 176-187 alongside main app authentication
  - **Solution**: Removed duplicate authentication check from Stock Analysis page since authentication is handled at app entry point
  - **Files Modified**: `pages/bro.py` - removed redundant authentication block and login button
  - **Result**: Clean single login flow with authentication properly centralized in main app

- [2025-08-06] **Duplicate Logout Button Issue**: Removed redundant logout button from Stock Analysis page
  - **Issue**: Users were seeing two logout buttons - one from main app sidebar and one from Stock Analysis page sidebar
  - **Root Cause**: Duplicate logout functionality in `pages/bro.py` lines 226-227 alongside main app logout button
  - **Solution**: Removed duplicate logout button from Stock Analysis page since logout is handled in main app
  - **Files Modified**: `pages/bro.py` - removed redundant logout button from sidebar
  - **Result**: Clean single logout flow with session management properly centralized in main app

## [0.2.6] - 2025-08-06

### Added
- [2025-08-06] **Foreign Transaction Analysis Tab**: Added comprehensive foreign trading data visualization to Company Overview page
  - **New Tab**: Added "Foreign Transaction" tab alongside Management Team, Subsidiaries, and Insider Deals tabs
  - **Data Integration**: Uses `vnstock.explorer.vci.Company` with `trading_stats()` method for comprehensive foreign trading data
  - **Enterprise Value Metric**: Displays Enterprise Value (EV) as primary metric from foreign trading data
  - **Foreign Holding Room Visualization**: Horizontal bar chart showing foreign room, foreign holding room, current holding room, and max holding room
  - **Summary Metrics**: Five-column layout displaying Foreign Volume, Total Volume, Foreign Room, Current Holding Ratio, and Max Holding Ratio
  - **Data Caching**: Added `get_foreign_trading_data()` function with 1-hour TTL caching to optimize API performance
  - **Error Handling**: Comprehensive error handling for missing foreign trading data with user-friendly messages

### Changed
- [2025-08-06] **UI Layout Improvements**: Enhanced Company Overview page layout for better user experience
  - **Visualization First**: Moved all visualizations above dataframes in Management Team, Subsidiaries, and Insider Deals tabs
  - **Consistent Layout**: All tabs now follow the pattern of visualization → metrics → dataframe display
  - **User Experience**: Visual insights now appear first, followed by detailed raw data tables
  - **Import Optimization**: Added `from vnstock.explorer.vci import Company` import for foreign trading functionality

### Technical Implementation
- **Foreign Trading Data Structure**: Complete access to 24-column foreign trading dataset including:
  - Basic trading metrics: symbol, exchange, price data, volume data
  - Foreign investor metrics: foreign_volume, foreign_room, foreign_holding_room, current_holding_ratio, max_holding_ratio
  - Enterprise valuation: ev (Enterprise Value)
  - Technical indicators: high_price_1y, low_price_1y, pct_low_change_1y, pct_high_change_1y
- **Visualization Architecture**: Altair-based horizontal bar charts with interactive tooltips and responsive design
- **Metrics Display**: Professional five-column layout with formatted numerical displays (thousands separators, percentages)
- **Session State Management**: Proper integration with existing stock symbol session state pattern

### User Experience Improvements
- **Visual Priority**: Charts and visualizations now appear first in all tabs for immediate insights
- **Foreign Investment Insights**: Users can quickly assess foreign investor activity and holding capacity
- **Enterprise Valuation**: Direct access to enterprise value metric for company valuation analysis
- **Comprehensive Foreign Data**: Full foreign trading dataset available in tabular format for detailed analysis
- **Consistent Navigation**: Foreign Transaction tab seamlessly integrated into existing Company Overview workflow

## [0.2.5] - 2025-08-05

### Added
- [2025-08-05] **Subsidiaries Visualization**: Added new subsidiaries tab with ownership percentage visualization
  - **New Tab**: Added "Subsidiaries" tab to Company Overview page alongside Management Team and Full Details
  - **Data Integration**: Uses `company.subsidiaries()` with columns: `organ_name`, `ownership_percent`, `type`
  - **Altair Visualization**: Horizontal bar chart showing subsidiaries ownership distribution with steelblue bars
  - **Summary Metrics**: Total subsidiaries count, subsidiaries with ownership data, and average ownership percentage
  - **Percentage Display**: Converted decimal ownership values (0.75) to percentage format (75.0%) for better readability
  - **Data Caching**: Added `get_subsidiaries_data()` function with 1-hour TTL caching to reduce API calls
  - **Error Handling**: Comprehensive error handling for missing subsidiaries data with user-friendly messages

### Changed
- [2025-08-05] **Ownership Data Display Enhancement**: Converted all ownership percentages from decimal to percentage format
  - **Main Ownership Chart**: Share ownership percentages now display as readable percentages (75.0% vs 0.75)
  - **Management Team Chart**: Officer ownership percentages converted to percentage format for consistency
  - **Summary Metrics**: Largest shareholder and top 3 combined metrics now show proper percentage values
  - **Chart Labels**: Updated text formatting to display percentage values without redundant % symbols
  - **User Experience**: All ownership data now consistently displayed in intuitive percentage format

## [0.2.4] - 2025-08-04

### Added
- [2025-08-04] **File Upload Integration**: Enhanced chat interface with CSV/Excel file upload support
  - **Upload Support**: Added `accept_file=True` parameter to `st.chat_input` with CSV and Excel file type filtering
  - **File Processing**: Automatic detection and loading of uploaded CSV (.csv) and Excel (.xlsx, .xls) files
  - **DataFrame Integration**: Uploaded files automatically added to PandasAI agent for analysis alongside stock data
  - **User Feedback**: Clear notifications showing successful file uploads with row counts
  - **Error Handling**: Comprehensive error handling for file loading failures with user-friendly messages
  - **Chat History**: File uploads properly tracked in chat history with file attachment indicators

### Changed
- [2025-08-04] **Agent Architecture Refactor**: Implemented lazy agent creation pattern to handle file uploads
  - **Lazy Loading**: Created `get_or_create_agent()` function to handle timing between chat input and agent creation
  - **Dynamic Updates**: Agent automatically recreates when new files are uploaded or dataframes change
  - **Session Caching**: Intelligent caching system prevents unnecessary agent recreation
  - **Scope Resolution**: Fixed agent availability issues across quick buttons and chat interface

- [2025-08-04] **Code Quality Enhancement**: Major code cleanup and refactoring for maintainability
  - **Helper Functions**: Extracted three key helper functions to eliminate ~150 lines of duplicate code:
    - `detect_latest_chart()`: Centralized chart detection logic
    - `process_agent_response()`: Unified agent response processing with error handling
    - `transpose_financial_dataframe()`: Consolidated data transposition logic across all dataframes
  - **Code Reduction**: Eliminated massive code duplication in quick buttons and chat handlers
  - **Error Handling**: Improved error handling consistency across all response processing paths
  - **Maintainability**: Cleaner, more maintainable codebase with single source of truth for common operations

### Fixed
- [2025-08-04] **Streamlit Deprecation Warning**: Fixed use_column_width parameter deprecation
  - **Issue**: "The use_column_width parameter has been deprecated and will be removed in a future release"
  - **Solution**: Replaced `use_column_width=True` with `use_container_width=True` in chart display code
  - **Location**: Updated chart display in chat input handler (pages/bro.py:607)
  - **Impact**: Eliminates deprecation warnings and ensures future Streamlit compatibility

### Technical Implementation
- **File Upload Flow**: Streamlit 1.47+ chat input with file support returns object with `.text` and `.files` attributes
- **Agent Management**: Smart agent recreation based on dataframe changes with unique cache key system
- **Memory Efficiency**: Session state management prevents memory leaks from agent recreation
- **Error Resilience**: Graceful handling of file loading errors, agent creation failures, and processing exceptions

### User Experience Improvements
- **Seamless Integration**: Users can upload data files directly in chat interface without disrupting workflow
- **Multi-Format Support**: Support for both CSV and Excel formats with automatic format detection
- **Visual Feedback**: Clear success/error messages for file operations with meaningful context
- **Enhanced Analysis**: Uploaded data automatically available for AI analysis alongside stock financial data

## [0.2.3] - 2025-08-04

### Changed
- [2025-08-04] **Multi-Index Column Processing Enhancement**: Replaced custom multi-index flattening with vnstock's built-in function
  - **Migration**: Replaced manual multi-index column processing with `flatten_hierarchical_index()` from vnstock.core.utils.transform
  - **Improved Reliability**: Uses vnstock's official utility function for consistent column name handling
  - **Configuration**: Applied settings: separator="_", handle_duplicates=True, drop_levels=0
  - **Code Quality**: Removed custom logic that manually joined column names with ' - ' separator
  - **Files Modified**: pages/bro.py - updated ratio data processing section
  - **Import Management**: Added vnstock.core.utils.transform import at top of file instead of inline

### Technical Implementation
- **Built-in Function**: Leverages vnstock's official `flatten_hierarchical_index()` utility
- **Consistent Naming**: Uses underscore separator instead of dash separator for better compatibility
- **Error Handling**: Built-in duplicate handling and level dropping capabilities
- **Performance**: More efficient processing using library's optimized implementation

## [0.2.2] - 2025-08-02

### Changed
- [2025-08-02] **Stock Symbols Loading Optimization**: Centralized symbols loading to Stock Analysis page for optimal user flow
  - **Migration**: Moved `Listing().all_symbols()` loading from multiple pages to `pages/bro.py` (Stock Analysis page)
  - **Centralized Caching**: Stock symbols now loaded once in the primary workflow entry point and cached for all pages
  - **Performance**: Eliminated redundant API calls across pages - symbols loaded only once per session
  - **User Flow**: Stock Analysis page is now the recommended first stop after homepage for optimal caching
  - **Company Names**: Full company names (via `organ_name`) now available across all pages from single cache
  - **Files Modified**: 
    - `pages/bro.py`: Added symbols loading and caching logic
    - `pages/Portfolio_Optimization.py`: Removed symbols loading fallback, now uses cached data
    - `pages/Company_Overview.py`: Enhanced to use cached company names from DataFrame
    - `app.py`: Simplified to use cached symbols or show default list with helpful guidance

### Added  
- [2025-08-02] **Enhanced Company Name Display**: Company Overview page now shows full company names instead of just symbols
  - **Full Names**: Headers now display "Company Name (SYMBOL)" format instead of just "SYMBOL"
  - **Chart Titles**: Updated ownership and management charts to use full company names
  - **Data Source**: Uses cached `symbols_df['organ_name']` field for proper company names
  - **Example**: "Vietnam Dairy Products Joint Stock Company (VNM) - Ownership Structure"

### Technical Implementation
- **Single Loading Point**: Symbols loaded efficiently in main user workflow (bro.py) instead of multiple pages
- **Session State Caching**: Both `stock_symbols_list` and full `symbols_df` DataFrame cached in session state
- **Graceful Fallbacks**: Pages still work if accessed directly, with helpful messages directing users to optimal flow
- **User Guidance**: Clear messages throughout app directing users to Stock Analysis page for best experience
- **Code Cleanup**: Removed redundant import statements and unused fallback loading logic

### User Experience Improvements
- **Optimal Flow**: Users guided to visit Stock Analysis page first for complete symbols loading and caching
- **Better Performance**: Faster page loads after initial symbols caching in Stock Analysis page
- **Professional Display**: Company names displayed properly throughout application
- **Clear Guidance**: Helpful messages guide users to optimal workflow for best experience

## [0.2.1] - 2025-08-02

### Fixed
- [2025-08-02] **Environment Variable Loading**: Fixed API key not being loaded from .env file
  - **Issue**: App was showing API key input page despite having API key saved in .env file
  - **Root Cause**: Missing `load_dotenv()` call to load environment variables from .env file
  - **Solution**: Added `python-dotenv` import and `load_dotenv()` call at app startup
  - **Files Modified**: app.py - added dotenv import and load_dotenv() call before other imports
  - **Result**: API key now properly loaded from .env file, skipping manual input step

- [2025-08-02] **Chat Input File Upload Compatibility**: Fixed "expected string or bytes-like object" error in chat interface
  - **Issue**: Chat input with `accept_file=True` parameter returned object instead of string, causing TypeError
  - **Root Cause**: Streamlit 1.47+ `st.chat_input` with file support returns dict-like object with `.text` and `.files` attributes
  - **Solution**: Added proper handling for new chat input format with fallback for string input
  - **Technical Details**:
    - Added detection for object vs string input types
    - Extract text content from `.text` attribute when available
    - Added validation to only process chat when text content exists
    - Maintains backwards compatibility with string-only input
  - **Files Modified**: pages/bro.py - updated chat input handling logic
  - **Result**: Chat interface now works properly with file upload support enabled

### Technical Implementation
- **Environment Loading**: Proper dotenv integration ensures environment variables are available throughout application
- **Chat Input Handling**: Robust input processing that handles both new object-based and legacy string-based input formats
- **Error Prevention**: Added input validation to prevent processing empty or invalid chat submissions
- **Backwards Compatibility**: Code works with both newer Streamlit versions (with file support) and older versions

## [0.2.0] - 2025-08-02

### Added
- [2025-08-02] **Multipage Application Architecture**: Implemented comprehensive multipage application using Streamlit's st.navigation and st.Page
  - **Navigation System**: Added st.navigation with position="top" for seamless page switching
  - **Session State Management**: Implemented stock_symbol sharing across all pages via st.session_state
  - **Main Entry Point**: Created new app.py as central hub for stock symbol selection and navigation
  - **Page Integration**: Refactored all existing pages to use shared session state pattern
  - **User Experience**: Users select stock symbol once and it's available across all analysis pages

### Changed
- [2025-08-02] **Application Structure Refactor**: Complete reorganization from single-page to multipage application
  - **Entry Point**: New app.py serves as main navigation hub with stock symbol selection
  - **Pages Integration**: All analysis tools moved to dedicated pages that share session state
  - **Navigation Menu**: Organized pages into "Home" and "Analysis" sections with descriptive icons
  - **Session State Pattern**: All pages now check for stock_symbol in session state with fallback warnings
  - **File Structure**: Original app.py renamed to pages/bro.py (main Finance Bro analysis page)

### Technical Implementation
- **st.Page Configuration**: Each page defined with custom titles, icons, and file paths
- **Session State Pattern**: Consistent implementation across all pages:
  ```python
  if 'stock_symbol' in st.session_state and st.session_state.stock_symbol:
      stock_symbol = st.session_state.stock_symbol
      st.info(f"📊 Analyzing stock: **{stock_symbol}** (from main app)")
  else:
      st.warning("⚠️ No stock symbol selected. Please go to the main Finance Bro page and select a stock symbol first.")
      st.stop()
  ```
- **Navigation Structure**: 
  - Home: Main Finance Bro hub page for stock selection
  - Analysis: Stock Analysis (bro.py), Price Analysis, Company Overview, Portfolio Optimization
- **Page Organization**: Clean separation of concerns with each page handling specific analysis types

### User Experience Improvements
- **Single Symbol Selection**: Users input stock symbol once and it persists across all pages
- **Seamless Navigation**: Top navigation bar allows easy switching between analysis tools
- **Context Preservation**: Selected stock symbol maintained throughout user session
- **Clear Guidance**: Warning messages guide users to select symbol on main page if none chosen
- **Quick Navigation**: Direct buttons on main page to jump to specific analysis tools

### Files Modified
- **app.py**: New main entry point with st.navigation and stock symbol selection hub
- **pages/bro.py**: Original app.py functionality moved here, updated to use session state
- **pages/Company_Overview.py**: Updated to use session state stock_symbol
- **pages/Portfolio_Optimization.py**: Updated to use session state with smart default inclusion
- **pages/Stock_Price_Analysis.py**: Updated to use session state stock_symbol
- **Dockerfile**: Updated to run app.py as entry point
- **README.md**: Updated documentation to reflect new app.py entry point

## [0.1.3] - 2025-08-02

### Changed
- [2025-08-02] **Stock Symbol Input Enhancement**: Replaced text input with searchable multiselect dropdown using vnstock symbols
  - **Main App (app.py)**: Replaced text_input with multiselect using vnstock Listing().all_symbols()
  - **Portfolio Optimization**: Updated Portfolio_Optimization.py to use multiselect with vnstock symbols
  - **Symbol Source**: Uses `Listing().all_symbols()` to populate dropdown with all available stock symbols
  - **User Experience**: Users can now select multiple symbols from searchable dropdown instead of typing comma-separated values
  - **Error Handling**: Added fallback to default symbol list when vnstock symbols cannot be loaded
  - **Multi-symbol Support**: Framework in place for future multi-symbol analysis (currently uses first selected symbol)

### Added
- [2025-08-02] **Theme Display Feature**: Added current theme indicator in sidebar
  - **Theme Detection**: Uses st.get_option("theme.base") to detect light/dark mode
  - **Visual Indicators**: Emoji indicators (☀️ for light, 🌙 for dark) for quick recognition
  - **User Feedback**: Shows "Theme unavailable" when detection fails
  - **Location**: Added to sidebar as collapsible "🎨 Theme" expander section

## [0.1.2] - 2025-07-31

### Added
- [2025-07-31] **Google OAuth Authentication**: Implemented secure Google OAuth authentication using Streamlit 1.47.0+ built-in authentication features

### Fixed
- [2025-07-31] **Docker Build Error Resolution**: Fixed osqp package build failure in Docker container
  - **Issue**: osqp package (dependency of pyportfolioopt) failed to build due to missing git and build dependencies
  - **Root Cause**: Docker container lacked essential build tools required for scientific Python packages
  - **Solution**: Added comprehensive system dependencies to Dockerfile
  - **Additional Fix**: Added explicit osqp version (0.6.2.post8) in requirements.txt for better wheel compatibility
  - **Result**: Docker build now completes successfully, all Python packages install properly

## [0.1.1] - 2025-07-30

### Added
- [2025-07-30] **Stock Portfolio Optimization Page**: New comprehensive portfolio optimization feature using PyPortfolioOpt library
- [2025-07-30] **Company Profile Streamlit Enhancement**: Added interactive company profile page with ownership visualization
- [2025-07-30] **Enhanced Color Scheme and Typography**: Comprehensive styling improvements across the application
- [2025-07-30] **Management Team Ownership Visualization**: New altair bar chart for management share ownership
- [2025-07-30] **Data Caching System**: Implemented Streamlit caching to reduce API calls
- [2025-07-30] **Enhanced Data Visualization**: Improved chart interactivity and user experience

### Changed
- [2025-07-30] **Stock Portfolio Optimization UI Updates**: Streamlined visual design and removed grid lines
- [2025-07-30] **Chart Type Selector with Area Chart Gradient**: Added sidebar option to switch between line chart and area chart with gradient styling
- [2025-07-30] **Portfolio Weights Visualization Enhancement**: Replaced matplotlib bar charts with interactive Bokeh pie charts

## [0.1.0] - 2025-07-26

### Added
- [2025-07-26] **Financial Data Transformation Enhancement**: Implemented automatic transposition of financial statements from long to wide format
- [2025-07-26] **Chart Clearing Enhancement**: Implemented automatic chart clearing before new questions
- [2025-07-26] **Final Chart Display Fix**: Fixed chart display for all sample questions and chat messages
- [2025-07-26] **Dataframe Separation for AI Query Optimization**: Fixed PandasAI column detection issues by implementing dual dataframe architecture
- [2025-07-26] **Quarterly Data Transposition**: Fixed duplicate column names error when displaying quarterly financial data
- [2025-07-26] **Period Parameter Handling**: Fixed dataframes not respecting user's period selection
- [2025-07-26] **Automatic Data Reloading**: Implemented automatic data refresh when period changes
- [2025-07-26] **Redundant Row Cleanup**: Removed meaningless rows from annual data display
- [2025-07-25] **Chart Display Enhancement**: Enhanced AI responses with automatic chart generation
- [2025-07-25] **AI Response Formatting**: Improved natural language responses with structured data presentation
- [2025-07-25] **CSS Loading Order and Consistency**: Fixed StreamlitAPIException by ensuring set_page_config is called before CSS loading
- [2025-01-25] **Chart Management**: Implemented automatic chart clearing and single chart display

### Added
- [2025-07-31] **Google OAuth Authentication**: Implemented secure Google OAuth authentication using Streamlit 1.47.0+ built-in authentication features
- [2025-07-30] **Stock Portfolio Optimization Page**: New comprehensive portfolio optimization feature using PyPortfolioOpt library
- [2025-07-30] **Company Profile Streamlit Enhancement**: Added interactive company profile page with ownership visualization
- [2025-07-30] **Enhanced Color Scheme and Typography**: Comprehensive styling improvements across the application
- [2025-07-30] **Stock Portfolio Optimization UI Updates**: Streamlined visual design and removed grid lines
- [2025-07-30] **Chart Type Selector with Area Chart Gradient**: Added sidebar option to switch between line chart and area chart with gradient styling
- [2025-07-30] **Portfolio Weights Visualization Enhancement**: Replaced matplotlib bar charts with interactive Bokeh pie charts
- [2025-07-30] **Management Team Ownership Visualization**: New altair bar chart for management share ownership
- [2025-07-30] **Data Caching System**: Implemented Streamlit caching to reduce API calls
- [2025-07-30] **Enhanced Data Visualization**: Improved chart interactivity and user experience
- [2025-07-26] **Financial Data Transformation Enhancement**: Implemented automatic transposition of financial statements from long to wide format
- [2025-07-26] **Chart Clearing Enhancement**: Implemented automatic chart clearing before new questions
- [2025-07-26] **Final Chart Display Fix**: Fixed chart display for all sample questions and chat messages
- [2025-07-26] **Dataframe Separation for AI Query Optimization**: Fixed PandasAI column detection issues by implementing dual dataframe architecture
- [2025-07-26] **Quarterly Data Transposition**: Fixed duplicate column names error when displaying quarterly financial data
- [2025-07-26] **Period Parameter Handling**: Fixed dataframes not respecting user's period selection
- [2025-07-26] **Automatic Data Reloading**: Implemented automatic data refresh when period changes
- [2025-07-26] **Redundant Row Cleanup**: Removed meaningless rows from annual data display
- [2025-07-25] **Chart Display Enhancement**: Enhanced AI responses with automatic chart generation
- [2025-07-25] **AI Response Formatting**: Improved natural language responses with structured data presentation
- [2025-07-25] **CSS Loading Order and Consistency**: Fixed StreamlitAPIException by ensuring set_page_config is called before CSS loading
- [2025-01-25] **Chart Management**: Implemented automatic chart clearing and single chart display

### Fixed
- [2025-07-31] **Docker Build Error Resolution**: Fixed osqp package build failure in Docker container
  - **Issue**: osqp package (dependency of pyportfolioopt) failed to build due to missing git and build dependencies
  - **Root Cause**: Docker container lacked essential build tools required for scientific Python packages
  - **Solution**: Added comprehensive system dependencies to Dockerfile
  - **Additional Fix**: Added explicit osqp version (0.6.2.post8) in requirements.txt for better wheel compatibility
  - **Result**: Docker build now completes successfully, all Python packages install properly
  - **Issue**: osqp package (dependency of pyportfolioopt) failed to build due to missing git and build dependencies
  - **Root Cause**: Docker container lacked essential build tools required for scientific Python packages
  - **Solution**: Added comprehensive system dependencies to Dockerfile:
    - `build-essential` - Essential build tools and utilities
    - `git` - Required for osqp to clone dependencies during build
    - `cmake` - Required for CMake-based build process
    - `pkg-config` - Package configuration tool
    - `libblas-dev`, `liblapack-dev` - BLAS/LAPACK mathematical libraries
    - `gfortran` - Fortran compiler for scientific computing
    - `libopenblas-dev` - Optimized BLAS implementation
    - `curl` - For health checks and HTTP requests
  - **Additional Fix**: Added explicit osqp version (0.6.2.post8) in requirements.txt for better wheel compatibility
  - **Result**: Docker build now completes successfully, all Python packages install properly
  - **Impact**: Finance-bro application now runs successfully in Docker containers

### Added
- [2025-07-30] **Stock Portfolio Optimization Page**: New comprehensive portfolio optimization feature using PyPortfolioOpt library
  - **Library Integration**: Integrated PyPortfolioOpt for Modern Portfolio Theory calculations
  - **Portfolio Models**: Implemented Max Sharpe, Min Volatility, and Max Utility portfolio optimization
  - **Efficient Frontier**: Visual representation of efficient frontier with random portfolio simulation
  - **Risk Analysis**: Comprehensive risk metrics including Sharpe ratios, volatility, and expected returns
  - **Weight Visualization**: Bar charts for portfolio allocation across different optimization strategies
  - **Caching System**: Added intelligent caching to prevent repeated API calls
    - **Data Caching**: Stock price data cached for 1 hour using `@st.cache_data` to prevent repeated API calls
    - **Performance**: Significant speed improvements on page reloads while maintaining real-time optimization calculations
    - **Memory Efficiency**: Automatic cache invalidation when parameters change
  - **Data Viewing Enhancement**: Added interactive data viewing options
    - **Display Options**: Toggle between first 5 rows (.head()) and last 5 rows (.tail()) of price data
    - **User Control**: Radio button interface within price data expander for easy switching
    - **Flexible Viewing**: Users can quickly check both historical start and recent end of price datasets

### Changed
- [2025-07-30] **Portfolio Weights Visualization Enhancement**: Replaced matplotlib bar charts with interactive Bokeh pie charts
  - **Visualization**: Upgraded from matplotlib bar charts to interactive Bokeh pie charts for portfolio weights
  - **Colors**: Applied custom color scheme (#56524D, #76706C, #AAA39F) for consistent branding
  - **Interactivity**: Added hover tooltips showing symbol and weight percentages
  - **Layout**: Responsive three-column layout for Max Sharpe, Min Volatility, and Max Utility portfolios
  - **Data Filtering**: Implemented filtering to show only significant weights (>1%) for clarity
  - **Sizing**: Optimized chart dimensions (400x350px) for better container fit and visibility
- [2025-07-30] **Stock Portfolio Optimization UI Updates**: Streamlined visual design and removed grid lines
  - **Grid Lines**: Removed grid lines from efficient frontier scatter plot for cleaner appearance
  - **Icons**: Removed icons from section headers (Data Summary, Portfolio Optimization Results) for cleaner look
  - **Page Icon**: Removed page icon from Streamlit configuration
  - **Visual Consistency**: Maintained clean, professional appearance throughout the portfolio optimization interface

### Added
- [2025-07-30] **Chart Type Selector with Area Chart Gradient**: Added sidebar option to switch between line chart and area chart with gradient styling
  - **Feature**: New dropdown selector in sidebar allows users to choose between "Line Chart" and "Area Chart"
  - **Area Chart Enhancement**: Implemented gradient area chart using specified colors:
    - Gradient Start: `#3C3C3C` (dark gray)
    - Gradient End: `#807F80` (medium gray)
  - **Interactive**: Both chart types maintain full interactivity with hover tooltips and zoom capabilities
  - **User Experience**: Seamless switching between chart types without data reload
  - **Technical**: Uses Altair's gradient functionality with linear gradient stops

### Fixed
- [2025-07-30] **CSS Loading Order and Consistency**: Fixed StreamlitAPIException by ensuring set_page_config is called before CSS loading
  - **Issue**: CSS loading was happening before set_page_config, causing Streamlit errors
  - **Resolution**: Moved CSS loading after set_page_config in all pages (Portfolio_Optimization.py, Company_Overview.py, Stock_Price_Analysis.py)
  - **Result**: Consistent CSS styling across all pages without errors

### Styling Updates
- [2025-07-30] **Enhanced Color Scheme and Typography**: Comprehensive styling improvements across the application
  - **Page Titles**: Changed h1 color to #2B2523 (dark brown) for better visual hierarchy
  - **Headers**: Updated h2 and h3 colors to #828282 (medium gray) for consistency
  - **Metric Values**: Changed st.metrics value color to #56524D (dark olive)
  - **CSS Targeting**: Added specific Streamlit selectors ([data-testid]) for reliable styling
  - **Cross-Page Consistency**: Ensured all styling applies uniformly across main app and pages

### Fixed
- [2025-07-26] **Dataframe Separation for AI Query Optimization**: Fixed PandasAI column detection issues by implementing dual dataframe architecture
  - **Issue**: PandasAI couldn't properly detect `Quarter` column because dataframes still contained `lengthReport` column names
  - **Root Cause**: Single dataframe set caused conflict between display formatting needs and AI query requirements
  - **Solution**: Implemented separate dataframe storage systems:
    - `st.session_state.display_dataframes`: Original dataframes with `lengthReport` for proper wide format display
    - `st.session_state.dataframes`: AI-optimized copies with `Quarter` column names for enhanced query compatibility
  - **AI Query Enhancement**: Renaming `lengthReport` → `Quarter` provides semantic context that enables:
    - More intuitive natural language queries ("What's Q1 revenue?" vs "What's lengthReport 1 revenue?")
    - Better AI understanding of temporal relationships between quarters
    - Improved accuracy in quarterly trend analysis and comparisons
    - Enhanced contextual awareness for financial period-based calculations
  - **Display Integrity**: Wide format tables maintain original column structure for proper transposition logic
  - **Affected Components**: CashFlow, BalanceSheet, IncomeStatement, and Ratios dataframes for quarterly data

- [2025-07-26] **Show Table Button Error Handling**: Fixed AttributeError when clicking "Show Table" before loading data
  - **Issue**: `AttributeError: st.session_state has no attribute 'display_dataframes'` when no data loaded
  - **Solution**: Added proper existence checks and user-friendly warning messages
  - **User Experience**: Clear guidance to load data first before attempting to view tables

- [2025-07-26] **Display Logic Indentation**: Fixed multiple Python indentation errors in table display section
  - **Issue**: Syntax errors preventing proper code execution in wide format display logic
  - **Solution**: Corrected indentation throughout the display section for proper code structure
- [2025-01-25] Fixed sample questions functionality by moving from main content area to sidebar
- [2025-01-25] Resolved "🤖 Ask Question" button not working issue
- [2025-01-25] Fixed TypeError: object of type 'PandasConnector' has no len() by reverting to Agent approach
- [2025-01-25] Fixed multi-index Ratio dataframe processing for better AI analysis
- [2025-01-25] Fixed inconsistent generated code detection across different response methods
- [2025-01-25] Improved code visibility by implementing comprehensive code extraction logic

### Changed
- [2025-01-25] Moved sample questions from main content area (col3) to sidebar with dropdown menu
- [2025-01-25] Replaced individual question buttons with dropdown selection interface
- [2025-01-25] Relocated pending question processing logic from data loading section to AI Analysis section
- [2025-01-25] Simplified agent initialization by removing SmartDataframe approach

### Added
- [2025-01-25] Added dropdown menu for sample questions in sidebar
- [2025-01-25] Added spinner functionality for processing selected questions
- [2025-01-25] Added proper error handling for pending question processing
- [2025-01-25] Added multi-index column flattening for Ratio dataframe processing
- [2025-01-25] Added generated code display functionality for all AI responses
- [2025-01-25] Added expandable "🔍 View Generated Code" containers under AI responses
- [2025-01-25] Added chart display containers with "📈 View Chart" expandable sections
- [2025-01-25] Added comprehensive code extraction helper function for better code detection

### Technical Details
- **Sample Questions UI**: Converted from expandable buttons in main area to dropdown selection in sidebar
- **Button Functionality**: Fixed issue where "Ask Question" button only worked during data loading
- **Agent Initialization**: Reverted from SmartDataframe to Agent class for better stability
- **Processing Logic**: Moved pending question processing to ensure agent availability
- **Ratio Data Processing**: Added multi-index column flattening to transform Vietnamese financial categories into readable column names
  - Example: `('Chỉ tiêu khả năng sinh lợi', 'ROE (%)')` → `Chỉ tiêu khả năng sinh lợi - ROE (%)`
  - Preserves Meta columns (CP, Năm, Kỳ) with simple names
  - Enables better AI understanding of financial ratio categories
- **Generated Code Display**: Added transparency feature to show Python code generated by PandasAI
  - Uses official PandasAI API: `response.last_code_executed`
  - Displays code in expandable containers with syntax highlighting
  - Available for all AI response types: chat input, sidebar questions, quick buttons
  - Provides complete transparency into data analysis process
- **Chart Display Integration**: Added visual chart containers alongside generated code
  - Automatic chart detection from PandasAI exports/charts/ directory
  - Support for multiple chart formats: Plotly, Matplotlib, and image files
  - Expandable "📈 View Chart" containers positioned under code sections
- **Code Detection Enhancement**: Implemented robust code extraction system
  - Created `get_generated_code()` helper function for consistent code access
  - Tries multiple sources: response object, agent attributes, memory, internal state
  - Unified code detection across all response methods (chat, sidebar, quick buttons)
  - Improved reliability from inconsistent "Code generation details not available" messages

### User Experience Improvements
- ✅ Sample questions now accessible from sidebar at all times
- ✅ Cleaner main content area with sample questions removed from col3
- ✅ Dropdown interface provides better organization of predefined questions
- ✅ Spinner feedback shows processing status when analyzing selected questions
- ✅ Questions are properly added to chat history with AI responses

### [2025-01-25] PandasAI Visualization Enhancements

#### Changed
- [2025-07-31] **Chart Display Refactor**: Complete overhaul of chart display system in app.py
  - **Disk-Free Display**: Charts now display directly in Streamlit without saving to disk
  - **Memory Optimization**: Removed chart storage in session state/memory
  - **Display Logic**: Now shows only the latest generated chart instead of storing multiple charts
  - **Clear Previous**: Automatically clears previous charts when new ones are generated
  - **User Experience**: Charts display immediately below AI responses without cluttering the interface
  - **Implementation**: Uses Streamlit's `st.pyplot()` for direct matplotlib integration
  - **Pop-up Prevention**: Fixed chart pop-up window issue by configuring matplotlib to use non-interactive backend ('Agg')
  - **PandasAI Configuration**: Added `save_charts=False`, `save_logs=False`, and `enable_cache=False` to prevent all disk operations

#### Technical Updates
- **Chat Interface**: Charts display directly in main content with "📊 Analysis Chart" subheader
- **Quick Buttons**: All three buttons (ROIC, Dividend Yield, Debt Analysis) now include chart detection
- **Sidebar Questions**: Pending questions include chart detection and display
- **Code Containers**: Generated code remains in expandable containers as requested

#### Visual Improvements
- **Immediate Visibility**: Charts appear directly without requiring user interaction
- **Clean Layout**: Generated code stays in expandable containers to avoid clutter
- **Consistent Design**: All AI response types follow the same display pattern
- **User Experience**: Better balance between transparency and clean interface

### [2025-01-25] Final Chart Display Fix
- **Sample Questions**: Fixed chart display for all sample questions (sidebar dropdown, quick buttons)
- **Chat Messages**: Updated chart display to show directly in main content area for all response types
- **Consistency**: All AI responses now follow same pattern - code in expandable containers, charts in main content

### [2025-01-25] Chart Clearing Enhancement
- **Chart Management**: Implemented automatic chart clearing before new questions
- **Text Preservation**: Previous text answers are preserved while charts are cleared
- **Single Chart Display**: Only the most recent chart is displayed at any time
- **User Experience**: Cleaner interface without chart accumulation
- **Implementation**: Charts are displayed only for the latest message in chat history
- **All Response Types**: Applied to chat input, sidebar questions, and quick buttons

## [2025-07-30] Company Profile Streamlit Enhancement

### Changed
- [2025-07-30] **Ownership Structure Chart Migration**: Converted from Seaborn to Altair for enhanced interactivity
  - **Migration**: Replaced seaborn barplot with altair horizontal bar chart
  - **Visual Improvements**: Added interactive tooltips and responsive design
  - **Color Scheme**: Updated to black bars for consistent professional styling
  - **Data Labels**: Added percentage labels positioned at bar ends

### Added
- [2025-07-30] **Management Team Ownership Visualization**: New altair bar chart for management share ownership
  - **Data Source**: Uses management team dataframe with officer_name, quantity, and officer_own_percent
  - **Interactive Features**: Hover tooltips with officer_name, position_short_name, shares, and ownership %
  - **Visual Design**: Black bars matching ownership structure chart styling
  - **Layout**: Positioned below management team dataframe in "👥 Management Team" tab

- [2025-07-30] **Data Caching System**: Implemented Streamlit caching to reduce API calls
  - **Caching Functions**: Added @st.cache_data decorators for ownership and management data
  - **Cache Duration**: 1-hour TTL for cached data per stock symbol
  - **Performance**: Significant reduction in API calls and faster data loading
  - **Error Handling**: Graceful handling of API failures within cached functions

- [2025-07-30] **Enhanced Data Visualization**: Improved chart interactivity and user experience
  - **Hover Data**: Added position_short_name to management team tooltips
  - **Axis Configuration**: Quantity-based x-axis for both ownership and management charts
  - **Responsive Design**: Charts automatically adjust to container width
  - **Sorting**: Data sorted by quantity for better visual comparison

### Technical Implementation
- **Altair Integration**: Native altair charts with Streamlit integration
- **Layered Charts**: Combined bar charts with text labels using altair layering
- **Data Filtering**: Robust handling of null values and missing data
- **Error Handling**: Comprehensive error handling for missing data scenarios

### User Experience Improvements
- **Interactive Tooltips**: Detailed information available on hover
- **Faster Loading**: Cached data loads instantly for repeated queries
- **Consistent Styling**: Unified black color scheme across all charts
- **Responsive Layout**: Charts adapt to different screen sizes

## [2025-07-26] Financial Data Transformation Enhancement

### Fixed
- [2025-07-26] **Quarterly Data Transposition**: Fixed duplicate column names error when displaying quarterly financial data
  - Issue: When period="quarter" was selected, transposition failed with "Duplicate column names found" error
  - Root Cause: Only using `yearReport` as index created duplicates (2024, 2024, 2024, 2024 for Q1-Q4)
  - Solution: Combined `yearReport` and `lengthReport` to create unique quarterly identifiers (2024-Q1, 2024-Q2, etc.)
  - Affected: CashFlow, BalanceSheet, IncomeStatement, and Ratios dataframes

- [2025-07-26] **Period Parameter Handling**: Fixed dataframes not respecting user's period selection
  - Issue: Ratios dataframe showed quarterly headers even when period="year" was selected
  - Root Cause: Logic only checked for `lengthReport` column existence, not the actual period parameter
  - Solution: Added period parameter validation in transposition logic
  - Applied to: All financial dataframes (CashFlow, BalanceSheet, IncomeStatement, Ratios)

- [2025-07-26] **Automatic Data Reloading**: Implemented automatic data refresh when period changes
  - Issue: Changing period dropdown didn't reload data, causing stale data display
  - Root Cause: Data only loaded on "Analyze Stock" button click, not on period changes
  - Solution: Added period change detection with automatic data reloading
  - Benefit: Users no longer need to click "Analyze Stock" after changing period

- [2025-07-26] **Redundant Row Cleanup**: Removed meaningless rows from annual data display
  - Issue: `lengthReport` row showing value "5" when period="year" was confusing
  - Root Cause: API returns `lengthReport` column even for annual data
  - Solution: Drop `lengthReport` row for annual data since it's not meaningful
  - Applied to: Both financial statements and Ratios dataframes

### Added
- **Data Format Transformation**: Implemented automatic transposition of financial statements from long to wide format
- **Year Headers**: Financial metrics now display with years as column headers for easier trend analysis
- **Quarterly Support**: Added proper handling for quarterly data with quarter identifiers in column headers
- **Multi-format Support**: Added handling for different data structures including multi-index columns in Ratios
- **Smart Detection**: Automatic detection of data structure to apply appropriate transformation

### Technical Implementation
- **Financial Statements**: CashFlow, BalanceSheet, and IncomeStatement now transpose to wide format
  - Years promoted from `yearReport` column to column headers
  - Financial metrics displayed as row labels in "Metric" column
  - Ticker column dropped as redundant for display purposes
- **Ratios Handling**: Special processing for multi-index column structure
  - Detects if years are already in columns vs. need transposition
  - Handles flattened multi-index columns from Vietnamese financial data
  - Graceful fallback to original format when transposition fails
- **Dividends**: Maintained original format as time-series data is more appropriate

### User Experience Improvements
- **Trend Analysis**: Users can now easily compare financial metrics across years side-by-side
- **Standard Format**: Wide format aligns with traditional financial statement presentation
- **Error Handling**: Warning messages displayed if transposition fails for any dataset
- **Consistent Display**: All financial data follows the same wide format pattern

### Code Changes
- **Location**: Modified `📊 Show Raw Data` button functionality in app.py lines 483-520
- **Transformation Logic**: Added robust data structure detection and appropriate transposition methods
- **Fallback Support**: Maintains original display format when transformation is not possible
- **Data Integrity**: Preserves all original data while improving presentation format

## [2025-07-31] Google OAuth Authentication Integration

### Added
- [2025-07-31] **Google OAuth Authentication**: Implemented secure Google OAuth authentication using Streamlit 1.47.0+ built-in authentication features
  - **Authentication Gating**: App now requires Google login before accessing any features, similar to API key check
  - **Streamlit Integration**: Uses `st.login()`, `st.user`, and `st.logout()` for seamless OAuth flow
  - **Configuration**: Properly configured `.streamlit/secrets.toml` with Google OAuth credentials
  - **User Experience**: Clean login interface with Google sign-in button
  - **Logout Functionality**: Added logout button in sidebar for easy session management

### Technical Implementation
- **Authentication Flow**: Uses `st.user.is_logged_in` to properly check authentication state and prevent redirect loops
- **Configuration**: Updated `.streamlit/secrets.toml` with correct OAuth parameters:
  - `redirect_uri = "http://localhost:8501/oauth2callback"`
  - `client_id`, `client_secret`, and `server_metadata_url` for Google OAuth
- **Session Management**: Streamlit handles session cookies automatically with 30-day expiration
- **Security**: OAuth credentials stored securely in secrets.toml file

### User Experience Improvements
- **Seamless Login**: Users authenticate once and stay logged in across sessions
- **Clean Interface**: Minimal login page with Google sign-in button
- **Easy Logout**: One-click logout option in sidebar
- **No Redirect Loops**: Fixed previous authentication state issues
- **Professional Appearance**: Clean, modern authentication flow

### Files Modified
- `app.py`: Added authentication gating at application start
- `.streamlit/secrets.toml`: Configured Google OAuth credentials
- **Dependencies**: Requires `streamlit>=1.47.0` and `Authlib>=1.3.2`
