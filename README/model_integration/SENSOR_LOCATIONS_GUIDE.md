# Sensor Locations CSV (Optional)

## Overview

The `sensor_locations.csv` file is **OPTIONAL**. If not provided, the system will automatically generate an approximate grid of 325 sensors covering the San Francisco Bay Area.

## When to Use Real Sensor Locations

Use actual PEMS sensor coordinates for:
- **Production deployments** with high accuracy requirements
- **Research** comparing different routes with precise sensor mapping
- **Validation** against real-world traffic patterns

## File Location

```
backend/ml_models/sensor_locations.csv
```

## CSV Format

```csv
sensor_id,lat,lng
1,37.7749,-122.4194
2,37.8044,-122.2712
3,37.8715,-122.2730
...
```

**Columns:**
- `sensor_id`: Integer (0-324) matching PEMS Bay dataset indices
- `lat`: Latitude (decimal degrees)
- `lng`: Longitude (decimal degrees)

## How to Obtain Real Sensor Data

### Option 1: PeMS Website
1. Visit [pems.dot.ca.gov](https://pems.dot.ca.gov)
2. Request access (requires approval)
3. Download District 4 (Bay Area) station metadata
4. Extract sensor IDs and coordinates

### Option 2: From Your Training Data
If you trained your CNN model, you likely have:
- `adj_mx_bay.pkl` - Adjacency matrix (325×325)
- Original PEMS-BAY dataset with sensor metadata

Extract sensor coordinates from your training data source.

### Option 3: Academic Datasets
Check repositories like:
- [STSGCN GitHub](https://github.com/Davidham3/STSGCN)
- [PEMS-BAY dataset on Zenodo](https://zenodo.org/)
- Academic papers citing PEMS-BAY

## Approximate Grid (Default Behavior)

When `sensor_locations.csv` is missing:

```python
# Generates 325 sensors in a grid covering:
Latitude:  37.2 to 38.2  (Bay Area span)
Longitude: -123.0 to -121.5
```

**Grid specs:**
- Evenly spaced across the region
- 325 total points (matching model input)
- Covers: SF, Oakland, Berkeley, San Jose, Palo Alto, etc.

**Accuracy:** Reasonable for testing, but less precise than real sensor locations.

## Example: Create Sensor CSV

If you have sensor data in another format, convert it:

```python
import pandas as pd

# Example: If you have a dict or array
sensors = [
    {'sensor_id': 0, 'lat': 37.7749, 'lng': -122.4194},
    {'sensor_id': 1, 'lat': 37.8044, 'lng': -122.2712},
    # ... 323 more sensors
]

df = pd.DataFrame(sensors)
df.to_csv('backend/ml_models/sensor_locations.csv', index=False)
print(f"Created CSV with {len(df)} sensors")
```

## Troubleshooting

### Warning Message
```
Sensor metadata not found at .../sensor_locations.csv. Using approximate grid.
⚠️  No sensor metadata file found. Using approximate Bay Area locations.
```

**This is normal!** The system continues with approximate locations.

### To Silence Warnings
Either:
1. **Create the CSV** with real sensor data
2. **Ignore it** - approximate grid works fine for testing

### Verify Sensor Loading

```python
from app.ml.sensor_mapper import SensorMapper

mapper = SensorMapper()
print(f"Loaded {len(mapper.sensors)} sensors")
print(f"Using approximate: {mapper.using_approximate}")
```

## Impact on Route Optimization

| Aspect | Real Sensors | Approximate Grid |
|--------|-------------|------------------|
| **Accuracy** | High | Medium |
| **CNN Predictions** | Precise mapping | Interpolated mapping |
| **Route Comparison** | Works perfectly | Works perfectly |
| **Production Ready** | ✅ Yes | ⚠️ Testing only |

## Summary

- ✅ **File is optional** - system works without it
- ✅ **Approximate grid** is automatic fallback
- ✅ **Route optimization** works with both
- 🎯 **For production**: Use real sensor locations
- 🧪 **For testing**: Approximate grid is fine

---

**Current Status**: Your system is working correctly with the approximate grid! 🚀
