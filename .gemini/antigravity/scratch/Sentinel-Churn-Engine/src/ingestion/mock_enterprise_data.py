import sqlite3
import numpy as np
import pandas as pd
from faker import Faker
from pathlib import Path
from loguru import logger
import random

# Configuration
DB_PATH = Path("data/raw/telecom.db")
NUM_CUSTOMERS = 1000
RANDOM_SEED = 42

fake = Faker()
Faker.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)

def create_schema(conn):
    """Create the SQLite schema for customers and usage metrics."""
    cursor = conn.cursor()
    
    # Customers Profile Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers_profile (
            id TEXT PRIMARY KEY,
            join_date TEXT,
            location TEXT,
            contract_type TEXT,
            churn INTEGER
        )
    """)
    
    # Usage Metrics Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usage_metrics (
            id TEXT,
            monthly_gb REAL,
            call_duration REAL,
            support_calls INTEGER,
            payment_delay INTEGER,
            monthly_charges REAL,
            total_charges REAL,
            FOREIGN KEY(id) REFERENCES customers_profile(id)
        )
    """)
    conn.commit()
    logger.info("Schema created/verified.")

def generate_data(conn):
    """Generate synthetic data with business logic and quality issues."""
    cursor = conn.cursor()
    
    logger.info(f"Generating data for {NUM_CUSTOMERS} customers...")
    
    customer_data = []
    usage_data = []
    
    for _ in range(NUM_CUSTOMERS):
        # --- Customer Profile ---
        c_id = fake.uuid4()
        join_date = fake.date_between(start_date='-2y', end_date='today')
        location = fake.state()
        contract_type = np.random.choice(['Month-to-Month', 'One Year', 'Two Year'], p=[0.5, 0.3, 0.2])
        
        # Churn Logic (Simple rule-based)
        churn_prob = 0.1
        if contract_type == 'Month-to-Month': churn_prob += 0.2
        # We will adjust prob based on support calls later, but for now let's keep it simple at generation time 
        # or we should generate support calls BEFORE customer profile? 
        # Actually support calls is in usage loop...
        # Let's just randomize generic churn for now to ensure column exists.
        churn = int(np.random.choice([0, 1], p=[0.7, 0.3]))

        customer_data.append((c_id, str(join_date), location, contract_type, churn))
        
        # --- Usage Metrics (Business Logic) ---
        # Base logic:
        # - High support calls correlated with high payment delay (unhappy customers)
        # - High monthly_gb correlated with higher chance of 'Two Year' contract (loyal heavy users) - heuristic
        
        if contract_type == 'Two Year':
            monthly_gb = np.random.normal(loc=50, scale=10) # Heavy users
        else:
            monthly_gb = np.random.normal(loc=15, scale=5)  # Light/Medium users
            
        support_calls = np.random.choice([0, 1, 2, 3, 4, 5], p=[0.5, 0.2, 0.1, 0.1, 0.05, 0.05])
        
        # Correlation: Higher support calls -> Higher probability of payment delay
        if support_calls > 3:
            payment_delay = np.random.choice([0, 5, 15, 30], p=[0.2, 0.3, 0.3, 0.2])
        else:
            payment_delay = np.random.choice([0, 1, 2], p=[0.9, 0.05, 0.05])
            
        call_duration = np.random.exponential(scale=200) # Minutes
        
        monthly_charges = np.random.uniform(50, 150)
        # Approximate tenure (just random int for now since we don't have it explicitly here, but we have join_date)
        # We can approximate total_charges
        approx_tenure = np.random.randint(1, 72) 
        total_charges = monthly_charges * approx_tenure
        
        usage_data.append((c_id, float(monthly_gb), float(call_duration), int(support_calls), int(payment_delay), float(monthly_charges), float(total_charges)))

    # --- Inject Data Quality Issues ---
    logger.info("Injecting data quality issues...")
    
    usage_df = pd.DataFrame(usage_data, columns=['id', 'monthly_gb', 'call_duration', 'support_calls', 'payment_delay', 'monthly_charges', 'total_charges'])
    
    # 1. 5% NULL values in monthly_gb
    mask = np.random.choice([True, False], size=len(usage_df), p=[0.05, 0.95])
    usage_df.loc[mask, 'monthly_gb'] = None
    
    # 2. Negative call_duration (Anomalies) - 1%
    neg_mask = np.random.choice([True, False], size=len(usage_df), p=[0.01, 0.99])
    usage_df.loc[neg_mask, 'call_duration'] = usage_df.loc[neg_mask, 'call_duration'] * -1
    
    # 3. Duplicate Customer IDs (in usage table) - Duplicate 2% of records
    num_dupes = int(NUM_CUSTOMERS * 0.02)
    dupes = usage_df.sample(n=num_dupes, replace=True) # Sample existing to duplicate
    usage_df = pd.concat([usage_df, dupes], ignore_index=True)
    
    # Write to DB
    logger.info("Writing data to database...")
    cursor.executemany("INSERT INTO customers_profile VALUES (?, ?, ?, ?, ?)", customer_data)
    
    # Usage data via pandas to SQL (simpler for handling the dataframe manipulations)
    usage_df.to_sql('usage_metrics', conn, if_exists='append', index=False)
    
    conn.commit()
    logger.success(f"Successfully generated {len(customer_data)} profiles and {len(usage_df)} usage records (including duplicates).")

def main():
    # Ensure directory exists
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # clear old db if exists
    if DB_PATH.exists():
        DB_PATH.unlink()
        
    conn = sqlite3.connect(DB_PATH)
    try:
        create_schema(conn)
        generate_data(conn)
    finally:
        conn.close()

if __name__ == "__main__":
    main()
