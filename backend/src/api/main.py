from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from loguru import logger
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import init_db, get_db, close_db, Wallet
from core.wallet import generate_wallet, import_wallet, get_balance, keypair_to_base58
from utils.encryption import encrypt_private_key, decrypt_private_key
from api.routes import trading, sniper, analytics, groups

# Configure logging
logger.add(
    "logs/api_{time:YYYY-MM-DD}.log",
    rotation="00:00",
    retention="30 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Solana Trading Bot API",
    version="2.0.0",
    description="Professional Solana trading bot with multi-wallet support and automated sniping",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add rate limiter to app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Include routers
app.include_router(trading.router)
app.include_router(sniper.router)
app.include_router(analytics.router)
app.include_router(groups.router)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error occurred"}
    )

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = datetime.utcnow()

    # Log request
    logger.info(f"Request: {request.method} {request.url.path}")

    # Process request
    response = await call_next(request)

    # Log response time
    process_time = (datetime.utcnow() - start_time).total_seconds()
    logger.info(f"Response: {response.status_code} | Time: {process_time:.3f}s")

    return response

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()
    logger.info("API Server started successfully")
    logger.info(f"Documentation available at /docs")

# Shutdown logging
@app.on_event("shutdown")
def shutdown_event():
    logger.info("API Server shutting down")

# Pydantic models
class CreateWalletRequest(BaseModel):
    password: str
    label: str = "My Wallet"

class ImportWalletRequest(BaseModel):
    private_key: Optional[str] = None
    mnemonic: Optional[str] = None
    password: str
    label: str = "Imported Wallet"

class WalletResponse(BaseModel):
    id: int
    label: str
    public_key: str
    balance: float = 0.0
    is_primary: bool = False

# Routes
@app.get("/")
@limiter.limit("100/minute")
async def root(request: Request):
    """Root endpoint"""
    return {
        "message": "Solana Trading Bot API",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
@limiter.limit("100/minute")
async def health_check(request: Request):
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "API is running",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/wallet/create", response_model=WalletResponse)
@limiter.limit("10/minute")
async def create_wallet(req: Request, request: CreateWalletRequest, db: Session = Depends(get_db)):
    """Create new wallet"""
    try:
        logger.info(f"Creating new wallet: {request.label}")

        # Generate wallet
        mnemonic, keypair = generate_wallet()

        # Encrypt private key
        private_key = keypair_to_base58(keypair)
        encrypted_key = encrypt_private_key(private_key, request.password)

        # Save to database
        wallet = Wallet(
            label=request.label,
            encrypted_private_key=encrypted_key,
            public_key=str(keypair.pubkey()),
            is_primary=db.query(Wallet).count() == 0  # First wallet is primary
        )
        db.add(wallet)
        db.commit()
        db.refresh(wallet)

        logger.info(f"Wallet created successfully: {wallet.public_key}")

        # Get balance
        balance = get_balance(str(keypair.pubkey()))

        return WalletResponse(
            id=wallet.id,
            label=wallet.label,
            public_key=wallet.public_key,
            balance=balance,
            is_primary=wallet.is_primary
        )
    except Exception as e:
        logger.error(f"Error creating wallet: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        close_db(db)

@app.post("/wallet/import", response_model=WalletResponse)
def import_wallet_endpoint(request: ImportWalletRequest, db: Session = Depends(get_db)):
    """Import existing wallet"""
    try:
        # Import wallet
        if request.mnemonic:
            keypair = import_wallet(request.mnemonic, "mnemonic")
        elif request.private_key:
            keypair = import_wallet(request.private_key, "private_key")
        else:
            raise HTTPException(status_code=400, detail="Provide either private_key or mnemonic")
        
        # Check if wallet already exists
        existing = db.query(Wallet).filter(Wallet.public_key == str(keypair.pubkey())).first()
        if existing:
            raise HTTPException(status_code=400, detail="Wallet already exists")
        
        # Encrypt private key
        private_key = keypair_to_base58(keypair)
        encrypted_key = encrypt_private_key(private_key, request.password)
        
        # Save to database
        wallet = Wallet(
            label=request.label,
            encrypted_private_key=encrypted_key,
            public_key=str(keypair.pubkey()),
            is_primary=db.query(Wallet).count() == 0
        )
        db.add(wallet)
        db.commit()
        db.refresh(wallet)
        
        # Get balance
        balance = get_balance(str(keypair.pubkey()))
        
        return WalletResponse(
            id=wallet.id,
            label=wallet.label,
            public_key=wallet.public_key,
            balance=balance,
            is_primary=wallet.is_primary
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        close_db(db)

@app.get("/wallet/list", response_model=List[WalletResponse])
def list_wallets(db: Session = Depends(get_db)):
    """List all wallets"""
    try:
        wallets = db.query(Wallet).all()
        
        result = []
        for wallet in wallets:
            balance = get_balance(wallet.public_key)
            result.append(WalletResponse(
                id=wallet.id,
                label=wallet.label,
                public_key=wallet.public_key,
                balance=balance,
                is_primary=wallet.is_primary
            ))
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        close_db(db)

@app.get("/wallet/{wallet_id}", response_model=WalletResponse)
def get_wallet(wallet_id: int, db: Session = Depends(get_db)):
    """Get wallet details"""
    try:
        wallet = db.query(Wallet).filter(Wallet.id == wallet_id).first()
        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")
        
        balance = get_balance(wallet.public_key)
        
        return WalletResponse(
            id=wallet.id,
            label=wallet.label,
            public_key=wallet.public_key,
            balance=balance,
            is_primary=wallet.is_primary
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        close_db(db)

@app.get("/wallet/{wallet_id}/balance")
def get_wallet_balance(wallet_id: int, db: Session = Depends(get_db)):
    """Get wallet balance"""
    try:
        wallet = db.query(Wallet).filter(Wallet.id == wallet_id).first()
        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")
        
        balance = get_balance(wallet.public_key)
        
        return {
            "wallet_id": wallet_id,
            "public_key": wallet.public_key,
            "balance": balance,
            "balance_lamports": int(balance * 1e9)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        close_db(db)

@app.delete("/wallet/{wallet_id}")
def delete_wallet(wallet_id: int, db: Session = Depends(get_db)):
    """Delete wallet"""
    try:
        wallet = db.query(Wallet).filter(Wallet.id == wallet_id).first()
        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")
        
        db.delete(wallet)
        db.commit()
        
        return {"message": "Wallet deleted successfully", "wallet_id": wallet_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        close_db(db)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
