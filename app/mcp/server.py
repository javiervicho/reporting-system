"""
Main MCP Server FastAPI application.
"""

import logging
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from app.mcp.api.search import router as search_router
from app.mcp.config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ]
)

if settings.log_file:
    file_handler = logging.FileHandler(settings.log_file)
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    logging.getLogger().addHandler(file_handler)

logger = logging.getLogger("mcp.server")

# Create FastAPI app
app = FastAPI(
    title="MCP Server for Google Search",
    description="Master Control Program Server for Google Search API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests and responses."""
    request_id = str(time.time())
    logger.info(f"Request {request_id}: {request.method} {request.url.path}")
    
    start_time = time.time()
    
    try:
        response = await call_next(request)
        
        process_time = time.time() - start_time
        logger.info(f"Response {request_id}: {response.status_code} (took {process_time:.4f}s)")
        
        return response
    except Exception as e:
        logger.error(f"Error {request_id}: {str(e)}")
        return JSONResponse(
            status_code=500, 
            content={"detail": "Internal server error"}
        )

# Add router for search endpoints
app.include_router(search_router, prefix="/api/search", tags=["search"])

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "MCP Server for Google Search",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "search": "/api/search/",
            "health": "/api/search/health",
        }
    }

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "MCP Server for Google Search"
    }

def run_server():
    """Run the MCP server."""
    import uvicorn
    
    logger.info(f"Starting MCP Server on {settings.server_host}:{settings.server_port}")
    uvicorn.run(
        "app.mcp.server:app", 
        host=settings.server_host, 
        port=settings.server_port,
        reload=settings.debug_mode
    )

if __name__ == "__main__":
    run_server() 