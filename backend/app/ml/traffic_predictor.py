# Traffic Prediction Service using CNN Model
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
import logging
from dataclasses import dataclass

from .model_loader import get_traffic_model
from .sensor_mapper import get_sensor_mapper, SensorLocation

logger = logging.getLogger(__name__)


@dataclass
class TrafficPrediction:
    """Traffic prediction for a specific sensor and time"""
    sensor_id: int
    timestamp: datetime
    predicted_speed_mph: float
    confidence: float
    traffic_level: str  # "light", "moderate", "heavy"


class TrafficPredictor:
    """
    Uses CNN model to predict traffic conditions
    """
    
    def __init__(self):
        self.model = get_traffic_model()
        self.mapper = get_sensor_mapper()
        
        # Traffic level thresholds (mph)
        self.HEAVY_THRESHOLD = 35  # < 35 mph = heavy
        self.MODERATE_THRESHOLD = 50  # 35-50 mph = moderate, > 50 = light
    
    def _classify_traffic_level(self, speed_mph: float) -> str:
        """Classify traffic based on speed"""
        if speed_mph < self.HEAVY_THRESHOLD:
            return "heavy"
        elif speed_mph < self.MODERATE_THRESHOLD:
            return "moderate"
        else:
            return "light"
    
    def _get_historical_data(self, sensor_indices: List[int], 
                            reference_time: datetime) -> np.ndarray:
        """
        Get historical traffic data for the past hour (12 time steps)
        
        Args:
            sensor_indices: List of sensor array indices
            reference_time: The time to predict from
        
        Returns:
            Array of shape (12, n_sensors) with historical speed data
        
        NOTE: This is a placeholder. In production, you would:
        1. Query a database with historical PEMS data
        2. Use the actual speeds from the past hour
        3. Handle missing data gracefully
        
        For now, we'll use simulated data based on time of day
        """
        n_steps = 12
        n_sensors = 325
        
        # Create a matrix for all sensors
        historical_data = np.zeros((n_steps, n_sensors))
        
        # Simulate speeds based on time of day
        hour = reference_time.hour
        
        # Rush hour simulation (lower speeds)
        if 7 <= hour <= 9 or 16 <= hour <= 19:
            base_speed = 40  # mph during rush hour
            variation = 10
        else:
            base_speed = 60  # mph off-peak
            variation = 15
        
        # Fill with simulated data
        for step in range(n_steps):
            # Add some time-based variation
            time_factor = np.sin(step / n_steps * np.pi)
            speeds = base_speed + variation * time_factor + np.random.normal(0, 5, n_sensors)
            speeds = np.clip(speeds, 0, 70)  # Reasonable speed range
            historical_data[step, :] = speeds
        
        # Normalize using the scaler
        historical_normalized = self.model.normalize_speeds(historical_data)
        
        return historical_normalized
    
    def predict_route_traffic(self, 
                             route_segments: List[List[SensorLocation]],
                             start_time: datetime) -> Dict[str, any]:
        """
        Predict traffic for all segments in a route
        
        Args:
            route_segments: List of sensor lists, one per route segment
            start_time: When the trip starts
        
        Returns:
            Dictionary with predictions for each segment
        """
        predictions = []
        current_time = start_time
        
        for segment_idx, segment_sensors in enumerate(route_segments):
            if not segment_sensors:
                continue
            
            # Get sensor indices
            sensor_indices = [s.index for s in segment_sensors]
            
            # Get historical data (past hour)
            historical_data = self._get_historical_data(sensor_indices, current_time)
            
            # Predict next hour
            future_speeds = self.model.predict(historical_data, denormalize=True)
            
            # Extract predictions for the relevant sensors
            segment_predictions = []
            for step_idx in range(future_speeds.shape[0]):
                step_time = current_time + timedelta(minutes=step_idx * 5)
                
                for sensor_idx, sensor in enumerate(segment_sensors):
                    speed = future_speeds[step_idx, sensor.index]
                    
                    segment_predictions.append({
                        'timestamp': step_time.isoformat(),
                        'sensor_id': sensor.sensor_id,
                        'lat': sensor.lat,
                        'lng': sensor.lng,
                        'predicted_speed_mph': float(speed),
                        'traffic_level': self._classify_traffic_level(speed),
                        'step': step_idx
                    })
            
            # Calculate segment average
            avg_speed = np.mean([p['predicted_speed_mph'] for p in segment_predictions])
            min_speed = np.min([p['predicted_speed_mph'] for p in segment_predictions])
            
            # Calculate congestion score (0=free flow, 1=heavy congestion)
            # Clamp to [0, 1] range to handle edge cases
            congestion_score = max(0.0, min(1.0, 1.0 - (avg_speed / 70.0)))
            
            predictions.append({
                'segment_index': segment_idx,
                'sensors': [{'id': s.sensor_id, 'lat': s.lat, 'lng': s.lng} 
                           for s in segment_sensors],
                'predictions': segment_predictions,
                'avg_speed_mph': float(avg_speed),
                'min_speed_mph': float(min_speed),
                'traffic_level': self._classify_traffic_level(avg_speed),
                'congestion_score': float(congestion_score)
            })
            
            # Advance time (assume 15 min per segment for now)
            current_time += timedelta(minutes=15)
        
        return {
            'route_predictions': predictions,
            'start_time': start_time.isoformat(),
            'prediction_horizon_minutes': 60,
            'total_segments': len(predictions)
        }
    
    def compare_route_orders(self,
                            waypoints: List[Dict],  # [{'lat': x, 'lng': y, 'name': z}]
                            start_time: datetime,
                            duration_hours: int) -> Dict:
        """
        Compare all possible route orderings and find the best one
        
        Args:
            waypoints: List of waypoint dicts with lat, lng, name
            start_time: Trip start time
            duration_hours: Total trip duration
        
        Returns:
            Comparison of all route permutations with traffic predictions
        """
        from itertools import permutations
        
        n = len(waypoints)
        if n < 2:
            raise ValueError("Need at least 2 waypoints")
        
        # Generate all permutations
        all_permutations = list(permutations(range(n)))
        logger.info(f"Comparing {len(all_permutations)} route permutations for {n} waypoints")
        
        comparisons = []
        
        for perm_idx, perm in enumerate(all_permutations):
            # Reorder waypoints according to this permutation
            ordered_waypoints = [waypoints[i] for i in perm]
            
            # Get route coordinates
            coords = [(w['lat'], w['lng']) for w in ordered_waypoints]
            
            # Find sensors along this route
            route_sensors = self.mapper.find_route_sensors(coords, sensors_per_segment=5)
            
            # Predict traffic for this route
            predictions = self.predict_route_traffic(route_sensors, start_time)
            
            # Calculate total metrics
            total_distance_approx = self._estimate_route_distance(coords)
            avg_speed = np.mean([seg['avg_speed_mph'] for seg in predictions['route_predictions']])
            total_time_hours = total_distance_approx / avg_speed if avg_speed > 0 else 999
            congestion_score = np.mean([seg['congestion_score'] for seg in predictions['route_predictions']])
            
            # Count congested segments
            congested_segments = sum(
                1 for seg in predictions['route_predictions'] 
                if seg['traffic_level'] == 'heavy'
            )
            
            comparisons.append({
                'route_order': [w['name'] for w in ordered_waypoints],
                'route_indices': list(perm),
                'total_distance_miles': float(total_distance_approx),
                'avg_speed_mph': float(avg_speed),
                'estimated_travel_time_hours': float(total_time_hours),
                'congestion_score': float(congestion_score),
                'congested_segments': congested_segments,
                'segment_predictions': predictions['route_predictions'],
                'fits_duration': total_time_hours <= duration_hours
            })
        
        # Sort by best score (lowest congestion, fastest time)
        comparisons.sort(key=lambda x: (x['congestion_score'], x['estimated_travel_time_hours']))
        
        # Mark the best route
        if comparisons:
            comparisons[0]['is_optimal'] = True
        
        return {
            'total_comparisons': len(comparisons),
            'best_route': comparisons[0] if comparisons else None,
            'all_routes': comparisons,
            'start_time': start_time.isoformat(),
            'duration_hours': duration_hours
        }
    
    @staticmethod
    def _estimate_route_distance(coords: List[Tuple[float, float]]) -> float:
        """
        Estimate total route distance in miles
        
        Args:
            coords: List of (lat, lng) tuples
        
        Returns:
            Estimated distance in miles
        """
        from .sensor_mapper import SensorMapper
        
        total_km = 0.0
        for i in range(len(coords) - 1):
            lat1, lng1 = coords[i]
            lat2, lng2 = coords[i + 1]
            dist_km = SensorMapper._haversine_distance(lat1, lng1, lat2, lng2)
            total_km += dist_km
        
        # Convert km to miles
        return total_km * 0.621371


# Global predictor instance
_predictor_instance: Optional[TrafficPredictor] = None


def get_traffic_predictor() -> TrafficPredictor:
    """Get or create the global traffic predictor instance"""
    global _predictor_instance
    
    if _predictor_instance is None:
        _predictor_instance = TrafficPredictor()
        logger.info("🚦 Traffic predictor initialized")
    
    return _predictor_instance
