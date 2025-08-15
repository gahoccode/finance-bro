import streamlit as st
import pandas as pd
from src.components.ui_components import inject_custom_success_styling
from src.services.crewai_service import run_financial_health_analysis

st.set_page_config(
    page_title="Financial Health Report - Finance Bro",
    page_icon="🏥",
    layout="wide"
)

inject_custom_success_styling()

st.title("🏥 Financial Health Report")
st.markdown("AI-powered comprehensive financial health analysis using CrewAI multi-agent system")

if 'stock_symbol' not in st.session_state:
    st.warning("⚠️ No stock symbol selected. Please go to the main page to select a stock symbol first.")
    if st.button("📈 Go to Main Page", type="primary"):
        st.switch_page("app.py")
    st.stop()

current_symbol = st.session_state.stock_symbol

with st.container():
    st.markdown("### 📊 Current Analysis Setup")
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"**Selected Stock:** {current_symbol}")
    
    with col2:
        dataframes_available = 'dataframes' in st.session_state and st.session_state.dataframes
        if dataframes_available:
            df_count = len(st.session_state.dataframes)
            st.success(f"**Financial Data:** {df_count} dataframes loaded")
        else:
            st.error("**Financial Data:** No dataframes found")

if not dataframes_available:
    st.warning("📋 **No financial data found in session state.**")
    st.markdown("""
    To generate a financial health report, you need financial dataframes in session state.
    
    **How to load financial data:**
    1. Go to **📊 Stock Analysis** page
    2. Ask the AI to load financial statements (e.g., "Load balance sheet and income statement")
    3. Return to this page to generate the health report
    """)
    
    if st.button("📊 Go to Stock Analysis", type="primary"):
        st.switch_page("pages/bro.py")
    st.stop()

st.markdown("### 🤖 AI Financial Health Analysis")

col1, col2 = st.columns(2)
with col1:
    if st.button("🏥 Generate Health Report", type="primary", use_container_width=True):
        st.session_state.generate_report = True

with col2:
    if st.button("🔄 Reset Analysis", type="secondary", use_container_width=True):
        if 'health_report' in st.session_state:
            del st.session_state.health_report
        if 'generate_report' in st.session_state:
            del st.session_state.generate_report
        st.rerun()

if st.session_state.get('generate_report', False):
    with st.spinner("🤖 CrewAI agents are analyzing financial health... This may take a few moments."):
        try:
            result = run_financial_health_analysis()
            st.session_state.health_report = result
            st.session_state.generate_report = False
            
        except Exception as e:
            st.error(f"❌ Error generating financial health report: {str(e)}")
            st.session_state.generate_report = False

if 'health_report' in st.session_state and st.session_state.health_report:
    st.markdown("### 📋 Financial Health Report")
    st.markdown("---")
    
    with st.container():
        report_content = str(st.session_state.health_report)
        
        if hasattr(st.session_state.health_report, 'raw'):
            report_content = st.session_state.health_report.raw
        
        st.markdown(report_content)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        st.download_button(
            label="📄 Download Report",
            data=report_content,
            file_name=f"financial_health_report_{current_symbol}.txt",
            mime="text/plain",
            use_container_width=True
        )

st.markdown("---")
st.markdown("### ℹ️ About CrewAI Financial Analysis")

with st.expander("🤖 How the AI Analysis Works", expanded=False):
    st.markdown("""
    This financial health report is generated using **CrewAI**, a multi-agent AI framework with specialized agents:
    
    **🔬 Financial Data Analyst Agent:**
    - Analyzes financial statements from session state dataframes
    - Calculates key financial ratios and metrics
    - Identifies trends and patterns in financial performance
    
    **⚠️ Risk Assessment Specialist Agent:**
    - Evaluates potential financial risks and stability factors
    - Assesses liquidity, debt levels, and sustainability
    - Provides risk level categorization and early warnings
    
    **📝 Report Writer Agent:**
    - Synthesizes analysis from other agents into a comprehensive report
    - Creates actionable insights and recommendations
    - Formats findings in a structured, stakeholder-ready format
    
    **Process:** The agents work sequentially, with each building on the previous agent's analysis to create a comprehensive financial health assessment.
    """)

st.markdown("**🚀 Finance Bro** - CrewAI-Powered Financial Health Analysis")