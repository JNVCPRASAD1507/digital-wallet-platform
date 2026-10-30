from decimal import Decimal
from fastapi import APIRouter,Depends,Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.dependencies.auth import current_user
from app.models import Transaction,Wallet
from app.schemas import TransactionOut
router=APIRouter()
@router.get("/transactions",response_model=list[TransactionOut])
def list_api(page:int=Query(1,ge=1),page_size:int=Query(20,ge=1,le=100),type:str|None=None,min_amount:Decimal|None=None,max_amount:Decimal|None=None,db:Session=Depends(get_db),u=Depends(current_user)):
    ids=select(Wallet.id).where(Wallet.user_id==u.id);q=select(Transaction).where(Transaction.wallet_id.in_(ids))
    if type:q=q.where(Transaction.transaction_type==type)
    if min_amount is not None:q=q.where(Transaction.amount.abs()>=min_amount)
    if max_amount is not None:q=q.where(Transaction.amount.abs()<=max_amount)
    return list(db.scalars(q.order_by(Transaction.created_at.desc()).offset((page-1)*page_size).limit(page_size)))
