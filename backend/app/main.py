"""FastAPI main application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routes import locations, routes as route_endpoints
from . import crud  # Keep old CRUD routes for backward compatibility


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="PEMS Bay Route Planner API",
        description="Route optimization API for the PEMS Bay Area with traffic predictions",
        version="1.0.0",
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(locations.router, prefix="/api")
    app.include_router(route_endpoints.router, prefix="/api")
    
    # Legacy CRUD routes (from sample app)
    # app.include_router(crud_router, prefix="/api")
    
    @app.get("/")
    async def root():
        """Health check endpoint."""
        return {
            "status": "ok",
            "message": "PEMS Bay Route Planner API",
            "version": "1.0.0",
        }
    
    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {"status": "healthy"}
    
    return app


app = create_app()

