@echo off
TITLE CHRONOS 24/7 Background Service Launcher
COLOR 0A
cls

echo ============================================================
echo  CHRONOS 24/7 BACKGROUND SERVICE LAUNCHER
echo  Profile Mode: Active Profile Loaded from config.py
echo ============================================================
echo.

:: Navigate to script directory
cd /d "%~dp0"

:: Check for virtual environment
if not exist ".venv\Scripts\python.exe" (
  echo [ERROR] Python virtual environment not found in .venv
  echo Please run setup or install dependencies before starting service.
  pause
  exit /b 1
)

echo [SERVICE]: Starting CHRONOS Server in 24/7 Auto-Restart Loop...
echo [SERVICE]: Press Ctrl+C in this console to stop the service.
echo.

:: Open browser automatically after 3 seconds in background thread
start /min cmd /c "timeout /t 3 /nobreak > nul && start http://localhost:5000"

:SERVICE_LOOP
echo [%date% %time%] [SERVICE]: Starting server process...
.venv\Scripts\python.exe server.py

echo.
echo [WARNING]: CHRONOS server stopped or crashed at %time%.
echo [SERVICE]: Automatically restarting in 5 seconds...
timeout /t 5 /nobreak > nul
goto SERVICE_LOOP
