from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import List, Optional, Literal
import uuid
from datetime import datetime, timezone, timedelta
import bcrypt
import jwt
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
import yfinance as yf
import resend
import requests

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Supabase REST API connection
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_KEY') or os.environ.get('SUPABASE_KEY')

def supabase_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

def supabase_get(table: str, params: dict = None):
    """GET request to Supabase REST API"""
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    response = requests.get(url, headers=supabase_headers(), params=params)
    if response.status_code == 200:
        return response.json()
    return []

def supabase_post(table: str, data: dict):
    """POST request to Supabase REST API"""
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    response = requests.post(url, headers=supabase_headers(), json=data)
    if response.status_code in [200, 201]:
        result = response.json()
        return result[0] if result else None
    return None

def supabase_patch(table: str, match: dict, data: dict):
    """PATCH request to Supabase REST API"""
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    params = {f"{k}": f"eq.{v}" for k, v in match.items()}
    response = requests.patch(url, headers=supabase_headers(), params=params, json=data)
    return response.status_code in [200, 204]

def supabase_delete(table: str, match: dict):
    """DELETE request to Supabase REST API"""
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    params = {f"{k}": f"eq.{v}" for k, v in match.items()}
    response = requests.delete(url, headers=supabase_headers(), params=params)
    return response.status_code in [200, 204]

logging.info("Configured Supabase REST API connection")

# Resend setup
RESEND_API_KEY = os.environ.get('RESEND_API_KEY', '')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'onboarding@resend.dev')
if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY

# JWT Setup
SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

security = HTTPBearer()

# Scheduler
scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    scheduler.start()
    scheduler.add_job(check_prices_and_alerts, 'interval', minutes=15, id='price_checker')
    logging.info("Scheduler started - checking prices every 15 minutes")
    yield
    # Shutdown
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)
api_router = APIRouter(prefix="/api")

# Models
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    user_id: str
    email: EmailStr
    name: str
    created_at: str

class Asset(BaseModel):
    model_config = ConfigDict(extra="ignore")
    asset_id: str
    user_id: str
    asset_type: Literal["CEDEAR", "Acción", "Obligación Negociable"]
    ticker: str
    quantity: float
    avg_purchase_price: float
    purchase_date: str
    market: str
    created_at: str

class AssetCreate(BaseModel):
    asset_type: Literal["CEDEAR", "Acción", "Obligación Negociable"]
    ticker: str
    quantity: float
    avg_purchase_price: float
    purchase_date: str
    market: str

class AssetUpdate(BaseModel):
    asset_type: Optional[Literal["CEDEAR", "Acción", "Obligación Negociable"]] = None
    ticker: Optional[str] = None
    quantity: Optional[float] = None
    avg_purchase_price: Optional[float] = None
    purchase_date: Optional[str] = None
    market: Optional[str] = None

class Alert(BaseModel):
    model_config = ConfigDict(extra="ignore")
    alert_id: str
    user_id: str
    asset_id: str
    alert_type: Literal["target_buy", "target_sell", "stop_loss", "take_profit"]
    target_value: float
    is_percentage: bool
    is_active: bool
    created_at: str

class AlertCreate(BaseModel):
    asset_id: str
    alert_type: Literal["target_buy", "target_sell", "stop_loss", "take_profit"]
    target_value: float
    is_percentage: bool = False

class AlertUpdate(BaseModel):
    alert_type: Optional[Literal["target_buy", "target_sell", "stop_loss", "take_profit"]] = None
    target_value: Optional[float] = None
    is_percentage: Optional[bool] = None
    is_active: Optional[bool] = None

class AlertHistory(BaseModel):
    model_config = ConfigDict(extra="ignore")
    history_id: str
    user_id: str
    asset_id: str
    ticker: str
    alert_type: str
    current_price: float
    message: str
    sent_at: str

class Notification(BaseModel):
    model_config = ConfigDict(extra="ignore")
    notification_id: str
    user_id: str
    title: str
    message: str
    notification_type: str
    ticker: Optional[str] = None
    current_price: Optional[float] = None
    is_read: bool = False
    created_at: str

class PriceHistory(BaseModel):
    model_config = ConfigDict(extra="ignore")
    price_id: str
    ticker: str
    price: float
    timestamp: str

class PortfolioSummary(BaseModel):
    total_investment: float
    current_value: float
    total_gain_loss: float
    total_gain_loss_pct: float
    assets_count: int

class AssetWithPrice(BaseModel):
    asset: Asset
    current_price: Optional[float]
    current_value: Optional[float]
    gain_loss: Optional[float]
    gain_loss_pct: Optional[float]
    recommendation: Optional[str]

# Helper functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": user_id, "exp": expire}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_price_from_yahoo_sync(ticker: str) -> Optional[float]:
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1d")
        if not hist.empty:
            return float(hist['Close'].iloc[-1])
    except Exception as e:
        logging.error(f"Yahoo Finance error for {ticker}: {e}")
    return None

async def get_current_price(ticker: str) -> Optional[float]:
    # Try Yahoo Finance first
    price = await asyncio.to_thread(get_price_from_yahoo_sync, ticker)
    if price:
        return price
    
    # Could add Google Finance fallback here if needed
    logging.warning(f"Could not fetch price for {ticker}")
    return None

async def save_price_history(ticker: str, price: float):
    price_doc = {
        "id": str(uuid.uuid4()),
        "ticker": ticker,
        "price": price,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    supabase_post("price_history", price_doc)

def get_alert_type_name(alert_type: str) -> str:
    """Convierte el tipo de alerta a un nombre legible"""
    names = {
        'target_buy': 'Objetivo de Compra',
        'target_sell': 'Objetivo de Venta',
        'stop_loss': 'Stop Loss',
        'take_profit': 'Take Profit'
    }
    return names.get(alert_type, alert_type)

async def save_notification(user_id: str, ticker: str, alert_type: str, current_price: float, message: str):
    """Guarda una notificación in-app para el usuario"""
    notification_doc = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "title": f"🔔 {get_alert_type_name(alert_type)}: {ticker}",
        "message": message,
        "notification_type": "alert_triggered",
        "ticker": ticker,
        "current_price": current_price,
        "is_read": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    result = supabase_post("notifications", notification_doc)
    if result:
        logging.info(f"Notification saved for user {user_id}: {ticker} - {alert_type}")
    else:
        logging.error(f"Failed to save notification for user {user_id}")
    return result

async def check_prices_and_alerts():
    logging.info("Starting price check and alert evaluation")
    try:
        # Get all assets
        assets = supabase_get("assets", {})
        tickers = list(set([asset['ticker'] for asset in assets]))
        
        for ticker in tickers:
            price = await get_current_price(ticker)
            if price:
                await save_price_history(ticker, price)
                
                # Check alerts for this ticker
                ticker_assets = [a for a in assets if a['ticker'] == ticker]
                for asset in ticker_assets:
                    alerts = supabase_get("alerts", {"asset_id": f"eq.{asset['id']}", "is_active": "eq.true"})
                    
                    for alert in alerts:
                        should_trigger = False
                        message = ""
                        
                        if alert['is_percentage']:
                            threshold = float(asset['avg_purchase_price']) * (1 + float(alert['target_value']) / 100)
                        else:
                            threshold = float(alert['target_value'])
                        
                        if alert['alert_type'] == 'target_buy' and price <= threshold:
                            should_trigger = True
                            message = f"El precio ha alcanzado tu objetivo de compra: ${price:.2f}"
                        elif alert['alert_type'] == 'target_sell' and price >= threshold:
                            should_trigger = True
                            message = f"El precio ha alcanzado tu objetivo de venta: ${price:.2f}"
                        elif alert['alert_type'] == 'stop_loss' and price <= threshold:
                            should_trigger = True
                            message = f"¡STOP LOSS activado! Precio actual: ${price:.2f}"
                        elif alert['alert_type'] == 'take_profit' and price >= threshold:
                            should_trigger = True
                            message = f"¡TAKE PROFIT alcanzado! Precio actual: ${price:.2f}"
                        
                        if should_trigger:
                            # Save in-app notification
                            await save_notification(
                                alert['user_id'],
                                ticker,
                                alert['alert_type'],
                                price,
                                message
                            )
                            
                            # Save to history
                            history_doc = {
                                "id": str(uuid.uuid4()),
                                "user_id": alert['user_id'],
                                "asset_id": asset['id'],
                                "ticker": ticker,
                                "alert_type": alert['alert_type'],
                                "current_price": price,
                                "message": message,
                                "sent_at": datetime.now(timezone.utc).isoformat()
                            }
                            supabase_post("alert_history", history_doc)
                            
                            # Deactivate alert
                            supabase_patch("alerts", {"id": alert['id']}, {"is_active": False})
                                
        logging.info("Price check and alert evaluation completed")
    except Exception as e:
        logging.error(f"Error in check_prices_and_alerts: {e}")

# Auth routes
@api_router.post("/auth/register")
async def register(user_data: UserRegister):
    result = supabase_get("users", {"email": f"eq.{user_data.email}"})
    if result:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = str(uuid.uuid4())
    user_doc = {
        "id": user_id,
        "email": user_data.email,
        "password_hash": hash_password(user_data.password),
        "name": user_data.name,
    }
    
    supabase_post("users", user_doc)
    token = create_token(user_id)
    
    return {
        "token": token,
        "user": {
            "user_id": user_id,
            "email": user_data.email,
            "name": user_data.name
        }
    }

@api_router.post("/auth/login")
async def login(credentials: UserLogin):
    result = supabase_get("users", {"email": f"eq.{credentials.email}"})
    user = result[0] if result else None
    if not user or not verify_password(credentials.password, user['password_hash']):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_token(user['id'])
    
    return {
        "token": token,
        "user": {
            "user_id": user['id'],
            "email": user['email'],
            "name": user['name']
        }
    }

@api_router.get("/auth/me")
async def get_me(user_id: str = Depends(get_current_user)):
    result = supabase_get("users", {"id": f"eq.{user_id}", "select": "id,email,name,created_at"})
    user = result[0] if result else None
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user_id": user['id'], "email": user['email'], "name": user['name'], "created_at": user.get('created_at', '')}

# Assets routes
@api_router.post("/assets", response_model=Asset)
async def create_asset(asset_data: AssetCreate, user_id: str = Depends(get_current_user)):
    asset_id = str(uuid.uuid4())
    asset_doc = {
        "id": asset_id,
        "user_id": user_id,
        **asset_data.model_dump(),
    }
    
    supabase_post("assets", asset_doc)
    return Asset(asset_id=asset_id, user_id=user_id, created_at=datetime.now(timezone.utc).isoformat(), **asset_data.model_dump())

@api_router.get("/assets", response_model=List[Asset])
async def get_assets(user_id: str = Depends(get_current_user)):
    result = supabase_get("assets", {"user_id": f"eq.{user_id}"})
    assets = []
    for a in result:
        assets.append(Asset(asset_id=a['id'], user_id=a['user_id'], asset_type=a['asset_type'], 
                           ticker=a['ticker'], quantity=a['quantity'], avg_purchase_price=a['avg_purchase_price'],
                           purchase_date=a['purchase_date'], market=a['market'], created_at=a.get('created_at', '')))
    return assets

@api_router.get("/assets/{asset_id}", response_model=Asset)
async def get_asset(asset_id: str, user_id: str = Depends(get_current_user)):
    result = supabase_get("assets", {"id": f"eq.{asset_id}", "user_id": f"eq.{user_id}"})
    if not result:
        raise HTTPException(status_code=404, detail="Asset not found")
    a = result[0]
    return Asset(asset_id=a['id'], user_id=a['user_id'], asset_type=a['asset_type'], 
                ticker=a['ticker'], quantity=a['quantity'], avg_purchase_price=a['avg_purchase_price'],
                purchase_date=a['purchase_date'], market=a['market'], created_at=a.get('created_at', ''))

@api_router.put("/assets/{asset_id}", response_model=Asset)
async def update_asset(asset_id: str, update_data: AssetUpdate, user_id: str = Depends(get_current_user)):
    result = supabase_get("assets", {"id": f"eq.{asset_id}", "user_id": f"eq.{user_id}"})
    if not result:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
    if update_dict:
        supabase_patch("assets", {"id": asset_id}, update_dict)
    
    result = supabase_get("assets", {"id": f"eq.{asset_id}"})
    a = result[0]
    return Asset(asset_id=a['id'], user_id=a['user_id'], asset_type=a['asset_type'], 
                ticker=a['ticker'], quantity=a['quantity'], avg_purchase_price=a['avg_purchase_price'],
                purchase_date=a['purchase_date'], market=a['market'], created_at=a.get('created_at', ''))

@api_router.delete("/assets/{asset_id}")
async def delete_asset(asset_id: str, user_id: str = Depends(get_current_user)):
    result = supabase_get("assets", {"id": f"eq.{asset_id}", "user_id": f"eq.{user_id}"})
    if not result:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    supabase_delete("assets", {"id": asset_id})
    supabase_delete("alerts", {"asset_id": asset_id})
    
    return {"message": "Asset deleted successfully"}

# Portfolio routes
@api_router.get("/portfolio/summary", response_model=PortfolioSummary)
async def get_portfolio_summary(user_id: str = Depends(get_current_user)):
    assets = supabase_get("assets", {"user_id": f"eq.{user_id}"})
    
    total_investment = 0
    current_value = 0
    
    for asset in assets:
        investment = float(asset['quantity']) * float(asset['avg_purchase_price'])
        total_investment += investment
        
        price = await get_current_price(asset['ticker'])
        if price:
            current_value += float(asset['quantity']) * price
        else:
            current_value += investment
    
    gain_loss = current_value - total_investment
    gain_loss_pct = (gain_loss / total_investment * 100) if total_investment > 0 else 0
    
    return PortfolioSummary(
        total_investment=total_investment,
        current_value=current_value,
        total_gain_loss=gain_loss,
        total_gain_loss_pct=gain_loss_pct,
        assets_count=len(assets)
    )

@api_router.get("/portfolio/assets", response_model=List[AssetWithPrice])
async def get_assets_with_prices(user_id: str = Depends(get_current_user)):
    assets = supabase_get("assets", {"user_id": f"eq.{user_id}"})
    response = []
    
    for a in assets:
        asset = Asset(asset_id=a['id'], user_id=a['user_id'], asset_type=a['asset_type'], 
                     ticker=a['ticker'], quantity=a['quantity'], avg_purchase_price=a['avg_purchase_price'],
                     purchase_date=a['purchase_date'], market=a['market'], created_at=a.get('created_at', ''))
        price = await get_current_price(asset.ticker)
        
        if price:
            current_value = float(asset.quantity) * price
            investment = float(asset.quantity) * float(asset.avg_purchase_price)
            gain_loss = current_value - investment
            gain_loss_pct = (gain_loss / investment * 100) if investment > 0 else 0
            
            # Simple recommendation logic
            if gain_loss_pct > 20:
                recommendation = "Considerar venta (ganancia >20%)"
            elif gain_loss_pct < -10:
                recommendation = "Revisar posición (pérdida >10%)"
            else:
                recommendation = "Mantener"
            
            response.append(AssetWithPrice(
                asset=asset,
                current_price=price,
                current_value=current_value,
                gain_loss=gain_loss,
                gain_loss_pct=gain_loss_pct,
                recommendation=recommendation
            ))
        else:
            response.append(AssetWithPrice(
                asset=asset,
                current_price=None,
                current_value=None,
                gain_loss=None,
                gain_loss_pct=None,
                recommendation="Precio no disponible"
            ))
    
    return response

# Alerts routes
@api_router.post("/alerts", response_model=Alert)
async def create_alert(alert_data: AlertCreate, user_id: str = Depends(get_current_user)):
    # Verify asset belongs to user
    result = supabase_get("assets", {"id": f"eq.{alert_data.asset_id}", "user_id": f"eq.{user_id}"})
    if not result:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    alert_id = str(uuid.uuid4())
    alert_doc = {
        "id": alert_id,
        "user_id": user_id,
        "asset_id": alert_data.asset_id,
        "alert_type": alert_data.alert_type,
        "target_value": alert_data.target_value,
        "is_percentage": alert_data.is_percentage,
        "is_active": True,
    }
    
    supabase_post("alerts", alert_doc)
    return Alert(alert_id=alert_id, user_id=user_id, asset_id=alert_data.asset_id, 
                alert_type=alert_data.alert_type, target_value=alert_data.target_value,
                is_percentage=alert_data.is_percentage, is_active=True, 
                created_at=datetime.now(timezone.utc).isoformat())

@api_router.get("/alerts", response_model=List[Alert])
async def get_alerts(user_id: str = Depends(get_current_user)):
    result = supabase_get("alerts", {"user_id": f"eq.{user_id}"})
    alerts = []
    for a in result:
        alerts.append(Alert(alert_id=a['id'], user_id=a['user_id'], asset_id=a['asset_id'],
                           alert_type=a['alert_type'], target_value=a['target_value'],
                           is_percentage=a['is_percentage'], is_active=a['is_active'], created_at=a.get('created_at', '')))
    return alerts

@api_router.get("/alerts/asset/{asset_id}", response_model=List[Alert])
async def get_alerts_by_asset(asset_id: str, user_id: str = Depends(get_current_user)):
    # Verify asset belongs to user
    result = supabase_get("assets", {"id": f"eq.{asset_id}", "user_id": f"eq.{user_id}"})
    if not result:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    result = supabase_get("alerts", {"asset_id": f"eq.{asset_id}"})
    alerts = []
    for a in result:
        alerts.append(Alert(alert_id=a['id'], user_id=a['user_id'], asset_id=a['asset_id'],
                           alert_type=a['alert_type'], target_value=a['target_value'],
                           is_percentage=a['is_percentage'], is_active=a['is_active'], created_at=a.get('created_at', '')))
    return alerts

@api_router.put("/alerts/{alert_id}", response_model=Alert)
async def update_alert(alert_id: str, update_data: AlertUpdate, user_id: str = Depends(get_current_user)):
    result = supabase_get("alerts", {"id": f"eq.{alert_id}", "user_id": f"eq.{user_id}"})
    if not result:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
    if update_dict:
        supabase_patch("alerts", {"id": alert_id}, update_dict)
    
    result = supabase_get("alerts", {"id": f"eq.{alert_id}"})
    a = result[0]
    return Alert(alert_id=a['id'], user_id=a['user_id'], asset_id=a['asset_id'],
                alert_type=a['alert_type'], target_value=a['target_value'],
                is_percentage=a['is_percentage'], is_active=a['is_active'], created_at=a.get('created_at', ''))

@api_router.delete("/alerts/{alert_id}")
async def delete_alert(alert_id: str, user_id: str = Depends(get_current_user)):
    result = supabase_get("alerts", {"id": f"eq.{alert_id}", "user_id": f"eq.{user_id}"})
    if not result:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    supabase_delete("alerts", {"id": alert_id})
    return {"message": "Alert deleted successfully"}

# Alert history routes
@api_router.get("/alerts/history", response_model=List[AlertHistory])
async def get_alert_history(user_id: str = Depends(get_current_user)):
    result = supabase_get("alert_history", {"user_id": f"eq.{user_id}", "order": "sent_at.desc", "limit": "100"})
    history = []
    for h in result:
        history.append(AlertHistory(history_id=h['id'], user_id=h['user_id'], asset_id=h.get('asset_id', ''),
                                   ticker=h.get('ticker', ''), alert_type=h.get('alert_type', ''), 
                                   current_price=h.get('current_price', 0),
                                   message=h.get('message', ''), sent_at=h.get('sent_at', '')))
    return history

# Price history routes
@api_router.get("/prices/{ticker}")
async def get_price_history(ticker: str, limit: int = 100):
    result = supabase_get("price_history", {"ticker": f"eq.{ticker}", "order": "timestamp.desc", "limit": str(limit)})
    return result

@api_router.get("/prices/{ticker}/current")
async def get_current_price_endpoint(ticker: str):
    price = await get_current_price(ticker)
    if price is None:
        raise HTTPException(status_code=404, detail="Price not available")
    return {"ticker": ticker, "price": price, "timestamp": datetime.now(timezone.utc).isoformat()}

# Test endpoint para verificar alertas manualmente
@api_router.post("/alerts/check-now")
async def check_alerts_now(user_id: str = Depends(get_current_user)):
    """Ejecuta la verificación de alertas manualmente (para testing)"""
    await check_prices_and_alerts()
    return {"message": "Verificación de alertas completada", "timestamp": datetime.now(timezone.utc).isoformat()}

# Notifications routes
@api_router.get("/notifications")
async def get_notifications(user_id: str = Depends(get_current_user)):
    """Obtiene todas las notificaciones del usuario ordenadas por fecha"""
    result = supabase_get("notifications", {"user_id": f"eq.{user_id}", "order": "created_at.desc", "limit": "50"})
    notifications = []
    for n in result:
        notifications.append(Notification(
            notification_id=n['id'],
            user_id=n['user_id'],
            title=n['title'],
            message=n['message'],
            notification_type=n['notification_type'],
            ticker=n.get('ticker'),
            current_price=n.get('current_price'),
            is_read=n.get('is_read', False),
            created_at=n.get('created_at', '')
        ))
    return notifications

@api_router.get("/notifications/unread-count")
async def get_unread_count(user_id: str = Depends(get_current_user)):
    """Obtiene la cantidad de notificaciones no leídas"""
    result = supabase_get("notifications", {"user_id": f"eq.{user_id}", "is_read": "eq.false"})
    return {"count": len(result)}

@api_router.put("/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str, user_id: str = Depends(get_current_user)):
    """Marca una notificación como leída"""
    result = supabase_get("notifications", {"id": f"eq.{notification_id}", "user_id": f"eq.{user_id}"})
    if not result:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    supabase_patch("notifications", {"id": notification_id}, {"is_read": True})
    return {"message": "Notification marked as read"}

@api_router.put("/notifications/read-all")
async def mark_all_notifications_read(user_id: str = Depends(get_current_user)):
    """Marca todas las notificaciones del usuario como leídas"""
    supabase_patch("notifications", {"user_id": user_id, "is_read": False}, {"is_read": True})
    return {"message": "All notifications marked as read"}

@api_router.delete("/notifications/{notification_id}")
async def delete_notification(notification_id: str, user_id: str = Depends(get_current_user)):
    """Elimina una notificación"""
    result = supabase_get("notifications", {"id": f"eq.{notification_id}", "user_id": f"eq.{user_id}"})
    if not result:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    supabase_delete("notifications", {"id": notification_id})
    return {"message": "Notification deleted"}

@api_router.post("/notifications/test")
async def create_test_notification(user_id: str = Depends(get_current_user)):
    """Crea una notificación de prueba para el usuario actual"""
    await save_notification(
        user_id,
        "TEST",
        "target_sell",
        150.50,
        "¡Esta es una notificación de prueba! El precio de TEST ha alcanzado $150.50"
    )
    return {"message": "Notificación de prueba creada", "timestamp": datetime.now(timezone.utc).isoformat()}

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)