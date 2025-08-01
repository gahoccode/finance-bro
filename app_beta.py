import os
import glob
import streamlit as st
import pandas as pd
from vnstock import Vnstock
import warnings

# pandasai v3.x beta imports
import pandasai as pai
from pandasai_litellm import LiteLLM

warnings.filterwarnings("ignore")

# Helper function to extract generated code from PandasAI response
def get_generated_code(response):
    """Extract generated code from PandasAI v3.x response"""
    try:
        # For v3.x, check response attributes
        if hasattr(response, 'code'):
            return response.code
        elif hasattr(response, 'last_code_executed'):
            return response.last_code_executed
        return "# Code generation details not available"
    except Exception as e:
        return f"# Error accessing code: {str(e)}"

# Page configuration
st.set_page_config(
    page_title="Finance Bro - Beta",
    layout="wide"
)

# Load custom CSS
try:
    with open('static/style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except FileNotFoundError:
    pass

# Title
st.markdown('<h1 class="main-header">Finance Bro - Beta</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #666; font-size: 1.1rem; margin-top: -0.5rem; margin-bottom: 1rem;">Ask your finance bro about your company\'s financial statements (PandasAI v3.x Beta)</p>', unsafe_allow_html=True)

# Authentication handling
if not st.user.is_logged_in:
    st.title("🔒 Authentication Required")
    st.markdown("Please authenticate with Google to access Finance Bro")
    st.button("Login with Google", on_click=st.login)
    st.markdown("---")
    st.info("After logging in, you'll be redirected back to the app automatically.")
    st.stop()

# User is now authenticated - show welcome message in sidebar
st.sidebar.success("Successfully logged in")

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
    
    # User logout option
    if st.sidebar.button("Logout", use_container_width=True):
        st.logout()
    
    st.sidebar.markdown("---")
    
    # User input fields
    stock_symbol = st.text_input(
        "Stock Symbol:",
        value="REE",
        placeholder="e.g., VIC, VNM, FPT"
    ).upper()
    
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
        st.session_state.pending_question = selected_question
    
    # Clear Chat button in sidebar
    st.markdown("---")
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
                <div style='font-size: 0.8rem; color: #000000; font-weight: 600; line-height: 1;'>Finance Bro Beta</div>
                <div style='font-size: 0.7rem; color: #000000; line-height: 1;'>PandasAI v3.x</div>
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
if (analyze_button and stock_symbol) or (period_changed and 'stock_symbol' in st.session_state):
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
            dividend_schedule_AI = dividend_schedule.copy()
            
            # Configure PandasAI with LiteLLM (v3.x beta)
            llm = LiteLLM(
                model="gpt-4.1-mini",
                api_key=st.session_state.api_key,
                api_base="https://api.openai.com/v1"
            )
            pai.config.set({"llm": llm})
            
            # Create semantic dataframes for v3.x (replacing SmartDataframe/Agent)
            df_cashflow = pai.DataFrame(CashFlow_AI, name="CashFlow")
            df_balancesheet = pai.DataFrame(BalanceSheet_AI, name="BalanceSheet")
            df_incomestatement = pai.DataFrame(IncomeStatement_AI, name="IncomeStatement")
            df_ratios = pai.DataFrame(Ratio_AI, name="Ratios")
            df_dividends = pai.DataFrame(dividend_schedule_AI, name="Dividends")
            
            # Store semantic dataframes for chat usage
            st.session_state.semantic_dataframes = [
                df_cashflow, df_balancesheet, df_incomestatement, df_ratios, df_dividends
            ]
            
            st.session_state.stock_symbol = stock_symbol
            st.session_state.last_period = period
            st.success(f"✅ Successfully loaded data for {stock_symbol} with PandasAI v3.x")
            st.rerun()
            
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")

# Chat interface
if 'semantic_dataframes' in st.session_state:
    st.markdown("---")
    st.subheader(f"💬 Chat with Finance Bro about {st.session_state.stock_symbol}")
    
    # Initialize chat history
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Handle pending questions from sidebar
    if 'pending_question' in st.session_state:
        pending_question = st.session_state.pending_question
        del st.session_state.pending_question
        
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": pending_question})
        
        # Generate response using v3.x API
        with st.chat_message("assistant"):
            try:
                with st.spinner("🤖 Analyzing..."):
                    response = pai.chat(pending_question, *st.session_state.semantic_dataframes)
                    
                    # Display response
                    st.markdown(response)
                    
                    # Get the generated code
                    generated_code = get_generated_code(response)
                    
                    # Add assistant response to chat history
                    message_data = {"role": "assistant", "content": str(response)}
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
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "generated_code" in message:
                with st.expander("View Generated Code", expanded=False):
                    st.code(message["generated_code"], language="python")
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about this stock..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response using v3.x API
        with st.chat_message("assistant"):
            try:
                with st.spinner("🤖 Analyzing..."):
                    response = pai.chat(prompt, *st.session_state.semantic_dataframes)
                    
                    # Display response
                    st.markdown(response)
                    
                    # Get the generated code
                    generated_code = get_generated_code(response)
                    
                    # Add assistant response to chat history
                    message_data = {"role": "assistant", "content": str(response)}
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
                                    
                                    # Handle quarterly vs annual data
                                    if ('lengthReport' in df.columns and period == 'quarter' and 
                                        df['lengthReport'].isin([1, 2, 3, 4]).any()):
                                        # Rename lengthReport to Quarter for more intuitive AI queries
                                        df_clean = df_clean.rename(columns={'lengthReport': 'Quarter'})
                                        # Create unique identifiers for quarters
                                        df_clean['period_id'] = df_clean['yearReport'].astype(str) + '-Q' + df_clean['Quarter'].astype(str)
                                        df_wide = df_clean.set_index('period_id').T
                                        # Drop redundant yearReport and Quarter rows
                                        df_wide = df_wide.drop(['yearReport', 'Quarter'], axis=0, errors='ignore')
                                    else:
                                        # Annual data - use year only
                                        df_wide = df_clean.set_index('yearReport').T
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
                                # Handle Ratios dataframe
                                if hasattr(df, 'columns') and len(df.columns) > 0:
                                    # Check if years are already in columns
                                    year_cols = [str(col) for col in df.columns if str(col).isdigit() and len(str(col)) == 4]
                                    
                                    if len(year_cols) > 1:
                                        # Years are already columns, display as-is
                                        st.dataframe(df)
                                    elif 'yearReport' in df.columns:
                                        # Standard long format, transpose to wide
                                        df_clean = df.drop('ticker', axis=1, errors='ignore')
                                        
                                        # Handle quarterly vs annual data
                                        if ('lengthReport' in df.columns and period == 'quarter' and 
                                            df['lengthReport'].isin([1, 2, 3, 4]).any()):
                                            df_clean = df_clean.rename(columns={'lengthReport': 'Quarter'})
                                            df_clean['period_id'] = df_clean['yearReport'].astype(str) + '-Q' + df_clean['Quarter'].astype(str)
                                            df_wide = df_clean.set_index('period_id').T
                                            df_wide = df_wide.drop(['yearReport', 'Quarter'], axis=0, errors='ignore')
                                        else:
                                            df_wide = df_clean.set_index('yearReport').T
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
        <p>Built with <a href="https://streamlit.io" target="_blank">Streamlit</a>, <a href="https://pandas-ai.com" target="_blank">PandasAI v3.x Beta</a>, and <a href="https://github.com/thinh-vu/vnstock" target="_blank">Vnstock</a></p>
    </div>
    """,
    unsafe_allow_html=True
)
