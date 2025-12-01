from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import get_db, close_db, Wallet, SniperConfig, WalletGroup
from core.wallet import import_wallet
from utils.encryption import decrypt_private_key
from trading.sniper import SniperManager

router = APIRouter(prefix="/sniper", tags=["sniper"])

# Pydantic models
class SniperConfigRequest(BaseModel):
    wallet_id: int
    buy_amount: float = 0.1
    slippage: float = 5.0
    min_liquidity: float = 5.0
    min_safety_score: int = 70
    require_mint_renounced: bool = True
    require_freeze_renounced: bool = True
    max_buy_tax: float = 10.0
    max_sell_tax: float = 10.0

class SniperStartRequest(BaseModel):
    wallet_id: int
    password: str
    platforms: list = ["raydium", "pumpfun"]

class GroupSniperConfigRequest(BaseModel):
    group_id: int
    buy_amount: float = 0.1
    slippage: float = 5.0
    min_liquidity: float = 5.0
    min_safety_score: int = 70
    require_mint_renounced: bool = True
    require_freeze_renounced: bool = True
    max_buy_tax: float = 10.0
    max_sell_tax: float = 10.0
    password: str
    platforms: list = ["raydium", "pumpfun"]

# Routes
@router.post("/config")
def save_sniper_config(request: SniperConfigRequest, db: Session = Depends(get_db)):
    """Save or update sniper configuration"""
    try:
        # Check if config exists
        config = db.query(SniperConfig).filter(
            SniperConfig.wallet_id == request.wallet_id
        ).first()
        
        if config:
            # Update existing
            config.buy_amount = request.buy_amount
            config.slippage = request.slippage
            config.min_liquidity = request.min_liquidity
            config.require_mint_renounced = request.require_mint_renounced
            config.require_freeze_renounced = request.require_freeze_renounced
            config.max_buy_tax = request.max_buy_tax
            config.max_sell_tax = request.max_sell_tax
        else:
            # Create new
            config = SniperConfig(
                wallet_id=request.wallet_id,
                buy_amount=request.buy_amount,
                slippage=request.slippage,
                min_liquidity=request.min_liquidity,
                require_mint_renounced=request.require_mint_renounced,
                require_freeze_renounced=request.require_freeze_renounced,
                max_buy_tax=request.max_buy_tax,
                max_sell_tax=request.max_sell_tax
            )
            db.add(config)
        
        db.commit()
        db.refresh(config)
        
        return {
            "id": config.id,
            "wallet_id": config.wallet_id,
            "buy_amount": config.buy_amount,
            "slippage": config.slippage,
            "min_liquidity": config.min_liquidity,
            "is_active": config.is_active
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        close_db(db)

@router.get("/config/{wallet_id}")
def get_sniper_config(wallet_id: int, db: Session = Depends(get_db)):
    """Get sniper configuration for wallet"""
    try:
        config = db.query(SniperConfig).filter(
            SniperConfig.wallet_id == wallet_id
        ).first()
        
        if not config:
            raise HTTPException(status_code=404, detail="Config not found")
        
        return {
            "id": config.id,
            "wallet_id": config.wallet_id,
            "buy_amount": config.buy_amount,
            "slippage": config.slippage,
            "min_liquidity": config.min_liquidity,
            "require_mint_renounced": config.require_mint_renounced,
            "require_freeze_renounced": config.require_freeze_renounced,
            "max_buy_tax": config.max_buy_tax,
            "max_sell_tax": config.max_sell_tax,
            "is_active": config.is_active
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        close_db(db)

@router.post("/start")
async def start_sniper(
    request: SniperStartRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Start sniper bot"""
    try:
        # Get wallet
        wallet = db.query(Wallet).filter(Wallet.id == request.wallet_id).first()
        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")
        
        # Get config
        config = db.query(SniperConfig).filter(
            SniperConfig.wallet_id == request.wallet_id
        ).first()
        
        if not config:
            raise HTTPException(status_code=404, detail="Sniper config not found")
        
        # Decrypt private key
        try:
            private_key = decrypt_private_key(wallet.encrypted_private_key, request.password)
        except:
            raise HTTPException(status_code=401, detail="Invalid password")
        
        # Import keypair
        keypair = import_wallet(private_key, "private_key")
        
        # Prepare config dict
        config_dict = {
            "buy_amount": config.buy_amount,
            "slippage": config.slippage,
            "min_liquidity": config.min_liquidity,
            "min_safety_score": 70,
            "require_mint_renounced": config.require_mint_renounced,
            "require_freeze_renounced": config.require_freeze_renounced,
            "max_buy_tax": config.max_buy_tax
        }
        
        # Start sniper via manager
        manager = SniperManager.get_instance()
        result = await manager.start(request.wallet_id, keypair, config_dict)
        
        # Update config status
        config.is_active = True
        db.commit()
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        close_db(db)

@router.post("/stop")
async def stop_sniper(db: Session = Depends(get_db)):
    """Stop sniper bot"""
    try:
        manager = SniperManager.get_instance()
        result = await manager.stop()
        
        # Update all configs to inactive
        db.query(SniperConfig).update({"is_active": False})
        db.commit()
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        close_db(db)

@router.get("/status")
def get_sniper_status():
    """Get sniper bot status"""
    try:
        manager = SniperManager.get_instance()
        return manager.get_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/group/setup")
async def setup_group_sniper(
    request: GroupSniperConfigRequest,
    db: Session = Depends(get_db)
):
    """Setup sniper configuration for all wallets in a group"""
    try:
        # Get group
        group = db.query(WalletGroup).filter(WalletGroup.id == request.group_id).first()
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")

        # Get all wallets in group
        wallets = db.query(Wallet).filter(Wallet.group_id == request.group_id).all()
        if not wallets:
            raise HTTPException(status_code=404, detail="No wallets found in group")

        # Verify password with first wallet
        try:
            decrypt_private_key(wallets[0].encrypted_private_key, request.password)
        except:
            raise HTTPException(status_code=401, detail="Invalid password")

        # Create/update config for each wallet
        configs_created = 0
        configs_updated = 0

        for wallet in wallets:
            config = db.query(SniperConfig).filter(
                SniperConfig.wallet_id == wallet.id
            ).first()

            if config:
                # Update existing
                config.buy_amount = request.buy_amount
                config.slippage = request.slippage
                config.min_liquidity = request.min_liquidity
                config.require_mint_renounced = request.require_mint_renounced
                config.require_freeze_renounced = request.require_freeze_renounced
                config.max_buy_tax = request.max_buy_tax
                config.max_sell_tax = request.max_sell_tax
                configs_updated += 1
            else:
                # Create new
                config = SniperConfig(
                    wallet_id=wallet.id,
                    buy_amount=request.buy_amount,
                    slippage=request.slippage,
                    min_liquidity=request.min_liquidity,
                    require_mint_renounced=request.require_mint_renounced,
                    require_freeze_renounced=request.require_freeze_renounced,
                    max_buy_tax=request.max_buy_tax,
                    max_sell_tax=request.max_sell_tax
                )
                db.add(config)
                configs_created += 1

        db.commit()

        return {
            "success": True,
            "message": f"Group sniper configured for {len(wallets)} wallets",
            "group_id": request.group_id,
            "group_name": group.name,
            "total_wallets": len(wallets),
            "configs_created": configs_created,
            "configs_updated": configs_updated,
            "platforms": request.platforms,
            "config": {
                "buy_amount": request.buy_amount,
                "slippage": request.slippage,
                "min_liquidity": request.min_liquidity,
                "min_safety_score": request.min_safety_score,
                "require_mint_renounced": request.require_mint_renounced,
                "require_freeze_renounced": request.require_freeze_renounced
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        close_db(db)
