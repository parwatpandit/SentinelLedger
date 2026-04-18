from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db, Base, engine
from models import User, Transaction
from schemas import UserRegister, UserResponse, TransferRequest, TransactionResponse, Token
from utils.auth import hash_password, verify_password, create_access_token, verify_token
import random

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="SentinelLedger", version="2.0")

# ----- CORS -----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# ----- Utilities -----
def generate_account_number():
    return random.randint(1000000000, 9999999999)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    username = verify_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# ----- Routes -----
@app.get("/")
def root():
    return {"message": "SentinelLedger v2 is running!"}

@app.post("/register", response_model=UserResponse)
def register(data: UserRegister, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    user = User(
        account_number=generate_account_number(),
        username=data.username,
        email=data.email,
        hashed_password=hash_password(data.password),
        balance=1000.0  # starter balance
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/balance", response_model=UserResponse)
def get_balance(current_user: User = Depends(get_current_user)):
    return current_user

@app.post("/transfer")
def transfer(data: TransferRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Idempotency check
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

@app.get("/transactions", response_model=list[TransactionResponse])
def get_transactions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Transaction).filter(
        (Transaction.sender_account == current_user.account_number) |
        (Transaction.receiver_account == current_user.account_number)
    ).all()