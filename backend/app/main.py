"""FastAPI main application."""

import os
import asyncio
import aiohttp
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routes import locations, routes as route_endpoints
from . import crud  # Keep old CRUD routes for backward compatibility


async def download_pems_dataset():
    """Download PEMS-Bay dataset if it doesn't exist."""
    # Define paths
    ml_models_dir = Path(__file__).parent.parent / "ml_models"
    dataset_path = ml_models_dir / "pems-bay.h5"
    
    # Create ml_models directory if it doesn't exist
    ml_models_dir.mkdir(exist_ok=True)
    
    # Check if dataset already exists
    if dataset_path.exists():
        print(f"✅ PEMS-Bay dataset already exists at: {dataset_path}")
        return
    
    print("📥 Downloading PEMS-Bay traffic dataset...")
    print("This may take a few minutes (file size: ~200MB)...")
    # Zenodo URL for PEMS-Bay dataset
    url = "https://zenodo.org/records/4263971/files/pems-bay.h5?download=1"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                
                # Get total file size for progress tracking
                total_size = int(response.headers.get('content-length', 0))
                
                with open(dataset_path, 'wb') as f:
                    downloaded = 0
                    chunk_size = 8192
                    
                    async for chunk in response.content.iter_chunked(chunk_size):
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Show progress every 10MB
                        if downloaded % (10 * 1024 * 1024) < chunk_size:
                            if total_size > 0:
                                progress = (downloaded / total_size) * 100
                                print(f"Downloaded: {progress:.1f}% ({downloaded / (1024*1024):.1f} MB)")
                            else:
                                print(f"Downloaded: {downloaded / (1024*1024):.1f} MB")
        
        print(f"✅ Dataset downloaded successfully to: {dataset_path}")
        print(f"File size: {dataset_path.stat().st_size / (1024*1024):.1f} MB")
        
    except Exception as e:
        print(f"❌ Failed to download dataset: {e}")
        print("The application will continue, but CNN model training will not work without the dataset.")
        print("You can manually download it later using:")
        print(f"wget -N {url} -O {dataset_path}")


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


@app.on_event("startup")
async def startup_event():
    """Run startup tasks when the application starts."""
    print("\n🚀 Starting PEMS Bay Route Planner API...")
    print("=" * 50)
    
    # Download PEMS-Bay dataset if needed
    await download_pems_dataset()
    
    print("\n✅ Startup complete! API is ready.")
    print("=" * 50)

