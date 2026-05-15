from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import db


class PortfolioAccess(db.Model):
    __tablename__ = 'portfolio_access'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    portfolio_id: Mapped[int] = mapped_column(Integer, ForeignKey('portfolio.id'), nullable=False)
    username: Mapped[str] = mapped_column(String(30), ForeignKey('user.username'), nullable=False)
    # role is either 'viewer' or 'manager'
    role: Mapped[str] = mapped_column(String(20), nullable=False)

    def __to_dict__(self):
        return {
            'id': self.id,
            'portfolio_id': self.portfolio_id,
            'username': self.username,
            'role': self.role,
        }
