from typing import Optional, Dict, Any
from solders.keypair import Keypair
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trading.jupiter import buy_token, sell_token
from core.database import Trade, get_db, close_db
from core.wallet import get_balance

class TradeExecutor:
    """Execute buy and sell trades"""
    
    def __init__(self, wallet_id: int, keypair: Keypair):
        self.wallet_id = wallet_id
        self.keypair = keypair
        self.db = get_db()
    
    async def execute_buy(
        self,
        token_address: str,
        sol_amount: float,
        slippage: float = 1.0,
        strategy: str = "manual"
    ) -> Dict[str, Any]:
        """
        Execute buy trade
        
        Args:
            token_address: Token to buy
            sol_amount: SOL amount to spend
            slippage: Slippage tolerance (%)
            strategy: Trade strategy (manual, snipe, copy)
        
        Returns:
            Trade result with signature and details
        """
        try:
            # Check balance
            balance = get_balance(str(self.keypair.pubkey()))
            if balance < sol_amount:
                return {
                    "success": False,
                    "error": f"Insufficient balance. Have {balance} SOL, need {sol_amount} SOL"
                }
            
            # Execute buy
            signature = await buy_token(
                keypair=self.keypair,
                token_address=token_address,
                sol_amount=sol_amount,
                slippage_percent=slippage
            )
            
            if not signature:
                return {
                    "success": False,
                    "error": "Failed to execute buy transaction"
                }
            
            # Save to database
            trade = Trade(
                wallet_id=self.wallet_id,
                token_address=token_address,
                trade_type="buy",
                amount=0,  # Will be updated when we parse transaction
                price=0,   # Will be calculated
                cost=sol_amount,
                signature=signature,
                timestamp=datetime.utcnow(),
                strategy=strategy
            )
            
            self.db.add(trade)
            self.db.commit()
            self.db.refresh(trade)
            
            return {
                "success": True,
                "signature": signature,
                "trade_id": trade.id,
                "token_address": token_address,
                "sol_amount": sol_amount,
                "explorer_url": f"https://solscan.io/tx/{signature}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def execute_sell(
        self,
        token_address: str,
        percentage: float = 100.0,
        slippage: float = 1.0,
        strategy: str = "manual"
    ) -> Dict[str, Any]:
        """
        Execute sell trade
        
        Args:
            token_address: Token to sell
            percentage: Percentage of holdings to sell (1-100)
            slippage: Slippage tolerance (%)
            strategy: Trade strategy
        
        Returns:
            Trade result
        """
        try:
            # For now, we'll use a placeholder for token amount
            # In production, you'd query token accounts to get actual balance
            token_amount = 1000000  # Placeholder
            
            # Calculate amount to sell based on percentage
            sell_amount = int(token_amount * (percentage / 100))
            
            if sell_amount <= 0:
                return {
                    "success": False,
                    "error": "No tokens to sell"
                }
            
            # Execute sell
            signature = await sell_token(
                keypair=self.keypair,
                token_address=token_address,
                token_amount=sell_amount,
                slippage_percent=slippage
            )
            
            if not signature:
                return {
                    "success": False,
                    "error": "Failed to execute sell transaction"
                }
            
            # Save to database
            trade = Trade(
                wallet_id=self.wallet_id,
                token_address=token_address,
                trade_type="sell",
                amount=sell_amount,
                price=0,
                revenue=0,  # Will be updated
                signature=signature,
                timestamp=datetime.utcnow(),
                strategy=strategy
            )
            
            self.db.add(trade)
            self.db.commit()
            self.db.refresh(trade)
            
            return {
                "success": True,
                "signature": signature,
                "trade_id": trade.id,
                "token_address": token_address,
                "percentage": percentage,
                "explorer_url": f"https://solscan.io/tx/{signature}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def __del__(self):
        """Cleanup database connection"""
        try:
            close_db(self.db)
        except:
            pass

# Helper functions
async def quick_buy(
    wallet_id: int,
    keypair: Keypair,
    token_address: str,
    sol_amount: float,
    slippage: float = 1.0
) -> Dict[str, Any]:
    """Quick buy function"""
    executor = TradeExecutor(wallet_id, keypair)
    return await executor.execute_buy(token_address, sol_amount, slippage)

async def quick_sell(
    wallet_id: int,
    keypair: Keypair,
    token_address: str,
    percentage: float = 100.0,
    slippage: float = 1.0
) -> Dict[str, Any]:
    """Quick sell function"""
    executor = TradeExecutor(wallet_id, keypair)
    return await executor.execute_sell(token_address, percentage, slippage)
