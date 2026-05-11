from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User, Transaction, AuditLog
from schemas import UserResponse, TransactionResponse
from routers.users import get_current_user
from utils.email import send_account_blocked_email

router = APIRouter(prefix="/admin", tags=["Admin"])

def get_admin_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

def log_action(db: Session, admin_username: str, action: str, target: str, details: str = None):
    log = AuditLog(
        admin_username=admin_username,
        action=action,
        target=target,
        details=details
    )
    db.add(log)
    db.commit()

@router.get("/users", response_model=list[UserResponse])
def get_all_users(admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    return db.query(User).all()

@router.get("/transactions", response_model=list[TransactionResponse])
def get_all_transactions(admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    return db.query(Transaction).all()

@router.put("/block/{account_number}")
def block_user(account_number: int, admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.account_number == account_number).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    db.commit()
    send_account_blocked_email(to=user.email)
    log_action(db, admin.username, "block_user", str(account_number), f"Blocked user {user.username}")
    return {"message": f"User {account_number} has been blocked"}

@router.put("/unblock/{account_number}")
def unblock_user(account_number: int, admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.account_number == account_number).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = True
    db.commit()
    log_action(db, admin.username, "unblock_user", str(account_number), f"Unblocked user {user.username}")
    return {"message": f"User {account_number} has been unblocked"}

@router.put("/unlock/{account_number}")
def unlock_account(account_number: int, admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.account_number == account_number).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.failed_attempts = 0
    user.locked_at = None
    db.commit()
    log_action(db, admin.username, "unlock_account", str(account_number), f"Unlocked account {user.username}")
    return {"message": f"Account {account_number} has been unlocked"}

@router.put("/reverse/{transaction_id}")
def reverse_transaction(transaction_id: int, admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    txn = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")

    if txn.status != "flagged":
        raise HTTPException(status_code=400, detail="Only flagged transactions can be reversed")

    sender = db.query(User).filter(User.account_number == txn.sender_account).first()
    receiver = db.query(User).filter(User.account_number == txn.receiver_account).first()

    if not sender or not receiver:
        raise HTTPException(status_code=404, detail="Sender or receiver not found")

    # Reverse the money
    receiver.balance -= txn.amount
    sender.balance += txn.amount
    txn.status = "reversed"
    db.commit()

    log_action(db, admin.username, "reverse_transaction", str(transaction_id), f"Reversed £{txn.amount} from account {txn.receiver_account} back to {txn.sender_account}")

    return {"message": f"Transaction {transaction_id} reversed. £{txn.amount} returned to account {txn.sender_account}"}

@router.get("/audit-logs")
def get_audit_logs(admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).all()
    return logs