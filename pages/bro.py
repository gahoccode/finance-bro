import os
from src.services.chart_service import detect_latest_chart
from src.core.config import VNSTOCK_API_KEY_ENV
import streamlit as st
import pandas as pd
from vnstock import Vnstock, Listing, register_user
from vnstock.core.utils.transform import flatten_hierarchical_index
import warnings

# pandasai v2.4.2 imports
from pandasai import Agent
from pandasai.llm import OpenAI

warnings.filterwarnings("ignore")

# Setup Vnstock API key if available
_vnstock_api_key = os.environ.get(VNSTOCK_API_KEY_ENV, "")
if _vnstock_api_key:
    try:
        register_user(_vnstock_api_key)
        if "vnstock_registered" not in st.session_state:
            st.session_state.vnstock_registered = True
    except Exception:
        # Silently fail if registration doesn't work - vnstock will work in free tier
        pass


# Helper function to extract generated code from PandasAI response/agent
def get_generated_code(response, agent):
    """Extract generated code from PandasAI response or agent object"""
    try:
        # Try response object first
        if hasattr(response, "last_code_executed") and response.last_code_executed:
            return response.last_code_executed

        # Try agent object
        if hasattr(agent, "last_code_executed") and agent.last_code_executed:
            return agent.last_code_executed

        # Try agent's memory or context
        if hasattr(agent, "memory") and hasattr(agent.memory, "get_last_code"):
            code = agent.memory.get_last_code()
            if code:
                return code

        # Try to find code in agent's internal state
        for attr_name in ["_last_code_generated", "_code_executed", "last_code"]:
            if hasattr(agent, attr_name):
                code = getattr(agent, attr_name)
                if code and isinstance(code, str) and len(code.strip()) > 5:
                    return code

        return "# Code generation details not available"

    except Exception as e:
        return f"# Error accessing code: {str(e)}"


def process_agent_response(agent, question):
    """Process agent response and return formatted message data"""
    try:
        with st.spinner("🤖 Analyzing..."):
            response = agent.chat(question)

            # Get the generated code
            generated_code = get_generated_code(response, agent)

            # Detect chart
            chart_data = detect_latest_chart()

            # Create message data
            message_data = {"role": "assistant", "content": str(response)}
            if generated_code:
                message_data["generated_code"] = generated_code
            if chart_data:
                message_data["chart_data"] = chart_data

            return message_data

    except Exception as e:
        return {"role": "assistant", "content": f"Analysis error: {str(e)}"}


def transpose_financial_dataframe(df, name, period):
    """Transpose financial dataframes from long to wide format"""
    try:
        if name in ["CashFlow", "BalanceSheet", "IncomeStatement"]:
            if "yearReport" in df.columns:
                df_clean = df.drop("ticker", axis=1, errors="ignore")

                # Handle quarterly vs annual data
                if (
                    "lengthReport" in df.columns
                    and period == "quarter"
                    and df["lengthReport"].isin([1, 2, 3, 4]).any()
                ):
                    # Quarterly data
                    df_clean = df_clean.rename(columns={"lengthReport": "Quarter"})
                    df_clean["period_id"] = (
                        df_clean["yearReport"].astype(str)
                        + "-Q"
                        + df_clean["Quarter"].astype(str)
                    )
                    df_wide = df_clean.set_index("period_id").T
                    df_wide = df_wide.drop(
                        ["yearReport", "Quarter"], axis=0, errors="ignore"
                    )
                else:
                    # Annual data
                    df_wide = df_clean.set_index("yearReport").T
                    df_wide = df_wide.drop(["lengthReport"], axis=0, errors="ignore")

                df_wide = df_wide.reset_index()
                df_wide = df_wide.rename(columns={"index": "Metric"})
                return df_wide

        elif name == "Ratios":
            if hasattr(df, "columns") and len(df.columns) > 0:
                # Check if years are already in columns
                year_cols = [
                    str(col)
                    for col in df.columns
                    if str(col).isdigit() and len(str(col)) == 4
                ]

                if len(year_cols) > 1:
                    # Years already in columns
                    return df
                elif "yearReport" in df.columns:
                    # Standard long format, transpose to wide
                    df_clean = df.drop("ticker", axis=1, errors="ignore")

                    if (
                        "lengthReport" in df.columns
                        and period == "quarter"
                        and df["lengthReport"].isin([1, 2, 3, 4]).any()
                    ):
                        # Quarterly data
                        df_clean = df_clean.rename(columns={"lengthReport": "Quarter"})
                        df_clean["period_id"] = (
                            df_clean["yearReport"].astype(str)
                            + "-Q"
                            + df_clean["Quarter"].astype(str)
                        )
                        df_wide = df_clean.set_index("period_id").T
                        df_wide = df_wide.drop(
                            ["yearReport", "Quarter"], axis=0, errors="ignore"
                        )
                    else:
                        # Annual data
                        df_wide = df_clean.set_index("yearReport").T
                        df_wide = df_wide.drop(
                            ["lengthReport"], axis=0, errors="ignore"
                        )

                    df_wide = df_wide.reset_index()
                    df_wide = df_wide.rename(columns={"index": "Metric"})
                    return df_wide
                else:
                    # Multi-index or other format
                    df_transposed = df.T
                    df_transposed = df_transposed.reset_index()
                    df_transposed = df_transposed.rename(columns={"index": "Metric"})
                    return df_transposed

        # For other dataframes, return as-is
        return df

    except Exception:
        # If transposition fails, return original dataframe
        return df


# Page configuration
st.set_page_config(
    page_title="Finance Bro",
    # page_icon="",
    layout="wide",
)

# CSS loading removed

# Get stock symbol from session state (set in main app)
# If not available, show message to use main app first
if "stock_symbol" in st.session_state and st.session_state.stock_symbol:
    stock_symbol = st.session_state.stock_symbol
else:
    st.warning(
        "No stock symbol selected. Please go to the main Finance Bro page and select a stock symbol first."
    )
    st.stop()

# Title
st.markdown("# Finance Bro")
st.markdown("Ask your finance bro about your company's financial statements")


# Load stock symbols and cache in session state if not already loaded
if "stock_symbols_list" not in st.session_state:
    try:
        with st.spinner("Loading stock symbols..."):
            symbols_df = Listing().all_symbols()
            st.session_state.stock_symbols_list = sorted(symbols_df["symbol"].tolist())
            st.session_state.symbols_df = (
                symbols_df  # Cache the full DataFrame for organ_name access
            )
            st.success("Stock symbols loaded and cached!")
    except Exception as e:
        st.warning(f"Could not load stock symbols from vnstock: {str(e)}")
        st.session_state.stock_symbols_list = [
            "REE",
            "VIC",
            "VNM",
            "VCB",
            "BID",
            "HPG",
            "FPT",
            "FMC",
            "DHC",
        ]
        st.session_state.symbols_df = None

# API Key handling
if "api_key" not in st.session_state:
    st.session_state.api_key = os.environ.get("OPENAI_API_KEY", "")

if not st.session_state.api_key:
    st.warning("OpenAI API Key Required")

    with st.expander("Enter API Key", expanded=True):
        api_key_input = st.text_input(
            "OpenAI API Key:",
            type="password",
            placeholder="sk-...",
            help="Enter your OpenAI API key to enable AI analysis",
        )

        if st.button("Save API Key", type="primary"):
            if api_key_input.startswith("sk-"):
                st.session_state.api_key = api_key_input
                os.environ["OPENAI_API_KEY"] = api_key_input
                st.success("API Key saved successfully!")
                st.rerun()
            else:
                st.error("Invalid API key format. Please check your key.")

    st.stop()

# Sidebar for stock configuration
with st.sidebar:
    st.header("Stock configuration")

    # Show current stock symbol from session state
    st.metric("Current symbol", stock_symbol, border=True)

    period = st.segmented_control("Period", options=["year", "quarter"], default="year")

    source = st.selectbox("Data Source:", options=["VCI", "TCBS"], index=0)

    company_source = st.selectbox(
        "Company Data Source:", options=["TCBS", "VCI"], index=0
    )

    analyze_button = st.button(
        "Analyze Stock", type="primary", use_container_width=True
    )

    # Sample questions - dropdown menu in sidebar
    st.subheader("Sample questions")

    sample_questions = [
        "What is the return on invested capital (ROIC) trend?",
        "What is the company's debt-to-equity ratio?",
        "What's 2024 revenue growth?",
        "What's the ROE in 2024?",
        "How has cash flow evolved over time?",
        "What is the company's profitability trend?",
        "Analyze the balance sheet health indicators",
    ]

    selected_question = st.selectbox(
        "Select a question to analyze:",
        options=["Choose a question..."] + sample_questions,
        index=0,
        key="sample_question_selector",
    )

    if selected_question != "Choose a question..." and st.button(
        "Ask Question", use_container_width=True
    ):
        # Store the selected question for processing
        st.session_state.pending_question = selected_question

    # Clear Chat button in sidebar

    # Display current theme
    with st.sidebar.expander("Theme", expanded=False):
        try:
            # Check if dark mode is enabled
            is_dark = st.get_option("theme.base") == "dark"
            if is_dark:
                st.write("**Dark Mode**")
            else:
                st.write("**Light Mode**")
        except Exception:
            st.write("**Theme unavailable**")

    if st.button("Clear Chat", use_container_width=True, key="sidebar_clear_chat"):
        st.session_state.messages = []
        st.rerun()

    st.markdown(
        "[Finance Bro on GitHub](https://github.com/gahoccode/finance-bro) by Tam Le"
    )

# Check if period has changed and data needs to be reloaded
period_changed = False
if "last_period" in st.session_state and st.session_state.last_period != period:
    period_changed = True

# Main content area
if analyze_button or (period_changed and "stock_symbol" in st.session_state):
    try:
        with st.spinner(f"Loading data for {stock_symbol}..."):
            # Initialize Vnstock
            stock = Vnstock().stock(symbol=stock_symbol, source=source)
            company = (
                Vnstock().stock(symbol=stock_symbol, source=company_source).company
            )

            # Load financial data
            CashFlow = stock.finance.cash_flow(period=period)
            BalanceSheet = stock.finance.balance_sheet(
                period=period, lang="en", dropna=True
            )
            IncomeStatement = stock.finance.income_statement(
                period=period, lang="en", dropna=True
            )

            # Load and process Ratio data (multi-index columns)
            Ratio_raw = stock.finance.ratio(period=period, lang="en", dropna=True)

            # Use vnstock's built-in flatten_hierarchical_index function
            Ratio = flatten_hierarchical_index(
                Ratio_raw, separator="_", handle_duplicates=True, drop_levels=0
            )

            # Dividends data not available in vnstock - use empty DataFrame
            dividend_schedule = pd.DataFrame()

            # Store original dataframes for display (keep original column names)
            st.session_state.display_dataframes = {
                "CashFlow": CashFlow,
                "BalanceSheet": BalanceSheet,
                "IncomeStatement": IncomeStatement,
                "Ratios": Ratio,
                "Dividends": dividend_schedule,
            }

            # Create copies with renamed columns for PandasAI (better query compatibility)
            CashFlow_AI = CashFlow.copy()
            BalanceSheet_AI = BalanceSheet.copy()
            IncomeStatement_AI = IncomeStatement.copy()
            Ratio_AI = Ratio.copy()

            if period == "quarter":
                # Rename columns in AI copies for better query compatibility
                if (
                    "lengthReport" in CashFlow_AI.columns
                    and CashFlow_AI["lengthReport"].isin([1, 2, 3, 4]).any()
                ):
                    CashFlow_AI = CashFlow_AI.rename(
                        columns={"lengthReport": "Quarter"}
                    )

                if (
                    "lengthReport" in BalanceSheet_AI.columns
                    and BalanceSheet_AI["lengthReport"].isin([1, 2, 3, 4]).any()
                ):
                    BalanceSheet_AI = BalanceSheet_AI.rename(
                        columns={"lengthReport": "Quarter"}
                    )

                if (
                    "lengthReport" in IncomeStatement_AI.columns
                    and IncomeStatement_AI["lengthReport"].isin([1, 2, 3, 4]).any()
                ):
                    IncomeStatement_AI = IncomeStatement_AI.rename(
                        columns={"lengthReport": "Quarter"}
                    )

                if (
                    "lengthReport" in Ratio_AI.columns
                    and Ratio_AI["lengthReport"].isin([1, 2, 3, 4]).any()
                ):
                    Ratio_AI = Ratio_AI.rename(columns={"lengthReport": "Quarter"})

            # Store AI-optimized dataframes for PandasAI
            st.session_state.dataframes = {
                "CashFlow": CashFlow_AI,
                "BalanceSheet": BalanceSheet_AI,
                "IncomeStatement": IncomeStatement_AI,
                "Ratios": Ratio_AI,
                "Dividends": dividend_schedule,
            }

            st.session_state.stock_symbol = stock_symbol
            st.session_state.last_period = (
                period  # Store current period to detect changes
            )

    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.info("Please check the stock symbol and try again.")

# AI Analysis section
if "dataframes" in st.session_state:
    # Get company full name from cached symbols DataFrame
    company_name = st.session_state.stock_symbol
    if "symbols_df" in st.session_state and st.session_state.symbols_df is not None:
        try:
            symbols_df = st.session_state.symbols_df
            matching_company = symbols_df[
                symbols_df["symbol"] == st.session_state.stock_symbol
            ]
            if not matching_company.empty and "organ_name" in symbols_df.columns:
                company_name = matching_company["organ_name"].iloc[0]
        except Exception:
            company_name = st.session_state.stock_symbol

    st.header(company_name)

    # Initialize LLM with OpenAI for pandasai v2.4.2
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    llm = OpenAI(api_token=st.session_state.api_key, model=model)

    # Initialize session state for uploaded files if not exists
    if "uploaded_dataframes" not in st.session_state:
        st.session_state.uploaded_dataframes = []

    def get_or_create_agent():
        """
        Creates or retrieves cached PandasAI agent with all available dataframes.
        Only recreates when dataframes have changed.
        """
        # Create unique key based on current dataframes
        stock_df_count = (
            len(st.session_state.dataframes) if "dataframes" in st.session_state else 0
        )
        uploaded_df_count = len(st.session_state.uploaded_dataframes)
        current_key = f"agent_{stock_df_count}_{uploaded_df_count}"

        # Check if agent exists and is up to date
        if (
            "agent" in st.session_state
            and "agent_key" in st.session_state
            and st.session_state.agent_key == current_key
        ):
            return st.session_state.agent

        # Create new agent with all dataframes
        all_dataframes = []
        if "dataframes" in st.session_state:
            all_dataframes.extend(list(st.session_state.dataframes.values()))
        all_dataframes.extend(st.session_state.uploaded_dataframes)

        if not all_dataframes:
            return None

        agent = Agent(all_dataframes, config={"llm": llm, "verbose": True})

        # Cache the agent
        st.session_state.agent = agent
        st.session_state.agent_key = current_key

        return agent

    # Process any pending sample question from sidebar
    if "pending_question" in st.session_state:
        agent = get_or_create_agent()
        if agent:
            pending_q = st.session_state.pending_question
            del st.session_state.pending_question

            # Add to chat and generate response
            if "messages" not in st.session_state:
                st.session_state.messages = []

            st.session_state.messages.append({"role": "user", "content": pending_q})

            # Process agent response
            message_data = process_agent_response(agent, pending_q)
            st.session_state.messages.append(message_data)

        st.rerun()

    # Predefined questions
    st.subheader("Quick questions")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("ROIC Analysis"):
            agent = get_or_create_agent()
            if agent:
                question = "What is the return on invested capital (ROIC) in 2024?"
                st.session_state.messages.append({"role": "user", "content": question})
                message_data = process_agent_response(agent, question)
                st.session_state.messages.append(message_data)
                st.rerun()

    with col2:
        if st.button("Debt Analysis"):
            agent = get_or_create_agent()
            if agent:
                question = "What is the company's debt-to-equity ratio and debt coverage metrics?"
                st.session_state.messages.append({"role": "user", "content": question})
                message_data = process_agent_response(agent, question)
                st.session_state.messages.append(message_data)
                st.rerun()

    # Chat Interface
    st.subheader("Chat with AI analyst")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for i, message in enumerate(st.session_state.messages):
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

                # Show generated code for assistant messages
                if message["role"] == "assistant" and "generated_code" in message:
                    with st.expander("View Generated Code", expanded=False):
                        st.code(message["generated_code"], language="python")

                # Show chart only for the latest message to avoid accumulation
                if "chart_data" in message and i == len(st.session_state.messages) - 1:
                    st.subheader("Analysis chart")
                    # Increase chart dimensions by 200px (1000x700)
                    if message["chart_data"]["type"] == "plotly":
                        st.plotly_chart(
                            message["chart_data"]["figure"],
                            use_container_width=False,
                            width=1000,
                            height=700,
                        )
                    elif message["chart_data"]["type"] == "matplotlib":
                        st.pyplot(message["chart_data"]["figure"])
                    elif message["chart_data"]["type"] == "image":
                        st.image(message["chart_data"]["path"], width=1000)

    # Chat input with file upload support
    if user_input := st.chat_input(
        "Ask me anything about this stock...",
        accept_file=True,
        file_type=["csv", "xlsx"],
    ):
        # Extract text and files from the input object
        if hasattr(user_input, "text"):
            # New format with file support
            prompt = user_input.text if user_input.text else ""
            files = user_input.files if hasattr(user_input, "files") else []
        else:
            # Fallback for string input (when no files)
            prompt = str(user_input) if user_input else ""
            files = []

        # Process uploaded files and add to session state
        if files:
            for file in files:
                try:
                    if file.name.endswith(".csv"):
                        df = pd.read_csv(file)
                        st.session_state.uploaded_dataframes.append(df)
                        st.info(f"Loaded CSV file: {file.name} ({len(df)} rows)")
                    elif file.name.endswith((".xlsx", ".xls")):
                        df = pd.read_excel(file)
                        st.session_state.uploaded_dataframes.append(df)
                        st.info(f"Loaded Excel file: {file.name} ({len(df)} rows)")
                except Exception as e:
                    st.error(f"Error loading file {file.name}: {str(e)}")

        # Only proceed if there's text content or files were uploaded
        if prompt.strip() or files:
            # Get or create agent with all current dataframes
            agent = get_or_create_agent()

            if not agent:
                st.error(
                    "No data available for analysis. Please load stock data first."
                )
                st.stop()

            # Add user message to chat history
            message_content = prompt
            if files:
                file_names = [f.name for f in files]
                message_content += f"\nUploaded files: {', '.join(file_names)}"

            if message_content.strip():
                st.session_state.messages.append(
                    {"role": "user", "content": message_content}
                )

                # Display user message
                with st.chat_message("user"):
                    st.markdown(message_content)

            # Generate response if there's text content
            if prompt.strip():
                with st.chat_message("assistant"):
                    message_data = process_agent_response(agent, prompt)

                    # Display response
                    st.markdown(message_data["content"])

                    # Display chart if available
                    if "chart_data" in message_data:
                        chart_data = message_data["chart_data"]
                        if chart_data["type"] == "image":
                            st.image(chart_data["path"], use_container_width=True)

                    # Display generated code in expandable container
                    if "generated_code" in message_data:
                        with st.expander("View Generated Code", expanded=False):
                            st.code(message_data["generated_code"], language="python")

                    # Add to chat history
                    st.session_state.messages.append(message_data)

    # Chat controls
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Show Table", use_container_width=True):
            if "display_dataframes" in st.session_state:
                with st.expander("Financial Data"):
                    for name, df in st.session_state.display_dataframes.items():
                        st.subheader(name)

                        # Use helper function to transpose dataframes
                        df_display = transpose_financial_dataframe(df, name, period)
                        st.dataframe(df_display)
            else:
                st.warning(
                    "No data loaded yet. Please click 'Analyze Stock' first to load financial data."
                )

# Footer
st.caption(
    "Tip: Specify the table you want to analyze for more accurate results and customize charts by including any desired technical settings in your prompt."
)
st.markdown(
    "Built with [Streamlit](https://streamlit.io), [PandasAI](https://pandas-ai.com), and [Vnstock](https://github.com/thinh-vu/vnstock) by [Thinh Vu](https://github.com/thinh-vu)"
)
