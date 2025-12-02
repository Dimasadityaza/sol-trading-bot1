"""
Wallet Group Manager
Handles bulk wallet creation, group management, and bulk operations
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.wallet import generate_wallet, keypair_to_base58
from core.database import get_db, close_db, Wallet, WalletGroup
from utils.encryption import encrypt_private_key
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.api import Client
from config import RPC_ENDPOINT

class WalletGroupManager:
    """Manage wallet groups and bulk operations"""
    
    def __init__(self):
        self.client = Client(RPC_ENDPOINT)
    
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
            
            return {
                "group_id": group.id,
                "group_name": name,
                "wallet_count": count,
                "wallets": wallets
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
                    pubkey = Pubkey.from_string(wallet.public_key)
                    response = self.client.get_balance(pubkey)
                    balance = response.value / 1e9 if response.value is not None else 0.0
                    total_balance += balance

                    balances.append({
                        "id": wallet.id,
                        "index": wallet.wallet_index,
                        "label": wallet.label,
                        "address": wallet.public_key,
                        "balance": balance
                    })
                except Exception as e:
                    print(f"Error getting balance for {wallet.label}: {str(e)}")
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

    def add_wallet_to_group(self, wallet_id: int, group_id: int):
        """
        Add an existing wallet to a group

        Args:
            wallet_id: ID of the wallet to add
            group_id: ID of the group to add wallet to

        Returns:
            dict with success status and updated group info
        """
        db = get_db()
        try:
            # Check if wallet exists
            wallet = db.query(Wallet).filter(Wallet.id == wallet_id).first()
            if not wallet:
                raise ValueError(f"Wallet with ID {wallet_id} not found")

            # Check if group exists
            group = db.query(WalletGroup).filter(WalletGroup.id == group_id).first()
            if not group:
                raise ValueError(f"Group with ID {group_id} not found")

            # Check if wallet is already in a group
            if wallet.group_id is not None:
                raise ValueError(f"Wallet '{wallet.label}' is already in a group")

            # Get next wallet index for this group
            max_index = db.query(Wallet).filter(
                Wallet.group_id == group_id
            ).order_by(Wallet.wallet_index.desc()).first()

            next_index = (max_index.wallet_index + 1) if max_index else 1

            # Update wallet
            wallet.group_id = group_id
            wallet.wallet_index = next_index

            # Update group wallet count
            group.wallet_count = group.wallet_count + 1

            db.commit()
            db.refresh(wallet)
            db.refresh(group)

            return {
                "success": True,
                "message": f"Wallet '{wallet.label}' added to group '{group.name}'",
                "wallet": {
                    "id": wallet.id,
                    "label": wallet.label,
                    "address": wallet.public_key,
                    "index": wallet.wallet_index
                },
                "group": {
                    "id": group.id,
                    "name": group.name,
                    "wallet_count": group.wallet_count
                }
            }

        except Exception as e:
            db.rollback()
            raise e
        finally:
            close_db(db)

    def remove_wallet_from_group(self, wallet_id: int):
        """
        Remove a wallet from its group (but don't delete the wallet)

        Args:
            wallet_id: ID of the wallet to remove from group

        Returns:
            dict with success status
        """
        db = get_db()
        try:
            # Check if wallet exists
            wallet = db.query(Wallet).filter(Wallet.id == wallet_id).first()
            if not wallet:
                raise ValueError(f"Wallet with ID {wallet_id} not found")

            if wallet.group_id is None:
                raise ValueError(f"Wallet '{wallet.label}' is not in any group")

            # Get group for count update
            group = db.query(WalletGroup).filter(WalletGroup.id == wallet.group_id).first()

            # Remove from group
            wallet.group_id = None
            wallet.wallet_index = None

            # Update group wallet count
            if group:
                group.wallet_count = max(0, group.wallet_count - 1)

            db.commit()

            return {
                "success": True,
                "message": f"Wallet '{wallet.label}' removed from group"
            }

        except Exception as e:
            db.rollback()
            raise e
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
