"""Tests for evaluation reporter."""

import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime
import tempfile
import os

from src.evaluation.reporting.reporter import EvaluationReporter
from src.evaluation.analyzers.specificity import SpecificityPushAnalyzer
from src.evaluation.analyzers.action import ActionOrientationAnalyzer
from src.evaluation.generator import GeneratedConversation


class TestEvaluationReporter:
    """Test evaluation reporter functionality."""
    
    @pytest.fixture
    def mock_analyzers(self):
        """Create mock analyzers for testing."""
        specificity = Mock(spec=SpecificityPushAnalyzer)
        specificity.name = "SpecificityPush"
        specificity.analyze = AsyncMock()
        
        action = Mock(spec=ActionOrientationAnalyzer) 
        action.name = "ActionOrientation"
        action.analyze = AsyncMock()
        
        return [specificity, action]
    
    @pytest.fixture
    def sample_conversation(self):
        """Create sample conversation for testing."""
        return GeneratedConversation(
            messages=[
                {"role": "user", "content": "I need to be more productive", "timestamp": datetime.now()},
                {"role": "assistant", "content": "Good morning Michael! What's the one challenge you're ready to tackle today?", "timestamp": datetime.now()},
                {"role": "user", "content": "I want to finish my product roadmap", "timestamp": datetime.now()},
                {"role": "assistant", "content": "Productive is a big word. What's one specific thing you'd do differently if you were 'productive' today?", "timestamp": datetime.now()}
            ],
            persona_type="FrameworkRigid",
            scenario="morning_goal_setting",
            timestamp=datetime.now(),
            final_resistance_level=0.6,
            breakthrough_achieved=False
        )
    
    @pytest.fixture
    def reporter(self):
        """Create evaluation reporter for testing."""
        return EvaluationReporter()
    
    @pytest.mark.asyncio
    async def test_evaluation_with_performance(self, reporter, mock_analyzers, sample_conversation):
        """Test evaluation reporter generates complete report with performance metrics."""
        # Mock analyzer responses
        from src.evaluation.analyzers.base import AnalysisScore
        mock_analyzers[0].analyze.return_value = AnalysisScore(
            value=0.8, reasoning="Good specificity push", analyzer_name="SpecificityPush"
        )
        mock_analyzers[1].analyze.return_value = AnalysisScore(
            value=0.6, reasoning="Moderate action orientation", analyzer_name="ActionOrientation"
        )
        
        # Mock performance data
        performance_data = {
            "response_times_ms": [850, 920, 750, 1100],
            "percentile_80": 980,
            "responses_under_1s_percentage": 0.75
        }
        
        # Generate report
        report = await reporter.generate_report(
            conversation=sample_conversation,
            user_notes="Coach was good at pushing for specificity",
            analyzers=mock_analyzers,
            performance_data=performance_data
        )
        
        # Verify report structure
        assert report.response_times_ms is not None
        assert report.percentile_80 == 980
        assert report.responses_under_1s_percentage == 0.75
        assert report.overall_score >= 0 and report.overall_score <= 1
        assert len(report.behavioral_scores) == 2
        assert report.user_notes == "Coach was good at pushing for specificity"
        assert report.conversation_metadata["persona_type"] == "FrameworkRigid"
        assert report.conversation_metadata["scenario"] == "morning_goal_setting"
    
    @pytest.mark.asyncio
    async def test_report_markdown_generation(self, reporter, mock_analyzers, sample_conversation):
        """Test markdown report generation."""
        # Mock analyzer responses
        from src.evaluation.analyzers.base import AnalysisScore
        mock_analyzers[0].analyze.return_value = AnalysisScore(
            value=0.8, reasoning="Strong specificity push with concrete questions", analyzer_name="SpecificityPush"
        )
        mock_analyzers[1].analyze.return_value = AnalysisScore(
            value=0.6, reasoning="Moderate action orientation, could be stronger", analyzer_name="ActionOrientation"
        )
        
        # Generate report
        report = await reporter.generate_report(
            conversation=sample_conversation,
            user_notes="Good coaching session overall",
            analyzers=mock_analyzers,
            performance_data={"percentile_80": 850, "responses_under_1s_percentage": 0.9}
        )
        
        # Generate markdown
        markdown = report.to_markdown()
        
        # Verify markdown content
        assert "# Coaching Evaluation Report" in markdown
        assert "## Summary" in markdown
        assert "## Performance Metrics" in markdown
        assert "## Behavioral Analysis" in markdown
        assert "### SpecificityPush:" in markdown
        assert "### ActionOrientation:" in markdown
        assert "## User Notes" in markdown
        assert "Good coaching session overall" in markdown
        assert "850ms" in markdown
        assert "90%" in markdown
    
    @pytest.mark.asyncio
    async def test_save_markdown_report(self, reporter, mock_analyzers, sample_conversation):
        """Test saving report as markdown file."""
        # Mock analyzer responses
        from src.evaluation.analyzers.base import AnalysisScore
        mock_analyzers[0].analyze.return_value = AnalysisScore(
            value=0.7, reasoning="Good specificity", analyzer_name="SpecificityPush"
        )
        
        # Generate report
        report = await reporter.generate_report(
            conversation=sample_conversation,
            user_notes="Test notes",
            analyzers=mock_analyzers[:1],  # Just one analyzer
            performance_data={"percentile_80": 900, "responses_under_1s_percentage": 0.8}
        )
        
        # Save to temporary file
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "test_eval.md")
            report.save_as_markdown(file_path)
            
            # Verify file was created and contains expected content
            assert os.path.exists(file_path)
            
            with open(file_path, 'r') as f:
                content = f.read()
                assert "# Coaching Evaluation Report" in content
                assert "Test notes" in content
                assert "SpecificityPush" in content
    
    @pytest.mark.asyncio
    async def test_overall_score_calculation(self, reporter, mock_analyzers, sample_conversation):
        """Test overall effectiveness score calculation."""
        # Mock different analyzer scores
        from src.evaluation.analyzers.base import AnalysisScore
        mock_analyzers[0].analyze.return_value = AnalysisScore(
            value=0.9, reasoning="Excellent specificity", analyzer_name="SpecificityPush"
        )
        mock_analyzers[1].analyze.return_value = AnalysisScore(
            value=0.4, reasoning="Weak action orientation", analyzer_name="ActionOrientation"
        )
        
        # Generate report
        report = await reporter.generate_report(
            conversation=sample_conversation,
            user_notes="Mixed performance",
            analyzers=mock_analyzers,
            performance_data={"percentile_80": 1200, "responses_under_1s_percentage": 0.5}
        )
        
        # Overall score should be average of behavioral scores
        expected_behavioral_avg = (0.9 + 0.4) / 2
        assert abs(report.overall_score - expected_behavioral_avg) < 0.1
        
        # Should be penalized for slow performance 
        assert report.overall_score <= expected_behavioral_avg