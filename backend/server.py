from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
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

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

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
    client.close()

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
        "price_id": str(uuid.uuid4()),
        "ticker": ticker,
        "price": price,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    await db.price_history.insert_one(price_doc)

async def send_alert_email(user_email: str, ticker: str, alert_type: str, current_price: float, message: str):
    if not RESEND_API_KEY:
        logging.warning("Resend API key not configured, skipping email")
        return
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #4338ca; color: white; padding: 20px; text-align: center; }}
            .content {{ background-color: #f4f4f5; padding: 20px; }}
            .alert-box {{ background-color: white; border-left: 4px solid #4338ca; padding: 15px; margin: 15px 0; }}
            .price {{ font-size: 24px; font-weight: bold; color: #4338ca; }}
            .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔔 Alerta de Inversión</h1>
            </div>
            <div class="content">
                <div class="alert-box">
                    <h2>Activo: {ticker}</h2>
                    <p><strong>Tipo de alerta:</strong> {alert_type}</p>
                    <p><strong>Precio actual:</strong> <span class="price">${current_price:.2f}</span></p>
                    <p><strong>Mensaje:</strong> {message}</p>
                    <p><strong>Fecha y hora:</strong> {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                </div>
            </div>
            <div class="footer">
                <p>Este es un mensaje automático de tu sistema de seguimiento de inversiones.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    params = {
        "from": SENDER_EMAIL,
        "to": [user_email],
        "subject": f"🔔 Alerta: {ticker} - {alert_type}",
        "html": html_content
    }
    
    try:
        await asyncio.to_thread(resend.Emails.send, params)
        logging.info(f"Alert email sent to {user_email} for {ticker}")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")

async def check_prices_and_alerts():
    logging.info("Starting price check and alert evaluation")
    try:
        # Get all unique tickers from assets
        assets = await db.assets.find({}, {"_id": 0}).to_list(1000)
        tickers = list(set([asset['ticker'] for asset in assets]))
        
        for ticker in tickers:
            price = await get_current_price(ticker)
            if price:
                await save_price_history(ticker, price)
                
                # Check alerts for this ticker
                ticker_assets = [a for a in assets if a['ticker'] == ticker]
                for asset in ticker_assets:
                    alerts = await db.alerts.find({
                        "asset_id": asset['asset_id'],
                        "is_active": True
                    }, {"_id": 0}).to_list(100)
                    
                    for alert in alerts:
                        should_trigger = False
                        message = ""
                        
                        if alert['is_percentage']:
                            threshold = asset['avg_purchase_price'] * (1 + alert['target_value'] / 100)
                        else:
                            threshold = alert['target_value']
                        
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
                            # Get user email
                            user = await db.users.find_one({"user_id": alert['user_id']}, {"_id": 0})
                            if user:
                                await send_alert_email(
                                    user['email'],
                                    ticker,
                                    alert['alert_type'],
                                    price,
                                    message
                                )
                                
                                # Save to history
                                history_doc = {
                                    "history_id": str(uuid.uuid4()),
                                    "user_id": alert['user_id'],
                                    "asset_id": asset['asset_id'],
                                    "ticker": ticker,
                                    "alert_type": alert['alert_type'],
                                    "current_price": price,
                                    "message": message,
                                    "sent_at": datetime.now(timezone.utc).isoformat()
                                }
                                await db.alert_history.insert_one(history_doc)
                                
                                # Deactivate alert
                                await db.alerts.update_one(
                                    {"alert_id": alert['alert_id']},
                                    {"$set": {"is_active": False}}
                                )
                                
        logging.info("Price check and alert evaluation completed")
    except Exception as e:
        logging.error(f"Error in check_prices_and_alerts: {e}")

# Auth routes
@api_router.post("/auth/register")
async def register(user_data: UserRegister):
    existing = await db.users.find_one({"email": user_data.email}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = str(uuid.uuid4())
    user_doc = {
        "user_id": user_id,
        "email": user_data.email,
        "password": hash_password(user_data.password),
        "name": user_data.name,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.users.insert_one(user_doc)
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
    user = await db.users.find_one({"email": credentials.email}, {"_id": 0})
    if not user or not verify_password(credentials.password, user['password']):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_token(user['user_id'])
    
    return {
        "token": token,
        "user": {
            "user_id": user['user_id'],
            "email": user['email'],
            "name": user['name']
        }
    }

@api_router.get("/auth/me")
async def get_me(user_id: str = Depends(get_current_user)):
    user = await db.users.find_one({"user_id": user_id}, {"_id": 0, "password": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Assets routes
@api_router.post("/assets", response_model=Asset)
async def create_asset(asset_data: AssetCreate, user_id: str = Depends(get_current_user)):
    asset_id = str(uuid.uuid4())
    asset_doc = {
        "asset_id": asset_id,
        "user_id": user_id,
        **asset_data.model_dump(),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.assets.insert_one(asset_doc)
    return Asset(**asset_doc)

@api_router.get("/assets", response_model=List[Asset])
async def get_assets(user_id: str = Depends(get_current_user)):
    assets = await db.assets.find({"user_id": user_id}, {"_id": 0}).to_list(1000)
    return assets

@api_router.get("/assets/{asset_id}", response_model=Asset)
async def get_asset(asset_id: str, user_id: str = Depends(get_current_user)):
    asset = await db.assets.find_one({"asset_id": asset_id, "user_id": user_id}, {"_id": 0})
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset

@api_router.put("/assets/{asset_id}", response_model=Asset)
async def update_asset(asset_id: str, update_data: AssetUpdate, user_id: str = Depends(get_current_user)):
    asset = await db.assets.find_one({"asset_id": asset_id, "user_id": user_id}, {"_id": 0})
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
    if update_dict:
        await db.assets.update_one({"asset_id": asset_id}, {"$set": update_dict})
        asset.update(update_dict)
    
    return asset

@api_router.delete("/assets/{asset_id}")
async def delete_asset(asset_id: str, user_id: str = Depends(get_current_user)):
    result = await db.assets.delete_one({"asset_id": asset_id, "user_id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    # Delete associated alerts
    await db.alerts.delete_many({"asset_id": asset_id})
    
    return {"message": "Asset deleted successfully"}

# Portfolio routes
@api_router.get("/portfolio/summary", response_model=PortfolioSummary)
async def get_portfolio_summary(user_id: str = Depends(get_current_user)):
    assets = await db.assets.find({"user_id": user_id}, {"_id": 0}).to_list(1000)
    
    total_investment = 0
    current_value = 0
    
    for asset in assets:
        investment = asset['quantity'] * asset['avg_purchase_price']
        total_investment += investment
        
        price = await get_current_price(asset['ticker'])
        if price:
            current_value += asset['quantity'] * price
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
    assets = await db.assets.find({"user_id": user_id}, {"_id": 0}).to_list(1000)
    result = []
    
    for asset_doc in assets:
        asset = Asset(**asset_doc)
        price = await get_current_price(asset.ticker)
        
        if price:
            current_value = asset.quantity * price
            investment = asset.quantity * asset.avg_purchase_price
            gain_loss = current_value - investment
            gain_loss_pct = (gain_loss / investment * 100) if investment > 0 else 0
            
            # Simple recommendation logic
            if gain_loss_pct > 20:
                recommendation = "Considerar venta (ganancia >20%)"
            elif gain_loss_pct < -10:
                recommendation = "Revisar posición (pérdida >10%)"
            else:
                recommendation = "Mantener"
            
            result.append(AssetWithPrice(
                asset=asset,
                current_price=price,
                current_value=current_value,
                gain_loss=gain_loss,
                gain_loss_pct=gain_loss_pct,
                recommendation=recommendation
            ))
        else:
            result.append(AssetWithPrice(
                asset=asset,
                current_price=None,
                current_value=None,
                gain_loss=None,
                gain_loss_pct=None,
                recommendation="Precio no disponible"
            ))
    
    return result

# Alerts routes
@api_router.post("/alerts", response_model=Alert)
async def create_alert(alert_data: AlertCreate, user_id: str = Depends(get_current_user)):
    # Verify asset belongs to user
    asset = await db.assets.find_one({"asset_id": alert_data.asset_id, "user_id": user_id}, {"_id": 0})
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    alert_id = str(uuid.uuid4())
    alert_doc = {
        "alert_id": alert_id,
        "user_id": user_id,
        "asset_id": alert_data.asset_id,
        "alert_type": alert_data.alert_type,
        "target_value": alert_data.target_value,
        "is_percentage": alert_data.is_percentage,
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.alerts.insert_one(alert_doc)
    return Alert(**alert_doc)

@api_router.get("/alerts", response_model=List[Alert])
async def get_alerts(user_id: str = Depends(get_current_user)):
    alerts = await db.alerts.find({"user_id": user_id}, {"_id": 0}).to_list(1000)
    return alerts

@api_router.get("/alerts/asset/{asset_id}", response_model=List[Alert])
async def get_alerts_by_asset(asset_id: str, user_id: str = Depends(get_current_user)):
    # Verify asset belongs to user
    asset = await db.assets.find_one({"asset_id": asset_id, "user_id": user_id}, {"_id": 0})
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    alerts = await db.alerts.find({"asset_id": asset_id}, {"_id": 0}).to_list(1000)
    return alerts

@api_router.put("/alerts/{alert_id}", response_model=Alert)
async def update_alert(alert_id: str, update_data: AlertUpdate, user_id: str = Depends(get_current_user)):
    alert = await db.alerts.find_one({"alert_id": alert_id, "user_id": user_id}, {"_id": 0})
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
    if update_dict:
        await db.alerts.update_one({"alert_id": alert_id}, {"$set": update_dict})
        alert.update(update_dict)
    
    return alert

@api_router.delete("/alerts/{alert_id}")
async def delete_alert(alert_id: str, user_id: str = Depends(get_current_user)):
    result = await db.alerts.delete_one({"alert_id": alert_id, "user_id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return {"message": "Alert deleted successfully"}

# Alert history routes
@api_router.get("/alerts/history", response_model=List[AlertHistory])
async def get_alert_history(user_id: str = Depends(get_current_user)):
    history = await db.alert_history.find({"user_id": user_id}, {"_id": 0}).sort("sent_at", -1).to_list(100)
    return history

# Price history routes
@api_router.get("/prices/{ticker}")
async def get_price_history(ticker: str, limit: int = 100):
    prices = await db.price_history.find({"ticker": ticker}, {"_id": 0}).sort("timestamp", -1).limit(limit).to_list(limit)
    return prices

@api_router.get("/prices/{ticker}/current")
async def get_current_price_endpoint(ticker: str):
    price = await get_current_price(ticker)
    if price is None:
        raise HTTPException(status_code=404, detail="Price not available")
    return {"ticker": ticker, "price": price, "timestamp": datetime.now(timezone.utc).isoformat()}

# Demo data endpoint
@api_router.post("/demo/create")
async def create_demo_data():
    # Create demo user
    demo_email = "demo@inversiones.com"
    existing = await db.users.find_one({"email": demo_email}, {"_id": 0})
    
    if existing:
        return {"message": "Demo user already exists", "email": demo_email, "password": "demo123"}
    
    user_id = str(uuid.uuid4())
    user_doc = {
        "user_id": user_id,
        "email": demo_email,
        "password": hash_password("demo123"),
        "name": "Usuario Demo",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.users.insert_one(user_doc)
    
    # Create demo assets
    demo_assets = [
        {
            "asset_type": "CEDEAR",
            "ticker": "AAPL",
            "quantity": 10,
            "avg_purchase_price": 150.0,
            "purchase_date": "2024-01-15",
            "market": "NYSE"
        },
        {
            "asset_type": "CEDEAR",
            "ticker": "GOOGL",
            "quantity": 5,
            "avg_purchase_price": 140.0,
            "purchase_date": "2024-02-10",
            "market": "NASDAQ"
        },
        {
            "asset_type": "Acción",
            "ticker": "YPFD.BA",
            "quantity": 100,
            "avg_purchase_price": 25000.0,
            "purchase_date": "2024-03-05",
            "market": "BCBA"
        },
        {
            "asset_type": "Acción",
            "ticker": "GGAL.BA",
            "quantity": 50,
            "avg_purchase_price": 15000.0,
            "purchase_date": "2024-03-20",
            "market": "BCBA"
        }
    ]
    
    asset_ids = []
    for asset_data in demo_assets:
        asset_id = str(uuid.uuid4())
        asset_doc = {
            "asset_id": asset_id,
            "user_id": user_id,
            **asset_data,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.assets.insert_one(asset_doc)
        asset_ids.append(asset_id)
    
    # Create demo alerts
    demo_alerts = [
        {
            "asset_id": asset_ids[0],
            "alert_type": "target_sell",
            "target_value": 200.0,
            "is_percentage": False
        },
        {
            "asset_id": asset_ids[0],
            "alert_type": "stop_loss",
            "target_value": -10.0,
            "is_percentage": True
        },
        {
            "asset_id": asset_ids[1],
            "alert_type": "take_profit",
            "target_value": 15.0,
            "is_percentage": True
        }
    ]
    
    for alert_data in demo_alerts:
        alert_id = str(uuid.uuid4())
        alert_doc = {
            "alert_id": alert_id,
            "user_id": user_id,
            "is_active": True,
            **alert_data,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.alerts.insert_one(alert_doc)
    
    return {
        "message": "Demo data created successfully",
        "email": demo_email,
        "password": "demo123"
    }

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)