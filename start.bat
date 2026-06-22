@echo off
echo ============================================================
echo  Stock Query Server — DSA-CH23-GROUP (Theme C)
echo ============================================================
echo.

echo [1/2] Starting Flask backend on http://localhost:5000
start "Flask Backend" cmd /c "cd /d "%~dp0backend" && python api\server.py"

timeout /t 2 /nobreak > nul

echo [2/2] Starting React frontend on http://localhost:3000
start "React Frontend" cmd /c "cd /d "%~dp0frontend" && npm run dev"

echo.
echo Servers starting in separate windows.
echo   Backend  : http://localhost:5000
echo   Frontend : http://localhost:3000
echo   Health   : http://localhost:5000/api/health
echo   Vanilla  : frontend\vanilla\index.html (open in browser)
echo.
pause
