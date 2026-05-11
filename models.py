from sqlalchemy import Column, Integer, BigInteger, String, Float, DateTime, Boolean
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    account_number = Column(BigInteger, unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    balance = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    failed_attempts = Column(Integer, default=0)
    locked_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    sender_account = Column(BigInteger, nullable=False)
    receiver_account = Column(BigInteger, nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String(20), default="success")
    request_id = Column(String(50), unique=True, nullable=False)
    category = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), nullable=False)
    token = Column(String(100), unique=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class OTPCode(Base):
    __tablename__ = "otp_codes"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), nullable=False)
    code = Column(String(6), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    admin_username = Column(String(50), nullable=False)
    action = Column(String(100), nullable=False)
    target = Column(String(100), nullable=False)
    details = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class DailyLimit(Base):
    __tablename__ = "daily_limits"
    id = Column(Integer, primary_key=True, index=True)
    account_number = Column(BigInteger, unique=True, nullable=False)
    daily_limit = Column(Float, default=2000.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ScheduledPayment(Base):
    __tablename__ = "scheduled_payments"
    id = Column(Integer, primary_key=True, index=True)
    sender_account = Column(BigInteger, nullable=False)
    receiver_account = Column(BigInteger, nullable=False)
    amount = Column(Float, nullable=False)
    scheduled_date = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())