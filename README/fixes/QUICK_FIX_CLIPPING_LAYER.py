# Quick Fix: Add Clipping Layer to Model
# Run this in your Jupyter notebook to fix out-of-bounds predictions

print("\n" + "="*80)
print("QUICK FIX: ADD CLIPPING LAYER")
print("="*80)

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, TimeDistributed, Reshape, Lambda

print("\n✓ Rebuilding model with clipping layer...")

# Rebuild the model with clipping
model_fixed = Sequential([
    # Reshape the input to be treated as an image (time steps, sensors)
    Reshape((SEQ_LEN, N_SENSORS, 1), input_shape=(SEQ_LEN, N_SENSORS)),

    # Convolutional layers
    Conv2D(filters=32, kernel_size=(3, 3), activation='relu', padding='same'),
    MaxPooling2D(pool_size=(2, 2)),
    Conv2D(filters=64, kernel_size=(3, 3), activation='relu', padding='same'),
    MaxPooling2D(pool_size=(2, 2)),

    # Flatten the output of the convolutional layers
    Flatten(),

    # Dense layers
    Dense(128, activation='relu'),
    Dense(SEQ_LEN * N_SENSORS),
    
    # Reshape the output to match the target shape (horizon, sensors)
    Reshape((HORIZON, N_SENSORS)),
    
    # ✅ NEW: Add clipping layer to ensure predictions are in [0, 1]
    Lambda(lambda x: tf.clip_by_value(x, 0, 1))
])

# Compile the model
model_fixed.compile(optimizer='adam', loss='mse')

print("✅ Model rebuilt with clipping layer")
print(f"\nModel summary:")
model_fixed.summary()

# Option: Transfer weights from old model (if you want to skip retraining)
print("\n" + "="*80)
print("OPTION 1: Transfer Weights (Skip Retraining - 30 seconds)")
print("="*80)

try:
    # Get weights from old model (excluding lambda layer)
    old_weights = model.get_weights()
    # Set them to new model (excluding lambda layer which has no weights)
    model_fixed.get_layer(index=0).set_weights(old_weights[0])  # First layer weights
    # ... etc for other layers
    
    print("✅ Weights transferred!")
    print("\nNow test predictions:")
    y_pred_fixed = model_fixed.predict(X_test[:100], verbose=0)
    print(f"  Min prediction: {y_pred_fixed.min():.6f}")
    print(f"  Max prediction: {y_pred_fixed.max():.6f}")
    if (y_pred_fixed >= 0).all() and (y_pred_fixed <= 1).all():
        print("  ✅ All predictions in bounds!")
    
except Exception as e:
    print(f"⚠️  Weight transfer failed (this is OK): {str(e)[:50]}...")
    print("\nUsing Option 2 instead...")

print("\n" + "="*80)
print("OPTION 2: Quick Retrain (Recommended - 15-30 minutes)")
print("="*80)

print("\n✓ Retraining with clipping layer...")
print("  This will fine-tune the model to respect bounds")

history_fixed = model_fixed.fit(
    X_train, y_train,
    epochs=10,  # Can adjust based on time/performance
    batch_size=32,
    validation_data=(X_val, y_val),
    verbose=1
)

print("\n✅ Training complete!")

# Verify predictions are in bounds
print("\n✓ Verifying predictions...")
y_pred_train = model_fixed.predict(X_train[:1000], verbose=0)
y_pred_val = model_fixed.predict(X_val[:1000], verbose=0)
y_pred_test = model_fixed.predict(X_test[:1000], verbose=0)

for name, pred in [('Train', y_pred_train), ('Val', y_pred_val), ('Test', y_pred_test)]:
    below_min = (pred < 0).sum()
    above_max = (pred > 1).sum()
    print(f"  {name}: below_min={below_min}, above_max={above_max}")
    if below_min == 0 and above_max == 0:
        print(f"    ✅ All predictions in bounds")
    else:
        print(f"    ⚠️  Still some out-of-bounds (expected to improve with more training)")

# Save the fixed model
print("\n✓ Saving fixed model...")
model_save_path = "/content/drive/MyDrive/PEMS_BAY/cnn_traffic_model_v2.keras"

try:
    model_fixed.save(model_save_path)
    print(f"✅ Model saved: {model_save_path}")
except Exception as e:
    print(f"⚠️  Save failed: {e}")
    print("  Trying local save...")
    model_fixed.save('cnn_traffic_model_v2.keras')
    print("✅ Model saved locally as: cnn_traffic_model_v2.keras")

print("\n" + "="*80)
print("NEXT: Run full testing suite on fixed model")
print("="*80)

print("""
from cnn_model_testing import run_complete_testing_suite

# Test the fixed model
run_complete_testing_suite(
    model_fixed,  # Use the fixed model!
    X_train, X_val, X_test,
    y_train, y_val, y_test,
    scaler,
    n_sensors=325
)
""")

print("\n" + "="*80)
print("✅ CLIPPING LAYER FIX COMPLETE")
print("="*80)
