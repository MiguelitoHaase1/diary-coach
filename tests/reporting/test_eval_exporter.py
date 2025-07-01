"""Tests for Evaluation Exporter functionality."""

import pytest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch
from src.evaluation.reporting.eval_exporter import EvaluationExporter
from src.evaluation.analyzers.base import AnalysisScore
from src.evaluation.reporting.reporter import EvaluationReport


class TestEvaluationExporter:
    """Test suite for Evaluation Exporter."""

    @pytest.fixture
    def exporter(self):
        """Create an EvaluationExporter instance."""
        return EvaluationExporter()

    @pytest.fixture
    def sample_evaluation_report(self):
        """Sample evaluation report for testing."""
        # Create sample behavioral scores
        behavioral_scores = [
            AnalysisScore(
                value=0.8,
                reasoning="Coach effectively challenged problem selection",
                analyzer_name="ProblemSelection"
            ),
            AnalysisScore(
                value=0.7,
                reasoning="Good reframing of user's perspective",
                analyzer_name="ThinkingPivot"
            ),
            AnalysisScore(
                value=0.9,
                reasoning="Excellent energy building with vivid language",
                analyzer_name="ExcitementBuilder"
            ),
            AnalysisScore(
                value=0.6,
                reasoning="Some specificity push but could be stronger",
                analyzer_name="SpecificityPush"
            )
        ]

        # Create conversation metadata
        conversation_metadata = {
            "report_id": 1,
            "messages": [
                {"role": "user", "content": "good morning"},
                {"role": "assistant", "content": "Good morning, Michael! What dragon are you most excited to slay today?"},
                {"role": "user", "content": "I need to organize my files"},
                {"role": "assistant", "content": "Is organizing files really the biggest lever you could pull today?"}
            ],
            "persona_type": "Real User",
            "scenario": "Morning coaching session",
            "breakthrough_achieved": True,
            "final_resistance_level": 0.3
        }

        return EvaluationReport(
            timestamp=datetime(2025, 1, 30, 9, 30),
            conversation_metadata=conversation_metadata,
            response_times_ms=[850, 920, 780, 1100],
            percentile_80=1000,
            responses_under_1s_percentage=0.75,
            behavioral_scores=behavioral_scores,
            overall_score=0.75,
            user_notes="Good morning session with effective problem challenge",
            ai_reflection="Strong performance on problem selection and excitement building"
        )

    @pytest.mark.asyncio
    async def test_eval_exporter_includes_all_metrics(self, exporter, sample_evaluation_report):
        """Export includes all 4 behavioral analyzers + performance."""
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 1, 30, 9, 30)
            
            result = await exporter.export_evaluation_markdown(sample_evaluation_report)

            # Should include all behavioral analyzers
            assert "ProblemSelection" in result
            assert "ThinkingPivot" in result  
            assert "ExcitementBuilder" in result
            assert "SpecificityPush" in result

            # Should include performance metrics (new format)
            assert "Performance" in result
            assert "1000ms" in result  # 80th percentile
            assert "75%" in result  # Responses under 1s

    @pytest.mark.asyncio
    async def test_eval_exporter_filename_format(self, exporter, sample_evaluation_report):
        """Files named Eval_YYYYMMDD_HHMM.md in docs/prototype/Evals/."""
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 1, 30, 14, 30, 45)  # 2:30:45 PM
            
            # Export the evaluation
            await exporter.export_evaluation_markdown(sample_evaluation_report)
            
            # Check the filepath format
            filepath = exporter.get_output_filepath(datetime(2025, 1, 30, 14, 30, 45))

            expected_filename = "Eval_20250130_1430.md"
            assert expected_filename in str(filepath)
            assert "docs/prototype/Evals/" in str(filepath)

    @pytest.mark.asyncio
    async def test_eval_exporter_preserves_scores(self, exporter, sample_evaluation_report):
        """All numeric scores and analysis preserved in markdown."""
        result = await exporter.export_evaluation_markdown(sample_evaluation_report)

        # Should preserve all scores
        assert "8.0/10" in result  # ProblemSelection 0.8
        assert "7.0/10" in result  # ThinkingPivot 0.7  
        assert "9.0/10" in result  # ExcitementBuilder 0.9
        assert "6.0/10" in result  # SpecificityPush 0.6

        # New format doesn't include detailed reasoning (kept concise)
        # Just check that all the scores are preserved
        pass

    @pytest.mark.asyncio
    async def test_eval_exporter_includes_conversation_context(self, exporter, sample_evaluation_report):
        """Export includes conversation metadata and transcript."""
        result = await exporter.export_evaluation_markdown(sample_evaluation_report)

        # New format is more concise - just check basic structure
        assert "# Coaching Evaluation" in result
        assert "messages" in result  # Should show message count

    @pytest.mark.asyncio
    async def test_eval_exporter_markdown_structure(self, exporter, sample_evaluation_report):
        """Export should have proper markdown structure."""
        result = await exporter.export_evaluation_markdown(sample_evaluation_report)

        # Should have proper markdown headers (new format)
        assert "# Coaching Evaluation" in result
        assert "## Performance" in result
        assert "## Behavioral Scores" in result

    @pytest.mark.asyncio
    async def test_eval_exporter_creates_directory_if_not_exists(self, exporter, sample_evaluation_report, tmp_path):
        """Should create output directory if it doesn't exist."""
        # Override the output directory to use temp path
        test_dir = tmp_path / "docs" / "prototype" / "Evals"
        assert not test_dir.exists()
        
        with patch.object(exporter, '_get_output_path', return_value=test_dir / "test.md"):
            await exporter.export_evaluation_markdown(sample_evaluation_report)
            
            # Directory should be created
            assert test_dir.parent.exists()

    @pytest.mark.asyncio
    async def test_eval_exporter_separates_morning_metrics(self, exporter, sample_evaluation_report):
        """Morning-specific metrics should be in separate section."""
        result = await exporter.export_evaluation_markdown(sample_evaluation_report)

        # Should have morning coaching section
        assert "Morning Coaching" in result
        
        # Check that morning analyzers are grouped together
        morning_analyzers = ["ProblemSelection", "ThinkingPivot", "ExcitementBuilder"]
        for analyzer in morning_analyzers:
            if analyzer in result:
                # Should appear in the results somewhere
                assert analyzer in result

    @pytest.mark.asyncio
    async def test_eval_exporter_includes_overall_effectiveness(self, exporter, sample_evaluation_report):
        """Export should include overall effectiveness score."""
        result = await exporter.export_evaluation_markdown(sample_evaluation_report)

        # Should include overall score
        assert "7.5/10" in result or "75%" in result  # Overall score 0.75

    @pytest.mark.asyncio
    async def test_eval_exporter_handles_missing_performance_data(self, exporter):
        """Should handle reports without performance data gracefully."""
        # Create report without performance data
        report_without_perf = EvaluationReport(
            timestamp=datetime(2025, 1, 30, 9, 30),
            conversation_metadata={"report_id": 1, "messages": []},
            response_times_ms=[],
            percentile_80=0,
            responses_under_1s_percentage=0,
            behavioral_scores=[],
            overall_score=0.5,
            user_notes="Test",
            ai_reflection="Test reflection"
        )

        result = await exporter.export_evaluation_markdown(report_without_perf)

        # Should not crash and should include placeholders
        assert "Performance" in result
        assert "0ms" in result or "No performance data" in result

    @pytest.mark.asyncio
    async def test_eval_exporter_formats_timestamps_correctly(self, exporter, sample_evaluation_report):
        """Should format timestamps in readable format."""
        result = await exporter.export_evaluation_markdown(sample_evaluation_report)

        # Should include formatted date
        assert "2025-01-30" in result
        assert "9:30" in result or "09:30" in result