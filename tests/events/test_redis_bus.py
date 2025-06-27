import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from src.events.redis_bus import RedisEventBus
import redis.asyncio as redis


@pytest.fixture
async def mock_redis():
    """Create a mock Redis client for testing"""
    mock_client = AsyncMock()
    mock_pubsub = AsyncMock()
    
    # Mock pubsub methods
    mock_pubsub.subscribe = AsyncMock()
    mock_pubsub.unsubscribe = AsyncMock()
    mock_pubsub.close = AsyncMock()
    
    # Mock the listen method to return messages
    async def mock_listen():
        # Simulate receiving a message
        yield {
            'type': 'message',
            'channel': b'test_channel',
            'data': b'{"test": "data"}'
        }
    
    mock_pubsub.listen = AsyncMock(return_value=mock_listen())
    mock_client.pubsub = MagicMock(return_value=mock_pubsub)
    return mock_client


@pytest.mark.asyncio
async def test_redis_event_bus(mock_redis):
    """Redis bus should match in-memory bus interface"""
    bus = RedisEventBus(mock_redis)
    
    received = []
    
    async def handler(event):
        received.append(event)
    
    await bus.subscribe("test_channel", handler)
    
    # Simulate message received through listener
    await asyncio.sleep(0.1)  # Allow listener to start
    
    # Verify subscription was called
    mock_redis.pubsub.assert_called_once()
    
    await bus.close()


@pytest.mark.asyncio 
async def test_redis_bus_publish():
    """Test that publish calls Redis correctly"""
    mock_redis = AsyncMock()
    bus = RedisEventBus(mock_redis)
    
    await bus.publish("test_channel", {"test": "data"})
    
    # Verify Redis publish was called with JSON serialized data
    mock_redis.publish.assert_called_once_with("test_channel", '{"test": "data"}')
    
    await bus.close()


@pytest.mark.asyncio
async def test_redis_bus_close():
    """Test proper cleanup on close"""
    mock_redis = AsyncMock()
    mock_pubsub = AsyncMock()
    
    # Mock pubsub methods
    mock_pubsub.subscribe = AsyncMock()
    mock_pubsub.unsubscribe = AsyncMock()
    mock_pubsub.close = AsyncMock()
    mock_pubsub.listen = AsyncMock(return_value=iter([]))  # Empty iterator
    
    mock_redis.pubsub = MagicMock(return_value=mock_pubsub)
    
    bus = RedisEventBus(mock_redis)
    
    # Subscribe to start listener
    await bus.subscribe("test", lambda x: None)
    
    # Close should clean up resources
    await bus.close()
    
    assert not bus._running
    assert len(bus._channels) == 0