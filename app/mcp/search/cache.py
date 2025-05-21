"""
Cache implementation for the MCP Server.
"""

import json
import hashlib
import logging
import time
from typing import Dict, Any, Optional, Union, List
from functools import wraps

import redis
from cachetools import LRUCache

from app.mcp.config import settings

# Set up logging
logger = logging.getLogger("mcp.search.cache")

class SearchCache:
    """
    Search result cache implementation.
    Supports both in-memory caching and Redis caching.
    """
    
    def __init__(self):
        """
        Initialize the search cache.
        """
        self.enabled = settings.cache.enabled
        
        # Initialize in-memory cache
        self.memory_cache = LRUCache(maxsize=settings.cache.max_cache_size)
        
        # Initialize Redis connection if configured
        self.redis_client = None
        if settings.cache.redis_url:
            try:
                self.redis_client = redis.from_url(settings.cache.redis_url)
                logger.info("Redis cache connection established")
            except Exception as e:
                logger.error(f"Error connecting to Redis: {str(e)}")
                logger.warning("Falling back to in-memory cache only")
    
    def _generate_key(self, query: str, **params) -> str:
        """
        Generate a cache key for a search query and parameters.
        
        Args:
            query: The search query
            **params: Additional search parameters
            
        Returns:
            str: The cache key
        """
        # Create a string representation of the query and parameters
        key_parts = [
            f"query:{query}"
        ]
        
        # Add sorted parameters to ensure consistent key generation
        for k, v in sorted(params.items()):
            key_parts.append(f"{k}:{v}")
        
        key_string = "|".join(key_parts)
        
        # Hash the key for storage
        return f"search:{hashlib.md5(key_string.encode()).hexdigest()}"
    
    def get(self, query: str, **params) -> Optional[Dict[str, Any]]:
        """
        Get a cached search result.
        
        Args:
            query: The search query
            **params: Additional search parameters
            
        Returns:
            Optional[Dict[str, Any]]: The cached result, or None if not found
        """
        if not self.enabled:
            return None
            
        # Generate the cache key
        key = self._generate_key(query, **params)
        
        # Try memory cache first
        if key in self.memory_cache:
            logger.debug(f"Cache hit (memory) for key: {key}")
            return self.memory_cache[key]
        
        # Then try Redis if available
        if self.redis_client:
            try:
                cached_data = self.redis_client.get(key)
                if cached_data:
                    # Deserialize and cache in memory too
                    result = json.loads(cached_data)
                    self.memory_cache[key] = result
                    logger.debug(f"Cache hit (Redis) for key: {key}")
                    return result
            except Exception as e:
                logger.error(f"Error retrieving from Redis cache: {str(e)}")
        
        logger.debug(f"Cache miss for key: {key}")
        return None
    
    def set(self, query: str, result: Dict[str, Any], **params) -> None:
        """
        Cache a search result.
        
        Args:
            query: The search query
            result: The search result to cache
            **params: Additional search parameters
        """
        if not self.enabled:
            return
            
        # Generate the cache key
        key = self._generate_key(query, **params)
        
        # Cache in memory
        self.memory_cache[key] = result
        
        # Cache in Redis if available
        if self.redis_client:
            try:
                # Serialize and store with TTL
                serialized = json.dumps(result)
                self.redis_client.setex(
                    key, 
                    settings.cache.ttl_seconds,
                    serialized
                )
                logger.debug(f"Result cached in Redis for key: {key}")
            except Exception as e:
                logger.error(f"Error storing in Redis cache: {str(e)}")
        
        logger.debug(f"Result cached in memory for key: {key}")
    
    def clear(self, query: Optional[str] = None, **params) -> None:
        """
        Clear cached results.
        
        Args:
            query: The search query to clear (None to clear all)
            **params: Additional search parameters
        """
        if not self.enabled:
            return
            
        if query is None:
            # Clear all cache
            self.memory_cache.clear()
            
            if self.redis_client:
                try:
                    self.redis_client.flushdb()
                    logger.info("Redis cache cleared")
                except Exception as e:
                    logger.error(f"Error clearing Redis cache: {str(e)}")
            
            logger.info("All cache cleared")
        else:
            # Clear specific query
            key = self._generate_key(query, **params)
            
            if key in self.memory_cache:
                del self.memory_cache[key]
            
            if self.redis_client:
                try:
                    self.redis_client.delete(key)
                    logger.debug(f"Redis cache entry cleared for key: {key}")
                except Exception as e:
                    logger.error(f"Error clearing Redis cache entry: {str(e)}")
            
            logger.debug(f"Cache cleared for key: {key}")

# Create a global cache instance
cache = SearchCache()

def cached_search(func):
    """
    Decorator to cache search results.
    
    Args:
        func: The search function to decorate
        
    Returns:
        Decorated function with caching
    """
    @wraps(func)
    def wrapper(self, query: str, *args, **kwargs):
        # Try to get from cache
        cached_result = cache.get(query, **kwargs)
        if cached_result:
            return cached_result
        
        # Execute the search function
        result = func(self, query, *args, **kwargs)
        
        # Cache the result
        cache.set(query, result, **kwargs)
        
        return result
    
    return wrapper 