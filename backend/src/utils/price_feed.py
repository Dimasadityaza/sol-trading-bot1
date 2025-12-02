"""
Price Feed Utility
Fetch real-time cryptocurrency prices from various sources
"""
import httpx
import asyncio
from typing import Optional, Dict
from datetime import datetime, timedelta

class PriceFeed:
    """Fetch real-time crypto prices"""

    def __init__(self):
        self.cache: Dict[str, tuple[float, datetime]] = {}
        self.cache_duration = timedelta(seconds=30)  # Cache for 30 seconds

    async def get_sol_price_usd(self) -> Optional[float]:
        """
        Get SOL price in USD with caching

        Returns:
            SOL price in USD or None if failed
        """
        # Check cache first
        if 'SOL' in self.cache:
            price, timestamp = self.cache['SOL']
            if datetime.utcnow() - timestamp < self.cache_duration:
                return price

        # Try Jupiter Price API first (fastest)
        price = await self._get_sol_price_jupiter()
        if price:
            self.cache['SOL'] = (price, datetime.utcnow())
            return price

        # Fallback to CoinGecko
        price = await self._get_sol_price_coingecko()
        if price:
            self.cache['SOL'] = (price, datetime.utcnow())
            return price

        # Return cached value if available (even if expired)
        if 'SOL' in self.cache:
            price, _ = self.cache['SOL']
            print("⚠️ Using cached SOL price (stale)")
            return price

        return None

    async def _get_sol_price_jupiter(self) -> Optional[float]:
        """Get SOL price from Jupiter Price API"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                # Jupiter Price API v2
                response = await client.get(
                    "https://price.jup.ag/v4/price",
                    params={"ids": "So11111111111111111111111111111111111111112"}
                )

                if response.status_code == 200:
                    data = response.json()
                    sol_data = data.get("data", {}).get("So11111111111111111111111111111111111111112")

                    if sol_data and 'price' in sol_data:
                        price = float(sol_data['price'])
                        print(f"💰 SOL Price (Jupiter): ${price:.2f}")
                        return price

        except Exception as e:
            print(f"Jupiter price fetch failed: {e}")

        return None

    async def _get_sol_price_coingecko(self) -> Optional[float]:
        """Get SOL price from CoinGecko API (fallback)"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    "https://api.coingecko.com/api/v3/simple/price",
                    params={"ids": "solana", "vs_currencies": "usd"}
                )

                if response.status_code == 200:
                    data = response.json()
                    price = data.get("solana", {}).get("usd")

                    if price:
                        price = float(price)
                        print(f"💰 SOL Price (CoinGecko): ${price:.2f}")
                        return price

        except Exception as e:
            print(f"CoinGecko price fetch failed: {e}")

        return None

    def sol_to_usd(self, sol_amount: float, sol_price: float) -> float:
        """Convert SOL amount to USD"""
        return sol_amount * sol_price

    async def get_token_price_usd(self, token_address: str) -> Optional[float]:
        """
        Get any token price in USD via Jupiter

        Args:
            token_address: Token mint address

        Returns:
            Token price in USD or None
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    "https://price.jup.ag/v4/price",
                    params={"ids": token_address}
                )

                if response.status_code == 200:
                    data = response.json()
                    token_data = data.get("data", {}).get(token_address)

                    if token_data and 'price' in token_data:
                        return float(token_data['price'])

        except Exception as e:
            print(f"Token price fetch failed: {e}")

        return None


# Singleton instance
_price_feed = None

def get_price_feed() -> PriceFeed:
    """Get PriceFeed singleton instance"""
    global _price_feed
    if _price_feed is None:
        _price_feed = PriceFeed()
    return _price_feed
