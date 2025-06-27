# tests/evaluation/test_relevance.py
import pytest
from src.evaluation.metrics import ResponseRelevanceMetric

@pytest.mark.asyncio
async def test_relevance_metric_scores_on_topic_response():
    """A response about goals should score high for goal-setting context"""
    metric = ResponseRelevanceMetric()
    
    context = "User wants to set morning goals"
    response = "Let's explore what you want to accomplish today. What's most important?"
    
    score = await metric.evaluate(context, response)
    assert score > 0.7  # Expecting high relevance