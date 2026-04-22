from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User, Transaction
from schemas import TransferRequest, TransactionResponse
from routers.users import get_current_user
from connections import connections
from fraud_detection import check_fraud, get_transaction_hour

router = APIRouter(tags=["Transactions"])

@router.post("/transfer")
async def transfer(
    data: TransferRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check for duplicate transaction
    if db.query(Transaction).filter(Transaction.request_id == data.request_id).first():
        raise HTTPException(status_code=400, detail="Duplicate transaction")

    # Make sure the sender is the logged in user
    if current_user.account_number != data.sender_account:
        raise HTTPException(status_code=403, detail="Unauthorized transfer")

    # Make sure amount is valid
    if data.amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid amount")

    # Find the receiver
    receiver = db.query(User).filter(User.account_number == data.receiver_account).first()
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver not found")

    # Check the sender has enough balance
    if current_user.balance < data.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    # Get the user's last 10 real transactions to understand their spending pattern
    last_transactions = db.query(Transaction).filter(
        Transaction.sender_account == current_user.account_number,
        Transaction.status != "deposit"
    ).order_by(Transaction.created_at.desc()).limit(10).all()

    # Calculate their real average spending
    # If they have no history yet, use the current amount as the average
    if last_transactions:
        typical_amount = sum(t.amount for t in last_transactions) / len(last_transactions)
    else:
        typical_amount = data.amount

    # Count how many transactions they made today
    from datetime import date
    today = date.today()
    daily_frequency = db.query(Transaction).filter(
        Transaction.sender_account == current_user.account_number,
        Transaction.status != "deposit"
    ).count()

    # Work out what ratio of their balance they are sending
    balance_ratio = round(data.amount / current_user.balance, 2) if current_user.balance > 0 else 1.0

    # Run the fraud check with real user data
    fraud_result = check_fraud(
        amount=data.amount,
        hour=get_transaction_hour(),
        daily_frequency=daily_frequency,
        balance_ratio=balance_ratio,
        typical_amount=typical_amount
    )

    # If high risk — block the transaction completely
    if fraud_result["risk_level"] == "high":
        raise HTTPException(
        status_code=400,
        detail=f"Transaction blocked — high fraud risk. Risk score: {fraud_result['risk_score']} | Reason: {fraud_result['reason']}"
    )

    # Set the status based on fraud result
    if fraud_result["risk_level"] == "medium":
        status = "flagged"
    else:
        status = "success"

    try:
        # Move the money
        current_user.balance -= data.amount
        receiver.balance += data.amount

        # Save the transaction with the correct status
        txn = Transaction(
            sender_account=data.sender_account,
            receiver_account=data.receiver_account,
            amount=data.amount,
            request_id=data.request_id,
            status=status
        )
        db.add(txn)
        db.commit()

        # Notify both users via WebSocket if they are connected
        if receiver.account_number in connections:
            await connections[receiver.account_number].send_text("update")
        if current_user.account_number in connections:
            await connections[current_user.account_number].send_text("update")

        return {
            "message": "Transfer successful",
            "new_balance": current_user.balance,
            "fraud_check": fraud_result
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/transactions", response_model=list[TransactionResponse])
def get_transactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Transaction).filter(
        (Transaction.sender_account == current_user.account_number) |
        (Transaction.receiver_account == current_user.account_number)
    ).all()


@router.post("/deposit")
def deposit(
    amount: float,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than 0")

    current_user.balance += amount

    txn = Transaction(
        sender_account=current_user.account_number,
        receiver_account=current_user.account_number,
        amount=amount,
        request_id=f"deposit_{current_user.account_number}_{int(amount)}",
        status="deposit"
    )
    db.add(txn)
    db.commit()

    return {"message": "Deposit successful", "new_balance": current_user.balance}