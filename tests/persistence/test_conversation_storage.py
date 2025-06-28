"""Tests for conversation storage."""

import pytest
import json
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
from src.persistence.conversation_storage import ConversationStorage, Conversation


class TestConversationStorage:
    """Test suite for ConversationStorage."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_path = Path(tempfile.mkdtemp())
        yield temp_path
        # Cleanup after test
        shutil.rmtree(temp_path)

    @pytest.fixture
    def storage(self, temp_dir):
        """Create a ConversationStorage instance with temp directory."""
        return ConversationStorage(base_path=temp_dir)

    @pytest.fixture
    def sample_conversation(self):
        """Create a sample conversation for testing."""
        return Conversation(
            session_id="test_123",
            started_at=datetime(2025, 1, 30, 9, 0, 0),
            ended_at=datetime(2025, 1, 30, 9, 15, 0),
            messages=[
                {"role": "user", "content": "good morning"},
                {"role": "assistant", "content": "Good morning Michael! What's your challenge today?"},
                {"role": "user", "content": "I want to be present"},
                {"role": "assistant", "content": "Being present sounds meaningful. What value drives that?"}
            ],
            metadata={
                "total_tokens": 245,
                "total_cost": 0.0023,
                "duration_seconds": 45,
                "morning_challenge": "being more present",
                "conversation_quality_score": 0.85
            }
        )

    @pytest.mark.asyncio
    async def test_saves_conversation_to_json(self, storage, sample_conversation, temp_dir):
        """Test saving conversation creates JSON file."""
        filepath = await storage.save(sample_conversation)
        
        # Verify file exists
        assert filepath.exists()
        assert filepath.suffix == ".json"
        
        # Verify content
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        assert data["session_id"] == "test_123"
        assert len(data["messages"]) == 4
        assert data["metadata"]["total_tokens"] == 245
        assert data["metadata"]["total_cost"] == 0.0023

    @pytest.mark.asyncio
    async def test_load_conversation_from_json(self, storage, sample_conversation):
        """Test loading conversation from JSON file."""
        # Save first
        filepath = await storage.save(sample_conversation)
        
        # Load back
        loaded = await storage.load(filepath)
        
        assert loaded.session_id == sample_conversation.session_id
        assert len(loaded.messages) == len(sample_conversation.messages)
        assert loaded.metadata["total_tokens"] == sample_conversation.metadata["total_tokens"]
        assert loaded.started_at == sample_conversation.started_at

    @pytest.mark.asyncio
    async def test_storage_creates_daily_folders(self, storage, sample_conversation, temp_dir):
        """Test storage creates date-based folder structure."""
        filepath = await storage.save(sample_conversation)
        
        # Should create date-based folders (2025-01-30 from sample data)
        assert "2025-01-30" in str(filepath)
        assert filepath.name.startswith("conversation_")
        
        # Verify folder structure
        date_folder = temp_dir / "2025-01-30"
        assert date_folder.exists()
        assert date_folder.is_dir()

    @pytest.mark.asyncio
    async def test_load_latest_conversation(self, storage, temp_dir):
        """Test loading the most recent conversation."""
        # Create multiple conversations with different timestamps
        conv1 = Conversation(
            session_id="conv1",
            started_at=datetime(2025, 1, 30, 9, 0, 0),
            messages=[{"role": "user", "content": "first"}],
            metadata={"order": 1}
        )
        
        conv2 = Conversation(
            session_id="conv2", 
            started_at=datetime(2025, 1, 30, 10, 0, 0),
            messages=[{"role": "user", "content": "second"}],
            metadata={"order": 2}
        )
        
        conv3 = Conversation(
            session_id="conv3",
            started_at=datetime(2025, 1, 30, 11, 0, 0),
            messages=[{"role": "user", "content": "third"}],
            metadata={"order": 3}
        )
        
        # Save in random order
        await storage.save(conv2)
        await storage.save(conv1)
        await storage.save(conv3)
        
        # Load latest should return conv3
        latest = await storage.load_latest()
        assert latest.session_id == "conv3"
        assert latest.metadata["order"] == 3

    @pytest.mark.asyncio
    async def test_conversation_filename_format(self, storage, sample_conversation):
        """Test conversation filename follows expected format."""
        filepath = await storage.save(sample_conversation)
        
        # Should be: conversation_YYYYMMDD_HHMMSS.json
        filename = filepath.name
        assert filename.startswith("conversation_")
        assert filename.endswith(".json")
        
        # Extract timestamp part
        timestamp_part = filename.replace("conversation_", "").replace(".json", "")
        # Should be parseable as datetime format
        datetime.strptime(timestamp_part, "%Y%m%d_%H%M%S")

    @pytest.mark.asyncio
    async def test_handles_missing_directory(self, temp_dir):
        """Test storage creates missing directories."""
        # Create storage with non-existent subdirectory
        storage_path = temp_dir / "nonexistent" / "conversations"
        storage = ConversationStorage(base_path=storage_path)
        
        conversation = Conversation(
            session_id="test",
            started_at=datetime.now(),
            messages=[{"role": "user", "content": "test"}],
            metadata={}
        )
        
        # Should create directories and save successfully
        filepath = await storage.save(conversation)
        assert filepath.exists()

    @pytest.mark.asyncio
    async def test_conversation_serialization_completeness(self, storage, sample_conversation):
        """Test all conversation fields are preserved during save/load."""
        filepath = await storage.save(sample_conversation)
        loaded = await storage.load(filepath)
        
        # Verify all fields match
        assert loaded.session_id == sample_conversation.session_id
        assert loaded.started_at == sample_conversation.started_at
        assert loaded.ended_at == sample_conversation.ended_at
        assert loaded.messages == sample_conversation.messages
        assert loaded.metadata == sample_conversation.metadata