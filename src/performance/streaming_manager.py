"""
Streaming response manager for progressive content delivery
"""
import asyncio
import time
import re
import logging
from typing import AsyncIterator, Optional, List, Dict, Any
from dataclasses import dataclass, field
from contextlib import asynccontextmanager
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class StreamingConfig:
    """Configuration for streaming behavior"""
    chunk_size: int = 50  # Target characters per chunk
    buffer_threshold: int = 100  # Buffer size before yielding
    typing_delay: float = 0.01  # Delay between chunks (seconds)
    natural_breaks: List[str] = field(default_factory=lambda: ['.', '!', '?', '\n'])
    max_buffer_time: float = 0.5  # Max seconds before force flush
    enable_typing_indicators: bool = True
    adaptive_chunking: bool = True  # Smart chunking for code blocks etc


class ChunkBuffer:
    """Buffer for accumulating chunks with smart flushing"""
    
    def __init__(
        self,
        threshold: int = 100,
        natural_breaks: Optional[List[str]] = None,
        max_age: float = 0.5
    ):
        self.threshold = threshold
        self.natural_breaks = natural_breaks or ['.', '!', '?', '\n']
        self.max_age = max_age
        self.buffer: List[str] = []
        self.buffer_size = 0
        self.buffer_start_time = None
    
    def add(self, content: str):
        """Add content to buffer"""
        if not self.buffer:
            self.buffer_start_time = time.perf_counter()
        self.buffer.append(content)
        self.buffer_size += len(content)
    
    def should_flush(self) -> bool:
        """Check if buffer should be flushed"""
        if not self.buffer:
            return False
        
        # Check size threshold
        if self.buffer_size >= self.threshold:
            return True
        
        # Check age threshold
        if self.should_flush_by_age():
            return True
        
        # Check for natural break at end
        if self.has_natural_break():
            return True
        
        return False
    
    def should_flush_by_age(self) -> bool:
        """Check if buffer is too old"""
        if not self.buffer_start_time:
            return False
        age = time.perf_counter() - self.buffer_start_time
        return age >= self.max_age
    
    def has_natural_break(self) -> bool:
        """Check if buffer ends with natural break"""
        if not self.buffer:
            return False
        
        last_content = self.buffer[-1].rstrip()
        if not last_content:
            return False
        
        return any(last_content.endswith(br) for br in self.natural_breaks)
    
    def flush(self, force: bool = False) -> str:
        """Flush buffer and return content"""
        if not self.buffer and not force:
            return ""
        
        content = ''.join(self.buffer)
        self.buffer = []
        self.buffer_size = 0
        self.buffer_start_time = None
        return content
    
    def is_empty(self) -> bool:
        """Check if buffer is empty"""
        return len(self.buffer) == 0
    
    @property
    def size(self) -> int:
        """Current buffer size"""
        return self.buffer_size


class TypingIndicator:
    """Manages typing indicator state"""
    
    def __init__(self):
        self.is_typing = False
        self.start_time = None
        self.typing_message = "AI is thinking..."
    
    def start(self, message: str = None):
        """Start typing indicator"""
        self.is_typing = True
        self.start_time = time.perf_counter()
        if message:
            self.typing_message = message
        logger.debug(f"Typing indicator started: {self.typing_message}")
    
    def stop(self):
        """Stop typing indicator"""
        self.is_typing = False
        if self.start_time:
            duration = time.perf_counter() - self.start_time
            logger.debug(f"Typing indicator stopped after {duration:.2f}s")
        self.start_time = None
    
    def get_duration(self) -> float:
        """Get typing duration"""
        if not self.start_time:
            return 0.0
        return time.perf_counter() - self.start_time


class StreamingMetrics:
    """Track streaming performance metrics"""
    
    def __init__(self):
        self.total_streams = 0
        self.total_chunks = 0
        self.total_bytes = 0
        self.stream_durations = []
        self.first_chunk_latencies = []
        self.chunk_sizes = []
        self.current_stream_start = None
    
    def record_stream_start(self):
        """Record start of streaming"""
        self.total_streams += 1
        self.current_stream_start = time.perf_counter()
    
    def record_chunk(self, content: str, size: int):
        """Record chunk delivery"""
        self.total_chunks += 1
        self.total_bytes += size
        self.chunk_sizes.append(size)
    
    def record_first_chunk_time(self, latency: float):
        """Record time to first chunk"""
        self.first_chunk_latencies.append(latency)
    
    def record_stream_end(self, duration: float):
        """Record stream completion"""
        self.stream_durations.append(duration)
        self.current_stream_start = None
    
    @property
    def average_chunk_size(self) -> float:
        """Average size of chunks"""
        if not self.chunk_sizes:
            return 0
        return sum(self.chunk_sizes) / len(self.chunk_sizes)
    
    @property
    def average_stream_duration(self) -> float:
        """Average stream duration"""
        if not self.stream_durations:
            return 0
        return sum(self.stream_durations) / len(self.stream_durations)
    
    @property
    def average_first_chunk_latency(self) -> float:
        """Average time to first chunk"""
        if not self.first_chunk_latencies:
            return 0
        return sum(self.first_chunk_latencies) / len(self.first_chunk_latencies)
    
    @property
    def perceived_latency_ratio(self) -> float:
        """Ratio of perceived latency to total time"""
        if not self.first_chunk_latencies or not self.stream_durations:
            return 0
        avg_first = self.average_first_chunk_latency
        avg_total = self.average_stream_duration
        if avg_total == 0:
            return 0
        return avg_first / avg_total


class StreamingResponseManager:
    """Manages streaming responses with progressive delivery"""
    
    def __init__(self, config: Optional[StreamingConfig] = None):
        self.config = config or StreamingConfig()
        self.metrics = StreamingMetrics()
        self.typing_indicator = TypingIndicator()
        self.is_streaming = False
        self._active_streams = set()
    
    async def stream_text(
        self,
        text: str,
        adaptive: bool = None
    ) -> AsyncIterator[str]:
        """Stream text in chunks with natural breaking"""
        if adaptive is None:
            adaptive = self.config.adaptive_chunking
        
        self.is_streaming = True
        stream_id = id(text)
        self._active_streams.add(stream_id)
        
        try:
            self.metrics.record_stream_start()
            start_time = time.perf_counter()
            first_chunk_sent = False
            
            # Handle adaptive chunking for code blocks
            if adaptive:
                chunks = self._adaptive_split(text)
            else:
                chunks = self._simple_split(text)
            
            buffer = ChunkBuffer(
                threshold=self.config.buffer_threshold,
                natural_breaks=self.config.natural_breaks,
                max_age=self.config.max_buffer_time
            )
            
            for chunk in chunks:
                # Ensure chunk doesn't exceed buffer threshold
                if len(chunk) > self.config.buffer_threshold:
                    # Split large chunks
                    for i in range(0, len(chunk), self.config.buffer_threshold):
                        sub_chunk = chunk[i:i + self.config.buffer_threshold]
                        if not first_chunk_sent:
                            latency = time.perf_counter() - start_time
                            self.metrics.record_first_chunk_time(latency)
                            first_chunk_sent = True
                        
                        self.metrics.record_chunk(sub_chunk, len(sub_chunk))
                        yield sub_chunk
                        
                        if self.config.typing_delay > 0:
                            await asyncio.sleep(self.config.typing_delay)
                else:
                    buffer.add(chunk)
                    
                    if buffer.should_flush():
                        content = buffer.flush()
                        if content:
                            # Record first chunk timing
                            if not first_chunk_sent:
                                latency = time.perf_counter() - start_time
                                self.metrics.record_first_chunk_time(latency)
                                first_chunk_sent = True
                            
                            self.metrics.record_chunk(content, len(content))
                            yield content
                            
                            # Add typing delay for natural feel
                            if self.config.typing_delay > 0:
                                await asyncio.sleep(self.config.typing_delay)
            
            # Flush remaining buffer
            remaining = buffer.flush(force=True)
            if remaining:
                if not first_chunk_sent:
                    latency = time.perf_counter() - start_time
                    self.metrics.record_first_chunk_time(latency)
                
                self.metrics.record_chunk(remaining, len(remaining))
                yield remaining
            
            # Record completion
            duration = time.perf_counter() - start_time
            self.metrics.record_stream_end(duration)
            
        finally:
            self._active_streams.discard(stream_id)
            if not self._active_streams:
                self.is_streaming = False
    
    async def stream_from_generator(
        self,
        generator: AsyncIterator[str]
    ) -> AsyncIterator[str]:
        """Stream from an async generator with buffering"""
        self.is_streaming = True
        stream_id = id(generator)
        self._active_streams.add(stream_id)
        
        try:
            self.metrics.record_stream_start()
            start_time = time.perf_counter()
            first_chunk_sent = False
            
            buffer = ChunkBuffer(
                threshold=self.config.buffer_threshold,
                natural_breaks=self.config.natural_breaks,
                max_age=self.config.max_buffer_time
            )
            
            async for chunk in generator:
                buffer.add(chunk)
                
                if buffer.should_flush():
                    content = buffer.flush()
                    if content:
                        if not first_chunk_sent:
                            latency = time.perf_counter() - start_time
                            self.metrics.record_first_chunk_time(latency)
                            first_chunk_sent = True
                        
                        self.metrics.record_chunk(content, len(content))
                        yield content
                        
                        if self.config.typing_delay > 0:
                            await asyncio.sleep(self.config.typing_delay)
            
            # Flush remaining
            remaining = buffer.flush(force=True)
            if remaining:
                if not first_chunk_sent:
                    latency = time.perf_counter() - start_time
                    self.metrics.record_first_chunk_time(latency)
                
                self.metrics.record_chunk(remaining, len(remaining))
                yield remaining
            
            duration = time.perf_counter() - start_time
            self.metrics.record_stream_end(duration)
            
        finally:
            self._active_streams.discard(stream_id)
            if not self._active_streams:
                self.is_streaming = False
    
    def _simple_split(self, text: str) -> List[str]:
        """Simple chunking by size"""
        chunks = []
        chunk_size = self.config.chunk_size
        
        # Split by chunk size
        for i in range(0, len(text), chunk_size):
            chunk = text[i:i + chunk_size]
            chunks.append(chunk)
        
        return chunks
    
    def _adaptive_split(self, text: str) -> List[str]:
        """Adaptive chunking that keeps code blocks and paragraphs together"""
        chunks = []
        
        # Check for code blocks
        code_pattern = r'```[\s\S]*?```'
        code_blocks = list(re.finditer(code_pattern, text))
        
        if code_blocks:
            last_end = 0
            for match in code_blocks:
                # Add text before code block
                if match.start() > last_end:
                    before_text = text[last_end:match.start()]
                    chunks.extend(self._split_by_sentences(before_text))
                
                # Add entire code block as one chunk
                chunks.append(match.group())
                last_end = match.end()
            
            # Add remaining text
            if last_end < len(text):
                chunks.extend(self._split_by_sentences(text[last_end:]))
        else:
            # No code blocks, split by sentences/paragraphs
            chunks = self._split_by_sentences(text)
        
        return chunks
    
    def _split_by_sentences(self, text: str) -> List[str]:
        """Split text by sentences or natural breaks"""
        chunks = []
        current = []
        current_size = 0
        
        # Split by sentences
        sentences = re.split(r'([.!?\n]+)', text)
        
        for i in range(0, len(sentences), 2):
            sentence = sentences[i]
            if i + 1 < len(sentences):
                sentence += sentences[i + 1]  # Add punctuation
            
            if current_size + len(sentence) > self.config.chunk_size and current:
                chunks.append(''.join(current))
                current = []
                current_size = 0
            
            current.append(sentence)
            current_size += len(sentence)
        
        if current:
            chunks.append(''.join(current))
        
        return chunks
    
    @asynccontextmanager
    async def typing_indicator(self, message: str = None):
        """Context manager for typing indicator"""
        if self.config.enable_typing_indicators:
            self.typing_indicator.start(message)
        try:
            yield self.typing_indicator
        finally:
            if self.config.enable_typing_indicators:
                self.typing_indicator.stop()
    
    @property
    def is_typing(self) -> bool:
        """Check if currently showing typing indicator"""
        return self.typing_indicator.is_typing
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get streaming metrics"""
        return {
            "total_streams": self.metrics.total_streams,
            "total_chunks": self.metrics.total_chunks,
            "total_bytes": self.metrics.total_bytes,
            "average_chunk_size": self.metrics.average_chunk_size,
            "average_stream_duration": self.metrics.average_stream_duration,
            "average_first_chunk_latency": self.metrics.average_first_chunk_latency,
            "perceived_latency_ratio": self.metrics.perceived_latency_ratio,
            "is_streaming": self.is_streaming,
            "active_streams": len(self._active_streams)
        }


# Global streaming manager instance
_streaming_manager: Optional[StreamingResponseManager] = None


def get_streaming_manager(
    config: Optional[StreamingConfig] = None
) -> StreamingResponseManager:
    """Get global streaming manager instance"""
    global _streaming_manager
    if _streaming_manager is None:
        _streaming_manager = StreamingResponseManager(config)
    return _streaming_manager