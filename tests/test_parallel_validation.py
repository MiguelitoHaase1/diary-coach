"""Tests for parallel run validation framework."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, List
from dataclasses import dataclass, field

from src.orchestration.state import ConversationState
from src.orchestration.parallel_validation import ParallelValidationFramework, ComparisonResult
from src.orchestration.agent_interface import AgentInterface
from src.events.schemas import UserMessage, AgentResponse


@dataclass
class MockConversation:
    """Mock conversation for validation testing."""
    messages: List[UserMessage] = field(default_factory=list)
    expected_topics: List[str] = field(default_factory=list)
    context: str = "general"


class TestParallelValidation:
    """Test parallel validation framework functionality."""

    @pytest.fixture
    def mock_eventbus_agent(self):
        """Mock event-bus agent implementation."""
        agent = Mock(spec=AgentInterface)
        agent.process_message = AsyncMock()
        agent.get_conversation_state = AsyncMock()
        agent.get_metrics = AsyncMock()
        agent.get_agent_name = AsyncMock(return_value="EventBusAgent")
        return agent

    @pytest.fixture
    def mock_langgraph_agent(self):
        """Mock LangGraph agent implementation."""
        agent = Mock(spec=AgentInterface)
        agent.process_message = AsyncMock()
        agent.get_conversation_state = AsyncMock()
        agent.get_metrics = AsyncMock()
        agent.get_agent_name = AsyncMock(return_value="LangGraphAgent")
        return agent

    @pytest.fixture
    def validation_framework(self, mock_eventbus_agent, mock_langgraph_agent):
        """Create validation framework with mock agents."""
        return ParallelValidationFramework(
            eventbus_agent=mock_eventbus_agent,
            langgraph_agent=mock_langgraph_agent
        )

    @pytest.fixture
    def test_conversations(self):
        """Create test conversations for validation."""
        conversations = []
        
        # Morning conversation
        morning_conv = MockConversation(
            messages=[
                UserMessage(
                    content="Good morning! I want to tackle my biggest challenge today",
                    user_id="user123",
                    timestamp=datetime.now(),
                    conversation_id="test_conv_1"
                ),
                UserMessage(
                    content="I think organizing my project files is important",
                    user_id="user123",
                    timestamp=datetime.now(),
                    conversation_id="test_conv_1"
                )
            ],
            expected_topics=["morning", "challenge", "priorities"],
            context="morning"
        )
        conversations.append(morning_conv)
        
        # General conversation
        general_conv = MockConversation(
            messages=[
                UserMessage(
                    content="I'm feeling stuck on my project",
                    user_id="user123",
                    timestamp=datetime.now(),
                    conversation_id="test_conv_2"
                ),
                UserMessage(
                    content="Maybe I should just reorganize everything",
                    user_id="user123",
                    timestamp=datetime.now(),
                    conversation_id="test_conv_2"
                )
            ],
            expected_topics=["problem", "action", "specificity"],
            context="general"
        )
        conversations.append(general_conv)
        
        return conversations

    @pytest.fixture
    def mock_responses(self):
        """Mock agent responses for testing."""
        return {
            "eventbus": AgentResponse(
                content="What's the most important outcome you want to achieve with this project?",
                agent_name="EventBusAgent",
                response_to="msg123",
                conversation_id="test_conv_1"
            ),
            "langgraph": AgentResponse(
                content="What's the most important outcome you want to achieve with this project?",
                agent_name="LangGraphAgent",
                response_to="msg123",
                conversation_id="test_conv_1"
            )
        }

    @pytest.mark.asyncio
    async def test_parallel_system_parity(self, validation_framework, test_conversations, mock_responses):
        """Test parallel system parity validation."""
        # Mock identical responses from both agents
        validation_framework.eventbus_agent.process_message.return_value = mock_responses["eventbus"]
        validation_framework.langgraph_agent.process_message.return_value = mock_responses["langgraph"]
        
        # Mock metrics
        validation_framework.eventbus_agent.get_metrics.return_value = {
            "latency": 850,
            "cost": 0.025,
            "token_count": 150
        }
        validation_framework.langgraph_agent.get_metrics.return_value = {
            "latency": 720,
            "cost": 0.023,
            "token_count": 145
        }
        
        # Run parallel comparison
        results = await validation_framework.run_parallel_comparison(
            test_conversations=test_conversations,
            metrics=["response_quality", "latency", "cost"]
        )
        
        # Verify results
        assert isinstance(results, ComparisonResult)
        assert results.total_conversations == 2
        assert results.divergence_rate < 0.05  # 95% parity
        assert results.langgraph_latency < results.eventbus_latency
        assert results.langgraph_cost <= results.eventbus_cost
        
        # Verify both agents were called
        assert validation_framework.eventbus_agent.process_message.call_count == 4  # 2 conversations × 2 messages each
        assert validation_framework.langgraph_agent.process_message.call_count == 4

    @pytest.mark.asyncio
    async def test_response_comparison_identical(self, validation_framework, mock_responses):
        """Test response comparison with identical responses."""
        # Compare identical responses
        comparison = await validation_framework.compare_responses(
            mock_responses["eventbus"],
            mock_responses["langgraph"]
        )
        
        # Should be identical
        assert comparison.content_similarity >= 0.95
        assert comparison.semantic_similarity >= 0.95
        assert comparison.is_functionally_equivalent is True
        assert comparison.divergence_score < 0.05

    @pytest.mark.asyncio
    async def test_response_comparison_different(self, validation_framework):
        """Test response comparison with different responses."""
        # Create different responses
        eventbus_response = AgentResponse(
            content="What's the most important outcome you want to achieve?",
            agent_name="EventBusAgent",
            response_to="msg123",
            conversation_id="test_conv_1"
        )
        
        langgraph_response = AgentResponse(
            content="Tell me about your biggest challenge today.",
            agent_name="LangGraphAgent",
            response_to="msg123",
            conversation_id="test_conv_1"
        )
        
        # Compare different responses
        comparison = await validation_framework.compare_responses(
            eventbus_response,
            langgraph_response
        )
        
        # Should show differences
        assert comparison.content_similarity < 0.95
        assert comparison.semantic_similarity < 0.95
        assert comparison.is_functionally_equivalent is False
        assert comparison.divergence_score >= 0.05

    @pytest.mark.asyncio
    async def test_performance_metrics_collection(self, validation_framework, test_conversations):
        """Test collection of performance metrics."""
        # Mock responses with timing
        validation_framework.eventbus_agent.process_message.return_value = AgentResponse(
            content="Test response",
            agent_name="EventBusAgent",
            response_to="msg123",
            conversation_id="test_conv_1"
        )
        validation_framework.langgraph_agent.process_message.return_value = AgentResponse(
            content="Test response",
            agent_name="LangGraphAgent",
            response_to="msg123",
            conversation_id="test_conv_1"
        )
        
        # Mock different performance metrics
        validation_framework.eventbus_agent.get_metrics.return_value = {
            "latency": 1200,
            "cost": 0.035,
            "token_count": 180,
            "memory_usage": 45.2
        }
        validation_framework.langgraph_agent.get_metrics.return_value = {
            "latency": 950,
            "cost": 0.028,
            "token_count": 175,
            "memory_usage": 42.1
        }
        
        # Run performance comparison
        results = await validation_framework.run_parallel_comparison(
            test_conversations=test_conversations[:1],  # Just one conversation
            metrics=["latency", "cost", "memory_usage"]
        )
        
        # Verify performance metrics
        assert results.eventbus_latency == 1200
        assert results.langgraph_latency == 950
        assert results.eventbus_cost == 0.035
        assert results.langgraph_cost == 0.028
        assert results.performance_improvement > 0  # LangGraph should be faster

    @pytest.mark.asyncio
    async def test_divergence_analysis(self, validation_framework, test_conversations):
        """Test divergence analysis tools."""
        # Mock different responses to create divergence
        responses = [
            (
                AgentResponse(content="Response A", agent_name="EventBusAgent", response_to="msg1", conversation_id="conv1"),
                AgentResponse(content="Response A", agent_name="LangGraphAgent", response_to="msg1", conversation_id="conv1")
            ),
            (
                AgentResponse(content="Response B", agent_name="EventBusAgent", response_to="msg2", conversation_id="conv1"),
                AgentResponse(content="Different Response", agent_name="LangGraphAgent", response_to="msg2", conversation_id="conv1")
            )
        ]
        
        # Mock the agents to return these responses
        validation_framework.eventbus_agent.process_message.side_effect = [r[0] for r in responses]
        validation_framework.langgraph_agent.process_message.side_effect = [r[1] for r in responses]
        
        # Mock metrics
        validation_framework.eventbus_agent.get_metrics.return_value = {"latency": 800, "cost": 0.02}
        validation_framework.langgraph_agent.get_metrics.return_value = {"latency": 750, "cost": 0.019}
        
        # Run comparison
        results = await validation_framework.run_parallel_comparison(
            test_conversations=test_conversations[:1],
            metrics=["response_quality", "latency"]
        )
        
        # Should detect divergence
        assert results.divergence_rate >= 0.25  # 50% divergence (1 of 2 responses different)
        assert len(results.divergent_responses) > 0
        assert results.total_responses == 2

    @pytest.mark.asyncio
    async def test_ab_testing_capability(self, validation_framework, test_conversations):
        """Test A/B testing infrastructure."""
        # Mock consistent responses
        validation_framework.eventbus_agent.process_message.return_value = AgentResponse(
            content="What's your main goal?",
            agent_name="EventBusAgent",
            response_to="msg123",
            conversation_id="test_conv_1"
        )
        validation_framework.langgraph_agent.process_message.return_value = AgentResponse(
            content="What's your main goal?",
            agent_name="LangGraphAgent",
            response_to="msg123",
            conversation_id="test_conv_1"
        )
        
        # Mock metrics showing LangGraph advantage
        validation_framework.eventbus_agent.get_metrics.return_value = {
            "latency": 1000,
            "cost": 0.03,
            "satisfaction_score": 7.5
        }
        validation_framework.langgraph_agent.get_metrics.return_value = {
            "latency": 800,
            "cost": 0.025,
            "satisfaction_score": 8.2
        }
        
        # Run A/B test
        ab_results = await validation_framework.run_ab_test(
            test_conversations=test_conversations,
            confidence_level=0.95
        )
        
        # Verify A/B test results
        assert ab_results.is_statistically_significant is True
        assert ab_results.recommended_system == "LangGraph"
        assert ab_results.performance_delta > 0
        assert ab_results.confidence_level >= 0.95

    @pytest.mark.asyncio
    async def test_shadow_testing_mode(self, validation_framework, test_conversations):
        """Test shadow testing mode."""
        # Mock responses
        validation_framework.eventbus_agent.process_message.return_value = AgentResponse(
            content="Production response",
            agent_name="EventBusAgent",
            response_to="msg123",
            conversation_id="test_conv_1"
        )
        validation_framework.langgraph_agent.process_message.return_value = AgentResponse(
            content="Shadow response",
            agent_name="LangGraphAgent",
            response_to="msg123",
            conversation_id="test_conv_1"
        )
        
        # Mock metrics
        validation_framework.eventbus_agent.get_metrics.return_value = {"latency": 900, "cost": 0.028}
        validation_framework.langgraph_agent.get_metrics.return_value = {"latency": 750, "cost": 0.024}
        
        # Run shadow testing
        shadow_results = await validation_framework.run_shadow_test(
            test_conversations=test_conversations,
            production_system="EventBus",
            shadow_system="LangGraph"
        )
        
        # Verify shadow testing results
        assert shadow_results.production_system == "EventBus"
        assert shadow_results.shadow_system == "LangGraph"
        assert shadow_results.shadow_performance_better is True
        assert shadow_results.production_traffic_preserved is True
        assert len(shadow_results.shadow_insights) > 0

    @pytest.mark.asyncio
    async def test_error_handling_in_parallel_run(self, validation_framework, test_conversations):
        """Test error handling during parallel execution."""
        # Mock one agent failing
        validation_framework.eventbus_agent.process_message.return_value = AgentResponse(
            content="Success response",
            agent_name="EventBusAgent",
            response_to="msg123",
            conversation_id="test_conv_1"
        )
        validation_framework.langgraph_agent.process_message.side_effect = Exception("Agent failure")
        
        # Mock metrics for successful agent
        validation_framework.eventbus_agent.get_metrics.return_value = {"latency": 800, "cost": 0.025}
        validation_framework.langgraph_agent.get_metrics.return_value = {"latency": 999999, "cost": 0}  # Error state
        
        # Run comparison with error handling
        results = await validation_framework.run_parallel_comparison(
            test_conversations=test_conversations[:1],
            metrics=["response_quality", "latency"],
            handle_errors=True
        )
        
        # Should handle errors gracefully
        assert results.error_rate > 0
        assert results.failed_comparisons > 0
        assert results.successful_comparisons < results.total_responses

    @pytest.mark.asyncio
    async def test_rollback_capability(self, validation_framework):
        """Test rollback capability for safe migration."""
        # Mock migration state
        validation_framework.current_primary = "EventBus"
        validation_framework.migration_percentage = 50
        
        # Mock performance degradation
        degraded_metrics = {
            "error_rate": 0.15,  # 15% error rate
            "latency": 2000,     # 2s latency
            "satisfaction_score": 6.0  # Low satisfaction
        }
        
        # Test rollback decision
        should_rollback = await validation_framework.should_rollback(degraded_metrics)
        
        # Should recommend rollback
        assert should_rollback is True
        
        # Execute rollback
        rollback_result = await validation_framework.execute_rollback()
        
        # Verify rollback
        assert rollback_result.rollback_executed is True
        assert rollback_result.system_restored_to == "EventBus"
        assert rollback_result.migration_percentage == 0