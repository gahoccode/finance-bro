import os
import streamlit as st
import pandas as pd
from vnstock import Vnstock
import warnings

# pandasai v2.4.2 imports
from pandasai import Agent
from pandasai.llm import OpenAI
import warnings

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
    page_title="Finance Bro - AI Stock Analysis",
    page_icon="📈",
    layout="wide"
)

# Load custom CSS
with open('static/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-header">📈 Finance Bro - AI Stock Analysis</h1>', unsafe_allow_html=True)

# API Key handling
if 'api_key' not in st.session_state:
    st.session_state.api_key = os.environ.get("OPENAI_API_KEY", "")

if not st.session_state.api_key:
    st.warning("🔑 OpenAI API Key Required")
    
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
    st.header("📊 Stock Configuration")
    
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
    
    analyze_button = st.button("🔍 Analyze Stock", type="primary", use_container_width=True)
    
    # Sample Questions - dropdown menu in sidebar
    st.markdown("---")
    st.subheader("💡 Sample Questions")
    
    sample_questions = [
        "What is the return on invested capital (ROIC) trend?",
        "Analyze the dividend yield and payout ratio trends",
        "What is the company's debt-to-equity ratio?",
        "Compare revenue growth across years",
        "What are the key financial strengths and weaknesses?",
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
    
    if selected_question != "Choose a question..." and st.button("🤖 Ask Question", use_container_width=True):
        # Store the selected question for processing
        st.session_state.pending_question = selected_question
    
    # Clear Chat button in sidebar
    st.markdown("---")
    if st.button("🗑️ Clear Chat", use_container_width=True, key="sidebar_clear_chat"):
        st.session_state.messages = []
        st.rerun()

# Main content area
if analyze_button and stock_symbol:
    try:
        with st.spinner(f"📊 Loading data for {stock_symbol}..."):
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
            
            # Store dataframes in session state
            st.session_state.dataframes = {
                'CashFlow': CashFlow,
                'BalanceSheet': BalanceSheet,
                'IncomeStatement': IncomeStatement,
                'Ratios': Ratio,
                'Dividends': dividend_schedule
            }
            
            st.session_state.stock_symbol = stock_symbol
            st.success(f"✅ Successfully loaded data for {stock_symbol}")
    
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        st.info("Please check the stock symbol and try again.")

# AI Analysis section
if 'dataframes' in st.session_state:
    st.header(f"🤖 AI Analysis for {st.session_state.stock_symbol}")
    
    # Initialize LLM with OpenAI for pandasai v2.4.2
    llm = OpenAI(api_token=st.session_state.api_key)
    
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
                    import os
                    import glob
                    
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
        if st.button("📈 ROIC Analysis"):
            question = "What is the return on invested capital (ROIC) trend and how does it compare to industry standards?"
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
        if st.button("💰 Dividend Yield"):
            question = "Analyze the dividend yield and payout ratio trends over the past years"
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
        if st.button("⚖️ Debt Analysis"):
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
    st.subheader("💬 Chat with AI Analyst")
    
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
                    st.subheader("📊 Analysis Chart")
                    # Increase chart dimensions by 200px (1000x700)
                    if message["chart_data"]["type"] == "plotly":
                        st.plotly_chart(message["chart_data"]["figure"], use_container_width=False, width=1000, height=700)
                    elif message["chart_data"]["type"] == "matplotlib":
                        st.pyplot(message["chart_data"]["figure"])
                    elif message["chart_data"]["type"] == "image":
                        st.image(message["chart_data"]["path"], width=1000)
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about this stock..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            try:
                with st.spinner("🤖 Analyzing..."):
                    response = agent.chat(prompt)
                    
                    # Display response
                    st.markdown(response)
                    
                    # Get the generated code using helper function
                    generated_code = get_generated_code(response, agent)
                    
                    # Try to detect if a chart was generated
                    chart_data = None
                    try:
                        # Check if PandasAI generated a chart/plot
                        import os
                        import glob
                        
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
                    
                    # Display generated code in expandable container
                    if generated_code:
                        with st.expander("🔍 View Generated Code", expanded=False):
                            st.code(generated_code, language="python")
                    
            except Exception as e:
                error_msg = f"❌ Analysis error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    # Chat controls
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 Show Raw Data", use_container_width=True):
            with st.expander("📊 Financial Data"):
                for name, df in st.session_state.dataframes.items():
                    st.subheader(name)
                    
                    # Transpose financial statements from long to wide format
                    if name in ['CashFlow', 'BalanceSheet', 'IncomeStatement']:
                        try:
                            # Create wide format with years/quarters as columns
                            if 'yearReport' in df.columns:
                                df_clean = df.drop('ticker', axis=1, errors='ignore')
                                
                                # Handle quarterly data by combining year and quarter
                                if 'lengthReport' in df.columns:
                                    # Create unique identifiers for quarters (e.g., "2024-Q1", "2024-Q2")
                                    df_clean['period_id'] = df_clean['yearReport'].astype(str) + '-Q' + df_clean['lengthReport'].astype(str)
                                    df_wide = df_clean.set_index('period_id').T
                                else:
                                    # Annual data - use year only
                                    df_wide = df_clean.set_index('yearReport').T
                                
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
                                    
                                    # Handle quarterly data by combining year and quarter
                                    if 'lengthReport' in df.columns:
                                        # Create unique identifiers for quarters (e.g., "2024-Q1", "2024-Q2")
                                        df_clean['period_id'] = df_clean['yearReport'].astype(str) + '-Q' + df_clean['lengthReport'].astype(str)
                                        df_wide = df_clean.set_index('period_id').T
                                    else:
                                        # Annual data - use year only
                                        df_wide = df_clean.set_index('yearReport').T
                                    
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

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p>💡 Tip: Ask specific questions for more insightful analysis results, and customize charts by including any desired settings in your prompt</p>
        <p>Built with using Streamlit, PandasAI, and Vnstock</p>
    </div>
    """,
    unsafe_allow_html=True
)
