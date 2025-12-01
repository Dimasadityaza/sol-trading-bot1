from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional, List
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import get_db, close_db, Wallet, Trade
from core.wallet import import_wallet
from utils.encryption import decrypt_private_key
from trading.executor import TradeExecutor
from monitoring.token_analyzer import TokenAnalyzer

router = APIRouter(prefix="/trade", tags=["trading"])

# Pydantic models
class BuyRequest(BaseModel):
    wallet_id: int
    token_address: str
    sol_amount: float
    slippage: float = 1.0
    password: str

class SellRequest(BaseModel):
    wallet_id: int
    token_address: str
    percentage: float = 100.0
    slippage: float = 1.0
    password: str

class TokenAnalyzeRequest(BaseModel):
    token_address: str

# Routes
@router.post("/buy")
async def execute_buy(request: BuyRequest, db: Session = Depends(get_db)):
    """Execute buy trade"""
    try:
        # Get wallet
        wallet = db.query(Wallet).filter(Wallet.id == request.wallet_id).first()
        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")
        
        # Decrypt private key
        try:
            private_key = decrypt_private_key(wallet.encrypted_private_key, request.password)
        except:
            raise HTTPException(status_code=401, detail="Invalid password")
        
        # Import keypair
        keypair = import_wallet(private_key, "private_key")
        
        # Execute trade
        executor = TradeExecutor(request.wallet_id, keypair)
        result = await executor.execute_buy(
            token_address=request.token_address,
            sol_amount=request.sol_amount,
            slippage=request.slippage,
            strategy="manual"
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        close_db(db)

@router.post("/sell")
async def execute_sell(request: SellRequest, db: Session = Depends(get_db)):
    """Execute sell trade"""
    try:
        # Get wallet
        wallet = db.query(Wallet).filter(Wallet.id == request.wallet_id).first()
        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")
        
        # Decrypt private key
        try:
            private_key = decrypt_private_key(wallet.encrypted_private_key, request.password)
        except:
            raise HTTPException(status_code=401, detail="Invalid password")
        
        # Import keypair
        keypair = import_wallet(private_key, "private_key")
        
        # Execute trade
        executor = TradeExecutor(request.wallet_id, keypair)
        result = await executor.execute_sell(
            token_address=request.token_address,
            percentage=request.percentage,
            slippage=request.slippage,
            strategy="manual"
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        close_db(db)

@router.get("/history")
def get_trade_history(
    wallet_id: Optional[int] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get trade history"""
    try:
        query = db.query(Trade)
        
        if wallet_id:
            query = query.filter(Trade.wallet_id == wallet_id)
        
        trades = query.order_by(Trade.timestamp.desc()).limit(limit).all()
        
        return [{
            "id": trade.id,
            "wallet_id": trade.wallet_id,
            "token_address": trade.token_address,
            "trade_type": trade.trade_type,
            "amount": trade.amount,
            "price": trade.price,
            "cost": trade.cost,
            "revenue": trade.revenue,
            "pnl": trade.pnl,
            "signature": trade.signature,
            "timestamp": trade.timestamp.isoformat(),
            "strategy": trade.strategy
        } for trade in trades]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        close_db(db)

@router.post("/analyze")
async def analyze_token(request: TokenAnalyzeRequest):
    """Analyze token safety"""
    try:
        analyzer = TokenAnalyzer()
        result = analyzer.analyze_token(request.token_address)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
def get_trading_stats(wallet_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Get trading statistics"""
    try:
        query = db.query(Trade)
        
        if wallet_id:
            query = query.filter(Trade.wallet_id == wallet_id)
        
        trades = query.all()
        
        total_trades = len(trades)
        buy_trades = len([t for t in trades if t.trade_type == "buy"])
        sell_trades = len([t for t in trades if t.trade_type == "sell"])
        
        # Calculate PnL
        total_pnl = sum([t.pnl or 0 for t in trades])
        winning_trades = len([t for t in trades if (t.pnl or 0) > 0])
        
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        return {
            "total_trades": total_trades,
            "buy_trades": buy_trades,
            "sell_trades": sell_trades,
            "total_pnl": total_pnl,
            "winning_trades": winning_trades,
            "losing_trades": total_trades - winning_trades,
            "win_rate": round(win_rate, 2)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        close_db(db)
