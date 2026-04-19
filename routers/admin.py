from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User, Transaction
from schemas import UserResponse, TransactionResponse
from routers.users import get_current_user

router = APIRouter(prefix="/admin", tags=["Admin"])

def get_admin_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

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
    return {"message": f"User {account_number} has been blocked"}

@router.put("/unblock/{account_number}")
def unblock_user(account_number: int, admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.account_number == account_number).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = True
    db.commit()
    return {"message": f"User {account_number} has been unblocked"}