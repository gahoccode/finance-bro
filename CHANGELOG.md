# Changelog

All notable changes to the Finance Bro AI Stock Analysis application will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
