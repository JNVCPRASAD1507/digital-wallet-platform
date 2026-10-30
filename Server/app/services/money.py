from decimal import Decimal
from uuid import uuid4
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.enums import WalletStatus,OperationStatus,TransactionType
from app.core.exceptions import DomainError
from app.models import Wallet,Deposit,Withdrawal,Transfer,Transaction,IdempotencyKey,Notification

def idem(db,user,key,op):
    if not key: raise DomainError("IDEMPOTENCY_KEY_REQUIRED","Idempotency-Key header is required",400)
    return db.scalar(select(IdempotencyKey).where(IdempotencyKey.user_id==user.id,IdempotencyKey.key==key,IdempotencyKey.operation==op))

def note(db,uid,title,msg): db.add(Notification(user_id=uid,title=title,message=msg))

def ledger(db,w,typ,amount,ref,uid,desc):
    before=Decimal(w.available_balance); after=before+amount
    db.add(Transaction(wallet_id=w.id,transaction_type=typ,amount=amount,balance_before=before,balance_after=after,
                       reference_entity=ref[0],reference_id=str(ref[1]),description=desc,created_by=uid))

def deposit(db,user,wid,amount,key):
    old=idem(db,user,key,"DEPOSIT")
    if old:return db.get(Deposit,old.resource_id)
    w=db.query(Wallet).filter(Wallet.id==wid).with_for_update().first()
    if not w:raise DomainError("WALLET_NOT_FOUND","Wallet not found",404)
    if w.user_id!=user.id:raise DomainError("FORBIDDEN","Wallet does not belong to user",403)
    if w.status!=WalletStatus.ACTIVE:raise DomainError("WALLET_FROZEN","Wallet is not active",409)
    d=Deposit(wallet_id=w.id,amount=amount,currency=w.currency,status=OperationStatus.COMPLETED,reference_number=f"DEP-{uuid4().hex[:16]}")
    db.add(d);w.available_balance=Decimal(w.available_balance)+amount;db.flush()
    ledger(db,w,TransactionType.DEPOSIT,amount,("deposit",d.id),user.id,"Deposit")
    db.add(IdempotencyKey(user_id=user.id,key=key,operation="DEPOSIT",resource_id=str(d.id)));note(db,user.id,"Deposit completed",d.reference_number)
    db.commit();db.refresh(d);return d

def withdraw(db,user,wid,amount,key):
    old=idem(db,user,key,"WITHDRAWAL")
    if old:return db.get(Withdrawal,old.resource_id)
    w=db.query(Wallet).filter(Wallet.id==wid).with_for_update().first()
    if not w:raise DomainError("WALLET_NOT_FOUND","Wallet not found",404)
    if w.user_id!=user.id:raise DomainError("FORBIDDEN","Wallet does not belong to user",403)
    if w.status!=WalletStatus.ACTIVE:raise DomainError("WALLET_FROZEN","Frozen wallet cannot withdraw",409)
    if Decimal(w.available_balance)<amount:raise DomainError("INSUFFICIENT_BALANCE","Insufficient wallet balance",409)
    x=Withdrawal(wallet_id=w.id,amount=amount,currency=w.currency,status=OperationStatus.COMPLETED,reference_number=f"WDR-{uuid4().hex[:16]}")
    db.add(x);w.available_balance=Decimal(w.available_balance)-amount;db.flush()
    ledger(db,w,TransactionType.WITHDRAWAL,-amount,("withdrawal",x.id),user.id,"Withdrawal")
    db.add(IdempotencyKey(user_id=user.id,key=key,operation="WITHDRAWAL",resource_id=str(x.id)));note(db,user.id,"Withdrawal completed",x.reference_number)
    db.commit();db.refresh(x);return x

def transfer(db,user,sender_id,receiver_id,amount,key):
    old=idem(db,user,key,"TRANSFER")
    if old:return db.get(Transfer,old.resource_id)
    if sender_id==receiver_id:raise DomainError("INVALID_TRANSFER","Sender and receiver must differ",400)
    a,b=sorted([sender_id,receiver_id],key=str)
    w1=db.query(Wallet).filter(Wallet.id==a).with_for_update().first()
    w2=db.query(Wallet).filter(Wallet.id==b).with_for_update().first()
    if not w1 or not w2:raise DomainError("WALLET_NOT_FOUND","Wallet not found",404)
    s=w1 if w1.id==sender_id else w2;r=w2 if w2.id==receiver_id else w1
    if s.user_id!=user.id:raise DomainError("FORBIDDEN","Sender wallet does not belong to user",403)
    if s.status!=WalletStatus.ACTIVE or r.status!=WalletStatus.ACTIVE:raise DomainError("WALLET_FROZEN","Both wallets must be active",409)
    if s.currency!=r.currency:raise DomainError("CURRENCY_MISMATCH","Currencies must match",409)
    if Decimal(s.available_balance)<amount:raise DomainError("INSUFFICIENT_BALANCE","Insufficient wallet balance",409)
    x=Transfer(sender_wallet_id=s.id,receiver_wallet_id=r.id,amount=amount,currency=s.currency,status=OperationStatus.COMPLETED,reference=f"TRF-{uuid4().hex[:16]}")
    db.add(x);db.flush()
    sb=Decimal(s.available_balance);rb=Decimal(r.available_balance);s.available_balance=sb-amount;r.available_balance=rb+amount
    db.add(Transaction(wallet_id=s.id,transaction_type=TransactionType.TRANSFER_DEBIT,amount=-amount,balance_before=sb,balance_after=s.available_balance,reference_entity="transfer",reference_id=str(x.id),description="Transfer sent",created_by=user.id))
    db.add(Transaction(wallet_id=r.id,transaction_type=TransactionType.TRANSFER_CREDIT,amount=amount,balance_before=rb,balance_after=r.available_balance,reference_entity="transfer",reference_id=str(x.id),description="Transfer received",created_by=user.id))
    db.add(IdempotencyKey(user_id=user.id,key=key,operation="TRANSFER",resource_id=str(x.id)));note(db,user.id,"Transfer completed",x.reference)
    if r.user_id!=user.id:note(db,r.user_id,"Transfer received",f"{amount} {s.currency} received")
    db.commit();db.refresh(x);return x
