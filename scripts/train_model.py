import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import pickle
from datetime import datetime

from src.database import get_db
from src.ml.feature_store import FeatureStore
from src.data.symbols import get_universe, Universe

def train():
    print("Initializing Feature Store...")
    db = next(get_db())
    store = FeatureStore(db)
    
    # Train on NIFTY_NEXT50
    tickers = get_universe(Universe.NIFTY_NEXT50)
    print(f"Loading data for {len(tickers)} tickers...")
    
    df = store.get_training_set(tickers, days=90) # 90 days history
    
    if df.empty:
        print("❌ No data found! Run fetch_90d.py first.")
        return

    # Define Features
    feature_cols = ['RSI', 'rsi_norm', 'volatility_5', 'dist_ema50', 'return_1', 'return_5']
    target_col = 'target_class'
    
    X = df[feature_cols]
    y = df[target_col]
    
    print(f"Dataset shape: {X.shape}")
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
    # Shuffle=False is debatable for time-series, but safer to respect time order if we split by time.
    # Actually, random split is okay for "general" classification if features are stationary.
    # For this prototype, random split (shuffle=True default) is often used for "state detection".
    # Let's use shuffle=False to simulate "future" test.
    
    # Train
    print("Training RandomForest...")
    clf = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
    clf.fit(X_train, y_train)
    
    # Eval
    probs = clf.predict_proba(X_test)[:, 1]
    preds = (probs > 0.55).astype(int) # Higher threshold for precision?
    
    acc = accuracy_score(y_test, preds)
    print(f"\nModel Accuracy: {acc:.2f}")
    print(classification_report(y_test, preds))
    
    # Save
    model_dir = "models"
    os.makedirs(model_dir, exist_ok=True)
    model_path = f"{model_dir}/signal_classifier.pkl"
    
    with open(model_path, "wb") as f:
        pickle.dump(clf, f)
        
    print(f"✅ Model saved to {model_path}")

if __name__ == "__main__":
    train()
