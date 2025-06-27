import pytest
from src.events.stream_buffer import StreamBuffer, StreamTrack


@pytest.mark.asyncio
async def test_stream_buffer_handles_multiple_tracks():
    """Buffer should maintain separate tracks for conversation and insights"""
    buffer = StreamBuffer()
    
    # Add to main conversation track
    await buffer.add_to_track(StreamTrack.CONVERSATION, {
        "role": "user",
        "content": "I want to be more productive"
    })
    
    # Add to insights track (parallel processing)
    await buffer.add_to_track(StreamTrack.INSIGHTS, {
        "type": "observation",
        "content": "User expressing productivity concerns"
    })
    
    # Should be able to read from both tracks
    conv_items = await buffer.read_track(StreamTrack.CONVERSATION)
    insight_items = await buffer.read_track(StreamTrack.INSIGHTS)
    
    assert len(conv_items) == 1
    assert len(insight_items) == 1
    assert conv_items[0]["role"] == "user"
    assert insight_items[0]["type"] == "observation"