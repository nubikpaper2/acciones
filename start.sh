#!/bin/bash
# =============================================
# Script de Arranque Rápido - InvestTracker
# Para Linux/Mac
# =============================================

set -e  # Salir si hay errores

echo "🚀 Iniciando InvestTracker..."
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # Sin color

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no está instalado. Por favor instálalo primero."
    exit 1
fi

# Verificar Node
if ! command -v node &> /dev/null; then
    echo "❌ Node.js no está instalado. Por favor instálalo primero."
    exit 1
fi

echo -e "${GREEN}✓ Python3 encontrado${NC}"
echo -e "${GREEN}✓ Node.js encontrado${NC}"
echo ""

# =============================================
# BACKEND
# =============================================
echo -e "${YELLOW}📦 Configurando Backend...${NC}"
cd backend

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "Creando entorno virtual..."
    python3 -m venv venv
fi

# Activar entorno virtual
source venv/bin/activate

# Instalar dependencias
echo "Instalando dependencias de Python..."
pip install -r requirements.txt -q

# Crear .env si no existe
if [ ! -f ".env" ]; then
    echo "Creando archivo .env desde template..."
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Recuerda editar backend/.env con tus credenciales${NC}"
fi

# Iniciar backend en segundo plano
echo "Iniciando servidor backend..."
uvicorn server:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo -e "${GREEN}✓ Backend iniciado (PID: $BACKEND_PID)${NC}"

cd ..

# =============================================
# FRONTEND
# =============================================
echo ""
echo -e "${YELLOW}📦 Configurando Frontend...${NC}"
cd frontend

# Instalar dependencias si no existen
if [ ! -d "node_modules" ]; then
    echo "Instalando dependencias de Node.js..."
    npm install
fi

# Iniciar frontend
echo "Iniciando servidor frontend..."
npm start &
FRONTEND_PID=$!
echo -e "${GREEN}✓ Frontend iniciado (PID: $FRONTEND_PID)${NC}"

cd ..

# =============================================
# RESUMEN
# =============================================
echo ""
echo "============================================="
echo -e "${GREEN}🎉 ¡InvestTracker está corriendo!${NC}"
echo "============================================="
echo ""
echo "📱 Frontend:  http://localhost:3000"
echo "🔧 Backend:   http://localhost:8000"
echo "📚 API Docs:  http://localhost:8000/docs"
echo ""
echo "👤 Cuenta Demo:"
echo "   Email:    demo@inversiones.com"
echo "   Password: demo123"
echo ""
echo "Para detener: Ctrl+C o mata los procesos:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo ""

# Esperar a que terminen los procesos
wait
