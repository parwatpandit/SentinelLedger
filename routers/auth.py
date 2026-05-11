from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
from models import User, PasswordResetToken, OTPCode
from schemas import UserRegister, UserResponse, Token
from utils.auth import hash_password, verify_password, create_access_token, create_refresh_token, verify_refresh_token
from utils.email import send_password_reset_email, send_otp_email
from datetime import datetime, timezone, timedelta
import random
import secrets

router = APIRouter(tags=["Authentication"])

def generate_account_number():
    return random.randint(1000000000, 9999999999)

@router.post("/register", response_model=UserResponse)
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
        balance=1000.0
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if user.locked_at:
        raise HTTPException(status_code=403, detail="Account is locked due to too many failed attempts. Contact support.")

    if not verify_password(form_data.password, user.hashed_password):
        user.failed_attempts += 1
        if user.failed_attempts >= 5:
            user.locked_at = datetime.now(timezone.utc)
            db.commit()
            raise HTTPException(status_code=403, detail="Account locked after 5 failed attempts. Contact support.")
        db.commit()
        raise HTTPException(status_code=401, detail=f"Invalid credentials. {5 - user.failed_attempts} attempts remaining.")

    user.failed_attempts = 0
    user.locked_at = None
    db.commit()

    # Generate 6 digit OTP
    otp_code = str(random.randint(100000, 999999))
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

    otp = OTPCode(
        email=user.email,
        code=otp_code,
        expires_at=expires_at
    )
    db.add(otp)
    db.commit()

    # Send OTP email
    send_otp_email(to=user.email, code=otp_code)

    return {"message": "OTP sent to your email. Use /verify-otp to complete login."}

@router.post("/verify-otp")
def verify_otp(email: str, code: str, db: Session = Depends(get_db)):
    otp = db.query(OTPCode).filter(
        OTPCode.email == email,
        OTPCode.code == code,
        OTPCode.used == False
    ).first()

    if not otp:
        raise HTTPException(status_code=401, detail="Invalid OTP code")

    if otp.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="OTP code has expired")

    otp.used = True
    db.commit()

    user = db.query(User).filter(User.email == email).first()

    access_token = create_access_token({"sub": user.username})
    refresh_token = create_refresh_token({"sub": user.username})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh")
def refresh(refresh_token: str, db: Session = Depends(get_db)):
    username = verify_refresh_token(refresh_token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    new_access_token = create_access_token({"sub": user.username})
    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }

@router.post("/forgot-password")
def forgot_password(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return {"message": "If that email exists, a reset token has been sent"}

    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

    reset_token = PasswordResetToken(
        email=email,
        token=token,
        expires_at=expires_at
    )
    db.add(reset_token)
    db.commit()

    send_password_reset_email(to=email, token=token)

    return {"message": "Password reset email sent"}

@router.post("/reset-password")
def reset_password(token: str, new_password: str, db: Session = Depends(get_db)):
    reset = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == token,
        PasswordResetToken.used == False
    ).first()

    if not reset:
        raise HTTPException(status_code=400, detail="Invalid or already used token")

    if reset.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Reset token has expired")

    user = db.query(User).filter(User.email == reset.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = hash_password(new_password)
    reset.used = True
    db.commit()

    return {"message": "Password reset successful"}