@echo off
title InvestTracker - Cerrando servicios...
color 0C

echo.
echo ========================================
echo    CERRANDO TODOS LOS SERVICIOS
echo ========================================
echo.

echo Cerrando procesos...
taskkill /FI "WINDOWTITLE eq Backend*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Frontend*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq LocalTunnel*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq ngrok*" /F >nul 2>&1
taskkill /IM "ngrok.exe" /F >nul 2>&1
taskkill /IM "node.exe" /F >nul 2>&1

echo.
echo Todos los servicios han sido cerrados.
echo.
pause
