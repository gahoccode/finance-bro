"""Tests for CrewAI streaming service module."""

from unittest.mock import MagicMock

from src.services.crewai_streaming import (
    CrewAIStreamingOrchestrator,
    stream_report_text,
)


class TestStreamReportText:
    """Tests for stream_report_text generator."""

    def test_yields_words(self) -> None:
        """Verify generator yields individual words with spaces."""
        text = "Hello world test"
        chunks = list(stream_report_text(text))
        assert chunks == ["Hello ", "world ", "test"]

    def test_reconstructs_original(self) -> None:
        """Concatenated output matches the original input text."""
        text = "This is a comprehensive financial health report for VNM"
        result = "".join(stream_report_text(text))
        assert result == text

    def test_empty_string(self) -> None:
        """Handles empty input gracefully with no output."""
        chunks = list(stream_report_text(""))
        assert chunks == []

    def test_single_word(self) -> None:
        """Handles single-word input without trailing space."""
        chunks = list(stream_report_text("Hello"))
        assert chunks == ["Hello"]

    def test_multiline_text(self) -> None:
        """Handles text with newlines correctly."""
        text = "Line one\nLine two"
        result = "".join(stream_report_text(text))
        assert result == text


class TestCrewAIStreamingOrchestrator:
    """Tests for CrewAIStreamingOrchestrator."""

    def test_initialization(self) -> None:
        """Verify default state on initialization."""
        orchestrator = CrewAIStreamingOrchestrator()
        assert orchestrator.task_outputs == {}
        assert orchestrator.is_complete is False
        assert orchestrator.error is None
        assert orchestrator.message_queue.empty()

    def test_task_callback_captures_output(self) -> None:
        """Mock TaskOutput is captured and placed on the queue."""
        orchestrator = CrewAIStreamingOrchestrator()

        mock_task_output = MagicMock()
        mock_task_output.name = "analyze_financial_data"
        mock_task_output.agent = "Financial Data Analyst"
        mock_task_output.summary = "Analysis complete"
        mock_task_output.raw = "Detailed analysis results..."

        orchestrator.task_callback(mock_task_output)

        assert not orchestrator.message_queue.empty()
        message = orchestrator.message_queue.get()
        assert message["type"] == "task_complete"
        assert message["task_name"] == "analyze_financial_data"
        assert message["agent"] == "Financial Data Analyst"
        assert message["raw"] == "Detailed analysis results..."

    def test_task_callback_stores_in_task_outputs(self) -> None:
        """Task output is stored in the task_outputs dict."""
        orchestrator = CrewAIStreamingOrchestrator()

        mock_task_output = MagicMock()
        mock_task_output.name = "assess_financial_risks"
        mock_task_output.agent = "Risk Assessment Specialist"
        mock_task_output.summary = "Risk assessed"
        mock_task_output.raw = "Risk details..."

        orchestrator.task_callback(mock_task_output)

        assert "assess_financial_risks" in orchestrator.task_outputs
        assert (
            orchestrator.task_outputs["assess_financial_risks"]["agent"]
            == "Risk Assessment Specialist"
        )

    def test_task_callback_fallback_to_description(self) -> None:
        """Falls back to description when name is not available."""
        orchestrator = CrewAIStreamingOrchestrator()

        mock_task_output = MagicMock(spec=[])
        mock_task_output.description = "Analyze financial data task"
        mock_task_output.agent = "Analyst"
        mock_task_output.summary = ""
        mock_task_output.raw = ""

        orchestrator.task_callback(mock_task_output)

        message = orchestrator.message_queue.get()
        assert message["task_name"] == "Analyze financial data task"

    def test_multiple_callbacks_queue_order(self) -> None:
        """Multiple callbacks are queued in order."""
        orchestrator = CrewAIStreamingOrchestrator()

        for i, name in enumerate(["task_1", "task_2", "task_3"]):
            mock = MagicMock()
            mock.name = name
            mock.agent = f"Agent {i}"
            mock.summary = ""
            mock.raw = ""
            orchestrator.task_callback(mock)

        messages = []
        while not orchestrator.message_queue.empty():
            messages.append(orchestrator.message_queue.get())

        assert [m["task_name"] for m in messages] == ["task_1", "task_2", "task_3"]
        assert len(orchestrator.task_outputs) == 3
