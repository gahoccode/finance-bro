"""
CrewAI Streaming Service Module

Provides real-time progress tracking and typewriter-style streaming for CrewAI
financial health analysis. Uses threading to run the crew in the background while
updating Streamlit UI with agent progress via queue-based communication.
"""

import queue
import threading
import time
from typing import Generator

import streamlit as st

# Timeout for crew execution in seconds
CREW_EXECUTION_TIMEOUT = 300  # 5 minutes

# Agent display names mapped to task names from tasks.yaml
TASK_AGENT_DISPLAY = {
    "analyze_financial_data": "Financial Data Analyst",
    "assess_financial_risks": "Risk Assessment Specialist",
    "generate_health_report": "Report Writer",
}


def stream_report_text(report_content: str) -> Generator[str, None, None]:
    """
    Generator that yields words one-by-one for typewriter streaming effect.

    Uses adaptive speed based on report length:
    - Normal reports (<5000 words): 20ms per word
    - Long reports (>=5000 words): 5ms per word

    Args:
        report_content: The full report text to stream

    Yields:
        Individual words with trailing spaces for st.write_stream()
    """
    if not report_content:
        return

    words = report_content.split(" ")
    delay = 0.005 if len(words) >= 5000 else 0.02

    for i, word in enumerate(words):
        if i < len(words) - 1:
            yield word + " "
        else:
            yield word
        time.sleep(delay)


class CrewAIStreamingOrchestrator:
    """
    Orchestrates CrewAI crew execution with real-time progress tracking.

    Runs the crew in a background thread and communicates task completion
    events to the main Streamlit thread via a queue for live UI updates.
    """

    def __init__(self) -> None:
        self.message_queue: queue.Queue = queue.Queue()
        self.task_outputs: dict = {}
        self.is_complete: bool = False
        self.error: str | None = None

    def task_callback(self, task_output) -> None:
        """
        Callback invoked by CrewAI when each task completes.

        Captures task output info and puts it on the queue for the main thread.

        Args:
            task_output: CrewAI TaskOutput with description, name, raw, agent, summary
        """
        task_name = getattr(task_output, "name", None) or getattr(
            task_output, "description", "Unknown Task"
        )
        agent_name = getattr(task_output, "agent", "Unknown Agent")

        task_info = {
            "type": "task_complete",
            "task_name": str(task_name),
            "agent": str(agent_name),
            "summary": getattr(task_output, "summary", ""),
            "raw": getattr(task_output, "raw", ""),
        }

        self.task_outputs[str(task_name)] = task_info
        self.message_queue.put(task_info)

    def run_crew_in_thread(
        self, stock_symbol: str, inputs: dict, dataframes: dict
    ) -> None:
        """
        Runs the CrewAI crew in a background thread.

        Sets shared dataframes for tool access (st.session_state is thread-local
        and inaccessible from background threads), then sets task_callback on
        the crew instance before kickoff. Signals completion/error via the queue.

        Args:
            stock_symbol: The stock symbol being analyzed
            inputs: Dictionary of inputs for the crew kickoff
            dataframes: Financial dataframes captured from the main thread
        """
        try:
            from src.financial_health_crew.crew import FinancialHealthCrew
            from src.financial_health_crew.tools.financial_analysis_tool import (
                set_shared_dataframes,
            )

            # Bridge dataframes from main thread to background thread
            set_shared_dataframes(dataframes)

            crew_instance = FinancialHealthCrew()
            crew_obj = crew_instance.crew()
            crew_obj.task_callback = self.task_callback
            result = crew_obj.kickoff(inputs=inputs)

            self.message_queue.put({"type": "complete", "result": result})

        except Exception as e:
            self.message_queue.put({"type": "error", "error": str(e)})
        finally:
            # Clean up shared state
            try:
                from src.financial_health_crew.tools.financial_analysis_tool import (
                    set_shared_dataframes,
                )

                set_shared_dataframes(None)
            except Exception:
                pass

    def execute_with_progress(self, stock_symbol: str) -> dict:
        """
        Main entry point — runs crew with live progress tracking in Streamlit.

        Starts the crew in a background thread, then polls the message queue
        in the main thread to update st.status containers as each agent completes.

        Args:
            stock_symbol: The stock symbol to analyze

        Returns:
            dict with keys: success (bool), result (CrewOutput or None),
            error (str or None), task_outputs (dict of completed task info)
        """
        inputs = {
            "stock_symbol": stock_symbol,
            "analysis_context": (
                f"Financial health analysis for {stock_symbol} using loaded dataframes"
            ),
        }

        # Capture dataframes from main thread before spawning background thread.
        # st.session_state is thread-local and won't be accessible in the child thread.
        dataframes = st.session_state.get("dataframes", {})

        # Start crew in background thread
        thread = threading.Thread(
            target=self.run_crew_in_thread,
            args=(stock_symbol, inputs, dataframes),
            daemon=True,
        )
        thread.start()

        # Track progress in Streamlit UI
        completed_tasks = 0
        total_tasks = 3  # Data Analyst, Risk Specialist, Report Writer
        result = None

        agent_names = list(TASK_AGENT_DISPLAY.values())

        with st.status("Analyzing financial data...", expanded=True) as status:
            # Show initial state
            for name in agent_names:
                st.write(f"⏳ {name} — Waiting...")

            start_time = time.time()

            while True:
                # Check timeout
                elapsed = time.time() - start_time
                if elapsed > CREW_EXECUTION_TIMEOUT:
                    self.error = f"Analysis timed out after {CREW_EXECUTION_TIMEOUT // 60} minutes"
                    status.update(label="Analysis timed out", state="error")
                    return {
                        "success": False,
                        "result": None,
                        "error": self.error,
                        "task_outputs": self.task_outputs,
                    }

                # Poll queue for messages
                try:
                    message = self.message_queue.get(timeout=0.5)
                except queue.Empty:
                    continue

                if message["type"] == "task_complete":
                    completed_tasks += 1
                    agent_display = message.get("agent", "Agent")

                    # Update status label
                    if completed_tasks < total_tasks:
                        next_idx = min(completed_tasks, len(agent_names) - 1)
                        status.update(
                            label=f"{agent_names[next_idx]} working... ({completed_tasks}/{total_tasks} tasks done)"
                        )
                    st.write(f"✅ {agent_display} — Complete")

                elif message["type"] == "complete":
                    result = message["result"]
                    self.is_complete = True
                    status.update(
                        label="Analysis complete!", state="complete", expanded=False
                    )
                    break

                elif message["type"] == "error":
                    self.error = message["error"]
                    status.update(label="Analysis failed", state="error")
                    return {
                        "success": False,
                        "result": None,
                        "error": self.error,
                        "task_outputs": self.task_outputs,
                    }

        return {
            "success": True,
            "result": result,
            "error": None,
            "task_outputs": self.task_outputs,
        }
