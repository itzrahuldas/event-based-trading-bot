import pandas as pd
import joblib
from pathlib import Path
from loguru import logger
import numpy as np

class ModelPredictor:
    def __init__(self):
        # Resolve paths relative to this file
        self.base_path = Path(__file__).resolve().parent.parent.parent
        self.models_dir = self.base_path / "src" / "models" / "saved"
        
        self.model_path = self.models_dir / "xgb_model.pkl"
        self.preprocessor_path = self.models_dir / "preprocessor.pkl"
        
        self.model = None
        self.preprocessor = None
        
        self._load_artifacts()
        
    def _load_artifacts(self):
        """Load model and preprocessor pickles."""
        try:
            if not self.model_path.exists():
                raise FileNotFoundError(f"Model not found at {self.model_path}")
            if not self.preprocessor_path.exists():
                raise FileNotFoundError(f"Preprocessor not found at {self.preprocessor_path}")
                
            self.model = joblib.load(self.model_path)
            self.preprocessor = joblib.load(self.preprocessor_path)
            logger.info("Model and preprocessor loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load artifacts: {e}")
            raise

    def predict_single(self, data_dict):
        """
        Predict churn probability for a single customer.
        
        Args:
            data_dict (dict): Dictionary containing feature values.
            
        Returns:
            tuple: (probability_of_churn, predicted_class)
        """
        # Default values for features not provided in the UI
        # Ideally, these should be medians/modes from training data
        defaults = {
            'location': 'New York', 
            'gender': 'Male',
            'monthly_gb': 15.0,
            'call_duration': 150.0,
            'support_calls': 1,
            'payment_delay': 0,
            'monthly_charges': 50.0,
            'total_charges': 500.0,
            'tenure': 12,
            'contract_type': 'Month-to-Month'
        }
        
        # Merge input with defaults (input overrides defaults)
        complete_data = defaults.copy()
        complete_data.update(data_dict)
        
        # Create DataFrame
        df = pd.DataFrame([complete_data])
        
        try:
            # Preprocess
            X_processed = self.preprocessor.transform(df)
            
            # Predict
            prob = self.model.predict_proba(X_processed)[0][1]
            pred_class = self.model.predict(X_processed)[0]
            
            return prob, int(pred_class)
        except Exception as e:
            logger.error(f"Prediction logic failed: {e}")
            raise

    def get_feature_importance(self):
        """
        Get feature importance from the model.
        
        Returns:
            pd.DataFrame: DataFrame with 'Feature' and 'Importance' columns.
        """
        try:
            # Get feature importance
            importances = self.model.feature_importances_
            
            # Try to get feature names
            try:
                feature_names = self.preprocessor.get_feature_names_out()
            except:
                feature_names = [f"Feature {i}" for i in range(len(importances))]
                
            df_imp = pd.DataFrame({
                'Feature': feature_names,
                'Importance': importances
            }).sort_values(by='Importance', ascending=False)
            
            return df_imp
        except Exception as e:
            logger.error(f"Could not retrieve feature importance: {e}")
            return pd.DataFrame()
