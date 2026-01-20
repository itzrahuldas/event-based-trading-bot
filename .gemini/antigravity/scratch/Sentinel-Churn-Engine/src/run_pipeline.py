from pathlib import Path
from loguru import logger
from src.ingestion.loader import DataLoader
from src.processing.cleaner import ChurnDataCleaner

# Configuration
DB_PATH = "data/raw/telecom.db"
SQL_PATH = "src/ingestion/sql/extract_churn_data.sql"
OUTPUT_PATH = "data/processed/cleaned_data.parquet"

def main():
    logger.info("Starting ETL Pipeline...")

    # 1. Extraction
    try:
        loader = DataLoader(db_path=DB_PATH, sql_path=SQL_PATH)
        df = loader.load_data()
        logger.info(f"Loaded columns: {df.columns}")
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        return

    # 2. Transformation (Cleaning)
    try:
        cleaner = ChurnDataCleaner(df)
        cleaned_df = cleaner.process()
        logger.info(f"Cleaned columns: {cleaned_df.columns}")
    except Exception as e:
        logger.error(f"Cleaning failed: {e}")
        return

    # 3. Load (Save)
    try:
        output_file = Path(OUTPUT_PATH)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        cleaned_df.write_parquet(output_file)
        logger.success(f"Pipeline finished. Data saved to {OUTPUT_PATH}")
        logger.info(f"Final shape: {cleaned_df.shape}")
    except Exception as e:
        logger.error(f"Saving data failed: {e}")

if __name__ == "__main__":
    main()
