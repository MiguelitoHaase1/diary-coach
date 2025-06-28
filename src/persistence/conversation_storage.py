"""Conversation storage with JSON persistence."""

import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class Conversation:
    """Conversation data model for persistence."""
    session_id: str
    started_at: datetime
    messages: List[Dict[str, str]]
    metadata: Dict[str, Any]
    ended_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert conversation to dictionary for JSON serialization."""
        data = asdict(self)
        # Convert datetime objects to ISO strings
        data["started_at"] = self.started_at.isoformat()
        if self.ended_at:
            data["ended_at"] = self.ended_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Conversation":
        """Create conversation from dictionary (JSON deserialization)."""
        # Parse datetime strings back to datetime objects
        started_at = datetime.fromisoformat(data["started_at"])
        ended_at = None
        if data.get("ended_at"):
            ended_at = datetime.fromisoformat(data["ended_at"])
        
        return cls(
            session_id=data["session_id"],
            started_at=started_at,
            ended_at=ended_at,
            messages=data["messages"],
            metadata=data["metadata"]
        )


class ConversationStorage:
    """JSON-based conversation storage with date-based folder organization."""
    
    def __init__(self, base_path: Path = None):
        """Initialize conversation storage.
        
        Args:
            base_path: Base directory for conversation storage
        """
        if base_path is None:
            base_path = Path.cwd() / "conversations"
        
        self.base_path = Path(base_path)
    
    async def save(self, conversation: Conversation) -> Path:
        """Save conversation to JSON file.
        
        Args:
            conversation: The conversation to save
            
        Returns:
            Path to the saved file
        """
        # Create date-based folder structure
        date_str = conversation.started_at.strftime("%Y-%m-%d")
        date_folder = self.base_path / date_str
        
        # Create directories if they don't exist
        date_folder.mkdir(parents=True, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp_str = conversation.started_at.strftime("%Y%m%d_%H%M%S")
        filename = f"conversation_{timestamp_str}.json"
        filepath = date_folder / filename
        
        # Save to JSON file
        conversation_data = conversation.to_dict()
        
        def write_file():
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(conversation_data, f, indent=2, ensure_ascii=False)
        
        # Run file I/O in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, write_file)
        
        return filepath
    
    async def load(self, filepath: Path) -> Conversation:
        """Load conversation from JSON file.
        
        Args:
            filepath: Path to the conversation file
            
        Returns:
            Loaded conversation object
        """
        def read_file():
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Run file I/O in thread pool
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, read_file)
        
        return Conversation.from_dict(data)
    
    async def load_latest(self) -> Optional[Conversation]:
        """Load the most recent conversation.
        
        Returns:
            Latest conversation, or None if no conversations exist
        """
        if not self.base_path.exists():
            return None
        
        # Find all conversation files
        all_files = []
        for date_folder in self.base_path.iterdir():
            if date_folder.is_dir():
                for conv_file in date_folder.glob("conversation_*.json"):
                    all_files.append(conv_file)
        
        if not all_files:
            return None
        
        # Sort by modification time (most recent first)
        all_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        latest_file = all_files[0]
        
        return await self.load(latest_file)
    
    async def list_conversations(self, date: Optional[datetime] = None) -> List[Path]:
        """List conversation files, optionally filtered by date.
        
        Args:
            date: Optional date filter (only conversations from this date)
            
        Returns:
            List of conversation file paths
        """
        if date:
            date_str = date.strftime("%Y-%m-%d")
            date_folder = self.base_path / date_str
            if not date_folder.exists():
                return []
            return list(date_folder.glob("conversation_*.json"))
        else:
            # Return all conversations
            all_files = []
            if self.base_path.exists():
                for date_folder in self.base_path.iterdir():
                    if date_folder.is_dir():
                        all_files.extend(date_folder.glob("conversation_*.json"))
            return sorted(all_files)