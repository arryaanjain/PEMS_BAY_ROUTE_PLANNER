"""Test script to verify Google Maps API configuration."""

import os
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

print("=" * 60)
print("Google Maps API Configuration Test")
print("=" * 60)

# Check if API key is set
if not GOOGLE_MAPS_API_KEY:
    print("❌ ERROR: GOOGLE_MAPS_API_KEY is not set in .env file")
    print("\nPlease:")
    print("1. Copy backend/.env.example to backend/.env")
    print("2. Add your Google Maps API key to backend/.env")
    print("3. Get API key from: https://console.cloud.google.com/apis/credentials")
    exit(1)

print(f"✓ API Key is set")
print(f"  Length: {len(GOOGLE_MAPS_API_KEY)} characters")
print(f"  Prefix: {GOOGLE_MAPS_API_KEY[:10]}...")

# Test Places API Autocomplete
print("\n" + "=" * 60)
print("Testing Places API Autocomplete")
print("=" * 60)

GOOGLE_PLACES_URL = "https://maps.googleapis.com/maps/api/place/autocomplete/json"

params = {
    "input": "San Francisco",
    "key": GOOGLE_MAPS_API_KEY,
    "location": "37.7749,-122.4194",
    "radius": 50000,
}

try:
    response = httpx.get(GOOGLE_PLACES_URL, params=params, timeout=10.0)
    data = response.json()
    
    print(f"Status Code: {response.status_code}")
    print(f"API Status: {data.get('status')}")
    
    if data.get("status") == "REQUEST_DENIED":
        print("\n❌ REQUEST_DENIED - Common causes:")
        print("1. API key is invalid")
        print("2. Places API is not enabled in Google Cloud Console")
        print("3. API key has IP/HTTP referrer restrictions")
        print("4. Billing is not set up for the project")
        
        if "error_message" in data:
            print(f"\nError message from Google: {data['error_message']}")
        
        print("\n📋 Steps to fix:")
        print("1. Go to https://console.cloud.google.com/apis/library")
        print("2. Enable 'Places API'")
        print("3. Enable 'Geocoding API'")
        print("4. Go to https://console.cloud.google.com/apis/credentials")
        print("5. Check your API key restrictions")
        print("6. Ensure billing is enabled for your project")
        
    elif data.get("status") == "OK":
        predictions = data.get("predictions", [])
        print(f"✓ Success! Got {len(predictions)} predictions")
        if predictions:
            print("\nFirst prediction:")
            print(f"  - {predictions[0]['description']}")
    else:
        print(f"⚠️  Unexpected status: {data.get('status')}")
        if "error_message" in data:
            print(f"Error: {data['error_message']}")
    
    print("\nFull response:")
    print(data)
    
except Exception as e:
    print(f"❌ Error making request: {e}")

print("\n" + "=" * 60)
