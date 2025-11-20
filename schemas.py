"""
Database Schemas for Crypto Wallet Platform

Each Pydantic model below maps to a MongoDB collection (collection name = lowercase class name).
Use these schemas for validating inputs before writing to the database.
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Literal

class Wallet(BaseModel):
    name: str = Field(..., description="Display name for the wallet")
    address: str = Field(..., description="Public address or descriptor for the wallet")
    chain: Optional[str] = Field(None, description="Blockchain network, e.g., Ethereum, Solana")

class Asset(BaseModel):
    wallet_id: str = Field(..., description="ID of the wallet that owns this asset")
    symbol: str = Field(..., description="Asset symbol, e.g., BTC, ETH, SOL")
    amount: float = Field(..., ge=0, description="Amount held")

class Transaction(BaseModel):
    wallet_id: str = Field(..., description="ID of the wallet involved")
    type: Literal['deposit', 'withdraw'] = Field(..., description="Transaction type")
    symbol: str = Field(..., description="Asset symbol")
    amount: float = Field(..., gt=0, description="Amount transacted")
    tx_hash: Optional[str] = Field(None, description="Optional blockchain transaction hash")
    note: Optional[str] = Field(None, description="Optional note")

class User(BaseModel):
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    is_active: bool = Field(True, description="Whether user is active")
