from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import hash_password,verify_password
from app.core.exceptions import DomainError
from app.dependencies.auth import current_user
from app.models import User
from app.schemas import Register,Login,Refresh,Tokens,UserOut
from app.services.auth import register,login,rotate
router=APIRouter()
@router.post("/register",response_model=UserOut,status_code=201)
def register_api(x:Register,db:Session=Depends(get_db)):return register(db,x.email,x.full_name,x.password)
@router.post("/login",response_model=Tokens)
def login_api(x:Login,db:Session=Depends(get_db)):
    a,r=login(db,x.email,x.password);return Tokens(access_token=a,refresh_token=r)
@router.post("/refresh",response_model=Tokens)
def refresh_api(x:Refresh,db:Session=Depends(get_db)):
    a,r=rotate(db,x.refresh_token);return Tokens(access_token=a,refresh_token=r)
@router.post("/logout")
def logout(x:Refresh,db:Session=Depends(get_db)):
    import hashlib
    from sqlalchemy import update
    from app.models import RefreshToken
    db.execute(update(RefreshToken).where(RefreshToken.token_hash==hashlib.sha256(x.refresh_token.encode()).hexdigest()).values(revoked=True));db.commit()
    return {"message":"Logged out"}
@router.get("/me",response_model=UserOut)
def me(u=Depends(current_user)):return u
@router.post("/change-password")
def change(x:dict,db:Session=Depends(get_db),u=Depends(current_user)):
    if not verify_password(x.get("current_password",""),u.password_hash):raise DomainError("INVALID_CREDENTIALS","Current password is incorrect",400)
    u.password_hash=hash_password(x["new_password"]);db.commit();return {"message":"Password changed"}
