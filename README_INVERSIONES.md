# InvestTracker - Aplicación de Seguimiento de Inversiones

## 📊 Descripción

Plataforma completa para el seguimiento de inversiones en el mercado argentino e internacional. Rastrea CEDEARs, acciones y obligaciones negociables con alertas automáticas por email.

## ✨ Características Implementadas

### 🎯 Funcionalidades Core
- ✅ **Gestión de Cartera**: CRUD completo de activos (CEDEARs, acciones, obligaciones negociables)
- ✅ **Seguimiento de Precios**: Integración con Yahoo Finance para precios en tiempo real
- ✅ **Sistema de Alertas**: Configuración de alertas con precio objetivo, stop loss y take profit
- ✅ **Análisis Automático**: Actualización de precios cada 15 minutos mediante scheduler
- ✅ **Recomendaciones**: Sistema inteligente de sugerencias de compra/venta/mantener
- ✅ **Alertas por Email**: Envío automático de notificaciones con Resend
- ✅ **Historial**: Registro completo de alertas disparadas

### 💼 Gestión de Activos
Cada activo incluye:
- Tipo (CEDEAR, Acción, Obligación Negociable)
- Ticker (ej: AAPL, GOOGL, YPFD.BA)
- Cantidad
- Precio promedio de compra
- Fecha de compra
- Mercado (NYSE, NASDAQ, BCBA)

### 🔔 Sistema de Alertas
- **Precio Objetivo de Compra**: Alerta cuando el precio baja al nivel deseado
- **Precio Objetivo de Venta**: Alerta cuando el precio sube al nivel deseado
- **Stop Loss**: Protección contra pérdidas (% o precio fijo)
- **Take Profit**: Alerta al alcanzar ganancia objetivo (% o precio fijo)
- Soporte para valores en **porcentaje** o **precio fijo**
- Pausar/reactivar alertas en cualquier momento

### 📈 Dashboard
- **Resumen de Cartera**: Inversión total, valor actual, ganancia/pérdida ($ y %)
- **Lista de Activos**: Todos los activos con precios actuales y recomendaciones
- **Gestión Visual**: Indicadores de ganancia (verde) y pérdida (rojo)
- **Navegación Intuitiva**: Sidebar con acceso rápido a todas las secciones

## 🚀 Inicio Rápido

### 1. Cuenta Demo
La aplicación incluye datos demo para probar inmediatamente:
- **Email**: demo@inversiones.com
- **Password**: demo123

Los datos demo incluyen:
- 4 activos de ejemplo (AAPL, GOOGL, YPFD.BA, GGAL.BA)
- 3 alertas pre-configuradas
- Precios reales de Yahoo Finance

### 2. Crear tu Propia Cuenta
1. Ve a la pestaña "Registrarse"
2. Ingresa tu nombre, email y contraseña
3. ¡Listo! Comienza a agregar tus activos

## 🔧 Configuración de Alertas por Email

Para recibir alertas por email, necesitas configurar Resend:

### Paso 1: Obtener API Key de Resend
1. Ve a [https://resend.com](https://resend.com)
2. Crea una cuenta gratuita
3. En el Dashboard, ve a **API Keys**
4. Haz click en **Create API Key**
5. Copia la key (comienza con `re_...`)

### Paso 2: Configurar en la Aplicación
1. Edita el archivo `/app/backend/.env`
2. Reemplaza la línea `RESEND_API_KEY=""` con tu key:
   ```
   RESEND_API_KEY="re_tu_api_key_aqui"
   ```
3. (Opcional) Cambia el email de envío:
   ```
   SENDER_EMAIL="tu-email@tudominio.com"
   ```
   **Nota**: En modo test de Resend, los emails solo se envían a direcciones verificadas

### Paso 3: Reiniciar el Backend
```bash
sudo supervisorctl restart backend
```

### Paso 4: Verificar Email en Resend
- En modo test, necesitas verificar tu email en Resend
- Ve a Settings → Domains → Add Email para verificar tu email personal

## 📊 Uso de la Aplicación

### Agregar un Activo
1. Ve a la sección **Activos** o haz click en **Agregar** en el Dashboard
2. Completa el formulario:
   - Tipo de activo
   - Ticker (usar formato correcto: AAPL para US, YPFD.BA para Argentina)
   - Cantidad
   - Precio promedio de compra
   - Fecha de compra
   - Mercado

### Crear una Alerta
1. En la lista de activos, haz click en el ícono de campana (🔔)
2. Selecciona el tipo de alerta
3. Ingresa el valor objetivo
4. Elige si usar porcentaje o precio fijo
5. Guarda la alerta

### Gestionar Alertas
- **Pausar/Reactivar**: Usa el switch en la sección Alertas
- **Eliminar**: Haz click en el ícono de basura
- **Ver Historial**: Ve a la sección Historial para ver alertas enviadas

## 🔄 Sistema de Actualización Automática

El backend incluye un **scheduler** que:
- Se ejecuta automáticamente cada **15 minutos**
- Obtiene precios actualizados de Yahoo Finance
- Evalúa todas las alertas activas
- Envía emails cuando se cumplen las condiciones
- Guarda el historial de precios para análisis

## 🎨 Diseño

La aplicación utiliza un diseño **Swiss High-Contrast**:
- Colores profesionales (Deep Indigo)
- Tipografía: Manrope (headings), Public Sans (body), JetBrains Mono (datos)
- Indicadores visuales claros para ganancias/pérdidas
- Diseño responsive (mobile-friendly)

## 🔐 Seguridad

- **Autenticación JWT**: Tokens seguros con expiración de 7 días
- **Contraseñas hasheadas**: Usando bcrypt
- **Variables de entorno**: Credenciales protegidas
- **CORS configurado**: Protección contra solicitudes no autorizadas

## 📱 Tecnologías

### Backend
- **FastAPI**: API REST moderna y rápida
- **MongoDB**: Base de datos NoSQL
- **APScheduler**: Scheduler para tareas automáticas
- **yfinance**: Obtención de precios en tiempo real
- **Resend**: Servicio de emails transaccionales
- **JWT**: Autenticación segura

### Frontend
- **React**: Interfaz de usuario interactiva
- **Tailwind CSS**: Estilos modernos
- **Shadcn/UI**: Componentes de interfaz
- **Lucide React**: Iconos
- **Axios**: Peticiones HTTP
- **Sonner**: Notificaciones toast
- **React Router**: Navegación

## 📍 APIs Disponibles

### Autenticación
- `POST /api/auth/register` - Crear cuenta
- `POST /api/auth/login` - Iniciar sesión
- `GET /api/auth/me` - Obtener usuario actual

### Activos
- `POST /api/assets` - Crear activo
- `GET /api/assets` - Listar activos
- `GET /api/assets/{id}` - Obtener activo
- `PUT /api/assets/{id}` - Actualizar activo
- `DELETE /api/assets/{id}` - Eliminar activo

### Portfolio
- `GET /api/portfolio/summary` - Resumen de cartera
- `GET /api/portfolio/assets` - Activos con precios y cálculos

### Alertas
- `POST /api/alerts` - Crear alerta
- `GET /api/alerts` - Listar alertas
- `PUT /api/alerts/{id}` - Actualizar alerta
- `DELETE /api/alerts/{id}` - Eliminar alerta
- `GET /api/alerts/history` - Historial de alertas

### Precios
- `GET /api/prices/{ticker}` - Historial de precios
- `GET /api/prices/{ticker}/current` - Precio actual

### Demo
- `POST /api/demo/create` - Crear datos demo

## 🎯 Próximos Pasos Sugeridos

1. **Configurar Resend** para recibir alertas por email
2. **Agregar tus propios activos** y configurar alertas personalizadas
3. **Explorar el historial** después de que el scheduler se ejecute
4. **Personalizar configuraciones** según tus necesidades

## ⚠️ Notas Importantes

- Los precios se obtienen de **Yahoo Finance** (gratis, sin necesidad de API key)
- El scheduler se ejecuta **cada 15 minutos** automáticamente
- Las alertas se **desactivan automáticamente** después de dispararse
- Puedes tener **múltiples alertas por activo**
- Los datos demo se crean automáticamente al hacer login demo

## 📞 Soporte

Para tickers argentinos, usa el sufijo `.BA`:
- YPF: `YPFD.BA`
- Galicia: `GGAL.BA`
- Mercado Libre: `MELI`

Para CEDEARs y acciones US, usa el ticker estándar:
- Apple: `AAPL`
- Google: `GOOGL`
- Microsoft: `MSFT`

---

**¡Tu plataforma de inversiones está lista! Comienza a trackear tus activos ahora mismo.** 🚀
