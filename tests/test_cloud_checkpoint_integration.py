"""Test cloud checkpoint integration for Session 6.5."""

import pytest
from datetime import datetime
from typing import Dict, Any

from src.orchestration.context_state import ContextState
from src.orchestration.checkpoint_manager import CloudCheckpointManager


@pytest.mark.asyncio
async def test_conversation_memory_persistence():
    """Should remember previous conversations via checkpoints."""
    
    manager = CloudCheckpointManager()
    
    # First conversation
    thread_id = "user-123"
    state_1 = ContextState(
        messages=[{"type": "user", "content": "I'm struggling with delegation", "timestamp": datetime.now().isoformat()}],
        conversation_id="conv-1"
    )
    
    # Save state to checkpoint
    await manager.save_checkpoint(thread_id, state_1)
    
    # Second conversation should have access to history
    loaded_state = await manager.load_checkpoint(thread_id)
    
    assert loaded_state is not None
    assert len(loaded_state.conversation_history) > 0
    assert "delegation" in str(loaded_state.conversation_history)


@pytest.mark.asyncio
async def test_conversation_history_summarization():
    """Should summarize long conversation histories for efficient storage."""
    
    manager = CloudCheckpointManager()
    
    # Create a long conversation history
    long_messages = []
    for i in range(60):  # More than max_history_length (50)
        long_messages.append({
            "type": "user" if i % 2 == 0 else "assistant",
            "content": f"Message {i} about various topics and important insights",
            "timestamp": datetime.now().isoformat()
        })
    
    state = ContextState(
        messages=long_messages,
        conversation_id="conv-long"
    )
    
    # Process for summarization
    summarized_state = await manager.summarize_for_checkpoint(state)
    
    # Should have conversation history summary
    assert summarized_state.conversation_history is not None
    assert len(summarized_state.conversation_history) > 0
    
    # Should track summarization
    assert "summarized_messages" in summarized_state.context_usage
    assert summarized_state.context_usage["summarized_messages"] == 60


@pytest.mark.asyncio
async def test_memory_relevance_scoring():
    """Should score relevance of conversation memories."""
    
    manager = CloudCheckpointManager()
    
    # Create conversation history with different topics
    memories = [
        {"date": "2024-12-15", "topic": "delegation", "insights": "Need better systems for task handoff"},
        {"date": "2024-12-10", "topic": "prioritization", "insights": "Focus on impact over urgency"},
        {"date": "2024-12-05", "topic": "team communication", "insights": "Weekly check-ins improve clarity"}
    ]
    
    # Test relevance scoring
    query = "How can I improve my delegation skills?"
    relevant_memories = await manager.score_memory_relevance(memories, query)
    
    # Delegation should be most relevant
    assert len(relevant_memories) > 0
    assert relevant_memories[0]["topic"] == "delegation"
    assert "relevance_score" in relevant_memories[0]
    assert relevant_memories[0]["relevance_score"] > 0.3  # More realistic threshold


@pytest.mark.asyncio
async def test_privacy_controls():
    """Should handle sensitive topics with privacy controls."""
    
    manager = CloudCheckpointManager(privacy_mode=True)
    
    # Conversation with sensitive content
    state = ContextState(
        messages=[
            {"type": "user", "content": "I'm having personal issues with my manager", "timestamp": datetime.now().isoformat()},
            {"type": "assistant", "content": "That sounds challenging. What specific behaviors are concerning?", "timestamp": datetime.now().isoformat()}
        ],
        conversation_id="conv-sensitive"
    )
    
    # Should detect and handle sensitive content
    processed_state = await manager.apply_privacy_controls(state)
    
    # Should flag sensitive content
    assert "privacy_applied" in processed_state.context_usage
    assert processed_state.context_usage["privacy_applied"] == True
    
    # Should have anonymized or filtered content
    assert "sensitive_topics_detected" in processed_state.context_usage


@pytest.mark.asyncio
async def test_checkpoint_versioning():
    """Should handle checkpoint versioning and cleanup."""
    
    manager = CloudCheckpointManager()
    thread_id = "user-456"
    
    # Save multiple versions
    for i in range(5):
        state = ContextState(
            messages=[{"type": "user", "content": f"Message {i}", "timestamp": datetime.now().isoformat()}],
            conversation_id=f"conv-{i}"
        )
        await manager.save_checkpoint(thread_id, state, version=i)
    
    # Should track versions
    versions = await manager.list_checkpoint_versions(thread_id)
    assert len(versions) == 5
    
    # Should be able to load specific version
    version_2_state = await manager.load_checkpoint(thread_id, version=2)
    assert "Message 2" in str(version_2_state.messages)
    
    # Should clean up old versions
    await manager.cleanup_old_checkpoints(thread_id, keep_latest=3)
    versions_after_cleanup = await manager.list_checkpoint_versions(thread_id)
    assert len(versions_after_cleanup) == 3


@pytest.mark.asyncio
async def test_graph_integration():
    """Should integrate seamlessly with LangGraph execution."""
    
    from src.orchestration.context_graph import create_context_aware_graph
    
    # Create graph with checkpoint manager
    manager = CloudCheckpointManager()
    graph = create_context_aware_graph()
    
    # First conversation
    thread_config = {"configurable": {"thread_id": "user-789"}}
    result_1 = await graph.ainvoke({
        "messages": [{"type": "user", "content": "What are my priorities today?", "timestamp": datetime.now().isoformat()}],
        "conversation_id": "conv-first"
    }, thread_config)
    
    # Create state from result for checkpoint
    checkpoint_state = ContextState(
        messages=[{"type": "user", "content": "What are my priorities today?", "timestamp": datetime.now().isoformat()}],
        conversation_id="conv-first",
        coach_response=result_1.get("coach_response", "")
    )
    
    # Save checkpoint
    await manager.save_checkpoint("user-789", checkpoint_state)
    
    # Second conversation should have memory
    loaded_state = await manager.load_checkpoint("user-789")
    result_2 = await graph.ainvoke({
        "messages": [{"type": "user", "content": "Remember what we discussed yesterday?", "timestamp": datetime.now().isoformat()}],
        "conversation_id": "conv-second",
        "conversation_history": loaded_state.conversation_history if loaded_state else None
    }, thread_config)
    
    # Should have access to previous conversation context (memory was used in scoring)
    assert "memory" in result_2.get("context_usage", {}).get("context_sources_used", [])


@pytest.mark.asyncio
async def test_performance_optimization():
    """Should handle checkpoint operations efficiently."""
    
    manager = CloudCheckpointManager()
    
    # Large state object
    large_state = ContextState(
        messages=[{"type": "user", "content": "x" * 1000, "timestamp": datetime.now().isoformat()} for _ in range(100)],
        todo_context=[{"id": str(i), "content": "Task " + "x" * 100} for i in range(20)],
        conversation_id="conv-large"
    )
    
    # Should complete operations within performance threshold
    start_time = datetime.now()
    await manager.save_checkpoint("perf-test", large_state)
    save_duration = (datetime.now() - start_time).total_seconds()
    
    start_time = datetime.now()
    loaded_state = await manager.load_checkpoint("perf-test")
    load_duration = (datetime.now() - start_time).total_seconds()
    
    # Should be fast enough for real-time use
    assert save_duration < 1.0  # Under 1 second
    assert load_duration < 0.5  # Under 500ms
    assert loaded_state is not None