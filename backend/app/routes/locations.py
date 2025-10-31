"""Location-related API endpoints."""

from fastapi import APIRouter, Query, HTTPException
from typing import List
from ..schemas import (
    LocationSuggestion,
    LocationValidateRequest,
    LocationValidateResponse,
)
from ..services.maps import (
    fetch_google_autocomplete,
    validate_location as validate_location_service,
)
from ..config import settings

router = APIRouter(prefix="/locations", tags=["locations"])


@router.get("/config-check")
async def check_config():
    """Diagnostic endpoint to verify API configuration."""
    return {
        "google_maps_api_key_set": bool(settings.google_maps_api_key),
        "api_key_length": len(settings.google_maps_api_key) if settings.google_maps_api_key else 0,
        "api_key_prefix": settings.google_maps_api_key[:10] if settings.google_maps_api_key else "NOT SET",
        "pems_bay_center": f"{settings.pems_bay_center_lat},{settings.pems_bay_center_lng}",
        "pems_bay_radius_km": settings.pems_bay_radius_km,
    }


@router.get("/autocomplete", response_model=List[LocationSuggestion])
async def autocomplete(
    query: str = Query(..., min_length=2, description="Search query")
):
    """
    Get autocomplete suggestions for locations in PEMS Bay region.
    Only returns locations within the defined geographic boundary.
    """
    suggestions = await fetch_google_autocomplete(query)
    return suggestions


@router.post("/validate", response_model=LocationValidateResponse)
async def validate(request: LocationValidateRequest):
    """
    Validate if a location is within the PEMS Bay region.
    Accepts either a name (which will be geocoded) or name + coordinates.
    """
    valid, location, message = await validate_location_service(
        request.name, request.coordinates
    )
    
    return LocationValidateResponse(
        valid=valid,
        location=location,
        message=message,
    )


@router.get("/search", response_model=List[LocationSuggestion])
async def search(
    query: str = Query(..., min_length=2, description="Search query")
):
    """
    Search for specific locations within PEMS Bay.
    Similar to autocomplete but may return more detailed results.
    """
    # For now, use same implementation as autocomplete
    # Can be enhanced later with different Google Maps API calls
    suggestions = await fetch_google_autocomplete(query)
    return suggestions
