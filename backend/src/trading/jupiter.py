import httpx
from typing import Optional, Dict, Any
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.transaction import Transaction
from solana.rpc.api import Client
from solana.rpc.commitment import Confirmed
import base64
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import RPC_ENDPOINT

JUPITER_API = "https://quote-api.jup.ag/v6"
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
SOL_MINT = "So11111111111111111111111111111111111111112"

class JupiterClient:
    def __init__(self):
        self.api_url = JUPITER_API
        self.client = Client(RPC_ENDPOINT)
    
    async def get_quote(
        self,
        input_mint: str,
        output_mint: str,
        amount: int,
        slippage_bps: int = 50  # 0.5% default
    ) -> Optional[Dict[str, Any]]:
        """
        Get swap quote from Jupiter
        
        Args:
            input_mint: Input token mint address
            output_mint: Output token mint address
            amount: Amount in smallest unit (lamports for SOL)
            slippage_bps: Slippage in basis points (50 = 0.5%)
        
        Returns:
            Quote data or None if failed
        """
        try:
            async with httpx.AsyncClient() as client:
                params = {
                    "inputMint": input_mint,
                    "outputMint": output_mint,
                    "amount": str(amount),
                    "slippageBps": slippage_bps,
                }
                
                response = await client.get(f"{self.api_url}/quote", params=params)
                response.raise_for_status()
                
                return response.json()
        except Exception as e:
            print(f"Error getting quote: {e}")
            return None
    
    async def get_swap_transaction(
        self,
        quote: Dict[str, Any],
        user_public_key: str,
        wrap_unwrap_sol: bool = True
    ) -> Optional[str]:
        """
        Get swap transaction from Jupiter
        
        Args:
            quote: Quote data from get_quote
            user_public_key: User's wallet public key
            wrap_unwrap_sol: Whether to wrap/unwrap SOL
        
        Returns:
            Serialized transaction or None if failed
        """
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "quoteResponse": quote,
                    "userPublicKey": user_public_key,
                    "wrapAndUnwrapSol": wrap_unwrap_sol,
                }
                
                response = await client.post(
                    f"{self.api_url}/swap",
                    json=payload
                )
                response.raise_for_status()
                
                data = response.json()
                return data.get("swapTransaction")
        except Exception as e:
            print(f"Error getting swap transaction: {e}")
            return None
    
    def execute_swap(
        self,
        keypair: Keypair,
        swap_transaction: str,
        max_retries: int = 3
    ) -> Optional[str]:
        """
        Execute swap transaction
        
        Args:
            keypair: User's keypair
            swap_transaction: Serialized transaction from Jupiter
            max_retries: Maximum number of retries
        
        Returns:
            Transaction signature or None if failed
        """
        try:
            # Decode transaction
            transaction_bytes = base64.b64decode(swap_transaction)
            transaction = Transaction.from_bytes(transaction_bytes)
            
            # Sign transaction
            transaction.sign(keypair)
            
            # Send transaction
            opts = {"skip_preflight": False, "preflight_commitment": Confirmed}
            
            for attempt in range(max_retries):
                try:
                    result = self.client.send_raw_transaction(
                        bytes(transaction),
                        opts=opts
                    )
                    
                    if result.value:
                        signature = str(result.value)
                        print(f"Transaction sent: {signature}")
                        
                        # Wait for confirmation
                        self.client.confirm_transaction(result.value, commitment=Confirmed)
                        return signature
                except Exception as e:
                    print(f"Attempt {attempt + 1} failed: {e}")
                    if attempt == max_retries - 1:
                        raise
            
            return None
        except Exception as e:
            print(f"Error executing swap: {e}")
            return None
    
    async def swap(
        self,
        keypair: Keypair,
        input_mint: str,
        output_mint: str,
        amount: int,
        slippage_bps: int = 50
    ) -> Optional[str]:
        """
        Complete swap operation
        
        Args:
            keypair: User's keypair
            input_mint: Input token mint
            output_mint: Output token mint
            amount: Amount to swap
            slippage_bps: Slippage tolerance
        
        Returns:
            Transaction signature or None
        """
        # Get quote
        quote = await self.get_quote(input_mint, output_mint, amount, slippage_bps)
        if not quote:
            print("Failed to get quote")
            return None
        
        # Get swap transaction
        swap_tx = await self.get_swap_transaction(
            quote,
            str(keypair.pubkey()),
            wrap_unwrap_sol=True
        )
        if not swap_tx:
            print("Failed to get swap transaction")
            return None
        
        # Execute swap
        signature = self.execute_swap(keypair, swap_tx)
        return signature

# Helper functions
async def buy_token(
    keypair: Keypair,
    token_address: str,
    sol_amount: float,
    slippage_percent: float = 1.0
) -> Optional[str]:
    """
    Buy token with SOL
    
    Args:
        keypair: User's keypair
        token_address: Token to buy
        sol_amount: Amount of SOL to spend
        slippage_percent: Slippage tolerance (1.0 = 1%)
    
    Returns:
        Transaction signature or None
    """
    jupiter = JupiterClient()
    
    # Convert SOL to lamports
    amount_lamports = int(sol_amount * 1e9)
    
    # Convert slippage to basis points
    slippage_bps = int(slippage_percent * 100)
    
    return await jupiter.swap(
        keypair=keypair,
        input_mint=SOL_MINT,
        output_mint=token_address,
        amount=amount_lamports,
        slippage_bps=slippage_bps
    )

async def sell_token(
    keypair: Keypair,
    token_address: str,
    token_amount: int,
    slippage_percent: float = 1.0
) -> Optional[str]:
    """
    Sell token for SOL
    
    Args:
        keypair: User's keypair
        token_address: Token to sell
        token_amount: Amount of tokens (in smallest unit)
        slippage_percent: Slippage tolerance
    
    Returns:
        Transaction signature or None
    """
    jupiter = JupiterClient()
    
    slippage_bps = int(slippage_percent * 100)
    
    return await jupiter.swap(
        keypair=keypair,
        input_mint=token_address,
        output_mint=SOL_MINT,
        amount=token_amount,
        slippage_bps=slippage_bps
    )
