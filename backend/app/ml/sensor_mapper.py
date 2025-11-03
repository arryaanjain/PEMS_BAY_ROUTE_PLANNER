# Sensor Mapping Service - Map lat/lng to PEMS sensors
import pickle
import numpy as np
from pathlib import Path
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class SensorLocation:
    """Represents a PEMS sensor with location data"""
    sensor_id: int
    index: int  # Array index in the model
    lat: float
    lng: float
    station_id: Optional[str] = None
    freeway: Optional[str] = None


class SensorMapper:
    """
    Maps geographic coordinates to PEMS Bay sensors
    
    Since PEMS dataset doesn't include exact lat/lng, we need to:
    1. Use a sensor metadata file (if available)
    2. Or approximate based on known Bay Area freeway locations
    """
    
    def __init__(self, sensor_metadata_path: Optional[str] = None):
        """
        Initialize sensor mapper
        
        Args:
            sensor_metadata_path: Path to sensor location metadata (CSV/JSON)
        """
        self.sensors: List[SensorLocation] = []
        self.sensor_metadata_path = sensor_metadata_path
        
        # If no metadata, we'll use approximate freeway locations
        self._load_sensor_locations()
    
    def _load_sensor_locations(self):
        """
        Load sensor location data
        
        TODO: You need to provide a mapping file that contains:
        - sensor_id
        - lat, lng coordinates
        - (optional) freeway name, station ID
        
        For now, this creates mock data for demonstration.
        """
        if self.sensor_metadata_path and Path(self.sensor_metadata_path).exists():
            # Load from file
            logger.info(f"Loading sensor metadata from {self.sensor_metadata_path}")
            # TODO: Implement actual loading logic
            pass
        else:
            logger.warning(
                "⚠️  No sensor metadata file found. "
                "Using approximate Bay Area locations."
            )
            self._create_approximate_sensor_grid()
    
    def _create_approximate_sensor_grid(self):
        """
        Create approximate sensor locations based on Bay Area freeway network
        
        This is a placeholder - you should replace with actual sensor locations
        from PeMS metadata or CalTrans data
        """
        # PEMS Bay Area approximate bounding box
        lat_min, lat_max = 37.3, 38.0
        lng_min, lng_max = -122.6, -121.9
        
        # Create a grid of ~325 sensors
        n_sensors = 325
        n_lat = int(np.sqrt(n_sensors * 1.2))
        n_lng = int(n_sensors / n_lat)
        
        lats = np.linspace(lat_min, lat_max, n_lat)
        lngs = np.linspace(lng_min, lng_max, n_lng)
        
        index = 0
        for i, lat in enumerate(lats):
            for j, lng in enumerate(lngs):
                if index >= n_sensors:
                    break
                
                self.sensors.append(SensorLocation(
                    sensor_id=index + 1,  # IDs start at 1
                    index=index,
                    lat=float(lat),
                    lng=float(lng),
                    freeway=f"I-{80 if i % 2 == 0 else 101}"  # Mock freeway
                ))
                index += 1
        
        logger.info(f"Created grid with {len(self.sensors)} sensor locations")
    
    def find_nearest_sensor(self, lat: float, lng: float, k: int = 1) -> List[SensorLocation]:
        """
        Find k nearest sensors to a lat/lng coordinate
        
        Args:
            lat: Latitude
            lng: Longitude
            k: Number of nearest sensors to return
        
        Returns:
            List of nearest SensorLocation objects
        """
        if not self.sensors:
            raise ValueError("No sensor locations loaded")
        
        # Calculate Haversine distance to all sensors
        distances = []
        for sensor in self.sensors:
            dist = self._haversine_distance(lat, lng, sensor.lat, sensor.lng)
            distances.append((dist, sensor))
        
        # Sort by distance and return top k
        distances.sort(key=lambda x: x[0])
        return [sensor for _, sensor in distances[:k]]
    
    @staticmethod
    def _haversine_distance(lat1: float, lng1: float, 
                           lat2: float, lng2: float) -> float:
        """
        Calculate distance between two lat/lng points (in km)
        
        Args:
            lat1, lng1: First point
            lat2, lng2: Second point
        
        Returns:
            Distance in kilometers
        """
        R = 6371  # Earth radius in km
        
        lat1, lng1, lat2, lng2 = map(np.radians, [lat1, lng1, lat2, lng2])
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlng/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        
        return R * c
    
    def find_route_sensors(self, waypoints: List[Tuple[float, float]], 
                          sensors_per_segment: int = 5) -> List[List[SensorLocation]]:
        """
        Find sensors along a route between waypoints
        
        Args:
            waypoints: List of (lat, lng) tuples
            sensors_per_segment: Number of sensors to find per segment
        
        Returns:
            List of sensor lists, one per route segment
        """
        route_sensors = []
        
        for i in range(len(waypoints) - 1):
            start_lat, start_lng = waypoints[i]
            end_lat, end_lng = waypoints[i + 1]
            
            # Interpolate points along the segment
            n_points = sensors_per_segment
            lats = np.linspace(start_lat, end_lat, n_points)
            lngs = np.linspace(start_lng, end_lng, n_points)
            
            segment_sensors = []
            for lat, lng in zip(lats, lngs):
                nearest = self.find_nearest_sensor(lat, lng, k=1)[0]
                # Avoid duplicates
                if not segment_sensors or segment_sensors[-1].sensor_id != nearest.sensor_id:
                    segment_sensors.append(nearest)
            
            route_sensors.append(segment_sensors)
        
        return route_sensors
    
    def get_sensor_by_id(self, sensor_id: int) -> Optional[SensorLocation]:
        """Get sensor by its ID"""
        for sensor in self.sensors:
            if sensor.sensor_id == sensor_id:
                return sensor
        return None
    
    def get_sensor_by_index(self, index: int) -> Optional[SensorLocation]:
        """Get sensor by its array index"""
        if 0 <= index < len(self.sensors):
            return self.sensors[index]
        return None


# Global mapper instance
_mapper_instance: Optional[SensorMapper] = None


def get_sensor_mapper() -> SensorMapper:
    """Get or create the global sensor mapper instance"""
    global _mapper_instance
    
    if _mapper_instance is None:
        # Try to find metadata file
        base_dir = Path(__file__).resolve().parents[2]
        metadata_path = base_dir / "ml_models" / "sensor_locations.csv"
        
        if metadata_path.exists():
            _mapper_instance = SensorMapper(sensor_metadata_path=str(metadata_path))
        else:
            logger.warning(
                f"Sensor metadata not found at {metadata_path}. "
                f"Using approximate grid."
            )
            _mapper_instance = SensorMapper()
    
    return _mapper_instance
