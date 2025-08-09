"""
Smart caching layer for performance optimization
"""
import json
import hashlib
import logging
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import re
import sys

import numpy as np

try:
    import aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class CacheConfig:
    """Configuration for cache manager"""
    redis_url: str = "redis://localhost:6379"
    default_ttl: int = 300  # 5 minutes
    semantic_threshold: float = 0.85  # Similarity threshold
    max_cache_size_mb: float = 100  # Max cache size in MB
    enable_warming: bool = True
    morning_pattern_ttl: int = 7200  # 2 hours for morning patterns
    coach_response_ttl: int = 3600  # 1 hour for coach responses
    mcp_data_ttl: int = 300  # 5 minutes for MCP data
    personal_content_ttl: int = 86400  # 24 hours for personal content


@dataclass
class CacheEntry:
    """Single cache entry"""
    key: str
    value: Any
    timestamp: str
    ttl: int
    hit_count: int = 0
    size_bytes: int = 0
    embedding: Optional[List[float]] = None


class CacheManager:
    """Smart caching layer with Redis backend"""

    def __init__(self, config: Optional[CacheConfig] = None):
        """Initialize cache manager"""
        self.config = config or CacheConfig()
        self.redis = None
        self.enabled = False
        self.stats = {
            "hits": 0,
            "misses": 0,
            "writes": 0,
            "errors": 0,
            "total_size_bytes": 0
        }

        # Initialize embedding model for semantic similarity
        self.embedding_model = None
        if EMBEDDINGS_AVAILABLE:
            try:
                # Use a small, fast model for embeddings
                self.embedding_model = SentenceTransformer(
                    'all-MiniLM-L6-v2'
                )
            except Exception as e:
                logger.warning(f"Failed to load embedding model: {e}")

    async def initialize(self):
        """Initialize Redis connection"""
        if not REDIS_AVAILABLE:
            logger.warning("Redis not available, caching disabled")
            return

        try:
            self.redis = await aioredis.from_url(
                self.config.redis_url,
                encoding="utf-8",
                decode_responses=True
            )

            # Test connection
            await self.redis.ping()
            self.enabled = True
            logger.info("Cache manager initialized successfully")

        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e}")
            self.enabled = False

    async def get(self, namespace: str, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.enabled:
            self.stats["misses"] += 1
            return None

        try:
            cache_key = generate_cache_key(namespace, key)

            # Check TTL first
            ttl = await self.redis.ttl(cache_key)
            if ttl == -2:  # Key doesn't exist
                self.stats["misses"] += 1
                return None

            # Get cached value
            cached_data = await self.redis.get(cache_key)
            if not cached_data:
                self.stats["misses"] += 1
                return None

            # Parse cache entry
            entry_data = json.loads(cached_data)
            # Handle both dict format and direct value storage
            if isinstance(entry_data, dict) and "value" in entry_data:
                value = entry_data["value"]
                # Update hit count if possible
                if "hit_count" in entry_data:
                    entry_data["hit_count"] += 1
                    await self.redis.set(
                        cache_key,
                        json.dumps(entry_data),
                        ex=ttl if ttl > 0 else self.config.default_ttl
                    )
            else:
                value = entry_data

            self.stats["hits"] += 1
            return value

        except Exception as e:
            logger.error(f"Cache get error: {e}")
            self.stats["errors"] += 1
            return None

    async def set(
        self,
        namespace: str,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache"""
        if not self.enabled:
            return False

        try:
            cache_key = generate_cache_key(namespace, key)
            ttl = ttl or self.config.default_ttl

            # Check size limit
            value_json = json.dumps(value) if not isinstance(value, str) else value
            size_bytes = sys.getsizeof(value_json)

            if size_bytes > self.config.max_cache_size_mb * 1024 * 1024:
                logger.warning(f"Cache entry too large: {size_bytes} bytes")
                return False

            # Create cache entry
            entry = CacheEntry(
                key=cache_key,
                value=value,
                timestamp=datetime.now().isoformat(),
                ttl=ttl,
                hit_count=0,
                size_bytes=size_bytes
            )

            # Add embedding if text value
            if isinstance(value, str) and self.embedding_model:
                try:
                    embedding = self.embedding_model.encode(value).tolist()
                    entry.embedding = embedding
                except Exception as e:
                    logger.warning(f"Failed to generate embedding: {e}")

            # Store in Redis
            await self.redis.set(
                cache_key,
                json.dumps(asdict(entry)),
                ex=ttl
            )

            self.stats["writes"] += 1
            self.stats["total_size_bytes"] += size_bytes
            return True

        except Exception as e:
            logger.error(f"Cache set error: {e}")
            self.stats["errors"] += 1
            return False

    async def get_semantic(
        self,
        namespace: str,
        query: str,
        threshold: Optional[float] = None
    ) -> Optional[Any]:
        """Get semantically similar cached response"""
        if not self.enabled or not self.embedding_model:
            return None

        threshold = threshold or self.config.semantic_threshold

        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query)

            # Search all keys in namespace
            pattern = f"{namespace}:*"
            keys = await self.redis.keys(pattern)

            best_match = None
            best_similarity = 0

            for key in keys:
                cached_data = await self.redis.get(key)
                if not cached_data:
                    continue

                entry_data = json.loads(cached_data)

                # Check if has embedding
                if "embedding" not in entry_data or not entry_data["embedding"]:
                    continue

                # Calculate similarity
                cached_embedding = np.array(entry_data["embedding"])
                similarity = semantic_similarity(query_embedding, cached_embedding)

                if similarity > best_similarity and similarity >= threshold:
                    best_similarity = similarity
                    best_match = entry_data["value"]

            if best_match:
                self.stats["hits"] += 1
                logger.debug(
                    f"Semantic cache hit with similarity {best_similarity:.3f}"
                )
            else:
                self.stats["misses"] += 1

            return best_match

        except Exception as e:
            logger.error(f"Semantic cache error: {e}")
            self.stats["errors"] += 1
            return None

    async def delete(self, namespace: str, key: str) -> bool:
        """Delete entry from cache"""
        if not self.enabled:
            return False

        try:
            cache_key = generate_cache_key(namespace, key)
            result = await self.redis.delete(cache_key)
            return result > 0
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False

    async def clear_namespace(self, namespace: str) -> int:
        """Clear all entries in a namespace"""
        if not self.enabled:
            return 0

        try:
            pattern = f"{namespace}:*"
            keys = await self.redis.keys(pattern)

            if keys:
                deleted = await self.redis.delete(*keys)
                return deleted
            return 0

        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return 0

    async def warm_cache(self, patterns: List[Tuple[str, str]]):
        """Warm cache with common patterns"""
        if not self.enabled or not self.config.enable_warming:
            return

        logger.info(f"Warming cache with {len(patterns)} patterns")

        for query, response in patterns:
            await self.set(
                "morning_pattern",
                query,
                response,
                ttl=self.config.morning_pattern_ttl
            )

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total = self.stats["hits"] + self.stats["misses"]
        hit_rate = self.stats["hits"] / total if total > 0 else 0

        return {
            "enabled": self.enabled,
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "hit_rate": hit_rate,
            "writes": self.stats["writes"],
            "errors": self.stats["errors"],
            "total_size_mb": self.stats["total_size_bytes"] / (1024 * 1024)
        }

    # Convenience methods for specific data types

    async def get_coach_response(self, query: str) -> Optional[str]:
        """Get cached coach response"""
        # Try exact match first
        response = await self.get("coach_response", query)
        if response:
            return response

        # Try semantic similarity
        return await self.get_semantic("coach_response", query)

    async def set_coach_response(self, query: str, response: str):
        """Cache coach response"""
        await self.set(
            "coach_response",
            query,
            response,
            ttl=self.config.coach_response_ttl
        )

    async def get_mcp_data(self, data_type: str, user_id: str) -> Optional[Any]:
        """Get cached MCP data"""
        return await self.get(f"mcp_{data_type}", user_id)

    async def set_mcp_data(
        self,
        data_type: str,
        user_id: str,
        data: Any,
        ttl: Optional[int] = None
    ):
        """Cache MCP data with appropriate TTL"""
        ttl = ttl or self.config.mcp_data_ttl
        await self.set(f"mcp_{data_type}", user_id, data, ttl=ttl)

    async def get_personal_content(
        self,
        content_type: str,
        user_id: str
    ) -> Optional[str]:
        """Get cached personal content"""
        return await self.get(f"personal_{content_type}", user_id)

    async def set_personal_content(
        self,
        content_type: str,
        user_id: str,
        content: str,
        ttl: Optional[int] = None
    ):
        """Cache personal content with long TTL"""
        ttl = ttl or self.config.personal_content_ttl
        await self.set(f"personal_{content_type}", user_id, content, ttl=ttl)


def semantic_similarity(embedding1: np.ndarray, embedding2: np.ndarray) -> float:
    """Calculate cosine similarity between two embeddings"""
    # Normalize vectors
    norm1 = embedding1 / np.linalg.norm(embedding1)
    norm2 = embedding2 / np.linalg.norm(embedding2)

    # Calculate cosine similarity
    similarity = np.dot(norm1, norm2)

    return float(similarity)


def generate_cache_key(namespace: str, key: str) -> str:
    """Generate a cache key from namespace and key"""
    # Clean the key
    clean_key = re.sub(r'[^a-zA-Z0-9_]', '_', key.lower())
    clean_key = re.sub(r'_+', '_', clean_key)  # Remove multiple underscores

    # Truncate if too long
    if len(clean_key) > 100:
        # Use hash for long keys
        key_hash = hashlib.md5(key.encode()).hexdigest()[:8]
        clean_key = clean_key[:90] + "_" + key_hash

    return f"{namespace}:{clean_key}"


# Global cache instance
_cache_instance: Optional[CacheManager] = None


def get_cache() -> CacheManager:
    """Get global cache instance"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = CacheManager()
    return _cache_instance


async def initialize_cache(config: Optional[CacheConfig] = None):
    """Initialize global cache"""
    global _cache_instance
    _cache_instance = CacheManager(config)
    await _cache_instance.initialize()
    return _cache_instance
