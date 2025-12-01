from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy import func
import sys
import os
import csv
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import get_db, close_db, Trade, Wallet

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

    def export_to_csv(
        self,
        wallet_id: Optional[int] = None,
        filepath: str = "trades_export.csv"
    ) -> str:
        """
        Export trades to CSV file

        Args:
            wallet_id: Optional wallet ID to filter trades
            filepath: Path to save the CSV file

        Returns:
            Path to the exported file
        """
        query = self.db.query(Trade)

        if wallet_id:
            query = query.filter(Trade.wallet_id == wallet_id)

        trades = query.order_by(Trade.timestamp.desc()).all()

        # Write to CSV
        with open(filepath, 'w', newline='') as csvfile:
            fieldnames = [
                'id', 'wallet_id', 'token_address', 'trade_type',
                'amount', 'price', 'cost', 'revenue', 'pnl',
                'signature', 'timestamp', 'strategy'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for trade in trades:
                writer.writerow({
                    'id': trade.id,
                    'wallet_id': trade.wallet_id,
                    'token_address': trade.token_address,
                    'trade_type': trade.trade_type,
                    'amount': trade.amount,
                    'price': trade.price,
                    'cost': trade.cost,
                    'revenue': trade.revenue,
                    'pnl': trade.pnl,
                    'signature': trade.signature,
                    'timestamp': trade.timestamp,
                    'strategy': trade.strategy
                })

        return filepath

    def export_to_json(
        self,
        wallet_id: Optional[int] = None,
        filepath: str = "trades_export.json"
    ) -> str:
        """
        Export trades and analytics to JSON file

        Args:
            wallet_id: Optional wallet ID to filter trades
            filepath: Path to save the JSON file

        Returns:
            Path to the exported file
        """
        query = self.db.query(Trade)

        if wallet_id:
            query = query.filter(Trade.wallet_id == wallet_id)

        trades = query.order_by(Trade.timestamp.desc()).all()

        # Build export data
        export_data = {
            "export_date": datetime.utcnow().isoformat(),
            "wallet_id": wallet_id,
            "summary": {
                "pnl": self.calculate_pnl(wallet_id),
                "win_rate": self.get_win_rate(wallet_id),
                "trade_stats": self.get_trade_stats(wallet_id),
                "top_tokens": self.get_token_performance(wallet_id, limit=10),
                "strategy_performance": self.get_strategy_performance(wallet_id)
            },
            "trades": [
                {
                    "id": t.id,
                    "wallet_id": t.wallet_id,
                    "token_address": t.token_address,
                    "trade_type": t.trade_type,
                    "amount": float(t.amount),
                    "price": float(t.price),
                    "cost": float(t.cost) if t.cost else None,
                    "revenue": float(t.revenue) if t.revenue else None,
                    "pnl": float(t.pnl) if t.pnl else None,
                    "signature": t.signature,
                    "timestamp": t.timestamp.isoformat(),
                    "strategy": t.strategy
                }
                for t in trades
            ]
        }

        # Write to JSON
        with open(filepath, 'w') as jsonfile:
            json.dump(export_data, jsonfile, indent=2)

        return filepath

    def get_group_analytics(self, group_id: int) -> Dict[str, Any]:
        """
        Get analytics for all wallets in a group

        Args:
            group_id: Wallet group ID

        Returns:
            Dictionary with group-level analytics
        """
        # Get all wallets in the group
        wallets = self.db.query(Wallet).filter(Wallet.group_id == group_id).all()
        wallet_ids = [w.id for w in wallets]

        if not wallet_ids:
            return {
                "group_id": group_id,
                "total_wallets": 0,
                "total_pnl": 0,
                "avg_win_rate": 0,
                "total_trades": 0
            }

        # Get all trades for the group
        all_trades = self.db.query(Trade).filter(
            Trade.wallet_id.in_(wallet_ids)
        ).all()

        # Calculate aggregate metrics
        total_pnl = sum([t.pnl or 0 for t in all_trades if t.pnl is not None])
        trades_with_pnl = [t for t in all_trades if t.pnl is not None]
        winning_trades = len([t for t in trades_with_pnl if t.pnl > 0])
        avg_win_rate = (winning_trades / len(trades_with_pnl) * 100) if trades_with_pnl else 0

        # Get per-wallet stats
        wallet_stats = []
        for wallet in wallets:
            wallet_trades = [t for t in all_trades if t.wallet_id == wallet.id]
            wallet_pnl = sum([t.pnl or 0 for t in wallet_trades if t.pnl is not None])

            wallet_stats.append({
                "wallet_id": wallet.id,
                "wallet_label": wallet.label,
                "address": wallet.public_key,
                "total_trades": len(wallet_trades),
                "pnl": wallet_pnl
            })

        return {
            "group_id": group_id,
            "total_wallets": len(wallets),
            "total_pnl": total_pnl,
            "avg_win_rate": avg_win_rate,
            "total_trades": len(all_trades),
            "wallet_stats": wallet_stats
        }

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
