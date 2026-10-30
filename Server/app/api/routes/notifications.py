from uuid import UUID
from fastapi import APIRouter,Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.dependencies.auth import current_user
from app.models import Notification
router=APIRouter()
@router.get("")
def list_api(db:Session=Depends(get_db),u=Depends(current_user)):return list(db.scalars(select(Notification).where(Notification.user_id==u.id).order_by(Notification.created_at.desc())))
@router.patch("/{nid}/read")
def read(nid:UUID,db:Session=Depends(get_db),u=Depends(current_user)):
    n=db.scalar(select(Notification).where(Notification.id==nid,Notification.user_id==u.id))
    if n:n.is_read=True;db.commit()
    return {"message":"read"}
@router.patch("/read-all")
def all_read(db:Session=Depends(get_db),u=Depends(current_user)):
    db.query(Notification).filter(Notification.user_id==u.id,Notification.is_read==False).update({"is_read":True});db.commit();return {"message":"all read"}
