"""
Performance profiling infrastructure for the diary coach system
"""
import time
import os
import functools
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
import logging

try:
    import psutil
    MEMORY_TRACKING_AVAILABLE = True
except ImportError:
    MEMORY_TRACKING_AVAILABLE = False

try:
    from langsmith import Client as LangSmithClient
    LANGSMITH_AVAILABLE = True
except ImportError:
    LANGSMITH_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class ProfileMetrics:
    """Metrics for a single profiled operation"""
    operation_name: str
    start_time: float
    end_time: float
    duration: float
    error: bool = False
    error_message: Optional[str] = None
    memory_used: float = 0.0
    peak_memory: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AggregatedMetrics:
    """Aggregated metrics for multiple calls to same operation"""
    operation_name: str
    count: int
    total_duration: float
    average_duration: float
    min_duration: float
    max_duration: float
    error_count: int = 0


class PerformanceProfiler:
    """Central performance profiling system"""

    _instance = None
    _metrics: Dict[str, List[ProfileMetrics]] = {}

    def __new__(cls, *args, **kwargs):
        """Singleton pattern for global profiler instance"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, enable_langsmith: bool = False, batch_size: int = 10):
        """Initialize the profiler"""
        if self._initialized:
            return

        self._metrics = {}
        self.enable_langsmith = enable_langsmith and LANGSMITH_AVAILABLE
        self.batch_size = batch_size
        self._langsmith_buffer = []

        if self.enable_langsmith:
            try:
                self.langsmith_client = LangSmithClient()
            except Exception as e:
                logger.warning(f"Failed to initialize LangSmith: {e}")
                self.enable_langsmith = False

        self._initialized = True

    def record_metric(self, metric: ProfileMetrics):
        """Record a performance metric"""
        if metric.operation_name not in self._metrics:
            self._metrics[metric.operation_name] = []

        self._metrics[metric.operation_name].append(metric)

        # Send to LangSmith if enabled
        if self.enable_langsmith:
            self._langsmith_buffer.append(metric)
            if len(self._langsmith_buffer) >= self.batch_size:
                self.flush_to_langsmith()

    def get_metrics(self, operation_name: str) -> Optional[ProfileMetrics]:
        """Get the most recent metric for an operation"""
        if operation_name in self._metrics and self._metrics[operation_name]:
            return self._metrics[operation_name][-1]
        return None

    def get_all_metrics(self, operation_name: str) -> List[ProfileMetrics]:
        """Get all metrics for an operation"""
        return self._metrics.get(operation_name, [])

    def get_aggregated_metrics(
        self, operation_name: str
    ) -> Optional[AggregatedMetrics]:
        """Get aggregated metrics for an operation"""
        metrics = self.get_all_metrics(operation_name)
        if not metrics:
            return None

        durations = [m.duration for m in metrics]
        error_count = sum(1 for m in metrics if m.error)

        return AggregatedMetrics(
            operation_name=operation_name,
            count=len(metrics),
            total_duration=sum(durations),
            average_duration=sum(durations) / len(durations),
            min_duration=min(durations),
            max_duration=max(durations),
            error_count=error_count
        )

    def flush_to_langsmith(self):
        """Send buffered metrics to LangSmith"""
        if not self._langsmith_buffer:
            return

        try:
            self.send_to_langsmith(self._langsmith_buffer)
            self._langsmith_buffer = []
        except Exception as e:
            logger.error(f"Failed to send metrics to LangSmith: {e}")

    def send_to_langsmith(self, metrics: List[ProfileMetrics]):
        """Send metrics to LangSmith"""
        if not self.enable_langsmith or not hasattr(self, 'langsmith_client'):
            return

        for metric in metrics:
            try:
                # Create a run for each metric
                self.langsmith_client.create_run(
                    name=metric.operation_name,
                    run_type="tool",
                    inputs={"operation": metric.operation_name},
                    outputs={
                        "duration": metric.duration,
                        "error": metric.error,
                        "memory_used": metric.memory_used
                    },
                    error=metric.error_message if metric.error else None,
                    start_time=datetime.fromtimestamp(metric.start_time),
                    end_time=datetime.fromtimestamp(metric.end_time),
                    extra=metric.metadata
                )
            except Exception as e:
                logger.error(f"Failed to send metric to LangSmith: {e}")

    def generate_baseline_report(self, baseline: Dict[str, Dict]) -> str:
        """Generate a baseline performance report"""
        report = ["Performance Baseline Report", "=" * 40, ""]

        for conv_type, metrics in baseline.items():
            current = metrics["current"]
            target = metrics["target"]
            gap = metrics["gap"]

            status = "✅" if gap <= 0 else "❌"
            report.append(f"{conv_type}:")
            report.append(f"  Current: {current:.2f}s")
            report.append(f"  Target:  {target:.2f}s")
            report.append(f"  Gap:     {gap:+.2f}s {status}")
            report.append("")

        return "\n".join(report)

    def identify_bottlenecks(self, baseline: Dict[str, Dict]) -> List[str]:
        """Identify performance bottlenecks"""
        bottlenecks = []

        for conv_type, metrics in baseline.items():
            if metrics["gap"] > 0:
                bottlenecks.append(conv_type)

        # Sort by gap size (biggest bottlenecks first)
        bottlenecks.sort(key=lambda x: baseline[x]["gap"], reverse=True)
        return bottlenecks

    def clear_metrics(self):
        """Clear all recorded metrics"""
        self._metrics = {}
        self._langsmith_buffer = []


def profile_async(
    operation_name: str,
    send_to_langsmith: bool = False,
    track_memory: bool = False,
    metadata: Optional[Dict[str, Any]] = None
):
    """Decorator for profiling async functions"""
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Check if profiling is disabled
            if os.environ.get("DISABLE_PROFILING") == "true":
                return await func(*args, **kwargs)

            profiler = PerformanceProfiler()
            start_time = time.perf_counter()
            error = False
            error_message = None
            memory_before = 0
            peak_memory = 0

            if track_memory and MEMORY_TRACKING_AVAILABLE:
                process = psutil.Process()
                memory_before = process.memory_info().rss / 1024 / 1024  # MB

            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                error = True
                error_message = str(e)
                raise
            finally:
                end_time = time.perf_counter()
                duration = end_time - start_time

                memory_used = 0
                if track_memory and MEMORY_TRACKING_AVAILABLE:
                    memory_after = process.memory_info().rss / 1024 / 1024
                    memory_used = memory_after - memory_before
                    peak_memory = memory_after  # Simplified for now

                metric = ProfileMetrics(
                    operation_name=operation_name,
                    start_time=start_time,
                    end_time=end_time,
                    duration=duration,
                    error=error,
                    error_message=error_message,
                    memory_used=memory_used,
                    peak_memory=peak_memory,
                    metadata=metadata or {}
                )

                profiler.record_metric(metric)

                if send_to_langsmith and profiler.enable_langsmith:
                    profiler.flush_to_langsmith()

        return wrapper
    return decorator


def profile_sync(
    operation_name: str,
    send_to_langsmith: bool = False,
    track_memory: bool = False,
    metadata: Optional[Dict[str, Any]] = None
):
    """Decorator for profiling synchronous functions"""
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Check if profiling is disabled
            if os.environ.get("DISABLE_PROFILING") == "true":
                return func(*args, **kwargs)

            profiler = PerformanceProfiler()
            start_time = time.perf_counter()
            error = False
            error_message = None
            memory_before = 0
            peak_memory = 0

            if track_memory and MEMORY_TRACKING_AVAILABLE:
                process = psutil.Process()
                memory_before = process.memory_info().rss / 1024 / 1024  # MB

            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                error = True
                error_message = str(e)
                raise
            finally:
                end_time = time.perf_counter()
                duration = end_time - start_time

                memory_used = 0
                if track_memory and MEMORY_TRACKING_AVAILABLE:
                    memory_after = process.memory_info().rss / 1024 / 1024
                    memory_used = memory_after - memory_before
                    peak_memory = memory_after  # Simplified for now

                metric = ProfileMetrics(
                    operation_name=operation_name,
                    start_time=start_time,
                    end_time=end_time,
                    duration=duration,
                    error=error,
                    error_message=error_message,
                    memory_used=memory_used,
                    peak_memory=peak_memory,
                    metadata=metadata or {}
                )

                profiler.record_metric(metric)

                if send_to_langsmith and profiler.enable_langsmith:
                    profiler.flush_to_langsmith()

        return wrapper
    return decorator
