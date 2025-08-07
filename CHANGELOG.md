# Changelog

All notable changes to the Finance Bro AI Stock Analysis application will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
