# SentinelLedger 🏦

> A production-grade banking web application built with FastAPI, PostgreSQL, Redis, Docker, and Machine Learning fraud detection — deployed live on AWS.

---

## What is SentinelLedger?

SentinelLedger is a full-stack fintech application that simulates a real banking system. It was built from scratch as a learning project to develop job-ready skills in backend development, cloud deployment, and machine learning. The application handles user authentication, money transfers, deposits, transaction history, admin controls, and real-time fraud detection — all running live on AWS.

---

## Live Demo

| Service | URL |
|---|---|
| Backend API | http://18.130.226.110:8000 |
| API Documentation | http://18.130.226.110:8000/docs |
| Frontend | http://sentinelledger-frontend.s3-website.eu-west-2.amazonaws.com |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python 3.13) |
| Database | PostgreSQL 17 |
| Caching | Redis 7 |
| Authentication | JWT + Argon2 password hashing |
| Machine Learning | scikit-learn (Random Forest) |
| Containerisation | Docker + Docker Compose |
| Cloud | AWS EC2 + ECR + S3 |
| Frontend | HTML, CSS, JavaScript |

---

## Features

### Core Banking
- User registration with auto-generated 10-digit account numbers
- Secure login with JWT authentication
- Real-time balance checking with Redis caching
- Money transfers between accounts with idempotency keys (no duplicate transactions)
- Deposit endpoint
- Full transaction history

### Security
- Argon2 password hashing (2025 industry standard)
- JWT tokens on all protected routes
- Rate limiting to prevent abuse (slowapi)
- Environment variables for all secrets — nothing hardcoded

### ML Fraud Detection
- Random Forest model trained on 2000 transactions with 99% accuracy
- SMOTE technique to handle imbalanced data (fraud is rare)
- Personalised detection — learns each user's spending pattern from their last 10 transactions
- Flags transactions that deviate significantly from a user's normal behaviour
- Absolute hard limit — any transaction over £1500 is automatically blocked
- Risk scoring from 0 to 100
- Three risk levels: low, medium, high
- Clear reason returned for every flagged transaction (e.g. "£886 above normal spending pattern")
- High risk transactions are blocked; medium risk transactions are flagged for admin review

### Admin Dashboard
- View all users and transactions
- Block and unblock user accounts
- View all flagged transactions

### Real-Time Updates
- WebSocket connections for instant balance updates when money is received

### Infrastructure
- Fully Dockerised with Dockerfile and docker-compose.yml
- Deployed on AWS EC2 (t3.micro, eu-west-2 London)
- Docker images stored in AWS ECR
- Frontend hosted on AWS S3
- All three services (app, PostgreSQL, Redis) run as Docker containers with auto-restart

---

## Project Structure

```
SentinelLedger/
├── main.py                  # App entry point, middleware, WebSocket
├── database.py              # PostgreSQL connection
├── models.py                # SQLAlchemy database models
├── schemas.py               # Pydantic validation schemas
├── connections.py           # WebSocket connection store
├── fraud_detection.py       # ML fraud detection logic
├── train_model.py           # Model training script
├── fraud_model.pkl          # Trained Random Forest model
├── .env                     # Environment variables (never committed)
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker image definition
├── docker-compose.yml       # Local multi-container setup
├── routers/
│   ├── auth.py              # Register and login endpoints
│   ├── users.py             # Balance endpoint + auth dependency
│   ├── transactions.py      # Transfer, deposit, transaction history
│   └── admin.py            # Admin-only endpoints
├── utils/
│   └── auth.py              # Password hashing and JWT utilities
├── tests/
│   └── test_api.py          # pytest test suite
└── frontend/
    ├── index.html           # Login page
    ├── register.html        # Registration page
    ├── dashboard.html       # User dashboard
    ├── style.css            # Styles
    └── script.js            # Frontend logic + WebSocket
```

---

## How the Fraud Detection Works

Every time a user makes a transfer, the system runs it through a Machine Learning model before processing it.

**Step 1 — Build a spending profile**
The system fetches the user's last 10 transactions and calculates their average spend. For example, if a user normally sends £10–£20, their typical amount is around £15.

**Step 2 — Extract features**
The model looks at four things: the transaction amount, the hour of the day, how many transactions the user has made, the ratio of the amount to their balance, and how far the amount deviates from their normal pattern.

**Step 3 — Predict**
The Random Forest model returns a fraud probability (0.0 to 1.0), which is converted to a risk score out of 100.

**Step 4 — Take action**
- Risk score below 30 → transaction goes through as normal
- Risk score 30–70 → transaction goes through but is saved as "flagged" for admin review
- Risk score above 70 → transaction is blocked entirely with a clear reason

**Example blocked transaction response:**
```json
{
  "detail": "Transaction blocked — high fraud risk. Risk score: 100.0 | Reason: £886.75 above normal spending pattern"
}
```

---

## API Endpoints

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| POST | /register | Create a new user account | No |
| POST | /login | Login and receive JWT token | No |
| GET | /balance | Get current balance | Yes |
| POST | /transfer | Transfer money with fraud check | Yes |
| POST | /deposit | Deposit money | Yes |
| GET | /transactions | Get transaction history | Yes |
| GET | /admin/users | View all users | Admin only |
| GET | /admin/transactions | View all transactions | Admin only |
| PUT | /admin/block/{account} | Block a user | Admin only |
| PUT | /admin/unblock/{account} | Unblock a user | Admin only |

---

## Running Locally

**Prerequisites:** Python 3.13, PostgreSQL, Redis, Docker

```bash
# Clone the repository
git clone https://github.com/parwatpandit/SentinelLedger.git
cd SentinelLedger

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database credentials

# Run the app
uvicorn main:app --reload
```

Or with Docker Compose:

```bash
docker-compose up --build
```

---

## Deploying to AWS

```bash
# Build and push Docker image to ECR
aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin 369504341737.dkr.ecr.eu-west-2.amazonaws.com
docker buildx build --platform linux/amd64 -t sentinelledger:amd64 --load .
docker tag sentinelledger:amd64 369504341737.dkr.ecr.eu-west-2.amazonaws.com/sentinelledger:amd64
docker push 369504341737.dkr.ecr.eu-west-2.amazonaws.com/sentinelledger:amd64

# SSH into EC2 and pull the new image
ssh -i sentinelledger-key.pem ubuntu@18.130.226.110
```

---

## Running Tests

```bash
pytest tests/test_api.py -v
```

---

## What I Learned

Building SentinelLedger took me from zero to deploying a production-grade application on AWS. Along the way I learned FastAPI and REST API design, relational database design with PostgreSQL, JWT authentication and secure password hashing, Redis caching for performance, Docker containerisation, AWS EC2, ECR, and S3 deployment, machine learning with scikit-learn including handling imbalanced datasets with SMOTE, and how real banking systems detect fraud using behavioural analysis.

---

## Roadmap

- [x] Core banking API
- [x] JWT authentication
- [x] PostgreSQL database
- [x] Redis caching
- [x] Rate limiting
- [x] Docker containerisation
- [x] AWS deployment
- [x] ML fraud detection
- [ ] Kubernetes orchestration with Minikube
- [ ] HTTPS with SSL certificate
- [ ] Email notifications for flagged transactions

---

## Author

**Parwat Pandit**
Aspiring Full Stack / Fintech Developer — London
GitHub: https://github.com/parwatpandit/SentinelLedger

---

*Built as a portfolio project to demonstrate real-world full stack and fintech development skills.*