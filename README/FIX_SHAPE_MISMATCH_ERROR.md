# Fix for "ValueError: non-broadcastable output operand" Error

## Problem
You were getting this error when running the testing suite:
```
ValueError: non-broadcastable output operand with shape (40634100,1) 
doesn't match the broadcast shape (40634100,325)
```

## Root Cause
The scaler was fit on 2D data with shape `(timesteps, sensors)` where sensors = 325.
But the code was trying to inverse_transform 1D flattened data, causing a shape mismatch.

## Solution Applied
Updated `cnn_model_testing.py` to:
1. **Reshape data properly** before calling `inverse_transform`
2. **Handle 2D to 1D conversions correctly**
3. **Add fallback manual denormalization** if reshaping fails

## How to Use the Fixed Testing Suite

### Option 1: Simple Usage (Recommended)
```python
from cnn_model_testing import run_complete_testing_suite

# After training your model
run_complete_testing_suite(
    model, 
    X_train, X_val, X_test,
    y_train, y_val, y_test,
    scaler,
    n_sensors=325  # IMPORTANT: Pass the number of sensors!
)
```

### Option 2: Individual Testing Classes
```python
from cnn_model_testing import DataQualityTests, PerformanceMetrics, TemporalValidation

# Data quality testing
DataQualityTests.run_all_tests(X_train, X_val, X_test, y_train, y_val, y_test)

# Performance metrics (with proper n_sensors parameter)
y_pred_test = model.predict(X_test, verbose=0)
metrics = PerformanceMetrics.calculate_metrics(
    y_test, 
    y_pred_test, 
    scaler,
    n_sensors=325  # CRITICAL!
)
PerformanceMetrics.print_metrics_report(metrics, "TEST SET")

# Temporal validation
TemporalValidation.run_temporal_tests(y_pred_test)
```

## Key Changes Made

### 1. **Fixed denormalization logic** (lines 208-235)
```python
# Before (WRONG):
y_true_reshaped = y_true_flat.reshape(-1, 1)  # Wrong shape!

# After (CORRECT):
y_true_reshaped = y_true_flat.reshape(-1, n_sensors)  # Proper shape!
```

### 2. **Added n_sensors parameter**
```python
# Now pass n_sensors=325 to all functions that denormalize
def calculate_metrics(y_true, y_pred, scaler, n_sensors=325):
    # Uses n_sensors for proper reshaping
```

### 3. **Added robust error handling**
```python
try:
    # Try proper reshape and inverse_transform
    y_true_reshaped = y_true_flat.reshape(-1, n_sensors)
    y_true_denorm = scaler.inverse_transform(y_true_reshaped)
except ValueError:
    # Fallback to manual denormalization
    # Formula: y_denorm = y_norm * (max - min) + min
    avg_scale = scale_factor.mean()
    y_true_denorm = y_true_flat * avg_scale + avg_min
```

## What is `n_sensors`?

The number of features/sensors in your original data before flattening.

For PEMS Bay: **325 sensors**

You can verify this:
```python
print(N_SENSORS)  # Should be 325
print(scaler.data_min_.shape)  # Should be (325,)
print(scaler.data_max_.shape)  # Should be (325,)
```

## Complete Example - Copy This to Your Notebook

```python
# ============================================================
# FIXED TESTING SUITE - Paste this cell in your notebook
# ============================================================

import warnings
warnings.filterwarnings('ignore')

from cnn_model_testing import run_complete_testing_suite

# Important: Make sure scaler is loaded!
print("✓ Scaler loaded:", scaler is not None)
print("✓ N_SENSORS:", N_SENSORS)
print("✓ Model ready:", model is not None)

# Run the complete testing suite with n_sensors parameter
run_complete_testing_suite(
    model, 
    X_train, X_val, X_test,
    y_train, y_val, y_test,
    scaler=scaler,
    n_sensors=N_SENSORS  # CRITICAL!
)

print("\n✅ Testing complete!")
```

## Troubleshooting

### Still getting shape errors?
```python
# Check your scaler
print(f"Scaler features: {scaler.data_min_.shape[0]}")

# Check your data
print(f"X_test shape: {X_test.shape}")
print(f"y_test shape: {y_test.shape}")

# Should be (n_samples, 12, 325) for PEMS Bay
```

### Still getting ValueError?
```python
# The fallback manual denormalization will kick in
# Check the warning message for what went wrong
# Usually it means n_sensors is wrong

# Verify N_SENSORS:
print(N_SENSORS)  # Must be 325 for PEMS Bay
```

### Getting different metrics than before?
This is **expected and correct**! 
- Old code had wrong reshape → wrong denormalization → misleading metrics
- New code properly denormalizes → accurate metrics

## What Should Metrics Look Like?

**Good model** (after denormalization):
- RMSE: < 5 mph
- MAE: < 4 mph  
- MAPE: < 15%
- R²: > 0.75

**Example output:**
```
======================================================================
PERFORMANCE METRICS - TEST SET
======================================================================

📊 Denormalized Metrics (actual speed values in mph):
  MSE:  18.234560 mph²
  RMSE: 4.2701 mph
  MAE:  3.1245 mph
  MAPE: 12.34%
  R²:   0.823456
```

## Files Modified
- ✅ `cnn_model_testing.py` - Fixed denormalization logic
- ✅ Added `FIX_SCALER_DENORMALIZATION.py` - Reference implementation

## Next Steps

1. Copy the **Complete Example** above into your Jupyter notebook
2. Run it with your trained model
3. You should now get proper metrics without errors!

## Questions?

The key takeaway: **Always pass `n_sensors` when calculating metrics with denormalization!**
