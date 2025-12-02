import asyncio
import websockets
import json
from typing import Callable, Optional, Dict, Any
from datetime import datetime
import sys
import os
import base64
from solana.rpc.api import Client

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import WS_ENDPOINT, RPC_ENDPOINT

# DEX Program IDs
RAYDIUM_V4 = "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8"
RAYDIUM_AMM = "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1"
ORCA_WHIRLPOOL = "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc"
PUMPFUN = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"

class PoolMonitor:
    """Monitor new liquidity pools on Solana DEXs"""

    def __init__(self, platform: str = "raydium"):
        self.platform = platform
        self.ws_url = WS_ENDPOINT
        self.rpc_client = Client(RPC_ENDPOINT)
        self.is_running = False
        self.on_new_pool: Optional[Callable] = None
        self.websocket = None
        self.program_id = self._get_program_id()

    def _get_program_id(self) -> str:
        """Get program ID for platform"""
        if self.platform == "raydium":
            return RAYDIUM_V4
        elif self.platform == "orca":
            return ORCA_WHIRLPOOL
        elif self.platform == "pumpfun":
            return PUMPFUN
        else:
            return RAYDIUM_V4  # Default

    async def connect(self):
        """Connect to WebSocket"""
        try:
            self.websocket = await websockets.connect(self.ws_url)
            self.is_running = True
            print(f"✓ Connected to {self.platform} pool monitor")
            return True
        except Exception as e:
            print(f"✗ Failed to connect: {e}")
            return False
    
    async def subscribe_to_pools(self):
        """Subscribe to new pool events via logs subscription"""
        if not self.websocket:
            print("Not connected to WebSocket")
            return

        # Subscribe to program logs for DEX transactions
        subscription = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "logsSubscribe",
            "params": [
                {
                    "mentions": [self.program_id]
                },
                {
                    "commitment": "confirmed"  # Use confirmed for faster detection
                }
            ]
        }

        try:
            await self.websocket.send(json.dumps(subscription))
            print(f"✓ Subscribed to {self.platform} program logs (Program: {self.program_id})")
        except Exception as e:
            print(f"✗ Subscription failed: {e}")
    
    async def listen(self):
        """Listen for new pool events"""
        if not self.websocket:
            print("Not connected")
            return
        
        print(f"👂 Listening for new {self.platform} pools...")
        
        try:
            async for message in self.websocket:
                if not self.is_running:
                    break
                
                try:
                    data = json.loads(message)
                    
                    # Parse pool data
                    # In production, you'd properly parse the account data
                    # For now, create mock pool data
                    if "result" in data or "params" in data:
                        pool_data = self._parse_pool_data(data)
                        
                        if pool_data and self.on_new_pool:
                            await self.on_new_pool(pool_data)
                
                except json.JSONDecodeError:
                    continue
                except Exception as e:
                    print(f"Error processing message: {e}")
        
        except websockets.exceptions.ConnectionClosed:
            print("WebSocket connection closed")
            self.is_running = False
        except Exception as e:
            print(f"Error listening: {e}")
            self.is_running = False
    
    def _parse_pool_data(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse pool data from WebSocket log message

        Real implementation would:
        1. Detect 'initialize' or pool creation logs
        2. Extract transaction signature
        3. Fetch full transaction via RPC
        4. Parse account data to get token addresses, liquidity, etc.

        For now: Returns data when we detect pool-related logs
        """
        try:
            # Check if this is a notification with logs
            if "params" not in data or "result" not in data["params"]:
                return None

            result = data["params"]["result"]
            logs = result.get("value", {}).get("logs", [])
            signature = result.get("value", {}).get("signature", "")

            # Check for pool initialization keywords in logs
            pool_keywords = ["initialize", "InitializePool", "CreatePool", "init_pool"]
            is_pool_creation = any(
                any(keyword.lower() in log.lower() for keyword in pool_keywords)
                for log in logs
            )

            if not is_pool_creation or not signature:
                return None

            # In production, you would:
            # 1. Fetch transaction details: self.rpc_client.get_transaction(signature)
            # 2. Parse account keys to find token mints
            # 3. Extract pool address
            # 4. Calculate liquidity from account balances
            # 5. Fetch token metadata

            # For demo: Return detected pool with signature
            print(f"   🎯 Pool creation detected! Signature: {signature[:16]}...")

            # Extract basic info from logs (simplified)
            return {
                "platform": self.platform,
                "signature": signature,
                "pool_address": f"{self.platform}_pool_{signature[:8]}",
                "token_address": f"Token_{signature[8:16]}",
                "liquidity": 0,  # Would calculate from transaction
                "token_symbol": "NEW",
                "token_name": "New Token",
                "creator": "Unknown",
                "timestamp": datetime.utcnow().isoformat(),
                "logs": logs[:5]  # First 5 logs for debugging
            }

        except Exception as e:
            print(f"   Error parsing pool data: {e}")
            return None
    
    async def disconnect(self):
        """Disconnect from WebSocket"""
        self.is_running = False
        if self.websocket:
            await self.websocket.close()
            print(f"✓ Disconnected from {self.platform} monitor")
    
    async def start(self, on_new_pool: Callable):
        """Start monitoring pools"""
        self.on_new_pool = on_new_pool
        
        if await self.connect():
            await self.subscribe_to_pools()
            await self.listen()

# Convenience class for multi-platform monitoring
class MultiPlatformMonitor:
    """Monitor multiple DEX platforms simultaneously"""
    
    def __init__(self, platforms: list = None):
        self.platforms = platforms or ["raydium", "orca", "pumpfun"]
        self.monitors = {}
        self.is_running = False
    
    async def start(self, on_new_pool: Callable):
        """Start monitoring all platforms"""
        self.is_running = True
        
        tasks = []
        for platform in self.platforms:
            monitor = PoolMonitor(platform)
            self.monitors[platform] = monitor
            tasks.append(asyncio.create_task(monitor.start(on_new_pool)))
        
        await asyncio.gather(*tasks)
    
    async def stop(self):
        """Stop all monitors"""
        self.is_running = False
        for monitor in self.monitors.values():
            await monitor.disconnect()

# Example usage
async def example_handler(pool_data: Dict[str, Any]):
    """Example handler for new pools"""
    print(f"🎯 New pool detected!")
    print(f"   Platform: {pool_data['platform']}")
    print(f"   Token: {pool_data['token_symbol']}")
    print(f"   Liquidity: {pool_data['liquidity']} SOL")
    print(f"   Address: {pool_data['token_address']}")

if __name__ == "__main__":
    # Test the monitor
    async def test():
        monitor = PoolMonitor("raydium")
        await monitor.start(example_handler)
    
    asyncio.run(test())
