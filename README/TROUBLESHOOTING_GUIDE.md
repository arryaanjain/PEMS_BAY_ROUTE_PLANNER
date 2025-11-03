# Troubleshooting Guide - Testing Suite Errors

## Error 1: Shape Mismatch Error

### Error Message
```
ValueError: non-broadcastable output operand with shape (40634100,1) 
doesn't match the broadcast shape (40634100,325)
```

### Diagnosis
```python
# Check if n_sensors is missing
# In your code, you're doing:
run_complete_testing_suite(model, X_train, X_val, X_test, y_train, y_val, y_test, scaler)
# ❌ Missing n_sensors parameter!
```

### Solution
```python
# Add the n_sensors parameter:
run_complete_testing_suite(
    model, X_train, X_val, X_test, y_train, y_val, y_test, 
    scaler,
    n_sensors=325  # ✅ Add this!
)
```

**Status After Fix:** ✅ Error should be gone

---

## Error 2: Data Out of Range Error

### Error Message
```
AssertionError: ❌ X data out of expected range
```

### Diagnosis
```python
print(f"X_test range: [{X_test.min():.4f}, {X_test.max():.4f}]")
# If min < 0 or max > 1, data is out of range
```

### Causes & Solutions

| Cause | Solution |
|-------|----------|
| **NaN values in data** | Replace with column mean or remove rows |
| **Inf values in data** | Replace with 0 (for -inf) or 1 (for +inf) |
| **Scaler not fitted properly** | Refit scaler on full dataset |
| **Floating point errors** | Use `np.clip(data, 0, 1)` |

### Fix Code
```python
# Option 1: Auto-fix in testing module (already built-in)
run_complete_testing_suite(model, X_train, X_val, X_test, y_train, y_val, y_test, scaler, n_sensors=325)
# The test module will auto-clip values to [0, 1]

# Option 2: Manual fix before testing
X_test = np.clip(X_test, 0, 1)
y_test = np.clip(y_test, 0, 1)
```

**Status After Fix:** ✅ Error should be handled

---

## Error 3: NaN in Predictions

### Error Message
```
⚠️ Out of bounds predictions detected
Predictions contain NaN or Inf values
```

### Diagnosis
```python
y_pred = model.predict(X_test, verbose=0)
print(f"NaN count: {np.isnan(y_pred).sum()}")
print(f"Inf count: {np.isinf(y_pred).sum()}")
print(f"Range: [{y_pred.min()}, {y_pred.max()}]")
```

### Common Causes

1. **Model not trained well** → Retrain with more epochs
2. **Exploding gradients** → Reduce learning rate
3. **Input data issues** → Fix data preprocessing
4. **Model architecture problem** → Simplify model

### Quick Fix
```python
# Clip predictions to valid range
y_pred = np.clip(y_pred, 0, 1)

# Or add clipping layer to model
from tensorflow.keras.layers import Lambda
model.add(Lambda(lambda x: tf.clip_by_value(x, 0, 1)))
```

**Status After Fix:** ✅ Predictions will be valid

---

## Error 4: Scaler Not Loaded

### Error Message
```
AttributeError: 'NoneType' object has no attribute 'data_min_'
or
NameError: name 'scaler' is not defined
```

### Diagnosis
```python
print(scaler)  # Should NOT be None
```

### Solution
```python
# Load the scaler
import pickle

with open('scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)

print("✅ Scaler loaded")
print(f"Scaler shape: {scaler.data_min_.shape}")
```

**Status After Fix:** ✅ Scaler ready to use

---

## Error 5: Wrong N_SENSORS Value

### Error Message
```
ValueError: could not broadcast input array from shape (n,325) into shape (n,325)
```

### Diagnosis
```python
print(f"N_SENSORS: {N_SENSORS}")
print(f"Scaler features: {scaler.data_min_.shape[0]}")
print(f"X_test features: {X_test.shape[2]}")

# All three should be 325
```

### Solution
```python
# Make sure N_SENSORS is correct
N_SENSORS = 325  # For PEMS Bay

# Verify it matches your data
assert X_test.shape[2] == 325, f"Expected 325 sensors, got {X_test.shape[2]}"
assert scaler.data_min_.shape[0] == 325, f"Scaler expects 325 features"

print("✅ N_SENSORS is correct")
```

**Status After Fix:** ✅ Shapes will match

---

## Error 6: Model Not Loaded

### Error Message
```
AttributeError: 'NoneType' object has no attribute 'predict'
or
NameError: name 'model' is not defined
```

### Diagnosis
```python
print(model)  # Should show model summary, not None
```

### Solution
```python
from tensorflow.keras.models import load_model

model = load_model('cnn_traffic_model.keras')
print("✅ Model loaded")
print(model.summary())
```

**Status After Fix:** ✅ Model ready

---

## Verification Checklist

Before running tests, verify all of these:

```python
# 1. Model loaded
assert model is not None
print("✅ Model loaded")

# 2. Scaler loaded
assert scaler is not None
print("✅ Scaler loaded")

# 3. N_SENSORS correct
assert N_SENSORS == 325
print("✅ N_SENSORS correct")

# 4. Data shapes correct
assert X_test.shape == (len(X_test), 12, 325)
assert y_test.shape == (len(y_test), 12, 325)
print("✅ Data shapes correct")

# 5. Data in valid range
assert X_test.min() >= 0 and X_test.max() <= 1
assert y_test.min() >= 0 and y_test.max() <= 1
print("✅ Data in valid range")

# 6. Scaler shape correct
assert scaler.data_min_.shape[0] == 325
assert scaler.data_max_.shape[0] == 325
print("✅ Scaler shape correct")

print("\n✅ ALL CHECKS PASSED - Ready to test!")
```

---

## Quick Diagnostic Script

Copy and run this in your notebook to diagnose any issues:

```python
print("="*70)
print("DIAGNOSTIC CHECK")
print("="*70)

# 1. Model
try:
    print(f"\n✓ Model: {type(model).__name__}")
    print(f"  Predictions shape: {model.predict(X_test[0:1], verbose=0).shape}")
except Exception as e:
    print(f"✗ Model Error: {e}")

# 2. Scaler
try:
    print(f"\n✓ Scaler: {type(scaler).__name__}")
    print(f"  Features: {scaler.data_min_.shape[0]}")
    print(f"  Min range: {scaler.data_min_[0]:.2f}")
    print(f"  Max range: {scaler.data_max_[0]:.2f}")
except Exception as e:
    print(f"✗ Scaler Error: {e}")

# 3. Data
try:
    print(f"\n✓ Data:")
    print(f"  X_test: {X_test.shape}, range: [{X_test.min():.4f}, {X_test.max():.4f}]")
    print(f"  y_test: {y_test.shape}, range: [{y_test.min():.4f}, {y_test.max():.4f}]")
except Exception as e:
    print(f"✗ Data Error: {e}")

# 4. N_SENSORS
try:
    print(f"\n✓ N_SENSORS: {N_SENSORS}")
except Exception as e:
    print(f"✗ N_SENSORS Error: {e}")

# 5. Testing
try:
    from cnn_model_testing import run_complete_testing_suite
    print(f"\n✓ Testing module imported successfully")
except Exception as e:
    print(f"✗ Testing module Error: {e}")

print("\n" + "="*70)
```

---

## Common Patterns & Fixes

### Pattern 1: Missing Parameter
```python
# ❌ BROKEN
run_complete_testing_suite(model, X_train, X_val, X_test, y_train, y_val, y_test, scaler)

# ✅ FIXED
run_complete_testing_suite(model, X_train, X_val, X_test, y_train, y_val, y_test, scaler, n_sensors=325)
```

### Pattern 2: Wrong Variable Name
```python
# ❌ BROKEN
N_sensors = 325  # lowercase 's'
run_complete_testing_suite(..., n_sensors=N_SENSORS)  # NameError!

# ✅ FIXED
N_SENSORS = 325  # uppercase 'S'
run_complete_testing_suite(..., n_sensors=N_SENSORS)  # Works!
```

### Pattern 3: Data Not Normalized
```python
# ❌ BROKEN
# Data range: [0, 100] (not normalized!)

# ✅ FIXED
# Use MinMaxScaler first
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()
data_normalized = scaler.fit_transform(data_raw)
# Now data is in [0, 1]
```

---

## Getting Help

1. **Check the error message** - Usually tells you the problem
2. **Run the diagnostic script** - Identifies which component failed
3. **Verify the checklist** - Make sure all prerequisites are met
4. **Check the documentation** - Refer to comments in code

---

## Reference Documents

- `FIX_SUMMARY.md` - Overall summary of fixes
- `FIX_SHAPE_MISMATCH_ERROR.md` - Detailed shape error explanation
- `QUICK_REFERENCE_FIXED.md` - Quick reference guide
- `cnn_model_testing.py` - Source code with detailed comments

---

**Remember:** Most errors are due to missing `n_sensors=325` parameter or data range issues. Check those first!
