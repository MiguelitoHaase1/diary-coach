"""Test Memory Agent functionality."""

import pytest
import json
import os
import tempfile

from src.agents.memory_agent import MemoryAgent
from src.agents.base import AgentRequest


@pytest.fixture
def temp_conversations_dir():
    """Create a temporary directory with test conversations."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test conversation 1
        conv1 = {
            "conversation_id": "test_conv_1",
            "timestamp": "2024-01-15T09:00:00",
            "messages": [
                {
                    "type": "user",
                    "content": "I'm struggling with productivity lately",
                    "timestamp": "2024-01-15T09:00:00"
                },
                {
                    "type": "agent",
                    "content": "Tell me more about what productivity means to you",
                    "timestamp": "2024-01-15T09:00:30"
                },
                {
                    "type": "user",
                    "content": "I feel overwhelmed by all my tasks",
                    "timestamp": "2024-01-15T09:01:00"
                }
            ]
        }

        # Create test conversation 2
        conv2 = {
            "conversation_id": "test_conv_2",
            "timestamp": "2024-01-16T08:30:00",
            "messages": [
                {
                    "type": "user",
                    "content": "Good morning! I want to focus on clarity today",
                    "timestamp": "2024-01-16T08:30:00"
                },
                {
                    "type": "agent",
                    "content": "What does clarity mean in your context?",
                    "timestamp": "2024-01-16T08:30:30"
                },
                {
                    "type": "user",
                    "content": "Having a clear vision of my goals and values",
                    "timestamp": "2024-01-16T08:31:00"
                }
            ]
        }

        # Create test conversation 3
        conv3 = {
            "conversation_id": "test_conv_3",
            "timestamp": "2024-01-17T10:00:00",
            "messages": [
                {
                    "type": "user",
                    "content": "I believe growth is my core value",
                    "timestamp": "2024-01-17T10:00:00"
                },
                {
                    "type": "agent",
                    "content": "How do you embody growth in your daily life?",
                    "timestamp": "2024-01-17T10:00:30"
                }
            ]
        }

        # Write conversations to files
        for i, conv in enumerate([conv1, conv2, conv3], 1):
            filepath = os.path.join(temp_dir, f"conversation_{i}.json")
            with open(filepath, 'w') as f:
                json.dump(conv, f)

        yield temp_dir


@pytest.mark.asyncio
async def test_memory_agent_initialization(temp_conversations_dir):
    """Test that Memory Agent initializes and loads conversations."""
    agent = MemoryAgent(conversations_dir=temp_conversations_dir)

    # Should not be initialized yet
    assert not agent.is_initialized

    # Initialize
    await agent.initialize()

    # Should be initialized with loaded conversations
    assert agent.is_initialized
    assert len(agent.conversations_cache) == 3
    assert len(agent.patterns_cache) > 0


@pytest.mark.asyncio
async def test_memory_agent_loads_conversations(temp_conversations_dir):
    """Test conversation loading functionality."""
    agent = MemoryAgent(conversations_dir=temp_conversations_dir)
    await agent.initialize()

    # Check conversations are loaded and sorted
    assert agent.conversations_cache[0]["conversation_id"] == "test_conv_3"
    assert agent.conversations_cache[1]["conversation_id"] == "test_conv_2"
    assert agent.conversations_cache[2]["conversation_id"] == "test_conv_1"


@pytest.mark.asyncio
async def test_memory_agent_extracts_patterns(temp_conversations_dir):
    """Test pattern extraction from conversations."""
    agent = MemoryAgent(conversations_dir=temp_conversations_dir)
    await agent.initialize()

    patterns = agent.patterns_cache

    # Check challenges extracted
    assert "productivity" in patterns["challenges"]
    assert "overwhelmed" in patterns["emotions"]

    # Check values extracted
    assert "value" in patterns["values"]
    assert "growth" in patterns["values"]

    # Check topics extracted
    assert len(patterns["topics"]) > 0


@pytest.mark.asyncio
async def test_memory_agent_finds_specific_memory(temp_conversations_dir):
    """Test finding specific memories."""
    agent = MemoryAgent(conversations_dir=temp_conversations_dir)
    await agent.initialize()

    request = AgentRequest(
        from_agent="coach",
        to_agent="memory",
        query="remember when we discussed productivity",
        context={}
    )

    response = await agent.handle_request(request)
    result = json.loads(response.content)

    assert result["total_found"] > 0
    assert result["results"][0]["conversation_id"] == "test_conv_1"
    assert any(
        "productivity" in msg["content"].lower()
        for msg in result["results"][0]["matching_messages"]
    )


@pytest.mark.asyncio
async def test_memory_agent_search_conversations(temp_conversations_dir):
    """Test general conversation search."""
    agent = MemoryAgent(conversations_dir=temp_conversations_dir)
    await agent.initialize()

    request = AgentRequest(
        from_agent="coach",
        to_agent="memory",
        query="clarity goals values",
        context={}
    )

    response = await agent.handle_request(request)
    result = json.loads(response.content)

    assert result["total_found"] > 0
    # Should find conversation 2 which mentions all three terms
    found_conv2 = any(
        r["conversation_id"] == "test_conv_2"
        for r in result["results"]
    )
    assert found_conv2


@pytest.mark.asyncio
async def test_memory_agent_get_patterns(temp_conversations_dir):
    """Test getting conversation patterns."""
    agent = MemoryAgent(conversations_dir=temp_conversations_dir)
    await agent.initialize()

    request = AgentRequest(
        from_agent="coach",
        to_agent="memory",
        query="What are the common patterns in our conversations?",
        context={}
    )

    response = await agent.handle_request(request)
    result = json.loads(response.content)

    assert "patterns" in result
    assert "summary" in result
    assert result["summary"]["total_conversations"] == 3


@pytest.mark.asyncio
async def test_memory_agent_get_summary(temp_conversations_dir):
    """Test getting conversation summary."""
    agent = MemoryAgent(conversations_dir=temp_conversations_dir)
    await agent.initialize()

    request = AgentRequest(
        from_agent="coach",
        to_agent="memory",
        query="Give me a summary of our conversation history",
        context={}
    )

    response = await agent.handle_request(request)
    result = json.loads(response.content)

    assert result["total_conversations"] == 3
    assert result["total_messages"] == 8  # Total messages across all convs
    assert "date_range" in result
    assert result["date_range"]["earliest"] == "2024-01-15T09:00:00"
    assert result["date_range"]["latest"] == "2024-01-17T10:00:00"


@pytest.mark.asyncio
async def test_memory_agent_empty_directory():
    """Test Memory Agent with empty conversations directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        agent = MemoryAgent(conversations_dir=temp_dir)
        await agent.initialize()

        assert agent.is_initialized
        assert len(agent.conversations_cache) == 0

        request = AgentRequest(
            from_agent="coach",
            to_agent="memory",
            query="remember anything?",
            context={}
        )

        response = await agent.handle_request(request)
        result = json.loads(response.content)

        assert result["total_found"] == 0


@pytest.mark.asyncio
async def test_memory_agent_handles_malformed_files(temp_conversations_dir):
    """Test that Memory Agent handles malformed JSON files gracefully."""
    # Add a malformed file
    malformed_path = os.path.join(
        temp_conversations_dir,
        "malformed.json"
    )
    with open(malformed_path, 'w') as f:
        f.write("not valid json{")

    agent = MemoryAgent(conversations_dir=temp_conversations_dir)
    await agent.initialize()

    # Should still load the valid conversations
    assert len(agent.conversations_cache) == 3
    assert agent.is_initialized


@pytest.mark.asyncio
async def test_memory_agent_error_handling():
    """Test error handling in Memory Agent."""
    agent = MemoryAgent(conversations_dir="/non/existent/path")
    await agent.initialize()

    request = AgentRequest(
        from_agent="coach",
        to_agent="memory",
        query="test query",
        context={}
    )

    response = await agent.handle_request(request)

    # Should handle gracefully
    assert response.agent_name == "memory"
    assert not response.error  # No error because directory doesn't exist is ok
