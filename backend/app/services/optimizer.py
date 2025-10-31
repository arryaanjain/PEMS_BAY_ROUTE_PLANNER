"""Route optimization service using TSP solver and traffic predictions."""

import itertools
from datetime import datetime, timedelta
from typing import List, Tuple
from ..schemas import (
    Waypoint,
    OptimizedRoute,
    ItineraryDay,
    ItineraryStop,
    RouteSegment,
    Warning,
    Recommendation,
)


def calculate_distance(wp1: Waypoint, wp2: Waypoint) -> float:
    """
    Calculate approximate distance between two waypoints using Haversine formula.
    Returns distance in kilometers.
    """
    import math
    
    lat1, lon1 = math.radians(wp1.lat), math.radians(wp1.lng)
    lat2, lon2 = math.radians(wp2.lat), math.radians(wp2.lng)
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))
    
    # Earth radius in kilometers
    r = 6371
    
    return c * r


def estimate_travel_time(distance_km: float, traffic_level: str = "moderate") -> int:
    """
    Estimate travel time in minutes based on distance and traffic.
    
    Traffic multipliers:
    - light: 1.0x (60 km/h average)
    - moderate: 1.3x (46 km/h average)
    - heavy: 1.8x (33 km/h average)
    """
    base_speed_kmh = 60  # Base speed in km/h
    
    traffic_multipliers = {
        "light": 1.0,
        "moderate": 1.3,
        "heavy": 1.8,
    }
    
    multiplier = traffic_multipliers.get(traffic_level, 1.3)
    time_hours = (distance_km / base_speed_kmh) * multiplier
    
    return max(int(time_hours * 60), 5)  # At least 5 minutes


def predict_traffic_level(hour: int) -> str:
    """Simple heuristic for traffic prediction based on time of day."""
    # Peak hours: 7-9 AM and 4-7 PM
    if 7 <= hour <= 9 or 16 <= hour <= 19:
        return "heavy"
    # Light traffic: late night and early morning
    elif hour < 6 or hour > 21:
        return "light"
    else:
        return "moderate"


def solve_tsp_nearest_neighbor(
    waypoints: List[Waypoint], start_idx: int = 0
) -> List[int]:
    """
    Solve TSP using nearest neighbor heuristic.
    Returns indices of waypoints in optimal order.
    """
    n = len(waypoints)
    visited = [False] * n
    route = [start_idx]
    visited[start_idx] = True
    
    current_idx = start_idx
    
    for _ in range(n - 1):
        nearest_idx = -1
        min_distance = float("inf")
        
        for i in range(n):
            if not visited[i]:
                distance = calculate_distance(waypoints[current_idx], waypoints[i])
                if distance < min_distance:
                    min_distance = distance
                    nearest_idx = i
        
        route.append(nearest_idx)
        visited[nearest_idx] = True
        current_idx = nearest_idx
    
    return route


async def optimize_route(
    waypoints: List[Waypoint],
    start_time_str: str,
    duration: int,
    duration_type: str,
) -> OptimizedRoute:
    """
    Optimize route using TSP solver and generate detailed itinerary.
    """
    # Parse start time
    try:
        start_time = datetime.fromisoformat(start_time_str.replace("Z", "+00:00"))
    except:
        start_time = datetime.now()
    
    # Solve TSP to get optimal order
    optimal_order = solve_tsp_nearest_neighbor(waypoints)
    reordered_waypoints = [waypoints[i] for i in optimal_order]
    
    # Generate itinerary and segments
    itinerary_days = []
    segments = []
    warnings = []
    recommendations = []
    
    current_time = start_time
    total_travel_time = 0
    
    # Calculate total duration in hours
    total_hours = duration if duration_type == "hours" else duration * 24
    
    # Time spent at each stop (1 hour default)
    stop_duration = 60  # minutes
    
    # Generate itinerary
    day_num = 1
    current_day_stops = []
    current_day_start = current_time.date()
    
    for idx, wp in enumerate(reordered_waypoints):
        # Check if we've moved to a new day
        if current_time.date() != current_day_start:
            if current_day_stops:
                itinerary_days.append(
                    ItineraryDay(
                        day=day_num,
                        date=current_day_start.isoformat(),
                        stops=current_day_stops,
                    )
                )
            day_num += 1
            current_day_start = current_time.date()
            current_day_stops = []
        
        if idx == 0:
            # First waypoint - departure only
            current_day_stops.append(
                ItineraryStop(
                    time=current_time.strftime("%H:%M"),
                    type="depart",
                    location=wp.name,
                    insight="Starting your journey",
                )
            )
            current_time += timedelta(minutes=stop_duration)
        else:
            # Calculate travel from previous waypoint
            prev_wp = reordered_waypoints[idx - 1]
            distance = calculate_distance(prev_wp, wp)
            
            # Predict traffic based on time
            traffic_level = predict_traffic_level(current_time.hour)
            travel_time = estimate_travel_time(distance, traffic_level)
            total_travel_time += travel_time
            
            # Arrive at current waypoint
            current_time += timedelta(minutes=travel_time)
            
            segment_id = f"seg_{idx - 1}_{idx}"
            segments.append(
                RouteSegment(
                    id=segment_id,
                    from_location=prev_wp,
                    to=wp,
                    predictedTravelTime=travel_time,
                    trafficCondition=traffic_level,
                    congestionScore=0.2
                    if traffic_level == "light"
                    else 0.5
                    if traffic_level == "moderate"
                    else 0.8,
                    timeWindow={
                        "start": (current_time - timedelta(minutes=travel_time)).isoformat(),
                        "end": current_time.isoformat(),
                    },
                )
            )
            
            # Generate insight
            insight = f"Travel time: {travel_time} min"
            if traffic_level == "heavy":
                insight = f"⚠️ Heavy traffic expected. {insight}"
                warnings.append(
                    Warning(
                        severity="high",
                        message=f"Heavy congestion expected near {wp.name} around {current_time.strftime('%I:%M %p')}",
                        location=wp.name,
                        timeWindow={
                            "start": current_time.isoformat(),
                            "end": (current_time + timedelta(hours=1)).isoformat(),
                        },
                    )
                )
            
            current_day_stops.append(
                ItineraryStop(
                    time=current_time.strftime("%H:%M"),
                    type="arrive",
                    location=wp.name,
                    segmentId=segment_id,
                    travelTime=travel_time,
                    insight=insight,
                    trafficLevel=traffic_level,
                )
            )
            
            # Depart from current waypoint (if not last)
            if idx < len(reordered_waypoints) - 1:
                current_time += timedelta(minutes=stop_duration)
                current_day_stops.append(
                    ItineraryStop(
                        time=current_time.strftime("%H:%M"),
                        type="depart",
                        location=wp.name,
                    )
                )
    
    # Add last day
    if current_day_stops:
        itinerary_days.append(
            ItineraryDay(
                day=day_num,
                date=current_day_start.isoformat(),
                stops=current_day_stops,
            )
        )
    
    # Generate recommendations
    if any(s.trafficCondition == "heavy" for s in segments):
        recommendations.append(
            Recommendation(
                type="timing",
                message="Consider starting 30-60 minutes earlier to avoid peak traffic",
            )
        )
    
    return OptimizedRoute(
        optimizedOrder=optimal_order,
        recommendedStart=start_time.isoformat(),
        totalTravelTime=total_travel_time,
        insights={
            "warnings": [w.model_dump() for w in warnings],
            "recommendations": [r.model_dump() for r in recommendations],
        },
        itinerary=itinerary_days,
        segments=segments,
    )
