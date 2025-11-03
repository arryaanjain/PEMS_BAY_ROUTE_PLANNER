# Route Optimization Service with CNN Traffic Predictions
from datetime import datetime, timedelta
from typing import List, Dict
import logging

from ..schemas import Waypoint, OptimizedRoute, ItineraryDay, ItineraryStop, RouteSegment, TrafficWarning
from ..ml.traffic_predictor import get_traffic_predictor

logger = logging.getLogger(__name__)


class RouteOptimizer:
    """
    Optimizes routes using CNN traffic predictions
    """
    
    def __init__(self):
        self.predictor = get_traffic_predictor()
    
    async def optimize_route(self,
                            waypoints: List[Waypoint],
                            start_time: str,
                            duration: int,
                            duration_type: str) -> OptimizedRoute:
        """
        Optimize route order based on traffic predictions
        
        Args:
            waypoints: List of destinations
            start_time: ISO datetime string
            duration: Trip duration
            duration_type: "hours" or "days"
        
        Returns:
            OptimizedRoute with best order and traffic insights
        """
        logger.info(f"Optimizing route for {len(waypoints)} waypoints")
        
        # Parse start time
        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        
        # Convert duration to hours
        total_hours = duration if duration_type == "hours" else duration * 24
        
        # Prepare waypoint data
        waypoint_dicts = [
            {'lat': wp.lat, 'lng': wp.lng, 'name': wp.name}
            for wp in waypoints
        ]
        
        # Compare all possible routes using CNN predictions
        comparison_result = self.predictor.compare_route_orders(
            waypoint_dicts,
            start_dt,
            total_hours
        )
        
        best_route = comparison_result['best_route']
        
        if not best_route:
            raise ValueError("No valid route found")
        
        # Build the optimized route response
        optimized_indices = best_route['route_indices']
        ordered_waypoints = [waypoints[i] for i in optimized_indices]
        
        # Generate itinerary from predictions
        itinerary = self._build_itinerary(
            ordered_waypoints,
            best_route['segment_predictions'],
            start_dt,
            duration,
            duration_type
        )
        
        # Generate route segments
        segments = self._build_segments(
            ordered_waypoints,
            best_route['segment_predictions']
        )
        
        # Generate warnings
        warnings = self._generate_warnings(
            best_route['segment_predictions'],
            ordered_waypoints
        )
        
        # Determine recommended start time
        recommended_start = start_dt
        if best_route['congestion_score'] > 0.7:
            # Suggest starting earlier to avoid heavy traffic
            recommended_start = start_dt - timedelta(hours=1)
        
        return OptimizedRoute(
            optimizedOrder=optimized_indices,
            recommendedStart=recommended_start.isoformat(),
            totalTravelTime=int(best_route['estimated_travel_time_hours'] * 60),
            insights={
                'warnings': warnings,
                'recommendations': self._generate_recommendations(best_route, comparison_result)
            },
            itinerary=itinerary,
            segments=segments
        )
    
    def _build_itinerary(self,
                        ordered_waypoints: List[Waypoint],
                        segment_predictions: List[Dict],
                        start_dt: datetime,
                        duration: int,
                        duration_type: str) -> List[ItineraryDay]:
        """Build day-by-day itinerary"""
        itinerary = []
        current_time = start_dt
        current_day = 1
        day_stops = []
        
        # Add departure from first location
        day_stops.append(ItineraryStop(
            time=current_time.strftime("%H:%M"),
            type="depart",
            location=ordered_waypoints[0].name,
            insight="Starting your journey"
        ))
        
        # Process each segment
        for idx, wp in enumerate(ordered_waypoints[1:], 1):
            # Get segment prediction
            if idx - 1 < len(segment_predictions):
                seg_pred = segment_predictions[idx - 1]
                avg_speed = seg_pred['avg_speed_mph']
                traffic_level = seg_pred['traffic_level']
                
                # Estimate travel time (simplified)
                distance_miles = seg_pred.get('distance_miles', 10)  # Default 10 miles
                travel_minutes = int((distance_miles / avg_speed) * 60) if avg_speed > 0 else 30
            else:
                travel_minutes = 30
                traffic_level = "moderate"
            
            # Arrive at destination
            current_time += timedelta(minutes=travel_minutes)
            
            insight = self._get_traffic_insight(traffic_level, travel_minutes)
            
            day_stops.append(ItineraryStop(
                time=current_time.strftime("%H:%M"),
                type="arrive",
                location=wp.name,
                travelTime=travel_minutes,
                insight=insight,
                trafficLevel=traffic_level
            ))
            
            # Add stay time (1 hour per stop)
            current_time += timedelta(hours=1)
            
            # Depart (unless it's the last stop)
            if idx < len(ordered_waypoints) - 1:
                day_stops.append(ItineraryStop(
                    time=current_time.strftime("%H:%M"),
                    type="depart",
                    location=wp.name
                ))
            
            # Check if we need to start a new day
            if current_time.day != start_dt.day or idx == len(ordered_waypoints) - 1:
                itinerary.append(ItineraryDay(
                    day=current_day,
                    date=start_dt.strftime("%Y-%m-%d"),
                    stops=day_stops
                ))
                current_day += 1
                day_stops = []
                start_dt = current_time
        
        return itinerary if itinerary else [ItineraryDay(
            day=1,
            date=start_dt.strftime("%Y-%m-%d"),
            stops=day_stops
        )]
    
    def _build_segments(self,
                       ordered_waypoints: List[Waypoint],
                       segment_predictions: List[Dict]) -> List[RouteSegment]:
        """Build route segments with traffic data"""
        segments = []
        
        for idx in range(len(ordered_waypoints) - 1):
            wp_from = ordered_waypoints[idx]
            wp_to = ordered_waypoints[idx + 1]
            
            if idx < len(segment_predictions):
                seg_pred = segment_predictions[idx]
                predicted_time = int((seg_pred.get('distance_miles', 10) / seg_pred['avg_speed_mph']) * 60)
                traffic_condition = seg_pred['traffic_level']
                # Ensure congestion_score is within valid range [0, 1]
                congestion_score = max(0.0, min(1.0, seg_pred['congestion_score']))
            else:
                predicted_time = 30
                traffic_condition = "moderate"
                congestion_score = 0.5
            
            segments.append(RouteSegment(
                id=f"seg_{idx}",
                fromLocation={'name': wp_from.name, 'lat': wp_from.lat, 'lng': wp_from.lng},
                toLocation={'name': wp_to.name, 'lat': wp_to.lat, 'lng': wp_to.lng},
                predictedTravelTime=predicted_time,
                trafficCondition=traffic_condition,
                congestionScore=congestion_score,
                timeWindow={'start': '', 'end': ''}  # Simplified
            ))
        
        return segments
    
    def _generate_warnings(self,
                          segment_predictions: List[Dict],
                          ordered_waypoints: List[Waypoint]) -> List[TrafficWarning]:
        """Generate traffic warnings for congested segments"""
        warnings = []
        
        for idx, seg_pred in enumerate(segment_predictions):
            if seg_pred['traffic_level'] == 'heavy' or seg_pred['congestion_score'] > 0.7:
                if idx < len(ordered_waypoints) - 1:
                    location = ordered_waypoints[idx + 1].name
                    warnings.append(TrafficWarning(
                        severity='high',
                        message=f"Heavy congestion expected near {location}. "
                               f"Average speed: {seg_pred['avg_speed_mph']:.1f} mph"
                    ))
        
        return warnings
    
    def _generate_recommendations(self,
                                 best_route: Dict,
                                 comparison: Dict) -> List[Dict]:
        """Generate route recommendations"""
        recommendations = []
        
        # Compare with other routes
        all_routes = comparison['all_routes']
        if len(all_routes) > 1:
            worst_route = all_routes[-1]
            time_saved = worst_route['estimated_travel_time_hours'] - best_route['estimated_travel_time_hours']
            
            if time_saved > 0.5:
                recommendations.append({
                    'type': 'timing',
                    'message': f"This route saves {time_saved:.1f} hours compared to the worst alternative"
                })
        
        # Suggest off-peak travel if highly congested
        if best_route['congestion_score'] > 0.7:
            recommendations.append({
                'type': 'timing',
                'message': "Consider starting earlier or later to avoid peak traffic"
            })
        
        return recommendations
    
    @staticmethod
    def _get_traffic_insight(traffic_level: str, travel_minutes: int) -> str:
        """Generate insight text based on traffic level"""
        if traffic_level == "light":
            return f"Smooth traffic expected. {travel_minutes} min travel time."
        elif traffic_level == "moderate":
            return f"Moderate traffic. Allow {travel_minutes} min for this segment."
        else:
            return f"Heavy congestion. Expect delays. {travel_minutes}+ min travel time."


# Global optimizer instance
_optimizer_instance = None


def get_route_optimizer() -> RouteOptimizer:
    """Get or create the global route optimizer instance"""
    global _optimizer_instance
    
    if _optimizer_instance is None:
        _optimizer_instance = RouteOptimizer()
        logger.info("🗺️  Route optimizer initialized with CNN model")
    
    return _optimizer_instance
