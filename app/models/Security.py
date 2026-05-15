from __future__ import annotations

from sqlalchemy import Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import db


class Security(db.Model):
    __tablename__ = 'security'
    ticker: Mapped[str] = mapped_column(String(10), primary_key=True)
    issuer: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)

    def __str__(self):
        return f'<Security: ticker={self.ticker}; issuer={self.issuer}; price={self.price}>'

    def __to_dict__(self):
        return {
            'ticker': self.ticker,
            'issuer': self.issuer,
            'price': self.price,
        }

