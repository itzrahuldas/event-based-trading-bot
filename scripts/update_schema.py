import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import engine, Base, Report

def update_schema():
    print("Updating schema (creating missing tables)...")
    Base.metadata.create_all(engine)
    print("Done.")

if __name__ == "__main__":
    update_schema()
