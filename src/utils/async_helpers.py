"""Async utilities and error handling patterns."""

import asyncio
import logging
from typing import TypeVar, Callable, Any, Optional, List, Coroutine
from functools import wraps
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

T = TypeVar('T')


def async_retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """Decorator for retrying async functions with exponential backoff.
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Backoff multiplier for each retry
        exceptions: Tuple of exceptions to catch and retry
    """
    def decorator(func: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., Coroutine[Any, Any, T]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_attempts} failed for "
                            f"{func.__name__}: {str(e)}. Retrying in {current_delay}s..."
                        )
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            f"All {max_attempts} attempts failed for {func.__name__}"
                        )
            
            if last_exception:
                raise last_exception
            raise RuntimeError(f"Failed after {max_attempts} attempts")
        
        return wrapper
    return decorator


async def gather_with_timeout(
    *coroutines: Coroutine[Any, Any, T],
    timeout: float = 30.0,
    return_exceptions: bool = True
) -> List[Any]:
    """Gather multiple coroutines with a timeout.
    
    Args:
        *coroutines: Coroutines to run concurrently
        timeout: Timeout in seconds
        return_exceptions: If True, exceptions are returned as results
        
    Returns:
        List of results from the coroutines
    """
    try:
        return await asyncio.wait_for(
            asyncio.gather(*coroutines, return_exceptions=return_exceptions),
            timeout=timeout
        )
    except asyncio.TimeoutError:
        logger.error(f"Timeout after {timeout}s while gathering coroutines")
        # Cancel any still-running tasks
        for coro in coroutines:
            if hasattr(coro, 'cancel'):
                coro.cancel()
        raise


@asynccontextmanager
async def async_timeout(seconds: float):
    """Context manager for async operations with timeout.
    
    Args:
        seconds: Timeout in seconds
        
    Example:
        async with async_timeout(5.0):
            await some_long_operation()
    """
    async def timeout_handler():
        await asyncio.sleep(seconds)
        raise asyncio.TimeoutError(f"Operation timed out after {seconds}s")
    
    timeout_task = asyncio.create_task(timeout_handler())
    try:
        yield
    finally:
        timeout_task.cancel()
        try:
            await timeout_task
        except asyncio.CancelledError:
            pass


class AsyncResourceManager:
    """Base class for managing async resources with proper cleanup."""
    
    def __init__(self):
        self._resources: List[Any] = []
        self._cleanup_tasks: List[Callable] = []
    
    def register_resource(self, resource: Any, cleanup: Optional[Callable] = None):
        """Register a resource for cleanup.
        
        Args:
            resource: The resource to track
            cleanup: Optional cleanup function
        """
        self._resources.append(resource)
        if cleanup:
            self._cleanup_tasks.append(cleanup)
    
    async def cleanup(self):
        """Clean up all registered resources."""
        errors = []
        
        # Run cleanup tasks
        for cleanup_func in self._cleanup_tasks:
            try:
                if asyncio.iscoroutinefunction(cleanup_func):
                    await cleanup_func()
                else:
                    cleanup_func()
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")
                errors.append(e)
        
        # Clear resources
        self._resources.clear()
        self._cleanup_tasks.clear()
        
        if errors:
            raise Exception(f"Cleanup errors: {errors}")
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()


async def safe_gather(
    *tasks: Coroutine[Any, Any, T],
    default_value: Any = None,
    log_errors: bool = True
) -> List[Any]:
    """Safely gather multiple tasks, returning default values for failures.
    
    Args:
        *tasks: Tasks to run concurrently
        default_value: Value to return for failed tasks
        log_errors: Whether to log errors
        
    Returns:
        List of results, with default_value for any failures
    """
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    final_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            if log_errors:
                logger.error(f"Task {i} failed: {result}")
            final_results.append(default_value)
        else:
            final_results.append(result)
    
    return final_results