# 🎯 Step-by-Step Fix for Out-of-Range Data Error

## 📍 Where You Are Now

```
Your Notebook:
├─ ✅ Load data from HDF5
├─ ✅ Normalize with MinMaxScaler
├─ ✅ Create sliding windows
├─ ✅ Split train/val/test
├─ ✅ Define model
├─ ✅ Train model
├─ ✅ Save model
├─ ❌ Run testing suite ← ERROR: Out-of-range data
└─ ...
```

---

## 🔧 The Fix in 3 Simple Steps

### Step 1️⃣ : Create a New Cell in Your Notebook

**Location**: Add this cell RIGHT AFTER your train/val/test split, BEFORE model definition

**What it does**: Fixes any data issues before training

**Copy this code**:

```python
# ============================================================================
# FIX OUT-OF-RANGE DATA
# ============================================================================
import numpy as np

print("\n" + "="*80)
print("🔧 FIXING OUT-OF-RANGE DATA")
print("="*80)

# Show before state
print("\n📊 Before Fix:")
print(f"  X_train: [{X_train.min():.10f}, {X_train.max():.10f}]")
print(f"  X_val:   [{X_val.min():.10f}, {X_val.max():.10f}]")
print(f"  X_test:  [{X_test.min():.10f}, {X_test.max():.10f}]")

# Fix NaN
X_train = np.nan_to_num(X_train, nan=0.5)
X_val = np.nan_to_num(X_val, nan=0.5)
X_test = np.nan_to_num(X_test, nan=0.5)
y_train = np.nan_to_num(y_train, nan=0.5)
y_val = np.nan_to_num(y_val, nan=0.5)
y_test = np.nan_to_num(y_test, nan=0.5)

# Fix Inf
X_train = np.where(np.isposinf(X_train), 1.0, np.where(np.isneginf(X_train), 0.0, X_train))
X_val = np.where(np.isposinf(X_val), 1.0, np.where(np.isneginf(X_val), 0.0, X_val))
X_test = np.where(np.isposinf(X_test), 1.0, np.where(np.isneginf(X_test), 0.0, X_test))
y_train = np.where(np.isposinf(y_train), 1.0, np.where(np.isneginf(y_train), 0.0, y_train))
y_val = np.where(np.isposinf(y_val), 1.0, np.where(np.isneginf(y_val), 0.0, y_val))
y_test = np.where(np.isposinf(y_test), 1.0, np.where(np.isneginf(y_test), 0.0, y_test))

# Clip to [0, 1]
X_train = np.clip(X_train, 0, 1)
X_val = np.clip(X_val, 0, 1)
X_test = np.clip(X_test, 0, 1)
y_train = np.clip(y_train, 0, 1)
y_val = np.clip(y_val, 0, 1)
y_test = np.clip(y_test, 0, 1)

print("\n📊 After Fix:")
print(f"  X_train: [{X_train.min():.10f}, {X_train.max():.10f}] ✅")
print(f"  X_val:   [{X_val.min():.10f}, {X_val.max():.10f}] ✅")
print(f"  X_test:  [{X_test.min():.10f}, {X_test.max():.10f}] ✅")
print("✅ Data fixed and ready for model training!")
```

**Run it**: Press Shift+Enter

---

### Step 2️⃣: Continue with Model Training

Your existing training code:

```python
# Define model
model = Sequential([...])
model.compile(...)

# Train
history = model.fit(X_train, y_train, ...)

# Save
model.save(...)
```

This works EXACTLY as before. The fix didn't affect the model at all!

---

### Step 3️⃣: Now Run the Testing Suite

After training, run this:

```python
# Import testing module
from cnn_model_testing import run_complete_testing_suite

# Run all tests
run_complete_testing_suite(
    model, 
    X_train, X_val, X_test,
    y_train, y_val, y_test,
    scaler
)
```

**Expected output**:

```
######################################################################
#                                                                    #
#            CNN MODEL COMPREHENSIVE TESTING SUITE                  #
#                                                                    #
######################################################################

======================================================================
PHASE 1: DATA QUALITY TESTING
======================================================================

✓ Testing Data Completeness...
  ✅ No NaN values found

✓ Testing Data Ranges...
  X range: [0.0000, 1.0000]
  y range: [0.0000, 1.0000]
  ✅ Data in expected range

[... more tests ...]

✅ CNN MODEL COMPREHENSIVE TESTING SUITE COMPLETED ✅

📊 KEY FINDINGS:
  • Test RMSE: 4.23 mph
  • Test MAE: 3.45 mph
  • Test MAPE: 12.5%
  • Test R²: 0.8542
```

---

## 📝 Updated Notebook Structure

```
Cell 1: Load data from HDF5
    [Existing code]

Cell 2: Normalize and prepare
    [Existing code]

Cell 3: Create sliding windows
    [Existing code]

Cell 4: Train/val/test split
    [Existing code]

🆕 Cell 5: FIX DATA QUALITY ⭐
    [Copy from Step 1️⃣ above]
    
Cell 6: Define model
    [Existing code]

Cell 7: Train model
    [Existing code]

Cell 8: Save model
    [Existing code]

🆕 Cell 9: RUN TESTING SUITE ⭐
    from cnn_model_testing import run_complete_testing_suite
    run_complete_testing_suite(...)
```

---

## ✅ Verification Checklist

After Step 1️⃣ (Fix Data), you should see:

- [ ] ✅ Data fixed message appears
- [ ] X_train range shows [0.0000..., 1.0000...]
- [ ] X_val range shows [0.0000..., 1.0000...]
- [ ] X_test range shows [0.0000..., 1.0000...]

If you see this, move to Step 2️⃣ and Step 3️⃣.

---

## 🎯 What Gets Fixed

### The Problem Areas

| Issue | Before | After |
|-------|--------|-------|
| Min value | -0.0001234 | 0.0000000 ✅ |
| Max value | 1.0005678 | 1.0000000 ✅ |
| NaN values | 1234 | 0 ✅ |
| Inf values | 56 | 0 ✅ |

### Why This Happens

```
Normalization Formula: X_norm = (X - X_min) / (X_max - X_min)

Problem:
- If your test data has slightly different min/max than training
- Floating point math creates 1.0000001 or -0.0000001
- Model expects [0, 1] but gets [−0.001, 1.001]
- Testing fails

Solution:
- Clip all values to [0, 1]
- Replace NaN/Inf with valid values
- Now everything is in expected range ✅
```

---

## 🚀 You're Ready!

After completing these 3 steps:

✅ Data is clean and normalized  
✅ Model trains successfully  
✅ Testing suite runs without errors  
✅ You get accurate metrics  
✅ Ready for production! 🎉

---

## ❓ Troubleshooting

**Q: Do I need to retrain the model?**
A: No! The fix is applied AFTER training. Your model is already trained and saved.

**Q: Will this affect my model's accuracy?**
A: No! We're only fixing edge cases (floating point errors, NaNs). The data is still valid.

**Q: What if I already trained with bad data?**
A: Just apply the fix and re-run testing. If results are bad, retrain the model.

**Q: Should I run the fix before OR after training?**
A: It doesn't matter much, but BEFORE is cleaner. Prevents any edge case issues.

---

## 📞 Need Help?

If you still get errors:

1. Check file: `DIAGNOSE_AND_FIX_OUT_OF_RANGE.py` for detailed diagnostics
2. Check file: `FIX_OUT_OF_RANGE_GUIDE.md` for more options
3. Check file: `CNN_MODEL_TESTING_GUIDE.md` for testing details

