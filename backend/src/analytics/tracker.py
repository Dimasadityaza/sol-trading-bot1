from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy import func
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import get_db, close_db, Trade

class Analytics:
    """Trading analytics and PnL tracking"""
    
    def __init__(self):
        self.db = get_db()
    
    def calculate_pnl(self, wallet_id: Optional[int] = None) -> Dict[str, float]:
        """
        Calculate profit and loss
        
        Returns:
            Dict with total, realized, and unrealized PnL
        """
        query = self.db.query(Trade)
        
        if wallet_id:
            query = query.filter(Trade.wallet_id == wallet_id)
        
        trades = query.all()
        
        realized_pnl = sum([t.pnl or 0 for t in trades if t.pnl is not None])
        
        # Unrealized PnL would require current token prices
        # For now, set to 0
        unrealized_pnl = 0
        
        return {
            "total": realized_pnl + unrealized_pnl,
            "realized": realized_pnl,
            "unrealized": unrealized_pnl
        }
    
    def get_win_rate(self, wallet_id: Optional[int] = None) -> float:
        """Calculate win rate percentage"""
        query = self.db.query(Trade)
        
        if wallet_id:
            query = query.filter(Trade.wallet_id == wallet_id)
        
        trades = query.filter(Trade.pnl != None).all()
        
        if not trades:
            return 0.0
        
        winning_trades = len([t for t in trades if t.pnl > 0])
        total_trades = len(trades)
        
        return (winning_trades / total_trades * 100) if total_trades > 0 else 0
    
    def get_trade_stats(self, wallet_id: Optional[int] = None) -> Dict[str, Any]:
        """Get comprehensive trade statistics"""
        query = self.db.query(Trade)
        
        if wallet_id:
            query = query.filter(Trade.wallet_id == wallet_id)
        
        trades = query.all()
        
        if not trades:
            return {
                "total": 0,
                "wins": 0,
                "losses": 0,
                "avg_profit": 0,
                "avg_loss": 0,
                "best_trade": 0,
                "worst_trade": 0,
                "total_volume": 0
            }
        
        trades_with_pnl = [t for t in trades if t.pnl is not None]
        winning_trades = [t for t in trades_with_pnl if t.pnl > 0]
        losing_trades = [t for t in trades_with_pnl if t.pnl < 0]
        
        return {
            "total": len(trades),
            "wins": len(winning_trades),
            "losses": len(losing_trades),
            "avg_profit": sum([t.pnl for t in winning_trades]) / len(winning_trades) if winning_trades else 0,
            "avg_loss": sum([t.pnl for t in losing_trades]) / len(losing_trades) if losing_trades else 0,
            "best_trade": max([t.pnl for t in trades_with_pnl]) if trades_with_pnl else 0,
            "worst_trade": min([t.pnl for t in trades_with_pnl]) if trades_with_pnl else 0,
            "total_volume": sum([t.cost or 0 for t in trades])
        }
    
    def get_pnl_history(
        self,
        wallet_id: Optional[int] = None,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get PnL history over time"""
        query = self.db.query(Trade)
        
        if wallet_id:
            query = query.filter(Trade.wallet_id == wallet_id)
        
        # Get trades from last N days
        start_date = datetime.utcnow() - timedelta(days=days)
        query = query.filter(Trade.timestamp >= start_date)
        
        trades = query.order_by(Trade.timestamp).all()
        
        # Group by date
        daily_pnl = {}
        cumulative_pnl = 0
        
        for trade in trades:
            date = trade.timestamp.date().isoformat()
            pnl = trade.pnl or 0
            cumulative_pnl += pnl
            
            if date not in daily_pnl:
                daily_pnl[date] = {
                    "date": date,
                    "pnl": 0,
                    "cumulative_pnl": 0,
                    "trades": 0
                }
            
            daily_pnl[date]["pnl"] += pnl
            daily_pnl[date]["cumulative_pnl"] = cumulative_pnl
            daily_pnl[date]["trades"] += 1
        
        return list(daily_pnl.values())
    
    def get_token_performance(
        self,
        wallet_id: Optional[int] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get top/bottom performing tokens"""
        query = self.db.query(
            Trade.token_address,
            func.sum(Trade.pnl).label("total_pnl"),
            func.count(Trade.id).label("trade_count")
        )
        
        if wallet_id:
            query = query.filter(Trade.wallet_id == wallet_id)
        
        query = query.filter(Trade.pnl != None)
        query = query.group_by(Trade.token_address)
        query = query.order_by(func.sum(Trade.pnl).desc())
        
        results = query.limit(limit).all()
        
        return [{
            "token_address": r.token_address,
            "total_pnl": float(r.total_pnl or 0),
            "trade_count": r.trade_count
        } for r in results]
    
    def get_strategy_performance(
        self,
        wallet_id: Optional[int] = None
    ) -> Dict[str, Dict[str, Any]]:
        """Compare performance by strategy"""
        query = self.db.query(Trade)
        
        if wallet_id:
            query = query.filter(Trade.wallet_id == wallet_id)
        
        trades = query.all()
        
        strategies = {}
        
        for trade in trades:
            strategy = trade.strategy or "manual"
            
            if strategy not in strategies:
                strategies[strategy] = {
                    "total_trades": 0,
                    "total_pnl": 0,
                    "wins": 0,
                    "losses": 0
                }
            
            strategies[strategy]["total_trades"] += 1
            
            if trade.pnl is not None:
                strategies[strategy]["total_pnl"] += trade.pnl
                if trade.pnl > 0:
                    strategies[strategy]["wins"] += 1
                elif trade.pnl < 0:
                    strategies[strategy]["losses"] += 1
        
        # Calculate win rates
        for strategy in strategies.values():
            total = strategy["wins"] + strategy["losses"]
            strategy["win_rate"] = (strategy["wins"] / total * 100) if total > 0 else 0
        
        return strategies
    
    def __del__(self):
        """Cleanup"""
        try:
            close_db(self.db)
        except:
            pass

# Convenience functions
def get_portfolio_stats(wallet_id: Optional[int] = None) -> Dict[str, Any]:
    """Get complete portfolio statistics"""
    analytics = Analytics()
    
    return {
        "pnl": analytics.calculate_pnl(wallet_id),
        "win_rate": analytics.get_win_rate(wallet_id),
        "trade_stats": analytics.get_trade_stats(wallet_id),
        "top_tokens": analytics.get_token_performance(wallet_id, limit=5),
        "strategy_performance": analytics.get_strategy_performance(wallet_id)
    }
