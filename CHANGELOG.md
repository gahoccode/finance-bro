# Changelog

All notable changes to the Finance Bro AI Stock Analysis application will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- [2025-01-25] Fixed sample questions functionality by moving from main content area to sidebar
- [2025-01-25] Resolved "🤖 Ask Question" button not working issue
- [2025-01-25] Fixed TypeError: object of type 'PandasConnector' has no len() by reverting to Agent approach
- [2025-01-25] Fixed multi-index Ratio dataframe processing for better AI analysis

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

### Technical Details
- **Sample Questions UI**: Converted from expandable buttons in main area to dropdown selection in sidebar
- **Button Functionality**: Fixed issue where "Ask Question" button only worked during data loading
- **Agent Initialization**: Reverted from SmartDataframe to Agent class for better stability
- **Processing Logic**: Moved pending question processing to ensure agent availability
- **Ratio Data Processing**: Added multi-index column flattening to transform Vietnamese financial categories into readable column names
  - Example: `('Chỉ tiêu khả năng sinh lợi', 'ROE (%)')` → `Chỉ tiêu khả năng sinh lợi - ROE (%)`
  - Preserves Meta columns (CP, Năm, Kỳ) with simple names
  - Enables better AI understanding of financial ratio categories

### User Experience Improvements
- ✅ Sample questions now accessible from sidebar at all times
- ✅ Cleaner main content area with sample questions removed from col3
- ✅ Dropdown interface provides better organization of predefined questions
- ✅ Spinner feedback shows processing status when analyzing selected questions
- ✅ Questions are properly added to chat history with AI responses
