import polars as pl
from pathlib import Path
import os

path = "data/processed/debug.parquet"
Path(path).parent.mkdir(parents=True, exist_ok=True)

df = pl.DataFrame({"a": [1, 2, 3]})
try:
    df.write_parquet(path)
    print(f"Successfully wrote to {path}")
    print(f"File exists: {Path(path).exists()}")
    print(f"Absolute path: {Path(path).absolute()}")
except Exception as e:
    print(f"Failed: {e}")
