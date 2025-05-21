"""
Configuration for the MCP Server for Google Search.
"""

import os
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

class GoogleSearchSettings(BaseModel):
    """Settings for Google Search API."""
    api_key: str = Field(..., description="Google Custom Search API Key")
    custom_search_engine_id: str = Field(..., description="Google Custom Search Engine ID")
    api_version: str = Field("v1", description="Google Custom Search API version")
    max_results_per_query: int = Field(10, description="Maximum number of results per query")
    result_language: str = Field("en", description="Preferred language for search results")
    safe_search: str = Field("off", description="Safe search setting (off, medium, high)")
    
class CacheSettings(BaseModel):
    """Settings for search result caching."""
    enabled: bool = Field(True, description="Whether caching is enabled")
    redis_url: Optional[str] = Field(None, description="Redis connection URL for caching")
    ttl_seconds: int = Field(3600, description="Time-to-live for cache entries in seconds")
    max_cache_size: int = Field(1000, description="Maximum number of items in the cache")

class RateLimitSettings(BaseModel):
    """Settings for rate limiting."""
    max_requests_per_day: int = Field(100, description="Maximum number of requests per day")
    max_requests_per_minute: int = Field(5, description="Maximum number of requests per minute")
    retry_backoff_factor: float = Field(2.0, description="Backoff factor for retries")
    max_retries: int = Field(3, description="Maximum number of retries")

class MCPServerSettings(BaseSettings):
    """Main settings for the MCP Server."""
    google_search: GoogleSearchSettings
    cache: CacheSettings = CacheSettings()
    rate_limit: RateLimitSettings = RateLimitSettings()
    
    # Server settings
    server_host: str = Field("0.0.0.0", description="Host to bind the server to")
    server_port: int = Field(8080, description="Port to run the server on")
    debug_mode: bool = Field(False, description="Whether to run in debug mode")
    
    # Logging settings
    log_level: str = Field("INFO", description="Logging level")
    log_file: Optional[str] = Field(None, description="Log file path")
    
    class Config:
        env_file = ".env"
        env_prefix = "MCP_"
        case_sensitive = False
        
def get_settings() -> MCPServerSettings:
    """
    Get the settings for the MCP Server.
    
    Returns:
        MCPServerSettings: The server settings
    """
    # Get Google Search settings from environment variables
    google_search_settings = GoogleSearchSettings(
        api_key=os.getenv("MCP_GOOGLE_SEARCH_API_KEY", ""),
        custom_search_engine_id=os.getenv("MCP_GOOGLE_SEARCH_CSE_ID", ""),
        api_version=os.getenv("MCP_GOOGLE_SEARCH_API_VERSION", "v1"),
        max_results_per_query=int(os.getenv("MCP_GOOGLE_SEARCH_MAX_RESULTS", "10")),
        result_language=os.getenv("MCP_GOOGLE_SEARCH_LANGUAGE", "en"),
        safe_search=os.getenv("MCP_GOOGLE_SEARCH_SAFE_SEARCH", "off"),
    )
    
    # Create and return the settings object
    return MCPServerSettings(
        google_search=google_search_settings
    )

# Global settings instance
settings = get_settings() 