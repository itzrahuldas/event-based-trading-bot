import polars as pl
from ydata_profiling import ProfileReport
from pathlib import Path
from loguru import logger
import pandas as pd

# Configuration
INPUT_PATH = "data/processed/cleaned_data.parquet"
REPORT_PATH = "reports/churn_profile.html"

def main():
    logger.info("Starting EDA Profiling...")
    
    # Check if data exists
    if not Path(INPUT_PATH).exists():
        logger.error(f"Data file not found at {INPUT_PATH}. Please run the pipeline first.")
        return

    # Load data
    try:
        # ydata-profiling works best with pandas
        df = pl.read_parquet(INPUT_PATH).to_pandas()
        logger.info(f"Loaded data with shape: {df.shape}")
    except Exception as e:
        logger.error(f"Failed to load data: {e}")
        return

    # Generate Profile
    try:
        logger.info("Generating profile report...")
        profile = ProfileReport(df, title="Churn Data Profiling Report", explorative=True)
        
        # Ensure reports directory exists
        Path(REPORT_PATH).parent.mkdir(parents=True, exist_ok=True)
        
        profile.to_file(REPORT_PATH)
        logger.success(f"Report saved to {REPORT_PATH}")
    except Exception as e:
        logger.error(f"Failed to generate report: {e}")

if __name__ == "__main__":
    main()
