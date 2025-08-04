# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Application
```bash
# Recommended: Using uv (faster)
uv run streamlit run app.py

# Alternative: Using streamlit directly
streamlit run app.py

# Access at: http://localhost:8501
```

### Dependency Management
```bash
# Install dependencies with uv (recommended)
uv sync

# Alternative: Using pip
pip install -r requirements.txt

# Add new dependency
uv add package_name

# Development dependencies
uv sync --group dev
```

### Development Tools
```bash
# Code formatting
black .

# Linting
flake8

# Type checking
mypy .

# Testing
pytest
```

### Docker Commands
```bash
# Development with Docker Compose
docker-compose up --build

# Build Docker image
docker build -t finance-bro .

# Run with environment variables
docker run -p 8501:8501 -e OPENAI_API_KEY=your_key finance-bro
```

## Architecture Overview

### Application Structure
- **Streamlit Multi-page App**: Main entry point is `app.py` with pages in `pages/` directory
- **Session State Management**: Centralized stock symbol selection shared across pages
- **Data Flow**: Homepage → Stock Analysis (data loading/caching) → Other analysis pages
- **Authentication**: Google OAuth integration for user access control

### Core Components

#### Main Application (`app.py`)
- Authentication handling with Google OAuth
- API key management (environment or user input)
- Stock symbol loading and session state initialization
- Homepage with stock symbol selection dropdown

#### Analysis Pages (`pages/`)
- **`bro.py`**: Core AI chat interface with PandasAI integration
- **`Stock_Price_Analysis.py`**: Technical analysis and price charts
- **`Company_Overview.py`**: Company profile and ownership structure
- **`Portfolio_Optimization.py`**: Modern Portfolio Theory optimization

### Data Sources & APIs
- **Vnstock**: Vietnamese stock market data (VCI/TCBS sources)
- **OpenAI**: GPT models for AI analysis via PandasAI
- **PandasAI**: Natural language querying of financial data

### Critical Dependencies & Compatibility

**IMPORTANT**: This project uses specific version combinations that must be maintained:

- `pandasai==2.3.0` (NOT 3.x - has breaking changes)
- `pandas==1.5.3` (NOT 2.x - incompatible with pandasai 2.x)
- `python==3.10.11` (exact version required)

**Never upgrade these packages independently** - test in isolated environment first.

### Session State Architecture
```python
# Key session state variables:
st.session_state.selected_symbol    # Selected stock symbol (shared across pages)
st.session_state.company_names      # Stock symbol to company name mapping
st.session_state.api_key           # OpenAI API key
st.session_state.symbols_loaded    # Cache flag for symbols data
```

### Optimal User Flow
1. **Authentication** → Login with Google OAuth
2. **Homepage** → Select stock symbol (persists across session)
3. **Stock Analysis** → Load data (caches symbols for entire app)
4. **Other Pages** → Use cached data for faster performance

### File Structure Patterns
- Static assets in `static/` (CSS, images)
- Data exports in `exports/charts/`
- Cache storage in `cache/`
- Reference implementations in `Reference/`

## Development Guidelines

### Adding New Features
- Check existing pages for UI patterns and session state usage
- Ensure stock symbol selection integrates with session state
- Follow the data loading pattern: check cache first, then load from APIs
- Use consistent Streamlit components and styling

### Working with Stock Data
- Always use the selected symbol from `st.session_state.selected_symbol`
- Check if symbols are loaded before attempting data operations
- Handle VCI/TCBS data source selection consistently
- Cache expensive API calls to improve performance

### AI Integration
- PandasAI agents should use OpenAI LLM (built into pandasai 2.3.0)
- Configure SmartDataframe with proper data types
- Handle chat history and conversation context appropriately
- Export charts to `exports/charts/` directory

### Docker & Environment
- Always mount `exports/` and `cache/` volumes for persistence
- Set `OPENAI_API_KEY` environment variable
- Use `uv` for faster dependency resolution in containers
- Follow multi-stage build pattern for production images