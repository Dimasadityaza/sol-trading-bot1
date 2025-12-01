from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.api import Client
from mnemonic import Mnemonic
import base58
from typing import Tuple, Optional
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import RPC_ENDPOINT

class WalletManager:
    def __init__(self):
        self.client = Client(RPC_ENDPOINT)
        self.mnemo = Mnemonic("english")
    
    def generate_wallet(self) -> Tuple[str, Keypair]:
        """Generate new wallet with mnemonic"""
        # Generate mnemonic
        mnemonic = self.mnemo.generate(strength=128)
        
        # Generate keypair from mnemonic
        seed = self.mnemo.to_seed(mnemonic)
        keypair = Keypair.from_seed(seed[:32])
        
        return mnemonic, keypair
    
    def import_from_private_key(self, private_key: str) -> Keypair:
        """Import wallet from private key (base58 or hex)"""
        try:
            # Try base58 first
            if len(private_key) < 100:
                secret_key = base58.b58decode(private_key)
            else:
                # Try hex
                secret_key = bytes.fromhex(private_key)
            
            keypair = Keypair.from_bytes(secret_key)
            return keypair
        except Exception as e:
            raise ValueError(f"Invalid private key format: {str(e)}")
    
    def import_from_mnemonic(self, mnemonic: str) -> Keypair:
        """Import wallet from mnemonic phrase"""
        try:
            seed = self.mnemo.to_seed(mnemonic)
            keypair = Keypair.from_seed(seed[:32])
            return keypair
        except Exception as e:
            raise ValueError(f"Invalid mnemonic: {str(e)}")
    
    def get_balance(self, public_key: str) -> float:
        """Get SOL balance for public key"""
        try:
            pubkey = Pubkey.from_string(public_key)
            response = self.client.get_balance(pubkey)
            
            if response.value is not None:
                # Convert lamports to SOL
                balance_sol = response.value / 1e9
                return balance_sol
            return 0.0
        except Exception as e:
            print(f"Error getting balance: {str(e)}")
            return 0.0
    
    def get_token_accounts(self, public_key: str) -> list:
        """Get all token accounts for a wallet"""
        try:
            pubkey = Pubkey.from_string(public_key)
            response = self.client.get_token_accounts_by_owner(
                pubkey,
                {"programId": Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")}
            )
            
            if response.value:
                return response.value
            return []
        except Exception as e:
            print(f"Error getting token accounts: {str(e)}")
            return []

# Helper functions
def generate_wallet() -> Tuple[str, Keypair]:
    """Generate new wallet"""
    wm = WalletManager()
    return wm.generate_wallet()

def import_wallet(key: str, key_type: str = "private_key") -> Keypair:
    """Import wallet from private key or mnemonic"""
    wm = WalletManager()
    if key_type == "mnemonic":
        return wm.import_from_mnemonic(key)
    else:
        return wm.import_from_private_key(key)

def get_balance(public_key: str) -> float:
    """Get wallet balance"""
    wm = WalletManager()
    return wm.get_balance(public_key)

def keypair_to_base58(keypair: Keypair) -> str:
    """Convert keypair to base58 private key"""
    return base58.b58encode(bytes(keypair)).decode()
