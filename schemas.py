from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# ----- User Schemas -----
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

    class Config:
        from_attributes = True

# ----- Transaction Schemas -----
class TransferRequest(BaseModel):
    sender_account: int
    receiver_account: int
    amount: float = Field(..., gt=0)
    request_id: str

class TransactionResponse(BaseModel):
    id: int
    sender_account: int
    receiver_account: int
    amount: float
    status: str
    request_id: str
    created_at: datetime

    class Config:
        from_attributes = True

# ----- Token Schemas -----
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None