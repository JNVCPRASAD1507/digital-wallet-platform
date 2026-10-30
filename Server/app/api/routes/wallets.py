from uuid import UUID
from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.enums import Role,WalletStatus
from app.core.exceptions import DomainError
from app.dependencies.auth import current_user
from app.models import Wallet
from app.schemas import WalletCreate,WalletOut
from app.services.wallet import create,status
router=APIRouter()
@router.post("",response_model=WalletOut,status_code=201)
def create_api(x:WalletCreate,db:Session=Depends(get_db),u=Depends(current_user)):return create(db,u,x.currency)
@router.get("",response_model=list[WalletOut])
def list_api(db:Session=Depends(get_db),u=Depends(current_user)):return db.query(Wallet).filter(Wallet.user_id==u.id).all()
@router.get("/{wid}",response_model=WalletOut)
def get_api(wid:UUID,db:Session=Depends(get_db),u=Depends(current_user)):
    w=db.get(Wallet,wid)
    if not w:raise DomainError("WALLET_NOT_FOUND","Wallet not found",404)
    if w.user_id!=u.id and u.role not in {Role.ADMIN,Role.SUPER_ADMIN,Role.SUPPORT_AGENT}:raise DomainError("FORBIDDEN","Not authorized",403)
    return w
@router.patch("/{wid}",response_model=WalletOut)
def patch(wid:UUID,x:WalletCreate,db:Session=Depends(get_db),u=Depends(current_user)):
    w=db.get(Wallet,wid)
    if not w or (w.user_id!=u.id and u.role not in {Role.ADMIN,Role.SUPER_ADMIN}):raise DomainError("FORBIDDEN","Not authorized",403)
    w.currency=x.currency.upper();db.commit();db.refresh(w);return w
@router.post("/{wid}/freeze",response_model=WalletOut)
def freeze(wid:UUID,db:Session=Depends(get_db),u=Depends(current_user)):return status(db,wid,WalletStatus.FROZEN)
@router.post("/{wid}/unfreeze",response_model=WalletOut)
def unfreeze(wid:UUID,db:Session=Depends(get_db),u=Depends(current_user)):return status(db,wid,WalletStatus.ACTIVE)
