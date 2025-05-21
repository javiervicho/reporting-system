#!/usr/bin/env python
"""
Script to run the MCP Server for Google Search.
"""

import os
import sys
import argparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run the MCP Server for Google Search")
    
    parser.add_argument(
        "--host",
        type=str,
        help="Host to bind the server to (overrides MCP_SERVER_HOST env variable)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        help="Port to run the server on (overrides MCP_SERVER_PORT env variable)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Run in debug mode (enables auto-reload)"
    )
    
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level"
    )
    
    parser.add_argument(
        "--log-file",
        type=str,
        help="Log file path"
    )
    
    return parser.parse_args()

def main():
    """Main entry point."""
    args = parse_args()
    
    # Override environment variables with command line arguments
    if args.host:
        os.environ["MCP_SERVER_HOST"] = args.host
    
    if args.port:
        os.environ["MCP_SERVER_PORT"] = str(args.port)
    
    if args.debug:
        os.environ["MCP_DEBUG_MODE"] = "true"
    
    if args.log_level:
        os.environ["MCP_LOG_LEVEL"] = args.log_level
    
    if args.log_file:
        os.environ["MCP_LOG_FILE"] = args.log_file
    
    # Check for Google API key
    if "MCP_GOOGLE_SEARCH_API_KEY" not in os.environ:
        print("Error: MCP_GOOGLE_SEARCH_API_KEY environment variable is not set.")
        print("Please set it in your .env file or export it in your shell.")
        sys.exit(1)
    
    # Check for Custom Search Engine ID
    if "MCP_GOOGLE_SEARCH_CSE_ID" not in os.environ:
        print("Error: MCP_GOOGLE_SEARCH_CSE_ID environment variable is not set.")
        print("Please set it in your .env file or export it in your shell.")
        sys.exit(1)
    
    # Import and run the server (import here to ensure env vars are set first)
    from app.mcp.server import run_server
    run_server()

if __name__ == "__main__":
    main() 