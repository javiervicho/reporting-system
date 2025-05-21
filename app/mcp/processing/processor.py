"""
Search result processor for the MCP Server.
"""

import logging
import re
from typing import Dict, List, Any, Optional, Union

from app.mcp.search.google_client import GoogleSearchClient

# Set up logging
logger = logging.getLogger("mcp.processing.processor")

class SearchResultProcessor:
    """
    Processor for search results with advanced filtering and ranking.
    """
    
    def __init__(self, search_client: Optional[GoogleSearchClient] = None):
        """
        Initialize the search result processor.
        
        Args:
            search_client: Google Search client (creates a new one if not provided)
        """
        self.search_client = search_client or GoogleSearchClient()
        logger.info("Search result processor initialized")
    
    def process_query(
        self, 
        query: str, 
        num_results: int = 10,
        filter_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        min_relevance_score: float = 0.0,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Process a search query with advanced filtering and ranking.
        
        Args:
            query: The search query
            num_results: Number of results to return
            filter_domains: Only include results from these domains
            exclude_domains: Exclude results from these domains
            min_relevance_score: Minimum relevance score (0.0-1.0)
            **kwargs: Additional parameters to pass to the search
            
        Returns:
            Dict[str, Any]: Processed search results
        """
        # Execute the search
        raw_results = self.search_client.search(query, num_results=num_results, **kwargs)
        
        # Process and filter the results
        processed_results = self._process_raw_results(
            raw_results,
            query=query,
            filter_domains=filter_domains,
            exclude_domains=exclude_domains,
            min_relevance_score=min_relevance_score
        )
        
        return processed_results
    
    def _process_raw_results(
        self,
        raw_results: Dict[str, Any],
        query: str,
        filter_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        min_relevance_score: float = 0.0
    ) -> Dict[str, Any]:
        """
        Process and filter raw search results.
        
        Args:
            raw_results: Raw search results from Google API
            query: The original search query
            filter_domains: Only include results from these domains
            exclude_domains: Exclude results from these domains
            min_relevance_score: Minimum relevance score
            
        Returns:
            Dict[str, Any]: Processed search results
        """
        processed_data = {
            "query": query,
            "totalResults": int(raw_results.get("searchInformation", {}).get("totalResults", "0")),
            "searchTime": float(raw_results.get("searchInformation", {}).get("searchTime", "0")),
            "formattedSearchTime": raw_results.get("searchInformation", {}).get("formattedSearchTime", ""),
            "items": []
        }
        
        # If no items, return early
        if "items" not in raw_results:
            return processed_data
        
        # Process each item
        for item in raw_results["items"]:
            # Calculate relevance score
            relevance_score = self._calculate_relevance_score(item, query)
            
            # Skip if below minimum relevance
            if relevance_score < min_relevance_score:
                continue
            
            # Skip if domain not in filter list (if specified)
            if filter_domains:
                if not any(domain in item.get("displayLink", "") for domain in filter_domains):
                    continue
            
            # Skip if domain in exclude list (if specified)
            if exclude_domains:
                if any(domain in item.get("displayLink", "") for domain in exclude_domains):
                    continue
            
            # Add processed item
            processed_item = self._process_item(item, relevance_score)
            processed_data["items"].append(processed_item)
        
        # Sort by relevance score
        processed_data["items"].sort(key=lambda x: x["relevanceScore"], reverse=True)
        
        return processed_data
    
    def _process_item(self, item: Dict[str, Any], relevance_score: float) -> Dict[str, Any]:
        """
        Process a single search result item.
        
        Args:
            item: The search result item
            relevance_score: The calculated relevance score
            
        Returns:
            Dict[str, Any]: Processed item
        """
        processed_item = {
            "title": item.get("title", ""),
            "link": item.get("link", ""),
            "displayLink": item.get("displayLink", ""),
            "snippet": item.get("snippet", ""),
            "htmlSnippet": item.get("htmlSnippet", ""),
            "relevanceScore": relevance_score,
            "domain": item.get("displayLink", "").split(".", 1)[0] if "." in item.get("displayLink", "") else item.get("displayLink", ""),
        }
        
        # Extract image if available
        if "pagemap" in item:
            if "cse_image" in item["pagemap"]:
                processed_item["image"] = item["pagemap"]["cse_image"][0].get("src", "")
            
            if "metatags" in item["pagemap"]:
                meta_tags = item["pagemap"]["metatags"][0]
                processed_item["metaDescription"] = meta_tags.get("og:description", meta_tags.get("description", ""))
        
        return processed_item
    
    def _calculate_relevance_score(self, item: Dict[str, Any], query: str) -> float:
        """
        Calculate a relevance score for a search result.
        
        Args:
            item: The search result item
            query: The original search query
            
        Returns:
            float: Relevance score (0.0-1.0)
        """
        score = 0.0
        
        # Split query into terms
        query_terms = re.findall(r'\w+', query.lower())
        
        # Check title
        title = item.get("title", "").lower()
        title_score = 0.0
        for term in query_terms:
            if term in title:
                title_score += 0.2
                # Extra points for exact match in title
                if term == title:
                    title_score += 0.3
        score += min(0.5, title_score)  # Max 0.5 for title
        
        # Check snippet
        snippet = item.get("snippet", "").lower()
        snippet_score = 0.0
        for term in query_terms:
            if term in snippet:
                snippet_score += 0.1
        score += min(0.3, snippet_score)  # Max 0.3 for snippet
        
        # Check domain/URL relevance
        link = item.get("link", "").lower()
        display_link = item.get("displayLink", "").lower()
        domain_score = 0.0
        for term in query_terms:
            if term in display_link:
                domain_score += 0.1
            if term in link:
                domain_score += 0.05
        score += min(0.2, domain_score)  # Max 0.2 for domain/URL
        
        return min(1.0, score)  # Ensure max score is 1.0 