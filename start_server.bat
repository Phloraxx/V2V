@echo off
echo ============================================================
echo    V2V Traffic Management System - Server Startup
echo ============================================================
echo.
echo Starting Mother Server...
echo Server will run on http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

cd /d "%~dp0\backend\mother_server"
python app.py

pause
