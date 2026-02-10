# 🗄️ Configuración de Supabase para InvestTracker

## 📖 ¿Qué es Supabase?

Supabase es una alternativa open-source a Firebase que provee:
- ✅ Base de datos PostgreSQL
- ✅ Autenticación integrada
- ✅ API REST automática
- ✅ Realtime subscriptions
- ✅ Storage para archivos
- ✅ Plan gratuito generoso

---

## 🚀 Paso 1: Crear Cuenta y Proyecto

### 1.1 Crear cuenta en Supabase
1. Ve a [https://supabase.com](https://supabase.com)
2. Click en **Start your project**
3. Inicia sesión con GitHub o email

### 1.2 Crear nuevo proyecto
1. Click en **New Project**
2. Selecciona tu organización
3. Configura:
   - **Name**: `investtracker`
   - **Database Password**: (guarda esta contraseña!)
   - **Region**: Elige la más cercana (ej: `South America (São Paulo)`)
4. Click en **Create new project**
5. Espera 2-3 minutos mientras se crea

---

## 🗃️ Paso 2: Crear las Tablas

### 2.1 Ir al SQL Editor
1. En el menú lateral, click en **SQL Editor**
2. Click en **New query**

### 2.2 Ejecutar el Schema
Copia y pega el siguiente SQL, luego click en **Run**:

```sql
-- =============================================
-- SCHEMA PARA INVESTTRACKER
-- =============================================

-- Habilitar extensión UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================
-- TABLA: users (Usuarios)
-- =============================================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índice para búsqueda por email
CREATE INDEX idx_users_email ON users(email);

-- =============================================
-- TABLA: assets (Activos/Inversiones)
-- =============================================
CREATE TABLE assets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    asset_type VARCHAR(50) NOT NULL CHECK (asset_type IN ('CEDEAR', 'Acción', 'Obligación Negociable')),
    ticker VARCHAR(20) NOT NULL,
    quantity DECIMAL(18, 8) NOT NULL CHECK (quantity > 0),
    avg_purchase_price DECIMAL(18, 4) NOT NULL CHECK (avg_purchase_price >= 0),
    purchase_date DATE NOT NULL,
    market VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para assets
CREATE INDEX idx_assets_user_id ON assets(user_id);
CREATE INDEX idx_assets_ticker ON assets(ticker);

-- =============================================
-- TABLA: alerts (Alertas de precio)
-- =============================================
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    asset_id UUID NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    alert_type VARCHAR(50) NOT NULL CHECK (alert_type IN ('target_buy', 'target_sell', 'stop_loss', 'take_profit')),
    target_value DECIMAL(18, 4) NOT NULL,
    is_percentage BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para alerts
CREATE INDEX idx_alerts_user_id ON alerts(user_id);
CREATE INDEX idx_alerts_asset_id ON alerts(asset_id);
CREATE INDEX idx_alerts_active ON alerts(is_active) WHERE is_active = TRUE;

-- =============================================
-- TABLA: alert_history (Historial de alertas disparadas)
-- =============================================
CREATE TABLE alert_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    asset_id UUID REFERENCES assets(id) ON DELETE SET NULL,
    ticker VARCHAR(20) NOT NULL,
    alert_type VARCHAR(50) NOT NULL,
    current_price DECIMAL(18, 4) NOT NULL,
    target_price DECIMAL(18, 4),
    message TEXT NOT NULL,
    email_sent BOOLEAN DEFAULT FALSE,
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para alert_history
CREATE INDEX idx_alert_history_user_id ON alert_history(user_id);
CREATE INDEX idx_alert_history_sent_at ON alert_history(sent_at DESC);

-- =============================================
-- TABLA: price_cache (Caché de precios)
-- =============================================
CREATE TABLE price_cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticker VARCHAR(20) UNIQUE NOT NULL,
    price DECIMAL(18, 4) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índice para price_cache
CREATE INDEX idx_price_cache_ticker ON price_cache(ticker);
CREATE INDEX idx_price_cache_updated ON price_cache(updated_at DESC);

-- =============================================
-- FUNCIÓN: Actualizar timestamp automáticamente
-- =============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers para updated_at
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_assets_updated_at
    BEFORE UPDATE ON assets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_alerts_updated_at
    BEFORE UPDATE ON alerts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================
-- ROW LEVEL SECURITY (Seguridad por fila)
-- =============================================

-- Habilitar RLS en todas las tablas
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE assets ENABLE ROW LEVEL SECURITY;
ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE alert_history ENABLE ROW LEVEL SECURITY;

-- Políticas para users (solo ver/editar su propio perfil)
CREATE POLICY "Users can view own profile" ON users
    FOR SELECT USING (auth.uid()::text = id::text);

CREATE POLICY "Users can update own profile" ON users
    FOR UPDATE USING (auth.uid()::text = id::text);

-- Políticas para assets (solo ver/editar sus propios activos)
CREATE POLICY "Users can view own assets" ON assets
    FOR SELECT USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can insert own assets" ON assets
    FOR INSERT WITH CHECK (auth.uid()::text = user_id::text);

CREATE POLICY "Users can update own assets" ON assets
    FOR UPDATE USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can delete own assets" ON assets
    FOR DELETE USING (auth.uid()::text = user_id::text);

-- Políticas para alerts
CREATE POLICY "Users can view own alerts" ON alerts
    FOR SELECT USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can insert own alerts" ON alerts
    FOR INSERT WITH CHECK (auth.uid()::text = user_id::text);

CREATE POLICY "Users can update own alerts" ON alerts
    FOR UPDATE USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can delete own alerts" ON alerts
    FOR DELETE USING (auth.uid()::text = user_id::text);

-- Políticas para alert_history
CREATE POLICY "Users can view own alert history" ON alert_history
    FOR SELECT USING (auth.uid()::text = user_id::text);

-- =============================================
-- DATOS DE DEMO (Opcional)
-- =============================================

-- Usuario demo (password: demo123)
-- El hash es para 'demo123' usando bcrypt
INSERT INTO users (id, email, password_hash, name) VALUES 
(
    'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
    'demo@inversiones.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.nRE5RwTCBq1QFO',
    'Usuario Demo'
);

-- Activos de demo
INSERT INTO assets (user_id, asset_type, ticker, quantity, avg_purchase_price, purchase_date, market) VALUES
('a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'CEDEAR', 'AAPL', 10, 175.50, '2024-01-15', 'NASDAQ'),
('a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'CEDEAR', 'GOOGL', 5, 140.25, '2024-02-20', 'NASDAQ'),
('a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'Acción', 'YPFD.BA', 100, 25000.00, '2024-03-10', 'BCBA'),
('a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'Acción', 'GGAL.BA', 50, 5500.00, '2024-04-05', 'BCBA');

-- Alertas de demo
INSERT INTO alerts (user_id, asset_id, alert_type, target_value, is_percentage, is_active)
SELECT 
    'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
    id,
    'stop_loss',
    10,
    TRUE,
    TRUE
FROM assets WHERE ticker = 'AAPL' AND user_id = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'
LIMIT 1;

INSERT INTO alerts (user_id, asset_id, alert_type, target_value, is_percentage, is_active)
SELECT 
    'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
    id,
    'take_profit',
    200.00,
    FALSE,
    TRUE
FROM assets WHERE ticker = 'AAPL' AND user_id = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'
LIMIT 1;

COMMIT;
```

---

## 🔑 Paso 3: Obtener las Credenciales

### 3.1 Ir a Project Settings
1. Click en el ícono de ⚙️ **Settings** en el menú lateral
2. Click en **API**

### 3.2 Copiar las credenciales
Necesitarás estos valores:

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| **Project URL** | URL de tu proyecto | `https://abcdefg.supabase.co` |
| **anon public** | Key pública (para frontend) | `eyJhbGciOiJIUzI1NiIs...` |
| **service_role** | Key privada (SOLO backend) | `eyJhbGciOiJIUzI1NiIs...` |

⚠️ **IMPORTANTE**: La `service_role` key tiene permisos totales. NUNCA la expongas en el frontend.

---

## ⚙️ Paso 4: Configurar el Backend

### 4.1 Crear archivo `.env` en `/backend/`

```env
# =============================================
# SUPABASE CONFIGURATION
# =============================================

# URL de tu proyecto Supabase
SUPABASE_URL=https://tu-proyecto-id.supabase.co

# Key pública (anon)
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Key de servicio (solo backend!)
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Conexión directa a PostgreSQL (alternativa)
DATABASE_URL=postgresql://postgres:[TU-PASSWORD]@db.tu-proyecto-id.supabase.co:5432/postgres

# =============================================
# JWT (para tokens propios)
# =============================================
JWT_SECRET_KEY=tu-clave-secreta-muy-larga-y-segura-cambiar-en-produccion

# =============================================
# EMAIL (Resend - opcional)
# =============================================
RESEND_API_KEY=re_xxxxxxxxxxxx
SENDER_EMAIL=alertas@tudominio.com
```

### 4.2 Instalar dependencia de Supabase

```bash
cd backend
pip install supabase
```

O agregar a `requirements.txt`:
```
supabase>=2.0.0
```

---

## 🐍 Paso 5: Código de Conexión (Python)

### 5.1 Crear archivo `backend/database.py`

```python
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Configuración de Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")  # Usar service key en backend

# Cliente de Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# =============================================
# FUNCIONES DE BASE DE DATOS
# =============================================

# --- USUARIOS ---
async def create_user(email: str, password_hash: str, name: str):
    """Crear nuevo usuario"""
    result = supabase.table("users").insert({
        "email": email,
        "password_hash": password_hash,
        "name": name
    }).execute()
    return result.data[0] if result.data else None

async def get_user_by_email(email: str):
    """Obtener usuario por email"""
    result = supabase.table("users").select("*").eq("email", email).execute()
    return result.data[0] if result.data else None

async def get_user_by_id(user_id: str):
    """Obtener usuario por ID"""
    result = supabase.table("users").select("*").eq("id", user_id).execute()
    return result.data[0] if result.data else None

# --- ACTIVOS ---
async def create_asset(user_id: str, asset_data: dict):
    """Crear nuevo activo"""
    asset_data["user_id"] = user_id
    result = supabase.table("assets").insert(asset_data).execute()
    return result.data[0] if result.data else None

async def get_user_assets(user_id: str):
    """Obtener todos los activos de un usuario"""
    result = supabase.table("assets").select("*").eq("user_id", user_id).execute()
    return result.data

async def get_asset_by_id(asset_id: str, user_id: str):
    """Obtener activo por ID"""
    result = supabase.table("assets").select("*").eq("id", asset_id).eq("user_id", user_id).execute()
    return result.data[0] if result.data else None

async def update_asset(asset_id: str, user_id: str, update_data: dict):
    """Actualizar activo"""
    result = supabase.table("assets").update(update_data).eq("id", asset_id).eq("user_id", user_id).execute()
    return result.data[0] if result.data else None

async def delete_asset(asset_id: str, user_id: str):
    """Eliminar activo"""
    result = supabase.table("assets").delete().eq("id", asset_id).eq("user_id", user_id).execute()
    return len(result.data) > 0

# --- ALERTAS ---
async def create_alert(user_id: str, alert_data: dict):
    """Crear nueva alerta"""
    alert_data["user_id"] = user_id
    result = supabase.table("alerts").insert(alert_data).execute()
    return result.data[0] if result.data else None

async def get_user_alerts(user_id: str):
    """Obtener todas las alertas de un usuario"""
    result = supabase.table("alerts").select("*, assets(ticker, asset_type)").eq("user_id", user_id).execute()
    return result.data

async def get_active_alerts():
    """Obtener todas las alertas activas (para el scheduler)"""
    result = supabase.table("alerts").select("*, assets(ticker, avg_purchase_price), users(email, name)").eq("is_active", True).execute()
    return result.data

async def update_alert(alert_id: str, user_id: str, update_data: dict):
    """Actualizar alerta"""
    result = supabase.table("alerts").update(update_data).eq("id", alert_id).eq("user_id", user_id).execute()
    return result.data[0] if result.data else None

async def delete_alert(alert_id: str, user_id: str):
    """Eliminar alerta"""
    result = supabase.table("alerts").delete().eq("id", alert_id).eq("user_id", user_id).execute()
    return len(result.data) > 0

# --- HISTORIAL DE ALERTAS ---
async def create_alert_history(history_data: dict):
    """Crear registro en historial"""
    result = supabase.table("alert_history").insert(history_data).execute()
    return result.data[0] if result.data else None

async def get_user_alert_history(user_id: str, limit: int = 50):
    """Obtener historial de alertas del usuario"""
    result = supabase.table("alert_history").select("*").eq("user_id", user_id).order("sent_at", desc=True).limit(limit).execute()
    return result.data

# --- CACHÉ DE PRECIOS ---
async def update_price_cache(ticker: str, price: float):
    """Actualizar precio en caché"""
    result = supabase.table("price_cache").upsert({
        "ticker": ticker,
        "price": price,
        "updated_at": "now()"
    }, on_conflict="ticker").execute()
    return result.data[0] if result.data else None

async def get_cached_price(ticker: str):
    """Obtener precio del caché"""
    result = supabase.table("price_cache").select("*").eq("ticker", ticker).execute()
    return result.data[0] if result.data else None
```

---

## ✅ Paso 6: Verificar la Conexión

### Test rápido en Python:

```python
# test_supabase.py
from database import supabase

# Probar conexión
result = supabase.table("users").select("*").limit(1).execute()
print("✅ Conexión exitosa!")
print(f"Usuarios en la base: {len(result.data)}")
```

Ejecutar:
```bash
python test_supabase.py
```

---

## 📊 Paso 7: Ver los Datos en Supabase

1. En el dashboard de Supabase, click en **Table Editor**
2. Verás todas las tablas creadas
3. Puedes ver, editar y agregar datos directamente

---

## 🔒 Seguridad Adicional

### Configurar Authentication (opcional)
Si quieres usar la autenticación de Supabase en lugar de JWT propio:

1. Ve a **Authentication** → **Providers**
2. Habilita **Email** provider
3. Configura los templates de email

### Configurar Storage (para archivos)
Si necesitas subir archivos:

1. Ve a **Storage**
2. Crea un bucket: `documents`
3. Configura las políticas de acceso

---

## 🎯 Resumen de Credenciales Necesarias

| Variable | Dónde encontrarla |
|----------|-------------------|
| `SUPABASE_URL` | Settings → API → Project URL |
| `SUPABASE_KEY` | Settings → API → anon public |
| `SUPABASE_SERVICE_KEY` | Settings → API → service_role |
| `DATABASE_URL` | Settings → Database → Connection string |

---

## 🆘 Troubleshooting

### Error: "Invalid API key"
- Verifica que copiaste la key completa
- Usa `service_role` key en backend (no `anon`)

### Error: "relation does not exist"
- Ejecuta el SQL schema primero
- Verifica en Table Editor que las tablas existen

### Error: "permission denied"
- Las políticas RLS pueden bloquear queries
- Para desarrollo, puedes desactivar RLS temporalmente:
  ```sql
  ALTER TABLE nombre_tabla DISABLE ROW LEVEL SECURITY;
  ```

### Error de conexión
- Verifica que el proyecto esté activo (no pausado)
- Proyectos inactivos por 7 días se pausan (plan gratuito)

---

## 📚 Recursos Adicionales

- [Documentación oficial de Supabase](https://supabase.com/docs)
- [Supabase Python Client](https://supabase.com/docs/reference/python/introduction)
- [Supabase JavaScript Client](https://supabase.com/docs/reference/javascript/introduction)
- [Migrar de MongoDB a PostgreSQL](https://supabase.com/docs/guides/migrations)
