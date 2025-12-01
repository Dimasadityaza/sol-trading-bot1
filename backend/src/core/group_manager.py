"""
Wallet Group Manager
Handles bulk wallet creation, group management, and bulk operations
"""

import sys
import os
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.wallet import generate_wallet, keypair_to_base58
from core.database import get_db, close_db, Wallet, WalletGroup
from utils.encryption import encrypt_private_key
from solders.keypair import Keypair
from solana.rpc.api import Client
from config import RPC_ENDPOINT

# Get the project root directory (3 levels up from this file)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
WALLET_KEYS_DIR = os.path.join(PROJECT_ROOT, 'wallet_keys')

class WalletGroupManager:
    """Manage wallet groups and bulk operations"""

    def __init__(self):
        self.client = Client(RPC_ENDPOINT)
        # Ensure wallet_keys directory exists
        os.makedirs(WALLET_KEYS_DIR, exist_ok=True)

    def _save_wallet_keys_to_file(self, group_name: str, wallets_data: list):
        """
        Save wallet mnemonics to a file for backup

        Args:
            group_name: Name of the wallet group
            wallets_data: List of wallet dictionaries with mnemonic, address, label
        """
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Sanitize group name for filename
        safe_group_name = "".join(c for c in group_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_group_name = safe_group_name.replace(' ', '_')
        filename = f"{safe_group_name}_{timestamp}.txt"
        filepath = os.path.join(WALLET_KEYS_DIR, filename)

        # Create file content
        content = f"""GROUP: {group_name}
CREATED: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
PASSWORD: [user must fill this manually]

⚠️  IMPORTANT SECURITY WARNING ⚠️
- Keep this file in a secure location
- Never share these mnemonic phrases with anyone
- Anyone with access to these phrases can control your wallets
- Consider encrypting this file with a strong password

"""

        for wallet in wallets_data:
            content += f"""{'='*60}
=== WALLET {wallet['index']} ===
{'='*60}
Label: {wallet['label']}
Address: {wallet['address']}
Mnemonic: {wallet['mnemonic']}

"""

        # Write to file
        with open(filepath, 'w') as f:
            f.write(content)

        return filepath
    
    def create_group(self, name: str, description: str = "", count: int = 10, password: str = None):
        """
        Create a wallet group with multiple wallets
        
        Args:
            name: Group name (e.g., "Group 1")
            description: Group description
            count: Number of wallets to create (default 10)
            password: Password to encrypt all wallets
            
        Returns:
            dict with group info and wallets
        """
        db = get_db()
        try:
            # Create group
            group = WalletGroup(
                name=name,
                description=description,
                wallet_count=count
            )
            db.add(group)
            db.commit()
            db.refresh(group)
            
            # Create wallets
            wallets = []
            for i in range(count):
                # Generate wallet (returns: mnemonic, keypair)
                mnemonic, keypair = generate_wallet()
                private_key_bytes = keypair_to_base58(keypair)
                
                # Ensure private_key is string
                if isinstance(private_key_bytes, bytes):
                    private_key = private_key_bytes.decode('utf-8')
                else:
                    private_key = str(private_key_bytes)
                
                public_key = str(keypair.pubkey())
                
                # Encrypt private key
                encrypted_key = encrypt_private_key(private_key, password) if password else private_key
                
                # Create wallet label
                label = f"{name} - Wallet {i+1}"
                
                # Save to database
                wallet = Wallet(
                    group_id=group.id,
                    wallet_index=i + 1,
                    label=label,
                    encrypted_private_key=encrypted_key,
                    public_key=public_key
                )
                db.add(wallet)
                db.commit()
                db.refresh(wallet)
                
                wallets.append({
                    "id": wallet.id,
                    "index": i + 1,
                    "label": label,
                    "address": public_key,
                    "mnemonic": mnemonic  # Return for user to save
                })

            # Save wallet keys to file for backup
            try:
                keys_file_path = self._save_wallet_keys_to_file(name, wallets)
                print(f"✓ Wallet keys saved to: {keys_file_path}")
            except Exception as e:
                print(f"Warning: Could not save wallet keys to file: {e}")

            return {
                "group_id": group.id,
                "group_name": name,
                "wallet_count": count,
                "wallets": wallets,
                "keys_file": keys_file_path if 'keys_file_path' in locals() else None
            }
            
        except Exception as e:
            db.rollback()
            raise e
        finally:
            close_db(db)
    
    def get_group(self, group_id: int):
        """Get group details with all wallets"""
        db = get_db()
        try:
            group = db.query(WalletGroup).filter(WalletGroup.id == group_id).first()
            if not group:
                return None
            
            wallets = db.query(Wallet).filter(Wallet.group_id == group_id).order_by(Wallet.wallet_index).all()
            
            return {
                "id": group.id,
                "name": group.name,
                "description": group.description,
                "wallet_count": group.wallet_count,
                "created_at": str(group.created_at),
                "wallets": [
                    {
                        "id": w.id,
                        "index": w.wallet_index,
                        "label": w.label,
                        "address": w.public_key
                    }
                    for w in wallets
                ]
            }
        finally:
            close_db(db)
    
    def list_groups(self):
        """List all wallet groups"""
        db = get_db()
        try:
            groups = db.query(WalletGroup).all()
            return [
                {
                    "id": g.id,
                    "name": g.name,
                    "description": g.description,
                    "wallet_count": g.wallet_count,
                    "created_at": str(g.created_at)
                }
                for g in groups
            ]
        finally:
            close_db(db)
    
    def get_group_wallets(self, group_id: int):
        """Get all wallets in a group"""
        db = get_db()
        try:
            wallets = db.query(Wallet).filter(Wallet.group_id == group_id).order_by(Wallet.wallet_index).all()
            return [
                {
                    "id": w.id,
                    "index": w.wallet_index,
                    "label": w.label,
                    "address": w.public_key
                }
                for w in wallets
            ]
        finally:
            close_db(db)
    
    def delete_group(self, group_id: int):
        """Delete a group and all its wallets"""
        db = get_db()
        try:
            # Delete wallets
            db.query(Wallet).filter(Wallet.group_id == group_id).delete()
            
            # Delete group
            db.query(WalletGroup).filter(WalletGroup.id == group_id).delete()
            
            db.commit()
            return {"success": True, "message": "Group deleted"}
        except Exception as e:
            db.rollback()
            raise e
        finally:
            close_db(db)
    
    def get_group_balances(self, group_id: int):
        """Get SOL balance for all wallets in group"""
        db = get_db()
        try:
            wallets = db.query(Wallet).filter(Wallet.group_id == group_id).all()
            
            balances = []
            total_balance = 0.0
            
            for wallet in wallets:
                try:
                    response = self.client.get_balance(wallet.public_key)
                    balance = response.value / 1e9  # Convert lamports to SOL
                    total_balance += balance
                    
                    balances.append({
                        "id": wallet.id,
                        "index": wallet.wallet_index,
                        "label": wallet.label,
                        "address": wallet.public_key,
                        "balance": balance
                    })
                except:
                    balances.append({
                        "id": wallet.id,
                        "index": wallet.wallet_index,
                        "label": wallet.label,
                        "address": wallet.public_key,
                        "balance": 0.0
                    })
            
            return {
                "group_id": group_id,
                "total_balance": total_balance,
                "wallets": balances
            }
        finally:
            close_db(db)


# Singleton instance
_group_manager = None

def get_group_manager():
    """Get WalletGroupManager instance"""
    global _group_manager
    if _group_manager is None:
        _group_manager = WalletGroupManager()
    return _group_manager
