"""Performance tracking for coaching conversations."""

import time
from typing import List


class PerformanceTracker:
    """Tracks response times and performance metrics for coaching conversations."""
    
    def __init__(self):
        """Initialize performance tracker."""
        self.response_times: List[float] = []
    
    async def track_response(self, start_time: float, end_time: float) -> None:
        """Track response time in milliseconds.
        
        Args:
            start_time: Start time in seconds (from time.time())
            end_time: End time in seconds (from time.time())
        """
        response_time_ms = (end_time - start_time) * 1000
        self.response_times.append(response_time_ms)
    
    def get_percentile(self, percentile: int) -> float:
        """Get response time at given percentile.
        
        Args:
            percentile: Percentile to calculate (0-100)
            
        Returns:
            Response time in milliseconds at the given percentile
        """
        if not self.response_times:
            return 0
        
        sorted_times = sorted(self.response_times)
        index = int(len(sorted_times) * percentile / 100)
        return sorted_times[min(index, len(sorted_times) - 1)]
    
    def percentage_under_threshold(self, threshold_ms: float) -> float:
        """Calculate percentage of responses under threshold.
        
        Args:
            threshold_ms: Threshold in milliseconds
            
        Returns:
            Percentage of responses under threshold (0.0 to 1.0)
        """
        if not self.response_times:
            return 0.0
        
        under = sum(1 for t in self.response_times if t < threshold_ms)
        return under / len(self.response_times)
    
    def get_median(self) -> float:
        """Get median response time in milliseconds."""
        return self.get_percentile(50)
    
    def reset(self) -> None:
        """Reset all tracked response times."""
        self.response_times.clear()