"""
Tests for streaming response functionality
"""
import asyncio
import time
import pytest
from unittest.mock import Mock, AsyncMock, patch
from typing import AsyncIterator, List

from src.performance.streaming_manager import (
    StreamingResponseManager,
    StreamingConfig,
    ChunkBuffer,
    StreamingMetrics
)


class TestStreamingResponseManager:
    """Test streaming response functionality"""
    
    @pytest.fixture
    def streaming_config(self):
        """Create test streaming configuration"""
        return StreamingConfig(
            chunk_size=50,  # Characters per chunk
            buffer_threshold=100,  # Buffer before yielding
            typing_delay=0.01,  # Simulate typing
            natural_breaks=['.', '!', '?', '\n'],  # Natural pause points
            max_buffer_time=0.5  # Max time before force flush
        )
    
    @pytest.mark.asyncio
    async def test_basic_streaming(self, streaming_config):
        """Test basic streaming functionality"""
        manager = StreamingResponseManager(streaming_config)
        
        text = "This is a test message. It should stream in chunks."
        chunks_received = []
        
        async for chunk in manager.stream_text(text):
            chunks_received.append(chunk)
        
        # Should receive multiple chunks
        assert len(chunks_received) > 1
        
        # Reassembled text should match original
        assert ''.join(chunks_received) == text
    
    @pytest.mark.asyncio
    async def test_natural_breaking_points(self, streaming_config):
        """Test that streaming respects natural breaking points"""
        manager = StreamingResponseManager(streaming_config)
        
        text = "First sentence. Second sentence! Third sentence?"
        chunks = []
        
        async for chunk in manager.stream_text(text):
            chunks.append(chunk)
        
        # Each chunk should end at a natural break if possible
        for chunk in chunks[:-1]:  # Except possibly the last
            if chunk:
                last_char = chunk.rstrip()[-1] if chunk.rstrip() else ''
                # Should end with punctuation or be at buffer limit
                assert last_char in ['.', '!', '?'] or len(chunk) >= 50
    
    @pytest.mark.asyncio
    async def test_buffer_management(self, streaming_config):
        """Test buffer fills and flushes correctly"""
        manager = StreamingResponseManager(streaming_config)
        
        # Text without natural breaks
        text = "a" * 200  # Long text without breaks
        chunks = []
        
        async for chunk in manager.stream_text(text):
            chunks.append(chunk)
            # No chunk should exceed buffer threshold
            assert len(chunk) <= streaming_config.buffer_threshold
        
        # All text should be delivered
        assert ''.join(chunks) == text
    
    @pytest.mark.asyncio
    async def test_typing_indicators(self, streaming_config):
        """Test typing indicators during processing"""
        manager = StreamingResponseManager(streaming_config)
        
        # Track typing states
        typing_states = []
        
        async def process_with_typing():
            async with manager.typing_indicator("Processing...") as indicator:
                typing_states.append(indicator.is_typing)
                await asyncio.sleep(0.1)
                typing_states.append(indicator.is_typing)
            typing_states.append(manager.is_typing)
        
        await process_with_typing()
        
        # Should show typing during processing
        assert typing_states[0] is True
        assert typing_states[1] is True
        assert typing_states[2] is False
    
    @pytest.mark.asyncio
    async def test_perceived_latency(self, streaming_config):
        """Test that streaming reduces perceived latency"""
        manager = StreamingResponseManager(streaming_config)
        
        text = "This is a longer response that would normally take time to generate completely."
        
        # Measure time to first chunk
        start_time = time.perf_counter()
        first_chunk_time = None
        all_chunks = []
        
        async for chunk in manager.stream_text(text):
            if first_chunk_time is None:
                first_chunk_time = time.perf_counter() - start_time
            all_chunks.append(chunk)
        
        total_time = time.perf_counter() - start_time
        
        # First chunk should arrive quickly
        assert first_chunk_time < 0.1  # Under 100ms
        
        # Perceived latency (time to first chunk) should be much less than total
        assert first_chunk_time < total_time * 0.3  # Less than 30% of total
    
    @pytest.mark.asyncio
    async def test_error_handling_mid_stream(self, streaming_config):
        """Test error handling during streaming"""
        manager = StreamingResponseManager(streaming_config)
        
        async def faulty_generator():
            yield "First chunk works fine. "
            yield "Second chunk also works. "
            raise ValueError("Stream error!")
            yield "This should not be sent"
        
        chunks = []
        error_caught = False
        
        try:
            async for chunk in manager.stream_from_generator(faulty_generator()):
                chunks.append(chunk)
        except ValueError as e:
            error_caught = True
            assert str(e) == "Stream error!"
        
        assert error_caught
        assert len(chunks) == 2  # Should have received chunks before error
    
    @pytest.mark.asyncio
    async def test_concurrent_streams(self, streaming_config):
        """Test multiple concurrent streams"""
        manager = StreamingResponseManager(streaming_config)
        
        text1 = "Stream one content here."
        text2 = "Stream two different content."
        
        async def collect_stream(text):
            chunks = []
            async for chunk in manager.stream_text(text):
                chunks.append(chunk)
            return ''.join(chunks)
        
        # Run two streams concurrently
        results = await asyncio.gather(
            collect_stream(text1),
            collect_stream(text2)
        )
        
        assert results[0] == text1
        assert results[1] == text2
    
    @pytest.mark.asyncio
    async def test_stream_cancellation(self, streaming_config):
        """Test graceful stream cancellation"""
        # Use smaller chunks to ensure we get multiple chunks
        config = StreamingConfig(
            chunk_size=10,
            buffer_threshold=20,
            typing_delay=0
        )
        manager = StreamingResponseManager(config)
        
        text = "This is a very long text " * 100
        chunks_received = []
        
        async def stream_with_cancel():
            async for chunk in manager.stream_text(text):
                chunks_received.append(chunk)
                if len(chunks_received) >= 3:
                    # Cancel after 3 chunks
                    break
        
        await stream_with_cancel()
        
        # Should have at least 3 chunks
        assert len(chunks_received) >= 3
        
        # Manager should be in clean state after brief delay
        await asyncio.sleep(0.01)
        assert not manager.is_streaming
    
    @pytest.mark.asyncio
    async def test_adaptive_chunking(self, streaming_config):
        """Test adaptive chunk sizing based on content"""
        manager = StreamingResponseManager(streaming_config)
        
        # Code block should be kept together
        text = "Here is some code:\n```python\ndef hello():\n    print('world')\n```\nAnd more text."
        
        chunks = []
        async for chunk in manager.stream_text(text, adaptive=True):
            chunks.append(chunk)
        
        # Code block should be in a single chunk
        code_chunk = next((c for c in chunks if '```python' in c), None)
        assert code_chunk is not None
        assert '```' in code_chunk and 'def hello()' in code_chunk


class TestChunkBuffer:
    """Test chunk buffering logic"""
    
    def test_buffer_initialization(self):
        """Test buffer initializes correctly"""
        buffer = ChunkBuffer(threshold=100)
        
        assert buffer.is_empty()
        assert buffer.size == 0
        assert not buffer.should_flush()
    
    def test_buffer_accumulation(self):
        """Test buffer accumulates content"""
        buffer = ChunkBuffer(threshold=20, natural_breaks=['.'])  # Only period
        
        buffer.add("Hello ")
        assert buffer.size == 6
        assert not buffer.should_flush()
        
        buffer.add("World")
        assert buffer.size == 11
        assert not buffer.should_flush()
        
        buffer.add(" More text")
        assert buffer.size == 21
        assert buffer.should_flush()  # Over threshold
    
    def test_natural_break_detection(self):
        """Test natural break point detection"""
        buffer = ChunkBuffer(
            threshold=100,
            natural_breaks=['.', '!', '?']
        )
        
        buffer.add("This is a sentence")
        assert not buffer.has_natural_break()
        
        buffer.add(".")
        assert buffer.has_natural_break()
        
        content = buffer.flush()
        assert content == "This is a sentence."
        assert buffer.is_empty()
    
    def test_force_flush(self):
        """Test forced buffer flush"""
        buffer = ChunkBuffer(threshold=100)
        
        buffer.add("Small content")
        assert not buffer.should_flush()
        
        content = buffer.flush(force=True)
        assert content == "Small content"
        assert buffer.is_empty()
    
    def test_timeout_flush(self):
        """Test buffer flush on timeout"""
        buffer = ChunkBuffer(
            threshold=100,
            max_age=0.1  # 100ms timeout
        )
        
        buffer.add("Content")
        assert not buffer.should_flush()
        
        # Wait for timeout
        time.sleep(0.11)
        assert buffer.should_flush_by_age()
        
        content = buffer.flush()
        assert content == "Content"


class TestStreamingMetrics:
    """Test streaming metrics collection"""
    
    def test_metrics_initialization(self):
        """Test metrics initialize correctly"""
        metrics = StreamingMetrics()
        
        assert metrics.total_streams == 0
        assert metrics.total_chunks == 0
        assert metrics.total_bytes == 0
        assert metrics.average_chunk_size == 0
    
    def test_metrics_tracking(self):
        """Test metrics track streaming statistics"""
        metrics = StreamingMetrics()
        
        # Record a stream
        metrics.record_stream_start()
        metrics.record_chunk("Hello ", 6)
        metrics.record_chunk("World!", 6)
        metrics.record_stream_end(0.5)
        
        assert metrics.total_streams == 1
        assert metrics.total_chunks == 2
        assert metrics.total_bytes == 12
        assert metrics.average_chunk_size == 6
        assert metrics.average_stream_duration == 0.5
    
    def test_latency_metrics(self):
        """Test perceived latency tracking"""
        metrics = StreamingMetrics()
        
        metrics.record_stream_start()
        metrics.record_first_chunk_time(0.05)  # 50ms to first chunk
        metrics.record_stream_end(0.5)  # 500ms total
        
        assert metrics.average_first_chunk_latency == 0.05
        assert metrics.perceived_latency_ratio == 0.1  # 50ms / 500ms


class TestStreamingIntegration:
    """Test streaming integration with agents"""
    
    @pytest.mark.asyncio
    async def test_coach_agent_streaming(self):
        """Test coach agent with streaming responses"""
        from src.agents.enhanced_coach_agent import EnhancedCoachAgent
        
        # Mock LLM service to return streamable content
        mock_llm = AsyncMock()
        mock_llm.generate_response_stream = AsyncMock()
        
        async def mock_stream():
            chunks = [
                "I understand ",
                "you're feeling ",
                "overwhelmed. ",
                "Let's take ",
                "this step by step."
            ]
            for chunk in chunks:
                yield chunk
                await asyncio.sleep(0.01)
        
        mock_llm.generate_response_stream.return_value = mock_stream()
        
        # Create agent with streaming enabled
        with patch('src.agents.enhanced_coach_agent.AnthropicService', return_value=mock_llm):
            agent = EnhancedCoachAgent(mock_llm)
            agent.streaming_enabled = True
            
            # Collect streamed response
            streamed_chunks = []
            async for chunk in agent.handle_request_stream(Mock(
                query="I'm feeling overwhelmed",
                context={}
            )):
                streamed_chunks.append(chunk)
            
            # Should receive multiple chunks
            assert len(streamed_chunks) > 1
            
            # Complete response should be coherent
            full_response = ''.join(streamed_chunks)
            assert "overwhelmed" in full_response
            assert "step by step" in full_response
    
    @pytest.mark.asyncio
    async def test_deep_thoughts_streaming(self):
        """Test Deep Thoughts generation with paragraph streaming"""
        from src.agents.reporter_agent import ReporterAgent
        
        mock_llm = AsyncMock()
        
        # Mock Deep Thoughts generation in paragraphs
        async def mock_deep_thoughts():
            paragraphs = [
                "## Reflection\n\nToday's conversation revealed important patterns.",
                "\n\nYou mentioned feeling overwhelmed multiple times.",
                "\n\n## Insights\n\nThis pattern suggests a need for better boundaries.",
                "\n\nConsider what you can delegate or postpone."
            ]
            for para in paragraphs:
                yield para
                await asyncio.sleep(0.02)
        
        mock_llm.generate_response_stream.return_value = mock_deep_thoughts()
        
        with patch('src.agents.reporter_agent.AnthropicService', return_value=mock_llm):
            agent = ReporterAgent(mock_llm)
            
            # Stream Deep Thoughts
            paragraphs = []
            async for paragraph in agent.generate_deep_thoughts_stream(Mock()):
                paragraphs.append(paragraph)
            
            # Should receive multiple paragraphs
            assert len(paragraphs) >= 4
            
            # Should have section headers
            full_report = ''.join(paragraphs)
            assert "## Reflection" in full_report
            assert "## Insights" in full_report