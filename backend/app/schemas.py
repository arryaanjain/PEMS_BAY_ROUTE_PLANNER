"""Pydantic schemas for request/response models."""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


# ========== Location Schemas ==========

class Coordinates(BaseModel):
    """Geographic coordinates."""
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)


class LocationSuggestion(BaseModel):
    """Autocomplete suggestion for a location."""
    id: str
    name: str
    address: str
    lat: float
    lng: float


class LocationValidateRequest(BaseModel):
    """Request to validate a location."""
    name: str
    coordinates: Optional[Coordinates] = None


class LocationValidateResponse(BaseModel):
    """Response from location validation."""
    valid: bool
    location: Optional[LocationSuggestion] = None
    message: Optional[str] = None


# ========== Waypoint Schemas ==========

class Waypoint(BaseModel):
    """A waypoint/stop in a route."""
    id: str
    name: str
    lat: float
    lng: float


# ========== Route Optimization Schemas ==========

class OptimizeRouteRequest(BaseModel):
    """Request to optimize a route."""
    waypoints: list[Waypoint] = Field(..., min_length=2)
    startTime: str  # ISO datetime string
    duration: int = Field(..., gt=0)
    durationType: Literal["hours", "days"]


class TrafficWarning(BaseModel):
    """Traffic or route warning."""
    severity: Literal["low", "medium", "high"]
    message: str
    location: Optional[str] = None
    timeWindow: Optional[dict] = None


# Alias for backwards compatibility
Warning = TrafficWarning


class Recommendation(BaseModel):
    """Route recommendation."""
    type: str
    message: str


class ItineraryStop(BaseModel):
    """A stop in the itinerary."""
    time: str
    type: Literal["arrive", "depart"]
    location: str
    segmentId: Optional[str] = None
    travelTime: Optional[int] = None  # minutes
    insight: Optional[str] = None
    trafficLevel: Optional[Literal["light", "moderate", "heavy"]] = None


class ItineraryDay(BaseModel):
    """A day in the itinerary."""
    day: int
    date: str
    stops: list[ItineraryStop]


class RouteSegment(BaseModel):
    """A segment between two waypoints."""
    id: str
    fromLocation: dict  # {name, lat, lng}
    toLocation: dict    # {name, lat, lng}
    predictedTravelTime: int  # minutes
    trafficCondition: Literal["light", "moderate", "heavy"]
    congestionScore: float = Field(..., ge=0, le=1)
    timeWindow: dict
    
    class Config:
        populate_by_name = True


class OptimizedRoute(BaseModel):
    """Optimized route response."""
    optimizedOrder: list[int]  # indices of waypoints
    recommendedStart: str  # ISO datetime
    totalTravelTime: int  # minutes
    insights: dict  # Contains warnings and recommendations
    itinerary: list[ItineraryDay]
    segments: list[RouteSegment]


# ========== Traffic Schemas ==========

class TrafficPredictionRequest(BaseModel):
    """Request for traffic prediction."""
    fromLat: float
    fromLng: float
    toLat: float
    toLng: float
    time: str  # ISO datetime


class TrafficPrediction(BaseModel):
    """Traffic prediction for a segment."""
    segmentId: str
    travelTime: int  # minutes
    trafficLevel: Literal["light", "moderate", "heavy"]
    congestionScore: float = Field(..., ge=0, le=1)
    confidence: float = Field(..., ge=0, le=1)


class HeatmapPoint(BaseModel):
    """A point in the traffic heatmap."""
    lat: float
    lng: float
    trafficLevel: Literal["light", "moderate", "heavy"]
    congestionScore: float


class TrafficHeatmapResponse(BaseModel):
    """Traffic heatmap response."""
    time: str
    region: dict  # bounding box
    grid: list[HeatmapPoint]


# ========== Trip Schemas ==========

class TripBase(BaseModel):
    """Base trip schema."""
    title: str
    date: str
    stops: int
    waypoints: list[Waypoint]
    startTime: str
    duration: int
    durationType: Literal["hours", "days"]


class TripCreate(TripBase):
    """Schema for creating a trip."""
    optimizedRoute: OptimizedRoute


class Trip(TripBase):
    """Complete trip schema with ID."""
    id: str
    optimizedRoute: OptimizedRoute
    
    class Config:
        from_attributes = True


class TripListItem(BaseModel):
    """Abbreviated trip info for listings."""
    id: str
    title: str
    date: str
    stops: int
    createdAt: Optional[str] = None


# ========== Legacy Item Schemas (from sample CRUD) ==========

class ItemCreate(BaseModel):
    title: str
    description: Optional[str] = None


class ItemRead(ItemCreate):
    id: int

    class Config:
        orm_mode = True

