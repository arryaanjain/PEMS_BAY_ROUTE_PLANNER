"""Route optimization API endpoints."""

from fastapi import APIRouter, HTTPException
from ..schemas import OptimizeRouteRequest, OptimizedRoute
from ..services.route_optimizer import get_route_optimizer
from ..services.maps import is_in_pems_bay

router = APIRouter(prefix="/routes", tags=["routes"])


@router.post("/optimize", response_model=OptimizedRoute)
async def optimize_route(request: OptimizeRouteRequest):
    """
    Optimize a route with multiple waypoints using CNN traffic predictions.
    
    This endpoint:
    1. Validates all waypoints are in PEMS Bay region
    2. Generates all possible route permutations (N!)
    3. Uses CNN model to predict traffic for each route variant
    4. Selects the best route based on congestion and travel time
    5. Generates a detailed itinerary with arrival/departure times
    6. Provides traffic warnings and recommendations
    """
    # Validate all waypoints are in PEMS Bay
    for waypoint in request.waypoints:
        if not is_in_pems_bay(waypoint.lat, waypoint.lng):
            raise HTTPException(
                status_code=422,
                detail=f"Waypoint '{waypoint.name}' is outside the PEMS Bay region",
            )
    
    # Get CNN-powered optimizer
    optimizer = get_route_optimizer()
    
    # Optimize the route using CNN traffic predictions
    optimized_route = await optimizer.optimize_route(
        waypoints=request.waypoints,
        start_time=request.startTime,
        duration=request.duration,
        duration_type=request.durationType,
    )
    
    return optimized_route
