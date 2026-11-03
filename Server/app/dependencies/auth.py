from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.enums import Role
from app.core.exceptions import DomainError
from app.core.security import decode
from app.models import User

bearer_scheme = HTTPBearer()


def current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    try:
        payload = decode(credentials.credentials)
    except ValueError:
        raise DomainError("UNAUTHORIZED", "Invalid token", 401)

    if payload.get("type") != "access":
        raise DomainError("UNAUTHORIZED", "Invalid access token", 401)

    user_id = payload.get("sub")

    if not user_id:
        raise DomainError("UNAUTHORIZED", "Missing user ID", 401)

    u = db.get(User, user_id)

    if not u or not u.is_active:
        raise DomainError("UNAUTHORIZED", "Inactive or missing user", 401)

    return u


def roles(*allowed):
    def dep(u=Depends(current_user)):
        if u.role not in allowed:
            raise DomainError("FORBIDDEN", "Insufficient permissions", 403)
        return u

    return dep
