from fastapi import APIRouter

from app.api.v1.endpoints import incidents, coordinator
from app.mcp.api.search import router as mcp_search_router

api_router = APIRouter()

api_router.include_router(incidents.router, prefix="/incidents", tags=["incidents"])
api_router.include_router(coordinator.router, prefix="/coordinator", tags=["coordinator"])
api_router.include_router(mcp_search_router, prefix="/mcp/search", tags=["mcp-search"])

# Additional routers can be added here as the application grows
# Example: api_router.include_router(users.router, prefix="/users", tags=["users"]) 