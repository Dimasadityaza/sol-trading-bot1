from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import init_db, get_db, close_db, Wallet
from core.wallet import generate_wallet, import_wallet, get_balance, keypair_to_base58
from utils.encryption import encrypt_private_key, decrypt_private_key
from api.routes import trading, sniper, analytics, groups

app = FastAPI(title="Solana Sniper Bot API", version="1.0.0")

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

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()
    print("✓ API Server started successfully")

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
def root():
    return {"message": "Solana Sniper Bot API", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "API is running"}

@app.post("/wallet/create", response_model=WalletResponse)
def create_wallet(request: CreateWalletRequest, db: Session = Depends(get_db)):
    """Create new wallet"""
    try:
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

# Network settings
class NetworkConfig(BaseModel):
    network: str  # 'devnet' or 'mainnet'

# Initialize network from environment config
import config as cfg

# Detect network from RPC_ENDPOINT
def detect_network_from_config():
    """Detect network type from RPC endpoint in config"""
    if "mainnet" in cfg.RPC_ENDPOINT:
        return {
            "network": "mainnet",
            "rpc_endpoint": cfg.RPC_ENDPOINT,
            "ws_endpoint": cfg.WS_ENDPOINT
        }
    else:
        return {
            "network": "devnet",
            "rpc_endpoint": cfg.RPC_ENDPOINT,
            "ws_endpoint": cfg.WS_ENDPOINT
        }

# Global network state - initialized from .env
current_network = detect_network_from_config()

@app.get("/settings/network")
def get_network():
    """Get current network configuration"""
    return current_network

@app.post("/settings/network")
def set_network(config: NetworkConfig):
    """Set network (devnet or mainnet)"""
    global current_network

    if config.network not in ["devnet", "mainnet"]:
        raise HTTPException(status_code=400, detail="Network must be 'devnet' or 'mainnet'")

    if config.network == "mainnet":
        current_network = {
            "network": "mainnet",
            "rpc_endpoint": "https://api.mainnet-beta.solana.com",
            "ws_endpoint": "wss://api.mainnet-beta.solana.com"
        }
    else:
        current_network = {
            "network": "devnet",
            "rpc_endpoint": "https://api.devnet.solana.com",
            "ws_endpoint": "wss://api.devnet.solana.com"
        }

    # Update config module
    cfg.RPC_ENDPOINT = current_network["rpc_endpoint"]
    cfg.WS_ENDPOINT = current_network["ws_endpoint"]

    return current_network

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

@app.get("/price/sol")
async def get_sol_price():
    """Get current SOL price in USD"""
    try:
        from utils.price_feed import get_price_feed
        
        price_feed = get_price_feed()
        sol_price = await price_feed.get_sol_price_usd()
        
        if sol_price is None:
            raise HTTPException(status_code=503, detail="Unable to fetch SOL price")
        
        return {
            "symbol": "SOL",
            "price_usd": sol_price,
            "timestamp": "now"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/wallet/list-with-usd")
async def list_wallets_with_usd(db: Session = Depends(get_db)):
    """List all wallets with USD values"""
    try:
        from utils.price_feed import get_price_feed
        
        # Get SOL price
        price_feed = get_price_feed()
        sol_price = await price_feed.get_sol_price_usd()
        
        if sol_price is None:
            # Fallback to balance only if price fetch fails
            sol_price = 0.0
        
        wallets = db.query(Wallet).all()
        
        result = []
        for wallet in wallets:
            balance_sol = get_balance(wallet.public_key)
            balance_usd = balance_sol * sol_price if sol_price > 0 else 0.0
            
            result.append({
                "id": wallet.id,
                "label": wallet.label,
                "public_key": wallet.public_key,
                "balance_sol": balance_sol,
                "balance_usd": balance_usd,
                "is_primary": wallet.is_primary,
                "group_id": wallet.group_id
            })
        
        return {
            "sol_price_usd": sol_price,
            "wallets": result,
            "total_wallets": len(result)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        close_db(db)
