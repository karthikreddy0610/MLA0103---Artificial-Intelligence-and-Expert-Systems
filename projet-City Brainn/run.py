import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from backend.run import open_browser
import uvicorn
import threading

if __name__ == "__main__":
    print("\n=======================================================")
    print("   CityBrain Smart Urban Grievance Tracking Portal")
    print("   Connected Backend: FastAPI (http://localhost:8000)")
    print("   Connected Frontend: Modern Light UI (Web Dashboard)")
    print("=======================================================\n")

    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)

