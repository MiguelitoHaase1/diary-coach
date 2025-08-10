"""
Tests for execution path optimization
"""
import asyncio
import time
import pytest
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, List, Any

from src.performance.fast_path_router import (
    FastPathRouter,
    PathPattern,
    FastPathConfig,
    SpeculativeExecutor,
    PathMetrics
)


class TestFastPathDetection:
    """Test fast path pattern detection"""
    
    @pytest.fixture
    def fast_path_config(self):
        """Create test configuration"""
        return FastPathConfig(
            simple_query_threshold=20,  # Words
            fast_path_timeout=1.0,  # Seconds
            enable_speculation=True,
            speculation_confidence=0.7,
            precompute_morning=True
        )
    
    def test_simple_query_detection(self, fast_path_config):
        """Test detection of simple queries"""
        router = FastPathRouter(fast_path_config)
        
        # Simple queries that should use fast path
        simple_queries = [
            "What's the weather?",
            "How are you?",
            "Good morning",
            "Thank you",
            "What time is it?",
            "Hello there"
        ]
        
        for query in simple_queries:
            path = router.detect_path(query)
            assert path.is_fast_path
            assert path.pattern_type in ["greeting", "simple_question", "acknowledgment"]
    
    def test_complex_query_detection(self, fast_path_config):
        """Test that complex queries don't use fast path"""
        router = FastPathRouter(fast_path_config)
        
        # Complex queries requiring full processing
        complex_queries = [
            "I'm feeling overwhelmed with work and personal responsibilities, "
            "and I don't know how to prioritize everything effectively.",
            "Can you help me understand why I keep procrastinating on important "
            "tasks even though I know they need to be done?",
            "Let's do a deep reflection on my patterns from this week"
        ]
        
        for query in complex_queries:
            path = router.detect_path(query)
            assert not path.is_fast_path
            assert path.pattern_type == "complex"
    
    def test_morning_protocol_detection(self, fast_path_config):
        """Test morning protocol pattern detection"""
        router = FastPathRouter(fast_path_config)
        
        morning_queries = [
            "Good morning",
            "Morning check-in",
            "Let's start the day",
            "Morning!",
            "Ready for my morning routine"
        ]
        
        for query in morning_queries:
            path = router.detect_path(query, context={"time_of_day": "morning"})
            assert path.pattern_type == "morning_protocol"
            assert path.is_fast_path
            assert path.use_precomputed
    
    def test_pattern_caching(self, fast_path_config):
        """Test that patterns are cached for reuse"""
        router = FastPathRouter(fast_path_config)
        
        query = "How are you doing?"
        
        # First detection
        start = time.perf_counter()
        path1 = router.detect_path(query)
        first_time = time.perf_counter() - start
        
        # Second detection (should be cached)
        start = time.perf_counter()
        path2 = router.detect_path(query)
        second_time = time.perf_counter() - start
        
        assert path1.pattern_type == path2.pattern_type
        assert second_time < first_time * 0.5  # At least 2x faster
    
    def test_context_aware_routing(self, fast_path_config):
        """Test routing based on conversation context"""
        router = FastPathRouter(fast_path_config)
        
        # Same query, different contexts
        query = "Tell me more"
        
        # In simple context
        simple_context = {"previous_pattern": "greeting"}
        path1 = router.detect_path(query, context=simple_context)
        assert path1.is_fast_path
        
        # In complex context
        complex_context = {"previous_pattern": "deep_reflection"}
        path2 = router.detect_path(query, context=complex_context)
        assert not path2.is_fast_path


class TestSpeculativeExecution:
    """Test speculative execution for follow-ups"""
    
    @pytest.fixture
    def speculative_executor(self):
        """Create speculative executor"""
        return SpeculativeExecutor(
            confidence_threshold=0.7,
            max_speculations=3,
            timeout=2.0
        )
    
    @pytest.mark.asyncio
    async def test_follow_up_prediction(self, speculative_executor):
        """Test prediction of likely follow-up queries"""
        
        # Current query and context
        current_query = "Good morning"
        context = {"time_of_day": "morning", "user_pattern": "regular"}
        
        # Get predictions
        predictions = await speculative_executor.predict_follow_ups(
            current_query, context
        )
        
        # Should predict common morning follow-ups
        assert len(predictions) > 0
        assert any("weather" in p.query.lower() for p in predictions)
        assert any("today" in p.query.lower() for p in predictions)
        assert all(p.confidence >= 0.7 for p in predictions)
    
    @pytest.mark.asyncio
    async def test_speculative_execution(self, speculative_executor):
        """Test execution of speculative queries"""
        
        # Mock LLM service
        mock_llm = AsyncMock()
        mock_llm.generate_response = AsyncMock(
            return_value="Speculative response"
        )
        
        # Current state
        current_query = "How's the weather?"
        predictions = [
            Mock(query="What should I wear?", confidence=0.8),
            Mock(query="Any rain expected?", confidence=0.75)
        ]
        
        # Execute speculatively
        with patch('src.performance.fast_path_router.get_llm_service', return_value=mock_llm):
            results = await speculative_executor.execute_speculations(
                predictions, mock_llm
            )
        
        assert len(results) == 2
        assert all(r.is_ready for r in results)
        assert mock_llm.generate_response.call_count == 2
    
    @pytest.mark.asyncio
    async def test_speculative_cache_hit(self, speculative_executor):
        """Test using speculative results when prediction matches"""
        
        # Pre-execute speculation
        speculation_result = Mock(
            query="What should I focus on today?",
            response="Here are your priorities...",
            is_ready=True
        )
        
        speculative_executor.cache_speculation(speculation_result)
        
        # User asks the predicted question
        actual_query = "What should I focus on today?"
        
        # Should get instant response
        start = time.perf_counter()
        cached = await speculative_executor.get_cached_speculation(actual_query)
        duration = time.perf_counter() - start
        
        assert cached is not None
        assert cached.response == "Here are your priorities..."
        assert duration < 0.01  # Near instant
    
    @pytest.mark.asyncio
    async def test_speculation_timeout(self, speculative_executor):
        """Test that speculation doesn't block main execution"""
        
        # Slow speculation
        async def slow_speculation():
            await asyncio.sleep(5)
            return "Slow response"
        
        # Should timeout
        start = time.perf_counter()
        result = await speculative_executor.execute_with_timeout(
            slow_speculation(), timeout=0.5
        )
        duration = time.perf_counter() - start
        
        assert result is None  # Timed out
        assert duration < 0.6  # Respected timeout
    
    def test_speculation_accuracy_tracking(self, speculative_executor):
        """Test tracking of speculation accuracy"""
        
        # Record hits and misses
        speculative_executor.record_hit("weather")
        speculative_executor.record_hit("weather")
        speculative_executor.record_miss("weather")
        speculative_executor.record_hit("morning")
        speculative_executor.record_miss("morning")
        speculative_executor.record_miss("morning")
        
        # Check accuracy
        weather_accuracy = speculative_executor.get_accuracy("weather")
        morning_accuracy = speculative_executor.get_accuracy("morning")
        
        assert weather_accuracy == 0.67  # 2/3
        assert morning_accuracy == 0.33  # 1/3
        
        # Should disable speculation for low accuracy
        assert speculative_executor.should_speculate("weather") is True
        assert speculative_executor.should_speculate("morning") is False


class TestPrecomputation:
    """Test precomputation of static components"""
    
    def test_morning_protocol_precomputation(self):
        """Test precomputation of morning protocol components"""
        from src.performance.fast_path_router import PrecomputedComponents
        
        components = PrecomputedComponents()
        
        # Precompute morning components
        components.precompute_morning_protocol()
        
        # Should have cached components
        assert components.has_morning_greeting
        assert components.has_morning_prompts
        assert components.has_morning_transitions
        
        # Get precomputed components
        greeting = components.get_morning_greeting()
        assert "Good morning" in greeting
        
        prompts = components.get_morning_prompts()
        assert len(prompts) > 0
        assert any("feeling" in p.lower() for p in prompts)
    
    def test_static_prompt_compilation(self):
        """Test compilation of static prompt components"""
        from src.performance.fast_path_router import PromptCompiler
        
        compiler = PromptCompiler()
        
        # Compile static components
        compiled = compiler.compile_static_prompts()
        
        # Should have core components
        assert "coach_base" in compiled
        assert "agent_instructions" in compiled
        assert "response_format" in compiled
        
        # Should be faster than dynamic loading
        start = time.perf_counter()
        static = compiled["coach_base"]
        static_time = time.perf_counter() - start
        
        start = time.perf_counter()
        dynamic = compiler.load_dynamic_prompt("coach_base")
        dynamic_time = time.perf_counter() - start
        
        assert static == dynamic  # Same content
        assert static_time < dynamic_time * 0.1  # 10x faster
    
    def test_precomputed_response_templates(self):
        """Test precomputed response templates"""
        from src.performance.fast_path_router import ResponseTemplates
        
        templates = ResponseTemplates()
        
        # Common response patterns
        templates.precompute_common_responses()
        
        # Should have templates for common queries
        assert templates.has_template("greeting")
        assert templates.has_template("acknowledgment")
        assert templates.has_template("clarification")
        
        # Templates should be customizable
        greeting = templates.render("greeting", name="User")
        assert "User" in greeting
        assert "Hello" in greeting or "Hi" in greeting


class TestFastPathPerformance:
    """Test performance improvements from fast paths"""
    
    @pytest.mark.asyncio
    async def test_fast_path_latency(self):
        """Test that fast paths meet latency targets"""
        from src.performance.fast_path_router import FastPathExecutor
        
        executor = FastPathExecutor()
        
        # Simple queries should be under 1 second
        simple_queries = [
            "Hello",
            "Thank you",
            "What time is it?",
            "Good morning"
        ]
        
        for query in simple_queries:
            start = time.perf_counter()
            response = await executor.execute_fast_path(query)
            duration = time.perf_counter() - start
            
            assert response is not None
            assert duration < 1.0  # Under 1 second
    
    @pytest.mark.asyncio
    async def test_fast_path_vs_normal(self):
        """Test speedup from fast path routing"""
        from src.performance.fast_path_router import FastPathExecutor
        
        executor = FastPathExecutor()
        
        query = "How are you?"
        
        # Normal path
        start = time.perf_counter()
        normal_response = await executor.execute_normal_path(query)
        normal_time = time.perf_counter() - start
        
        # Fast path
        start = time.perf_counter()
        fast_response = await executor.execute_fast_path(query)
        fast_time = time.perf_counter() - start
        
        # Fast path should be significantly faster
        assert fast_time < normal_time * 0.3  # At least 3x faster
        
        # But should still have reasonable response
        assert len(fast_response) > 10
        assert "I'm" in fast_response or "doing" in fast_response
    
    def test_path_metrics_collection(self):
        """Test collection of path execution metrics"""
        metrics = PathMetrics()
        
        # Record executions
        metrics.record_execution("fast", 0.5)
        metrics.record_execution("fast", 0.6)
        metrics.record_execution("fast", 0.4)
        metrics.record_execution("normal", 2.0)
        metrics.record_execution("normal", 2.5)
        
        # Check metrics
        fast_avg = metrics.get_average_latency("fast")
        normal_avg = metrics.get_average_latency("normal")
        
        assert fast_avg == 0.5  # (0.5 + 0.6 + 0.4) / 3
        assert normal_avg == 2.25  # (2.0 + 2.5) / 2
        
        # Check hit rates
        metrics.record_cache_hit("fast")
        metrics.record_cache_hit("fast")
        metrics.record_cache_miss("fast")
        
        hit_rate = metrics.get_cache_hit_rate("fast")
        assert hit_rate == 0.67  # 2/3