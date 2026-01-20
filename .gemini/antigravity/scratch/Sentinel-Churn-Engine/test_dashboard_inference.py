from src.dashboard.inference import ModelPredictor
import pandas as pd

def test_inference():
    print("Initializing Predictor...")
    try:
        predictor = ModelPredictor()
        print("Model loaded.")
    except Exception as e:
        print(f"Failed to load model: {e}")
        return

    # Test single prediction
    sample_input = {
        "tenure": 24,
        "monthly_charges": 70.0,
        "total_charges": 1500.0,
        "contract_type": "One Year"
    }
    
    print(f"Testing prediction with: {sample_input}")
    try:
        prob, pred_class = predictor.predict_single(sample_input)
        print(f"Prediction: Class={pred_class}, Prob={prob:.4f}")
    except Exception as e:
        print(f"Prediction failed: {e}")

    # Test feature importance
    print("Getting feature importance...")
    imp = predictor.get_feature_importance()
    print(imp.head())

if __name__ == "__main__":
    test_inference()
