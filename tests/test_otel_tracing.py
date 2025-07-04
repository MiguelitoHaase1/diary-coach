"""Tests for OpenTelemetry tracing instrumentation."""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import time
from datetime import datetime
from typing import Dict, Any, List

from src.orchestration.otel_tracing import (
    OtelInstrumentation, 
    SpanCollector,
    TraceContext,
    PerformanceProfiler
)
from src.orchestration.state import ConversationState
from src.events.schemas import UserMessage, AgentResponse


class TestOtelTracing:
    """Test OpenTelemetry tracing functionality."""

    @pytest.fixture
    def mock_tracer(self):
        """Mock OpenTelemetry tracer."""
        from src.orchestration.otel_tracing import MockTracer
        return MockTracer()

    @pytest.fixture
    def otel_instrumentation(self, mock_tracer):
        """Create OTel instrumentation with mock tracer."""
        instrumentation = OtelInstrumentation()
        instrumentation.tracer = mock_tracer
        return instrumentation

    @pytest.fixture
    def span_collector(self):
        """Create span collector for testing."""
        return SpanCollector()

    @pytest.fixture
    def sample_message(self):
        """Create sample user message."""
        return UserMessage(
            content="Good morning, I want to work on my project today",
            user_id="user123",
            timestamp=datetime.now(),
            conversation_id="test_conv_123"
        )

    @pytest.fixture
    def sample_response(self):
        """Create sample agent response."""
        return AgentResponse(
            content="What's the most important outcome you want to achieve?",
            agent_name="DiaryCoach",
            response_to="msg123",
            conversation_id="test_conv_123"
        )

    @pytest.mark.asyncio
    async def test_tracing_spans(self, otel_instrumentation, span_collector, sample_message):
        """Test that every agent interaction creates spans."""
        # Start coach processing span
        with otel_instrumentation.trace_operation("coach_processing") as span:
            span_collector.add_span(span)
            span.set_attribute("user_id", sample_message.user_id)
            span.set_attribute("conversation_id", sample_message.conversation_id)
            span.set_attribute("message_length", len(sample_message.content))
            
            # Simulate processing time
            await asyncio.sleep(0.001)
            
            # Start evaluation scoring span
            with otel_instrumentation.trace_operation("evaluation_scoring") as eval_span:
                span_collector.add_span(eval_span)
                eval_span.set_attribute("analyzer", "SpecificityPush")
                eval_span.set_attribute("score", 8.5)
                
                # Simulate evaluation time
                await asyncio.sleep(0.001)
        
        # Verify spans were created
        assert "coach_processing" in span_collector.span_names
        assert "evaluation_scoring" in span_collector.span_names
        
        # Verify tracer was called
        assert len(otel_instrumentation.tracer.spans) >= 2

    @pytest.mark.asyncio
    async def test_trace_conversation_flow(self, otel_instrumentation, sample_message, sample_response):
        """Test tracing complete conversation flow."""
        conversation_id = sample_message.conversation_id
        
        # Start conversation trace
        with otel_instrumentation.trace_conversation(conversation_id) as conversation_span:
            conversation_span.set_attribute("conversation_id", conversation_id)
            conversation_span.set_attribute("user_id", sample_message.user_id)
            
            # Process user message
            with otel_instrumentation.trace_operation("message_processing") as msg_span:
                msg_span.set_attribute("message_type", "user")
                msg_span.set_attribute("content_length", len(sample_message.content))
                msg_span.set_attribute("timestamp", sample_message.timestamp.isoformat())
                
                # Simulate message processing
                await asyncio.sleep(0.001)
            
            # Generate agent response
            with otel_instrumentation.trace_operation("response_generation") as resp_span:
                resp_span.set_attribute("agent_name", sample_response.agent_name)
                resp_span.set_attribute("response_length", len(sample_response.content))
                resp_span.set_attribute("response_to", sample_response.response_to)
                
                # Simulate response generation
                await asyncio.sleep(0.001)
        
        # Verify spans were created with proper hierarchy
        assert len(otel_instrumentation.tracer.spans) >= 3

    @pytest.mark.asyncio
    async def test_performance_profiling(self, otel_instrumentation):
        """Test performance profiling capabilities."""
        profiler = PerformanceProfiler(otel_instrumentation)
        
        # Profile agent processing
        with profiler.profile_operation("agent_processing") as profile:
            # Simulate CPU-intensive operation
            await asyncio.sleep(0.005)
            
            # Add custom metrics
            profile.add_metric("tokens_processed", 150)
            profile.add_metric("api_calls", 2)
            profile.add_metric("memory_mb", 45.2)
        
        # Verify profiling data
        assert profile.duration_ms > 0
        assert profile.metrics["tokens_processed"] == 150
        assert profile.metrics["api_calls"] == 2
        assert profile.metrics["memory_mb"] == 45.2

    @pytest.mark.asyncio
    async def test_context_propagation(self, otel_instrumentation):
        """Test context propagation across operations."""
        trace_id = "trace-123-456"
        
        # Create trace context
        with otel_instrumentation.create_trace_context(trace_id) as context:
            context.set_user_id("user123")
            context.set_conversation_id("conv123")
            context.set_session_id("session123")
            
            # Start nested operation
            with otel_instrumentation.trace_operation("nested_operation") as span:
                # Context should be automatically propagated
                span.set_attribute("operation", "nested")
                
                # Start deeply nested operation
                with otel_instrumentation.trace_operation("deep_nested") as deep_span:
                    deep_span.set_attribute("level", "deep")
        
        # Verify context propagation
        assert context.trace_id == trace_id
        assert context.user_id == "user123"
        assert context.conversation_id == "conv123"

    @pytest.mark.asyncio
    async def test_error_tracking(self, otel_instrumentation, sample_message):
        """Test error tracking in spans."""
        try:
            with otel_instrumentation.trace_operation("error_operation") as span:
                span.set_attribute("message_id", sample_message.message_id)
                
                # Simulate an error
                raise ValueError("Test error for tracing")
                
        except ValueError:
            # Error should be captured in span
            pass
        
        # Verify error was recorded in the last span
        spans = otel_instrumentation.tracer.spans
        assert len(spans) > 0
        last_span = spans[-1]
        assert last_span.status is not None

    @pytest.mark.asyncio
    async def test_custom_attributes(self, otel_instrumentation, sample_message):
        """Test custom attribute setting."""
        with otel_instrumentation.trace_operation("custom_attributes") as span:
            # Set various custom attributes
            span.set_attribute("conversation_id", sample_message.conversation_id)
            span.set_attribute("user_id", sample_message.user_id)
            span.set_attribute("message_length", len(sample_message.content))
            span.set_attribute("processing_stage", "analysis")
            span.set_attribute("confidence_score", 0.87)
            span.set_attribute("is_morning", True)
        
        # Verify attributes were set
        spans = otel_instrumentation.tracer.spans
        assert len(spans) > 0
        last_span = spans[-1]
        assert len(last_span.attributes) >= 6

    @pytest.mark.asyncio
    async def test_distributed_tracing(self, otel_instrumentation):
        """Test distributed tracing across systems."""
        # Start parent span (simulating external request)
        with otel_instrumentation.trace_operation("external_request") as parent_span:
            parent_span.set_attribute("source", "client_app")
            parent_span.set_attribute("request_id", "req-123")
            
            # Process in EventBus system
            with otel_instrumentation.trace_operation("eventbus_processing") as eb_span:
                eb_span.set_attribute("system", "eventbus")
                eb_span.set_attribute("agent", "DiaryCoach")
                
                # Process in LangGraph system (parallel)
                with otel_instrumentation.trace_operation("langgraph_processing") as lg_span:
                    lg_span.set_attribute("system", "langgraph")
                    lg_span.set_attribute("node", "CoachNode")
        
        # Verify distributed trace structure
        assert len(otel_instrumentation.tracer.spans) >= 3

    @pytest.mark.asyncio
    async def test_span_relationships(self, otel_instrumentation):
        """Test parent-child span relationships."""
        # Parent operation
        with otel_instrumentation.trace_operation("parent_operation") as parent:
            parent.set_attribute("operation_type", "parent")
            
            # Child operation 1
            with otel_instrumentation.trace_operation("child_operation_1") as child1:
                child1.set_attribute("operation_type", "child")
                child1.set_attribute("child_number", 1)
            
            # Child operation 2  
            with otel_instrumentation.trace_operation("child_operation_2") as child2:
                child2.set_attribute("operation_type", "child")
                child2.set_attribute("child_number", 2)
        
        # Verify proper nesting
        assert len(otel_instrumentation.tracer.spans) == 3

    @pytest.mark.asyncio
    async def test_metrics_collection(self, otel_instrumentation):
        """Test metrics collection during operations."""
        metrics_collector = otel_instrumentation.get_metrics_collector()
        
        with otel_instrumentation.trace_operation("metrics_operation") as span:
            # Collect various metrics
            metrics_collector.record_counter("messages_processed", 1)
            metrics_collector.record_histogram("processing_duration", 150.5)
            metrics_collector.record_gauge("active_conversations", 5)
            
            # Add span-specific metrics
            span.set_attribute("tokens_used", 145)
            span.set_attribute("cost_usd", 0.023)
        
        # Verify metrics were collected
        assert metrics_collector.counters["messages_processed"] == 1
        assert metrics_collector.histograms["processing_duration"] == [150.5]
        assert metrics_collector.gauges["active_conversations"] == 5

    @pytest.mark.asyncio
    async def test_trace_sampling(self, otel_instrumentation):
        """Test trace sampling configuration."""
        # Configure sampling rate
        otel_instrumentation.set_sampling_rate(0.5)  # 50% sampling
        
        traces_sampled = 0
        total_traces = 10
        
        for i in range(total_traces):
            with otel_instrumentation.trace_operation(f"sampled_operation_{i}") as span:
                span.set_attribute("iteration", i)
                if otel_instrumentation.is_span_sampled(span):
                    traces_sampled += 1
        
        # Should sample approximately 50% (with some variance)
        sampling_rate = traces_sampled / total_traces
        assert 0.3 <= sampling_rate <= 0.7  # Allow some variance


import asyncio