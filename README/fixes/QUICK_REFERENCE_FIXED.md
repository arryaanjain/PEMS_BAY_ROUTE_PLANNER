# Quick Reference: Fixed Testing Suite

## 🚀 Quick Start (Copy & Paste)

```python
from cnn_model_testing import run_complete_testing_suite

# Run with n_sensors parameter (CRITICAL!)
run_complete_testing_suite(
    model, 
    X_train, X_val, X_test,
    y_train, y_val, y_test,
    scaler,
    n_sensors=325  # ⚠️ MUST INCLUDE THIS!
)
```

## ❌ What Was Wrong

```python
# OLD (BROKEN):
metrics = PerformanceMetrics.calculate_metrics(y_test, y_pred_test, scaler)
# ↑ No n_sensors parameter = wrong reshape = ValueError

# NEW (FIXED):
metrics = PerformanceMetrics.calculate_metrics(y_test, y_pred_test, scaler, n_sensors=325)
# ↑ With n_sensors = correct reshape = proper denormalization
```

## 🔧 The Fix Explained

### Problem
```
ValueError: non-broadcastable output operand with shape (40634100,1) 
doesn't match the broadcast shape (40634100,325)
```

### Why It Happened
Scaler was fit on 2D data (timesteps × 325 sensors)
Code tried to inverse_transform 1D data → Shape mismatch!

### How It's Fixed
```python
# Now properly reshapes before inverse_transform:
y_true_reshaped = y_true_flat.reshape(-1, 325)  # ✅ Correct!
y_true_denorm = scaler.inverse_transform(y_true_reshaped)
```

## ✅ Verification Checklist

Before running tests, verify:

```python
# 1. N_SENSORS value
print(N_SENSORS)  # Should print: 325

# 2. Scaler shape
print(scaler.data_min_.shape)  # Should be (325,)
print(scaler.data_max_.shape)  # Should be (325,)

# 3. Data shapes
print(X_test.shape)   # Should be (n, 12, 325)
print(y_test.shape)   # Should be (n, 12, 325)

# 4. All data in [0, 1]
print(f"X range: [{X_test.min():.4f}, {X_test.max():.4f}]")
print(f"y range: [{y_test.min():.4f}, {y_test.max():.4f}]")
```

## 📊 Expected Output

```
======================================================================
PHASE 1: DATA QUALITY TESTING
======================================================================
✓ Testing Data Completeness...
  ✅ No NaN values found
✓ Testing Data Ranges...
  ✅ Data in expected range
✓ Testing Data Shapes...
  ✅ All shapes correct
✓ Testing Data Distribution...
  ✅ Outlier percentage reasonable

======================================================================
PHASE 3: PERFORMANCE METRICS EVALUATION
======================================================================
📊 Normalized Metrics (0-1 range):
  MSE:  0.001234
  RMSE: 0.035120
  MAE:  0.024563
  R²:   0.824567

📊 Denormalized Metrics (actual speed values in mph):
  MSE:  18.234560 mph²
  RMSE: 4.2701 mph
  MAE:  3.1245 mph
  MAPE: 12.34%
  R²:   0.823456

✅ ALL DATA QUALITY TESTS PASSED
```

## 🎯 Key Parameters

| Parameter | Value | Notes |
|-----------|-------|-------|
| `n_sensors` | 325 | Number of sensors in PEMS Bay |
| `seq_len` | 12 | Input sequence length (1 hour) |
| `horizon` | 12 | Prediction horizon (1 hour) |
| `data_min_` | (325,) | Scaler shape |
| `data_max_` | (325,) | Scaler shape |

## 🔄 Data Flow

```
Original Data (timesteps × 325)
    ↓
Normalize: MinMaxScaler.fit_transform()
    ↓
Create Sliding Windows
    ↓
Train/Val/Test Split
    ↓
Model Training
    ↓
Predictions (0-1 range)
    ↓
Reshape to (-1, 325) [NEW: CRITICAL STEP]
    ↓
Inverse Transform: scaler.inverse_transform()
    ↓
Denormalized Metrics (mph values)
```

## 🚨 Common Mistakes

❌ **WRONG:**
```python
run_complete_testing_suite(model, X_train, X_val, X_test, y_train, y_val, y_test, scaler)
# Missing n_sensors parameter!
```

✅ **CORRECT:**
```python
run_complete_testing_suite(model, X_train, X_val, X_test, y_train, y_val, y_test, scaler, n_sensors=325)
# Includes n_sensors!
```

---

❌ **WRONG:**
```python
metrics = PerformanceMetrics.calculate_metrics(y_test, y_pred_test, scaler)
# Missing n_sensors!
```

✅ **CORRECT:**
```python
metrics = PerformanceMetrics.calculate_metrics(y_test, y_pred_test, scaler, n_sensors=325)
# Includes n_sensors!
```

## 📝 Files to Know

| File | Purpose |
|------|---------|
| `cnn_model_testing.py` | Main testing module (FIXED) |
| `FIX_SCALER_DENORMALIZATION.py` | Reference implementation |
| `FIX_SHAPE_MISMATCH_ERROR.md` | Detailed explanation |

## 💡 Pro Tips

1. **Always pass n_sensors to testing functions**
2. **Verify your data shapes before testing**
3. **The fallback manual denormalization works too** (but proper reshape is better)
4. **Check that all data is in [0, 1] range** before training

## 🆘 If It Still Fails

Check this order:

1. Is `N_SENSORS = 325`? 
2. Is scaler shape `(325,)` for both min and max?
3. Are X and y shapes `(n, 12, 325)`?
4. Are values in range `[0, 1]`?
5. Did you pass `n_sensors=325` to the function?

If all ✅, then it should work!

---

**Last Updated:** 2025-11-02
**Status:** ✅ Fixed and Tested
