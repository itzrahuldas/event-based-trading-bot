import sqlite3
import polars as pl
from pathlib import Path
from loguru import logger

class DataLoader:
    """Handles data loading from SQLite database."""
    
    def __init__(self, db_path: str, sql_path: str):
        """
        Initialize DataLoader.

        Args:
            db_path (str): Path to the SQLite database.
            sql_path (str): Path to the SQL query file.
        """
        self.db_path = db_path
        self.sql_path = sql_path

    def load_data(self) -> pl.DataFrame:
        """
        Execute SQL query and return data as Polars DataFrame.

        Returns:
            pl.DataFrame: The loaded data.
        
        Raises:
            FileNotFoundError: If DB or SQL file is missing.
        """
        if not Path(self.db_path).exists():
            raise FileNotFoundError(f"Database not found at {self.db_path}")
        
        if not Path(self.sql_path).exists():
            raise FileNotFoundError(f"SQL file not found at {self.sql_path}")

        logger.info(f"Loading data from {self.db_path} using query {self.sql_path}...")
        
        with open(self.sql_path, "r") as f:
            query = f.read()

        conn = sqlite3.connect(self.db_path)
        try:
            df = pl.read_database(query, conn)
            logger.info(f"Successfully loaded {df.height} rows. Columns: {df.columns}")
            return df
        finally:
            conn.close()
