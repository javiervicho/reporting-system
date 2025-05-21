"""
API endpoints for the MCP Server search functionality.
"""

from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from pydantic import BaseModel, Field

from app.mcp.processing.processor import SearchResultProcessor
from app.mcp.search.cache import cache

router = APIRouter()

class SearchQuery(BaseModel):
    """Request model for search queries."""
    query: str = Field(..., description="The search query")
    num_results: int = Field(10, description="Number of results to return", ge=1, le=50)
    filter_domains: Optional[List[str]] = Field(None, description="Only include results from these domains")
    exclude_domains: Optional[List[str]] = Field(None, description="Exclude results from these domains")
    min_relevance_score: float = Field(0.0, description="Minimum relevance score (0.0-1.0)", ge=0.0, le=1.0)
    language: Optional[str] = Field(None, description="Language for results (e.g., 'en')")
    safe_search: Optional[str] = Field(None, description="Safe search setting (off, medium, high)")

class SearchResult(BaseModel):
    """Model for a single search result."""
    title: str
    link: str
    displayLink: str
    snippet: str
    htmlSnippet: Optional[str] = None
    relevanceScore: float
    domain: str
    image: Optional[str] = None
    metaDescription: Optional[str] = None

class SearchResponse(BaseModel):
    """Response model for search queries."""
    query: str
    totalResults: int
    searchTime: float
    formattedSearchTime: str
    items: List[SearchResult]

class CacheOperation(BaseModel):
    """Request model for cache operations."""
    query: Optional[str] = Field(None, description="The search query to clear (None to clear all)")

# Dependency to get the search processor
def get_search_processor() -> SearchResultProcessor:
    """Get the search processor instance."""
    return SearchResultProcessor()

@router.post("/", response_model=SearchResponse)
async def search(
    request: SearchQuery,
    processor: SearchResultProcessor = Depends(get_search_processor)
):
    """
    Perform a search query through the MCP Server.
    """
    try:
        # Process the search query
        result = processor.process_query(
            query=request.query,
            num_results=request.num_results,
            filter_domains=request.filter_domains,
            exclude_domains=request.exclude_domains,
            min_relevance_score=request.min_relevance_score,
            language=request.language,
            safe_search=request.safe_search
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@router.get("/", response_model=SearchResponse)
async def search_get(
    query: str = Query(..., description="The search query"),
    num_results: int = Query(10, description="Number of results to return", ge=1, le=50),
    processor: SearchResultProcessor = Depends(get_search_processor)
):
    """
    Simple GET endpoint for search queries.
    """
    try:
        # Process the search query
        result = processor.process_query(
            query=query,
            num_results=num_results
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@router.post("/cache/clear")
async def clear_cache(request: CacheOperation):
    """
    Clear the search cache for a specific query or all queries.
    """
    try:
        cache.clear(request.query)
        if request.query:
            return {"message": f"Cache cleared for query: {request.query}"}
        else:
            return {"message": "All cache cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cache error: {str(e)}")

@router.get("/health")
async def health_check():
    """
    Health check endpoint for the MCP Server.
    """
    return {
        "status": "healthy",
        "service": "MCP Server",
        "cacheEnabled": cache.enabled
    } 