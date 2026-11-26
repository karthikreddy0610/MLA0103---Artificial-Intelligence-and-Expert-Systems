import sys
import webbrowser
import threading
import time
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import uvicorn

def open_browser():
    time.sleep(1.2)
    url = "http://localhost:8000"
    print(f"\n[CityBrain] Opening application in default web browser: {url}\n")
    webbrowser.open(url)

if __name__ == "__main__":
    print("=" * 60)
    print("  Starting CityBrain Backend & Web Portal (FastAPI)")
    print("  Server Address: http://localhost:8000")
    print("  API Docs:       http://localhost:8000/docs")
    print("=" * 60)

    # Launch browser thread
    threading.Thread(target=open_browser, daemon=True).start()

    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)

