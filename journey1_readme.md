What We Built — SentinelLedger v2

1. Project Setup

Created a Python virtual environment (venv) to isolate libraries
Installed all required libraries: FastAPI, SQLAlchemy, Pydantic, Argon2, PyMySQL, Uvicorn, python-jose, passlib, cryptography, python-dotenv, pytest, httpx
Created project folder structure with routers/, utils/, tests/, frontend/


2. database.py

Connected Python to MySQL using SQLAlchemy
create_engine — makes the connection
SessionLocal — opens and closes database sessions
Base — every model inherits from this
get_db — gives FastAPI a fresh database connection per request


3. models.py

Defined two database tables using SQLAlchemy ORM:
User table — id, account_number (BigInteger), username, email, hashed_password, balance, is_active, created_at
Transaction table — id, sender_account, receiver_account, amount, status, request_id, created_at
Used BigInteger for account numbers because 10-digit numbers exceed MySQL's INT limit


4. schemas.py

Defined Pydantic models for data validation:
UserRegister — validates username (min 3 chars), email format, password (min 8 chars)
UserLogin — username and password
UserResponse — what we send back to frontend
TransferRequest — validates transfer data, amount must be greater than 0
TransactionResponse — transaction data sent to frontend
Token — JWT token response
Used model_config = {"from_attributes": True} for SQLAlchemy compatibility


5. utils/auth.py

Argon2 password hashing — more secure than bcrypt, 2026 standard
hash_password — converts plain password to secure hash
verify_password — checks plain password against stored hash
JWT tokens — used for login sessions
create_access_token — creates a token when user logs in
verify_token — checks if token is valid on protected routes
All secrets loaded from .env file


6. Routers
Split main.py into clean separate files:
routers/auth.py

POST /register — creates new user, checks for duplicate username/email, hashes password, gives starter balance of £1000
POST /login — verifies credentials, returns JWT token

routers/users.py

get_current_user — dependency that verifies JWT token on every protected route
GET /balance — returns user info and balance (protected)

routers/transactions.py

POST /transfer — sends money between accounts with idempotency check, balance check, and unauthorized transfer prevention
GET /transactions — returns full transaction history for logged in user


7. main.py

Created FastAPI app
Added CORS middleware — allows frontend to talk to backend
Registered all routers
Added WebSocket endpoint /ws/{account_number} — real-time balance updates


8. .env file

Moved all sensitive data out of code:
Database credentials
Secret key for JWT signing
Token expiry time
Added .gitignore to prevent .env being pushed to GitHub


9. Frontend
style.css — dark theme UI with cyan accent colors
index.html — Login page with username and password fields
register.html — Register page with username, email, password fields
dashboard.html — Shows balance card, send money form, transaction history table
script.js

register() — sends POST to /register
login() — sends POST to /login, stores JWT token in localStorage
loadDashboard() — fetches balance and transactions on page load
sendMoney() — sends POST to /transfer with idempotency key (txn_ + timestamp)
fetchTransactions() — gets history and shows sent/received with colours
startWebSocket() — connects to WebSocket, refreshes dashboard on any update
logout() — clears localStorage and redirects to login


10. pytest
Wrote 6 automated tests:

Register new user — passes ✅
Duplicate register blocked — passes ✅
Login works — passes ✅
Wrong password rejected — passes ✅
Balance with token works — passes ✅
Balance without token blocked — passes ✅


Key Concepts You Used
ConceptWhereORMSQLAlchemy models instead of raw SQLHashingArgon2 on passwordsJWTLogin sessions without storing passwordsIdempotencyrequest_id prevents duplicate transfersCORSAllows frontend to call backendWebSocketReal-time balance updates.envSecrets never in codeRoutersClean code structurePydanticAuto validates all incoming datapytestAutomated testing

What You Fixed From Original Code
Original ProblemFixed WithPasswords in URLRequest body with PydanticNo CORSCORSMiddleware addedbcryptArgon2Broken indentationClean structured codeHardcoded DB password.env fileNo tests6 pytest testsEverything in main.pySplit into routersINT for account numbersBigInteger
