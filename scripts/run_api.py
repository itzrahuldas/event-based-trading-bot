import sys
import os
import uvicorn

# Ensure src is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    print("Starting Trading Bot API on http://localhost:8000")
    # Reload=True for dev convenience
    uvicorn.run("src.api.server:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()
