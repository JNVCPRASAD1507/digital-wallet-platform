import uuid
from decimal import Decimal
from sqlalchemy import String,Boolean,ForeignKey,Numeric,Text,JSON,DateTime,UniqueConstraint
from sqlalchemy.orm import Mapped,mapped_column,relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.core.enums import Role,WalletStatus,OperationStatus,TransactionType,RefundStatus,SuspicionStatus

class User(Base):
    __tablename__="users"
    id:Mapped[uuid.UUID]=mapped_column(primary_key=True,default=uuid.uuid4)
    email:Mapped[str]=mapped_column(String(255),unique=True,index=True)
    full_name:Mapped[str]=mapped_column(String(120))
    password_hash:Mapped[str]=mapped_column(String(255))
    role:Mapped[Role]=mapped_column(default=Role.CUSTOMER,index=True)
    is_active:Mapped[bool]=mapped_column(Boolean,default=True)
    created_at:Mapped[object]=mapped_column(DateTime(timezone=True),server_default=func.now())
    updated_at:Mapped[object]=mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now())
    wallets=relationship("Wallet",back_populates="user",cascade="all, delete-orphan")

class Wallet(Base):
    __tablename__="wallets"
    id:Mapped[uuid.UUID]=mapped_column(primary_key=True,default=uuid.uuid4)
    user_id:Mapped[uuid.UUID]=mapped_column(ForeignKey("users.id",ondelete="CASCADE"),index=True)
    currency:Mapped[str]=mapped_column(String(3),default="INR")
    available_balance:Mapped[Decimal]=mapped_column(Numeric(20,2),default=0)
    pending_balance:Mapped[Decimal]=mapped_column(Numeric(20,2),default=0)
    status:Mapped[WalletStatus]=mapped_column(default=WalletStatus.ACTIVE,index=True)
    created_at:Mapped[object]=mapped_column(DateTime(timezone=True),server_default=func.now())
    updated_at:Mapped[object]=mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now())
    user=relationship("User",back_populates="wallets")

class Transaction(Base):
    __tablename__="transactions"
    id:Mapped[uuid.UUID]=mapped_column(primary_key=True,default=uuid.uuid4)
    wallet_id:Mapped[uuid.UUID]=mapped_column(ForeignKey("wallets.id",ondelete="RESTRICT"),index=True)
    transaction_type:Mapped[TransactionType]=mapped_column(index=True)
    amount:Mapped[Decimal]=mapped_column(Numeric(20,2))
    balance_before:Mapped[Decimal]=mapped_column(Numeric(20,2))
    balance_after:Mapped[Decimal]=mapped_column(Numeric(20,2))
    reference_entity:Mapped[str|None]=mapped_column(String(50))
    reference_id:Mapped[str|None]=mapped_column(String(100),index=True)
    description:Mapped[str|None]=mapped_column(Text)
    created_by:Mapped[uuid.UUID|None]=mapped_column(ForeignKey("users.id",ondelete="SET NULL"))
    metadata_json:Mapped[dict|None]=mapped_column(JSON)
    created_at:Mapped[object]=mapped_column(DateTime(timezone=True),server_default=func.now())
    updated_at:Mapped[object]=mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now())

class Deposit(Base):
    __tablename__="deposits"
    id:Mapped[uuid.UUID]=mapped_column(primary_key=True,default=uuid.uuid4)
    wallet_id:Mapped[uuid.UUID]=mapped_column(ForeignKey("wallets.id",ondelete="RESTRICT"))
    amount:Mapped[Decimal]=mapped_column(Numeric(20,2)); currency:Mapped[str]=mapped_column(String(3))
    status:Mapped[OperationStatus]=mapped_column(default=OperationStatus.COMPLETED)
    reference_number:Mapped[str]=mapped_column(String(100),unique=True)
    created_at:Mapped[object]=mapped_column(DateTime(timezone=True),server_default=func.now())

class Withdrawal(Base):
    __tablename__="withdrawals"
    id:Mapped[uuid.UUID]=mapped_column(primary_key=True,default=uuid.uuid4)
    wallet_id:Mapped[uuid.UUID]=mapped_column(ForeignKey("wallets.id",ondelete="RESTRICT"))
    amount:Mapped[Decimal]=mapped_column(Numeric(20,2)); currency:Mapped[str]=mapped_column(String(3))
    status:Mapped[OperationStatus]=mapped_column(default=OperationStatus.COMPLETED)
    reference_number:Mapped[str]=mapped_column(String(100),unique=True)
    created_at:Mapped[object]=mapped_column(DateTime(timezone=True),server_default=func.now())

class Transfer(Base):
    __tablename__="transfers"
    id:Mapped[uuid.UUID]=mapped_column(primary_key=True,default=uuid.uuid4)
    sender_wallet_id:Mapped[uuid.UUID]=mapped_column(ForeignKey("wallets.id",ondelete="RESTRICT"))
    receiver_wallet_id:Mapped[uuid.UUID]=mapped_column(ForeignKey("wallets.id",ondelete="RESTRICT"))
    amount:Mapped[Decimal]=mapped_column(Numeric(20,2)); currency:Mapped[str]=mapped_column(String(3))
    status:Mapped[OperationStatus]=mapped_column(default=OperationStatus.COMPLETED)
    reference:Mapped[str]=mapped_column(String(100),unique=True)
    created_at:Mapped[object]=mapped_column(DateTime(timezone=True),server_default=func.now())

class Refund(Base):
    __tablename__="refunds"
    id:Mapped[uuid.UUID]=mapped_column(primary_key=True,default=uuid.uuid4)
    transaction_id:Mapped[uuid.UUID]=mapped_column(ForeignKey("transactions.id",ondelete="RESTRICT"))
    wallet_id:Mapped[uuid.UUID]=mapped_column(ForeignKey("wallets.id",ondelete="RESTRICT"))
    amount:Mapped[Decimal]=mapped_column(Numeric(20,2)); status:Mapped[RefundStatus]=mapped_column(default=RefundStatus.REQUESTED)
    reason:Mapped[str]=mapped_column(Text)
    __table_args__=(UniqueConstraint("transaction_id",name="uq_refund_transaction"),)

class SuspiciousTransaction(Base):
    __tablename__="suspicious_transactions"
    id:Mapped[uuid.UUID]=mapped_column(primary_key=True,default=uuid.uuid4)
    transaction_id:Mapped[uuid.UUID]=mapped_column(ForeignKey("transactions.id",ondelete="CASCADE"),unique=True)
    status:Mapped[SuspicionStatus]=mapped_column(default=SuspicionStatus.REVIEW_REQUIRED)
    reason:Mapped[str]=mapped_column(Text)

class Notification(Base):
    __tablename__="notifications"
    id:Mapped[uuid.UUID]=mapped_column(primary_key=True,default=uuid.uuid4)
    user_id:Mapped[uuid.UUID]=mapped_column(ForeignKey("users.id",ondelete="CASCADE"))
    title:Mapped[str]=mapped_column(String(200)); message:Mapped[str]=mapped_column(Text)
    is_read:Mapped[bool]=mapped_column(Boolean,default=False)
    created_at:Mapped[object]=mapped_column(DateTime(timezone=True),server_default=func.now())

class IdempotencyKey(Base):
    __tablename__="idempotency_keys"
    id:Mapped[uuid.UUID]=mapped_column(primary_key=True,default=uuid.uuid4)
    user_id:Mapped[uuid.UUID]=mapped_column(ForeignKey("users.id",ondelete="CASCADE"))
    key:Mapped[str]=mapped_column(String(255)); operation:Mapped[str]=mapped_column(String(50))
    resource_id:Mapped[str|None]=mapped_column(String(100))
    response_json:Mapped[dict|None]=mapped_column(JSON)
    __table_args__=(UniqueConstraint("user_id","key","operation",name="uq_idempotency"),)

class RefreshToken(Base):
    __tablename__="refresh_tokens"
    id:Mapped[uuid.UUID]=mapped_column(primary_key=True,default=uuid.uuid4)
    user_id:Mapped[uuid.UUID]=mapped_column(ForeignKey("users.id",ondelete="CASCADE"))
    token_hash:Mapped[str]=mapped_column(String(128),unique=True); revoked:Mapped[bool]=mapped_column(Boolean,default=False)

class AuditLog(Base):
    __tablename__="audit_logs"
    id:Mapped[uuid.UUID]=mapped_column(primary_key=True,default=uuid.uuid4)
    user_id:Mapped[uuid.UUID|None]=mapped_column(ForeignKey("users.id",ondelete="SET NULL"))
    action:Mapped[str]=mapped_column(String(100)); entity:Mapped[str|None]=mapped_column(String(80))
    entity_id:Mapped[str|None]=mapped_column(String(100)); ip_address:Mapped[str|None]=mapped_column(String(45))
    metadata_json:Mapped[dict|None]=mapped_column(JSON)
