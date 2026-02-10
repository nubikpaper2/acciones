# Configuración de la Tabla de Notificaciones en Supabase

## Crear la tabla `notifications`

Ejecuta este SQL en Supabase (SQL Editor):

```sql
-- Tabla de notificaciones in-app
CREATE TABLE notifications (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(50) NOT NULL, -- 'alert_triggered', 'price_change', 'system', etc.
    ticker VARCHAR(20),
    current_price DECIMAL(15, 2),
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para búsquedas eficientes
CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_is_read ON notifications(user_id, is_read);
CREATE INDEX idx_notifications_created_at ON notifications(created_at DESC);

-- Deshabilitar RLS para desarrollo (igual que las otras tablas)
ALTER TABLE notifications DISABLE ROW LEVEL SECURITY;
```

## Verificar la tabla

```sql
SELECT * FROM notifications LIMIT 10;
```

## Listo!

Una vez creada la tabla, el sistema de notificaciones funcionará automáticamente:
- Las alertas generarán notificaciones in-app
- Verás el icono de campana con badge en el dashboard
- Las notificaciones se guardan y puedes verlas después
