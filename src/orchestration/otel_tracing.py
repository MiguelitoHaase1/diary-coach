"""OpenTelemetry instrumentation for distributed tracing and performance monitoring."""

import time
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, List, ContextManager
from dataclasses import dataclass, field
from contextlib import contextmanager, asynccontextmanager
import logging

# Mock OpenTelemetry imports for now (would be real in production)
class MockSpan:
    def __init__(self, name: str):
        self.name = name
        self.attributes = {}
        self.status = None
        self.start_time = time.time()
        self.end_time = None
        
    def set_attribute(self, key: str, value: Any) -> None:
        self.attributes[key] = value
        
    def set_status(self, status: str, description: str = "") -> None:
        self.status = {"status": status, "description": description}
        
    def end(self) -> None:
        self.end_time = time.time()
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.set_status("ERROR", str(exc_val))
        self.end()


class MockTracer:
    def __init__(self):
        self.spans = []
        
    def start_span(self, name: str, context=None) -> MockSpan:
        span = MockSpan(name)
        self.spans.append(span)
        return span


@dataclass
class TraceContext:
    """Context for distributed tracing."""
    trace_id: str
    span_id: Optional[str] = None
    user_id: Optional[str] = None
    conversation_id: Optional[str] = None
    session_id: Optional[str] = None
    
    def set_user_id(self, user_id: str) -> None:
        self.user_id = user_id
        
    def set_conversation_id(self, conversation_id: str) -> None:
        self.conversation_id = conversation_id
        
    def set_session_id(self, session_id: str) -> None:
        self.session_id = session_id


@dataclass
class PerformanceProfile:
    """Performance profile for an operation."""
    operation_name: str
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    metrics: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def duration_ms(self) -> float:
        if self.end_time:
            return (self.end_time - self.start_time) * 1000
        return 0.0
        
    def add_metric(self, key: str, value: Any) -> None:
        self.metrics[key] = value
        
    def finish(self) -> None:
        self.end_time = time.time()


class PerformanceProfiler:
    """Performance profiler using OpenTelemetry."""
    
    def __init__(self, instrumentation: 'OtelInstrumentation'):
        self.instrumentation = instrumentation
        
    @contextmanager
    def profile_operation(self, operation_name: str) -> PerformanceProfile:
        """Profile an operation and yield performance data."""
        profile = PerformanceProfile(operation_name)
        
        try:
            yield profile
        finally:
            profile.finish()
            
            # Add performance data to current span if available
            with self.instrumentation.trace_operation(f"{operation_name}_profile") as span:
                span.set_attribute("duration_ms", profile.duration_ms)
                for key, value in profile.metrics.items():
                    span.set_attribute(f"metric_{key}", value)


class SpanCollector:
    """Collector for capturing spans during testing."""
    
    def __init__(self):
        self.collected_spans = []
        self.span_names = set()
        
    @contextmanager
    def collect_spans(self):
        """Context manager for collecting spans."""
        # Return self to collect spans directly
        yield self
        
    def add_span(self, span: MockSpan) -> None:
        """Add a span to the collection."""
        self.collected_spans.append(span)
        self.span_names.add(span.name)
            
    def get_duration(self, operation: str) -> float:
        """Get total duration for an operation type."""
        total_duration = 0.0
        for span in self.collected_spans:
            if operation in span.name:
                if span.end_time:
                    total_duration += (span.end_time - span.start_time) * 1000
        return total_duration


@dataclass
class SpanData:
    """Data structure for collected spans."""
    spans: List[MockSpan] = field(default_factory=list)
    
    @property
    def span_names(self) -> set:
        return {span.name for span in self.spans}
        
    def get_duration(self, operation: str) -> float:
        total = 0.0
        for span in self.spans:
            if operation in span.name and span.end_time:
                total += (span.end_time - span.start_time) * 1000
        return total


class MetricsCollector:
    """Collector for custom metrics."""
    
    def __init__(self):
        self.counters = {}
        self.histograms = {}
        self.gauges = {}
        
    def record_counter(self, name: str, value: int) -> None:
        """Record a counter metric."""
        self.counters[name] = self.counters.get(name, 0) + value
        
    def record_histogram(self, name: str, value: float) -> None:
        """Record a histogram value."""
        if name not in self.histograms:
            self.histograms[name] = []
        self.histograms[name].append(value)
        
    def record_gauge(self, name: str, value: float) -> None:
        """Record a gauge value."""
        self.gauges[name] = value


class OtelInstrumentation:
    """OpenTelemetry instrumentation for the coaching system."""
    
    def __init__(self):
        """Initialize OTel instrumentation."""
        self.tracer = MockTracer()  # Would be real OTel tracer in production
        self.current_context = None
        self.sampling_rate = 1.0  # 100% sampling by default
        self.metrics_collector = MetricsCollector()
        self.logger = logging.getLogger(__name__)
        
    def configure(self, 
                 service_name: str = "diary-coach",
                 service_version: str = "1.0.0",
                 endpoint: Optional[str] = None) -> None:
        """Configure OpenTelemetry instrumentation."""
        # In production, this would configure real OTel
        self.service_name = service_name
        self.service_version = service_version
        self.endpoint = endpoint
        
    @contextmanager
    def trace_operation(self, operation_name: str, **attributes) -> MockSpan:
        """Trace an operation with automatic span management."""
        span = self.tracer.start_span(operation_name)
        
        # Set default attributes
        span.set_attribute("service.name", getattr(self, 'service_name', 'diary-coach'))
        span.set_attribute("service.version", getattr(self, 'service_version', '1.0.0'))
        span.set_attribute("operation.name", operation_name)
        span.set_attribute("timestamp", datetime.now().isoformat())
        
        # Set custom attributes
        for key, value in attributes.items():
            span.set_attribute(key, value)
            
        # Add context information if available
        if self.current_context:
            span.set_attribute("trace.id", self.current_context.trace_id)
            if self.current_context.user_id:
                span.set_attribute("user.id", self.current_context.user_id)
            if self.current_context.conversation_id:
                span.set_attribute("conversation.id", self.current_context.conversation_id)
        
        try:
            yield span
        except Exception as e:
            span.set_status("ERROR", str(e))
            self.logger.error(f"Error in operation {operation_name}: {e}")
            raise
        finally:
            span.end()
            
    @contextmanager
    def trace_conversation(self, conversation_id: str) -> MockSpan:
        """Trace an entire conversation flow."""
        with self.trace_operation("conversation", conversation_id=conversation_id) as span:
            span.set_attribute("conversation.id", conversation_id)
            span.set_attribute("conversation.start_time", datetime.now().isoformat())
            yield span
            
    @contextmanager
    def create_trace_context(self, trace_id: str) -> TraceContext:
        """Create and manage trace context."""
        context = TraceContext(trace_id=trace_id)
        old_context = self.current_context
        self.current_context = context
        
        try:
            yield context
        finally:
            self.current_context = old_context
            
    def trace_agent_processing(self, agent_name: str, message_id: str):
        """Specialized tracing for agent processing."""
        return self.trace_operation(
            "agent_processing",
            agent_name=agent_name,
            message_id=message_id
        )
        
    def trace_evaluation(self, analyzer_name: str, score: float):
        """Specialized tracing for evaluation."""
        return self.trace_operation(
            "evaluation",
            analyzer_name=analyzer_name,
            score=score
        )
        
    def trace_llm_call(self, model: str, tokens: int, cost: float):
        """Specialized tracing for LLM calls."""
        return self.trace_operation(
            "llm_call",
            model=model,
            tokens=tokens,
            cost=cost
        )
        
    def set_sampling_rate(self, rate: float) -> None:
        """Set sampling rate for traces."""
        self.sampling_rate = max(0.0, min(1.0, rate))
        
    def is_span_sampled(self, span: MockSpan) -> bool:
        """Check if span is sampled (simplified)."""
        import random
        return random.random() < self.sampling_rate
        
    def get_metrics_collector(self) -> MetricsCollector:
        """Get the metrics collector."""
        return self.metrics_collector
        
    def record_custom_metric(self, metric_type: str, name: str, value: float, **labels) -> None:
        """Record a custom metric."""
        if metric_type == "counter":
            self.metrics_collector.record_counter(name, int(value))
        elif metric_type == "histogram":
            self.metrics_collector.record_histogram(name, value)
        elif metric_type == "gauge":
            self.metrics_collector.record_gauge(name, value)
            
    def flush_metrics(self) -> Dict[str, Any]:
        """Flush and return collected metrics."""
        metrics = {
            "counters": self.metrics_collector.counters.copy(),
            "histograms": self.metrics_collector.histograms.copy(),
            "gauges": self.metrics_collector.gauges.copy()
        }
        
        # Reset collectors
        self.metrics_collector = MetricsCollector()
        
        return metrics
        
    async def trace_async_operation(self, operation_name: str, coro):
        """Trace an async operation."""
        with self.trace_operation(operation_name) as span:
            start_time = time.time()
            try:
                result = await coro
                span.set_attribute("success", True)
                return result
            except Exception as e:
                span.set_attribute("success", False)
                span.set_attribute("error", str(e))
                raise
            finally:
                duration = (time.time() - start_time) * 1000
                span.set_attribute("duration_ms", duration)
                
    def create_performance_profiler(self) -> PerformanceProfiler:
        """Create a performance profiler."""
        return PerformanceProfiler(self)
        
    def get_trace_summary(self) -> Dict[str, Any]:
        """Get summary of tracing activity."""
        return {
            "total_spans": len(self.tracer.spans),
            "service_name": getattr(self, 'service_name', 'diary-coach'),
            "sampling_rate": self.sampling_rate,
            "active_traces": 1 if self.current_context else 0
        }
        
    def export_traces(self, format: str = "json") -> str:
        """Export traces for analysis."""
        # In production, this would export to OTel collectors
        import json
        
        traces_data = []
        for span in self.tracer.spans:
            trace_data = {
                "name": span.name,
                "attributes": span.attributes,
                "start_time": span.start_time,
                "end_time": span.end_time,
                "duration_ms": (span.end_time - span.start_time) * 1000 if span.end_time else None,
                "status": span.status
            }
            traces_data.append(trace_data)
            
        if format == "json":
            return json.dumps(traces_data, indent=2)
        else:
            return str(traces_data)