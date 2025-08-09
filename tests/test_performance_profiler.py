"""
Tests for performance profiling infrastructure
"""
import asyncio
import time
import pytest
from unittest.mock import Mock, patch, AsyncMock

from src.performance.profiler import (
    PerformanceProfiler,
    profile_async,
    profile_sync,
    ProfileMetrics
)


class TestPerformanceProfiler:
    """Test performance profiling infrastructure"""
    
    @pytest.mark.asyncio
    async def test_profiler_accuracy(self):
        """Test that timing measurements are accurate"""
        profiler = PerformanceProfiler()
        
        # Test async function timing
        @profile_async("test_operation")
        async def slow_operation():
            await asyncio.sleep(0.1)
            return "done"
        
        result = await slow_operation()
        assert result == "done"
        
        metrics = profiler.get_metrics("test_operation")
        assert metrics is not None
        assert 0.09 < metrics.duration < 0.11  # Allow 10ms variance
        assert metrics.operation_name == "test_operation"
        assert metrics.start_time > 0
        assert metrics.end_time > metrics.start_time
    
    def test_sync_profiler_accuracy(self):
        """Test synchronous function profiling"""
        profiler = PerformanceProfiler()
        
        @profile_sync("sync_operation")
        def slow_sync_operation():
            time.sleep(0.05)
            return "sync_done"
        
        result = slow_sync_operation()
        assert result == "sync_done"
        
        metrics = profiler.get_metrics("sync_operation")
        assert metrics is not None
        assert 0.04 < metrics.duration < 0.06  # Allow 10ms variance
    
    @pytest.mark.asyncio
    async def test_nested_profiling(self):
        """Test profiling of nested function calls"""
        profiler = PerformanceProfiler()
        
        @profile_async("outer")
        async def outer_operation():
            await asyncio.sleep(0.05)
            result = await inner_operation()
            return f"outer_{result}"
        
        @profile_async("inner")
        async def inner_operation():
            await asyncio.sleep(0.05)
            return "inner"
        
        result = await outer_operation()
        assert result == "outer_inner"
        
        outer_metrics = profiler.get_metrics("outer")
        inner_metrics = profiler.get_metrics("inner")
        
        assert outer_metrics.duration > inner_metrics.duration
        assert 0.09 < outer_metrics.duration < 0.11
        assert 0.04 < inner_metrics.duration < 0.06
    
    @pytest.mark.asyncio
    async def test_error_handling_in_profiled_function(self):
        """Test that profiling handles errors correctly"""
        profiler = PerformanceProfiler()
        
        @profile_async("error_operation")
        async def failing_operation():
            await asyncio.sleep(0.01)
            raise ValueError("Test error")
        
        with pytest.raises(ValueError):
            await failing_operation()
        
        metrics = profiler.get_metrics("error_operation")
        assert metrics is not None
        assert metrics.error is True
        assert metrics.error_message == "Test error"
        assert metrics.duration > 0
    
    def test_aggregated_metrics(self):
        """Test aggregation of multiple calls to same operation"""
        profiler = PerformanceProfiler()
        
        @profile_sync("repeated_op")
        def repeated_operation(sleep_time):
            time.sleep(sleep_time)
            return "done"
        
        # Call multiple times with different durations
        for sleep_time in [0.01, 0.02, 0.03]:
            repeated_operation(sleep_time)
        
        aggregated = profiler.get_aggregated_metrics("repeated_op")
        assert aggregated.count == 3
        assert aggregated.total_duration > 0.05
        assert aggregated.average_duration > 0.01
        assert aggregated.min_duration < aggregated.max_duration
    
    @pytest.mark.asyncio
    async def test_concurrent_profiling(self):
        """Test profiling of concurrent async operations"""
        profiler = PerformanceProfiler()
        
        @profile_async("concurrent_op")
        async def concurrent_operation(op_id, sleep_time):
            await asyncio.sleep(sleep_time)
            return f"op_{op_id}"
        
        # Run operations concurrently
        results = await asyncio.gather(
            concurrent_operation(1, 0.05),
            concurrent_operation(2, 0.03),
            concurrent_operation(3, 0.04)
        )
        
        assert results == ["op_1", "op_2", "op_3"]
        
        aggregated = profiler.get_aggregated_metrics("concurrent_op")
        assert aggregated.count == 3
        # Total time should be sum of all operations
        assert aggregated.total_duration > 0.11
    
    def test_memory_tracking(self):
        """Test memory usage tracking in profiler"""
        profiler = PerformanceProfiler()
        
        @profile_sync("memory_intensive", track_memory=True)
        def memory_operation():
            # Allocate some memory
            data = [i for i in range(100000)]
            return len(data)
        
        result = memory_operation()
        assert result == 100000
        
        metrics = profiler.get_metrics("memory_intensive")
        assert metrics.memory_used > 0
        assert metrics.peak_memory >= metrics.memory_used


class TestLangSmithIntegration:
    """Test LangSmith integration for performance visualization"""
    
    @pytest.mark.asyncio
    async def test_langsmith_integration(self):
        """Test that metrics are sent to LangSmith"""
        # Clear singleton state
        PerformanceProfiler._instance = None
        
        with patch('src.performance.profiler.LangSmithClient') as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance
            
            profiler = PerformanceProfiler(enable_langsmith=True)
            
            @profile_async("langsmith_op", send_to_langsmith=True)
            async def tracked_operation():
                await asyncio.sleep(0.01)
                return "tracked"
            
            result = await tracked_operation()
            assert result == "tracked"
            
            # Verify LangSmith client was called
            mock_instance.create_run.assert_called_once()
            call_args = mock_instance.create_run.call_args
            assert "langsmith_op" in str(call_args)
    
    @pytest.mark.asyncio
    async def test_langsmith_batch_send(self):
        """Test batching of metrics to LangSmith"""
        # Clear singleton state
        PerformanceProfiler._instance = None
        
        with patch('src.performance.profiler.LangSmithClient'):
            profiler = PerformanceProfiler(
                enable_langsmith=True,
                batch_size=3
            )
            
            with patch.object(profiler, 'send_to_langsmith') as mock_send:
                # Generate multiple metrics
                for i in range(5):
                    @profile_sync(f"batch_op_{i}")
                    def batch_operation():
                        return i
                    batch_operation()
                
                # Force flush
                profiler.flush_to_langsmith()
                
                # Should have sent 2 batches (3 + 2)
                assert mock_send.call_count == 2


class TestPerformanceBaseline:
    """Test baseline performance metrics collection"""
    
    @pytest.mark.asyncio
    async def test_performance_baseline(self):
        """Document current latencies for all conversation types"""
        profiler = PerformanceProfiler()
        baseline = {}
        
        # Simulate different conversation types
        conversation_types = [
            ("simple_greeting", 0.5),  # Target: <0.5s
            ("morning_protocol", 2.0),  # Target: <2s
            ("stage_2_complex", 4.0),   # Target: <3s
            ("deep_thoughts", 12.0),    # Target: <10s
            ("web_search", 3.0),        # Target: <5s
        ]
        
        for conv_type, simulated_time in conversation_types:
            @profile_async(conv_type)
            async def simulate_conversation():
                # Simulate processing time
                await asyncio.sleep(simulated_time / 100)  # Scale down for test
                return f"{conv_type}_response"
            
            await simulate_conversation()
            metrics = profiler.get_metrics(conv_type)
            baseline[conv_type] = {
                "current": simulated_time,
                "target": self._get_target_time(conv_type),
                "gap": simulated_time - self._get_target_time(conv_type)
            }
        
        # Generate baseline report
        report = profiler.generate_baseline_report(baseline)
        assert "simple_greeting" in report
        assert "Performance Baseline Report" in report
        
        # Check that we identify bottlenecks
        bottlenecks = profiler.identify_bottlenecks(baseline)
        assert "deep_thoughts" in bottlenecks
        assert "stage_2_complex" in bottlenecks
    
    def _get_target_time(self, conv_type):
        """Get target time for conversation type"""
        targets = {
            "simple_greeting": 0.5,
            "morning_protocol": 2.0,
            "stage_2_complex": 3.0,
            "deep_thoughts": 10.0,
            "web_search": 5.0,
        }
        return targets.get(conv_type, 3.0)


class TestProfilingDecorators:
    """Test profiling decorator behavior"""
    
    def test_decorator_preserves_function_metadata(self):
        """Test that decorators preserve function metadata"""
        @profile_sync("test_func")
        def original_function():
            """Original docstring"""
            return "result"
        
        assert original_function.__name__ == "original_function"
        assert original_function.__doc__ == "Original docstring"
    
    @pytest.mark.asyncio
    async def test_conditional_profiling(self):
        """Test conditional profiling based on environment"""
        import os
        
        # Disable profiling
        os.environ["DISABLE_PROFILING"] = "true"
        
        @profile_async("conditional_op")
        async def conditional_operation():
            await asyncio.sleep(0.01)
            return "done"
        
        result = await conditional_operation()
        assert result == "done"
        
        profiler = PerformanceProfiler()
        metrics = profiler.get_metrics("conditional_op")
        assert metrics is None  # Should not profile when disabled
        
        # Re-enable profiling
        del os.environ["DISABLE_PROFILING"]
    
    def test_custom_metadata_in_profile(self):
        """Test adding custom metadata to profile metrics"""
        profiler = PerformanceProfiler()
        
        @profile_sync("metadata_op", metadata={"user_id": "123", "session": "abc"})
        def operation_with_metadata():
            return "result"
        
        result = operation_with_metadata()
        assert result == "result"
        
        metrics = profiler.get_metrics("metadata_op")
        assert metrics.metadata["user_id"] == "123"
        assert metrics.metadata["session"] == "abc"