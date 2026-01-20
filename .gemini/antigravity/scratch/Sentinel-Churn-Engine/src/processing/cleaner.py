import polars as pl
import pandas as pd
from loguru import logger

class ChurnDataCleaner:
    """Handles data cleaning operations for churn data."""

    def __init__(self, df: pl.DataFrame):
        """
        Initialize ChurnDataCleaner.

        Args:
            df (pl.DataFrame): Input dataframe.
        """
        self.df = df

    def fix_negative_values(self):
        """Convert negative call_duration to positive."""
        count = self.df.filter(pl.col("call_duration") < 0).height
        if count > 0:
            logger.info(f"Fixing {count} records with negative call_duration.")
            self.df = self.df.with_columns(pl.col("call_duration").abs())
        return self

    def impute_missing(self):
        """Fill NULL monthly_gb with median value."""
        missing_count = self.df.filter(pl.col("monthly_gb").is_null()).height
        if missing_count > 0:
            median_val = self.df.select(pl.col("monthly_gb").median()).item()
            logger.info(f"Imputing {missing_count} missing monthly_gb values with median: {median_val:.2f}")
            self.df = self.df.with_columns(
                pl.col("monthly_gb").fill_null(median_val)
            )
        return self

    def deduplicate(self):
        """Remove duplicate customer ids."""
        initial_rows = self.df.height
        self.df = self.df.unique(subset=["customer_id"])
        dropped = initial_rows - self.df.height
        if dropped > 0:
            logger.info(f"Dropped {dropped} duplicate customer records.")
        return self

    def calculate_tenure(self):
        """Calculate tenure from join_date."""
        # Ensure join_date is date type
        self.df = self.df.with_columns(pl.col("join_date").str.to_date().alias("join_date"))
        # Calculate tenure in months (approx)
        # Using a fixed reference date or current date
        ref_date = pl.lit(pd.Timestamp.now().date())
        
        self.df = self.df.with_columns(
            ((ref_date - pl.col("join_date")).dt.total_days() / 30).cast(pl.Int32).alias("tenure")
        )
        logger.info("Calculated tenure column.")
        return self

    def process(self) -> pl.DataFrame:
        """
        Execute full cleaning pipeline.

        Returns:
            pl.DataFrame: Cleaned data.
        """
        logger.info("Starting data cleaning process...")
        (
            self.fix_negative_values()
            .impute_missing()
            .deduplicate()
            .calculate_tenure()
        )
        logger.info("Data cleaning completed.")
        return self.df
