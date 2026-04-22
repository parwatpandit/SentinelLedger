import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from imblearn.over_sampling import SMOTE
import pickle
import random

random.seed(42)
np.random.seed(42)

data = []

for i in range(2000):
    # Normal spending pattern for this user (between 20 and 300)
    typical_amount = random.uniform(20, 300)
    
    # The actual amount they are sending right now
    amount = round(random.uniform(1, 2000), 2)
    
    # Hour of the day
    hour = random.randint(0, 23)
    
    # How many transactions they made today
    daily_frequency = random.randint(1, 15)
    
    # What percentage of their balance they are sending
    balance_ratio = round(random.uniform(0.01, 1.0), 2)
    
    # How different is this transaction from their normal spending
    # For example if they normally send 100 and now send 1000, deviation is 900
    deviation_from_normal = round(amount - typical_amount, 2)
    
    # Start as legit
    is_fraud = 0

    # Flag as fraud based on our rules
    if amount > 600 and hour < 5:
        is_fraud = 1
    elif daily_frequency > 5 and amount > 600:
        is_fraud = 1
    elif balance_ratio > 0.60 and amount > 600:
        is_fraud = 1
    elif deviation_from_normal > 400 and amount > 600:
        # This is the new pattern detection
        # User normally spends small amounts but suddenly sending a lot
        is_fraud = 1

    data.append([amount, hour, daily_frequency, balance_ratio, deviation_from_normal, is_fraud])

df = pd.DataFrame(data, columns=[
    "amount",
    "hour", 
    "daily_frequency",
    "balance_ratio",
    "deviation_from_normal",
    "is_fraud"
])

print(f"Total transactions: {len(df)}")
print(f"Fraud cases: {df['is_fraud'].sum()}")
print(f"Legit cases: {len(df) - df['is_fraud'].sum()}")

# Handle imbalanced data with SMOTE
smote = SMOTE(random_state=42)
X = df[["amount", "hour", "daily_frequency", "balance_ratio", "deviation_from_normal"]]
y = df["is_fraud"]
X_resampled, y_resampled = smote.fit_resample(X, y)
print(f"\nAfter SMOTE — Total: {len(X_resampled)}, Fraud: {y_resampled.sum()}")

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X_resampled, y_resampled, test_size=0.2, random_state=42
)

# Train the model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate the model
y_pred = model.predict(X_test)
print("\n── Model Evaluation ──")
print(classification_report(y_test, y_pred))

# Save the model
with open("fraud_model.pkl", "wb") as f:
    pickle.dump(model, f)

print("✅ Model saved as fraud_model.pkl")