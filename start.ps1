# =============================================
# Script de Arranque Rápido - InvestTracker
# Para Windows (PowerShell)
# =============================================

Write-Host "🚀 Iniciando InvestTracker..." -ForegroundColor Cyan
Write-Host ""

# Verificar Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ $pythonVersion encontrado" -ForegroundColor Green
} catch {
    Write-Host "❌ Python no está instalado. Por favor instálalo primero." -ForegroundColor Red
    Write-Host "   Descarga: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Verificar Node
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✓ Node.js $nodeVersion encontrado" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js no está instalado. Por favor instálalo primero." -ForegroundColor Red
    Write-Host "   Descarga: https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# =============================================
# BACKEND
# =============================================
Write-Host "📦 Configurando Backend..." -ForegroundColor Yellow
Set-Location backend

# Crear entorno virtual si no existe
if (!(Test-Path "venv")) {
    Write-Host "Creando entorno virtual..."
    python -m venv venv
}

# Activar entorno virtual
& .\venv\Scripts\Activate.ps1

# Instalar dependencias
Write-Host "Instalando dependencias de Python..."
pip install -r requirements.txt -q

# Crear .env si no existe
if (!(Test-Path ".env")) {
    Write-Host "Creando archivo .env desde template..."
    Copy-Item ".env.example" ".env"
    Write-Host "⚠️  Recuerda editar backend\.env con tus credenciales" -ForegroundColor Yellow
}

# Iniciar backend en nueva ventana
Write-Host "Iniciando servidor backend..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\venv\Scripts\Activate.ps1; uvicorn server:app --reload --host 0.0.0.0 --port 8000"
Write-Host "✓ Backend iniciado en nueva ventana" -ForegroundColor Green

Set-Location ..

# =============================================
# FRONTEND
# =============================================
Write-Host ""
Write-Host "📦 Configurando Frontend..." -ForegroundColor Yellow
Set-Location frontend

# Instalar dependencias si no existen
if (!(Test-Path "node_modules")) {
    Write-Host "Instalando dependencias de Node.js..."
    npm install
}

# Iniciar frontend en nueva ventana
Write-Host "Iniciando servidor frontend..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; npm start"
Write-Host "✓ Frontend iniciado en nueva ventana" -ForegroundColor Green

Set-Location ..

# =============================================
# RESUMEN
# =============================================
Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "🎉 ¡InvestTracker está corriendo!" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📱 Frontend:  " -NoNewline; Write-Host "http://localhost:3000" -ForegroundColor Blue
Write-Host "🔧 Backend:   " -NoNewline; Write-Host "http://localhost:8000" -ForegroundColor Blue
Write-Host "📚 API Docs:  " -NoNewline; Write-Host "http://localhost:8000/docs" -ForegroundColor Blue
Write-Host ""
Write-Host "👤 Cuenta Demo:" -ForegroundColor Yellow
Write-Host "   Email:    demo@inversiones.com"
Write-Host "   Password: demo123"
Write-Host ""
Write-Host "Esperando a que los servidores inicien..." -ForegroundColor Gray
Start-Sleep -Seconds 5

# Abrir navegador
Write-Host "Abriendo navegador..." -ForegroundColor Gray
Start-Process "http://localhost:3000"

Write-Host ""
Write-Host "✅ ¡Listo! El navegador debería abrirse automáticamente." -ForegroundColor Green
Write-Host "   Si no, ve a http://localhost:3000" -ForegroundColor Gray
