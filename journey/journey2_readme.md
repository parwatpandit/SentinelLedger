Journey 1 — What You Built From Scratch ✅
The Foundation

Built a full banking backend using FastAPI and Python
Connected it to a MySQL database to store users and transactions
Created a proper folder structure like a real developer

Security

Argon2 password hashing — passwords are never stored as plain text
JWT tokens — users must login to access protected routes
CORS middleware — frontend can talk to backend safely
.env file — secret keys never exposed in code
.gitignore — secrets never pushed to GitHub

Banking Features

Register — creates user with random 10 digit account number
Login — returns a secure token
Balance — check your account balance
Transfer — send money to another account
Transaction history — see all your transactions
Idempotency keys — prevents duplicate transfers

Extra

WebSocket — real time balance updates
Pydantic validation — all inputs validated
pytest — 6 automated tests
Frontend — Login, Register, Dashboard pages
GitHub — all code pushed safely


Journey 2 — What You Added ✅
Phase 5 — Redis Caching

Installed Redis on Mac
Balance endpoint now checks Redis first before hitting database
10x faster balance lookups
Cache expires every 30 seconds

Phase 6 — Rate Limiting

Installed SlowAPI
Users can only hit the API 5 times per minute
Returns 429 error if exceeded
Prevents abuse and attacks

Phase 7 — Deposit Endpoint

Added /deposit endpoint
Users can add money to their account
Tested successfully via Postman

Phase 8 — Admin Dashboard

Added is_admin column to database
Created /admin router
Admin can see all users
Admin can see all transactions
Admin can block and unblock users
Only admin users can access these routes

Phase 9 — PostgreSQL Migration

Moved from MySQL to PostgreSQL
Installed PostgreSQL 17 via installer
Set up pgAdmin 4
Created sentinelledger database
Updated database.py to use PostgreSQL
Tables created automatically by SQLAlchemy

Phase 10 — Docker

Installed Docker Desktop
Created Dockerfile — packages your app
Created docker-compose.yml — runs app + PostgreSQL + Redis together
Created .dockerignore — keeps secrets out of Docker
All 3 services running together with one command

Phase 11 — AWS (In Progress)

Created AWS account
Set up MFA with Google Authenticator
Installed AWS CLI
Next: configure credentials and deploy! 🔄


What You Learned Without Realising 💡

How a real backend is structured
How databases work
How authentication and security works
How caching speeds up apps
How to protect APIs from abuse
How databases are migrated
How apps are containerised with Docker
How cloud deployment works