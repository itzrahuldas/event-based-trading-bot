
import sys
import os

# Add src to path
sys.path.append(os.getcwd())

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database import Base, Trade
from src.constants import Mode

def debug_mode_validation():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        print("Testing Valid Mode...")
        t1 = Trade(timestamp=datetime.now(), ticker="A", side="B", quantity=1, price=1, mode="LIVE")
        session.add(t1)
        session.commit()
        print(f"Valid Mode: {t1.mode}")
        
        print("Testing Lowercase Mode...")
        t2 = Trade(timestamp=datetime.now(), ticker="B", side="B", quantity=1, price=1, mode="live")
        session.add(t2)
        session.commit()
        print(f"Lowercase Mode: {t2.mode}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        
from datetime import datetime
debug_mode_validation()
