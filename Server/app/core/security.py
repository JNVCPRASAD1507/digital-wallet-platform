from datetime import datetime,timedelta,timezone
from jose import jwt,JWTError
from passlib.context import CryptContext
from app.core.config import settings
pwd=CryptContext(schemes=["bcrypt"],deprecated="auto")
def hash_password(v): return pwd.hash(v)
def verify_password(v,h): return pwd.verify(v,h)
def token(sub,typ,delta):
    now=datetime.now(timezone.utc)
    return jwt.encode({"sub":str(sub),"type":typ,"iat":now,"exp":now+delta},settings.secret_key,algorithm="HS256")
def access_token(uid): return token(uid,"access",timedelta(minutes=settings.access_token_expire_minutes))
def refresh_token(uid): return token(uid,"refresh",timedelta(days=settings.refresh_token_expire_days))
def decode(v):
    try: return jwt.decode(v,settings.secret_key,algorithms=["HS256"])
    except JWTError as e: raise ValueError("invalid token") from e
