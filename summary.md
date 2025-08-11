Global Variables:
  - api_key - OpenAI API key
  - stock_symbol - Current stock selection (shared across all pages)
  - stock_symbols_list & symbols_df - Cached symbols for performance
  - last_period - Change detection for data reloading

  Page-Specific Variables:
  - Stock Analysis: dataframes, display_dataframes, messages, agent, uploaded_dataframes
  - Price Analysis: stock_price_data, stock_returns
  - Portfolio: portfolio_returns, weights_*, portfolio_strategy_choice (new)
  - Screener: screener_data, dynamic preset_* filter keys

  Architecture Benefits:
  - Data consistency, performance optimization, seamless UX, intelligent memory management

  CHANGELOG.md Updates

  Enhanced v0.2.16 entry with detailed "Session State Architecture Enhancement" section:

  New Portfolio Strategy Variable:
  - st.session_state.portfolio_strategy_choice - Master control across portfolio tabs
  - Master-slave pattern: Tab 4 writes, Tab 3 & Tab 5 read