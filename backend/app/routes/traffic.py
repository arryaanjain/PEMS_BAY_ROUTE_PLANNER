"""Traffic prediction API endpoints."""

from fastapi import APIRouter, Query
from ..schemas import TrafficPrediction, TrafficHeatmapResponse, HeatmapPoint
from ..config import settings
import random

router = APIRouter(prefix="/traffic", tags=["traffic"])


@router.get("/predict", response_model=TrafficPrediction)
async def predict_traffic(
    fromLat: float = Query(...),
    fromLng: float = Query(...),
    toLat: float = Query(...),
    toLng: float = Query(...),
    time: str = Query(...),
):
    """
    Predict traffic for a specific route segment.
    
    TODO: Integrate with PEMS dataset for real predictions.
    Currently returns mock data based on time heuristics.
    """
    from datetime import datetime
    
    # Parse time
    try:
        dt = datetime.fromisoformat(time.replace("Z", "+00:00"))
        hour = dt.hour
    except:
        hour = 12
    
    # Simple heuristic based on time
    if 7 <= hour <= 9 or 16 <= hour <= 19:
        traffic_level = "heavy"
        congestion_score = 0.75 + random.random() * 0.2
        travel_time = 45
    elif hour < 6 or hour > 21:
        traffic_level = "light"
        congestion_score = 0.1 + random.random() * 0.2
        travel_time = 20
    else:
        traffic_level = "moderate"
        congestion_score = 0.4 + random.random() * 0.2
        travel_time = 30
    
    segment_id = f"seg_{fromLat:.4f}_{fromLng:.4f}_to_{toLat:.4f}_{toLng:.4f}"
    
    return TrafficPrediction(
        segmentId=segment_id,
        travelTime=travel_time,
        trafficLevel=traffic_level,
        congestionScore=min(congestion_score, 1.0),
        confidence=0.75,
    )


@router.get("/heatmap", response_model=TrafficHeatmapResponse)
async def get_traffic_heatmap(
    time: str = Query(...),
    duration: int = Query(1, description="Hours to aggregate"),
):
    """
    Get traffic heatmap for PEMS Bay region.
    
    TODO: Integrate with PEMS dataset for real heatmap data.
    Currently returns mock grid data.
    """
    from datetime import datetime
    
    # Parse time
    try:
        dt = datetime.fromisoformat(time.replace("Z", "+00:00"))
        hour = dt.hour
    except:
        hour = 12
    
    # Generate mock grid data
    grid = []
    lat_step = 0.05
    lng_step = 0.05
    
    lat = settings.pems_bay_min_lat
    while lat <= settings.pems_bay_max_lat:
        lng = settings.pems_bay_min_lng
        while lng <= settings.pems_bay_max_lng:
            # Random traffic based on time
            if 7 <= hour <= 9 or 16 <= hour <= 19:
                traffic_level = random.choice(["moderate", "heavy", "heavy"])
                score = 0.5 + random.random() * 0.4
            elif hour < 6 or hour > 21:
                traffic_level = "light"
                score = 0.1 + random.random() * 0.3
            else:
                traffic_level = random.choice(["light", "moderate"])
                score = 0.3 + random.random() * 0.3
            
            grid.append(
                HeatmapPoint(
                    lat=round(lat, 4),
                    lng=round(lng, 4),
                    trafficLevel=traffic_level,
                    congestionScore=min(score, 1.0),
                )
            )
            lng += lng_step
        lat += lat_step
    
    return TrafficHeatmapResponse(
        time=time,
        region={
            "bbox": [
                settings.pems_bay_min_lat,
                settings.pems_bay_min_lng,
                settings.pems_bay_max_lat,
                settings.pems_bay_max_lng,
            ]
        },
        grid=grid[:100],  # Limit to 100 points for demo
    )
