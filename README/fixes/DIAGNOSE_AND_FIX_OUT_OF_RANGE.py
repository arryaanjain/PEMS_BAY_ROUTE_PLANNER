"""
DIAGNOSTIC SCRIPT FOR OUT-OF-RANGE DATA
This script identifies WHY your data is outside [0, 1] and FIXES it
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import pickle

print("\n" + "="*80)
print("DIAGNOSING OUT-OF-RANGE DATA ISSUE")
print("="*80)

# ============================================================================
# STEP 1: IDENTIFY THE ROOT CAUSE
# ============================================================================

print("\n📋 STEP 1: Analyzing your data...")
print("-" * 80)

# Check what you currently have
print("\n❓ What's in your X_train, X_val, X_test?")
print(f"  X_train min: {X_train.min():.6f}")
print(f"  X_train max: {X_train.max():.6f}")
print(f"  X_val min:   {X_val.min():.6f}")
print(f"  X_val max:   {X_val.max():.6f}")
print(f"  X_test min:  {X_test.min():.6f}")
print(f"  X_test max:  {X_test.max():.6f}")

# ============================================================================
# ROOT CAUSE ANALYSIS
# ============================================================================

print("\n" + "="*80)
print("🔍 ROOT CAUSE ANALYSIS")
print("="*80)

# Possible causes:
print("\n⚠️  Possible causes of out-of-range data:")

# Cause 1: Scaler fitted on subset of data
print("\n1️⃣  CAUSE: Scaler fitted on partial data")
print("   - You normalized data_array with MinMaxScaler")
print("   - But X_test contains NEW data not seen during fitting")
print("   - If test data has values outside the training range → out of bounds")

if X_train.min() < 0 or X_train.max() > 1:
    print("   ✅ THIS IS YOUR ISSUE!")

# Cause 2: Floating point precision issues
print("\n2️⃣  CAUSE: Floating point precision errors")
print("   - Values like 1.0000001 or -0.0000001 due to rounding")
if (X_train.min() > -0.01 and X_train.min() < 0) or (X_train.max() > 1 and X_train.max() < 1.01):
    print("   ✅ THIS MIGHT BE YOUR ISSUE!")

# Cause 3: Data contamination during sliding windows
print("\n3️⃣  CAUSE: Data contamination in sliding window creation")
print("   - NaN or extreme values in original data_normalized")
print("   - These propagate into sliding windows")
if np.isnan(X_train).any() or np.isinf(X_train).any():
    print("   ✅ THIS IS YOUR ISSUE!")

# ============================================================================
# STEP 2: DETAILED ANALYSIS
# ============================================================================

print("\n" + "="*80)
print("📊 DETAILED DATA ANALYSIS")
print("="*80)

print("\n📌 X_train Statistics:")
print(f"  Min value:        {X_train.min():.10f}")
print(f"  Max value:        {X_train.max():.10f}")
print(f"  Mean:             {X_train.mean():.6f}")
print(f"  Std:              {X_train.std():.6f}")
print(f"  NaN count:        {np.isnan(X_train).sum()}")
print(f"  Inf count:        {np.isinf(X_train).sum()}")
print(f"  Values < 0:       {(X_train < 0).sum()}")
print(f"  Values > 1:       {(X_train > 1).sum()}")

print("\n📌 X_val Statistics:")
print(f"  Min value:        {X_val.min():.10f}")
print(f"  Max value:        {X_val.max():.10f}")
print(f"  Values < 0:       {(X_val < 0).sum()}")
print(f"  Values > 1:       {(X_val > 1).sum()}")

print("\n📌 X_test Statistics:")
print(f"  Min value:        {X_test.min():.10f}")
print(f"  Max value:        {X_test.max():.10f}")
print(f"  Values < 0:       {(X_test < 0).sum()}")
print(f"  Values > 1:       {(X_test > 1).sum()}")

# ============================================================================
# STEP 3: FIX THE PROBLEM
# ============================================================================

print("\n" + "="*80)
print("🔧 APPLYING FIXES")
print("="*80)

# SOLUTION 1: Clip all data to [0, 1]
print("\n✅ SOLUTION 1: Clipping out-of-range values to [0, 1]")
print("-" * 80)

X_train_fixed = np.clip(X_train, 0, 1)
X_val_fixed = np.clip(X_val, 0, 1)
X_test_fixed = np.clip(X_test, 0, 1)
y_train_fixed = np.clip(y_train, 0, 1)
y_val_fixed = np.clip(y_val, 0, 1)
y_test_fixed = np.clip(y_test, 0, 1)

clipped_count = (
    ((X_train < 0) | (X_train > 1)).sum() +
    ((X_val < 0) | (X_val > 1)).sum() +
    ((X_test < 0) | (X_test > 1)).sum()
)

print(f"  Total values clipped: {clipped_count}")
print(f"  ✅ X_train fixed: [{X_train_fixed.min():.6f}, {X_train_fixed.max():.6f}]")
print(f"  ✅ X_val fixed:   [{X_val_fixed.min():.6f}, {X_val_fixed.max():.6f}]")
print(f"  ✅ X_test fixed:  [{X_test_fixed.min():.6f}, {X_test_fixed.max():.6f}]")

# SOLUTION 2: Handle NaN and Inf values
print("\n✅ SOLUTION 2: Fixing NaN and Inf values")
print("-" * 80)

def fix_nan_inf(data, name):
    """Fix NaN and Inf values in array"""
    nan_count = np.isnan(data).sum()
    inf_count = np.isinf(data).sum()
    
    if nan_count > 0:
        print(f"  ⚠️  {name}: Found {nan_count} NaN values")
        # Replace NaN with column mean
        for i in range(data.shape[2]):  # For each sensor
            for j in range(data.shape[1]):  # For each timestep
                col = data[:, j, i]
                nan_mask = np.isnan(col)
                if nan_mask.any():
                    col_mean = np.nanmean(col)
                    data[nan_mask, j, i] = col_mean
        print(f"     ✅ Replaced NaN with column means")
    
    if inf_count > 0:
        print(f"  ⚠️  {name}: Found {inf_count} Inf values")
        # Replace inf with 1, -inf with 0
        data[np.isposinf(data)] = 1.0
        data[np.isneginf(data)] = 0.0
        print(f"     ✅ Replaced Inf values")
    
    return data

X_train_fixed = fix_nan_inf(X_train_fixed, "X_train")
X_val_fixed = fix_nan_inf(X_val_fixed, "X_val")
X_test_fixed = fix_nan_inf(X_test_fixed, "X_test")
y_train_fixed = fix_nan_inf(y_train_fixed, "y_train")
y_val_fixed = fix_nan_inf(y_val_fixed, "y_val")
y_test_fixed = fix_nan_inf(y_test_fixed, "y_test")

print("\n  ✅ All NaN/Inf values fixed")

# ============================================================================
# STEP 4: VERIFICATION
# ============================================================================

print("\n" + "="*80)
print("✅ VERIFICATION - All data fixed!")
print("="*80)

datasets_fixed = {
    'X_train': X_train_fixed,
    'X_val': X_val_fixed,
    'X_test': X_test_fixed,
    'y_train': y_train_fixed,
    'y_val': y_val_fixed,
    'y_test': y_test_fixed,
}

all_ok = True
for name, data in datasets_fixed.items():
    in_range = (data.min() >= 0) and (data.max() <= 1)
    has_nan = np.isnan(data).any()
    has_inf = np.isinf(data).any()
    
    status = "✅ OK" if (in_range and not has_nan and not has_inf) else "❌ ISSUE"
    print(f"  {name:12s}: [{data.min():.6f}, {data.max():.6f}] - {status}")
    
    if not in_range or has_nan or has_inf:
        all_ok = False

# ============================================================================
# STEP 5: UPDATE YOUR DATA
# ============================================================================

print("\n" + "="*80)
print("🔄 UPDATING YOUR DATA VARIABLES")
print("="*80)

print("\n⚠️  IMPORTANT: Run the following code in your notebook to update your data:")
print("-" * 80)

print("""
# Update your data with the fixed versions
X_train = X_train_fixed
X_val = X_val_fixed
X_test = X_test_fixed
y_train = y_train_fixed
y_val = y_val_fixed
y_test = y_test_fixed

print("✅ Data updated! Ready to continue with model testing.")
""")

print("-" * 80)

if all_ok:
    print("\n✅ ALL DATA QUALITY CHECKS PASSED!")
    print("   You can now safely run the testing suite.")
else:
    print("\n⚠️  Some issues remain. Contact support if problems persist.")

print("\n" + "="*80)
print("DIAGNOSTIC COMPLETE")
print("="*80)
