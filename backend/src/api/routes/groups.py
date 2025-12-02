from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import get_db, close_db
from core.group_manager import get_group_manager
from core.bulk_operations import get_bulk_operations

router = APIRouter(prefix="/group", tags=["wallet-groups"])

# Pydantic models
class CreateGroupRequest(BaseModel):
    name: str
    description: str = ""
    count: int = 10
    password: str

class DistributeSOLRequest(BaseModel):
    from_wallet_id: int
    to_group_id: int
    amount_per_wallet: float
    password: str

class CollectSOLRequest(BaseModel):
    from_group_id: int
    to_wallet_id: int
    password: str
    leave_amount: float = 0.001

class BulkBuyRequest(BaseModel):
    group_id: int
    token_address: str
    sol_amount: float
    slippage: float = 1.0
    password: str

class BulkSellRequest(BaseModel):
    group_id: int
    token_address: str
    percentage: int
    slippage: float = 1.0
    password: str

class AddWalletToGroupRequest(BaseModel):
    wallet_id: int
    group_id: int

class RemoveWalletFromGroupRequest(BaseModel):
    wallet_id: int

# Routes
@router.post("/create")
def create_group(request: CreateGroupRequest, db: Session = Depends(get_db)):
    """
    Create a wallet group with multiple wallets
    
    Example:
    - name: "Group 1"
    - count: 10
    Creates: Group 1 - Wallet 1, Group 1 - Wallet 2, ... Group 1 - Wallet 10
    """
    try:
        manager = get_group_manager()
        result = manager.create_group(
            name=request.name,
            description=request.description,
            count=request.count,
            password=request.password
        )
        
        return {
            "success": True,
            "message": f"Created group '{request.name}' with {request.count} wallets",
            **result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        close_db(db)

@router.get("/list")
def list_groups(db: Session = Depends(get_db)):
    """List all wallet groups"""
    try:
        manager = get_group_manager()
        groups = manager.list_groups()
        return {"groups": groups}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        close_db(db)

@router.get("/{group_id}")
def get_group(group_id: int, db: Session = Depends(get_db)):
    """Get group details with all wallets"""
    try:
        manager = get_group_manager()
        group = manager.get_group(group_id)
        
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        
        return group
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        close_db(db)

@router.get("/{group_id}/wallets")
def get_group_wallets(group_id: int, db: Session = Depends(get_db)):
    """Get all wallets in a group"""
    try:
        manager = get_group_manager()
        wallets = manager.get_group_wallets(group_id)
        return {"group_id": group_id, "wallets": wallets}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        close_db(db)

@router.get("/{group_id}/balances")
def get_group_balances(group_id: int, db: Session = Depends(get_db)):
    """Get SOL balances for all wallets in group"""
    try:
        manager = get_group_manager()
        balances = manager.get_group_balances(group_id)
        return balances
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        close_db(db)

@router.delete("/{group_id}")
def delete_group(group_id: int, db: Session = Depends(get_db)):
    """Delete a group and all its wallets"""
    try:
        manager = get_group_manager()
        result = manager.delete_group(group_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        close_db(db)

@router.post("/distribute-sol")
def distribute_sol(request: DistributeSOLRequest, db: Session = Depends(get_db)):
    """
    Distribute SOL from one wallet to all wallets in a group
    
    Example: Send 0.1 SOL to each wallet in group
    """
    try:
        bulk_ops = get_bulk_operations()
        result = bulk_ops.distribute_sol(
            from_wallet_id=request.from_wallet_id,
            to_group_id=request.to_group_id,
            amount_per_wallet=request.amount_per_wallet,
            password=request.password
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        close_db(db)

@router.post("/collect-sol")
def collect_sol(request: CollectSOLRequest, db: Session = Depends(get_db)):
    """
    Collect SOL from all wallets in group to one wallet
    
    Leaves small amount (default 0.001 SOL) in each wallet for rent
    """
    try:
        bulk_ops = get_bulk_operations()
        result = bulk_ops.collect_sol(
            from_group_id=request.from_group_id,
            to_wallet_id=request.to_wallet_id,
            password=request.password,
            leave_amount=request.leave_amount
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        close_db(db)

@router.post("/bulk-buy")
async def bulk_buy(request: BulkBuyRequest, db: Session = Depends(get_db)):
    """
    Buy token from all wallets in group simultaneously

    All wallets will buy the same token with same amount and slippage
    """
    try:
        bulk_ops = get_bulk_operations()
        result = await bulk_ops.bulk_buy(
            group_id=request.group_id,
            token_address=request.token_address,
            sol_amount=request.sol_amount,
            slippage=request.slippage,
            password=request.password
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        close_db(db)

@router.post("/bulk-sell")
async def bulk_sell(request: BulkSellRequest, db: Session = Depends(get_db)):
    """
    Sell token from all wallets in group simultaneously

    All wallets will sell same token with same percentage and slippage
    """
    try:
        bulk_ops = get_bulk_operations()
        result = await bulk_ops.bulk_sell(
            group_id=request.group_id,
            token_address=request.token_address,
            percentage=request.percentage,
            slippage=request.slippage,
            password=request.password
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        close_db(db)

@router.post("/add-wallet")
def add_wallet_to_group(request: AddWalletToGroupRequest, db: Session = Depends(get_db)):
    """
    Add an existing wallet to a group

    The wallet must not already be in a group
    """
    try:
        manager = get_group_manager()
        result = manager.add_wallet_to_group(
            wallet_id=request.wallet_id,
            group_id=request.group_id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        close_db(db)

@router.post("/remove-wallet")
def remove_wallet_from_group(request: RemoveWalletFromGroupRequest, db: Session = Depends(get_db)):
    """
    Remove a wallet from its group (wallet is not deleted)

    The wallet will remain in the system but won't be part of any group
    """
    try:
        manager = get_group_manager()
        result = manager.remove_wallet_from_group(wallet_id=request.wallet_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        close_db(db)
