@echo off
echo ============================================================
echo    V2V Traffic Management System - Quick Start
echo ============================================================
echo.
echo This will install all required dependencies...
echo.
pause

echo Installing Python packages...
pip install -r requirements.txt

echo.
echo ============================================================
echo Installation complete!
echo.
echo To run the system, you need 3 terminals:
echo.
echo Terminal 1: cd backend\mother_server ^&^& python app.py
echo Terminal 2: cd dashboard ^&^& streamlit run app.py
echo Terminal 3: cd vehicles ^&^& python vehicle_simulator.py
echo.
echo ============================================================
pause
