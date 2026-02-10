@echo off
title InvestTracker - Iniciando servicios...
color 0A

echo.
echo ========================================
echo    INVESTTRACKER - INICIO RAPIDO
echo ========================================
echo.

:: Configuracion
set BACKEND_PORT=8000
set FRONTEND_PORT=3000
set BACKEND_SUBDOMAIN=invest-backend-flopez
set PYTHON312="C:\Users\facundo lopez\AppData\Local\Programs\Python\Python312\python.exe"

echo [1/4] Iniciando Backend (FastAPI)...
start "Backend - FastAPI" cmd /k "cd /d E:\maia\acciones\acciones\backend && %PYTHON312% -m uvicorn server:app --reload --port %BACKEND_PORT%"
timeout /t 3 /nobreak >nul

echo [2/4] Iniciando LocalTunnel para Backend...
start "LocalTunnel - Backend" cmd /k "lt --port %BACKEND_PORT% --subdomain %BACKEND_SUBDOMAIN%"
timeout /t 2 /nobreak >nul

echo [3/4] Iniciando Frontend (React)...
start "Frontend - React" cmd /k "cd /d E:\maia\acciones\acciones\frontend && npm start"
timeout /t 2 /nobreak >nul

echo [4/4] Iniciando ngrok para Frontend...
start "ngrok - Frontend" cmd /k "ngrok http %FRONTEND_PORT%"

echo.
echo ========================================
echo    SERVICIOS INICIADOS
echo ========================================
echo.
echo  Backend:     http://localhost:%BACKEND_PORT%
echo  Backend URL: https://%BACKEND_SUBDOMAIN%.loca.lt
echo  Frontend:    http://localhost:%FRONTEND_PORT%
echo  Frontend URL: Ver ventana de ngrok
echo.
echo ========================================
echo.
echo Presiona cualquier tecla para cerrar esta ventana...
echo (Los servicios seguiran corriendo en sus ventanas)
pause >nul
