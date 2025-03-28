from datetime import datetime
from pydantic import BaseModel


class WalletRequest(BaseModel):
    """Wallet request schema."""

    wallet_address: str


class WalletDataResponse(BaseModel):
    """Wallet data response schema."""

    wallet_address: str
    created_at: datetime


class WalletInfoResponse(BaseModel):
    """Wallet info response schema."""

    wallet_address: str
    trx_balance: int
    bandwidth: int
    energy: int
