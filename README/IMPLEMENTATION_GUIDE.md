# Complete Implementation Guide - CNN Model Testing & Integration

## Overview

This guide walks you through the complete process of:
1. Training your CNN traffic prediction model
2. Testing it comprehensively
3. Integrating it with your FastAPI backend
4. Deploying for production

---

## Phase 1: Model Training (Jupyter Notebook)

### Step 1.1: Data Preparation

In your `PEMS_Bay_Places_Smart_Route_Suggestor.ipynb`, run these cells in order:

```python
# Cell 1: Download data
!wget -N https://zenodo.org/records/4263971/files/pems-bay.h5?download=1 -O pems-bay.h5
!wget -N https://zenodo.org/records/4263971/files/adj_mx_bay.pkl?download=1 -O adj_mx_bay.pkl

# Cell 2: Load data
from google.colab import drive
import pandas as pd
import numpy as np

drive.mount('/content/drive')
DATA_DIR = "/content/drive/MyDrive/PEMS_BAY"
data_df = pd.read_hdf(f"{DATA_DIR}/pems-bay.h5")

# Cell 3: Normalize data
from sklearn.preprocessing import MinMaxScaler
import pickle

data_array = data_df.values.astype(np.float32)
SEQ_LEN = 12
HORIZON = 12
N_SENSORS = data_array.shape[1]  # 325

scaler = MinMaxScaler()
data_normalized = scaler.fit_transform(data_array)

# Save scaler
with open('scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)

# Cell 4: Data quality diagnostic (CRITICAL!)
# ... run the data quality tests to fix any issues
```

### Step 1.2: Data Validation

```python
# Cell: Validate preprocessed data
import numpy as np

print("✓ Checking NaN values...")
assert not np.isnan(data_normalized).any(), "NaN values found!"

print("✓ Checking data range...")
assert (data_normalized >= 0).all() and (data_normalized <= 1).all(), "Data out of range!"

print("✓ Checking shapes...")
assert data_normalized.shape[1] == 325, f"Expected 325 sensors, got {data_normalized.shape[1]}"

print("✅ Data validation passed!")
```

### Step 1.3: Create Sliding Windows

```python
# Cell: Create training windows
def create_sliding_windows(data, seq_len, horizon):
    X = []
    y = []
    total_len = seq_len + horizon
    
    for i in range(data.shape[0] - total_len + 1):
        X.append(data[i : i + seq_len])
        y.append(data[i + seq_len : i + seq_len + horizon])
    
    return np.array(X), np.array(y)

X_data, y_data = create_sliding_windows(data_normalized, SEQ_LEN, HORIZON)

# Split: 70% train, 10% val, 20% test
total_samples = X_data.shape[0]
train_split = int(total_samples * 0.7)
val_split = int(total_samples * 0.8)

X_train = X_data[:train_split]
y_train = y_data[:train_split]
X_val = X_data[train_split:val_split]
y_val = y_data[train_split:val_split]
X_test = X_data[val_split:]
y_test = y_data[val_split:]

print(f"Training set: {X_train.shape}")
print(f"Validation set: {X_val.shape}")
print(f"Test set: {X_test.shape}")
```

### Step 1.4: Define and Train Model

```python
# Cell: Define CNN model
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Reshape

model = Sequential([
    Reshape((SEQ_LEN, N_SENSORS, 1), input_shape=(SEQ_LEN, N_SENSORS)),
    Conv2D(filters=32, kernel_size=(3, 3), activation='relu', padding='same'),
    MaxPooling2D(pool_size=(2, 2)),
    Conv2D(filters=64, kernel_size=(3, 3), activation='relu', padding='same'),
    MaxPooling2D(pool_size=(2, 2)),
    Flatten(),
    Dense(128, activation='relu'),
    Dense(SEQ_LEN * N_SENSORS)
])

model.add(Reshape((HORIZON, N_SENSORS)))
model.compile(optimizer='adam', loss='mse')

print(model.summary())

# Train
history = model.fit(
    X_train, y_train,
    epochs=10,
    batch_size=32,
    validation_data=(X_val, y_val)
)

# Save model
model.save('/content/drive/MyDrive/PEMS_BAY/cnn_traffic_model.keras')
```

---

## Phase 2: Comprehensive Testing

### Step 2.1: Import Testing Module

```python
# Cell: Import testing suite
from cnn_model_testing import run_complete_testing_suite

print("✓ Testing module imported successfully")
```

### Step 2.2: Run Complete Tests

```python
# Cell: Run all tests (CRITICAL!)
run_complete_testing_suite(
    model,
    X_train, X_val, X_test,
    y_train, y_val, y_test,
    scaler=scaler,
    n_sensors=N_SENSORS  # MUST INCLUDE THIS!
)
```

### Step 2.3: Interpret Results

Expected output:

```
PHASE 1: DATA QUALITY TESTING
✓ No NaN values
✓ Data in valid range [0, 1]
✓ All shapes correct
✓ Distribution reasonable

PHASE 3: PERFORMANCE METRICS
✓ RMSE (denormalized): 4.27 mph (Target: < 5)
✓ MAE: 3.12 mph (Target: < 4)
✓ MAPE: 12.34% (Target: < 15)
✓ R²: 0.823 (Target: > 0.75)

PHASE 4: TEMPORAL VALIDATION
✓ Predictions temporally smooth
✓ All predictions within bounds

✅ ALL TESTS PASSED - READY FOR PRODUCTION
```

### Success Criteria

| Metric | Target | Your Model |
|--------|--------|-----------|
| RMSE | < 5 mph | ___ mph |
| MAE | < 4 mph | ___ mph |
| MAPE | < 15% | __% |
| R² | > 0.75 | ___ |

---

## Phase 3: Backend Integration

### Step 3.1: Backend Setup

Your backend is in `/backend/app/`

**Current structure:**
```
app/
├── main.py          # FastAPI app
├── routes/
│   ├── locations.py # Location endpoints
│   ├── routes.py    # Route optimization
│   └── traffic.py   # Traffic prediction
├── services/
│   ├── maps.py      # Google Maps API
│   └── optimizer.py # Route optimization logic
└── schemas.py       # Data models
```

### Step 3.2: Add Traffic Prediction Service

Create file: `/backend/app/services/traffic_predictor.py`

```python
"""Traffic prediction service using CNN model"""

import numpy as np
import pickle
from tensorflow.keras.models import load_model
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class TrafficPredictor:
    def __init__(self, model_path: str, scaler_path: str):
        """Initialize traffic predictor"""
        try:
            self.model = load_model(model_path)
            with open(scaler_path, 'rb') as f:
                self.scaler = pickle.load(f)
            logger.info("✅ Traffic predictor initialized")
        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}")
            raise

    def predict_traffic(
        self, 
        sensor_data: np.ndarray,  # Shape: (12, 325)
        n_steps: int = 12
    ) -> Dict:
        """
        Predict traffic for next hour
        
        Args:
            sensor_data: Historical sensor readings (12 timesteps × 325 sensors)
            n_steps: Number of steps to predict (default 12 = 1 hour)
        
        Returns:
            dict with predictions, warnings, recommendations
        """
        try:
            # Validate input
            if sensor_data.shape != (12, 325):
                raise ValueError(f"Expected shape (12, 325), got {sensor_data.shape}")
            
            # Prepare for model
            X = sensor_data.reshape(1, 12, 325)  # Add batch dimension
            
            # Predict
            y_pred_norm = self.model.predict(X, verbose=0)[0]  # Shape: (12, 325)
            
            # Denormalize
            y_pred_denorm = self.scaler.inverse_transform(y_pred_norm)  # (12, 325)
            
            # Extract predictions
            predictions = {
                'next_hour_speeds': y_pred_denorm.tolist(),
                'average_speed': float(y_pred_denorm.mean()),
                'min_speed': float(y_pred_denorm.min()),
                'max_speed': float(y_pred_denorm.max()),
            }
            
            # Generate warnings
            warnings = self._generate_warnings(y_pred_denorm)
            predictions['warnings'] = warnings
            
            # Generate recommendations
            recommendations = self._generate_recommendations(y_pred_denorm)
            predictions['recommendations'] = recommendations
            
            return predictions
            
        except Exception as e:
            logger.error(f"❌ Prediction error: {e}")
            raise

    def _generate_warnings(self, predictions: np.ndarray) -> List[Dict]:
        """Generate traffic warnings"""
        warnings = []
        
        avg_speed = predictions.mean()
        
        # Congestion warning
        if avg_speed < 20:
            warnings.append({
                'severity': 'high',
                'message': f'Heavy congestion expected: {avg_speed:.1f} mph',
                'segment': 'entire_route'
            })
        elif avg_speed < 30:
            warnings.append({
                'severity': 'medium',
                'message': f'Moderate congestion: {avg_speed:.1f} mph',
                'segment': 'entire_route'
            })
        
        return warnings

    def _generate_recommendations(self, predictions: np.ndarray) -> List[str]:
        """Generate routing recommendations"""
        recommendations = []
        
        avg_speed = predictions.mean()
        
        if avg_speed < 25:
            recommendations.append("Consider avoiding peak traffic hours")
            recommendations.append("Use alternative routes if available")
        
        if predictions.std() > 15:
            recommendations.append("Variable traffic conditions expected")
        
        return recommendations
```

### Step 3.3: Update Route Optimizer

File: `/backend/app/services/optimizer.py`

```python
"""Route optimization service"""

from datetime import datetime, timedelta
from typing import List, Dict
from ..schemas import Waypoint, OptimizedRoute
from .traffic_predictor import TrafficPredictor
import numpy as np

class RouteOptimizer:
    def __init__(self, traffic_predictor: TrafficPredictor):
        self.traffic_predictor = traffic_predictor
    
    def optimize_route(
        self,
        waypoints: List[Waypoint],
        start_time: str,
        duration: int,
        duration_type: str,
        sensor_data: np.ndarray  # Current PEMS data
    ) -> OptimizedRoute:
        """
        Optimize route based on traffic predictions
        
        Args:
            waypoints: List of locations
            start_time: ISO format datetime
            duration: Duration value
            duration_type: 'hours' or 'days'
            sensor_data: Current sensor readings for prediction
        
        Returns:
            OptimizedRoute with timing and warnings
        """
        
        # Convert duration to minutes
        if duration_type == 'hours':
            total_minutes = duration * 60
        else:  # days
            total_minutes = duration * 24 * 60
        
        # Get traffic predictions
        traffic_pred = self.traffic_predictor.predict_traffic(sensor_data)
        
        # Optimize waypoint order
        optimized_waypoints = self._optimize_order(waypoints, traffic_pred)
        
        # Calculate timing
        itinerary = self._calculate_itinerary(
            optimized_waypoints,
            start_time,
            total_minutes,
            traffic_pred
        )
        
        # Create response
        return OptimizedRoute(
            recommendedStart=start_time,
            totalTime=f"{total_minutes // 60}h {total_minutes % 60}m",
            warnings=traffic_pred['warnings'],
            itinerary=itinerary,
            mapData={
                'waypoints': [
                    {'lat': wp.lat, 'lng': wp.lng, 'name': wp.name}
                    for wp in optimized_waypoints
                ]
            }
        )
    
    def _optimize_order(self, waypoints: List[Waypoint], traffic_pred: Dict) -> List[Waypoint]:
        """Optimize waypoint order based on traffic"""
        # Implement nearest neighbor or other optimization
        # For now, return in original order
        return waypoints
    
    def _calculate_itinerary(
        self,
        waypoints: List[Waypoint],
        start_time: str,
        total_minutes: int,
        traffic_pred: Dict
    ) -> List:
        """Calculate detailed itinerary"""
        # Implementation for itinerary calculation
        return []
```

### Step 3.4: Update Main Routes

File: `/backend/app/routes/routes.py`

```python
"""Route optimization endpoints"""

from fastapi import APIRouter, HTTPException
from ..schemas import (
    OptimizeRouteRequest,
    OptimizeRouteResponse
)
from ..services.optimizer import RouteOptimizer
from ..services.traffic_predictor import TrafficPredictor
import numpy as np

router = APIRouter()

# Initialize traffic predictor (done once at startup)
traffic_predictor = None

@router.post("/optimize-route")
async def optimize_route(request: OptimizeRouteRequest) -> OptimizeRouteResponse:
    """
    Optimize a route based on locations and time constraints
    
    Uses CNN traffic predictions to determine optimal ordering
    and timing for waypoints
    """
    try:
        # Validate waypoints
        if len(request.waypoints) < 2:
            raise HTTPException(
                status_code=400,
                detail="At least 2 waypoints required"
            )
        
        # Get current sensor data (from PEMS)
        # TODO: Fetch from PEMS database
        sensor_data = np.random.rand(12, 325)  # Placeholder
        
        # Optimize route
        optimizer = RouteOptimizer(traffic_predictor)
        optimized_route = optimizer.optimize_route(
            waypoints=request.waypoints,
            start_time=request.startTime,
            duration=request.duration,
            duration_type=request.durationType,
            sensor_data=sensor_data
        )
        
        return OptimizeRouteResponse(
            optimizedRoute=optimized_route,
            success=True
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Step 3.5: Update Schemas

File: `/backend/app/schemas.py`

```python
"""Data models and schemas"""

from pydantic import BaseModel
from typing import List, Optional

class Waypoint(BaseModel):
    id: str
    name: str
    address: Optional[str] = None
    lat: float
    lng: float

class TrafficWarning(BaseModel):
    severity: str  # 'low', 'medium', 'high'
    message: str
    segment: Optional[str] = None

class ItineraryStop(BaseModel):
    time: str
    type: str  # 'depart', 'arrive'
    location: str
    insight: Optional[str] = None

class ItineraryDay(BaseModel):
    day: int
    date: str
    stops: List[ItineraryStop]

class OptimizedRoute(BaseModel):
    recommendedStart: str
    totalTime: str
    warnings: List[TrafficWarning]
    itinerary: List[ItineraryDay]
    mapData: Optional[dict] = None

class OptimizeRouteRequest(BaseModel):
    waypoints: List[Waypoint]
    startTime: str
    duration: int
    durationType: str

class OptimizeRouteResponse(BaseModel):
    optimizedRoute: OptimizedRoute
    success: bool
```

---

## Phase 4: Model Deployment

### Step 4.1: Setup Backend Environment

```bash
# Install dependencies
cd /backend
pip install -r requirements.txt
pip install tensorflow scikit-learn

# Verify installations
python -c "import tensorflow; print(f'TensorFlow: {tensorflow.__version__}')"
python -c "import sklearn; print(f'scikit-learn: {sklearn.__version__}')"
```

### Step 4.2: Download Model Files

```bash
# Download model and scaler from Google Drive
# Place them in backend/models/ directory
mkdir -p backend/models/
# Download cnn_traffic_model.keras
# Download scaler.pkl
```

### Step 4.3: Initialize Traffic Predictor

In `/backend/app/main.py`:

```python
"""FastAPI main application"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .services.traffic_predictor import TrafficPredictor
from .routes import routes, locations, traffic
import os

app = FastAPI(title="PEMS Bay Route Planner API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize traffic predictor on startup
@app.on_event("startup")
async def startup_event():
    """Initialize models on startup"""
    try:
        model_path = os.getenv("MODEL_PATH", "models/cnn_traffic_model.keras")
        scaler_path = os.getenv("SCALER_PATH", "models/scaler.pkl")
        
        traffic_predictor = TrafficPredictor(model_path, scaler_path)
        print("✅ Traffic predictor initialized")
        
        # Store in app state
        app.state.traffic_predictor = traffic_predictor
    except Exception as e:
        print(f"❌ Failed to initialize traffic predictor: {e}")
        raise

# Include routes
app.include_router(routes.router, prefix="/api/routes", tags=["routes"])
app.include_router(locations.router, prefix="/api/locations", tags=["locations"])
app.include_router(traffic.router, prefix="/api/traffic", tags=["traffic"])

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "traffic_predictor": app.state.traffic_predictor is not None
    }
```

### Step 4.4: Start Backend Server

```bash
# Navigate to backend
cd backend

# Start with uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or with Python
python -m uvicorn app.main:app --reload
```

### Step 4.5: Test Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Optimize route
curl -X POST http://localhost:8000/api/routes/optimize-route \
  -H "Content-Type: application/json" \
  -d '{
    "waypoints": [
      {"id": "1", "name": "Location A", "lat": 37.3382, "lng": -121.8863},
      {"id": "2", "name": "Location B", "lat": 37.4419, "lng": -122.1430}
    ],
    "startTime": "2025-11-02T08:00:00",
    "duration": 2,
    "durationType": "hours"
  }'
```

---

## Phase 5: Frontend Integration

### Step 5.1: Update API Service

File: `/frontend/src/services/api.ts`

```typescript
/**
 * API client for PEMS Bay Route Planner backend
 */

const API_BASE_URL = process.env.VITE_API_URL || 'http://localhost:8000/api';

export interface OptimizeRouteRequest {
  waypoints: Array<{
    id: string;
    name: string;
    address?: string;
    lat: number;
    lng: number;
  }>;
  startTime: string;
  duration: number;
  durationType: 'hours' | 'days';
}

export interface OptimizeRouteResponse {
  optimizedRoute: {
    recommendedStart: string;
    totalTime: string;
    warnings: Array<{
      severity: 'low' | 'medium' | 'high';
      message: string;
      segment?: string;
    }>;
    itinerary: Array<{
      day: number;
      date: string;
      stops: Array<{
        time: string;
        type: 'depart' | 'arrive';
        location: string;
        insight?: string;
      }>;
    }>;
  };
  success: boolean;
}

/**
 * Optimize a route based on waypoints and constraints
 */
export async function optimizeRoute(request: OptimizeRouteRequest): Promise<OptimizeRouteResponse> {
  const response = await fetch(`${API_BASE_URL}/routes/optimize-route`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Get location suggestions
 */
export async function getLocationSuggestions(query: string) {
  const response = await fetch(
    `${API_BASE_URL}/locations/autocomplete?query=${encodeURIComponent(query)}`
  );

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }

  return response.json();
}
```

### Step 5.2: Test Integration

```bash
cd frontend
npm run dev

# Navigate to http://localhost:5173
```

---

## Phase 6: Production Deployment

### Step 6.1: Environment Configuration

Create `.env.production`:

```
VITE_API_URL=https://api.example.com/api
MODEL_PATH=/app/models/cnn_traffic_model.keras
SCALER_PATH=/app/models/scaler.pkl
DATABASE_URL=postgresql://user:password@db:5432/pems_bay
```

### Step 6.2: Docker Deployment

Create `Dockerfile` for backend:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir tensorflow scikit-learn

# Copy application
COPY backend/app ./app

# Copy models
COPY models ./models

# Run
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Step 6.3: Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      MODEL_PATH: /app/models/cnn_traffic_model.keras
      SCALER_PATH: /app/models/scaler.pkl
    volumes:
      - ./models:/app/models
    depends_on:
      - db

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    environment:
      VITE_API_URL: http://backend:8000/api

  db:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: password
      POSTGRES_DB: pems_bay
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Step 6.4: Deploy

```bash
# Build and start
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
```

---

## Monitoring & Maintenance

### Model Performance Monitoring

```python
"""Monitor model performance over time"""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ModelMonitor:
    def __init__(self):
        self.predictions = []
        self.actuals = []
    
    def log_prediction(self, prediction, actual):
        """Log a prediction for monitoring"""
        self.predictions.append({
            'timestamp': datetime.now(),
            'prediction': prediction,
            'actual': actual,
            'error': abs(prediction - actual)
        })
        
        # Alert if error too high
        if abs(prediction - actual) > 10:  # 10 mph threshold
            logger.warning(f"High prediction error: {abs(prediction - actual):.2f} mph")
    
    def get_metrics(self):
        """Calculate current metrics"""
        if not self.actuals:
            return None
        
        errors = [abs(p - a) for p, a in zip(self.predictions, self.actuals)]
        return {
            'mae': sum(errors) / len(errors),
            'rmse': (sum(e**2 for e in errors) / len(errors)) ** 0.5,
            'max_error': max(errors)
        }
```

### Retraining Schedule

```python
"""Periodic model retraining"""

from apscheduler.schedulers.background import BackgroundScheduler
import logging

logger = logging.getLogger(__name__)

def schedule_retraining():
    """Schedule monthly retraining"""
    scheduler = BackgroundScheduler()
    
    @scheduler.scheduled_job('cron', day=1, hour=2)  # 1st of month at 2 AM
    def retrain_model():
        logger.info("Starting scheduled model retraining...")
        try:
            # Fetch latest data
            # Train new model
            # Evaluate
            # If better, deploy
            logger.info("✅ Retraining completed successfully")
        except Exception as e:
            logger.error(f"❌ Retraining failed: {e}")
    
    scheduler.start()
```

---

## Troubleshooting & Support

See these files for detailed help:

- **`QUICK_REFERENCE_FIXED.md`** - Quick reference
- **`TROUBLESHOOTING_GUIDE.md`** - Common issues
- **`FIX_SHAPE_MISMATCH_ERROR.md`** - Shape errors
- **`FIX_SUMMARY.md`** - Fix overview

---

## Checklist - Step by Step

### Training Phase
- [ ] Download PEMS data
- [ ] Load and normalize data
- [ ] Create sliding windows
- [ ] Split into train/val/test
- [ ] Train CNN model
- [ ] Save model and scaler

### Testing Phase
- [ ] Import `cnn_model_testing`
- [ ] Run `run_complete_testing_suite()`
- [ ] Verify metrics meet targets
- [ ] Check all phases pass

### Backend Integration
- [ ] Create `traffic_predictor.py`
- [ ] Update `optimizer.py`
- [ ] Update `routes.py`
- [ ] Update `schemas.py`
- [ ] Update `main.py`
- [ ] Download model files
- [ ] Start backend server

### Frontend Integration
- [ ] Update `api.ts`
- [ ] Test API endpoints
- [ ] Verify UI updates
- [ ] Test end-to-end flow

### Deployment
- [ ] Create `.env.production`
- [ ] Create `Dockerfile`
- [ ] Create `docker-compose.yml`
- [ ] Build images
- [ ] Deploy to production
- [ ] Monitor and verify

---

## Success Indicators

✅ Model training completed
✅ All tests pass
✅ Metrics meet targets (RMSE < 5 mph, etc.)
✅ Backend API responds correctly
✅ Frontend displays results
✅ End-to-end flow works
✅ Deployed to production
✅ Monitoring active

---

**Status:** Complete Implementation Guide
**Last Updated:** 2025-11-02
