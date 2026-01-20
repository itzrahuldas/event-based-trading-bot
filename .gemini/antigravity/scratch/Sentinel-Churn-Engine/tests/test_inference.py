import pytest
import pandas as pd
from src.dashboard.inference import ModelPredictor

@pytest.fixture(scope="module")
def predictor():
    """Fixture to load the model predictor once for testing."""
    return ModelPredictor()

def test_model_loading(predictor):
    """Test that model and preprocessor are loaded correctly."""
    assert predictor.model is not None
    assert predictor.preprocessor is not None

def test_predict_single(predictor):
    """Test prediction for a single customer."""
    sample_input = {
        "tenure": 24,
        "monthly_charges": 70.0,
        "total_charges": 1500.0,
        "contract_type": "One Year",
        "internet_service": "Fiber Optic"
    }
    
    prob, pred_class = predictor.predict_single(sample_input)
    
    # Check types (allow numpy types)
    import numpy as np
    assert isinstance(prob, (float, np.floating))
    assert isinstance(pred_class, (int, np.integer))
    
    # Check ranges
    assert 0.0 <= prob <= 1.0
    assert pred_class in [0, 1]

def test_feature_importance(predictor):
    """Test feature importance retrieval."""
    importance_df = predictor.get_feature_importance()
    
    assert not importance_df.empty
    assert "Feature" in importance_df.columns
    assert "Importance" in importance_df.columns
    assert len(importance_df) > 0
