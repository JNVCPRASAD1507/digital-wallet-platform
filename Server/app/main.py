from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api
from app.core.config import settings
from app.core.database import Base, engine
from app.core.exceptions import DomainError, handler
import app.models

app = FastAPI(title="Digital Wallet & Transaction Processing Platform", version="1.0.0")
app.add_exception_handler(DomainError, handler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api)


@app.get("/health")
def health():
    return {"status": "ok"}
