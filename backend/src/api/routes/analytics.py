from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import get_db, close_db
from analytics.tracker import Analytics, get_portfolio_stats

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/pnl")
def get_pnl(wallet_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Get profit and loss data"""
    try:
        analytics = Analytics()
        return analytics.calculate_pnl(wallet_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        close_db(db)

@router.get("/win-rate")
def get_win_rate(wallet_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Get win rate percentage"""
    try:
        analytics = Analytics()
        return {"win_rate": analytics.get_win_rate(wallet_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        close_db(db)

@router.get("/stats")
def get_stats(wallet_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Get comprehensive trade statistics"""
    try:
        analytics = Analytics()
        return analytics.get_trade_stats(wallet_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        close_db(db)

@router.get("/history")
def get_pnl_history(
    wallet_id: Optional[int] = None,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get PnL history over time"""
    try:
        analytics = Analytics()
        return analytics.get_pnl_history(wallet_id, days)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        close_db(db)

@router.get("/tokens")
def get_token_performance(
    wallet_id: Optional[int] = None,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get top/bottom performing tokens"""
    try:
        analytics = Analytics()
        return analytics.get_token_performance(wallet_id, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        close_db(db)

@router.get("/strategies")
def get_strategy_performance(
    wallet_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get performance by strategy"""
    try:
        analytics = Analytics()
        return analytics.get_strategy_performance(wallet_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        close_db(db)

@router.get("/portfolio")
def get_portfolio(wallet_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Get complete portfolio statistics"""
    try:
        return get_portfolio_stats(wallet_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        close_db(db)
