"""Google Maps API service for location autocomplete, geocoding, and validation."""

import httpx
from typing import List, Optional
from ..config import settings
from ..schemas import LocationSuggestion, Coordinates


# PEMS Bay Area boundaries
PEMS_BAY_CENTER = f"{settings.pems_bay_center_lat},{settings.pems_bay_center_lng}"
PEMS_BAY_RADIUS = int(settings.pems_bay_radius_km * 1000)  # Convert km to meters


def is_in_pems_bay(lat: float, lng: float) -> bool:
    """Check if coordinates are within PEMS Bay bounding box."""
    return (
        settings.pems_bay_min_lat <= lat <= settings.pems_bay_max_lat
        and settings.pems_bay_min_lng <= lng <= settings.pems_bay_max_lng
    )


async def fetch_google_autocomplete(query: str) -> List[LocationSuggestion]:
    """
    Calls Google Places Autocomplete API, restricted to PEMS Bay area.
    Returns list of location suggestions with coordinates.
    """
    if len(query) < 2:
        return []
    
    GOOGLE_PLACES_URL = "https://maps.googleapis.com/maps/api/place/autocomplete/json"
    
    params = {
        "input": query,
        "key": settings.google_maps_api_key,
        "location": PEMS_BAY_CENTER,
        "radius": PEMS_BAY_RADIUS,
        "strictbounds": True,  # Restricts results to this region
        "types": "geocode|establishment",  # Get addresses, businesses, etc.
    }
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(GOOGLE_PLACES_URL, params=params)
            response.raise_for_status()
        except httpx.HTTPError as e:
            print(f"Google Autocomplete API error: {e}")
            return []
    
    data = response.json()
    
    if data.get("status") != "OK":
        error_message = data.get("error_message", "No error message provided")
        print(f"Google API status: {data.get('status')}")
        print(f"Google API error: {error_message}")
        print(f"API key (first 10 chars): {settings.google_maps_api_key[:10]}...")
        return []
    
    predictions = data.get("predictions", [])
    
    # Fetch coordinates for each suggestion
    suggestions = []
    async with httpx.AsyncClient(timeout=10.0) as client:
        for pred in predictions[:10]:  # Limit to 10 suggestions
            place_id = pred["place_id"]
            details = await fetch_place_details(client, place_id)
            
            if details and "lat" in details and "lng" in details:
                # Validate it's actually in PEMS Bay
                if is_in_pems_bay(details["lat"], details["lng"]):
                    suggestions.append(
                        LocationSuggestion(
                            id=place_id,
                            name=pred["structured_formatting"].get("main_text", ""),
                            address=pred["description"],
                            lat=details["lat"],
                            lng=details["lng"],
                        )
                    )
    
    return suggestions


async def fetch_place_details(
    client: httpx.AsyncClient, place_id: str
) -> Optional[dict]:
    """Helper to get lat/lng from a place_id."""
    GOOGLE_DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"
    
    params = {
        "place_id": place_id,
        "key": settings.google_maps_api_key,
        "fields": "geometry",
    }
    
    try:
        response = await client.get(GOOGLE_DETAILS_URL, params=params)
        response.raise_for_status()
    except httpx.HTTPError as e:
        print(f"Google Place Details API error: {e}")
        return None
    
    data = response.json()
    
    if data.get("status") != "OK":
        return None
    
    result = data.get("result", {})
    if "geometry" in result and "location" in result["geometry"]:
        return result["geometry"]["location"]  # Returns {"lat": ..., "lng": ...}
    
    return None


async def geocode_location(address: str) -> Optional[LocationSuggestion]:
    """
    Geocode an address string to get coordinates.
    Returns None if location is not in PEMS Bay region.
    """
    GOOGLE_GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"
    
    params = {
        "address": address,
        "key": settings.google_maps_api_key,
        "bounds": f"{settings.pems_bay_min_lat},{settings.pems_bay_min_lng}|"
        f"{settings.pems_bay_max_lat},{settings.pems_bay_max_lng}",
    }
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(GOOGLE_GEOCODE_URL, params=params)
            response.raise_for_status()
        except httpx.HTTPError as e:
            print(f"Google Geocoding API error: {e}")
            return None
    
    data = response.json()
    
    if data.get("status") != "OK" or not data.get("results"):
        return None
    
    result = data["results"][0]
    location = result["geometry"]["location"]
    lat, lng = location["lat"], location["lng"]
    
    # Validate it's in PEMS Bay
    if not is_in_pems_bay(lat, lng):
        return None
    
    return LocationSuggestion(
        id=result.get("place_id", ""),
        name=result.get("formatted_address", "").split(",")[0],
        address=result.get("formatted_address", ""),
        lat=lat,
        lng=lng,
    )


async def validate_location(
    name: str, coordinates: Optional[Coordinates] = None
) -> tuple[bool, Optional[LocationSuggestion], Optional[str]]:
    """
    Validate if a location is within PEMS Bay region.
    
    Returns:
        (valid, location, message)
    """
    # If coordinates provided, check them directly
    if coordinates:
        if is_in_pems_bay(coordinates.lat, coordinates.lng):
            # Try to enrich with name from reverse geocoding if needed
            return (
                True,
                LocationSuggestion(
                    id=f"coord_{coordinates.lat}_{coordinates.lng}",
                    name=name,
                    address=name,
                    lat=coordinates.lat,
                    lng=coordinates.lng,
                ),
                None,
            )
        else:
            return (False, None, "This location is outside the PEMS Bay region")
    
    # Otherwise, geocode the name
    location = await geocode_location(name)
    
    if location:
        return (True, location, None)
    else:
        return (
            False,
            None,
            "Location not found or is outside the PEMS Bay region",
        )
