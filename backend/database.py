"""
InvestTracker - Módulo de conexión a Supabase
=============================================

Este módulo proporciona funciones para interactuar con la base de datos Supabase.
Usar como alternativa a MongoDB para producción en la nube.

Uso:
    from database import supabase, get_user_by_email, create_asset, etc.
"""

import os
from typing import Optional, List, Dict, Any
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Verificar si Supabase está configurado
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_KEY")

supabase = None

if SUPABASE_URL and SUPABASE_KEY:
    try:
        from supabase import create_client, Client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Conexión a Supabase establecida")
    except ImportError:
        print("⚠️  Instala supabase: pip install supabase")
    except Exception as e:
        print(f"❌ Error conectando a Supabase: {e}")
else:
    print("ℹ️  Supabase no configurado. Usando MongoDB.")


# =============================================
# FUNCIONES DE USUARIOS
# =============================================

def create_user(email: str, password_hash: str, name: str) -> Optional[Dict]:
    """Crear nuevo usuario"""
    if not supabase:
        return None
    
    result = supabase.table("users").insert({
        "email": email,
        "password_hash": password_hash,
        "name": name
    }).execute()
    
    return result.data[0] if result.data else None


def get_user_by_email(email: str) -> Optional[Dict]:
    """Obtener usuario por email"""
    if not supabase:
        return None
    
    result = supabase.table("users").select("*").eq("email", email).execute()
    return result.data[0] if result.data else None


def get_user_by_id(user_id: str) -> Optional[Dict]:
    """Obtener usuario por ID"""
    if not supabase:
        return None
    
    result = supabase.table("users").select("*").eq("id", user_id).execute()
    return result.data[0] if result.data else None


def update_user(user_id: str, update_data: Dict) -> Optional[Dict]:
    """Actualizar datos del usuario"""
    if not supabase:
        return None
    
    result = supabase.table("users").update(update_data).eq("id", user_id).execute()
    return result.data[0] if result.data else None


# =============================================
# FUNCIONES DE ACTIVOS
# =============================================

def create_asset(user_id: str, asset_data: Dict) -> Optional[Dict]:
    """Crear nuevo activo"""
    if not supabase:
        return None
    
    asset_data["user_id"] = user_id
    result = supabase.table("assets").insert(asset_data).execute()
    return result.data[0] if result.data else None


def get_user_assets(user_id: str) -> List[Dict]:
    """Obtener todos los activos de un usuario"""
    if not supabase:
        return []
    
    result = supabase.table("assets").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
    return result.data or []


def get_asset_by_id(asset_id: str, user_id: str = None) -> Optional[Dict]:
    """Obtener activo por ID"""
    if not supabase:
        return None
    
    query = supabase.table("assets").select("*").eq("id", asset_id)
    if user_id:
        query = query.eq("user_id", user_id)
    
    result = query.execute()
    return result.data[0] if result.data else None


def update_asset(asset_id: str, user_id: str, update_data: Dict) -> Optional[Dict]:
    """Actualizar activo"""
    if not supabase:
        return None
    
    result = supabase.table("assets").update(update_data).eq("id", asset_id).eq("user_id", user_id).execute()
    return result.data[0] if result.data else None


def delete_asset(asset_id: str, user_id: str) -> bool:
    """Eliminar activo"""
    if not supabase:
        return False
    
    result = supabase.table("assets").delete().eq("id", asset_id).eq("user_id", user_id).execute()
    return len(result.data) > 0 if result.data else False


def get_all_tickers() -> List[str]:
    """Obtener lista de todos los tickers únicos (para actualización de precios)"""
    if not supabase:
        return []
    
    result = supabase.table("assets").select("ticker").execute()
    tickers = list(set([r["ticker"] for r in result.data])) if result.data else []
    return tickers


# =============================================
# FUNCIONES DE ALERTAS
# =============================================

def create_alert(user_id: str, alert_data: Dict) -> Optional[Dict]:
    """Crear nueva alerta"""
    if not supabase:
        return None
    
    alert_data["user_id"] = user_id
    result = supabase.table("alerts").insert(alert_data).execute()
    return result.data[0] if result.data else None


def get_user_alerts(user_id: str) -> List[Dict]:
    """Obtener todas las alertas de un usuario con info del activo"""
    if not supabase:
        return []
    
    result = supabase.table("alerts").select(
        "*, assets(id, ticker, asset_type, avg_purchase_price)"
    ).eq("user_id", user_id).order("created_at", desc=True).execute()
    
    return result.data or []


def get_active_alerts() -> List[Dict]:
    """Obtener todas las alertas activas (para el scheduler)"""
    if not supabase:
        return []
    
    result = supabase.table("alerts").select(
        "*, assets(ticker, avg_purchase_price, user_id), users!alerts_user_id_fkey(email, name)"
    ).eq("is_active", True).execute()
    
    return result.data or []


def get_alert_by_id(alert_id: str, user_id: str = None) -> Optional[Dict]:
    """Obtener alerta por ID"""
    if not supabase:
        return None
    
    query = supabase.table("alerts").select("*, assets(ticker, asset_type)").eq("id", alert_id)
    if user_id:
        query = query.eq("user_id", user_id)
    
    result = query.execute()
    return result.data[0] if result.data else None


def update_alert(alert_id: str, user_id: str, update_data: Dict) -> Optional[Dict]:
    """Actualizar alerta"""
    if not supabase:
        return None
    
    result = supabase.table("alerts").update(update_data).eq("id", alert_id).eq("user_id", user_id).execute()
    return result.data[0] if result.data else None


def delete_alert(alert_id: str, user_id: str) -> bool:
    """Eliminar alerta"""
    if not supabase:
        return False
    
    result = supabase.table("alerts").delete().eq("id", alert_id).eq("user_id", user_id).execute()
    return len(result.data) > 0 if result.data else False


def deactivate_alert(alert_id: str) -> bool:
    """Desactivar alerta (después de dispararse)"""
    if not supabase:
        return False
    
    result = supabase.table("alerts").update({"is_active": False}).eq("id", alert_id).execute()
    return len(result.data) > 0 if result.data else False


# =============================================
# FUNCIONES DE HISTORIAL DE ALERTAS
# =============================================

def create_alert_history(history_data: Dict) -> Optional[Dict]:
    """Crear registro en historial de alertas"""
    if not supabase:
        return None
    
    result = supabase.table("alert_history").insert(history_data).execute()
    return result.data[0] if result.data else None


def get_user_alert_history(user_id: str, limit: int = 50) -> List[Dict]:
    """Obtener historial de alertas del usuario"""
    if not supabase:
        return []
    
    result = supabase.table("alert_history").select("*").eq("user_id", user_id).order("sent_at", desc=True).limit(limit).execute()
    return result.data or []


# =============================================
# FUNCIONES DE CACHÉ DE PRECIOS
# =============================================

def update_price_cache(ticker: str, price: float) -> Optional[Dict]:
    """Actualizar precio en caché (upsert)"""
    if not supabase:
        return None
    
    result = supabase.table("price_cache").upsert({
        "ticker": ticker,
        "price": price,
        "updated_at": datetime.utcnow().isoformat()
    }, on_conflict="ticker").execute()
    
    return result.data[0] if result.data else None


def get_cached_price(ticker: str) -> Optional[Dict]:
    """Obtener precio del caché"""
    if not supabase:
        return None
    
    result = supabase.table("price_cache").select("*").eq("ticker", ticker).execute()
    return result.data[0] if result.data else None


def get_all_cached_prices() -> Dict[str, float]:
    """Obtener todos los precios del caché como diccionario"""
    if not supabase:
        return {}
    
    result = supabase.table("price_cache").select("ticker, price").execute()
    return {r["ticker"]: r["price"] for r in result.data} if result.data else {}


def bulk_update_prices(prices: Dict[str, float]) -> int:
    """Actualizar múltiples precios a la vez"""
    if not supabase or not prices:
        return 0
    
    records = [
        {"ticker": ticker, "price": price, "updated_at": datetime.utcnow().isoformat()}
        for ticker, price in prices.items()
    ]
    
    result = supabase.table("price_cache").upsert(records, on_conflict="ticker").execute()
    return len(result.data) if result.data else 0


# =============================================
# FUNCIONES AUXILIARES
# =============================================

def check_connection() -> bool:
    """Verificar si la conexión a Supabase está activa"""
    if not supabase:
        return False
    
    try:
        result = supabase.table("users").select("id").limit(1).execute()
        return True
    except Exception as e:
        print(f"Error de conexión: {e}")
        return False


def get_portfolio_summary(user_id: str, prices: Dict[str, float]) -> Dict:
    """Calcular resumen del portafolio"""
    assets = get_user_assets(user_id)
    
    if not assets:
        return {
            "total_investment": 0,
            "current_value": 0,
            "total_gain_loss": 0,
            "total_gain_loss_pct": 0,
            "assets_count": 0
        }
    
    total_investment = sum(a["quantity"] * a["avg_purchase_price"] for a in assets)
    current_value = sum(
        a["quantity"] * prices.get(a["ticker"], a["avg_purchase_price"])
        for a in assets
    )
    
    total_gain_loss = current_value - total_investment
    total_gain_loss_pct = (total_gain_loss / total_investment * 100) if total_investment > 0 else 0
    
    return {
        "total_investment": round(total_investment, 2),
        "current_value": round(current_value, 2),
        "total_gain_loss": round(total_gain_loss, 2),
        "total_gain_loss_pct": round(total_gain_loss_pct, 2),
        "assets_count": len(assets)
    }


# =============================================
# TEST DE CONEXIÓN
# =============================================

if __name__ == "__main__":
    print("\n🔍 Probando conexión a Supabase...\n")
    
    if check_connection():
        print("✅ Conexión exitosa!")
        
        # Contar registros
        users = supabase.table("users").select("id", count="exact").execute()
        assets = supabase.table("assets").select("id", count="exact").execute()
        alerts = supabase.table("alerts").select("id", count="exact").execute()
        
        print(f"\n📊 Estadísticas:")
        print(f"   - Usuarios: {users.count or 0}")
        print(f"   - Activos: {assets.count or 0}")
        print(f"   - Alertas: {alerts.count or 0}")
    else:
        print("❌ No se pudo conectar a Supabase")
        print("\n💡 Verifica:")
        print("   1. SUPABASE_URL en .env")
        print("   2. SUPABASE_SERVICE_KEY en .env")
        print("   3. pip install supabase")
