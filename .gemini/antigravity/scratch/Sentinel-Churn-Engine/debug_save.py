import joblib
import os
from pathlib import Path

path = "src/models/saved/debug_joblib.pkl"
Path(path).parent.mkdir(parents=True, exist_ok=True)

data = {"a": 1}
try:
    joblib.dump(data, path)
    print(f"Saved to {path}")
    print(f"File exists: {Path(path).exists()}")
    print(f"Absolute path: {Path(path).absolute()}")
except Exception as e:
    print(f"Failed: {e}")
