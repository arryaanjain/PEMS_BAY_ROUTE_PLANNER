# ML Model Loader for CNN Traffic Prediction Model
import os
import pickle
import numpy as np
from pathlib import Path
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class CNNTrafficModel:
    """
    Wrapper for the trained CNN traffic prediction model
    
    Model Details:
    - Input: (batch, 12, 325) - 12 time steps × 325 sensors
    - Output: (batch, 12, 325) - Predicted next 12 time steps
    - Time resolution: 5 minutes per step (12 steps = 1 hour)
    - Data: Normalized speeds [0, 1]
    """
    
    def __init__(self, model_path: str, scaler_path: str, adj_matrix_path: str):
        """
        Initialize the traffic prediction model
        
        Args:
            model_path: Path to .keras model file
            scaler_path: Path to scaler.pkl file
            adj_matrix_path: Path to adj_mx_bay.pkl file
        """
        self.model = None
        self.scaler = None
        self.sensor_ids = None
        self.sensor_id_to_ind = None
        self.adj_matrix = None
        self.n_sensors = 325
        self.seq_len = 12  # Input sequence length
        self.horizon = 12  # Prediction horizon
        
        # Load model lazily (only when needed)
        self.model_path = model_path
        self.scaler_path = scaler_path
        self.adj_matrix_path = adj_matrix_path
        
    def _load_model(self):
        """Load the TensorFlow model"""
        if self.model is None:
            try:
                import tensorflow as tf
                self.model = tf.keras.models.load_model(self.model_path)
                logger.info(f"✅ Loaded CNN model from {self.model_path}")
            except Exception as e:
                logger.error(f"❌ Failed to load model: {e}")
                raise
    
    def _load_scaler(self):
        """Load the MinMaxScaler for denormalization"""
        if self.scaler is None:
            try:
                with open(self.scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
                logger.info(f"✅ Loaded scaler from {self.scaler_path}")
            except Exception as e:
                logger.error(f"❌ Failed to load scaler: {e}")
                raise
    
    def _load_adjacency_matrix(self):
        """Load sensor adjacency matrix and sensor IDs"""
        if self.adj_matrix is None:
            try:
                with open(self.adj_matrix_path, 'rb') as f:
                    adj_data = pickle.load(f, encoding='latin1')
                
                self.sensor_ids = adj_data[0]  # List of sensor IDs
                self.sensor_id_to_ind = adj_data[1]  # Dict: sensor_id -> index
                self.adj_matrix = adj_data[2]  # Adjacency matrix
                
                logger.info(f"✅ Loaded {len(self.sensor_ids)} sensor IDs")
            except Exception as e:
                logger.error(f"❌ Failed to load adjacency matrix: {e}")
                raise
    
    def initialize(self):
        """Load all components"""
        self._load_model()
        self._load_scaler()
        self._load_adjacency_matrix()
    
    def normalize_speeds(self, speeds: np.ndarray) -> np.ndarray:
        """
        Normalize speed data using the fitted scaler
        
        Args:
            speeds: Array of shape (timesteps, n_sensors) with speed values
        
        Returns:
            Normalized array in [0, 1] range
        """
        if self.scaler is None:
            self._load_scaler()
        
        return self.scaler.transform(speeds)
    
    def denormalize_speeds(self, normalized_speeds: np.ndarray) -> np.ndarray:
        """
        Denormalize predictions back to actual speed values (mph)
        
        Args:
            normalized_speeds: Array in [0, 1] range
        
        Returns:
            Speed values in mph
        """
        if self.scaler is None:
            self._load_scaler()
        
        # Reshape if needed
        original_shape = normalized_speeds.shape
        if len(original_shape) > 2:
            # Flatten to (n_samples, n_features)
            normalized_reshaped = normalized_speeds.reshape(-1, self.n_sensors)
            denormalized = self.scaler.inverse_transform(normalized_reshaped)
            return denormalized.reshape(original_shape)
        else:
            return self.scaler.inverse_transform(normalized_speeds)
    
    def predict(self, input_sequence: np.ndarray, denormalize: bool = True) -> np.ndarray:
        """
        Predict future traffic speeds
        
        Args:
            input_sequence: Shape (batch, 12, 325) or (12, 325)
                           Last 12 time steps of normalized speed data
            denormalize: Whether to return denormalized values (mph)
        
        Returns:
            Predictions of shape (batch, 12, 325) or (12, 325)
            Next 12 time steps of speed predictions
        """
        if self.model is None:
            self._load_model()
        
        # Add batch dimension if needed
        single_sample = False
        if len(input_sequence.shape) == 2:
            input_sequence = np.expand_dims(input_sequence, axis=0)
            single_sample = True
        
        # Validate shape
        expected_shape = (input_sequence.shape[0], self.seq_len, self.n_sensors)
        if input_sequence.shape != expected_shape:
            raise ValueError(
                f"Expected input shape {expected_shape}, got {input_sequence.shape}"
            )
        
        # Predict
        predictions = self.model.predict(input_sequence, verbose=0)
        
        # Denormalize if requested
        if denormalize:
            predictions = self.denormalize_speeds(predictions)
        
        # Remove batch dimension if input was single sample
        if single_sample:
            predictions = predictions[0]
        
        return predictions
    
    def get_sensor_index(self, sensor_id: int) -> Optional[int]:
        """Get array index for a sensor ID"""
        if self.sensor_id_to_ind is None:
            self._load_adjacency_matrix()
        
        return self.sensor_id_to_ind.get(sensor_id)
    
    def get_sensor_id(self, index: int) -> Optional[int]:
        """Get sensor ID from array index"""
        if self.sensor_ids is None:
            self._load_adjacency_matrix()
        
        if 0 <= index < len(self.sensor_ids):
            return self.sensor_ids[index]
        return None


# Global model instance (singleton)
_model_instance: Optional[CNNTrafficModel] = None


def get_traffic_model() -> CNNTrafficModel:
    """
    Get or create the global traffic model instance
    
    Returns:
        Initialized CNNTrafficModel
    """
    global _model_instance
    
    if _model_instance is None:
        # Define paths (adjust based on your setup)
        base_dir = Path(__file__).resolve().parents[2]
        ml_dir = base_dir / "ml_models"
        
        model_path = ml_dir / "cnn_traffic_model.keras"
        scaler_path = ml_dir / "scaler.pkl"
        adj_matrix_path = ml_dir / "adj_mx_bay.pkl"
        
        # Check if files exist
        if not model_path.exists():
            raise FileNotFoundError(
                f"Model file not found: {model_path}\n"
                f"Please place your cnn_traffic_model.keras in {ml_dir}"
            )
        
        if not scaler_path.exists():
            raise FileNotFoundError(
                f"Scaler file not found: {scaler_path}\n"
                f"Please place your scaler.pkl in {ml_dir}"
            )
        
        if not adj_matrix_path.exists():
            raise FileNotFoundError(
                f"Adjacency matrix not found: {adj_matrix_path}\n"
                f"Please place your adj_mx_bay.pkl in {ml_dir}"
            )
        
        _model_instance = CNNTrafficModel(
            model_path=str(model_path),
            scaler_path=str(scaler_path),
            adj_matrix_path=str(adj_matrix_path)
        )
        
        # Initialize on first use
        _model_instance.initialize()
        logger.info("🚀 Traffic prediction model initialized")
    
    return _model_instance
