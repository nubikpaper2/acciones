@echo off
title InvestTracker - Solo Local
color 0B

echo.
echo ========================================
echo    INVESTTRACKER - MODO LOCAL
echo ========================================
echo.
echo (Sin tuneles - solo para usar en esta PC)
echo.

set PYTHON312="C:\Users\facundo lopez\AppData\Local\Programs\Python\Python312\python.exe"

echo [1/2] Iniciando Backend...
start "Backend - FastAPI" cmd /k "cd /d E:\maia\acciones\acciones\backend && %PYTHON312% -m uvicorn server:app --reload --port 8000"
timeout /t 3 /nobreak >nul

echo [2/2] Iniciando Frontend...
start "Frontend - React" cmd /k "cd /d E:\maia\acciones\acciones\frontend && npm start"

echo.
echo ========================================
echo    LISTO!
echo ========================================
echo.
echo  Backend:  http://localhost:8000
echo  Frontend: http://localhost:3000
echo.
echo  Abre http://localhost:3000 en tu navegador
echo.
echo ========================================
pause
