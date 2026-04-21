from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import UserResponse
from utils.auth import verify_token
import os
import redis
import json

router = APIRouter(tags=["Users"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Redis connection
r = redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379, db=0, decode_responses=True)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    username = verify_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/balance", response_model=UserResponse)
def get_balance(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cache_key = f"balance:{current_user.account_number}"

    # Check Redis cache first
    cached = r.get(cache_key)
    if cached:
        print("✅ Served from Redis cache")
        return current_user

    # If not in cache, get from MySQL and store in Redis
    r.setex(cache_key, 30, json.dumps({"balance": current_user.balance}))
    print("📦 Served from MySQL, saved to Redis")
    return current_user