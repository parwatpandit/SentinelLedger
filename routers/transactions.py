from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import User, Transaction, DailyLimit, ScheduledPayment
from schemas import TransferRequest, TransactionResponse, DailyLimitRequest, ScheduledPaymentRequest
from routers.users import get_current_user
from connections import connections
from fraud_detection import check_fraud, get_transaction_hour
from utils.email import send_transfer_received_email, send_flagged_transaction_email
from datetime import datetime, timezone

router = APIRouter(tags=["Transactions"])

VALID_CATEGORIES = ["food", "rent", "shopping", "transport", "entertainment", "health", "education", "other"]

@router.post("/transfer")
async def transfer(
    data: TransferRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if db.query(Transaction).filter(Transaction.request_id == data.request_id).first():
        raise HTTPException(status_code=400, detail="Duplicate transaction")

    if current_user.account_number != data.sender_account:
        raise HTTPException(status_code=403, detail="Unauthorized transfer")

    if data.amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid amount")

    # Validate category
    if data.category and data.category not in VALID_CATEGORIES:
        raise HTTPException(status_code=400, detail=f"Invalid category. Choose from: {VALID_CATEGORIES}")

    receiver = db.query(User).filter(User.account_number == data.receiver_account).first()
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver not found")

    if current_user.balance < data.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    # Check daily limit
    daily_limit_record = db.query(DailyLimit).filter(DailyLimit.account_number == current_user.account_number).first()
    if daily_limit_record:
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        today_spent = db.query(func.sum(Transaction.amount)).filter(
            Transaction.sender_account == current_user.account_number,
            Transaction.created_at >= today_start,
            Transaction.status != "deposit"
        ).scalar() or 0.0

        if today_spent + data.amount > daily_limit_record.daily_limit:
            raise HTTPException(
                status_code=400,
                detail=f"Daily limit of £{daily_limit_record.daily_limit} exceeded. You have spent £{today_spent} today."
            )

    last_transactions = db.query(Transaction).filter(
        Transaction.sender_account == current_user.account_number,
        Transaction.status != "deposit"
    ).order_by(Transaction.created_at.desc()).limit(10).all()

    if last_transactions:
        typical_amount = sum(t.amount for t in last_transactions) / len(last_transactions)
    else:
        typical_amount = data.amount

    daily_frequency = db.query(Transaction).filter(
        Transaction.sender_account == current_user.account_number,
        Transaction.status != "deposit"
    ).count()

    balance_ratio = round(data.amount / current_user.balance, 2) if current_user.balance > 0 else 1.0

    fraud_result = check_fraud(
        amount=data.amount,
        hour=get_transaction_hour(),
        daily_frequency=daily_frequency,
        balance_ratio=balance_ratio,
        typical_amount=typical_amount
    )

    if fraud_result["risk_level"] == "high":
        raise HTTPException(
            status_code=400,
            detail=f"Transaction blocked — high fraud risk. Risk score: {fraud_result['risk_score']} | Reason: {fraud_result['reason']}"
        )

    if fraud_result["risk_level"] == "medium":
        status = "flagged"
    else:
        status = "success"

    try:
        current_user.balance -= data.amount
        receiver.balance += data.amount

        txn = Transaction(
            sender_account=data.sender_account,
            receiver_account=data.receiver_account,
            amount=data.amount,
            request_id=data.request_id,
            status=status,
            category=data.category
        )
        db.add(txn)
        db.commit()

        send_transfer_received_email(
            to=receiver.email,
            amount=data.amount,
            sender_account=data.sender_account
        )

        if status == "flagged":
            send_flagged_transaction_email(
                to=current_user.email,
                amount=data.amount,
                reason=fraud_result["reason"]
            )

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


@router.post("/set-daily-limit")
def set_daily_limit(
    data: DailyLimitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    existing = db.query(DailyLimit).filter(DailyLimit.account_number == current_user.account_number).first()
    if existing:
        existing.daily_limit = data.daily_limit
    else:
        new_limit = DailyLimit(
            account_number=current_user.account_number,
            daily_limit=data.daily_limit
        )
        db.add(new_limit)
    db.commit()
    return {"message": f"Daily limit set to £{data.daily_limit}"}


@router.get("/spending-analytics")
def spending_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    transactions = db.query(Transaction).filter(
        Transaction.sender_account == current_user.account_number,
        Transaction.status != "deposit"
    ).all()

    category_totals = {}
    monthly_totals = {}

    for txn in transactions:
        # Category breakdown
        cat = txn.category or "uncategorized"
        category_totals[cat] = round(category_totals.get(cat, 0) + txn.amount, 2)

        # Monthly breakdown
        month = txn.created_at.strftime("%Y-%m")
        monthly_totals[month] = round(monthly_totals.get(month, 0) + txn.amount, 2)

    return {
        "total_spent": round(sum(category_totals.values()), 2),
        "by_category": category_totals,
        "by_month": monthly_totals
    }


@router.post("/schedule-payment")
def schedule_payment(
    data: ScheduledPaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.account_number != data.sender_account:
        raise HTTPException(status_code=403, detail="Unauthorized")

    if data.scheduled_date <= datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Scheduled date must be in the future")

    receiver = db.query(User).filter(User.account_number == data.receiver_account).first()
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver not found")

    payment = ScheduledPayment(
        sender_account=data.sender_account,
        receiver_account=data.receiver_account,
        amount=data.amount,
        scheduled_date=data.scheduled_date
    )
    db.add(payment)
    db.commit()

    return {"message": f"Payment of £{data.amount} scheduled for {data.scheduled_date}"}


@router.get("/scheduled-payments")
def get_scheduled_payments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    payments = db.query(ScheduledPayment).filter(
        ScheduledPayment.sender_account == current_user.account_number
    ).all()
    return payments