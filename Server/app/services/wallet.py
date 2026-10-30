from app.core.enums import WalletStatus
from app.core.exceptions import DomainError
from app.models import Wallet

ALLOWED={WalletStatus.ACTIVE:{WalletStatus.FROZEN,WalletStatus.SUSPENDED,WalletStatus.CLOSED},
WalletStatus.FROZEN:{WalletStatus.ACTIVE,WalletStatus.SUSPENDED},
WalletStatus.SUSPENDED:{WalletStatus.ACTIVE,WalletStatus.CLOSED},WalletStatus.CLOSED:set()}

def create(db,user,currency):
    w=Wallet(user_id=user.id,currency=currency.upper());db.add(w);db.commit();db.refresh(w);return w
def status(db,wid,new):
    w=db.query(Wallet).filter(Wallet.id==wid).with_for_update().first()
    if not w:raise DomainError("WALLET_NOT_FOUND","Wallet not found",404)
    if new not in ALLOWED[WalletStatus(w.status)]:raise DomainError("INVALID_WALLET_STATUS","Invalid wallet state transition",409)
    w.status=new;db.commit();db.refresh(w);return w
