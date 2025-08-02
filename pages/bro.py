import os
import glob
import streamlit as st
import pandas as pd
from vnstock import Vnstock, Listing
import warnings

# pandasai v2.4.2 imports
from pandasai import Agent
from pandasai.llm import OpenAI

warnings.filterwarnings("ignore")

# Helper function to extract generated code from PandasAI response/agent
def get_generated_code(response, agent):
    """Extract generated code from PandasAI response or agent object"""
    try:
        # Try response object first
        if hasattr(response, 'last_code_executed') and response.last_code_executed:
            return response.last_code_executed
        
        # Try agent object
        if hasattr(agent, 'last_code_executed') and agent.last_code_executed:
            return agent.last_code_executed
            
        # Try agent's memory or context
        if hasattr(agent, 'memory') and hasattr(agent.memory, 'get_last_code'):
            code = agent.memory.get_last_code()
            if code:
                return code
                
        # Try to find code in agent's internal state
        for attr_name in ['_last_code_generated', '_code_executed', 'last_code']:
            if hasattr(agent, attr_name):
                code = getattr(agent, attr_name)
                if code and isinstance(code, str) and len(code.strip()) > 5:
                    return code
        
        return "# Code generation details not available"
        
    except Exception as e:
        return f"# Error accessing code: {str(e)}"

# Page configuration
st.set_page_config(
    page_title="Finance Bro",
    #page_icon="",
    layout="wide"
)

# Load custom CSS
with open('static/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Get stock symbol from session state (set in main app)
# If not available, show message to use main app first
if 'stock_symbol' in st.session_state and st.session_state.stock_symbol:
    stock_symbol = st.session_state.stock_symbol
    st.info(f"📊 Analyzing stock: **{stock_symbol}** (from main app)")
else:
    st.warning("⚠️ No stock symbol selected. Please go to the main Finance Bro page and select a stock symbol first.")
    st.stop()

# Title
st.markdown('<h1 class="main-header">Finance Bro</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #666; font-size: 1.1rem; margin-top: -0.5rem; margin-bottom: 1rem;">Ask your finance bro about your company\'s financial statements</p>', unsafe_allow_html=True)

# Authentication handling
# Check if user is logged in using Streamlit's built-in authentication
if not st.user.is_logged_in:
    st.title("🔒 Authentication Required")
    st.markdown("Please authenticate with Google to access Finance Bro")
    
    # Create a clean login interface
    st.button("Login with Google", on_click=st.login)
    
    # Show helpful information
    st.markdown("---")
    st.info("After logging in, you'll be redirected back to the app automatically.")
    
    st.stop()

# User is now authenticated - show welcome message in sidebar
st.sidebar.success("Successfully logged in")

# Load stock symbols and cache in session state if not already loaded
if 'stock_symbols_list' not in st.session_state:
    try:
        with st.spinner("Loading stock symbols..."):
            symbols_df = Listing().all_symbols()
            st.session_state.stock_symbols_list = sorted(symbols_df['symbol'].tolist())
            st.session_state.symbols_df = symbols_df  # Cache the full DataFrame for organ_name access
            st.success("✅ Stock symbols loaded and cached!")
    except Exception as e:
        st.warning(f"Could not load stock symbols from vnstock: {str(e)}")
        st.session_state.stock_symbols_list = ["REE", "VIC", "VNM", "VCB", "BID", "HPG", "FPT", "FMC", "DHC"]
        st.session_state.symbols_df = None

# API Key handling
if 'api_key' not in st.session_state:
    st.session_state.api_key = os.environ.get("OPENAI_API_KEY", "")

if not st.session_state.api_key:
    st.warning("OpenAI API Key Required")
    
    with st.expander("Enter API Key", expanded=True):
        api_key_input = st.text_input(
            "OpenAI API Key:",
            type="password",
            placeholder="sk-...",
            help="Enter your OpenAI API key to enable AI analysis"
        )
        
        if st.button("Save API Key", type="primary"):
            if api_key_input.startswith("sk-"):
                st.session_state.api_key = api_key_input
                os.environ["OPENAI_API_KEY"] = api_key_input
                st.success("✅ API Key saved successfully!")
                st.rerun()
            else:
                st.error("❌ Invalid API key format. Please check your key.")
    
    st.stop()

# Sidebar for stock configuration
with st.sidebar:
    st.header("Stock Configuration")
    
    # Show current stock symbol from session state
    st.metric("Current Symbol", stock_symbol)
    
    # User logout option
    if st.sidebar.button("Logout", use_container_width=True):
        st.logout()
    
    st.sidebar.markdown("---")
    
    period = st.selectbox(
        "Period:",
        options=["year", "quarter"],
        index=0
    )
    
    source = st.selectbox(
        "Data Source:",
        options=["VCI", "TCBS"],
        index=0
    )
    
    company_source = st.selectbox(
        "Company Data Source:",
        options=["TCBS", "VCI"],
        index=0
    )
    
    analyze_button = st.button("Analyze Stock", type="primary", use_container_width=True)
    
    # Sample Questions - dropdown menu in sidebar
    st.markdown("---")
    st.subheader("Sample Questions")
    
    sample_questions = [
        "What is the return on invested capital (ROIC) trend?",
        "Analyze the dividend yield trend",
        "What is the company's debt-to-equity ratio?",
        "What's 2024 revenue growth?",
        "What's the ROE in 2024?",
        "How has cash flow evolved over time?",
        "What is the company's profitability trend?",
        "Analyze the balance sheet health indicators"
    ]
    
    selected_question = st.selectbox(
        "Select a question to analyze:",
        options=["Choose a question..."] + sample_questions,
        index=0,
        key="sample_question_selector"
    )
    
    if selected_question != "Choose a question..." and st.button("Ask Question", use_container_width=True):
        # Store the selected question for processing
        st.session_state.pending_question = selected_question
    
    # Clear Chat button in sidebar
    st.sidebar.markdown("---")
    
    # Display current theme
    with st.sidebar.expander("🎨 Theme", expanded=False):
        try:
            # Check if dark mode is enabled
            is_dark = st.get_option("theme.base") == "dark"
            if is_dark:
                st.write("**Dark Mode** 🌙")
            else:
                st.write("**Light Mode** ☀️")
        except Exception:
            st.write("**Theme unavailable**")
    
    if st.button("Clear Chat", use_container_width=True, key="sidebar_clear_chat"):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown(
        """
        <div style='text-align: center; padding: 0.25rem 0;'>
            <a href="https://github.com/gahoccode/finance-bro" target="_blank" style="text-decoration: none; display: flex; flex-direction: column; align-items: center; gap: 0.25rem;">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="vertical-align: middle;">
                    <circle cx="12" cy="12" r="9" stroke="#0366d6" stroke-width="1" fill="none"/>
                    <path d="M12 2C6.477 2 2 6.477 2 12C2 16.418 4.865 20.166 8.839 21.489C9.339 21.582 9.521 21.291 9.521 21.042C9.521 20.82 9.512 20.192 9.508 19.391C6.726 19.924 6.139 17.955 6.139 17.955C5.685 16.812 5.029 16.523 5.029 16.523C4.121 15.938 5.097 15.951 5.097 15.951C6.101 16.023 6.629 16.927 6.629 16.927C7.521 18.445 8.97 17.988 9.546 17.749C9.642 17.131 9.889 16.696 10.167 16.419C7.945 16.137 5.615 15.276 5.615 11.469C5.615 10.365 6.003 9.463 6.649 8.761C6.543 8.48 6.207 7.479 6.749 6.124C6.749 6.124 7.586 5.869 9.499 7.159C10.329 6.921 11.179 6.802 12.029 6.798C12.879 6.802 13.729 6.921 14.559 7.159C16.472 5.869 17.309 6.124 17.309 6.124C17.851 7.479 17.515 8.48 17.409 8.761C18.055 9.463 18.443 10.365 18.443 11.469C18.443 15.286 16.111 16.134 13.883 16.408C14.223 16.748 14.523 17.42 14.523 18.438C14.523 19.849 14.509 20.985 14.509 21.42C14.509 21.769 14.679 22.149 15.179 22.041C19.142 20.709 22 16.972 22 12C22 6.477 17.523 2 12 2Z" fill="#000000"/>
                </svg>
                <div style='font-size: 0.8rem; color: #000000; font-weight: 600; line-height: 1;'>Finance Bro</div>
                <div style='font-size: 0.7rem; color: #000000; line-height: 1;'>by Tam Le</div>
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )

# Check if period has changed and data needs to be reloaded
period_changed = False
if 'last_period' in st.session_state and st.session_state.last_period != period:
    period_changed = True

# Main content area
if analyze_button or (period_changed and 'stock_symbol' in st.session_state):
    try:
        with st.spinner(f"Loading data for {stock_symbol}..."):
            # Initialize Vnstock
            stock = Vnstock().stock(symbol=stock_symbol, source=source)
            company = Vnstock().stock(symbol=stock_symbol, source=company_source).company
            
            # Load financial data
            CashFlow = stock.finance.cash_flow(period=period)
            BalanceSheet = stock.finance.balance_sheet(period=period, lang="en", dropna=True)
            IncomeStatement = stock.finance.income_statement(period=period, lang="en", dropna=True)
            
            # Load and process Ratio data (multi-index columns)
            Ratio_raw = stock.finance.ratio(period=period, lang="en", dropna=True)
            
            # Process multi-index columns by flattening them
            if isinstance(Ratio_raw.columns, pd.MultiIndex):
                # Flatten multi-index columns by joining level names with ' - '
                Ratio = Ratio_raw.copy()
                Ratio.columns = [' - '.join(col).strip() if col[0] != 'Meta' else col[1] 
                               for col in Ratio_raw.columns.values]
                # Clean up column names
                Ratio.columns = [col.replace('Meta - ', '') for col in Ratio.columns]
            else:
                Ratio = Ratio_raw
            
            dividend_schedule = company.dividends()
            
            # Store original dataframes for display (keep original column names)
            st.session_state.display_dataframes = {
                'CashFlow': CashFlow,
                'BalanceSheet': BalanceSheet,
                'IncomeStatement': IncomeStatement,
                'Ratios': Ratio,
                'Dividends': dividend_schedule
            }
            
            # Create copies with renamed columns for PandasAI (better query compatibility)
            CashFlow_AI = CashFlow.copy()
            BalanceSheet_AI = BalanceSheet.copy()
            IncomeStatement_AI = IncomeStatement.copy()
            Ratio_AI = Ratio.copy()
            
            if period == 'quarter':
                # Rename columns in AI copies for better query compatibility
                if 'lengthReport' in CashFlow_AI.columns and CashFlow_AI['lengthReport'].isin([1, 2, 3, 4]).any():
                    CashFlow_AI = CashFlow_AI.rename(columns={'lengthReport': 'Quarter'})
                
                if 'lengthReport' in BalanceSheet_AI.columns and BalanceSheet_AI['lengthReport'].isin([1, 2, 3, 4]).any():
                    BalanceSheet_AI = BalanceSheet_AI.rename(columns={'lengthReport': 'Quarter'})
                
                if 'lengthReport' in IncomeStatement_AI.columns and IncomeStatement_AI['lengthReport'].isin([1, 2, 3, 4]).any():
                    IncomeStatement_AI = IncomeStatement_AI.rename(columns={'lengthReport': 'Quarter'})
                
                if 'lengthReport' in Ratio_AI.columns and Ratio_AI['lengthReport'].isin([1, 2, 3, 4]).any():
                    Ratio_AI = Ratio_AI.rename(columns={'lengthReport': 'Quarter'})
            
            # Store AI-optimized dataframes for PandasAI
            st.session_state.dataframes = {
                'CashFlow': CashFlow_AI,
                'BalanceSheet': BalanceSheet_AI,
                'IncomeStatement': IncomeStatement_AI,
                'Ratios': Ratio_AI,
                'Dividends': dividend_schedule
            }
            
            st.session_state.stock_symbol = stock_symbol
            st.session_state.last_period = period  # Store current period to detect changes
            st.success(f"✅ Successfully loaded data for {stock_symbol}")
    
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        st.info("Please check the stock symbol and try again.")

# AI Analysis section
if 'dataframes' in st.session_state:
    st.header(f"Analysis for {st.session_state.stock_symbol}")
    
    # Initialize LLM with OpenAI for pandasai v2.4.2
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    llm = OpenAI(api_token=st.session_state.api_key, model=model)
    
    # Use Agent approach with list of dataframes
    agent = Agent(
        list(st.session_state.dataframes.values()),
        config={"llm": llm, "verbose": True}
    )
    
    # Process any pending sample question from sidebar
    if 'pending_question' in st.session_state and agent:
        pending_q = st.session_state.pending_question
        del st.session_state.pending_question
        
        # Add to chat and generate response
        if 'messages' not in st.session_state:
            st.session_state.messages = []
            
        st.session_state.messages.append({"role": "user", "content": pending_q})
        
        try:
            with st.spinner("🤖 Analyzing..."):
                response = agent.chat(pending_q)
                
                # Get the generated code using helper function
                generated_code = get_generated_code(response, agent)
                
                # Try to detect if a chart was generated
                chart_data = None
                try:
                    # Check if PandasAI generated a chart/plot
                    # Look for recently created chart files in exports/charts/
                    chart_dir = "exports/charts/"
                    if os.path.exists(chart_dir):
                        chart_files = glob.glob(os.path.join(chart_dir, "*.png"))
                        if chart_files:
                            # Get the most recent chart file
                            latest_chart = max(chart_files, key=os.path.getctime)
                            chart_data = {
                                "type": "image",
                                "path": latest_chart
                            }
                except:
                    pass
                
                # Add assistant response to chat history with generated code and chart
                message_data = {"role": "assistant", "content": str(response)}
                if generated_code:
                    message_data["generated_code"] = generated_code
                if chart_data:
                    message_data["chart_data"] = chart_data
                st.session_state.messages.append(message_data)
        except Exception as e:
            error_msg = f"❌ Analysis error: {str(e)}"
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
        
        st.rerun()
    
    # Predefined questions
    st.subheader("Quick Questions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("ROIC Analysis"):
            question = "What is the return on invested capital (ROIC) in 2024?"
            # Add to chat and generate response
            st.session_state.messages.append({"role": "user", "content": question})
            try:
                with st.spinner("🤖 Analyzing..."):
                    response = agent.chat(question)
                    
                    # Get the generated code using helper function
                    generated_code = get_generated_code(response, agent)
                    
                    # Try to detect if a chart was generated
                    chart_data = None
                    try:
                        import os
                        import glob
                        
                        # Look for recently created chart files in exports/charts/
                        chart_dir = "exports/charts/"
                        if os.path.exists(chart_dir):
                            chart_files = glob.glob(os.path.join(chart_dir, "*.png"))
                            if chart_files:
                                latest_chart = max(chart_files, key=os.path.getctime)
                                chart_data = {
                                    "type": "image",
                                    "path": latest_chart
                                }
                    except:
                        pass
                    
                    # Add assistant response to chat history with generated code and chart
                    message_data = {"role": "assistant", "content": str(response)}
                    if generated_code:
                        message_data["generated_code"] = generated_code
                    if chart_data:
                        message_data["chart_data"] = chart_data
                    st.session_state.messages.append(message_data)
            except Exception as e:
                error_msg = f"❌ Analysis error: {str(e)}"
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
            st.rerun()
    
    with col2:
        if st.button("Dividend Schedule"):
            question = "Did the company issue cash dividends in 2024 and what was the exercise date, compare the percentage to last year?"
            # Add to chat and generate response
            st.session_state.messages.append({"role": "user", "content": question})
            try:
                with st.spinner("🤖 Analyzing..."):
                    response = agent.chat(question)
                    
                    # Get the generated code using helper function
                    generated_code = get_generated_code(response, agent)
                    
                    # Try to detect if a chart was generated
                    chart_data = None
                    try:
                        import os
                        import glob
                        
                        # Look for recently created chart files in exports/charts/
                        chart_dir = "exports/charts/"
                        if os.path.exists(chart_dir):
                            chart_files = glob.glob(os.path.join(chart_dir, "*.png"))
                            if chart_files:
                                latest_chart = max(chart_files, key=os.path.getctime)
                                chart_data = {
                                    "type": "image",
                                    "path": latest_chart
                                }
                    except:
                        pass
                    
                    # Add assistant response to chat history with generated code and chart
                    message_data = {"role": "assistant", "content": str(response)}
                    if generated_code:
                        message_data["generated_code"] = generated_code
                    if chart_data:
                        message_data["chart_data"] = chart_data
                    st.session_state.messages.append(message_data)
            except Exception as e:
                error_msg = f"❌ Analysis error: {str(e)}"
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
            st.rerun()
    
    with col3:
        if st.button("Debt Analysis"):
            question = "What is the company's debt-to-equity ratio and debt coverage metrics?"
            # Add to chat and generate response
            st.session_state.messages.append({"role": "user", "content": question})
            try:
                with st.spinner("🤖 Analyzing..."):
                    response = agent.chat(question)
                    
                    # Get the generated code using helper function
                    generated_code = get_generated_code(response, agent)
                    
                    # Try to detect if a chart was generated
                    chart_data = None
                    try:
                        import os
                        import glob
                        
                        # Look for recently created chart files in exports/charts/
                        chart_dir = "exports/charts/"
                        if os.path.exists(chart_dir):
                            chart_files = glob.glob(os.path.join(chart_dir, "*.png"))
                            if chart_files:
                                latest_chart = max(chart_files, key=os.path.getctime)
                                chart_data = {
                                    "type": "image",
                                    "path": latest_chart
                                }
                    except:
                        pass
                    
                    # Add assistant response to chat history with generated code and chart
                    message_data = {"role": "assistant", "content": str(response)}
                    if generated_code:
                        message_data["generated_code"] = generated_code
                    if chart_data:
                        message_data["chart_data"] = chart_data
                    st.session_state.messages.append(message_data)
            except Exception as e:
                error_msg = f"❌ Analysis error: {str(e)}"
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
            st.rerun()
    
    # Chat Interface
    st.subheader("Chat with AI Analyst")
    
    # Initialize chat history
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for i, message in enumerate(st.session_state.messages):
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
                # Show generated code for assistant messages
                if message["role"] == "assistant" and "generated_code" in message:
                    with st.expander("🔍 View Generated Code", expanded=False):
                        st.code(message["generated_code"], language="python")
                
                # Show chart only for the latest message to avoid accumulation
                if "chart_data" in message and i == len(st.session_state.messages) - 1:
                    st.subheader("Analysis Chart")
                    # Increase chart dimensions by 200px (1000x700)
                    if message["chart_data"]["type"] == "plotly":
                        st.plotly_chart(message["chart_data"]["figure"], use_container_width=False, width=1000, height=700)
                    elif message["chart_data"]["type"] == "matplotlib":
                        st.pyplot(message["chart_data"]["figure"])
                    elif message["chart_data"]["type"] == "image":
                        st.image(message["chart_data"]["path"], width=1000)
    
        
    # Chat input with file upload support
    if user_input := st.chat_input(
        "Ask me anything about this stock...",
        accept_file=True,
        file_type=["csv", "xlsx", "json", "txt", "pdf", "jpg", "jpeg", "png"]
    ):
        # Extract text and files from the input object
        if hasattr(user_input, 'text'):
            # New format with file support
            prompt = user_input.text if user_input.text else ""
            files = user_input.files if hasattr(user_input, 'files') else []
        else:
            # Fallback for string input (when no files)
            prompt = str(user_input) if user_input else ""
            files = []
        
        # Only proceed if there's text content
        if prompt.strip():
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
        
            # Generate response only if there's text content
            if prompt.strip():
                # Generate response
                with st.chat_message("assistant"):
                    try:
                        with st.spinner("🤖 Analyzing..."):
                            response = agent.chat(prompt)
                    
                        # Display response - ensure it's a string
                        response_text = str(response) if response is not None else "No response generated"
                        st.markdown(response_text)
                        
                        # Get the generated code using helper function
                        generated_code = get_generated_code(response, agent)
                        
                        # Clear any existing chart containers
                        chart_container = st.empty()
                        
                        # Try to detect if a chart was generated and display it
                        try:
                            # Check if PandasAI generated a chart/plot
                            chart_dir = "exports/charts/"
                            if os.path.exists(chart_dir):
                                chart_files = glob.glob(os.path.join(chart_dir, "*.png"))
                                if chart_files:
                                    # Get the most recent chart file
                                    latest_chart = max(chart_files, key=os.path.getctime)
                                    with chart_container:
                                        st.image(latest_chart, use_column_width=True)
                        except Exception as e:
                            # Chart display failed, continue without error
                            pass
                        
                        # Add assistant response to chat history
                        message_data = {"role": "assistant", "content": response_text}
                        if generated_code:
                            message_data["generated_code"] = generated_code
                        st.session_state.messages.append(message_data)
                        
                        # Display generated code in expandable container
                        if generated_code:
                            with st.expander("View Generated Code", expanded=False):
                                st.code(generated_code, language="python")
                        
                    except Exception as e:
                        error_msg = f"❌ Analysis error: {str(e)}"
                        st.error(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    # Chat controls
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Show Table", use_container_width=True):
            if 'display_dataframes' in st.session_state:
                with st.expander("Financial Data"):
                    for name, df in st.session_state.display_dataframes.items():
                        st.subheader(name)
                        
                        # Transpose financial statements from long to wide format
                        if name in ['CashFlow', 'BalanceSheet', 'IncomeStatement']:
                            try:
                                # Create wide format with years/quarters as columns
                                if 'yearReport' in df.columns:
                                    df_clean = df.drop('ticker', axis=1, errors='ignore')
                                    
                                    # Handle quarterly vs annual data based on period parameter and actual data content
                                    if ('lengthReport' in df.columns and period == 'quarter' and 
                                        df['lengthReport'].isin([1, 2, 3, 4]).any()):
                                        # Rename lengthReport to Quarter for more intuitive AI queries
                                        df_clean = df_clean.rename(columns={'lengthReport': 'Quarter'})
                                        # Create unique identifiers for quarters (e.g., "2024-Q1", "2024-Q2")
                                        df_clean['period_id'] = df_clean['yearReport'].astype(str) + '-Q' + df_clean['Quarter'].astype(str)
                                        df_wide = df_clean.set_index('period_id').T
                                        # Drop redundant yearReport and Quarter rows since info is now in column headers
                                        df_wide = df_wide.drop(['yearReport', 'Quarter'], axis=0, errors='ignore')
                                    else:
                                        # Annual data - use year only
                                        df_wide = df_clean.set_index('yearReport').T
                                        # Drop lengthReport row for annual data since it's not meaningful
                                        df_wide = df_wide.drop(['lengthReport'], axis=0, errors='ignore')
                                    
                                    df_wide = df_wide.reset_index()
                                    df_wide = df_wide.rename(columns={'index': 'Metric'})
                                    st.dataframe(df_wide)
                                else:
                                    st.dataframe(df)
                            except Exception as e:
                                st.warning(f"Could not transpose {name}: {str(e)}")
                                st.dataframe(df)
                        
                        elif name == 'Ratios':
                            try:
                                # Handle Ratios dataframe - check structure first
                                if hasattr(df, 'columns') and len(df.columns) > 0:
                                    # Check if years are already in columns (numeric years)
                                    year_cols = [str(col) for col in df.columns if str(col).isdigit() and len(str(col)) == 4]
                                    
                                    if len(year_cols) > 1:
                                        # Years are already columns, display as-is
                                        st.dataframe(df)
                                    elif 'yearReport' in df.columns:
                                        # Standard long format, transpose to wide
                                        df_clean = df.drop('ticker', axis=1, errors='ignore')
                                        
                                        # Handle quarterly vs annual data based on period parameter and actual data content
                                        if ('lengthReport' in df.columns and period == 'quarter' and 
                                            df['lengthReport'].isin([1, 2, 3, 4]).any()):
                                            # Rename lengthReport to Quarter for more intuitive AI queries
                                            df_clean = df_clean.rename(columns={'lengthReport': 'Quarter'})
                                            # Create unique identifiers for quarters (e.g., "2024-Q1", "2024-Q2")
                                            df_clean['period_id'] = df_clean['yearReport'].astype(str) + '-Q' + df_clean['Quarter'].astype(str)
                                            df_wide = df_clean.set_index('period_id').T
                                            # Drop redundant yearReport and Quarter rows since info is now in column headers
                                            df_wide = df_wide.drop(['yearReport', 'Quarter'], axis=0, errors='ignore')
                                        else:
                                            # Annual data - use year only
                                            df_wide = df_clean.set_index('yearReport').T
                                            # Drop lengthReport row for annual data since it's not meaningful
                                            df_wide = df_wide.drop(['lengthReport'], axis=0, errors='ignore')
                                        
                                        df_wide = df_wide.reset_index()
                                        df_wide = df_wide.rename(columns={'index': 'Metric'})
                                        st.dataframe(df_wide)
                                    else:
                                        # Multi-index or other format, try simple transpose
                                        df_transposed = df.T
                                        df_transposed = df_transposed.reset_index()
                                        df_transposed = df_transposed.rename(columns={'index': 'Metric'})
                                        st.dataframe(df_transposed)
                                else:
                                    st.dataframe(df)
                            except Exception as e:
                                st.warning(f"Could not transpose {name}: {str(e)}")
                                st.dataframe(df)
                        
                        else:
                            # For Dividends and other data, display as-is
                            st.dataframe(df)
            else:
                st.warning("⚠️ No data loaded yet. Please click 'Analyze Stock' first to load financial data.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p>Tip: Specify the table you want to analyze for more accurate results and customize charts by including any desired technical settings in your prompt</p>
        <p>Built with <a href="https://streamlit.io" target="_blank">Streamlit</a>, <a href="https://pandas-ai.com" target="_blank">PandasAI</a>, and <a href="https://github.com/thinh-vu/vnstock" target="_blank">Vnstock</a> by <a href="https://github.com/thinh-vu" target="_blank">Thinh Vu</a></p>
    </div>
    """,
    unsafe_allow_html=True
)
