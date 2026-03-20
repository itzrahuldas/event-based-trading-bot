import schedule
import time
import subprocess
import sys
import datetime
import os

# Configuration
REPORT_TIME = "15:30"  # Market Close Time
SCRIPT_TO_RUN = "scripts/send_daily_report.py"

def run_daily_report():
    """Executes the daily report script as a subprocess."""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] ⏰ Triggering End-of-Day Report...")
    
    # Check if script exists
    if not os.path.exists(SCRIPT_TO_RUN):
        print(f"[{now}] ❌ Error: '{SCRIPT_TO_RUN}' not found.")
        return

    try:
        # Run the reporting script using the same python interpreter
        result = subprocess.run([sys.executable, SCRIPT_TO_RUN], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"[{now}] ✅ Report Sent Successfully.")
            print(f"Output: {result.stdout}")
        else:
            print(f"[{now}] ⚠️ Report Script Failed.")
            print(f"Error: {result.stderr}")
            
    except Exception as e:
        print(f"[{now}] ❌ Exception while running report: {e}")

# --- SCHEDULING ---
print(f"🚀 Auto-Reporter Scheduler Started. Waiting for {REPORT_TIME} IST...")
schedule.every().day.at(REPORT_TIME).do(run_daily_report)

# Infinite Loop
if __name__ == "__main__":
    try:
        while True:
            schedule.run_pending()
            time.sleep(30) # Check every 30 seconds
    except KeyboardInterrupt:
        print("\n🛑 Scheduler Stopped by User.")
