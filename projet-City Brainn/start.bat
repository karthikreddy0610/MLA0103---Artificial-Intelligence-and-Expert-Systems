@echo off
cd /d "%~dp0"
title CityBrain Fullstack Portal Launcher
echo ========================================================
echo   Starting CityBrain Fullstack Portal (Backend + Frontend)
echo ========================================================
echo.
echo Installing dependencies (fastapi, uvicorn)...
pip install -r backend\requirements.txt
echo.
echo Starting FastAPI server on http://localhost:8000 ...
python run.py
if errorlevel 1 (
    echo.
    echo If python is not recognized, try running:
    echo py -m uvicorn backend.app.main:app --port 8000 --reload
    pause
)
pause

