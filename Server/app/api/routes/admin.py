from fastapi import APIRouter,Depends
from app.core.enums import Role
from app.dependencies.auth import roles
router=APIRouter()
limits={"maximum_transaction_amount":100000,"daily_transfer_limit":250000,"daily_withdrawal_limit":100000,"max_transactions_per_day":100}
@router.get("/transaction-limits")
def get_limits(u=Depends(roles(Role.ADMIN,Role.SUPER_ADMIN))):return limits
@router.patch("/transaction-limits")
def set_limits(x:dict,u=Depends(roles(Role.ADMIN,Role.SUPER_ADMIN))):limits.update(x);return limits
