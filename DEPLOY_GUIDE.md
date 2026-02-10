# 🚀 Guía de Despliegue - InvestTracker

## Arquitectura de Producción

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│     VERCEL      │────▶│     RAILWAY     │────▶│    SUPABASE     │
│   (Frontend)    │     │    (Backend)    │     │   (Database)    │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
     React App           FastAPI + Scheduler      PostgreSQL
```

---

## 1️⃣ Desplegar Backend en Railway (Gratis)

Railway es perfecto porque mantiene el servidor corriendo 24/7 con el scheduler.

### Pasos:

1. **Crear cuenta en Railway**
   - Ve a https://railway.app
   - Inicia sesión con GitHub

2. **Crear nuevo proyecto**
   - Click en "New Project"
   - Selecciona "Deploy from GitHub repo"
   - Conecta tu repositorio

3. **Configurar el servicio**
   - Railway detectará automáticamente que es Python
   - En la pestaña **Settings**, configura:
     - **Root Directory**: `backend`
     - **Start Command**: `uvicorn server:app --host 0.0.0.0 --port $PORT`

4. **Agregar variables de entorno**
   - Ve a la pestaña **Variables** y agrega:
   ```
   SUPABASE_URL=https://udrwtfgaosdsctmciccc.supabase.co
   SUPABASE_KEY=tu_supabase_key
   JWT_SECRET_KEY=tu_secret_key_seguro_para_produccion
   RESEND_API_KEY=re_2D2fohNK_FyrbeUDjD3FaSMcjdN6NY9ea
   SENDER_EMAIL=onboarding@resend.dev
   ```

5. **Desplegar**
   - Railway desplegará automáticamente
   - Te dará una URL como: `https://tu-app.railway.app`
   - **Guarda esta URL** - la necesitarás para el frontend

---

## 2️⃣ Desplegar Frontend en Vercel (Gratis)

### Pasos:

1. **Crear cuenta en Vercel**
   - Ve a https://vercel.com
   - Inicia sesión con GitHub

2. **Importar proyecto**
   - Click en "Add New" → "Project"
   - Selecciona tu repositorio de GitHub

3. **Configurar el proyecto**
   - **Framework Preset**: Create React App
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `build`

4. **Agregar variable de entorno**
   - En "Environment Variables" agrega:
   ```
   REACT_APP_BACKEND_URL=https://tu-app.railway.app
   ```
   (Usa la URL de Railway del paso anterior)

5. **Desplegar**
   - Click en "Deploy"
   - Vercel te dará una URL como: `https://tu-app.vercel.app`

---

## 3️⃣ Configurar CORS en Backend (Importante!)

Una vez que tengas la URL de Vercel, actualiza el backend para permitir solo tu dominio:

En `backend/server.py`, cambia:
```python
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["https://tu-app.vercel.app"],  # Tu URL de Vercel
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 4️⃣ Subir código a GitHub

Si aún no tienes el código en GitHub:

```bash
# En la carpeta raíz del proyecto
git init
git add .
git commit -m "Initial commit - InvestTracker"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/invest-tracker.git
git push -u origin main
```

---

## ✅ Checklist Final

- [ ] Backend desplegado en Railway
- [ ] Frontend desplegado en Vercel
- [ ] Variable `REACT_APP_BACKEND_URL` configurada en Vercel
- [ ] Variables de entorno configuradas en Railway
- [ ] CORS actualizado con URL de producción
- [ ] Tabla `notifications` creada en Supabase

---

## 🔧 Alternativas

### Si prefieres todo en un solo lugar:

**Render.com** (también gratis):
- Soporta tanto frontend como backend
- Similar a Railway para el backend
- URL: https://render.com

**Fly.io**:
- Más control, más complejo
- Buen tier gratuito
- URL: https://fly.io

---

## 📊 Monitoreo

- **Railway**: Dashboard con logs en tiempo real
- **Vercel**: Analytics y logs de funciones
- **Supabase**: Dashboard con métricas de la base de datos

---

## 💡 Tips

1. **Dominio personalizado**: Ambos servicios permiten conectar tu propio dominio gratis
2. **SSL**: Incluido automáticamente en ambos
3. **Deploys automáticos**: Cada push a GitHub despliega automáticamente
4. **Logs**: Revisa los logs si algo no funciona

---

## 🆘 Troubleshooting

**Error de CORS?**
- Verifica que la URL en `allow_origins` sea exacta (con https://)

**Backend no arranca?**
- Revisa los logs en Railway
- Verifica que las variables de entorno estén configuradas

**Frontend no conecta al backend?**
- Verifica `REACT_APP_BACKEND_URL` en Vercel
- Asegúrate de que no termine en `/`

**Scheduler no funciona?**
- Railway mantiene el servidor activo, debería funcionar
- Revisa los logs para ver los mensajes de "Starting price check"
