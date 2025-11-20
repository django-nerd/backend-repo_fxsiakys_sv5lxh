import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from database import create_document, get_documents, db
from schemas import Wallet as WalletSchema, Asset as AssetSchema, Transaction as TransactionSchema

app = FastAPI(title="Crypto Wallet Platform API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Crypto Wallet Platform API is running"}

# Health + DB test
@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response

# Simple DTOs for responses if needed
class CreateWallet(BaseModel):
    name: str
    address: str
    chain: Optional[str] = None

class CreateAsset(BaseModel):
    wallet_id: str
    symbol: str
    amount: float

class CreateTransaction(BaseModel):
    wallet_id: str
    type: str
    symbol: str
    amount: float
    tx_hash: Optional[str] = None
    note: Optional[str] = None

# Wallet Endpoints
@app.get("/api/wallets")
def list_wallets(limit: int = Query(default=50, ge=1, le=200)):
    try:
        docs = get_documents("wallet", limit=limit)
        for d in docs:
            d["_id"] = str(d.get("_id"))
        return {"items": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/wallets")
def create_wallet(payload: CreateWallet):
    try:
        # validate
        WalletSchema(**payload.model_dump())
        new_id = create_document("wallet", payload.model_dump())
        return {"id": new_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Asset Endpoints
@app.get("/api/assets")
def list_assets(wallet_id: Optional[str] = None, limit: int = Query(default=200, ge=1, le=500)):
    try:
        filt = {"wallet_id": wallet_id} if wallet_id else {}
        docs = get_documents("asset", filter_dict=filt, limit=limit)
        for d in docs:
            d["_id"] = str(d.get("_id"))
        return {"items": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/assets")
def create_asset(payload: CreateAsset):
    try:
        AssetSchema(**payload.model_dump())
        new_id = create_document("asset", payload.model_dump())
        return {"id": new_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Transaction Endpoints
@app.get("/api/transactions")
def list_transactions(wallet_id: Optional[str] = None, limit: int = Query(default=200, ge=1, le=500)):
    try:
        filt = {"wallet_id": wallet_id} if wallet_id else {}
        docs = get_documents("transaction", filter_dict=filt, limit=limit)
        for d in docs:
            d["_id"] = str(d.get("_id"))
        return {"items": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/transactions")
def create_transaction(payload: CreateTransaction):
    try:
        TransactionSchema(**payload.model_dump())
        new_id = create_document("transaction", payload.model_dump())
        return {"id": new_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
