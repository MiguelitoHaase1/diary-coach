"""In-memory event bus implementation using asyncio"""
import asyncio
from typing import Dict, List, Callable, Any, Awaitable
from collections import defaultdict

# Type aliases
Event = Dict[str, Any]
EventHandler = Callable[[Event], Awaitable[None]]


class EventBus:
    """In-memory event bus with async pub/sub pattern"""
    
    def __init__(self):
        self._channels: Dict[str, List[EventHandler]] = defaultdict(list)
        self._running = True
    
    async def subscribe(self, channel: str, handler: EventHandler) -> None:
        """Subscribe a handler to a channel"""
        self._channels[channel].append(handler)
    
    async def publish(self, channel: str, event: Event) -> None:
        """Publish an event to a channel"""
        if channel in self._channels:
            # Create tasks for all handlers to run concurrently
            tasks = []
            for handler in self._channels[channel]:
                task = asyncio.create_task(handler(event))
                tasks.append(task)
            
            # Wait for all handlers to complete
            if tasks:
                await asyncio.gather(*tasks)
    
    async def unsubscribe(self, channel: str, handler: EventHandler) -> None:
        """Remove a handler from a channel"""
        if channel in self._channels:
            try:
                self._channels[channel].remove(handler)
                # Clean up empty channel lists
                if not self._channels[channel]:
                    del self._channels[channel]
            except ValueError:
                pass  # Handler not found, ignore
    
    async def close(self) -> None:
        """Close the event bus and clean up resources"""
        self._running = False
        self._channels.clear()
    
    def get_channels(self) -> List[str]:
        """Get list of active channels (for debugging/testing)"""
        return list(self._channels.keys())
    
    def get_subscriber_count(self, channel: str) -> int:
        """Get number of subscribers for a channel (for debugging/testing)"""
        return len(self._channels.get(channel, []))