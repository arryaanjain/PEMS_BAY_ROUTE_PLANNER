#!/usr/bin/env python3
"""
Test script to verify CNN model integration

Run this after placing model files in backend/ml_models/
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

def test_model_files():
    """Check if all required files exist"""
    print("\n" + "="*70)
    print("TEST 1: Checking Model Files")
    print("="*70)
    
    ml_dir = backend_dir / "ml_models"
    required_files = [
        "cnn_traffic_model.keras",
        "scaler.pkl",
        "adj_mx_bay.pkl"
    ]
    
    all_exist = True
    for filename in required_files:
        filepath = ml_dir / filename
        exists = filepath.exists()
        status = "✅" if exists else "❌"
        print(f"{status} {filename}: {'Found' if exists else 'NOT FOUND'}")
        if exists:
            size_mb = filepath.stat().st_size / (1024 * 1024)
            print(f"   Size: {size_mb:.2f} MB")
        all_exist = all_exist and exists
    
    return all_exist


def test_model_loading():
    """Test loading the CNN model"""
    print("\n" + "="*70)
    print("TEST 2: Loading CNN Model")
    print("="*70)
    
    try:
        from app.ml.model_loader import get_traffic_model
        
        print("Loading model...")
        model = get_traffic_model()
        
        print(f"✅ Model loaded successfully")
        print(f"   Sensors: {model.n_sensors}")
        print(f"   Sequence length: {model.seq_len}")
        print(f"   Prediction horizon: {model.horizon}")
        
        if model.sensor_ids:
            print(f"   Total sensor IDs: {len(model.sensor_ids)}")
        
        return True
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        return False


def test_prediction():
    """Test making a prediction"""
    print("\n" + "="*70)
    print("TEST 3: Making Prediction")
    print("="*70)
    
    try:
        import numpy as np
        from app.ml.model_loader import get_traffic_model
        
        model = get_traffic_model()
        
        # Create dummy input (simulated historical data)
        print("Creating test input (12 timesteps × 325 sensors)...")
        test_input = np.random.rand(12, 325).astype(np.float32)
        
        # Predict
        print("Running prediction...")
        predictions = model.predict(test_input, denormalize=True)
        
        print(f"✅ Prediction successful!")
        print(f"   Input shape: {test_input.shape}")
        print(f"   Output shape: {predictions.shape}")
        print(f"   Predicted speeds range: {predictions.min():.2f} - {predictions.max():.2f} mph")
        print(f"   Average predicted speed: {predictions.mean():.2f} mph")
        
        return True
    except Exception as e:
        print(f"❌ Prediction failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_sensor_mapping():
    """Test sensor mapping"""
    print("\n" + "="*70)
    print("TEST 4: Sensor Mapping")
    print("="*70)
    
    try:
        from app.ml.sensor_mapper import get_sensor_mapper
        
        mapper = get_sensor_mapper()
        
        # Test finding nearest sensor
        test_lat, test_lng = 37.8044, -122.2712  # Oakland
        print(f"Finding sensor near Oakland ({test_lat}, {test_lng})...")
        
        nearest = mapper.find_nearest_sensor(test_lat, test_lng, k=3)
        
        print(f"✅ Found {len(nearest)} nearest sensors:")
        for i, sensor in enumerate(nearest, 1):
            print(f"   {i}. Sensor ID {sensor.sensor_id} at ({sensor.lat:.4f}, {sensor.lng:.4f})")
        
        return True
    except Exception as e:
        print(f"❌ Sensor mapping failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_route_comparison():
    """Test route comparison"""
    print("\n" + "="*70)
    print("TEST 5: Route Comparison")
    print("="*70)
    
    try:
        from app.ml.traffic_predictor import get_traffic_predictor
        from datetime import datetime
        
        predictor = get_traffic_predictor()
        
        # Test waypoints
        waypoints = [
            {'lat': 37.8044, 'lng': -122.2712, 'name': 'Oakland'},
            {'lat': 37.7749, 'lng': -122.4194, 'name': 'San Francisco'},
            {'lat': 37.8715, 'lng': -122.2730, 'name': 'Berkeley'}
        ]
        
        print(f"Comparing {len(waypoints)} waypoints...")
        print(f"Locations: {', '.join([w['name'] for w in waypoints])}")
        
        result = predictor.compare_route_orders(
            waypoints,
            datetime(2025, 11, 4, 8, 0),  # 8 AM
            duration_hours=8
        )
        
        print(f"✅ Comparison complete!")
        print(f"   Total permutations analyzed: {result['total_comparisons']}")
        
        best = result['best_route']
        print(f"\n   🏆 Best Route: {' → '.join(best['route_order'])}")
        print(f"   Avg speed: {best['avg_speed_mph']:.1f} mph")
        print(f"   Travel time: {best['estimated_travel_time_hours']:.1f} hours")
        print(f"   Congestion score: {best['congestion_score']:.2f}")
        print(f"   Congested segments: {best['congested_segments']}")
        
        # Show all routes for comparison
        print(f"\n   All routes ranked:")
        for i, route in enumerate(result['all_routes'], 1):
            order = ' → '.join(route['route_order'])
            score = route['congestion_score']
            time = route['estimated_travel_time_hours']
            marker = "🏆" if route.get('is_optimal') else "  "
            print(f"   {marker}{i}. {order} | Score: {score:.2f} | Time: {time:.1f}h")
        
        return True
    except Exception as e:
        print(f"❌ Route comparison failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "#"*70)
    print("#" + " "*68 + "#")
    print("#" + "CNN TRAFFIC MODEL INTEGRATION TEST SUITE".center(68) + "#")
    print("#" + " "*68 + "#")
    print("#"*70)
    
    tests = [
        ("Model Files", test_model_files),
        ("Model Loading", test_model_loading),
        ("Prediction", test_prediction),
        ("Sensor Mapping", test_sensor_mapping),
        ("Route Comparison", test_route_comparison)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Model integration is ready.")
        print("\nNext steps:")
        print("1. Start the server: uvicorn app.main:app --reload")
        print("2. Test the API: POST /api/routes/optimize")
        print("3. Check the frontend integration")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        print("\nTroubleshooting:")
        print("1. Ensure all model files are in backend/ml_models/")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Check CNN_MODEL_INTEGRATION.md for detailed setup")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    main()
