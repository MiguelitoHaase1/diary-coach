"""End-to-end integration tests for Session 2."""

import pytest
import os
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock

from src.interface.multi_agent_cli import MultiAgentCLI
from src.persistence.conversation_storage import ConversationStorage, Conversation


class DiaryCoachSystem:
    """Complete diary coach system for integration testing."""
    
    def __init__(self, cli, conversation_storage):
        self.cli = cli
        self.coach = cli.coach
        self.event_bus = cli.event_bus
        self.conversation_storage = conversation_storage
        self.running = True


@pytest.fixture
def temp_storage_dir():
    """Create temporary directory for conversation storage."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
async def mock_diary_coach_system(temp_storage_dir):
    """Create complete mocked diary coach system."""
    # Set environment to disable multi-agent for simpler testing
    os.environ["DISABLE_MULTI_AGENT"] = "true"
    
    # Create CLI which will create its own coach and event bus
    cli = MultiAgentCLI()
    
    # Mock the LLM service in the coach
    mock_llm = MagicMock()
    mock_llm.generate_response = AsyncMock(return_value="I hear you. Tell me more.")
    mock_llm.session_cost = 0.0
    mock_llm.total_cost = 0.0
    mock_llm.total_tokens = 0
    cli.coach.llm_service = mock_llm
    
    # Create conversation storage
    conversation_storage = ConversationStorage(base_path=temp_storage_dir)
    
    return DiaryCoachSystem(
        cli=cli,
        conversation_storage=conversation_storage
    )


@pytest.fixture
async def real_diary_coach_system(temp_storage_dir):
    """Create diary coach system with real API (requires API key)."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        pytest.skip("ANTHROPIC_API_KEY not set - skipping real API tests")
    
    # Set environment to disable multi-agent for simpler testing
    os.environ["DISABLE_MULTI_AGENT"] = "true"
    
    # Create CLI which will use real API
    cli = MultiAgentCLI()
    
    # Create conversation storage
    conversation_storage = ConversationStorage(base_path=temp_storage_dir)
    
    return DiaryCoachSystem(
        cli=cli,
        conversation_storage=conversation_storage
    )


class TestSession2EndToEnd:
    """End-to-end integration tests for Session 2 prototype."""

    @pytest.mark.asyncio
    async def test_complete_morning_conversation_flow(self, mock_diary_coach_system):
        """Test complete morning ritual conversation flow."""
        system = mock_diary_coach_system
        
        # Mock realistic morning conversation responses
        system.cli.coach.llm_service.generate_response.side_effect = [
            "Good morning Michael! What's the one challenge you're ready to tackle today that could shift everything?",
            "That sounds significant. What core value do you want to fight for today? Tell me a bit more about it.",
            "That's powerful. How does fighting for your integrity feel in your body right now?"
        ]
        
        # Test morning ritual
        response1 = await system.cli.process_input("good morning")
        assert "Good morning Michael!" in response1
        assert response1.count("?") == 1
        
        # Test challenge discussion
        response2 = await system.cli.process_input(
            "I need to have a difficult conversation with my team lead"
        )
        assert len(response2) < 300  # Concise response
        
        # Test value exploration
        response3 = await system.cli.process_input(
            "I want to fight for my integrity - being honest about my capacity"
        )
        
        # Verify conversation state tracking
        assert system.coach.conversation_state == "morning"
        assert system.coach.morning_challenge is not None
        assert system.coach.morning_value is not None
        
        # Verify message history
        assert len(system.coach.message_history) == 6  # 3 user + 3 assistant

    @pytest.mark.asyncio
    async def test_complete_evening_reflection_flow(self, mock_diary_coach_system):
        """Test complete evening ritual conversation flow."""
        system = mock_diary_coach_system
        
        # Mock conversation responses
        system.cli.coach.llm_service.generate_response.side_effect = [
            "Good morning Michael! What challenge are you ready to tackle today?",
            "That's meaningful. What core value do you want to fight for today?",
            "Good evening Michael! How did being more present with your family actually unfold today?",
            "That sounds like a real moment of connection. What did you learn about yourself?"
        ]
        
        # Simulate morning first
        await system.cli.process_input("good morning")
        await system.cli.process_input("I want to be more present with my family")
        
        # Evening reflection
        response = await system.cli.process_input("good evening")
        assert "Good evening Michael!" in response
        assert "present" in response.lower() or "family" in response.lower()
        
        # Should ask about specific moment
        assert "moment" in response.lower() or "unfold" in response.lower()

    @pytest.mark.asyncio
    async def test_conversation_persistence_integration(self, mock_diary_coach_system, temp_storage_dir):
        """Test conversation is automatically saved."""
        system = mock_diary_coach_system
        
        # Mock responses
        system.cli.coach.llm_service.generate_response.side_effect = [
            "Good morning Michael! What's your challenge today?",
            "That sounds important. What value drives that?"
        ]
        system.cli.coach.llm_service.session_cost = 0.0025
        system.cli.coach.llm_service.total_tokens = 150
        
        # Have a conversation
        await system.cli.process_input("good morning")
        await system.cli.process_input("I want to be more focused")
        
        # Create and save conversation manually (CLI doesn't auto-save yet)
        conversation = Conversation(
            session_id="test_session",
            started_at=datetime.now(),
            messages=system.coach.message_history,
            metadata={
                "total_tokens": system.cli.coach.llm_service.total_tokens,
                "total_cost": system.cli.coach.llm_service.session_cost,
                "morning_challenge": system.coach.morning_challenge
            }
        )
        
        filepath = await system.conversation_storage.save(conversation)
        
        # Verify conversation was saved
        assert filepath.exists()
        
        # Verify can load back
        loaded = await system.conversation_storage.load(filepath)
        assert len(loaded.messages) == 4  # 2 user + 2 assistant
        assert loaded.metadata["total_cost"] == 0.0025

    @pytest.mark.asyncio
    async def test_system_handles_api_errors_gracefully(self, mock_diary_coach_system):
        """Test system handles API errors without crashing."""
        system = mock_diary_coach_system
        
        # Mock API error
        system.cli.coach.llm_service.generate_response.side_effect = Exception("API Error: Rate limited")
        
        response = await system.cli.process_input("good morning")
        assert "error" in response.lower() or "try again" in response.lower()
        assert system.running  # System didn't crash

    @pytest.mark.asyncio
    async def test_coach_style_compliance(self, mock_diary_coach_system):
        """Test coach responses follow style guidelines."""
        system = mock_diary_coach_system
        
        # Mock responses that should follow style guide
        system.cli.coach.llm_service.generate_response.return_value = (
            "That's an interesting perspective. What feels most alive about that idea right now?"
        )
        
        response = await system.cli.process_input("I'm feeling stuck")
        
        # Style validation
        assert "•" not in response
        assert not response.strip().startswith("-")
        assert len(response.split("\n")) <= 6
        assert response.count("?") <= 1  # At most one question

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_real_api_morning_conversation(self, real_diary_coach_system):
        """Test morning conversation with real Anthropic API."""
        system = real_diary_coach_system
        
        # Test real morning conversation
        response = await system.cli.process_input("good morning")
        
        # Verify real API response characteristics
        assert "Good morning Michael!" in response
        assert len(response) > 10  # Should have substantial content
        assert response.count("?") >= 1  # Should ask a question
        
        # Verify cost tracking
        assert system.cli.coach.llm_service.session_cost > 0
        assert system.cli.coach.llm_service.total_tokens > 0
        
        print(f"Real API Response: {response}")
        print(f"Cost: ${system.cli.coach.llm_service.session_cost:.4f}")
        print(f"Tokens: {system.cli.coach.llm_service.total_tokens}")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_real_api_challenge_discussion(self, real_diary_coach_system):
        """Test challenge discussion with real API."""
        system = real_diary_coach_system
        
        # Start morning conversation
        await system.cli.process_input("good morning")
        
        # Discuss a real challenge
        response = await system.cli.process_input(
            "I'm struggling to maintain focus while working from home with constant distractions"
        )
        
        # Verify meaningful coaching response
        assert len(response) > 20
        assert response.count("?") <= 1  # Should follow question discipline
        
        # Should not be generic advice
        assert "focus" in response.lower() or "distraction" in response.lower()
        
        print(f"Challenge Response: {response}")

    @pytest.mark.asyncio
    async def test_system_component_integration(self, mock_diary_coach_system):
        """Test all system components work together."""
        system = mock_diary_coach_system
        
        # Verify all components are properly initialized
        assert system.cli.coach.llm_service is not None
        assert system.coach is not None
        assert system.cli is not None
        assert system.event_bus is not None
        assert system.conversation_storage is not None
        
        # Verify coach has LLM service
        assert system.coach.llm_service == system.cli.coach.llm_service
        
        # Verify CLI has coach
        assert system.cli.coach == system.coach
        
        # Test component interaction
        system.cli.coach.llm_service.generate_response.return_value = "Hello Michael!"
        response = await system.cli.process_input("test")
        assert response == "Hello Michael!"