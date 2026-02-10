# 🚀 Guía de Arranque Rápido - InvestTracker

## ⚡ Inicio en 5 Minutos

### Opción 1: Arranque con Scripts (Recomendado)

#### Windows (PowerShell)
```powershell
# Clonar y entrar al proyecto
cd acciones

# Instalar y ejecutar todo
.\start.ps1
```

#### Linux/Mac (Bash)
```bash
# Dar permisos y ejecutar
chmod +x start.sh
./start.sh
```

---

### Opción 2: Arranque Manual

#### Paso 1: Backend (Python/FastAPI)

```bash
# Entrar a la carpeta del backend
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Crear archivo .env
cp .env.example .env
# (Editar .env con tus credenciales)

# Ejecutar servidor
uvicorn server:app --reload --port 8000
```

#### Paso 2: Frontend (React)

```bash
# En otra terminal, entrar a frontend
cd frontend

# Instalar dependencias
npm install

# Ejecutar
npm start
```

---

## 🔧 Configuración de Variables de Entorno

### Crear archivo `backend/.env`:

```env
# Base de Datos (elegir una opción)

# Opción A: MongoDB (actual)
MONGO_URL=mongodb://localhost:27017
DB_NAME=investtracker

# Opción B: Supabase (recomendado para producción)
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-anon-key
SUPABASE_SERVICE_KEY=tu-service-key

# JWT (cambiar en producción!)
JWT_SECRET_KEY=tu-clave-secreta-super-segura-cambiar-en-produccion

# Email (opcional - para alertas)
RESEND_API_KEY=re_xxxxxxxxxxxxx
SENDER_EMAIL=alertas@tudominio.com
```

---

## 🌐 URLs de la Aplicación

| Servicio | URL |
|----------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| API Redoc | http://localhost:8000/redoc |

---

## 👤 Cuenta Demo

Para probar sin registrarte:

- **Email**: `demo@inversiones.com`
- **Password**: `demo123`

---

## 📋 Checklist de Arranque

- [ ] Python 3.10+ instalado
- [ ] Node.js 18+ instalado
- [ ] Base de datos configurada (MongoDB o Supabase)
- [ ] Archivo `.env` creado con credenciales
- [ ] Backend ejecutándose en puerto 8000
- [ ] Frontend ejecutándose en puerto 3000

---

## 🆘 Solución de Problemas Comunes

### Error: "MONGO_URL not found"
```bash
# Crear archivo .env en backend/
echo "MONGO_URL=mongodb://localhost:27017" >> backend/.env
echo "DB_NAME=investtracker" >> backend/.env
```

### Error: "Module not found"
```bash
# Backend
cd backend && pip install -r requirements.txt

# Frontend
cd frontend && npm install
```

### Error: Puerto en uso
```bash
# Cambiar puerto del backend
uvicorn server:app --reload --port 8001

# Cambiar puerto del frontend (en package.json o)
set PORT=3001 && npm start  # Windows
PORT=3001 npm start         # Linux/Mac
```

### Error de CORS
Verificar que el backend tenga configurado CORS para `http://localhost:3000`

---

## 📱 Siguiente Paso

Una vez funcionando, revisa:
- [SUPABASE_SETUP.md](./SUPABASE_SETUP.md) - Configurar base de datos en la nube
- [README_INVERSIONES.md](./README_INVERSIONES.md) - Documentación completa
