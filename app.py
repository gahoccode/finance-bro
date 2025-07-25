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

# Page configuration
st.set_page_config(
    page_title="Finance Bro - AI Stock Analysis",
    page_icon="📈",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton > button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
        transition: background-color 0.3s;
    }
    .stButton > button:hover {
        background-color: #0d5a8f;
    }
    </style>
""", unsafe_allow_html=True)

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
            Ratio = stock.finance.ratio(period=period, lang="en", dropna=True)
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
    
    # Use SmartDataframe approach for v2.4.2 to avoid tuple errors
    from pandasai import SmartDataframe
    
    # Create SmartDataframes first
    smart_dfs = []
    for name, df in st.session_state.dataframes.items():
        smart_df = SmartDataframe(df, config={"llm": llm})
        smart_dfs.append(smart_df)
    
    # Use the first SmartDataframe as the main agent
    agent = smart_dfs[0] if smart_dfs else None
    
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
                    st.session_state.messages.append({"role": "assistant", "content": str(response)})
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
                    st.session_state.messages.append({"role": "assistant", "content": str(response)})
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
                    st.session_state.messages.append({"role": "assistant", "content": str(response)})
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
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
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
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": str(response)})
                    
            except Exception as e:
                error_msg = f"❌ Analysis error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    # Chat controls
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    
    with col2:
        if st.button("📊 Show Raw Data", use_container_width=True):
            with st.expander("📊 Financial Data"):
                for name, df in st.session_state.dataframes.items():
                    st.subheader(name)
                    st.dataframe(df)
    
    with col3:
        # Sample Questions - always visible
        with st.expander("💡 Sample Questions"):
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
            
            for i, q in enumerate(sample_questions):
                if st.button(q, key=f"sample_q_{i}", use_container_width=True):
                    # Add user message to chat history
                    st.session_state.messages.append({"role": "user", "content": q})
                    
                    # Generate AI response immediately
                    try:
                        with st.spinner("🤖 Analyzing..."):
                            response = agent.chat(q)
                            st.session_state.messages.append({"role": "assistant", "content": str(response)})
                    except Exception as e:
                        error_msg = f"❌ Analysis error: {str(e)}"
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    
                    st.rerun()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p>💡 Tip: Use specific questions for better analysis results</p>
        <p>Built with ❤️ using Streamlit, PandasAI, and Vnstock</p>
    </div>
    """,
    unsafe_allow_html=True
)
