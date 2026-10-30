from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel,EmailStr,Field
from app.core.enums import Role,WalletStatus,TransactionType

class Register(BaseModel):
    email:EmailStr; full_name:str=Field(min_length=2,max_length=120); password:str=Field(min_length=8)
class Login(BaseModel): email:EmailStr; password:str
class Refresh(BaseModel): refresh_token:str
class Tokens(BaseModel):
    access_token:str; refresh_token:str; token_type:str="bearer"
class UserOut(BaseModel):
    id:UUID; email:EmailStr; full_name:str; role:Role; is_active:bool
    model_config={"from_attributes":True}
class WalletCreate(BaseModel): currency:str="INR"
class WalletOut(BaseModel):
    id:UUID; user_id:UUID; currency:str; available_balance:Decimal; pending_balance:Decimal; status:WalletStatus
    model_config={"from_attributes":True}
class Money(BaseModel): amount:Decimal=Field(gt=0,max_digits=20,decimal_places=2)
class TransferIn(BaseModel):
    sender_wallet_id:UUID; receiver_wallet_id:UUID; amount:Decimal=Field(gt=0,max_digits=20,decimal_places=2)
class TransactionOut(BaseModel):
    id:UUID; wallet_id:UUID; transaction_type:TransactionType; amount:Decimal; balance_before:Decimal; balance_after:Decimal
    reference_entity:str|None; reference_id:str|None; description:str|None
    model_config={"from_attributes":True}
class RefundIn(BaseModel):
    transaction_id:UUID; amount:Decimal=Field(gt=0); reason:str=Field(min_length=3,max_length=500)
