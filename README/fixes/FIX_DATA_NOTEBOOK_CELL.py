# ============================================================================
# FIX OUT-OF-RANGE DATA - ADD THIS CELL TO YOUR NOTEBOOK
# ============================================================================
# Run this cell BEFORE calling run_complete_testing_suite()
# This will automatically fix any out-of-range values in your data

import numpy as np

print("\n" + "="*80)
print("🔧 FIXING OUT-OF-RANGE DATA")
print("="*80)

# Store original data info
print("\n📊 Before Fix:")
print(f"  X_train range: [{X_train.min():.10f}, {X_train.max():.10f}]")
print(f"  X_val range:   [{X_val.min():.10f}, {X_val.max():.10f}]")
print(f"  X_test range:  [{X_test.min():.10f}, {X_test.max():.10f}]")
print(f"  y_train range: [{y_train.min():.10f}, {y_train.max():.10f}]")
print(f"  y_val range:   [{y_val.min():.10f}, {y_val.max():.10f}]")
print(f"  y_test range:  [{y_test.min():.10f}, {y_test.max():.10f}]")

# Count out-of-range values
out_of_range_before = (
    ((X_train < 0) | (X_train > 1)).sum() +
    ((X_val < 0) | (X_val > 1)).sum() +
    ((X_test < 0) | (X_test > 1)).sum() +
    ((y_train < 0) | (y_train > 1)).sum() +
    ((y_val < 0) | (y_val > 1)).sum() +
    ((y_test < 0) | (y_test > 1)).sum()
)

print(f"\n⚠️  Out-of-range values found: {out_of_range_before}")

# Step 1: Fix NaN values
print("\n✓ Fixing NaN values...")
nan_count = (
    np.isnan(X_train).sum() + np.isnan(X_val).sum() + np.isnan(X_test).sum() +
    np.isnan(y_train).sum() + np.isnan(y_val).sum() + np.isnan(y_test).sum()
)

if nan_count > 0:
    print(f"  Found {nan_count} NaN values - replacing with 0.5 (normalized mean)...")
    
    X_train = np.nan_to_num(X_train, nan=0.5)
    X_val = np.nan_to_num(X_val, nan=0.5)
    X_test = np.nan_to_num(X_test, nan=0.5)
    y_train = np.nan_to_num(y_train, nan=0.5)
    y_val = np.nan_to_num(y_val, nan=0.5)
    y_test = np.nan_to_num(y_test, nan=0.5)
    print(f"  ✅ NaN values fixed")
else:
    print(f"  ✅ No NaN values found")

# Step 2: Fix Infinite values
print("\n✓ Fixing infinite values...")
inf_count = (
    np.isinf(X_train).sum() + np.isinf(X_val).sum() + np.isinf(X_test).sum() +
    np.isinf(y_train).sum() + np.isinf(y_val).sum() + np.isinf(y_test).sum()
)

if inf_count > 0:
    print(f"  Found {inf_count} infinite values...")
    
    # Replace positive inf with 1, negative inf with 0
    X_train = np.where(np.isposinf(X_train), 1.0, np.where(np.isneginf(X_train), 0.0, X_train))
    X_val = np.where(np.isposinf(X_val), 1.0, np.where(np.isneginf(X_val), 0.0, X_val))
    X_test = np.where(np.isposinf(X_test), 1.0, np.where(np.isneginf(X_test), 0.0, X_test))
    y_train = np.where(np.isposinf(y_train), 1.0, np.where(np.isneginf(y_train), 0.0, y_train))
    y_val = np.where(np.isposinf(y_val), 1.0, np.where(np.isneginf(y_val), 0.0, y_val))
    y_test = np.where(np.isposinf(y_test), 1.0, np.where(np.isneginf(y_test), 0.0, y_test))
    print(f"  ✅ Infinite values fixed")
else:
    print(f"  ✅ No infinite values found")

# Step 3: Clip values to [0, 1]
print("\n✓ Clipping values to [0, 1] range...")

X_train = np.clip(X_train, 0, 1)
X_val = np.clip(X_val, 0, 1)
X_test = np.clip(X_test, 0, 1)
y_train = np.clip(y_train, 0, 1)
y_val = np.clip(y_val, 0, 1)
y_test = np.clip(y_test, 0, 1)

print(f"  ✅ Clipping complete")

# Verify the fix
print("\n📊 After Fix:")
print(f"  X_train range: [{X_train.min():.10f}, {X_train.max():.10f}]")
print(f"  X_val range:   [{X_val.min():.10f}, {X_val.max():.10f}]")
print(f"  X_test range:  [{X_test.min():.10f}, {X_test.max():.10f}]")
print(f"  y_train range: [{y_train.min():.10f}, {y_train.max():.10f}]")
print(f"  y_val range:   [{y_val.min():.10f}, {y_val.max():.10f}]")
print(f"  y_test range:  [{y_test.min():.10f}, {y_test.max():.10f}]")

# Final verification
all_valid = (
    (X_train.min() >= 0 and X_train.max() <= 1) and
    (X_val.min() >= 0 and X_val.max() <= 1) and
    (X_test.min() >= 0 and X_test.max() <= 1) and
    (y_train.min() >= 0 and y_train.max() <= 1) and
    (y_val.min() >= 0 and y_val.max() <= 1) and
    (y_test.min() >= 0 and y_test.max() <= 1) and
    not np.isnan(X_train).any() and not np.isnan(X_val).any() and not np.isnan(X_test).any() and
    not np.isnan(y_train).any() and not np.isnan(y_val).any() and not np.isnan(y_test).any()
)

if all_valid:
    print("\n" + "="*80)
    print("✅ ALL DATA FIXED AND VALIDATED!")
    print("   You can now safely run: run_complete_testing_suite(...)")
    print("="*80)
else:
    print("\n" + "="*80)
    print("⚠️  WARNING: Some data quality issues remain")
    print("="*80)
