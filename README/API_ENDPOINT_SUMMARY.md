# API Endpoint Summary - Route Optimizer

## Current Status: ✅ CNN Integration Active

The route optimization endpoint is now using your **CNN traffic prediction model**!

---

## Endpoint

**POST** `/api/routes/optimize`

**Location**: `backend/app/routes/routes.py`

---

## Request Structure

```json
{
  "waypoints": [
    {
      "id": "1",
      "name": "San Francisco",
      "lat": 37.7749,
      "lng": -122.4194
    },
    {
      "id": "2",
      "name": "Oakland",
      "lat": 37.8044,
      "lng": -122.2712
    },
    {
      "id": "3", 
      "name": "Berkeley",
      "lat": 37.8715,
      "lng": -122.2730
    }
  ],
  "startTime": "2025-11-04T08:00:00Z",
  "duration": 8,
  "durationType": "hours"
}
```

---

## Response Structure

```json
{
  "optimizedOrder": [0, 2, 1],
  "recommendedStart": "2025-11-04T08:00:00Z",
  "totalTravelTime": 120,
  "insights": {
    "warnings": [
      {
        "severity": "high",
        "message": "Heavy congestion expected near Oakland. Average speed: 28.3 mph"
      }
    ],
    "recommendations": [
      {
        "type": "timing",
        "message": "This route saves 0.8 hours compared to the worst alternative"
      }
    ]
  },
  "itinerary": [
    {
      "day": 1,
      "date": "2025-11-04",
      "stops": [
        {
          "time": "08:00",
          "type": "depart",
          "location": "San Francisco",
          "insight": "Starting your journey"
        },
        {
          "time": "08:45",
          "type": "arrive",
          "location": "Berkeley",
          "travelTime": 45,
          "insight": "Moderate traffic. Allow 45 min for this segment.",
          "trafficLevel": "moderate"
        },
        {
          "time": "09:45",
          "type": "depart",
          "location": "Berkeley"
        },
        {
          "time": "10:15",
          "type": "arrive",
          "location": "Oakland",
          "travelTime": 30,
          "insight": "Heavy congestion. Expect delays. 30+ min travel time.",
          "trafficLevel": "heavy"
        }
      ]
    }
  ],
  "segments": [
    {
      "id": "seg_0",
      "fromLocation": {"name": "San Francisco", "lat": 37.7749, "lng": -122.4194},
      "toLocation": {"name": "Berkeley", "lat": 37.8715, "lng": -122.2730},
      "predictedTravelTime": 45,
      "trafficCondition": "moderate",
      "congestionScore": 0.52,
      "timeWindow": {"start": "", "end": ""}
    },
    {
      "id": "seg_1",
      "fromLocation": {"name": "Berkeley", "lat": 37.8715, "lng": -122.2730},
      "toLocation": {"name": "Oakland", "lat": 37.8044, "lng": -122.2712},
      "predictedTravelTime": 30,
      "trafficCondition": "heavy",
      "congestionScore": 0.78,
      "timeWindow": {"start": "", "end": ""}
    }
  ]
}
```

---

## What Happens Behind the Scenes

### 1. **Route Permutation Generation**
For N waypoints → generates **N! route variants**

| Waypoints | Routes Generated | Example |
|-----------|------------------|---------|
| 2 | 2 | AB, BA |
| 3 | 6 | ABC, ACB, BAC, BCA, CAB, CBA |
| 4 | 24 | All permutations |

### 2. **CNN Traffic Prediction**
For each route variant:
- Maps lat/lng coordinates to PEMS Bay sensor indices
- Fetches historical traffic (last hour) from database or simulation
- Feeds to CNN model: Input shape `(12, 325)` = 12 timesteps × 325 sensors
- Gets predictions: Output shape `(12, 325)` = next hour forecast
- Denormalizes speeds (0-70 mph range)

### 3. **Route Scoring**
Each route gets scored on:
- **Average speed** across all segments
- **Congestion score** (0-1 scale)
- **Traffic level** classification:
  - `light`: > 50 mph
  - `moderate`: 35-50 mph  
  - `heavy`: < 35 mph
- **Estimated travel time** in hours

### 4. **Best Route Selection**
Routes sorted by:
1. Lowest congestion score
2. Fastest travel time

Winner becomes the `optimizedOrder` in response.

---

## Files Involved

| File | Purpose |
|------|---------|
| `app/routes/routes.py` | **API endpoint** - validates PEMS Bay region, calls optimizer |
| `app/services/route_optimizer.py` | **Main orchestrator** - builds itinerary, segments, warnings |
| `app/ml/traffic_predictor.py` | **Route comparison** - generates permutations, calls CNN |
| `app/ml/model_loader.py` | **CNN wrapper** - loads model, normalizes/denormalizes data |
| `app/ml/sensor_mapper.py` | **Geo mapping** - converts lat/lng to sensor indices |
| `app/schemas.py` | **Type definitions** - Pydantic models for request/response |

---

## Key Changes Made

### ✅ Updated Endpoint
**Before**: Used simple TSP solver (`optimizer.py`)  
**After**: Uses CNN-powered optimizer (`route_optimizer.py`)

### ✅ Fixed Schema Mismatch
- Renamed `Warning` → `TrafficWarning` (with backwards compatibility alias)
- Changed `RouteSegment` fields from `from_location`/`to` → `fromLocation`/`toLocation`

### ✅ Integration Complete
Endpoint now:
1. Validates waypoints in PEMS Bay region ✅
2. Generates all N! route permutations ✅
3. Uses CNN for traffic predictions ✅
4. Returns best route with detailed itinerary ✅

---

## Testing the Endpoint

```bash
# Start the backend
cd backend
uvicorn app.main:app --reload

# Test with curl
curl -X POST http://localhost:8000/api/routes/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "waypoints": [
      {"id":"1", "name":"SF", "lat":37.7749, "lng":-122.4194},
      {"id":"2", "name":"Oakland", "lat":37.8044, "lng":-122.2712}
    ],
    "startTime": "2025-11-04T08:00:00Z",
    "duration": 8,
    "durationType": "hours"
  }'
```

---

## Prerequisites

Before testing, ensure:
1. ✅ CNN model files in `backend/ml_models/`:
   - `cnn_traffic_model.keras`
   - `scaler.pkl`
   - `adj_mx_bay.pkl`

2. ✅ Dependencies installed:
   ```bash
   pip install -r requirements.txt
   ```

3. ✅ Google Maps API key in `.env` (for location validation)

---

## Old vs New Architecture

### Old: Simple TSP Solver
```
Waypoints → Nearest Neighbor → Time-of-Day Heuristic → Route
```

### New: CNN-Powered Optimizer
```
Waypoints → All Permutations → CNN Traffic Prediction → Best Route
            (N! routes)         (325 sensors × 12 steps)
```

**Result**: Much smarter routing based on actual traffic patterns! 🚀

---

## Response Field Breakdown

| Field | Type | Description |
|-------|------|-------------|
| `optimizedOrder` | `int[]` | Indices of waypoints in best order |
| `recommendedStart` | `string` | ISO datetime (may suggest earlier start) |
| `totalTravelTime` | `int` | Total minutes of driving time |
| `insights.warnings` | `TrafficWarning[]` | Alerts for heavy traffic segments |
| `insights.recommendations` | `dict[]` | Suggestions (timing, alternatives) |
| `itinerary` | `ItineraryDay[]` | Day-by-day schedule with times |
| `segments` | `RouteSegment[]` | Leg-by-leg traffic predictions |

---

## Traffic Level Thresholds

```python
speed > 50 mph  → "light"     (congestionScore ~0.2)
35 ≤ speed ≤ 50 → "moderate"  (congestionScore ~0.5)
speed < 35 mph  → "heavy"     (congestionScore ~0.8)
```

---

**Status**: Ready for CNN model integration! 🎯
