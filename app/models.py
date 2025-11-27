from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class UserModel(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    balance = Column(Float, nullable=False, default=0.0)
    role = Column(String(20), nullable=False, default='user')
    
    portfolios = relationship('PortfolioModel', back_populates='owner', cascade='all, delete-orphan')
    transactions = relationship('TransactionModel', back_populates='user', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<UserModel(username='{self.username}', role='{self.role}')>"


class PortfolioModel(Base):
    __tablename__ = 'portfolios'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    investment_strategy = Column(String(100))
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    owner = relationship('UserModel', back_populates='portfolios')
    investments = relationship('InvestmentModel', back_populates='portfolio', cascade='all, delete-orphan')
    transactions = relationship('TransactionModel', back_populates='portfolio', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<PortfolioModel(id={self.id}, name='{self.name}')>"


class SecurityModel(Base):
    __tablename__ = 'securities'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(10), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    reference_price = Column(Float, nullable=False)
    
    investments = relationship('InvestmentModel', back_populates='security')
    transactions = relationship('TransactionModel', back_populates='security')
    
    def __repr__(self):
        return f"<SecurityModel(ticker='{self.ticker}', name='{self.name}')>"


class InvestmentModel(Base):
    __tablename__ = 'investments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    portfolio_id = Column(Integer, ForeignKey('portfolios.id', ondelete='CASCADE'), nullable=False)
    security_id = Column(Integer, ForeignKey('securities.id', ondelete='CASCADE'), nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    
    portfolio = relationship('PortfolioModel', back_populates='investments')
    security = relationship('SecurityModel', back_populates='investments')
    
    def __repr__(self):
        return f"<InvestmentModel(portfolio_id={self.portfolio_id}, security_id={self.security_id}, quantity={self.quantity})>"


class TransactionType(enum.Enum):
    BUY = "BUY"
    SELL = "SELL"


class TransactionModel(Base):
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    portfolio_id = Column(Integer, ForeignKey('portfolios.id', ondelete='CASCADE'), nullable=False)
    security_id = Column(Integer, ForeignKey('securities.id', ondelete='CASCADE'), nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    user = relationship('UserModel', back_populates='transactions')
    portfolio = relationship('PortfolioModel', back_populates='transactions')
    security = relationship('SecurityModel', back_populates='transactions')
    
    def __repr__(self):
        return f"<TransactionModel(id={self.id}, type={self.transaction_type.value}, quantity={self.quantity})>"
