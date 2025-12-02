"""
Liquidity Pool Monitor
Monitors specific token addresses and auto-buys when liquidity is added
"""
import asyncio
import sys
import os
from typing import Optional, Dict, Any, List
from datetime import datetime
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solana.rpc.api import Client
from solana.rpc.websocket_api import connect
from solana.rpc.commitment import Confirmed

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import RPC_ENDPOINT, WS_ENDPOINT
from trading.executor import TradeExecutor
from monitoring.token_analyzer import TokenAnalyzer

# Raydium Pool Program IDs
RAYDIUM_POOL_PROGRAM = "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8"
RAYDIUM_AMM_PROGRAM = "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1"

# Orca Pool Program
ORCA_WHIRLPOOL_PROGRAM = "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc"

# Pumpfun
PUMPFUN_PROGRAM = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"


class LiquidityMonitor:
    """Monitor token for liquidity addition and auto-buy"""

    def __init__(self):
        self.client = Client(RPC_ENDPOINT)
        self.ws_endpoint = WS_ENDPOINT
        self.active_monitors: Dict[str, Dict[str, Any]] = {}
        self.monitor_tasks: Dict[str, asyncio.Task] = {}

    async def start_monitor(
        self,
        token_address: str,
        wallet_id: int,
        keypair: Keypair,
        sol_amount: float,
        slippage: float = 5.0,
        min_liquidity: float = 1.0,
        platforms: List[str] = None
    ) -> Dict[str, Any]:
        """
        Start monitoring a token for liquidity addition

        Args:
            token_address: Token mint address to monitor
            wallet_id: Wallet ID for trading
            keypair: Wallet keypair
            sol_amount: SOL amount to spend on auto-buy
            slippage: Slippage tolerance
            min_liquidity: Minimum liquidity required (SOL)
            platforms: Platforms to monitor (raydium, orca, pumpfun)

        Returns:
            Monitor status
        """
        if platforms is None:
            platforms = ["raydium", "pumpfun"]

        monitor_id = f"{token_address}_{wallet_id}"

        # Check if already monitoring
        if monitor_id in self.active_monitors:
            return {
                "success": False,
                "error": "Already monitoring this token with this wallet"
            }

        # Store monitor config
        self.active_monitors[monitor_id] = {
            "token_address": token_address,
            "wallet_id": wallet_id,
            "keypair": keypair,
            "sol_amount": sol_amount,
            "slippage": slippage,
            "min_liquidity": min_liquidity,
            "platforms": platforms,
            "status": "monitoring",
            "started_at": datetime.utcnow().isoformat(),
            "checks_performed": 0,
            "pool_detected": False
        }

        # Start monitoring task
        task = asyncio.create_task(
            self._monitor_loop(monitor_id)
        )
        self.monitor_tasks[monitor_id] = task

        print(f"✅ Started monitoring {token_address} for liquidity")
        print(f"   Wallet: {wallet_id}")
        print(f"   Auto-buy amount: {sol_amount} SOL")
        print(f"   Platforms: {', '.join(platforms)}")

        return {
            "success": True,
            "monitor_id": monitor_id,
            "token_address": token_address,
            "wallet_id": wallet_id,
            "config": {
                "sol_amount": sol_amount,
                "slippage": slippage,
                "min_liquidity": min_liquidity,
                "platforms": platforms
            }
        }

    async def _monitor_loop(self, monitor_id: str):
        """Main monitoring loop"""
        monitor = self.active_monitors.get(monitor_id)
        if not monitor:
            return

        token_address = monitor["token_address"]
        check_interval = 2  # Check every 2 seconds

        print(f"🔄 Monitor loop started for {token_address}")

        try:
            while monitor_id in self.active_monitors:
                monitor["checks_performed"] += 1

                # Check for liquidity pools
                pool_found = await self._check_liquidity_pools(monitor_id)

                if pool_found:
                    print(f"🎯 Pool detected for {token_address}!")
                    monitor["pool_detected"] = True
                    monitor["pool_detected_at"] = datetime.utcnow().isoformat()

                    # Execute auto-buy
                    await self._execute_auto_buy(monitor_id)

                    # Stop monitoring after successful buy
                    await self.stop_monitor(monitor_id)
                    break

                # Wait before next check
                await asyncio.sleep(check_interval)

        except Exception as e:
            print(f"❌ Error in monitor loop for {token_address}: {e}")
            monitor["status"] = "error"
            monitor["error"] = str(e)

    async def _check_liquidity_pools(self, monitor_id: str) -> bool:
        """Check if liquidity pool exists for token"""
        monitor = self.active_monitors.get(monitor_id)
        if not monitor:
            return False

        token_address = monitor["token_address"]
        platforms = monitor["platforms"]

        try:
            # Check Raydium
            if "raydium" in platforms:
                if await self._check_raydium_pool(token_address):
                    monitor["platform_detected"] = "raydium"
                    return True

            # Check Pumpfun
            if "pumpfun" in platforms:
                if await self._check_pumpfun_pool(token_address):
                    monitor["platform_detected"] = "pumpfun"
                    return True

            # Check Orca
            if "orca" in platforms:
                if await self._check_orca_pool(token_address):
                    monitor["platform_detected"] = "orca"
                    return True

            return False

        except Exception as e:
            print(f"Error checking pools: {e}")
            return False

    async def _check_raydium_pool(self, token_address: str) -> bool:
        """Check if Raydium pool exists"""
        try:
            # Check for token accounts associated with Raydium programs
            token_pubkey = Pubkey.from_string(token_address)

            # Get token accounts
            response = self.client.get_token_accounts_by_owner(
                token_pubkey,
                {"programId": Pubkey.from_string(RAYDIUM_AMM_PROGRAM)}
            )

            if response.value:
                print(f"✅ Raydium pool found for {token_address}")
                return True

            return False

        except Exception as e:
            # Might not exist yet, that's okay
            return False

    async def _check_pumpfun_pool(self, token_address: str) -> bool:
        """Check if Pumpfun pool exists"""
        try:
            # Simple check - try to get token account info
            token_pubkey = Pubkey.from_string(token_address)

            # Check if token has any activity
            response = self.client.get_account_info(token_pubkey)

            if response.value and response.value.lamports > 0:
                print(f"✅ Pumpfun pool/activity found for {token_address}")
                return True

            return False

        except Exception as e:
            return False

    async def _check_orca_pool(self, token_address: str) -> bool:
        """Check if Orca pool exists"""
        try:
            token_pubkey = Pubkey.from_string(token_address)

            response = self.client.get_token_accounts_by_owner(
                token_pubkey,
                {"programId": Pubkey.from_string(ORCA_WHIRLPOOL_PROGRAM)}
            )

            if response.value:
                print(f"✅ Orca pool found for {token_address}")
                return True

            return False

        except Exception as e:
            return False

    async def _execute_auto_buy(self, monitor_id: str):
        """Execute auto-buy when pool is detected"""
        monitor = self.active_monitors.get(monitor_id)
        if not monitor:
            return

        print(f"💰 Executing auto-buy for {monitor['token_address']}")

        try:
            executor = TradeExecutor(
                monitor["wallet_id"],
                monitor["keypair"]
            )

            result = await executor.execute_buy(
                token_address=monitor["token_address"],
                sol_amount=monitor["sol_amount"],
                slippage=monitor["slippage"],
                strategy="pre_launch_snipe"
            )

            monitor["buy_result"] = result
            monitor["status"] = "completed" if result.get("success") else "failed"

            if result.get("success"):
                print(f"✅ Auto-buy successful!")
                print(f"   Signature: {result.get('signature')}")
                print(f"   Explorer: {result.get('explorer_url')}")
            else:
                print(f"❌ Auto-buy failed: {result.get('error')}")

        except Exception as e:
            print(f"❌ Error executing auto-buy: {e}")
            monitor["status"] = "error"
            monitor["error"] = str(e)

    async def stop_monitor(self, monitor_id: str) -> Dict[str, Any]:
        """Stop monitoring a token"""
        if monitor_id not in self.active_monitors:
            return {
                "success": False,
                "error": "Monitor not found"
            }

        # Cancel task
        if monitor_id in self.monitor_tasks:
            self.monitor_tasks[monitor_id].cancel()
            del self.monitor_tasks[monitor_id]

        # Get final status
        monitor = self.active_monitors[monitor_id]
        del self.active_monitors[monitor_id]

        print(f"⏹️ Stopped monitoring {monitor['token_address']}")

        return {
            "success": True,
            "monitor_id": monitor_id,
            "final_status": monitor
        }

    def get_monitor_status(self, monitor_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific monitor"""
        return self.active_monitors.get(monitor_id)

    def list_active_monitors(self) -> List[Dict[str, Any]]:
        """List all active monitors"""
        return [
            {
                "monitor_id": mid,
                **monitor
            }
            for mid, monitor in self.active_monitors.items()
        ]


# Singleton instance
_liquidity_monitor = None

def get_liquidity_monitor() -> LiquidityMonitor:
    """Get LiquidityMonitor singleton instance"""
    global _liquidity_monitor
    if _liquidity_monitor is None:
        _liquidity_monitor = LiquidityMonitor()
    return _liquidity_monitor
