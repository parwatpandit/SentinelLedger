import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

def send_email(to: str, subject: str, body: str):
    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.sendmail(EMAIL_ADDRESS, to, msg.as_string())

        print(f"✅ Email sent to {to}")
        return True

    except Exception as e:
        print(f"❌ Email failed: {e}")
        return False

def send_transfer_received_email(to: str, amount: float, sender_account: int):
    subject = "SentinelLedger — You received money"
    body = f"""
Hello,

You have received £{amount} from account {sender_account}.

Log in to your SentinelLedger account to view your updated balance.

SentinelLedger Security Team
"""
    send_email(to, subject, body)

def send_flagged_transaction_email(to: str, amount: float, reason: str):
    subject = "SentinelLedger — Transaction Flagged"
    body = f"""
Hello,

Your transaction of £{amount} has been flagged for review.

Reason: {reason}

If this was you, no action is needed. If you did not make this transaction, please contact support immediately.

SentinelLedger Security Team
"""
    send_email(to, subject, body)

def send_account_blocked_email(to: str):
    subject = "SentinelLedger — Account Blocked"
    body = f"""
Hello,

Your SentinelLedger account has been blocked by an administrator.

If you believe this is a mistake, please contact support.

SentinelLedger Security Team
"""
    send_email(to, subject, body)

def send_password_reset_email(to: str, token: str):
    subject = "SentinelLedger — Password Reset"
    body = f"""
Hello,

You requested a password reset for your SentinelLedger account.

Your reset token is: {token}

This token expires in 1 hour.

If you did not request this, please ignore this email.

SentinelLedger Security Team
"""
    send_email(to, subject, body)

def send_otp_email(to: str, code: str):
    subject = "SentinelLedger — Your Login Code"
    body = f"""
Hello,

Your one time login code is: {code}

This code expires in 10 minutes.

If you did not request this, please ignore this email.

SentinelLedger Security Team
"""
    send_email(to, subject, body)