import hashlib
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.exceptions import DomainError
from app.core.security import hash_password,verify_password,access_token,refresh_token,decode
from app.models import User,RefreshToken

def register(db,email,name,password):
    if db.scalar(select(User).where(User.email==email.lower())): raise DomainError("DUPLICATE_USER","Email already registered",409)
    u=User(email=email.lower(),full_name=name,password_hash=hash_password(password)); db.add(u); db.commit(); db.refresh(u); return u
def login(db,email,password):
    u=db.scalar(select(User).where(User.email==email.lower()))
    if not u or not verify_password(password,u.password_hash): raise DomainError("INVALID_CREDENTIALS","Invalid email or password",401)
    if not u.is_active: raise DomainError("INACTIVE_USER","Inactive users cannot authenticate",401)
    a=access_token(u.id); r=refresh_token(u.id)
    db.add(RefreshToken(user_id=u.id,token_hash=hashlib.sha256(r.encode()).hexdigest())); db.commit()
    return a,r
def rotate(db,raw):
    try:p=decode(raw)
    except ValueError:raise DomainError("UNAUTHORIZED","Invalid refresh token",401)
    if p.get("type")!="refresh":raise DomainError("UNAUTHORIZED","Invalid refresh token",401)
    u=db.get(User,p.get("sub")); h=hashlib.sha256(raw.encode()).hexdigest()
    row=db.scalar(select(RefreshToken).where(RefreshToken.token_hash==h))
    if not u or not row or row.revoked or not u.is_active:raise DomainError("UNAUTHORIZED","Refresh token revoked or invalid",401)
    row.revoked=True; a=access_token(u.id); r=refresh_token(u.id)
    db.add(RefreshToken(user_id=u.id,token_hash=hashlib.sha256(r.encode()).hexdigest())); db.commit()
    return a,r
