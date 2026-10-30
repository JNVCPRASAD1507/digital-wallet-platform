from fastapi import Depends,Header
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.enums import Role
from app.core.exceptions import DomainError
from app.core.security import decode
from app.models import User

def current_user(authorization:str=Header(...),db:Session=Depends(get_db)):
    if not authorization.lower().startswith("bearer "): raise DomainError("UNAUTHORIZED","Bearer token required",401)
    try: p=decode(authorization.split(" ",1)[1])
    except ValueError: raise DomainError("UNAUTHORIZED","Invalid token",401)
    if p.get("type")!="access": raise DomainError("UNAUTHORIZED","Invalid access token",401)
    u=db.get(User,p.get("sub"))
    if not u or not u.is_active: raise DomainError("UNAUTHORIZED","Inactive or missing user",401)
    return u

def roles(*allowed):
    def dep(u=Depends(current_user)):
        if u.role not in allowed: raise DomainError("FORBIDDEN","Insufficient permissions",403)
        return u
    return dep
