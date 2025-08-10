"""
Fast path routing for optimized execution of common patterns
"""
import re
import time
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
from datetime import datetime, timedelta
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class FastPathConfig:
    """Configuration for fast path routing"""
    simple_query_threshold: int = 20  # Max words for simple query
    fast_path_timeout: float = 1.0  # Timeout for fast path execution
    enable_speculation: bool = True  # Enable speculative execution
    speculation_confidence: float = 0.7  # Min confidence for speculation
    precompute_morning: bool = True  # Precompute morning protocol
    cache_ttl: int = 3600  # Pattern cache TTL in seconds


@dataclass
class PathPattern:
    """Detected path pattern"""
    query: str
    pattern_type: str  # greeting, simple_question, complex, etc.
    is_fast_path: bool
    confidence: float
    use_precomputed: bool = False
    cache_key: Optional[str] = None
    
    def __post_init__(self):
        if not self.cache_key:
            # Generate cache key from query
            self.cache_key = hashlib.md5(
                self.query.lower().encode()
            ).hexdigest()[:16]


@dataclass
class SpeculativePrediction:
    """Prediction for speculative execution"""
    query: str
    confidence: float
    context: Dict[str, Any]
    response: Optional[str] = None
    is_ready: bool = False
    timestamp: datetime = field(default_factory=datetime.now)


class PatternDetector:
    """Detects conversation patterns for routing"""
    
    # Common greeting patterns
    GREETING_PATTERNS = [
        r'^(hi|hello|hey|good morning|morning|evening|afternoon)',
        r'^(greetings|salutations|howdy)',
        r'^how are you',
        r"^what's up"
    ]
    
    # Simple question patterns
    SIMPLE_QUESTIONS = [
        r'^what time',
        r'^what day',
        r'^what.*weather',
        r'^how.*weather',
        r'^thank',
        r'^thanks',
        r'^okay',
        r'^ok\b',
        r'^yes\b',
        r'^no\b',
        r'^sure',
        r'^got it'
    ]
    
    # Morning protocol patterns
    MORNING_PATTERNS = [
        r'morning.*check',
        r'start.*day',
        r'morning.*routine',
        r'daily.*check',
        r'morning.*protocol'
    ]
    
    # Complex query indicators
    COMPLEX_INDICATORS = [
        'help me understand',
        'I\'m feeling',
        'I\'ve been thinking',
        'can you explain',
        'deep dive',
        'reflection',
        'analyze',
        'struggling with',
        'overwhelmed',
        'confused about'
    ]
    
    def __init__(self):
        self._pattern_cache = {}
        self._cache_timestamps = {}
    
    def detect_pattern(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> PathPattern:
        """Detect the pattern type of a query"""
        
        # Include context in cache key
        cache_key = self._get_cache_key(query, context)
        if self._is_cached(cache_key):
            cached = self._pattern_cache[cache_key]
            logger.debug(f"Pattern cache hit for: {query[:30]}...")
            return cached
        
        # Normalize query
        normalized = query.lower().strip()
        word_count = len(query.split())
        
        # Check for morning protocol
        if self._is_morning_protocol(normalized, context):
            pattern = PathPattern(
                query=query,
                pattern_type="morning_protocol",
                is_fast_path=True,
                confidence=0.95,
                use_precomputed=True
            )
            self._cache_pattern(cache_key, pattern)
            return pattern
        
        # Check for greeting
        if self._is_greeting(normalized):
            pattern = PathPattern(
                query=query,
                pattern_type="greeting",
                is_fast_path=True,
                confidence=0.9
            )
            self._cache_pattern(cache_key, pattern)
            return pattern
        
        # Check context for complex conversation
        if context and context.get("previous_pattern") == "deep_reflection":
            # Even simple queries in complex context should use normal path
            pattern = PathPattern(
                query=query,
                pattern_type="contextual_follow_up",
                is_fast_path=False,
                confidence=0.8
            )
            self._cache_pattern(cache_key, pattern)
            return pattern
        
        # Check for simple question/acknowledgment
        if self._is_simple_question(normalized) or word_count <= 5:
            pattern_type = "acknowledgment" if word_count <= 2 else "simple_question"
            pattern = PathPattern(
                query=query,
                pattern_type=pattern_type,
                is_fast_path=True,
                confidence=0.85
            )
            self._cache_pattern(cache_key, pattern)
            return pattern
        
        # Check for complex query
        if self._is_complex_query(normalized) or word_count > 20:
            pattern = PathPattern(
                query=query,
                pattern_type="complex",
                is_fast_path=False,
                confidence=0.8
            )
            self._cache_pattern(cache_key, pattern)
            return pattern
        
        # Default to normal path for uncertain queries
        pattern = PathPattern(
            query=query,
            pattern_type="normal",
            is_fast_path=word_count <= 10,
            confidence=0.6
        )
        self._cache_pattern(cache_key, pattern)
        return pattern
    
    def _is_greeting(self, text: str) -> bool:
        """Check if text is a greeting"""
        return any(re.match(pattern, text) for pattern in self.GREETING_PATTERNS)
    
    def _is_simple_question(self, text: str) -> bool:
        """Check if text is a simple question"""
        return any(re.match(pattern, text) for pattern in self.SIMPLE_QUESTIONS)
    
    def _is_morning_protocol(
        self,
        text: str,
        context: Optional[Dict[str, Any]]
    ) -> bool:
        """Check if text triggers morning protocol"""
        # Check explicit morning patterns
        if any(re.search(pattern, text) for pattern in self.MORNING_PATTERNS):
            return True
        
        # Check context for morning time
        if context and context.get("time_of_day") == "morning":
            if self._is_greeting(text):
                return True
        
        return False
    
    def _is_complex_query(self, text: str) -> bool:
        """Check if text is a complex query"""
        return any(indicator in text for indicator in self.COMPLEX_INDICATORS)
    
    def _get_cache_key(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate cache key for query with context"""
        key_parts = [query.lower()]
        if context:
            # Include relevant context in key
            if "previous_pattern" in context:
                key_parts.append(f"prev:{context['previous_pattern']}")
            if "time_of_day" in context:
                key_parts.append(f"time:{context['time_of_day']}")
        
        combined = "|".join(key_parts)
        return hashlib.md5(combined.encode()).hexdigest()[:16]
    
    def _is_cached(self, cache_key: str) -> bool:
        """Check if pattern is cached and valid"""
        if cache_key not in self._pattern_cache:
            return False
        
        # Check TTL
        timestamp = self._cache_timestamps.get(cache_key)
        if not timestamp:
            return False
        
        age = (datetime.now() - timestamp).total_seconds()
        return age < 3600  # 1 hour TTL
    
    def _cache_pattern(self, cache_key: str, pattern: PathPattern):
        """Cache a pattern detection result"""
        self._pattern_cache[cache_key] = pattern
        self._cache_timestamps[cache_key] = datetime.now()


class SpeculativeExecutor:
    """Handles speculative execution of likely follow-ups"""
    
    # Common follow-up patterns
    FOLLOW_UP_PATTERNS = {
        "greeting": [
            ("How can I help you today?", 0.8),
            ("What's on your mind?", 0.75),
            ("How are you feeling?", 0.7)
        ],
        "morning_protocol": [
            ("What should I focus on today?", 0.85),
            ("How did I sleep?", 0.75),
            ("What's the weather like?", 0.7)
        ],
        "simple_question": [
            ("Anything else?", 0.6),
            ("Tell me more", 0.65)
        ]
    }
    
    def __init__(
        self,
        confidence_threshold: float = 0.7,
        max_speculations: int = 3,
        timeout: float = 2.0
    ):
        self.confidence_threshold = confidence_threshold
        self.max_speculations = max_speculations
        self.timeout = timeout
        self._speculation_cache = {}
        self._accuracy_stats = defaultdict(lambda: {"hits": 0, "misses": 0})
    
    async def predict_follow_ups(
        self,
        current_query: str,
        context: Dict[str, Any]
    ) -> List[SpeculativePrediction]:
        """Predict likely follow-up queries"""
        
        # Get current pattern type from context or detect it
        pattern_type = context.get("pattern_type")
        if not pattern_type:
            # Simple detection based on query
            if "morning" in current_query.lower() or "good morning" in current_query.lower():
                pattern_type = "morning_protocol"
            elif "hello" in current_query.lower() or "hi" in current_query.lower():
                pattern_type = "greeting"
            else:
                pattern_type = "normal"
        
        # Get potential follow-ups
        follow_ups = self.FOLLOW_UP_PATTERNS.get(pattern_type, [])
        
        # Filter by confidence threshold
        predictions = []
        for query, confidence in follow_ups[:self.max_speculations]:
            if confidence >= self.confidence_threshold:
                predictions.append(
                    SpeculativePrediction(
                        query=query,
                        confidence=confidence,
                        context=context
                    )
                )
        
        return predictions
    
    async def execute_speculations(
        self,
        predictions: List[SpeculativePrediction],
        llm_service: Any
    ) -> List[SpeculativePrediction]:
        """Execute speculative queries in parallel"""
        
        tasks = []
        for prediction in predictions:
            task = self._execute_single_speculation(prediction, llm_service)
            tasks.append(task)
        
        # Execute with timeout
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=self.timeout
            )
            
            # Update predictions with results
            for prediction, result in zip(predictions, results):
                if not isinstance(result, Exception):
                    prediction.response = result
                    prediction.is_ready = True
            
        except asyncio.TimeoutError:
            logger.warning("Speculative execution timed out")
        
        return predictions
    
    async def _execute_single_speculation(
        self,
        prediction: SpeculativePrediction,
        llm_service: Any
    ) -> str:
        """Execute a single speculative query"""
        response = await llm_service.generate_response(
            messages=[{"role": "user", "content": prediction.query}],
            temperature=0.3  # Lower temperature for consistency
        )
        return response
    
    def cache_speculation(self, speculation: SpeculativePrediction):
        """Cache a speculative result"""
        key = self._get_cache_key(speculation.query)
        self._speculation_cache[key] = speculation
    
    async def get_cached_speculation(
        self,
        query: str
    ) -> Optional[SpeculativePrediction]:
        """Get cached speculation if available"""
        key = self._get_cache_key(query)
        
        if key in self._speculation_cache:
            speculation = self._speculation_cache[key]
            
            # Check if still valid (5 minute TTL)
            age = (datetime.now() - speculation.timestamp).total_seconds()
            if age < 300 and speculation.is_ready:
                self.record_hit(query)
                return speculation
        
        self.record_miss(query)
        return None
    
    async def execute_with_timeout(
        self,
        coro: Any,
        timeout: float
    ) -> Optional[Any]:
        """Execute coroutine with timeout"""
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError:
            return None
    
    def record_hit(self, pattern: str):
        """Record a speculation hit"""
        self._accuracy_stats[pattern]["hits"] += 1
    
    def record_miss(self, pattern: str):
        """Record a speculation miss"""
        self._accuracy_stats[pattern]["misses"] += 1
    
    def get_accuracy(self, pattern: str) -> float:
        """Get speculation accuracy for a pattern"""
        stats = self._accuracy_stats[pattern]
        total = stats["hits"] + stats["misses"]
        if total == 0:
            return 0.0
        return round(stats["hits"] / total, 2)
    
    def should_speculate(self, pattern: str) -> bool:
        """Check if we should speculate for this pattern"""
        stats = self._accuracy_stats[pattern]
        total = stats["hits"] + stats["misses"]
        
        # Always speculate if we have limited data
        if total < 3:
            return True
        
        accuracy = self.get_accuracy(pattern)
        # Don't speculate if accuracy is too low
        return accuracy >= 0.5
    
    def _get_cache_key(self, query: str) -> str:
        """Generate cache key for query"""
        # Normalize and hash
        normalized = query.lower().strip()
        return hashlib.md5(normalized.encode()).hexdigest()[:16]


class PrecomputedComponents:
    """Manages precomputed static components"""
    
    def __init__(self):
        self.morning_greeting = None
        self.morning_prompts = []
        self.morning_transitions = {}
        self.static_prompts = {}
    
    def precompute_morning_protocol(self):
        """Precompute morning protocol components"""
        
        # Morning greeting
        self.morning_greeting = (
            "Good morning! I'm here to support you as you start your day. "
            "How are you feeling this morning?"
        )
        
        # Morning prompts
        self.morning_prompts = [
            "What's on your mind as you begin today?",
            "How did you sleep?",
            "What are you looking forward to today?",
            "Any concerns or thoughts from yesterday?",
            "What would make today successful for you?"
        ]
        
        # State transitions
        self.morning_transitions = {
            "greeting": "check_in",
            "check_in": "priorities",
            "priorities": "support",
            "support": "complete"
        }
        
        logger.info("Precomputed morning protocol components")
    
    @property
    def has_morning_greeting(self) -> bool:
        return self.morning_greeting is not None
    
    @property
    def has_morning_prompts(self) -> bool:
        return len(self.morning_prompts) > 0
    
    @property
    def has_morning_transitions(self) -> bool:
        return len(self.morning_transitions) > 0
    
    def get_morning_greeting(self) -> str:
        """Get precomputed morning greeting"""
        if not self.morning_greeting:
            self.precompute_morning_protocol()
        return self.morning_greeting
    
    def get_morning_prompts(self) -> List[str]:
        """Get precomputed morning prompts"""
        if not self.morning_prompts:
            self.precompute_morning_protocol()
        return self.morning_prompts


class PromptCompiler:
    """Compiles and caches static prompt components"""
    
    def __init__(self):
        self._compiled_prompts = {}
        self._compile_time = None
    
    def compile_static_prompts(self) -> Dict[str, str]:
        """Compile static prompt components"""
        
        if self._compiled_prompts and self._compile_time:
            # Check if cache is still valid (1 hour)
            age = (datetime.now() - self._compile_time).total_seconds()
            if age < 3600:
                return self._compiled_prompts
        
        # Compile core prompts
        self._compiled_prompts = {
            "coach_base": self._load_coach_base(),
            "agent_instructions": self._load_agent_instructions(),
            "response_format": self._load_response_format()
        }
        
        self._compile_time = datetime.now()
        logger.info("Compiled static prompt components")
        
        return self._compiled_prompts
    
    def load_dynamic_prompt(self, name: str) -> str:
        """Load a prompt dynamically (for comparison)"""
        # Simulate loading from file
        time.sleep(0.01)  # Simulate I/O
        
        if name == "coach_base":
            return self._load_coach_base()
        elif name == "agent_instructions":
            return self._load_agent_instructions()
        elif name == "response_format":
            return self._load_response_format()
        return ""
    
    def _load_coach_base(self) -> str:
        """Load base coach prompt"""
        return (
            "You are a supportive diary coach helping users reflect "
            "on their thoughts and feelings."
        )
    
    def _load_agent_instructions(self) -> str:
        """Load agent coordination instructions"""
        return (
            "You can coordinate with other agents when needed "
            "to provide comprehensive support."
        )
    
    def _load_response_format(self) -> str:
        """Load response format instructions"""
        return (
            "Respond in a warm, empathetic tone. "
            "Keep responses concise but meaningful."
        )


class ResponseTemplates:
    """Manages precomputed response templates"""
    
    def __init__(self):
        self.templates = {}
        self._precomputed = False
    
    def precompute_common_responses(self):
        """Precompute templates for common responses"""
        
        self.templates = {
            "greeting": "Hello {name}! How can I help you today?",
            "acknowledgment": "I understand. {context}",
            "clarification": "Could you tell me more about {topic}?",
            "morning": "Good morning {name}! Ready to start your day?",
            "encouragement": "You're doing great. {message}",
            "reflection": "That's an interesting point about {topic}."
        }
        
        self._precomputed = True
        logger.info("Precomputed response templates")
    
    def has_template(self, template_type: str) -> bool:
        """Check if template exists"""
        if not self._precomputed:
            self.precompute_common_responses()
        return template_type in self.templates
    
    def render(self, template_type: str, **kwargs) -> str:
        """Render a template with variables"""
        if not self._precomputed:
            self.precompute_common_responses()
        
        template = self.templates.get(template_type, "")
        
        # Provide defaults for missing variables
        defaults = {
            "name": "there",
            "context": "Let me help you with that.",
            "topic": "that",
            "message": "Keep going!"
        }
        
        # Merge with provided kwargs
        variables = {**defaults, **kwargs}
        
        # Safe format with defaults
        try:
            return template.format(**variables)
        except KeyError as e:
            logger.warning(f"Missing template variable: {e}")
            return template


class FastPathExecutor:
    """Executes queries through fast or normal paths"""
    
    def __init__(self):
        self.templates = ResponseTemplates()
        self.templates.precompute_common_responses()
    
    async def execute_fast_path(self, query: str) -> str:
        """Execute query through fast path"""
        
        # Simulate fast processing
        await asyncio.sleep(0.1)  # Much faster than normal
        
        # Use templates for common queries
        query_lower = query.lower()
        
        if "hello" in query_lower or "hi" in query_lower:
            return self.templates.render("greeting")
        elif "thank" in query_lower:
            return "You're welcome! Is there anything else I can help with?"
        elif "how are you" in query_lower:
            return "I'm doing well, thank you for asking! How are you doing?"
        elif "morning" in query_lower:
            return self.templates.render("morning")
        elif "time" in query_lower:
            return f"The current time is {datetime.now().strftime('%I:%M %p')}"
        else:
            return "I understand. How can I assist you further?"
    
    async def execute_normal_path(self, query: str) -> str:
        """Execute query through normal path"""
        
        # Simulate normal processing (slower)
        await asyncio.sleep(2.0)
        
        return f"[Normal path response to: {query}]"


class PathMetrics:
    """Tracks metrics for path execution"""
    
    def __init__(self):
        self.executions = defaultdict(list)
        self.cache_hits = defaultdict(int)
        self.cache_misses = defaultdict(int)
    
    def record_execution(self, path_type: str, latency: float):
        """Record an execution"""
        self.executions[path_type].append(latency)
    
    def record_cache_hit(self, path_type: str):
        """Record a cache hit"""
        self.cache_hits[path_type] += 1
    
    def record_cache_miss(self, path_type: str):
        """Record a cache miss"""
        self.cache_misses[path_type] += 1
    
    def get_average_latency(self, path_type: str) -> float:
        """Get average latency for path type"""
        latencies = self.executions[path_type]
        if not latencies:
            return 0.0
        return sum(latencies) / len(latencies)
    
    def get_cache_hit_rate(self, path_type: str) -> float:
        """Get cache hit rate for path type"""
        hits = self.cache_hits[path_type]
        misses = self.cache_misses[path_type]
        total = hits + misses
        if total == 0:
            return 0.0
        return round(hits / total, 2)


class FastPathRouter:
    """Main router for fast path optimization"""
    
    def __init__(self, config: Optional[FastPathConfig] = None):
        self.config = config or FastPathConfig()
        self.detector = PatternDetector()
        self.speculator = SpeculativeExecutor(
            confidence_threshold=self.config.speculation_confidence
        )
        self.components = PrecomputedComponents()
        self.metrics = PathMetrics()
        
        # Precompute if enabled
        if self.config.precompute_morning:
            self.components.precompute_morning_protocol()
    
    def detect_path(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> PathPattern:
        """Detect optimal execution path for query"""
        
        # Use detector to identify pattern
        pattern = self.detector.detect_pattern(query, context)
        
        # Record in metrics
        if pattern.is_fast_path:
            self.metrics.record_cache_hit("detection")
        else:
            self.metrics.record_cache_miss("detection")
        
        return pattern
    
    async def route_query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, PathPattern]:
        """Route query through optimal path"""
        
        start_time = time.perf_counter()
        
        # Detect path
        pattern = self.detect_path(query, context)
        
        # Check for cached speculation
        if self.config.enable_speculation:
            cached = await self.speculator.get_cached_speculation(query)
            if cached and cached.is_ready:
                latency = time.perf_counter() - start_time
                self.metrics.record_execution("speculative", latency)
                logger.info(f"Speculative cache hit: {latency:.3f}s")
                return cached.response, pattern
        
        # Execute through appropriate path
        executor = FastPathExecutor()
        
        if pattern.is_fast_path:
            response = await executor.execute_fast_path(query)
            path_type = "fast"
        else:
            response = await executor.execute_normal_path(query)
            path_type = "normal"
        
        # Record metrics
        latency = time.perf_counter() - start_time
        self.metrics.record_execution(path_type, latency)
        
        logger.info(
            f"Routed through {path_type} path: {latency:.3f}s "
            f"(pattern: {pattern.pattern_type})"
        )
        
        return response, pattern


# Global router instance
_router_instance: Optional[FastPathRouter] = None


def get_fast_path_router(
    config: Optional[FastPathConfig] = None
) -> FastPathRouter:
    """Get global fast path router instance"""
    global _router_instance
    if _router_instance is None:
        _router_instance = FastPathRouter(config)
    return _router_instance