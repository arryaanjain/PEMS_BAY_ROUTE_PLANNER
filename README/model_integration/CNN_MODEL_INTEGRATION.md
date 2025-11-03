# CNN Traffic Model Integration Guide

## Overview

This guide explains how to integrate your trained CNN traffic prediction model with the FastAPI backend for the PEMS Bay Route Planner.

## Model Architecture

Your CNN model was trained on PEMS Bay traffic data with the following specifications:

- **Input Shape**: `(batch, 12, 325)`
  - 12 time steps = 1 hour at 5-minute intervals
  - 325 sensors across the PEMS Bay region
  
- **Output Shape**: `(batch, 12, 325)`
  - Predicts the next 12 time steps (next hour)
  - Speed predictions for all 325 sensors

- **Data Range**: 
  - Normalized: [0, 1]
  - Denormalized: Speed in mph (typically 0-70)

## Files Required

Place these files in `backend/ml_models/`:

1. **`cnn_traffic_model.keras`** - Your trained model
2. **`scaler.pkl`** - MinMaxScaler fitted on training data
3. **`adj_mx_bay.pkl`** - Sensor adjacency matrix with sensor IDs

```bash
backend/
├── ml_models/
│   ├── cnn_traffic_model.keras
│   ├── scaler.pkl
│   ├── adj_mx_bay.pkl
│   └── sensor_locations.csv  (optional - for exact sensor coordinates)
```

## Setup Steps

### 1. Copy Model Files

```bash
# Create ml_models directory
mkdir -p backend/ml_models

# Copy your files from Google Drive or local storage
cp /path/to/cnn_traffic_model.keras backend/ml_models/
cp /path/to/scaler.pkl backend/ml_models/
cp /path/to/adj_mx_bay.pkl backend/ml_models/
```

### 2. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This installs:
- TensorFlow 2.13+
- NumPy
- scikit-learn (for the scaler)

### 3. (Optional) Create Sensor Location Mapping

The model works with sensor indices, but your API uses lat/lng coordinates. Create a CSV file mapping sensors to locations:

**`backend/ml_models/sensor_locations.csv`**:
```csv
sensor_id,index,lat,lng,freeway,station_id
1,0,37.8044,-122.3712,I-80,401234
2,1,37.8050,-122.3800,I-80,401235
...
```

If you don't have exact sensor locations:
- The system will create an approximate grid
- You can extract sensor metadata from PeMS or CalTrans databases
- Check: https://pems.dot.ca.gov/

## How It Works

### 1. User Flow

```
User selects waypoints (A, B, C) 
    ↓
System finds all route permutations (ABC, ACB, BAC, BCA, CAB, CBA)
    ↓
For each permutation:
  - Map lat/lng to nearest PEMS sensors
  - Get historical traffic data (or simulate based on time)
  - Use CNN to predict next hour of traffic
  - Calculate: avg speed, congestion score, travel time
    ↓
Compare all routes and return the best one
```

### 2. API Endpoints

**POST `/api/routes/optimize`**

Request:
```json
{
  "waypoints": [
    {"id": "1", "name": "Oakland", "lat": 37.8044, "lng": -122.2712},
    {"id": "2", "name": "SF Downtown", "lat": 37.7749, "lng": -122.4194},
    {"id": "3", "name": "Berkeley", "lat": 37.8715, "lng": -122.2730}
  ],
  "startTime": "2025-11-04T08:00:00Z",
  "duration": 8,
  "durationType": "hours"
}
```

Response:
```json
{
  "optimizedOrder": [0, 2, 1],
  "recommendedStart": "2025-11-04T07:00:00Z",
  "totalTravelTime": 90,
  "insights": {
    "warnings": [
      {
        "severity": "high",
        "message": "Heavy congestion near SF Downtown. Avg speed: 28.5 mph"
      }
    ],
    "recommendations": [
      {
        "type": "timing",
        "message": "This route saves 1.2 hours compared to the worst alternative"
      }
    ]
  },
  "itinerary": [...],
  "segments": [...]
}
```

### 3. Model Usage Flow

```python
# 1. Load model (happens once on startup)
from app.ml.model_loader import get_traffic_model
model = get_traffic_model()

# 2. Get historical data for sensors (past hour)
historical_data = get_historical_speeds(sensor_indices, reference_time)
# Shape: (12, 325) - last 12 time steps for all sensors

# 3. Normalize
normalized = model.normalize_speeds(historical_data)

# 4. Predict future traffic
predictions = model.predict(normalized, denormalize=True)
# Shape: (12, 325) - next 12 time steps predicted

# 5. Extract speed for specific sensors
sensor_speeds = predictions[:, sensor_index]
# Array of 12 predicted speeds for that sensor
```

## Route Comparison Logic

For N destinations, the system generates N! permutations:

| Destinations | Permutations | Example |
|-------------|-------------|---------|
| 2 | 2 | AB, BA |
| 3 | 6 | ABC, ACB, BAC, BCA, CAB, CBA |
| 4 | 24 | ABCD, ABDC, ... |
| 5 | 120 | ... |

**For each permutation:**

1. **Map route to sensors**
   - Find sensors along the path between each waypoint pair
   - Typically 5-10 sensors per segment

2. **Predict traffic**
   - Use CNN to predict speeds for the next hour
   - Account for start time (rush hour vs off-peak)

3. **Calculate metrics**
   - Average speed across route
   - Total travel time
   - Congestion score (0-1, where 1 = heavily congested)
   - Number of congested segments

4. **Rank routes**
   - Sort by: lowest congestion → fastest time
   - Mark the optimal route

## Expected Results

### Input
- 3 waypoints: Oakland → SF → Berkeley
- Start time: 8:00 AM (rush hour)
- Duration: 8 hours

### CNN Model Predictions
For sensors along each route segment:
- Oakland → SF: 30-35 mph (heavy traffic, rush hour)
- Oakland → Berkeley: 50-55 mph (light traffic, reverse commute)
- SF → Berkeley: 25-30 mph (heavy traffic, bridge congestion)

### Output Comparison

```json
{
  "total_comparisons": 6,
  "best_route": {
    "route_order": ["Oakland", "Berkeley", "SF"],
    "avg_speed_mph": 48.5,
    "estimated_travel_time_hours": 1.2,
    "congestion_score": 0.35,
    "is_optimal": true
  },
  "all_routes": [
    {"route_order": ["Oakland", "Berkeley", "SF"], "congestion_score": 0.35, ...},
    {"route_order": ["Oakland", "SF", "Berkeley"], "congestion_score": 0.72, ...},
    ...
  ]
}
```

## Traffic Level Classification

Based on predicted speeds:

| Speed (mph) | Classification | Description |
|------------|---------------|-------------|
| 0-35 | Heavy | Significant congestion |
| 35-50 | Moderate | Some slowdowns |
| 50+ | Light | Free-flowing traffic |

## Limitations & Notes

### 1. Historical Data Requirement

The CNN needs the past hour of traffic data as input. Currently, the system **simulates** this data based on:
- Time of day (rush hour vs off-peak)
- Random variation

**For production**, you need to:
- Store actual PEMS data in a database
- Query the last 12 time steps (past hour) for the relevant sensors
- Use real speeds instead of simulated ones

### 2. Sensor Coverage

Not all lat/lng coordinates will map directly to PEMS sensors. The system:
- Finds the nearest sensor within a reasonable radius
- Interpolates between sensors along a route

### 3. Model Accuracy

Your CNN achieved:
- **RMSE**: ~4.5 mph
- **MAPE**: ~8-12%
- **R²**: ~0.85-0.90

This is good for relative comparisons (route A vs B) but may have absolute error.

### 4. Computation Time

For N waypoints:
- N=3: 6 routes, ~2-5 seconds
- N=4: 24 routes, ~10-20 seconds  
- N=5: 120 routes, ~60+ seconds

Consider caching or limiting to N≤5 waypoints.

## Testing the Integration

### 1. Test Model Loading

```bash
cd backend
python -c "from app.ml.model_loader import get_traffic_model; m = get_traffic_model(); print('✅ Model loaded')"
```

### 2. Test Prediction

```python
from app.ml.traffic_predictor import get_traffic_predictor
from datetime import datetime

predictor = get_traffic_predictor()

waypoints = [
    {'lat': 37.8044, 'lng': -122.2712, 'name': 'Oakland'},
    {'lat': 37.7749, 'lng': -122.4194, 'name': 'SF'},
]

result = predictor.compare_route_orders(
    waypoints,
    datetime.now(),
    duration_hours=4
)

print(f"Best route: {result['best_route']['route_order']}")
print(f"Congestion score: {result['best_route']['congestion_score']}")
```

### 3. Test Full API

```bash
# Start server
uvicorn app.main:app --reload

# Test endpoint
curl -X POST http://localhost:8000/api/routes/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "waypoints": [
      {"id":"1","name":"Oakland","lat":37.8044,"lng":-122.2712},
      {"id":"2","name":"SF","lat":37.7749,"lng":-122.4194}
    ],
    "startTime":"2025-11-04T08:00:00Z",
    "duration":8,
    "durationType":"hours"
  }'
```

## Troubleshooting

### Error: "Model file not found"

```bash
# Check files exist
ls -lh backend/ml_models/
# Should show: cnn_traffic_model.keras, scaler.pkl, adj_mx_bay.pkl
```

### Error: "TensorFlow not installed"

```bash
pip install tensorflow>=2.13.0
```

### Error: "Scaler dimension mismatch"

The scaler was fit on (timesteps, 325) data. Ensure you're passing data with 325 features.

### Slow predictions

- TensorFlow loads models lazily
- First prediction is slower (~5-10s)
- Subsequent predictions are fast (~100-500ms)
- Consider using TensorFlow Lite for faster inference

## Next Steps

1. **Get Real Sensor Locations**
   - Download from PeMS: https://pems.dot.ca.gov/
   - Or use CalTrans data
   - Create `sensor_locations.csv`

2. **Store Historical Traffic Data**
   - Set up a database (PostgreSQL/TimescaleDB)
   - Ingest PEMS data periodically
   - Query last hour for real-time predictions

3. **Improve Route Mapping**
   - Use Google Directions API to get actual route paths
   - Map paths to PEMS sensors more accurately
   - Consider multiple sensors per segment

4. **Add Caching**
   - Cache predictions for common routes
   - Use Redis for fast lookups
   - Invalidate cache hourly

5. **Monitor Performance**
   - Log prediction accuracy
   - Compare predicted vs actual speeds
   - Retrain model periodically

## References

- PEMS Dataset: https://zenodo.org/records/4263971
- PeMS Portal: https://pems.dot.ca.gov/
- TensorFlow Serving: https://www.tensorflow.org/tfx/guide/serving

