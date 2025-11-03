# 🚗 PEMS Bay Route Planner

> **AI-Powered Route Optimization Using CNN Traffic Predictions**

<div align="center">

![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.95+-green)
![React](https://img.shields.io/badge/React-18.3-61dafb)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.13+-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

**Intelligent route planning for San Francisco Bay Area using deep learning traffic predictions**

[Demo](#-demo) • [Features](#-key-features) • [Quick Start](#-quick-start) • [Tech Stack](#-tech-stack) • [Documentation](#-documentation)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [CNN Model Setup](#-cnn-model-setup)
- [API Endpoints](#-api-endpoints)
- [Frontend Components](#-frontend-components)
- [Project Structure](#-project-structure)
- [Documentation](#-documentation)
- [Contributing](#-contributing)

---

## 🎯 Overview

**PEMS Bay Route Planner** is a full-stack intelligent route optimization system that leverages a **Convolutional Neural Network (CNN)** trained on real-world traffic data from the [PEMS Bay dataset](https://zenodo.org/records/4263971) to predict optimal routes based on traffic conditions.

### What Makes This Special?

- **🧠 CNN Traffic Predictions**: Not just heuristics - real ML model trained on 325 Bay Area traffic sensors
- **🔄 Route Permutation Analysis**: Compares all N! possible route orderings to find the optimal path
- **📊 Real-time Traffic Insights**: Per-segment congestion scores, travel time predictions, traffic levels
- **🎨 Beautiful UI**: Modern React interface with drag-drop waypoint reordering and live results
- **⚡ Fast API**: Async FastAPI backend with optimized ML inference

---

## ✨ Key Features

### 🚀 Core Functionality

- **Multi-Waypoint Route Optimization**
  - Support for 2-5 destinations (N! permutation comparison)
  - Drag-and-drop waypoint reordering
  - Time window based planning (hours or days)

- **AI Traffic Prediction**
  - CNN model trained on 52,000+ PEMS Bay traffic samples
  - 12-timestep (1 hour) lookback for predictions
  - 325 sensor coverage across SF Bay Area
  - Traffic classification: Light (>50mph) / Moderate (35-50mph) / Heavy (<35mph)

- **Smart Route Analysis**
  - Congestion score (0-1 scale) per segment
  - Predicted travel time with traffic
  - Alternative route suggestions
  - Traffic warnings and recommendations

- **Interactive Results**
  - Detailed itinerary with arrive/depart times
  - Traffic level indicators per segment
  - Optimized visit order visualization
  - Map integration ready

### 🔧 Technical Highlights

- **Async FastAPI** backend with CNN model integration
- **React + TypeScript** frontend with Tailwind CSS
- **Google Maps API** integration for location services
- **PEMS Bay region validation** (37.2-38.2°N, -123.0 to -121.5°W)
- **Automatic sensor mapping** (lat/lng to PEMS sensor indices)

---

## 🛠 Tech Stack

### Backend

| Technology | Purpose | Version |
|------------|---------|---------|
| **FastAPI** | Async web framework | 0.95+ |
| **TensorFlow** | CNN model inference | 2.13+ |
| **NumPy** | Numerical computing | 1.24+ |
| **scikit-learn** | Data preprocessing (scaler) | 1.6+ |
| **SQLAlchemy** | ORM for MySQL | 1.4+ |
| **Pydantic** | Data validation & settings | 2.0+ |
| **Uvicorn** | ASGI server | 0.18+ |

### Frontend

| Technology | Purpose | Version |
|------------|---------|---------|
| **React** | UI framework | 18.3 |
| **TypeScript** | Type safety | 5.6 |
| **Vite** | Build tool | 6.0 |
| **Tailwind CSS** | Styling | 3.4 |
| **React Router** | Navigation | 7.0 |
| **@dnd-kit** | Drag & drop | Latest |
| **Lucide React** | Icons | Latest |

### Machine Learning

| Component | Details |
|-----------|---------|
| **Dataset** | PEMS Bay (325 sensors, 52K samples) |
| **Model Type** | Convolutional Neural Network (CNN) |
| **Input Shape** | (12, 325) - 12 timesteps × 325 sensors |
| **Output Shape** | (12, 325) - Next hour predictions |
| **Training** | 70% train / 10% val / 20% test split |
| **Metrics** | RMSE ~8mph, MAE ~6mph, R² ~0.85 |

---

## 🏗 Architecture

### System Flow

```
┌─────────────┐
│   User UI   │ (React + TypeScript)
│  Frontend   │
└──────┬──────┘
       │ HTTP Requests
       ▼
┌─────────────────────────────────────────┐
│          FastAPI Backend                │
│                                         │
│  ┌──────────────┐   ┌───────────────┐  │
│  │   Routes     │──▶│ Route         │  │
│  │   /optimize  │   │ Optimizer     │  │
│  └──────────────┘   └───────┬───────┘  │
│                             │          │
│  ┌──────────────┐   ┌───────▼───────┐  │
│  │  Location    │   │   Traffic     │  │
│  │  Services    │   │  Predictor    │  │
│  └──────────────┘   └───────┬───────┘  │
│                             │          │
│  ┌──────────────┐   ┌───────▼───────┐  │
│  │ Google Maps  │   │  CNN Model    │  │
│  │     API      │   │   Loader      │  │
│  └──────────────┘   └───────┬───────┘  │
│                             │          │
│                     ┌───────▼───────┐  │
│                     │ Sensor Mapper │  │
│                     └───────────────┘  │
└─────────────────────────────────────────┘
       │
       ▼
┌──────────────────┐
│   MySQL Database │ (Optional - for trip storage)
└──────────────────┘

┌──────────────────┐
│ TensorFlow Model │ (cnn_traffic_model.keras)
│   PEMS Bay CNN   │ (325 sensors, traffic prediction)
└──────────────────┘
```

### Request Flow Example

```
POST /api/routes/optimize
  ↓
1. Validate waypoints (Google Maps API)
  ↓
2. Generate route permutations (N!)
  ↓
3. For each route:
   - Map waypoints → PEMS sensor indices
   - Get historical traffic (last hour)
   - CNN predicts next hour traffic
   - Calculate: avg speed, travel time, congestion
  ↓
4. Rank routes by congestion + travel time
  ↓
5. Build itinerary with detailed stops
  ↓
6. Return optimized route + segments + insights
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.12+**
- **Node.js 18+**
- **npm 10+**
- **MySQL 8+** (optional, for trip persistence)

### 1️⃣ Clone Repository

```bash
git clone https://github.com/arryaanjain/PEMS_BAY_ROUTE_PLANNER.git
cd PEMS_BAY_ROUTE_PLANNER
```

### 2️⃣ Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings:
#   - DATABASE_URL (optional)
#   - GOOGLE_MAPS_API_KEY (required for location services)
```

### 3️⃣ CNN Model Setup

⚠️ **IMPORTANT**: The trained model is **NOT included** in this repository due to file size (~200MB).

You have **two options**:

#### Option A: Train Your Own Model (Recommended)

1. Open `PEMS_Bay_Places_Smart_Route_Suggestor.ipynb` in Google Colab
2. Run all cells to download PEMS Bay dataset and train the CNN
3. Download the generated files:
   - `cnn_traffic_model.keras` (trained model)
   - `scaler.pkl` (data normalizer)
   - `adj_mx_bay.pkl` (sensor adjacency matrix)
4. Place them in `backend/ml_models/` directory

```bash
backend/ml_models/
├── cnn_traffic_model.keras  ← Your trained model
├── scaler.pkl                ← MinMaxScaler
└── adj_mx_bay.pkl            ← Sensor graph
```

#### Option B: Use Pre-trained Model

If you have access to a pre-trained model, place the `.keras`, `.pkl` files in `backend/ml_models/`.

### 4️⃣ Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure API URL
cp .env.example .env
# Edit .env:
#   VITE_APP_URL=http://localhost:8000
```

### 5️⃣ Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```
Backend runs at: http://localhost:8000

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```
Frontend runs at: http://localhost:5173

### 6️⃣ Test the API

Import `PEMS_Bay_Route_Planner.postman_collection.json` into Postman and test:

- ✅ Route optimization (2-4 waypoints)
- ✅ Location autocomplete
- ✅ Location validation

---

## 🧠 CNN Model Setup

### Training the Model

The Jupyter Notebook (`PEMS_Bay_Places_Smart_Route_Suggestor.ipynb`) provides a complete pipeline:

**Cells to Run:**

1. **Download Dataset** - Fetches PEMS Bay data from Zenodo
2. **Load & Inspect** - Verifies data integrity (52K samples, 325 sensors)
3. **Normalize Data** - Creates MinMaxScaler for [0,1] normalization
4. **Create Sliding Windows** - Generates (12, 325) input/output pairs
5. **Split Data** - 70/10/20 train/val/test chronological split
6. **Build CNN Model** - Conv2D layers with pooling
7. **Train Model** - 5-10 epochs (adjustable)
8. **Test & Validate** - Comprehensive testing suite
9. **Save Model** - Exports `.keras` and `.pkl` files

### Model Architecture

```python
Sequential([
    Reshape((12, 325, 1)),           # Input: 12 timesteps × 325 sensors
    Conv2D(32, (3,3), activation='relu', padding='same'),
    MaxPooling2D((2,2)),
    Conv2D(64, (3,3), activation='relu', padding='same'),
    MaxPooling2D((2,2)),
    Flatten(),
    Dense(128, activation='relu'),
    Dense(12 * 325),                 # Output: flattened predictions
    Reshape((12, 325))               # Output: 12 timesteps × 325 sensors
])
```

### Expected Files

After training, you should have:

| File | Size | Description |
|------|------|-------------|
| `cnn_traffic_model.keras` | ~200MB | Trained CNN weights |
| `scaler.pkl` | ~3KB | MinMaxScaler (fitted on training data) |
| `adj_mx_bay.pkl` | ~4MB | Sensor adjacency matrix + sensor IDs |

### Optional: Sensor Locations

For higher accuracy, create `backend/ml_models/sensor_locations.csv`:

```csv
sensor_id,lat,lng
0,37.7749,-122.4194
1,37.8044,-122.2712
...
```

If not provided, the system uses an approximate 325-sensor grid (works fine for testing).

---

## 📡 API Endpoints

### Route Optimization

**POST** `/api/routes/optimize`

Optimizes route order based on CNN traffic predictions.

**Request:**
```json
{
  "waypoints": [
    {"id": "1", "name": "San Francisco", "lat": 37.7749, "lng": -122.4194},
    {"id": "2", "name": "Oakland", "lat": 37.8044, "lng": -122.2712},
    {"id": "3", "name": "Berkeley", "lat": 37.8715, "lng": -122.2730}
  ],
  "startTime": "2025-11-04T08:00:00Z",
  "duration": 8,
  "durationType": "hours"
}
```

**Response:**
```json
{
  "optimizedOrder": [1, 0, 2],
  "recommendedStart": "2025-11-04T08:00:00+00:00",
  "totalTravelTime": 45,
  "insights": {
    "warnings": [...],
    "recommendations": [...]
  },
  "itinerary": [...],
  "segments": [
    {
      "id": "seg_0",
      "fromLocation": {...},
      "toLocation": {...},
      "predictedTravelTime": 15,
      "trafficCondition": "light",
      "congestionScore": 0.12
    }
  ]
}
```

### Location Services

**GET** `/api/locations/autocomplete?query=san+francisco`

Returns location suggestions via Google Maps API.

**POST** `/api/locations/validate`

Validates if location is within PEMS Bay region.

---

## 🎨 Frontend Components

### Core Pages

1. **HomePage** (`/`)
   - Displays saved trips
   - Quick access to trip planner
   - Recent routes

2. **TripPlannerPage** (`/plan`)
   - Waypoint input with autocomplete
   - Drag-and-drop reordering
   - Time settings (start time, duration)
   - Optimize button

3. **RoutePage** (`/route/:tripId`)
   - Route overview (total time, recommended start)
   - Traffic segments grid
   - Detailed itinerary
   - Map display (integration ready)

### Key Components

| Component | Purpose |
|-----------|---------|
| `RouteOverview` | Summary card with key metrics |
| `RouteSegmentCard` | Individual segment with traffic viz |
| `WaypointInput` | Location search with autocomplete |
| `WaypointList` | Drag-drop waypoint manager |
| `ItineraryView` | Day-by-day schedule |
| `TimeSettings` | Trip duration & start time |

---

## 📂 Project Structure

```
PEMS_BAY_ROUTE_PLANNER/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI app entry
│   │   ├── config.py                  # Settings (env vars)
│   │   ├── database.py                # SQLAlchemy setup
│   │   ├── models.py                  # DB models
│   │   ├── schemas.py                 # Pydantic schemas
│   │   │
│   │   ├── ml/                        # ML Integration
│   │   │   ├── __init__.py
│   │   │   ├── model_loader.py        # CNN model wrapper
│   │   │   ├── sensor_mapper.py       # Lat/lng → sensor mapping
│   │   │   └── traffic_predictor.py   # Route comparison engine
│   │   │
│   │   ├── routes/                    # API Endpoints
│   │   │   ├── __init__.py
│   │   │   ├── locations.py           # Location services
│   │   │   └── routes.py              # Route optimization
│   │   │
│   │   └── services/                  # Business Logic
│   │       ├── __init__.py
│   │       ├── maps.py                # Google Maps integration
│   │       └── route_optimizer.py     # Main optimizer
│   │
│   ├── ml_models/                     # Model Files (NOT in repo)
│   │   ├── cnn_traffic_model.keras    # ← You need to add this
│   │   ├── scaler.pkl                 # ← You need to add this
│   │   ├── adj_mx_bay.pkl             # ← You need to add this
│   │   └── sensor_locations.csv       # (Optional)
│   │
│   ├── requirements.txt               # Python dependencies
│   ├── .env.example                   # Environment template
│   └── create_tables.py               # DB initialization
│
├── frontend/
│   ├── src/
│   │   ├── main.tsx                   # React entry point
│   │   ├── App.tsx                    # Router setup
│   │   │
│   │   ├── pages/                     # Page Components
│   │   │   ├── HomePage.tsx
│   │   │   ├── TripPlannerPage.tsx
│   │   │   └── RoutePage.tsx
│   │   │
│   │   ├── components/                # UI Components
│   │   │   ├── RouteOverview.tsx      # Summary card
│   │   │   ├── RouteSegmentCard.tsx   # Traffic segment
│   │   │   ├── WaypointInput.tsx      # Location search
│   │   │   ├── WaypointList.tsx       # Drag-drop list
│   │   │   └── ...
│   │   │
│   │   ├── services/                  # API Client
│   │   │   └── api.ts                 # Backend integration
│   │   │
│   │   ├── types/                     # TypeScript Types
│   │   │   └── index.ts
│   │   │
│   │   └── utils/                     # Utilities
│   │       ├── config.ts              # API URL config
│   │       └── storage.ts             # LocalStorage
│   │
│   ├── package.json                   # npm dependencies
│   ├── vite.config.ts                 # Vite config
│   ├── tailwind.config.js             # Tailwind config
│   └── .env.example                   # Environment template
│
├── PEMS_Bay_Places_Smart_Route_Suggestor.ipynb  # ← MODEL TRAINING
├── PEMS_Bay_Route_Planner.postman_collection.json
├── cnn_model_testing.py               # Model testing suite
└── README.md                          # This file
```

---

## 📚 Documentation

Comprehensive guides available in `/README` directory:

### Quick Reference

- **`API_ENDPOINT_SUMMARY.md`** - Complete API documentation
- **`QUICK_FIX_GUIDE.md`** - Common issues & solutions
- **`SENSOR_LOCATIONS_GUIDE.md`** - Sensor metadata setup

### Implementation Guides

- **`IMPLEMENTATION_GUIDE.md`** - Full deployment guide
- **`CNN_MODEL_INTEGRATION.md`** - ML integration details
- **`CNN_INTEGRATION_SUMMARY.md`** - Quick start for CNN
- **`GOOGLE_MAPS_SETUP.md`** - API key configuration

### Testing & Performance

- **`MODEL_PERFORMANCE_ANALYSIS.md`** - Model metrics & analysis
- **`CNN_MODEL_TESTING_GUIDE.md`** - Testing procedures
- **`TESTING_CHECKLIST.md`** - QA checklist

### Troubleshooting

- **`TROUBLESHOOTING_GUIDE.md`** - Common issues
- **`FIX_SHAPE_MISMATCH_ERROR.md`** - Shape errors
- **`FIX_SCALER_DENORMALIZATION.py`** - Scaler fixes

---

## 🧪 Testing

### Backend Tests

```bash
cd backend

# Test CNN integration
python test_cnn_integration.py

# Test API endpoints
pytest tests/

# Run comprehensive model testing
python cnn_model_testing.py
```

### Frontend Tests

```bash
cd frontend

# Run tests
npm test

# Build for production
npm run build
```

### Postman Collection

Import `PEMS_Bay_Route_Planner.postman_collection.json` for:
- 6 route optimization test cases
- Location autocomplete tests
- Validation tests

---

## 🌟 Performance Metrics

### CNN Model Performance

| Metric | Value | Description |
|--------|-------|-------------|
| **RMSE** | ~8 mph | Root Mean Square Error |
| **MAE** | ~6 mph | Mean Absolute Error |
| **MAPE** | ~12% | Mean Absolute Percentage Error |
| **R²** | ~0.85 | Coefficient of determination |

### API Performance

| Waypoints | Routes Compared | Avg Response Time |
|-----------|----------------|-------------------|
| 2 | 2 | 0.5s |
| 3 | 6 | 1-2s |
| 4 | 24 | 5-8s |
| 5 | 120 | 20-30s |

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- **PEMS Bay Dataset**: [Zenodo Repository](https://zenodo.org/records/4263971)
- **FastAPI**: Modern Python web framework
- **TensorFlow**: ML framework for CNN training
- **React**: Frontend UI library
- **Google Maps API**: Location services

---

## 📧 Contact

**Arryaan Jain** - [GitHub](https://github.com/arryaanjain)

Project Link: [https://github.com/arryaanjain/PEMS_BAY_ROUTE_PLANNER](https://github.com/arryaanjain/PEMS_BAY_ROUTE_PLANNER)

---

<div align="center">

**⭐ Star this repo if you find it helpful!**

Made with ❤️ and lots of ☕

</div>
