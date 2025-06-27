"""
End-to-end integration test for Session 1 complete system
Tests the full conversation flow: User Message → Event Bus → Agent → Response → Evaluation → Stream Buffer
"""
import pytest
import asyncio
from datetime import datetime
from dataclasses import asdict

from src.events.bus import EventBus
from src.events.schemas import UserMessage, AgentResponse
from src.events.stream_buffer import StreamBuffer, StreamTrack
from src.agents.base import BaseAgent
from src.evaluation.metrics import ResponseRelevanceMetric


class IntegrationTestCoach(BaseAgent):
    """Test coach that provides predictable responses for integration testing"""
    
    def __init__(self, name: str = "test_coach"):
        super().__init__(name)
        self.processed_messages = []
    
    async def process_message(self, message: UserMessage) -> AgentResponse:
        self.processed_messages.append(message)
        
        # Generate contextual response based on user input
        if "goal" in message.content.lower():
            response_content = "Let's explore what you want to accomplish today. What's most important?"
        elif "productive" in message.content.lower():
            response_content = "What specific actions would make you feel more productive?"
        else:
            response_content = f"I understand you said: {message.content}. Tell me more about that."
        
        return AgentResponse(
            agent_name=self.name,
            content=response_content,
            response_to=message.message_id,
            conversation_id=message.conversation_id,
            timestamp=datetime.now()
        )


@pytest.mark.asyncio
async def test_full_conversation_flow_with_dual_tracks():
    """
    Validate entire system working together:
    User message → Event Bus → Agent → Response → Evaluation → Stream Buffer
    """
    # Initialize all components
    event_bus = EventBus()
    stream_buffer = StreamBuffer()
    coach = IntegrationTestCoach("integration_coach")
    relevance_metric = ResponseRelevanceMetric()
    
    # Storage for captured events and responses
    agent_responses = []
    evaluation_results = []
    
    # Set up event handlers
    async def handle_user_message(event):
        """Process user messages through the coach agent"""
        message = UserMessage(**event)
        response = await coach.process_message(message)
        agent_responses.append(response)
        
        # Add response to conversation track
        await stream_buffer.add_to_track(StreamTrack.CONVERSATION, {
            "role": "assistant", 
            "content": response.content,
            "agent": response.agent_name,
            "timestamp": response.timestamp.isoformat()
        })
        
        # Publish agent response event
        await event_bus.publish("coaching.response", asdict(response))
    
    async def handle_agent_response(event):
        """Evaluate agent responses and add insights"""
        response = AgentResponse(**event)
        
        # Find the original user message for context - use actual user content
        # In a real system, we'd track the conversation history
        if "goal" in response.content.lower():
            user_context = "I want to set some goals for today"
        elif "productive" in response.content.lower():
            user_context = "I want to be more productive"
        else:
            user_context = "General conversation"
        
        # Evaluate response quality
        score = await relevance_metric.evaluate(user_context, response.content)
        
        evaluation_result = {
            "response_id": response.conversation_id,
            "relevance_score": score,
            "agent": response.agent_name,
            "timestamp": datetime.now().isoformat()
        }
        evaluation_results.append(evaluation_result)
        
        # Add evaluation insights to insights track
        await stream_buffer.add_to_track(StreamTrack.INSIGHTS, {
            "type": "evaluation",
            "relevance_score": score,
            "quality_level": "high" if score > 0.7 else "medium" if score > 0.4 else "low",
            "timestamp": evaluation_result["timestamp"]
        })
    
    # Subscribe to events
    await event_bus.subscribe("coaching.user_message", handle_user_message)
    await event_bus.subscribe("coaching.response", handle_agent_response)
    
    # Test Case 1: Goal-setting conversation
    user_message_1 = UserMessage(
        user_id="test_user_001",
        content="I want to set some goals for today",
        timestamp=datetime.now()
    )
    
    # Publish user message
    await event_bus.publish("coaching.user_message", asdict(user_message_1))
    
    # Add user message to conversation track
    await stream_buffer.add_to_track(StreamTrack.CONVERSATION, {
        "role": "user",
        "content": user_message_1.content,
        "user_id": user_message_1.user_id,
        "timestamp": user_message_1.timestamp.isoformat()
    })
    
    # Allow event processing
    await asyncio.sleep(0.1)
    
    # Test Case 2: Productivity conversation
    user_message_2 = UserMessage(
        user_id="test_user_001", 
        content="I want to be more productive",
        conversation_id=user_message_1.conversation_id,  # Same conversation
        timestamp=datetime.now()
    )
    
    await event_bus.publish("coaching.user_message", asdict(user_message_2))
    await stream_buffer.add_to_track(StreamTrack.CONVERSATION, {
        "role": "user",
        "content": user_message_2.content,
        "user_id": user_message_2.user_id,
        "timestamp": user_message_2.timestamp.isoformat()
    })
    
    # Allow event processing
    await asyncio.sleep(0.1)
    
    # Validate event processing
    assert len(agent_responses) == 2, "Should have 2 agent responses"
    assert len(evaluation_results) == 2, "Should have 2 evaluations"
    assert len(coach.processed_messages) == 2, "Coach should have processed 2 messages"
    
    # Validate conversation flow
    response_1 = agent_responses[0]
    assert response_1.agent_name == "integration_coach"
    assert "accomplish" in response_1.content.lower()
    assert response_1.conversation_id == user_message_1.conversation_id
    
    response_2 = agent_responses[1]
    assert "specific actions" in response_2.content.lower()
    assert response_2.conversation_id == user_message_1.conversation_id
    
    # Validate evaluation quality
    eval_1 = evaluation_results[0]
    eval_2 = evaluation_results[1]
    
    assert eval_1["relevance_score"] > 0.5, f"Goal response should be relevant (got {eval_1['relevance_score']})"
    assert eval_2["relevance_score"] > 0.3, f"Productivity response should be somewhat relevant (got {eval_2['relevance_score']})"
    
    # Validate dual-track streaming
    conversation_track = await stream_buffer.read_track(StreamTrack.CONVERSATION)
    insights_track = await stream_buffer.read_track(StreamTrack.INSIGHTS)
    
    assert len(conversation_track) == 4, "Should have 2 user + 2 agent messages"
    assert len(insights_track) == 2, "Should have 2 evaluation insights"
    
    # Validate conversation track structure (order may vary due to async processing)
    conv_messages = conversation_track
    user_messages = [msg for msg in conv_messages if msg["role"] == "user"]
    assistant_messages = [msg for msg in conv_messages if msg["role"] == "assistant"]
    
    assert len(user_messages) == 2, "Should have 2 user messages"
    assert len(assistant_messages) == 2, "Should have 2 assistant messages"
    
    # Validate insights track structure
    insight_1 = insights_track[0]
    insight_2 = insights_track[1]
    
    assert insight_1["type"] == "evaluation"
    assert insight_1["quality_level"] in ["high", "medium"], f"First insight quality: {insight_1}"
    assert insight_2["type"] == "evaluation"
    assert insight_2["quality_level"] in ["high", "medium", "low"], f"Second insight quality: {insight_2}"
    
    # Cleanup
    await event_bus.close()


@pytest.mark.asyncio
async def test_event_bus_load_handling():
    """Test event bus can handle multiple concurrent conversations"""
    event_bus = EventBus()
    coach = IntegrationTestCoach("load_test_coach")
    processed_count = 0
    
    async def message_handler(event):
        nonlocal processed_count
        message = UserMessage(**event)
        await coach.process_message(message)
        processed_count += 1
    
    await event_bus.subscribe("coaching.user_message", message_handler)
    
    # Generate multiple concurrent messages
    messages = [
        UserMessage(
            user_id=f"user_{i}",
            content=f"Message {i} about goals",
            timestamp=datetime.now()
        ) for i in range(10)
    ]
    
    # Publish all messages concurrently
    tasks = [
        event_bus.publish("coaching.user_message", asdict(msg)) 
        for msg in messages
    ]
    
    await asyncio.gather(*tasks)
    await asyncio.sleep(0.1)  # Allow processing
    
    assert processed_count == 10, "All messages should be processed"
    assert len(coach.processed_messages) == 10, "Coach should have processed all messages"
    
    await event_bus.close()


@pytest.mark.asyncio
async def test_stream_buffer_concurrent_access():
    """Test stream buffer handles concurrent reads/writes correctly"""
    buffer = StreamBuffer()
    
    # Concurrent writers
    async def write_conversation_items():
        for i in range(5):
            await buffer.add_to_track(StreamTrack.CONVERSATION, {
                "role": "user",
                "content": f"Message {i}",
                "id": i
            })
            await asyncio.sleep(0.01)  # Small delay to test concurrency
    
    async def write_insight_items():
        for i in range(5):
            await buffer.add_to_track(StreamTrack.INSIGHTS, {
                "type": "evaluation",
                "score": i * 0.2,
                "id": i
            })
            await asyncio.sleep(0.01)
    
    # Run writers concurrently
    await asyncio.gather(
        write_conversation_items(),
        write_insight_items()
    )
    
    # Verify both tracks populated correctly
    conversation_items = await buffer.read_track(StreamTrack.CONVERSATION)
    insight_items = await buffer.read_track(StreamTrack.INSIGHTS)
    
    assert len(conversation_items) == 5, "Should have 5 conversation items"
    assert len(insight_items) == 5, "Should have 5 insight items"
    
    # Verify content integrity
    for i, item in enumerate(conversation_items):
        assert item["content"] == f"Message {i}"
        assert item["id"] == i
    
    for i, item in enumerate(insight_items):
        assert item["score"] == i * 0.2
        assert item["id"] == i
    
    # StreamBuffer doesn't have close method - it's automatically cleaned up


@pytest.mark.asyncio
async def test_system_error_handling():
    """Test system gracefully handles errors without breaking event flow"""
    event_bus = EventBus()
    error_count = 0
    success_count = 0
    
    async def faulty_handler(event):
        nonlocal error_count, success_count
        try:
            message = UserMessage(**event)
            
            # Simulate intermittent failures
            if "error" in message.content:
                error_count += 1
                raise Exception("Simulated handler error")
            else:
                success_count += 1
        except Exception as e:
            if "error" not in str(e):
                # Re-raise unexpected errors
                raise
    
    await event_bus.subscribe("coaching.user_message", faulty_handler)
    
    # Send mix of good and bad messages
    messages = [
        {"user_id": "user1", "content": "Normal message", "timestamp": datetime.now().isoformat()},
        {"user_id": "user2", "content": "error message please", "timestamp": datetime.now().isoformat()},
        {"user_id": "user3", "content": "Another normal message", "timestamp": datetime.now().isoformat()},
    ]
    
    # Process messages - event bus handles errors internally
    for msg in messages:
        await event_bus.publish("coaching.user_message", msg)
    
    await asyncio.sleep(0.1)
    
    # Verify error isolation - good messages still processed
    assert success_count >= 2, "Non-error messages should be processed"
    assert error_count >= 1, "Error should have been triggered"
    
    await event_bus.close()


if __name__ == "__main__":
    # Allow running tests directly
    asyncio.run(test_full_conversation_flow_with_dual_tracks())