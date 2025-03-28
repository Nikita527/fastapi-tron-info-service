from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime

from app.models.base import Base


class WalletQuery(Base):
    """WalletQuery model."""

    __tablename__ = "wallet_queries"

    id = Column(Integer, primary_key=True, index=True)
    wallet_address = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        """String representation of the model."""
        return (
            f"<WalletQuery(id={self.id}, "
            f"wallet_address='{self.wallet_address}', "
            f"created_at={self.created_at})>"
        )
