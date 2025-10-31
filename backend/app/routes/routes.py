"""Route optimization API endpoints."""

from fastapi import APIRouter, HTTPException
from ..schemas import OptimizeRouteRequest, OptimizedRoute
from ..services.optimizer import optimize_route as optimize_route_service
from ..services.maps import is_in_pems_bay

router = APIRouter(prefix="/routes", tags=["routes"])


@router.post("/optimize", response_model=OptimizedRoute)
async def optimize_route(request: OptimizeRouteRequest):
    """
    Optimize a route with multiple waypoints.
    
    This endpoint:
    1. Validates all waypoints are in PEMS Bay region
    2. Solves the Traveling Salesman Problem (TSP) to find optimal order
    3. Predicts traffic for each segment
    4. Generates a detailed itinerary with arrival/departure times
    5. Provides warnings and recommendations
    """
    # Validate all waypoints are in PEMS Bay
    for waypoint in request.waypoints:
        if not is_in_pems_bay(waypoint.lat, waypoint.lng):
            raise HTTPException(
                status_code=422,
                detail=f"Waypoint '{waypoint.name}' is outside the PEMS Bay region",
            )
    
    # Optimize the route
    optimized_route = await optimize_route_service(
        waypoints=request.waypoints,
        start_time_str=request.startTime,
        duration=request.duration,
        duration_type=request.durationType,
    )
    
    return optimized_route
