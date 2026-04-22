import pickle
import numpy as np
from datetime import datetime

# Load the trained model once when the app starts
with open("fraud_model.pkl", "rb") as f:
    model = pickle.load(f)

# Absolute hard limit — any transaction over this amount is always flagged
# regardless of the user's spending history
ABSOLUTE_LIMIT = 1500

def check_fraud(amount: float, hour: int, daily_frequency: int, balance_ratio: float, typical_amount: float):
    
    # Hard limit check first — if amount is over £1500 always flag it
    if amount > ABSOLUTE_LIMIT:
        return {
            "is_fraud": True,
            "risk_score": 100.0,
            "risk_level": "high",
            "reason": f"Amount £{amount} exceeds absolute limit of £{ABSOLUTE_LIMIT}"
        }

    # Work out how different this transaction is from the user's normal spending
    deviation_from_normal = round(amount - typical_amount, 2)

    # Put all features into the format the model expects
    features = np.array([[amount, hour, daily_frequency, balance_ratio, deviation_from_normal]])

    # Get the fraud probability (0.0 to 1.0)
    fraud_probability = model.predict_proba(features)[0][1]

    # Get the actual prediction (0 = legit, 1 = fraud)
    prediction = model.predict(features)[0]

    # Convert probability to a risk score out of 100
    risk_score = round(fraud_probability * 100, 2)

    # Work out the reason for flagging
    reason = get_reason(amount, hour, daily_frequency, balance_ratio, deviation_from_normal)

    return {
        "is_fraud": bool(prediction),
        "risk_score": risk_score,
        "risk_level": get_risk_level(risk_score),
        "reason": reason
    }

def get_risk_level(risk_score: float):
    if risk_score < 30:
        return "low"
    elif risk_score < 70:
        return "medium"
    else:
        return "high"

def get_reason(amount, hour, daily_frequency, balance_ratio, deviation_from_normal):
    # Tell the admin exactly why this transaction was flagged
    reasons = []

    if amount > 600:
        reasons.append(f"Large amount £{amount}")
    if hour < 5:
        reasons.append(f"Unusual hour {hour}:00")
    if daily_frequency > 5:
        reasons.append(f"High frequency {daily_frequency} transactions today")
    if balance_ratio > 0.60:
        reasons.append(f"Sending {round(balance_ratio * 100)}% of balance")
    if deviation_from_normal > 500:
        reasons.append(f"£{deviation_from_normal} above normal spending pattern")

    if reasons:
        return " | ".join(reasons)
    return "Normal transaction"

def get_transaction_hour():
    return datetime.now().hour