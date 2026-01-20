import polars as pl
import sqlite3
from loguru import logger

def verify():
    # 1. Check Raw Data
    conn = sqlite3.connect("data/raw/telecom.db")
    raw_df = pl.read_database("SELECT * FROM usage_metrics", conn)
    conn.close()
    
    logger.info(f"Raw Usage Data: {raw_df.height} rows")
    
    neg_raw = raw_df.filter(pl.col("call_duration") < 0).height
    null_raw = raw_df.filter(pl.col("monthly_gb").is_null()).height
    
    logger.info(f"Raw Negative Call Duration: {neg_raw}")
    logger.info(f"Raw Missing Monthly GB: {null_raw}")

    # 2. Check Processed Data
    try:
        clean_df = pl.read_parquet("data/processed/cleaned_data.parquet")
    except Exception as e:
        logger.error(f"Could not read processed data: {e}")
        return

    logger.info(f"Processed Data: {clean_df.height} rows")
    
    neg_clean = clean_df.filter(pl.col("call_duration") < 0).height
    null_clean = clean_df.filter(pl.col("monthly_gb").is_null()).height
    
    # Verify fixes
    if neg_clean == 0:
        logger.success("VERIFIED: No negative call_duration in processed data.")
    else:
        logger.error(f"FAILED: Found {neg_clean} negative call_duration records.")

    if null_clean == 0:
        logger.success("VERIFIED: No missing monthly_gb in processed data.")
    else:
        logger.error(f"FAILED: Found {null_clean} missing monthly_gb records.")
        
    logger.info("Verifying duplicates...")
    if clean_df.height == clean_df.unique(subset=["customer_id"]).height:
        logger.success("VERIFIED: No duplicate customer_ids.")
    else:
        logger.error("FAILED: Duplicates found.")

if __name__ == "__main__":
    verify()
