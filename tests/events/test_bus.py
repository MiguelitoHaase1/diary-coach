"""Test event bus implementation"""
import pytest
import asyncio
from src.events.bus import EventBus, Event


@pytest.mark.asyncio
async def test_event_bus_pub_sub():
    """Events published to a channel are received by subscribers"""
    bus = EventBus()
    received_events = []
    
    async def handler(event: Event):
        received_events.append(event)
    
    await bus.subscribe("coaching.goals", handler)
    await bus.publish("coaching.goals", {"type": "user_message", "content": "test"})
    
    # Allow event propagation
    await asyncio.sleep(0.1)
    
    assert len(received_events) == 1
    assert received_events[0]["content"] == "test"


@pytest.mark.asyncio
async def test_event_bus_multiple_subscribers():
    """Multiple subscribers can receive the same event"""
    bus = EventBus()
    received_1 = []
    received_2 = []
    
    async def handler_1(event: Event):
        received_1.append(event)
    
    async def handler_2(event: Event):
        received_2.append(event)
    
    await bus.subscribe("test.channel", handler_1)
    await bus.subscribe("test.channel", handler_2)
    await bus.publish("test.channel", {"message": "hello"})
    
    await asyncio.sleep(0.1)
    
    assert len(received_1) == 1
    assert len(received_2) == 1
    assert received_1[0]["message"] == "hello"
    assert received_2[0]["message"] == "hello"


@pytest.mark.asyncio
async def test_event_bus_different_channels():
    """Events are only delivered to subscribers of the correct channel"""
    bus = EventBus()
    channel_a_events = []
    channel_b_events = []
    
    async def handler_a(event: Event):
        channel_a_events.append(event)
    
    async def handler_b(event: Event):
        channel_b_events.append(event)
    
    await bus.subscribe("channel.a", handler_a)
    await bus.subscribe("channel.b", handler_b)
    
    await bus.publish("channel.a", {"data": "for_a"})
    await bus.publish("channel.b", {"data": "for_b"})
    
    await asyncio.sleep(0.1)
    
    assert len(channel_a_events) == 1
    assert len(channel_b_events) == 1
    assert channel_a_events[0]["data"] == "for_a"
    assert channel_b_events[0]["data"] == "for_b"