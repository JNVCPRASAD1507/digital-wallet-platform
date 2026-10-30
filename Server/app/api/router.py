from fastapi import APIRouter
from app.api.routes import auth,wallets,money,transactions,notifications,admin,dashboard
api=APIRouter(prefix="/api")
api.include_router(auth.router,prefix="/auth",tags=["Authentication"])
api.include_router(wallets.router,prefix="/wallets",tags=["Wallets"])
api.include_router(money.router,tags=["Money"])
api.include_router(transactions.router,tags=["Transactions"])
api.include_router(notifications.router,prefix="/notifications",tags=["Notifications"])
api.include_router(admin.router,prefix="/admin",tags=["Admin"])
api.include_router(dashboard.router,prefix="/dashboard",tags=["Dashboard"])
