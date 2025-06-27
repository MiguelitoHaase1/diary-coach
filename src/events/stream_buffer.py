import asyncio
from enum import Enum
from typing import Dict, List, Any, Optional


class StreamTrack(Enum):
    """Different tracks for stream buffer content"""
    CONVERSATION = "conversation"
    INSIGHTS = "insights"


class StreamBuffer:
    """Buffer for handling multiple parallel conversation tracks"""
    
    def __init__(self):
        self._tracks: Dict[StreamTrack, asyncio.Queue] = {
            StreamTrack.CONVERSATION: asyncio.Queue(),
            StreamTrack.INSIGHTS: asyncio.Queue()
        }
    
    async def add_to_track(self, track: StreamTrack, item: Dict[str, Any]) -> None:
        """Add an item to the specified track"""
        await self._tracks[track].put(item)
    
    async def read_track(self, track: StreamTrack, max_items: Optional[int] = None) -> List[Dict[str, Any]]:
        """Read all available items from the specified track (non-blocking)"""
        items = []
        queue = self._tracks[track]
        
        # Read all available items without blocking
        while True:
            try:
                item = queue.get_nowait()
                items.append(item)
                if max_items and len(items) >= max_items:
                    break
            except asyncio.QueueEmpty:
                break
        
        return items