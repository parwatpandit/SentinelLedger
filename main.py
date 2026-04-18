from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
from routers import auth, users, transactions
import json

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SentinelLedger", version="2.0")

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
app.include_router(transactions.router)

@app.get("/")
def root():
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