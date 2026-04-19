from fastapi import FastAPI, WebSocket, Request
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
from routers import auth, users, transactions, admin
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import json

Base.metadata.create_all(bind=engine)

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="SentinelLedger", version="2.0")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

connections = {}

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admin.router)

@app.get("/")
@limiter.limit("5/minute")
def root(request: Request):
    return {"message": "SentinelLedger v2 is running!"}

@app.websocket("/ws/{account_number}")
async def websocket_endpoint(websocket: WebSocket, account_number: int):
    await websocket.accept()
    connections[account_number] = websocket
    try:
        while True:
            await websocket.receive_text()
    except:
        connections.pop(account_number, None)