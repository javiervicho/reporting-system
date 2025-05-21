"""
Google Search API client implementation for the MCP Server.
"""

import json
import logging
from typing import Dict, List, Any, Optional, Union

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from tenacity import retry, stop_after_attempt, wait_exponential

from app.mcp.config import settings
from app.mcp.search.cache import cached_search

# Set up logging
logger = logging.getLogger("mcp.search.google_client")

class GoogleSearchClient:
    """
    Client for the Google Custom Search API.
    """
    
    def __init__(self, api_key: Optional[str] = None, cse_id: Optional[str] = None):
        """
        Initialize the Google Search client.
        
        Args:
            api_key: Google API key (uses settings if not provided)
            cse_id: Custom Search Engine ID (uses settings if not provided)
        """
        self.api_key = api_key or settings.google_search.api_key
        self.cse_id = cse_id or settings.google_search.custom_search_engine_id
        
        if not self.api_key:
            raise ValueError("Google API key is required")
        
        if not self.cse_id:
            raise ValueError("Custom Search Engine ID is required")
        
        self.service = build(
            "customsearch", 
            settings.google_search.api_version,
            developerKey=self.api_key
        )
        logger.info("Google Search client initialized")
    
    @cached_search
    @retry(
        stop=stop_after_attempt(settings.rate_limit.max_retries),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        reraise=True
    )
    def search(
        self, 
        query: str, 
        num_results: int = None,
        start_index: int = 1,
        language: str = None,
        safe_search: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Perform a Google search query.
        
        Args:
            query: The search query
            num_results: Number of results to return (default from settings)
            start_index: Start index for pagination
            language: Language for results (default from settings)
            safe_search: Safe search setting (default from settings)
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Dict[str, Any]: The search results
        """
        try:
            # Set defaults from settings if not provided
            if num_results is None:
                num_results = settings.google_search.max_results_per_query
            
            if language is None:
                language = settings.google_search.result_language
                
            if safe_search is None:
                safe_search = settings.google_search.safe_search
            
            # Build the search parameters
            search_params = {
                "q": query,
                "cx": self.cse_id,
                "num": min(num_results, 10),  # API max is 10 results per request
                "start": start_index,
                "lr": f"lang_{language}",
                "safe": safe_search
            }
            
            # Add any additional parameters
            search_params.update(kwargs)
            
            # Execute the search
            logger.debug(f"Executing search query: {query}")
            result = self.service.cse().list(**search_params).execute()
            
            logger.info(f"Search completed, found {result.get('searchInformation', {}).get('totalResults', 0)} results")
            return result
            
        except HttpError as e:
            error_details = json.loads(e.content.decode())
            logger.error(f"Google Search API error: {error_details}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during search: {str(e)}")
            raise
    
    def get_formatted_results(self, query: str, num_results: int = None) -> List[Dict[str, Any]]:
        """
        Get search results in a simplified, formatted structure.
        
        Args:
            query: The search query
            num_results: Number of results to return
            
        Returns:
            List[Dict[str, Any]]: Formatted search results
        """
        # Get the raw search results
        search_results = self.search(query, num_results=num_results)
        
        # Extract and format the items
        formatted_results = []
        
        if "items" in search_results:
            for item in search_results["items"]:
                formatted_item = {
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                    "displayLink": item.get("displayLink", ""),
                    "formattedUrl": item.get("formattedUrl", "")
                }
                
                # Add image if available
                if "pagemap" in item and "cse_image" in item["pagemap"]:
                    formatted_item["image"] = item["pagemap"]["cse_image"][0].get("src", "")
                
                formatted_results.append(formatted_item)
        
        return formatted_results 