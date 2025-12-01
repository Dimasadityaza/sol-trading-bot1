import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from monitoring.pool_monitor import MultiPlatformMonitor
from monitoring.token_analyzer import TokenAnalyzer
from trading.executor import TradeExecutor
from core.database import get_db, close_db, SniperConfig, Trade
from solders.keypair import Keypair

class SniperBot:
    """Automated token sniper bot"""
    
    def __init__(self, wallet_id: int, keypair: Keypair, config: Optional[Dict[str, Any]] = None):
        self.wallet_id = wallet_id
        self.keypair = keypair
        self.config = config or {}
        self.is_running = False
        self.monitor = None
        self.analyzer = TokenAnalyzer()
        self.executor = TradeExecutor(wallet_id, keypair)
        self.db = get_db()
        
        # Default config
        self.buy_amount = self.config.get("buy_amount", 0.1)
        self.slippage = self.config.get("slippage", 5.0)
        self.min_liquidity = self.config.get("min_liquidity", 5.0)
        self.min_safety_score = self.config.get("min_safety_score", 70)
        self.require_mint_renounced = self.config.get("require_mint_renounced", True)
        self.require_freeze_renounced = self.config.get("require_freeze_renounced", True)
        self.max_buy_tax = self.config.get("max_buy_tax", 10.0)
        
        # Tracking
        self.pools_detected = 0
        self.tokens_bought = 0
        self.tokens_skipped = 0
    
    async def on_new_pool(self, pool_data: Dict[str, Any]):
        """Handle new pool detection"""
        self.pools_detected += 1
        
        token_address = pool_data.get("token_address")
        liquidity = pool_data.get("liquidity", 0)
        
        print(f"\n🎯 New pool detected #{self.pools_detected}")
        print(f"   Token: {pool_data.get('token_symbol', 'Unknown')}")
        print(f"   Address: {token_address}")
        print(f"   Liquidity: {liquidity} SOL")
        
        # Check liquidity requirement
        if liquidity < self.min_liquidity:
            print(f"   ✗ Skipped: Liquidity too low ({liquidity} < {self.min_liquidity})")
            self.tokens_skipped += 1
            return
        
        # Analyze token safety
        print(f"   🔍 Analyzing token safety...")
        try:
            analysis = self.analyzer.analyze_token(token_address)
            safety_score = analysis["safety_score"]
            
            print(f"   Safety Score: {safety_score}/100")
            
            # Check safety requirements
            if self.require_mint_renounced and not analysis["mint_renounced"]:
                print(f"   ✗ Skipped: Mint authority not renounced")
                self.tokens_skipped += 1
                return
            
            if self.require_freeze_renounced and not analysis["freeze_renounced"]:
                print(f"   ✗ Skipped: Freeze authority not renounced")
                self.tokens_skipped += 1
                return
            
            if safety_score < self.min_safety_score:
                print(f"   ✗ Skipped: Safety score too low ({safety_score} < {self.min_safety_score})")
                self.tokens_skipped += 1
                return
            
            # All checks passed - execute buy
            print(f"   ✓ All safety checks passed!")
            print(f"   💰 Executing buy: {self.buy_amount} SOL")
            
            result = await self.executor.execute_buy(
                token_address=token_address,
                sol_amount=self.buy_amount,
                slippage=self.slippage,
                strategy="snipe"
            )
            
            if result["success"]:
                self.tokens_bought += 1
                print(f"   ✅ Buy successful!")
                print(f"   Signature: {result['signature']}")
                print(f"   Explorer: {result['explorer_url']}")
            else:
                print(f"   ✗ Buy failed: {result.get('error')}")
                self.tokens_skipped += 1
        
        except Exception as e:
            print(f"   ✗ Error: {e}")
            self.tokens_skipped += 1
    
    async def start(self, platforms: list = None):
        """Start the sniper bot"""
        print("="*60)
        print("🎯 SNIPER BOT STARTING")
        print("="*60)
        print(f"Wallet ID: {self.wallet_id}")
        print(f"Buy Amount: {self.buy_amount} SOL")
        print(f"Min Liquidity: {self.min_liquidity} SOL")
        print(f"Min Safety Score: {self.min_safety_score}/100")
        print(f"Require Mint Renounced: {self.require_mint_renounced}")
        print(f"Require Freeze Renounced: {self.require_freeze_renounced}")
        print("="*60)
        
        self.is_running = True
        
        # Start monitoring
        platforms = platforms or ["raydium", "pumpfun", "orca"]
        self.monitor = MultiPlatformMonitor(platforms)
        
        try:
            await self.monitor.start(self.on_new_pool)
        except KeyboardInterrupt:
            await self.stop()
    
    async def stop(self):
        """Stop the sniper bot"""
        print("\n" + "="*60)
        print("🛑 STOPPING SNIPER BOT")
        print("="*60)
        print(f"Pools Detected: {self.pools_detected}")
        print(f"Tokens Bought: {self.tokens_bought}")
        print(f"Tokens Skipped: {self.tokens_skipped}")
        print("="*60)
        
        self.is_running = False
        
        if self.monitor:
            await self.monitor.stop()
        
        close_db(self.db)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get sniper statistics"""
        return {
            "is_running": self.is_running,
            "pools_detected": self.pools_detected,
            "tokens_bought": self.tokens_bought,
            "tokens_skipped": self.tokens_skipped,
            "success_rate": (self.tokens_bought / self.pools_detected * 100) if self.pools_detected > 0 else 0
        }

# Sniper manager for API
class SniperManager:
    """Manage sniper bot instances"""
    
    _instance = None
    _sniper = None
    _task = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def is_running(self) -> bool:
        """Check if sniper is running"""
        return self._sniper is not None and self._sniper.is_running
    
    async def start(self, wallet_id: int, keypair: Keypair, config: Dict[str, Any]):
        """Start sniper bot"""
        if self.is_running():
            raise Exception("Sniper already running")
        
        self._sniper = SniperBot(wallet_id, keypair, config)
        self._task = asyncio.create_task(self._sniper.start())
        
        # Give it a moment to start
        await asyncio.sleep(0.5)
        
        return {"status": "started", "message": "Sniper bot started successfully"}
    
    async def stop(self):
        """Stop sniper bot"""
        if not self.is_running():
            raise Exception("Sniper not running")
        
        await self._sniper.stop()
        
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        
        stats = self._sniper.get_stats()
        self._sniper = None
        self._task = None
        
        return {"status": "stopped", "stats": stats}
    
    def get_status(self) -> Dict[str, Any]:
        """Get sniper status"""
        if not self._sniper:
            return {"is_running": False}
        
        return self._sniper.get_stats()
