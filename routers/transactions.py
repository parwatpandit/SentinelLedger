from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User, Transaction
from schemas import TransferRequest, TransactionResponse
from routers.users import get_current_user

router = APIRouter(tags=["Transactions"])

@router.post("/transfer")
def transfer(data: TransferRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if db.query(Transaction).filter(Transaction.request_id == data.request_id).first():
        raise HTTPException(status_code=400, detail="Duplicate transaction")
    if current_user.account_number != data.sender_account:
        raise HTTPException(status_code=403, detail="Unauthorized transfer")
    if data.amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid amount")
    receiver = db.query(User).filter(User.account_number == data.receiver_account).first()
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver not found")
    if current_user.balance < data.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    try:
        current_user.balance -= data.amount
        receiver.balance += data.amount
        txn = Transaction(
            sender_account=data.sender_account,
            receiver_account=data.receiver_account,
            amount=data.amount,
            request_id=data.request_id,
            status="success"
        )
        db.add(txn)
        db.commit()
        return {"message": "Transfer successful", "new_balance": current_user.balance}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/transactions", response_model=list[TransactionResponse])
def get_transactions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Transaction).filter(
        (Transaction.sender_account == current_user.account_number) |
        (Transaction.receiver_account == current_user.account_number)
    ).all()