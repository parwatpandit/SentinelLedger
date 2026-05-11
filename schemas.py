from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    account_number: int
    username: str
    email: str
    balance: float
    is_active: bool
    created_at: datetime
    model_config = {"from_attributes": True}

class TransferRequest(BaseModel):
    sender_account: int
    receiver_account: int
    amount: float = Field(..., gt=0)
    request_id: str
    category: Optional[str] = None

class TransactionResponse(BaseModel):
    id: int
    sender_account: int
    receiver_account: int
    amount: float
    status: str
    request_id: str
    category: Optional[str] = None
    created_at: datetime
    model_config = {"from_attributes": True}

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class DailyLimitRequest(BaseModel):
    daily_limit: float = Field(..., gt=0)

class ScheduledPaymentRequest(BaseModel):
    sender_account: int
    receiver_account: int
    amount: float = Field(..., gt=0)
    scheduled_date: datetime