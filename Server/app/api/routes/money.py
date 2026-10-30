from uuid import UUID
from fastapi import APIRouter,Depends,Header
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.dependencies.auth import current_user
from app.models import User
from app.schemas import Money,TransferIn
from app.services.money import deposit,withdraw,transfer
router=APIRouter()
@router.post("/wallets/{wid}/deposits")
def deposit_api(wid:UUID,x:Money,idempotency_key:str|None=Header(None,alias="Idempotency-Key"),db:Session=Depends(get_db),u:User=Depends(current_user)):
    return deposit(db,u,wid,x.amount,idempotency_key)
@router.post("/wallets/{wid}/withdrawals")
def withdraw_api(wid:UUID,x:Money,idempotency_key:str|None=Header(None,alias="Idempotency-Key"),db:Session=Depends(get_db),u:User=Depends(current_user)):
    return withdraw(db,u,wid,x.amount,idempotency_key)
@router.post("/transfers")
def transfer_api(x:TransferIn,idempotency_key:str|None=Header(None,alias="Idempotency-Key"),db:Session=Depends(get_db),u:User=Depends(current_user)):
    return transfer(db,u,x.sender_wallet_id,x.receiver_wallet_id,x.amount,idempotency_key)
