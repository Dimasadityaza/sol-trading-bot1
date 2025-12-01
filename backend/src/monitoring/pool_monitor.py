import asyncio
import websockets
import json
from typing import Callable, Optional, Dict, Any
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import WS_ENDPOINT

class PoolMonitor:
    """Monitor new liquidity pools on Solana DEXs"""
    
    def __init__(self, platform: str = "raydium"):
        self.platform = platform
        self.ws_url = WS_ENDPOINT
        self.is_running = False
        self.on_new_pool: Optional[Callable] = None
        self.websocket = None
    
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
        """Subscribe to new pool events"""
        if not self.websocket:
            print("Not connected to WebSocket")
            return
        
        # Subscribe to account updates for Raydium/Orca/etc
        # This is a simplified version - in production you'd subscribe to specific program IDs
        subscription = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "programSubscribe",
            "params": [
                "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8",  # Raydium V4 program
                {
                    "encoding": "jsonParsed",
                    "commitment": "finalized"
                }
            ]
        }
        
        try:
            await self.websocket.send(json.dumps(subscription))
            print(f"✓ Subscribed to {self.platform} pools")
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
        """Parse pool data from WebSocket message"""
        # This is a mock parser - in production you'd parse actual Raydium/Orca data
        # For demo purposes, return mock data occasionally
        
        import random
        if random.random() < 0.1:  # 10% chance to simulate new pool
            return {
                "platform": self.platform,
                "token_address": f"Mock{random.randint(1000, 9999)}Token",
                "pool_address": f"Pool{random.randint(1000, 9999)}",
                "liquidity": random.uniform(1, 100),
                "token_symbol": f"TKN{random.randint(1, 999)}",
                "token_name": f"Test Token {random.randint(1, 999)}",
                "creator": f"Creator{random.randint(1, 100)}",
                "timestamp": datetime.utcnow().isoformat()
            }
        
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
