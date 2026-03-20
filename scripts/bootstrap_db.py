import sys
import os

# Ensure src is in path
sys.path.append(os.getcwd())

from src.database import init_db

if __name__ == "__main__":
    print("Initializing Database...")
    try:
        if os.path.exists("trading_bot.db"):
            print("Deleting existing DB (Dev Policy)...")
            os.remove("trading_bot.db")
            
        init_db()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error: {e}")
