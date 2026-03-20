import pickle
import os
import pandas as pd
import numpy as np
from src.utils.logger import get_logger

logger = get_logger(__name__)

class Predictor:
    def __init__(self, model_path: str = "models/signal_classifier.pkl"):
        self.model = None
        self.feature_cols = ['RSI', 'rsi_norm', 'volatility_5', 'dist_ema50', 'return_1', 'return_5']
        
        if os.path.exists(model_path):
            try:
                with open(model_path, "rb") as f:
                    self.model = pickle.load(f)
                logger.info("ml_model_loaded", path=model_path)
            except Exception as e:
                logger.error("ml_load_error", error=str(e))
        else:
            logger.warning("ml_model_missing", path=model_path)

    def predict_confidence(self, features_df: pd.DataFrame) -> float:
        """
        Returns confidence (probability of UP class).
        """
        if not self.model: return 0.5 # Neutral if no model
        
        try:
            # Ensure columns exist and order matches
            X = features_df[self.feature_cols].copy()
            # Handle single row (reshape) if needed, but DF handles it.
            
            # Predict
            probs = self.model.predict_proba(X)
            # Class 1 is UP
            confidence = probs[0][1] # Assuming single row input
            return confidence
        except Exception as e:
            logger.error("prediction_error", error=str(e))
            return 0.5
