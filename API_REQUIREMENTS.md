# Backend API Requirements for PEMS Bay Route Planner

## Overview
This document outlines all the backend APIs needed to support the frontend UI and enforce the PEMS Bay region constraint.

## Core Constraint
**All locations must be within the PEMS Bay region.** The backend should validate coordinates and reject any locations outside this geographic boundary.

---

## 1. Location Services

### 1.1 Autocomplete Location
**Endpoint:** `GET /api/locations/autocomplete`

**Query Parameters:**
- `query` (string, required): Search text (minimum 2 characters)

**Response:** `200 OK`
```json
[
  {
    "id": "loc_abc123",
    "name": "Oakland Bay Bridge Toll Plaza",
    "address": "Oakland, CA 94607",
    "lat": 37.8044,
    "lng": -122.3712
  },
  ...
]
```

**Business Logic:**
- Only return locations within PEMS Bay region
- Use spatial filtering on coordinates
- Limit results to 10 suggestions
- Order by relevance/distance from Bay Area center

**Error Responses:**
- `400 Bad Request`: Query too short or invalid

---

### 1.2 Validate Location
**Endpoint:** `POST /api/locations/validate`

**Request Body:**
```json
{
  "name": "Oakland Bay Bridge",
  "coordinates": {  // optional
    "lat": 37.8044,
    "lng": -122.3712
  }
}
```

**Response:** `200 OK`
```json
{
  "valid": true,
  "location": {
    "id": "loc_abc123",
    "name": "Oakland Bay Bridge Toll Plaza",
    "lat": 37.8044,
    "lng": -122.3712
  },
  "message": null
}
```

**Response (Invalid Location):** `200 OK`
```json
{
  "valid": false,
  "location": null,
  "message": "This location is outside the PEMS Bay region"
}
```

**Business Logic:**
- Check if coordinates fall within PEMS Bay bounding box
- If coordinates not provided, geocode the name first
- Return enriched location data if valid
- Use PEMS dataset metadata to define valid region

**Error Responses:**
- `400 Bad Request`: Missing required fields
- `404 Not Found`: Location cannot be geocoded

---

## 2. Route Optimization Service

### 2.1 Optimize Route
**Endpoint:** `POST /api/routes/optimize`

**Request Body:**
```json
{
  "waypoints": [
    {
      "id": "wp_1",
      "name": "Oakland Bay Bridge",
      "lat": 37.8044,
      "lng": -122.3712
    },
    {
      "id": "wp_2",
      "name": "San Francisco Pier 39",
      "lat": 37.8087,
      "lng": -122.4098
    },
    {
      "id": "wp_3",
      "name": "Golden Gate Bridge",
      "lat": 37.8199,
      "lng": -122.4783
    }
  ],
  "startTime": "2025-11-01T09:00:00Z",
  "duration": 8,
  "durationType": "hours"
}
```

**Response:** `200 OK`
```json
{
  "optimizedOrder": [0, 2, 1],  // Indices of waypoints in optimal order
  "recommendedStart": "2025-11-01T09:15:00Z",
  "totalTravelTime": 252,  // minutes
  "insights": {
    "warnings": [
      {
        "severity": "high",
        "message": "Heavy congestion expected near Golden Gate Bridge from 4:00 PM - 6:00 PM",
        "location": "Golden Gate Bridge",
        "timeWindow": {
          "start": "2025-11-01T16:00:00Z",
          "end": "2025-11-01T18:00:00Z"
        }
      }
    ],
    "recommendations": [
      {
        "type": "timing",
        "message": "Start 15 minutes earlier to avoid peak traffic"
      }
    ]
  },
  "itinerary": [
    {
      "day": 1,
      "date": "2025-11-01",
      "stops": [
        {
          "time": "09:15",
          "type": "depart",
          "location": "Oakland Bay Bridge",
          "insight": "Starting your journey"
        },
        {
          "time": "09:45",
          "type": "arrive",
          "location": "Golden Gate Bridge",
          "segmentId": "seg_123",
          "travelTime": 30,
          "insight": "Light traffic on I-80 West",
          "trafficLevel": "light"
        },
        {
          "time": "11:00",
          "type": "depart",
          "location": "Golden Gate Bridge"
        },
        {
          "time": "11:25",
          "type": "arrive",
          "location": "San Francisco Pier 39",
          "segmentId": "seg_124",
          "travelTime": 25,
          "insight": "Moderate traffic expected",
          "trafficLevel": "moderate"
        }
      ]
    }
  ],
  "segments": [
    {
      "id": "seg_123",
      "from": {
        "name": "Oakland Bay Bridge",
        "lat": 37.8044,
        "lng": -122.3712
      },
      "to": {
        "name": "Golden Gate Bridge",
        "lat": 37.8199,
        "lng": -122.4783
      },
      "predictedTravelTime": 30,
      "trafficCondition": "light",
      "congestionScore": 0.2,
      "timeWindow": {
        "start": "2025-11-01T09:15:00Z",
        "end": "2025-11-01T09:45:00Z"
      }
    },
    ...
  ]
}
```

**Business Logic - Route Optimization Algorithm:**
1. **Validate all waypoints** are in PEMS Bay region
2. **Load traffic predictions** from PEMS dataset for the given time windows
3. **Apply optimization**:
   - TSP (Traveling Salesman Problem) solver for order
   - Consider traffic predictions (lighter traffic = lower cost)
   - Factor in time windows and duration constraints
4. **Generate itinerary**:
   - Calculate arrival/departure times for each stop
   - Add buffer time for activities (e.g., 1 hour per stop)
   - Use PEMS segment IDs to link to real traffic data
5. **Generate insights**:
   - Identify high-congestion segments
   - Recommend optimal start time adjustments
   - Highlight critical bottlenecks

**Machine Learning Components:**
- Traffic prediction model (LSTM/GNN on PEMS data)
- Congestion forecasting for multi-day trips
- Route cost function balancing time vs. traffic

**Error Responses:**
- `400 Bad Request`: Invalid waypoints or parameters
- `422 Unprocessable Entity`: Waypoint outside PEMS Bay region

---

## 3. Traffic Prediction Service

### 3.1 Predict Traffic for Segment
**Endpoint:** `GET /api/traffic/predict`

**Query Parameters:**
- `fromLat` (number, required)
- `fromLng` (number, required)
- `toLat` (number, required)
- `toLng` (number, required)
- `time` (ISO 8601 string, required)

**Response:** `200 OK`
```json
{
  "segmentId": "seg_456",
  "travelTime": 25,
  "trafficLevel": "moderate",
  "congestionScore": 0.65,
  "confidence": 0.85
}
```

**Business Logic:**
- Map lat/lng to nearest PEMS segment(s)
- Query ML model for traffic prediction at given time
- Return aggregated prediction across matched segments

---

### 3.2 Traffic Heatmap
**Endpoint:** `GET /api/traffic/heatmap`

**Query Parameters:**
- `time` (ISO 8601 string, required)
- `duration` (number, optional): Hours to aggregate (default: 1)

**Response:** `200 OK`
```json
{
  "time": "2025-11-01T09:00:00Z",
  "region": {
    "bbox": [37.7, -122.5, 37.9, -122.3]  // [minLat, minLng, maxLat, maxLng]
  },
  "grid": [
    {
      "lat": 37.8044,
      "lng": -122.3712,
      "trafficLevel": "light",
      "congestionScore": 0.25
    },
    ...
  ]
}
```

**Business Logic:**
- Grid the PEMS Bay region
- Aggregate traffic predictions for each grid cell
- Used for map visualization in UI

---

## 4. Trip Management (Optional - Can use localStorage)

### 4.1 Get All Trips
**Endpoint:** `GET /api/trips`

**Response:** `200 OK`
```json
[
  {
    "id": "trip_123",
    "title": "Weekend Bay Tour",
    "date": "11/01/2025",
    "stops": 3,
    "createdAt": "2025-10-30T12:00:00Z"
  },
  ...
]
```

---

### 4.2 Get Trip by ID
**Endpoint:** `GET /api/trips/{id}`

**Response:** `200 OK`
```json
{
  "id": "trip_123",
  "title": "Weekend Bay Tour",
  "date": "11/01/2025",
  "stops": 3,
  "waypoints": [...],
  "startTime": "2025-11-01T09:00:00Z",
  "duration": 8,
  "durationType": "hours",
  "optimizedRoute": {...}
}
```

---

### 4.3 Save Trip
**Endpoint:** `POST /api/trips`

**Request Body:** (Full trip object)

**Response:** `201 Created`
```json
{
  "id": "trip_123",
  ...
}
```

---

### 4.4 Delete Trip
**Endpoint:** `DELETE /api/trips/{id}`

**Response:** `204 No Content`

---

## 5. Data Requirements

### PEMS Bay Dataset
- **Segment IDs**: Map lat/lng to PEMS segment identifiers
- **Segment Metadata**: Road names, coordinates, segment length
- **Historical Traffic**: Speed, flow, occupancy data
- **Prediction Model**: Pre-trained ML model for traffic forecasting

### Geographic Boundaries
- Define PEMS Bay region bounding box
- Store segment coordinate ranges
- Validate waypoints against this boundary

---

## 6. Implementation Priority

### Phase 1 (MVP):
1. ✅ Location validation (`/api/locations/validate`)
2. ✅ Route optimization (`/api/routes/optimize`) - with simple heuristic
3. ✅ Basic traffic prediction using historical averages

### Phase 2 (Enhanced):
4. Location autocomplete (`/api/locations/autocomplete`)
5. ML-based traffic prediction
6. Traffic heatmap visualization

### Phase 3 (Advanced):
7. Multi-day itinerary support
8. Real-time traffic updates
9. Alternative route suggestions
10. Server-side trip storage

---

## 7. Frontend Integration Points

### Components Using APIs:
- **WaypointInput**: `autocompleteLocation`, `validateLocation`
- **TripPlannerPage**: `optimizeRoute`
- **MapDisplay**: `trafficHeatmap` (future)
- **ItineraryView**: Uses optimized route data
- **HomePage**: `getTrips` (if using server storage)

### Error Handling:
- Display user-friendly messages for location validation failures
- Show loading states during optimization
- Retry logic for transient failures
- Graceful degradation if ML predictions unavailable

---

## 8. Testing Scenarios

### Location Validation:
- ✅ Valid PEMS Bay location accepted
- ❌ Location outside Bay Area rejected
- ❌ Invalid coordinates rejected

### Route Optimization:
- ✅ 2-5 waypoints optimized successfully
- ✅ Multi-day trip handled correctly
- ❌ Waypoints outside PEMS Bay rejected
- ⚠️ High-traffic warnings generated

### Traffic Prediction:
- ✅ Historical data returns reasonable estimates
- ✅ ML model predictions within acceptable error range
- ⚠️ Confidence scores below threshold flagged

---

## Next Steps

1. **Backend Team**: Implement Phase 1 APIs using FastAPI
2. **Data Team**: Prepare PEMS dataset and train prediction model
3. **Frontend Team**: Integrate API calls (already implemented in `services/api.ts`)
4. **Testing**: Create mock responses for development
5. **DevOps**: Set up CORS, rate limiting, and monitoring

