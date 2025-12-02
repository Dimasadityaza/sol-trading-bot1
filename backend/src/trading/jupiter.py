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
    
    async def execute_swap(
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

            # Parse transaction (handle versioned transactions)
            try:
                transaction = Transaction.from_bytes(transaction_bytes)
            except Exception as parse_error:
                print(f"Error parsing transaction: {parse_error}")
                print(f"Transaction bytes length: {len(transaction_bytes)}")
                raise ValueError(f"Failed to parse transaction: {parse_error}")

            # Sign transaction
            try:
                transaction.sign([keypair])
            except AttributeError:
                # Fallback for older solders version
                transaction.sign(keypair)
            except Exception as sign_error:
                print(f"Error signing transaction: {sign_error}")
                raise ValueError(f"Failed to sign transaction: {sign_error}")

            # Send transaction
            opts = {"skip_preflight": False, "preflight_commitment": Confirmed}

            for attempt in range(max_retries):
                try:
                    print(f"Sending transaction (attempt {attempt + 1}/{max_retries})...")

                    # Get raw transaction bytes
                    raw_tx = bytes(transaction)
                    print(f"Transaction size: {len(raw_tx)} bytes")

                    result = self.client.send_raw_transaction(
                        raw_tx,
                        opts=opts
                    )

                    if result.value:
                        signature = str(result.value)
                        print(f"✅ Transaction sent successfully: {signature}")

                        # Wait for confirmation
                        print(f"Waiting for confirmation...")
                        self.client.confirm_transaction(result.value, commitment=Confirmed)
                        print(f"✅ Transaction confirmed!")
                        return signature
                    else:
                        error_msg = "Transaction failed with no signature returned"
                        print(f"❌ {error_msg}")
                        if hasattr(result, 'error'):
                            print(f"Error details: {result.error}")

                except Exception as e:
                    error_msg = str(e)
                    print(f"❌ Attempt {attempt + 1} failed: {error_msg}")

                    # If this is the last attempt, raise the error
                    if attempt == max_retries - 1:
                        raise ValueError(f"Transaction failed after {max_retries} attempts: {error_msg}")

                    # Wait before retry
                    import asyncio
                    await asyncio.sleep(2)

            return None

        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error executing swap: {error_msg}")
            import traceback
            print(f"Full traceback:\n{traceback.format_exc()}")
            raise Exception(f"Swap execution failed: {error_msg}")
    
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
        try:
            print(f"🔄 Starting swap: {amount} from {input_mint[:8]}... to {output_mint[:8]}...")
            print(f"📊 Slippage: {slippage_bps} bps ({slippage_bps/100}%)")

            # Get quote
            print("1️⃣ Getting quote from Jupiter...")
            quote = await self.get_quote(input_mint, output_mint, amount, slippage_bps)
            if not quote:
                raise Exception("Failed to get quote from Jupiter API")

            print(f"✅ Quote received")
            if 'outAmount' in quote:
                print(f"   Expected output: {quote['outAmount']}")

            # Get swap transaction
            print("2️⃣ Building swap transaction...")
            swap_tx = await self.get_swap_transaction(
                quote,
                str(keypair.pubkey()),
                wrap_unwrap_sol=True
            )
            if not swap_tx:
                raise Exception("Failed to get swap transaction from Jupiter API")

            print(f"✅ Swap transaction built")

            # Execute swap (FIXED: Added await!)
            print("3️⃣ Executing swap transaction...")
            signature = await self.execute_swap(keypair, swap_tx)

            if signature:
                print(f"✅ Swap completed successfully!")
                print(f"🔗 Signature: {signature}")

            return signature

        except Exception as e:
            error_msg = str(e)
            print(f"❌ Swap failed: {error_msg}")
            import traceback
            print(f"Full traceback:\n{traceback.format_exc()}")
            raise Exception(f"Swap operation failed: {error_msg}")

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
