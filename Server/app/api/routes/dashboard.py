from fastapi import APIRouter,Depends
from sqlalchemy import func,select
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.enums import Role
from app.dependencies.auth import current_user
from app.models import User,Wallet,Transaction
router=APIRouter()
@router.get("")
def dashboard(db:Session=Depends(get_db),u=Depends(current_user)):
    if u.role in {Role.ADMIN,Role.SUPER_ADMIN}:
        return {"total_users":db.scalar(select(func.count(User.id))),"active_wallets":db.scalar(select(func.count(Wallet.id)).where(Wallet.status=="ACTIVE")),"total_wallet_balance":db.scalar(select(func.coalesce(func.sum(Wallet.available_balance),0))),"today_transactions":db.scalar(select(func.count(Transaction.id)))}
    ws=list(db.scalars(select(Wallet).where(Wallet.user_id==u.id)))
    return {"wallet_balance":sum((w.available_balance for w in ws),0),"wallets":len(ws)}
