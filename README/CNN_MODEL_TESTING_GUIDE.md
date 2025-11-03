# CNN Traffic Model Testing Guide

Complete testing methodology for your PEMS Bay CNN traffic prediction model.

## Testing Strategy Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    CNN MODEL TESTING PHASES                  │
├─────────────────────────────────────────────────────────────┤
│ 1. Data Quality Testing                                       │
│ 2. Model Training Validation                                  │
│ 3. Performance Metrics Evaluation                             │
│ 4. Temporal Validation (Time-series specific)                │
│ 5. Edge Case Testing                                          │
│ 6. Integration Testing (with FastAPI backend)                │
│ 7. Production Readiness Testing                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Data Quality Testing

### What to Test
- ✅ Data completeness (missing values, NaNs)
- ✅ Data ranges (min/max values are realistic)
- ✅ Data distribution (outliers, anomalies)
- ✅ Train/Val/Test split validity
- ✅ Scaler fit integrity

### How to Test
```python
# Check for NaNs and missing values
assert not X_train.isnan().any(), "NaNs found in training data"
assert not y_train.isnan().any(), "NaNs found in training targets"

# Check data ranges (speeds should be 0-100+ mph)
assert X_train.min() >= 0 and X_train.max() <= 1, "Data not normalized"
assert y_train.min() >= 0 and y_train.max() <= 1, "Targets not normalized"

# Check shapes
assert X_train.shape[1] == 12, "Input sequence length incorrect"
assert X_train.shape[2] == 325, "Number of sensors incorrect"
```

---

## Phase 2: Model Training Validation

### What to Test
- ✅ Model compiles without errors
- ✅ Training loss decreases over epochs
- ✅ Validation loss follows training loss (not diverging)
- ✅ No exploding/vanishing gradients
- ✅ Model converges to acceptable loss

### Key Metrics to Monitor
```
Training Loss:    MSE between predictions and actual
Validation Loss:  MSE on unseen validation set
Overfitting Gap:  |Train Loss - Val Loss| should be small
Epoch Time:       Time per epoch (consistency check)
```

### Red Flags 🚩
- ❌ Training loss not decreasing → Learning rate too low or model architecture issue
- ❌ Val loss diverging from train loss → Overfitting
- ❌ Loss becomes NaN → Exploding gradients (reduce learning rate)
- ❌ Very slow training → Check GPU usage, batch size

---

## Phase 3: Performance Metrics Evaluation

### Essential Metrics for Regression (Traffic Prediction)

#### 1. **Mean Squared Error (MSE)**
```
Formula: MSE = (1/n) * Σ(y_true - y_pred)²
What it means: Average squared difference between predicted and actual
Better: Lower is better
Range: 0 to ∞
```

#### 2. **Root Mean Squared Error (RMSE)**
```
Formula: RMSE = √MSE
What it means: MSE in original units (speed in mph)
Better: Lower is better
Interpretation: On average, predictions are off by X mph
```

#### 3. **Mean Absolute Error (MAE)**
```
Formula: MAE = (1/n) * Σ|y_true - y_pred|
What it means: Average absolute difference
Better: Lower is better
Advantage: Less sensitive to outliers than MSE
```

#### 4. **Mean Absolute Percentage Error (MAPE)**
```
Formula: MAPE = (100/n) * Σ|y_true - y_pred| / |y_true|
What it means: Average percentage error
Better: Lower is better
Range: 0% to ∞% (good model < 10%)
```

#### 5. **R² Score (Coefficient of Determination)**
```
Formula: R² = 1 - (SS_res / SS_tot)
What it means: Proportion of variance explained by model
Better: Higher is better
Range: 0 to 1 (1 = perfect, 0 = no better than mean)
Interpretation: R²=0.85 means model explains 85% of variance
```

---

## Phase 4: Temporal Validation (Time-Series Specific)

### Why This Matters
Traffic data has temporal patterns (rush hours, day of week, etc.)

### Tests to Perform

#### 4.1 **Temporal Consistency**
```python
# Prediction should not jump drastically between consecutive time steps
predictions_diff = np.diff(predictions, axis=1)
max_jump = np.max(np.abs(predictions_diff))
assert max_jump < 0.15, f"Prediction jumps too large: {max_jump}"
```

#### 4.2 **Seasonal Pattern Recognition**
```python
# Check if model captures peak hours better than off-peak
peak_hours_mae = calculate_mae_for_time_window(6, 10)  # 6-10 AM
off_peak_mae = calculate_mae_for_time_window(11, 15)   # 11 AM-3 PM
assert peak_hours_mae < off_peak_mae * 1.2, "Model struggles with peak hours"
```

#### 4.3 **Walk-Forward Validation**
```python
# Simulate production: predict next day using previous data
for test_date in test_dates:
    historical_data = get_data_before(test_date)
    predictions = model.predict(historical_data)
    actual = get_actual_data(test_date)
    error = calculate_error(predictions, actual)
    log_error(test_date, error)
```

---

## Phase 5: Edge Case Testing

### What to Test

#### 5.1 **Extreme Traffic Conditions**
```python
# Test on congested segments (very low speeds)
congested_predictions = model.predict(congested_test_samples)
# Check if model doesn't over-predict or under-predict

# Test on free-flow segments (high speeds)
freeflow_predictions = model.predict(freeflow_test_samples)
# Ensure realistic predictions
```

#### 5.2 **Missing Data Scenarios**
```python
# What if a sensor goes offline?
corrupted_input = X_test.copy()
corrupted_input[:, :, 50] = 0.5  # Fill sensor 50 with mean value
predictions_corrupted = model.predict(corrupted_input)
# Should still produce reasonable predictions
```

#### 5.3 **Boundary Predictions**
```python
# Predictions should stay within [0, 1] normalized range
assert (predictions_test >= 0).all() and (predictions_test <= 1).all()
```

---

## Phase 6: Integration Testing

### Test with FastAPI Backend

#### 6.1 **Model Loading**
```python
# Simulate what your FastAPI endpoint will do
model = load_model('cnn_traffic_model.keras')
scaler = load_scaler('scaler.pkl')
assert model is not None
assert scaler is not None
print("✅ Model and scaler loaded successfully")
```

#### 6.2 **Endpoint Testing**
```python
# Test the /api/optimize-route endpoint
test_request = {
    "waypoints": [
        {"lat": 37.3382, "lng": -121.8863, "name": "Location A"},
        {"lat": 37.4419, "lng": -122.1430, "name": "Location B"}
    ],
    "startTime": "2025-11-02T08:00:00",
    "duration": 2,
    "durationType": "hours"
}

response = requests.post(
    "http://localhost:8000/api/optimize-route",
    json=test_request
)

assert response.status_code == 200
result = response.json()
assert "optimizedRoute" in result
assert "itinerary" in result
```

#### 6.3 **Prediction Denormalization**
```python
# Ensure predictions are correctly converted back to speed values
normalized_pred = model.predict(X_test)[0]  # [0, 1] range
actual_speed = scaler.inverse_transform(normalized_pred)
# Should be in realistic range (e.g., 10-80 mph)
assert (actual_speed >= 0).all() and (actual_speed <= 100).all()
```

---

## Phase 7: Production Readiness Checklist

- ✅ Model converges consistently
- ✅ Test set MSE acceptable (< X%)
- ✅ R² score > 0.75
- ✅ No NaN or Inf predictions
- ✅ Inference time < 100ms
- ✅ Memory usage < 500MB
- ✅ Handles edge cases gracefully
- ✅ Scaler properly persisted
- ✅ Integration tests pass
- ✅ Documentation complete

---

## Testing Workflow (Recommended Order)

```
1. Run Data Quality Tests
   ↓
2. Train Model (monitor Training/Val loss)
   ↓
3. Calculate Performance Metrics on Test Set
   ↓
4. Run Temporal Validation Tests
   ↓
5. Test Edge Cases
   ↓
6. Run Integration Tests with FastAPI
   ↓
7. Final Production Readiness Check
```

---

## Success Criteria for Your Model

| Metric | Target | Why |
|--------|--------|-----|
| **RMSE** | < 5 mph | Predictions accurate within 5 mph |
| **MAE** | < 4 mph | Average error acceptable |
| **MAPE** | < 15% | Percentage error reasonable |
| **R²** | > 0.80 | Model explains 80%+ of variance |
| **Inference Time** | < 50ms | Fast enough for real-time routing |
| **Max Prediction** | ≤ 100 | No unrealistic high speeds |
| **Min Prediction** | ≥ 0 | No negative speeds |

---

## Next Steps

1. Add the **comprehensive testing notebook** with all test functions
2. Create **automated test suite** (pytest for backend)
3. Set up **continuous testing** on new data monthly
4. Monitor **model drift** (retrain if performance degrades)
5. Log all predictions for future analysis

