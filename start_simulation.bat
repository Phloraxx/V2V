@echo off
echo ============================================================
echo    V2V Traffic Management System - Simulation Startup
echo ============================================================
echo.
echo Starting Vehicle Simulation...
echo.
echo Configuration:
echo    - 8 V2V-enabled vehicles (smart)
echo    - 8 Non-V2V vehicles (legacy)
echo    - 2 Emergency vehicles
echo.
echo Watch the terminal for real-time events!
echo Press Ctrl+C to stop the simulation
echo ============================================================
echo.

cd /d "%~dp0\vehicles"
python vehicle_simulator.py

pause
