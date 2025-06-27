"""Redis-based event bus implementation"""
import asyncio
import json
from typing import Dict, List, Callable, Any, Awaitable
from collections import defaultdict
import redis.asyncio as redis

# Type aliases (same as in-memory bus)
Event = Dict[str, Any]
EventHandler = Callable[[Event], Awaitable[None]]


class RedisEventBus:
    """Redis-based event bus with async pub/sub pattern"""
    
    def __init__(self, redis_client: redis.Redis):
        self._redis = redis_client
        self._channels: Dict[str, List[EventHandler]] = defaultdict(list)
        self._pubsub = None
        self._listener_task = None
        self._running = False
    
    async def subscribe(self, channel: str, handler: EventHandler) -> None:
        """Subscribe a handler to a channel"""
        # Add handler to local registry
        self._channels[channel].append(handler)
        
        # Start listener if this is the first subscription
        if not self._running:
            await self._start_listener()
        
        # Subscribe to Redis channel
        if self._pubsub is None:
            self._pubsub = self._redis.pubsub()
        
        await self._pubsub.subscribe(channel)
    
    async def publish(self, channel: str, event: Event) -> None:
        """Publish an event to a channel"""
        # Serialize event to JSON
        event_data = json.dumps(event)
        await self._redis.publish(channel, event_data)
    
    async def unsubscribe(self, channel: str, handler: EventHandler) -> None:
        """Remove a handler from a channel"""
        if channel in self._channels:
            try:
                self._channels[channel].remove(handler)
                # If no more handlers for this channel, unsubscribe from Redis
                if not self._channels[channel]:
                    del self._channels[channel]
                    if self._pubsub:
                        await self._pubsub.unsubscribe(channel)
            except ValueError:
                pass  # Handler not found, ignore
    
    async def close(self) -> None:
        """Close the event bus and clean up resources"""
        self._running = False
        
        # Cancel listener task
        if self._listener_task:
            self._listener_task.cancel()
            try:
                await self._listener_task
            except asyncio.CancelledError:
                pass
        
        # Close pubsub
        if self._pubsub:
            await self._pubsub.close()
        
        # Clear channels
        self._channels.clear()
    
    async def _start_listener(self) -> None:
        """Start the Redis message listener"""
        self._running = True
        self._listener_task = asyncio.create_task(self._listen_for_messages())
    
    async def _listen_for_messages(self) -> None:
        """Listen for messages from Redis and dispatch to handlers"""
        if not self._pubsub:
            return
        
        try:
            async for message in self._pubsub.listen():
                if not self._running:
                    break
                
                if message['type'] == 'message':
                    channel = message['channel'].decode('utf-8')
                    try:
                        # Deserialize event data
                        event_data = json.loads(message['data'].decode('utf-8'))
                        
                        # Dispatch to all handlers for this channel
                        if channel in self._channels:
                            tasks = []
                            for handler in self._channels[channel]:
                                task = asyncio.create_task(handler(event_data))
                                tasks.append(task)
                            
                            # Wait for all handlers to complete
                            if tasks:
                                await asyncio.gather(*tasks, return_exceptions=True)
                    
                    except (json.JSONDecodeError, Exception) as e:
                        # Log error but continue processing
                        print(f"Error processing message on channel {channel}: {e}")
                        continue
        
        except asyncio.CancelledError:
            # Expected when shutting down
            pass
        except Exception as e:
            print(f"Error in Redis listener: {e}")
    
    def get_channels(self) -> List[str]:
        """Get list of active channels (for debugging/testing)"""
        return list(self._channels.keys())
    
    def get_subscriber_count(self, channel: str) -> int:
        """Get number of subscribers for a channel (for debugging/testing)"""
        return len(self._channels.get(channel, []))