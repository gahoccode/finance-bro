"""
CrewAI Service Module

This module provides a service wrapper for running CrewAI financial health analysis.
It integrates with the Finance Bro application's session state to access financial dataframes
and orchestrate the multi-agent financial health analysis crew.
"""

import streamlit as st
from src.financial_health_crew.crew import FinancialHealthCrew


@st.cache_data(show_spinner=False, ttl=300)  # Cache for 5 minutes
def run_financial_health_analysis():
    """
    Run the CrewAI Financial Health Analysis crew

    This function serves as the main entry point for running financial health analysis
    using the CrewAI multi-agent system. It accesses financial dataframes from session
    state and coordinates the analysis workflow.

    Returns:
        CrewOutput: The result from the CrewAI crew execution containing the financial health report
    """
    try:
        # Check if required session state data exists
        if "stock_symbol" not in st.session_state:
            raise ValueError(
                "No stock symbol selected. Please select a stock symbol first."
            )

        if "dataframes" not in st.session_state or not st.session_state.dataframes:
            raise ValueError(
                "No financial dataframes found. Please load financial data first."
            )

        # Get current stock symbol for context
        stock_symbol = st.session_state.stock_symbol

        # Initialize and run the CrewAI crew
        crew = FinancialHealthCrew()

        # Prepare inputs for the crew
        inputs = {
            "stock_symbol": stock_symbol,
            "analysis_context": f"Financial health analysis for {stock_symbol} using loaded dataframes",
        }

        # Execute the crew
        result = crew.crew().kickoff(inputs=inputs)

        return result

    except Exception as e:
        error_msg = f"CrewAI Financial Health Analysis failed: {str(e)}"
        st.error(error_msg)
        raise Exception(error_msg)


def get_available_dataframes():
    """
    Get information about available financial dataframes in session state

    Returns:
        dict: Dictionary containing dataframe names and their basic info
    """
    if "dataframes" not in st.session_state:
        return {}

    dataframes_info = {}
    for key, df in st.session_state.dataframes.items():
        dataframes_info[key] = {
            "shape": df.shape,
            "columns": list(df.columns),
            "data_types": df.dtypes.to_dict(),
        }

    return dataframes_info


def validate_session_state():
    """
    Validate that required session state data is available for CrewAI analysis

    Returns:
        tuple: (is_valid: bool, error_message: str)
    """
    if "stock_symbol" not in st.session_state:
        return False, "No stock symbol selected"

    if "dataframes" not in st.session_state:
        return False, "No dataframes found in session state"

    if not st.session_state.dataframes:
        return False, "Dataframes dictionary is empty"

    # Check if at least one dataframe has data
    has_data = any(not df.empty for df in st.session_state.dataframes.values())
    if not has_data:
        return False, "All dataframes are empty"

    return True, "Session state is valid for CrewAI analysis"
