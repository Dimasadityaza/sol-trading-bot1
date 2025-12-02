"""
Bulk Operations
Handle distribute/collect SOL and tokens across wallet groups
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.transaction import Transaction
from solders.system_program import TransferParams, transfer
from solana.rpc.api import Client
from solana.rpc.commitment import Confirmed
from core.database import get_db, close_db, Wallet
from utils.encryption import decrypt_private_key
from core.wallet import import_wallet
from config import RPC_ENDPOINT
import asyncio
from typing import List

class BulkOperations:
    """Handle bulk operations for wallet groups"""
    
    def __init__(self):
        self.client = Client(RPC_ENDPOINT)
    
    def distribute_sol(self, from_wallet_id: int, to_group_id: int, amount_per_wallet: float, password: str):
        """
        Distribute SOL from one wallet to all wallets in a group
        
        Args:
            from_wallet_id: Source wallet ID
            to_group_id: Target group ID
            amount_per_wallet: SOL amount to send to each wallet
            password: Password to decrypt source wallet
            
        Returns:
            dict with results
        """
        db = get_db()
        try:
            # Get source wallet
            source = db.query(Wallet).filter(Wallet.id == from_wallet_id).first()
            if not source:
                raise Exception("Source wallet not found")
            
            # Decrypt and import keypair
            private_key = decrypt_private_key(source.encrypted_private_key, password)
            source_keypair = import_wallet(private_key, "private_key")
            
            # Get target wallets
            target_wallets = db.query(Wallet).filter(Wallet.group_id == to_group_id).all()
            
            if not target_wallets:
                raise Exception("No wallets found in group")
            
            # Send to each wallet
            results = []
            for wallet in target_wallets:
                try:
                    # Create transfer instruction
                    lamports = int(amount_per_wallet * 1e9)
                    
                    transfer_params = TransferParams(
                        from_pubkey=source_keypair.pubkey(),
                        to_pubkey=Pubkey.from_string(wallet.public_key),
                        lamports=lamports
                    )
                    
                    transfer_ix = transfer(transfer_params)
                    
                    # Get recent blockhash
                    blockhash_resp = self.client.get_latest_blockhash()
                    recent_blockhash = blockhash_resp.value.blockhash
                    
                    # Create and sign transaction
                    tx = Transaction.new_signed_with_payer(
                        [transfer_ix],
                        source_keypair.pubkey(),
                        [source_keypair],
                        recent_blockhash
                    )
                    
                    # Send transaction
                    result = self.client.send_transaction(tx)
                    signature = str(result.value)
                    
                    results.append({
                        "wallet_id": wallet.id,
                        "wallet_index": wallet.wallet_index,
                        "address": wallet.public_key,
                        "amount": amount_per_wallet,
                        "signature": signature,
                        "success": True
                    })
                    
                except Exception as e:
                    results.append({
                        "wallet_id": wallet.id,
                        "wallet_index": wallet.wallet_index,
                        "address": wallet.public_key,
                        "amount": amount_per_wallet,
                        "error": str(e),
                        "success": False
                    })
            
            # Calculate summary
            successful = sum(1 for r in results if r["success"])
            failed = len(results) - successful
            total_sent = successful * amount_per_wallet
            
            return {
                "total_wallets": len(results),
                "successful": successful,
                "failed": failed,
                "total_sol_sent": total_sent,
                "results": results
            }
            
        finally:
            close_db(db)
    
    def collect_sol(self, from_group_id: int, to_wallet_id: int, password: str, leave_amount: float = 0.001):
        """
        Collect SOL from all wallets in group to one wallet
        
        Args:
            from_group_id: Source group ID
            to_wallet_id: Target wallet ID
            password: Password to decrypt wallets
            leave_amount: SOL to leave in each wallet for rent (default 0.001)
            
        Returns:
            dict with results
        """
        db = get_db()
        try:
            # Get target wallet
            target = db.query(Wallet).filter(Wallet.id == to_wallet_id).first()
            if not target:
                raise Exception("Target wallet not found")
            
            target_pubkey = Pubkey.from_string(target.public_key)
            
            # Get source wallets
            source_wallets = db.query(Wallet).filter(Wallet.group_id == from_group_id).all()
            
            results = []
            total_collected = 0.0
            
            for wallet in source_wallets:
                try:
                    # Get balance
                    wallet_pubkey = Pubkey.from_string(wallet.public_key)
                    balance_resp = self.client.get_balance(wallet_pubkey)
                    balance_lamports = balance_resp.value
                    balance_sol = balance_lamports / 1e9

                    # Calculate amount to send (leave some for rent)
                    send_amount = balance_sol - leave_amount

                    if send_amount <= 0:
                        results.append({
                            "wallet_id": wallet.id,
                            "wallet_index": wallet.wallet_index,
                            "balance": balance_sol,
                            "collected": 0,
                            "success": False,
                            "message": "Insufficient balance"
                        })
                        continue

                    # Decrypt and import keypair
                    private_key = decrypt_private_key(wallet.encrypted_private_key, password)
                    source_keypair = import_wallet(private_key, "private_key")
                    
                    # Create transfer
                    lamports = int(send_amount * 1e9)
                    
                    transfer_params = TransferParams(
                        from_pubkey=source_keypair.pubkey(),
                        to_pubkey=target_pubkey,
                        lamports=lamports
                    )
                    
                    transfer_ix = transfer(transfer_params)
                    
                    # Get blockhash
                    blockhash_resp = self.client.get_latest_blockhash()
                    recent_blockhash = blockhash_resp.value.blockhash
                    
                    # Create and send tx
                    tx = Transaction.new_signed_with_payer(
                        [transfer_ix],
                        source_keypair.pubkey(),
                        [source_keypair],
                        recent_blockhash
                    )
                    
                    result = self.client.send_transaction(tx)
                    signature = str(result.value)
                    
                    total_collected += send_amount
                    
                    results.append({
                        "wallet_id": wallet.id,
                        "wallet_index": wallet.wallet_index,
                        "balance": balance_sol,
                        "collected": send_amount,
                        "signature": signature,
                        "success": True
                    })
                    
                except Exception as e:
                    results.append({
                        "wallet_id": wallet.id,
                        "wallet_index": wallet.wallet_index,
                        "error": str(e),
                        "success": False
                    })
            
            successful = sum(1 for r in results if r["success"])
            
            return {
                "total_wallets": len(results),
                "successful": successful,
                "failed": len(results) - successful,
                "total_collected": total_collected,
                "target_wallet": target.public_key,
                "results": results
            }
            
        finally:
            close_db(db)
    
    def bulk_buy(self, group_id: int, token_address: str, sol_amount: float, slippage: float, password: str):
        """
        Buy token from all wallets in group simultaneously
        
        Args:
            group_id: Wallet group ID
            token_address: Token to buy
            sol_amount: SOL amount per wallet
            slippage: Slippage percentage
            password: Password to decrypt wallets
            
        Returns:
            dict with results
        """
        from trading.executor import TradeExecutor
        
        db = get_db()
        try:
            wallets = db.query(Wallet).filter(Wallet.group_id == group_id).all()
            
            results = []
            
            for wallet in wallets:
                try:
                    # Decrypt wallet
                    private_key = decrypt_private_key(wallet.encrypted_private_key, password)
                    keypair = import_wallet(private_key, "private_key")
                    
                    # Execute buy
                    executor = TradeExecutor(wallet.id, keypair)
                    result = executor.execute_buy(
                        token_address=token_address,
                        sol_amount=sol_amount,
                        slippage=slippage,
                        strategy="bulk_buy"
                    )
                    
                    results.append({
                        "wallet_id": wallet.id,
                        "wallet_index": wallet.wallet_index,
                        **result
                    })
                    
                except Exception as e:
                    results.append({
                        "wallet_id": wallet.id,
                        "wallet_index": wallet.wallet_index,
                        "success": False,
                        "error": str(e)
                    })
            
            successful = sum(1 for r in results if r.get("success"))
            
            return {
                "total_wallets": len(results),
                "successful": successful,
                "failed": len(results) - successful,
                "token_address": token_address,
                "results": results
            }
            
        finally:
            close_db(db)
    
    def bulk_sell(self, group_id: int, token_address: str, percentage: int, slippage: float, password: str):
        """
        Sell token from all wallets in group simultaneously
        
        Args:
            group_id: Wallet group ID
            token_address: Token to sell
            percentage: Percentage to sell (1-100)
            slippage: Slippage percentage
            password: Password to decrypt wallets
            
        Returns:
            dict with results
        """
        from trading.executor import TradeExecutor
        
        db = get_db()
        try:
            wallets = db.query(Wallet).filter(Wallet.group_id == group_id).all()
            
            results = []
            
            for wallet in wallets:
                try:
                    # Decrypt wallet
                    private_key = decrypt_private_key(wallet.encrypted_private_key, password)
                    keypair = import_wallet(private_key, "private_key")
                    
                    # Execute sell
                    executor = TradeExecutor(wallet.id, keypair)
                    result = executor.execute_sell(
                        token_address=token_address,
                        percentage=percentage,
                        slippage=slippage,
                        strategy="bulk_sell"
                    )
                    
                    results.append({
                        "wallet_id": wallet.id,
                        "wallet_index": wallet.wallet_index,
                        **result
                    })
                    
                except Exception as e:
                    results.append({
                        "wallet_id": wallet.id,
                        "wallet_index": wallet.wallet_index,
                        "success": False,
                        "error": str(e)
                    })
            
            successful = sum(1 for r in results if r.get("success"))
            
            return {
                "total_wallets": len(results),
                "successful": successful,
                "failed": len(results) - successful,
                "token_address": token_address,
                "results": results
            }
            
        finally:
            close_db(db)


# Singleton
_bulk_ops = None

def get_bulk_operations():
    global _bulk_ops
    if _bulk_ops is None:
        _bulk_ops = BulkOperations()
    return _bulk_ops
