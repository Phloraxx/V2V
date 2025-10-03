@echo off
echo ============================================================
echo    V2V Traffic Management System - Dashboard Startup
echo ============================================================
echo.
echo Starting Dashboard...
echo Dashboard will open in your browser automatically
echo URL: http://localhost:8501
echo.
echo Press Ctrl+C to stop the dashboard
echo ============================================================
echo.

cd /d "%~dp0\dashboard"
streamlit run app.py

pause
