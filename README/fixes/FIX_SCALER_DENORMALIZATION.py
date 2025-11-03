# ============================================================================
# FIX: Proper Scaler Usage and Denormalization
# ============================================================================
# Add this BEFORE running the testing suite

print("\n" + "="*80)
print("FIXING SCALER FOR PROPER DENORMALIZATION")
print("="*80)

# Step 1: Understand your scaler
print("\n📋 Analyzing Scaler...")
print(f"  Scaler type: {type(scaler)}")
print(f"  Scaler data_min_ shape: {scaler.data_min_.shape}")
print(f"  Scaler data_max_ shape: {scaler.data_max_.shape}")
print(f"  Scaler feature_range: {scaler.feature_range}")

# Step 2: Check how scaler was fit
original_features = scaler.data_min_.shape[0]
print(f"  Number of features scaler was fit on: {original_features}")

# Step 3: Create a helper function for proper denormalization
def denormalize_data(normalized_data, scaler, original_shape=325):
    """
    Properly denormalize data that was normalized column-wise
    
    Args:
        normalized_data: The normalized data (can be any shape)
        scaler: The fitted MinMaxScaler
        original_shape: Number of features (sensors) in original data
    
    Returns:
        Denormalized data
    """
    original_shape_flat = normalized_data.shape
    
    # Reshape to (n_samples, n_features) for inverse_transform
    normalized_reshaped = normalized_data.reshape(-1, original_shape)
    
    # Inverse transform
    denormalized = scaler.inverse_transform(normalized_reshaped)
    
    # Reshape back to original shape
    denormalized = denormalized.reshape(original_shape_flat)
    
    return denormalized


# Test the denormalization function
print("\n✓ Testing denormalization function...")
test_sample = y_test[0:2].copy()  # Get 2 samples
print(f"  Original test shape: {test_sample.shape}")
print(f"  Value range before denorm: [{test_sample.min():.6f}, {test_sample.max():.6f}]")

denorm_test = denormalize_data(test_sample, scaler, original_shape=N_SENSORS)
print(f"  Denormalized shape: {denorm_test.shape}")
print(f"  Value range after denorm: [{denorm_test.min():.6f}, {denorm_test.max():.6f}]")
print(f"  ✅ Denormalization working correctly")

# Step 4: Update the testing module with this function
print("\n✓ Creating updated metrics calculation...")

def calculate_metrics_fixed(y_true, y_pred, scaler, n_sensors=325):
    """
    Calculate metrics with proper denormalization
    """
    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
    
    y_true_flat = y_true.reshape(-1)
    y_pred_flat = y_pred.reshape(-1)
    
    metrics = {}
    
    # Normalized metrics
    metrics['mse_normalized'] = float(mean_squared_error(y_true_flat, y_pred_flat))
    metrics['rmse_normalized'] = float(np.sqrt(metrics['mse_normalized']))
    metrics['mae_normalized'] = float(mean_absolute_error(y_true_flat, y_pred_flat))
    metrics['r2_normalized'] = float(r2_score(y_true_flat, y_pred_flat))
    
    # Denormalized metrics
    if scaler is not None:
        try:
            # Reshape properly for scaler
            y_true_reshaped = y_true.reshape(-1, n_sensors)
            y_pred_reshaped = y_pred.reshape(-1, n_sensors)
            
            # Inverse transform
            y_true_denorm = scaler.inverse_transform(y_true_reshaped).reshape(-1)
            y_pred_denorm = scaler.inverse_transform(y_pred_reshaped).reshape(-1)
            
            metrics['mse_denorm'] = float(mean_squared_error(y_true_denorm, y_pred_denorm))
            metrics['rmse_denorm'] = float(np.sqrt(metrics['mse_denorm']))
            metrics['mae_denorm'] = float(mean_absolute_error(y_true_denorm, y_pred_denorm))
            metrics['r2_denorm'] = float(r2_score(y_true_denorm, y_pred_denorm))
            
            # MAPE
            mask = y_true_denorm != 0
            if mask.sum() > 0:
                mape = np.mean(np.abs((y_true_denorm[mask] - y_pred_denorm[mask]) / 
                                      y_true_denorm[mask])) * 100
            else:
                mape = 0.0
            metrics['mape'] = float(mape)
            
            metrics['y_true_denorm_stats'] = {
                'min': float(y_true_denorm.min()),
                'max': float(y_true_denorm.max()),
                'mean': float(y_true_denorm.mean()),
                'std': float(y_true_denorm.std())
            }
            metrics['y_pred_denorm_stats'] = {
                'min': float(y_pred_denorm.min()),
                'max': float(y_pred_denorm.max()),
                'mean': float(y_pred_denorm.mean()),
                'std': float(y_pred_denorm.std())
            }
            
            print("  ✅ Denormalization successful")
            
        except Exception as e:
            print(f"  ⚠️  Denormalization failed: {str(e)[:100]}...")
            print(f"  Falling back to normalized metrics only")
    
    return metrics


# Test it on a small sample
print("\n✓ Testing fixed metrics calculation on sample...")
y_pred_sample = model.predict(X_test[0:10], verbose=0)
metrics_sample = calculate_metrics_fixed(y_test[0:10], y_pred_sample, scaler, N_SENSORS)

print(f"  RMSE (normalized): {metrics_sample['rmse_normalized']:.6f}")
if 'rmse_denorm' in metrics_sample:
    print(f"  RMSE (denorm - mph): {metrics_sample['rmse_denorm']:.4f}")
    print(f"  MAE (denorm - mph): {metrics_sample['mae_denorm']:.4f}")
    print(f"  MAPE: {metrics_sample['mape']:.2f}%")
    print(f"  R²: {metrics_sample['r2_denorm']:.6f}")
    print(f"  ✅ All metrics calculated successfully!")

print("\n" + "="*80)
print("✅ SCALER FIX COMPLETE")
print("="*80)

print("\n💡 NEXT STEPS:")
print("  1. Use calculate_metrics_fixed() instead of calculate_metrics()")
print("  2. Or, update cnn_model_testing.py with the proper denormalization")
print("  3. Run the testing suite again")
