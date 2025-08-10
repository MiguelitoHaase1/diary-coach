"""
Tests for cost optimization and tracking
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
from typing import Dict, List, Any

from src.performance.cost_optimizer import (
    CostTracker,
    ModelSelector,
    TokenOptimizer,
    CostDashboard,
    BudgetManager,
    CostConfig,
    ConversationCost,
    ModelChoice
)


class TestCostTracking:
    """Test cost tracking functionality"""
    
    @pytest.fixture
    def cost_config(self):
        """Create test configuration"""
        return CostConfig(
            opus_cost_per_1k_input=0.015,  # $15 per million
            opus_cost_per_1k_output=0.075,  # $75 per million
            sonnet_cost_per_1k_input=0.003,  # $3 per million
            sonnet_cost_per_1k_output=0.015,  # $15 per million
            haiku_cost_per_1k_input=0.0003,  # $0.30 per million
            haiku_cost_per_1k_output=0.0015,  # $1.50 per million
            daily_budget_usd=10.0,
            per_user_budget_usd=1.0,
            quality_threshold=0.8
        )
    
    def test_token_cost_calculation(self, cost_config):
        """Test accurate cost calculation for tokens"""
        tracker = CostTracker(cost_config)
        
        # Test Opus pricing
        opus_cost = tracker.calculate_cost(
            model="claude-3-opus",
            input_tokens=1000,
            output_tokens=500
        )
        expected = (1000 * 0.015 / 1000) + (500 * 0.075 / 1000)
        assert opus_cost == pytest.approx(expected, rel=0.01)
        
        # Test Sonnet pricing
        sonnet_cost = tracker.calculate_cost(
            model="claude-3-sonnet",
            input_tokens=1000,
            output_tokens=500
        )
        expected = (1000 * 0.003 / 1000) + (500 * 0.015 / 1000)
        assert sonnet_cost == pytest.approx(expected, rel=0.01)
    
    def test_conversation_cost_tracking(self, cost_config):
        """Test tracking costs across a conversation"""
        tracker = CostTracker(cost_config)
        
        # Start conversation
        conversation_id = "test-conv-123"
        tracker.start_conversation(conversation_id, user_id="user-1")
        
        # Add multiple LLM calls
        tracker.add_call(
            conversation_id=conversation_id,
            model="claude-3-opus",
            input_tokens=500,
            output_tokens=200,
            agent="coach"
        )
        
        tracker.add_call(
            conversation_id=conversation_id,
            model="claude-3-sonnet",
            input_tokens=300,
            output_tokens=150,
            agent="reporter"
        )
        
        # Get conversation cost
        cost = tracker.get_conversation_cost(conversation_id)
        assert cost.total_cost > 0
        assert cost.call_count == 2
        assert cost.total_input_tokens == 800
        assert cost.total_output_tokens == 350
        assert "coach" in cost.agent_costs
        assert "reporter" in cost.agent_costs
    
    def test_cost_aggregation(self, cost_config):
        """Test cost aggregation by user and time period"""
        tracker = CostTracker(cost_config)
        
        # Add costs for multiple users
        for i in range(3):
            conv_id = f"conv-{i}"
            tracker.start_conversation(conv_id, user_id="user-1")
            tracker.add_call(
                conversation_id=conv_id,
                model="claude-3-opus",
                input_tokens=1000,
                output_tokens=500,
                agent="coach"
            )
        
        # Different user
        tracker.start_conversation("conv-other", user_id="user-2")
        tracker.add_call(
            conversation_id="conv-other",
            model="claude-3-sonnet",
            input_tokens=500,
            output_tokens=250,
            agent="coach"
        )
        
        # Get user costs
        user1_cost = tracker.get_user_cost("user-1", period_hours=24)
        user2_cost = tracker.get_user_cost("user-2", period_hours=24)
        
        assert user1_cost.conversation_count == 3
        assert user2_cost.conversation_count == 1
        assert user1_cost.total_cost > user2_cost.total_cost
    
    def test_daily_cost_tracking(self, cost_config):
        """Test daily cost aggregation"""
        tracker = CostTracker(cost_config)
        
        # Add costs throughout the day
        for hour in range(0, 24, 4):
            conv_id = f"conv-{hour}"
            tracker.start_conversation(conv_id, user_id="user-1")
            tracker.add_call(
                conversation_id=conv_id,
                model="claude-3-opus",
                input_tokens=500,
                output_tokens=250,
                agent="coach"
            )
        
        # Get daily costs
        daily_cost = tracker.get_daily_cost()
        assert daily_cost.conversation_count == 6
        assert daily_cost.total_cost > 0
        assert len(daily_cost.hourly_costs) > 0


class TestModelSelection:
    """Test dynamic model selection"""
    
    @pytest.fixture
    def model_selector(self):
        """Create model selector"""
        config = CostConfig(quality_threshold=0.8)
        return ModelSelector(config)
    
    def test_simple_query_model_selection(self, model_selector):
        """Test that simple queries use cheaper models"""
        
        # Simple queries should use Haiku or Sonnet
        simple_queries = [
            "What time is it?",
            "Thank you",
            "Good morning",
            "Ok"
        ]
        
        for query in simple_queries:
            choice = model_selector.select_model(
                query=query,
                context={"complexity": "simple"}
            )
            assert choice.model in ["claude-3-haiku", "claude-3-sonnet"]
            assert choice.reasoning == "Simple query - using efficient model"
    
    def test_complex_query_model_selection(self, model_selector):
        """Test that complex queries use Opus"""
        
        complex_queries = [
            "I'm struggling with deep emotional issues and need help understanding my patterns",
            "Can you help me analyze my behavior patterns from the past week?",
            "I need a comprehensive reflection on my progress"
        ]
        
        for query in complex_queries:
            choice = model_selector.select_model(
                query=query,
                context={"complexity": "complex"}
            )
            assert choice.model == "claude-3-opus"
            assert "complex" in choice.reasoning.lower()
    
    def test_context_based_selection(self, model_selector):
        """Test model selection based on conversation context"""
        
        # Morning protocol should use Sonnet
        choice = model_selector.select_model(
            query="Good morning",
            context={"time_of_day": "morning", "protocol": "morning_routine"}
        )
        assert choice.model == "claude-3-sonnet"
        assert "morning protocol" in choice.reasoning.lower()
        
        # Deep reflection requires Opus
        choice = model_selector.select_model(
            query="Tell me more",
            context={"previous_model": "opus", "mode": "deep_reflection"}
        )
        assert choice.model == "claude-3-opus"
        assert "context" in choice.reasoning.lower()
    
    def test_budget_aware_selection(self, model_selector):
        """Test that model selection considers budget"""
        
        # When near budget limit, prefer cheaper models
        choice = model_selector.select_model(
            query="How can I improve?",
            context={"budget_remaining": 0.10, "daily_budget": 10.0}
        )
        assert choice.model != "claude-3-opus"
        assert "budget" in choice.reasoning.lower()
    
    def test_quality_threshold(self, model_selector):
        """Test quality threshold enforcement"""
        
        # Critical queries should maintain quality
        critical_queries = [
            "I'm having suicidal thoughts",
            "I'm in crisis",
            "Emergency help needed"
        ]
        
        for query in critical_queries:
            choice = model_selector.select_model(
                query=query,
                context={"budget_remaining": 0.01}  # Even with low budget
            )
            assert choice.model == "claude-3-opus"
            assert choice.override_budget
            assert "critical" in choice.reasoning.lower()


class TestTokenOptimization:
    """Test token usage optimization"""
    
    @pytest.fixture
    def token_optimizer(self):
        """Create token optimizer"""
        return TokenOptimizer()
    
    def test_prompt_compression(self, token_optimizer):
        """Test prompt compression while maintaining meaning"""
        
        # Long verbose prompt
        verbose_prompt = """
        You are a helpful AI assistant. Your role is to help users with their questions.
        Please provide helpful, accurate, and detailed responses to their queries.
        Make sure to be respectful and professional at all times.
        Consider the context of the conversation when providing answers.
        """
        
        compressed = token_optimizer.compress_prompt(verbose_prompt)
        
        # Should be shorter
        assert len(compressed) < len(verbose_prompt)
        # But maintain key information
        assert "helpful" in compressed.lower()
        assert "users" in compressed.lower()
    
    def test_context_pruning(self, token_optimizer):
        """Test pruning of conversation context"""
        
        # Long conversation history
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": "How are you?"},
            {"role": "assistant", "content": "I'm doing well, thank you!"},
            {"role": "user", "content": "What's the weather?"},
            {"role": "assistant", "content": "I don't have weather data."},
            {"role": "user", "content": "Can you help me with something important?"}
        ]
        
        # Prune to stay under token limit
        pruned = token_optimizer.prune_context(
            messages=messages,
            max_tokens=100,
            preserve_recent=2
        )
        
        # Should keep recent messages
        assert len(pruned) < len(messages)
        assert pruned[-1] == messages[-1]  # Keep last message
        assert pruned[-2] == messages[-2]  # Keep second to last
    
    def test_response_length_optimization(self, token_optimizer):
        """Test optimization of response length guidance"""
        
        # Based on query complexity
        short_query = "What time is it?"
        guidance = token_optimizer.get_response_guidance(short_query)
        assert guidance.max_tokens <= 100
        assert "concise" in guidance.style.lower()
        
        complex_query = "Help me understand my emotional patterns"
        guidance = token_optimizer.get_response_guidance(complex_query)
        assert guidance.max_tokens >= 500
        assert "detailed" in guidance.style.lower()
    
    def test_template_optimization(self, token_optimizer):
        """Test optimization of prompt templates"""
        
        # Template with redundancy
        template = """
        As a coach, you should:
        - Be supportive and helpful
        - Provide support to users
        - Help users with their problems
        - Be understanding and supportive
        """
        
        optimized = token_optimizer.optimize_template(template)
        
        # Remove redundancy
        assert optimized.count("supportive") < template.count("supportive")
        assert optimized.count("help") < template.count("help")
        assert len(optimized) < len(template)


class TestCostDashboard:
    """Test cost dashboard and reporting"""
    
    @pytest.fixture
    def dashboard(self):
        """Create cost dashboard"""
        tracker = CostTracker(CostConfig())
        return CostDashboard(tracker)
    
    def test_dashboard_metrics(self, dashboard):
        """Test dashboard metric generation"""
        
        # Add some test data
        tracker = dashboard.tracker
        for i in range(5):
            conv_id = f"conv-{i}"
            tracker.start_conversation(conv_id, user_id="user-1")
            tracker.add_call(
                conversation_id=conv_id,
                model="claude-3-opus" if i % 2 == 0 else "claude-3-sonnet",
                input_tokens=1000,
                output_tokens=500,
                agent="coach"
            )
        
        # Generate dashboard
        metrics = dashboard.get_metrics(period_hours=24)
        
        assert metrics["total_cost"] > 0
        assert metrics["conversation_count"] == 5
        assert metrics["average_cost_per_conversation"] > 0
        assert "model_distribution" in metrics
        assert "agent_distribution" in metrics
        assert len(metrics["top_users"]) > 0
    
    def test_cost_trends(self, dashboard):
        """Test cost trend analysis"""
        
        # Add data over time
        tracker = dashboard.tracker
        base_time = datetime.now() - timedelta(days=7)
        
        for day in range(7):
            timestamp = base_time + timedelta(days=day)
            conv_id = f"conv-day-{day}"
            tracker.start_conversation(conv_id, user_id="user-1")
            
            # Increasing usage over time
            tokens = 500 * (day + 1)
            tracker.add_call(
                conversation_id=conv_id,
                model="claude-3-opus",
                input_tokens=tokens,
                output_tokens=tokens // 2,
                agent="coach"
            )
        
        # Get trends
        trends = dashboard.get_cost_trends(days=7)
        
        assert len(trends["daily_costs"]) == 7
        assert trends["trend"] == "increasing"
        assert trends["projection_next_day"] > trends["daily_costs"][-1]
    
    def test_cost_breakdown_by_agent(self, dashboard):
        """Test cost breakdown by agent type"""
        
        tracker = dashboard.tracker
        conv_id = "test-conv"
        tracker.start_conversation(conv_id, user_id="user-1")
        
        # Different agents with different costs
        agents = [
            ("coach", "claude-3-opus", 1000, 500),
            ("reporter", "claude-3-opus", 2000, 1000),
            ("personal_content", "claude-3-sonnet", 500, 250),
            ("web_search", "claude-3-haiku", 300, 150)
        ]
        
        for agent, model, input_tokens, output_tokens in agents:
            tracker.add_call(
                conversation_id=conv_id,
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                agent=agent
            )
        
        # Get breakdown
        breakdown = dashboard.get_agent_breakdown(period_hours=24)
        
        assert len(breakdown) == 4
        assert breakdown["reporter"]["total_cost"] > breakdown["web_search"]["total_cost"]
        assert all(agent in breakdown for agent, _, _, _ in agents)


class TestBudgetManagement:
    """Test budget alerts and limits"""
    
    @pytest.fixture
    def budget_manager(self):
        """Create budget manager"""
        config = CostConfig(
            daily_budget_usd=10.0,
            per_user_budget_usd=1.0
        )
        tracker = CostTracker(config)
        return BudgetManager(config, tracker)
    
    def test_budget_check(self, budget_manager):
        """Test budget checking"""
        
        # Check daily budget
        assert budget_manager.is_within_daily_budget()
        
        # Add costs
        tracker = budget_manager.tracker
        tracker.start_conversation("conv-1", user_id="user-1")
        
        # Add cost near daily limit
        for _ in range(100):
            tracker.add_call(
                conversation_id="conv-1",
                model="claude-3-opus",
                input_tokens=10000,
                output_tokens=5000,
                agent="coach"
            )
        
        # Should exceed budget
        assert not budget_manager.is_within_daily_budget()
    
    def test_user_budget_enforcement(self, budget_manager):
        """Test per-user budget limits"""
        
        user_id = "user-1"
        
        # Initially within budget
        assert budget_manager.is_user_within_budget(user_id)
        
        # Add costs for user
        tracker = budget_manager.tracker
        tracker.start_conversation("conv-1", user_id=user_id)
        
        # Add costs near user limit
        for _ in range(10):
            tracker.add_call(
                conversation_id="conv-1",
                model="claude-3-opus",
                input_tokens=5000,
                output_tokens=2500,
                agent="coach"
            )
        
        # Check if exceeded
        if not budget_manager.is_user_within_budget(user_id):
            remaining = budget_manager.get_user_budget_remaining(user_id)
            assert remaining <= 0
    
    def test_budget_alerts(self, budget_manager):
        """Test budget alert generation"""
        
        # Add costs at different thresholds
        tracker = budget_manager.tracker
        
        # 50% of daily budget
        self._add_costs_to_percentage(tracker, budget_manager.config.daily_budget_usd, 0.5)
        alerts = budget_manager.get_alerts()
        assert any("50%" in alert["message"] for alert in alerts)
        
        # 80% of daily budget
        self._add_costs_to_percentage(tracker, budget_manager.config.daily_budget_usd, 0.3)
        alerts = budget_manager.get_alerts()
        assert any("80%" in alert["message"] for alert in alerts)
        assert any(alert["level"] == "warning" for alert in alerts)
        
        # 95% of daily budget
        self._add_costs_to_percentage(tracker, budget_manager.config.daily_budget_usd, 0.15)
        alerts = budget_manager.get_alerts()
        assert any("95%" in alert["message"] or "critical" in alert["message"].lower() for alert in alerts)
        assert any(alert["level"] == "critical" for alert in alerts)
    
    def test_budget_reset(self, budget_manager):
        """Test daily budget reset"""
        
        # Add costs
        tracker = budget_manager.tracker
        tracker.start_conversation("conv-1", user_id="user-1")
        tracker.add_call(
            conversation_id="conv-1",
            model="claude-3-opus",
            input_tokens=1000,
            output_tokens=500,
            agent="coach"
        )
        
        # Check costs exist
        daily_cost = tracker.get_daily_cost()
        assert daily_cost.total_cost > 0
        
        # Simulate new day (would normally be scheduled)
        budget_manager.reset_daily_budgets()
        
        # New costs should be separate
        new_daily = tracker.get_daily_cost()
        assert new_daily.total_cost == 0 or new_daily.total_cost < daily_cost.total_cost
    
    def _add_costs_to_percentage(self, tracker, daily_budget, percentage):
        """Helper to add costs up to a percentage of budget"""
        target_cost = daily_budget * percentage
        conv_id = f"conv-{percentage}"
        tracker.start_conversation(conv_id, user_id="user-budget-test")
        
        # Calculate tokens needed (approximate)
        opus_rate = 0.075  # Output rate (higher)
        tokens_needed = int((target_cost / opus_rate) * 1000)
        
        tracker.add_call(
            conversation_id=conv_id,
            model="claude-3-opus",
            input_tokens=tokens_needed // 2,
            output_tokens=tokens_needed // 2,
            agent="coach"
        )


class TestCostOptimizationIntegration:
    """Integration tests for cost optimization"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_cost_optimization(self):
        """Test complete cost optimization flow"""
        
        # Create components
        config = CostConfig(
            daily_budget_usd=10.0,
            per_user_budget_usd=1.0,
            quality_threshold=0.8
        )
        tracker = CostTracker(config)
        selector = ModelSelector(config)
        optimizer = TokenOptimizer()
        budget_manager = BudgetManager(config, tracker)
        
        # Simulate conversation
        conv_id = "test-conversation"
        user_id = "test-user"
        tracker.start_conversation(conv_id, user_id)
        
        queries = [
            ("Good morning", "simple"),
            ("How are you?", "simple"),
            ("I'm struggling with motivation", "complex"),
            ("What should I focus on?", "medium")
        ]
        
        total_tokens = 0
        for query, complexity in queries:
            # Select model based on query
            model_choice = selector.select_model(
                query=query,
                context={"complexity": complexity}
            )
            
            # Optimize tokens
            optimized_query = optimizer.compress_prompt(query)
            
            # Track cost
            input_tokens = len(optimized_query.split()) * 10  # Approximate
            output_tokens = 100 if complexity == "simple" else 500
            
            tracker.add_call(
                conversation_id=conv_id,
                model=model_choice.model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                agent="coach"
            )
            
            total_tokens += input_tokens + output_tokens
            
            # Check budget
            if not budget_manager.is_user_within_budget(user_id):
                break
        
        # Verify optimization worked
        conv_cost = tracker.get_conversation_cost(conv_id)
        assert conv_cost.total_cost > 0
        assert conv_cost.total_input_tokens > 0
        assert conv_cost.total_output_tokens > 0
        
        # Check that simple queries used cheaper models
        assert conv_cost.model_distribution.get("claude-3-haiku", 0) > 0 or \
               conv_cost.model_distribution.get("claude-3-sonnet", 0) > 0
    
    @pytest.mark.asyncio  
    async def test_real_time_cost_monitoring(self):
        """Test real-time cost monitoring during execution"""
        
        config = CostConfig()
        tracker = CostTracker(config)
        dashboard = CostDashboard(tracker)
        
        # Simulate real-time tracking
        conv_id = "realtime-test"
        tracker.start_conversation(conv_id, user_id="user-1")
        
        # Add costs progressively
        for i in range(5):
            tracker.add_call(
                conversation_id=conv_id,
                model="claude-3-opus",
                input_tokens=500,
                output_tokens=250,
                agent="coach"
            )
            
            # Get real-time metrics
            metrics = dashboard.get_metrics(period_hours=1)
            assert metrics["conversation_count"] >= 1
            assert metrics["total_cost"] > 0
            
            # Cost should increase
            if i > 0:
                assert metrics["total_cost"] > previous_cost
            previous_cost = metrics["total_cost"]