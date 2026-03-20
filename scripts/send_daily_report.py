import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from src.ops.reporter import DailyReporter

def main():
    reporter = DailyReporter()
    today = datetime.now().date()
    
    # Generate
    metrics = reporter.generate_report(today, mode="LIVE")
    
    # Save
    reporter.save_report(metrics, mode="LIVE")
    
    # Send
    reporter.send_report(metrics)

if __name__ == "__main__":
    main()
