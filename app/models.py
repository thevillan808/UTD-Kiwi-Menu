from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum, Text
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import enum

Base = declarative_base()

# User table
class UserModel(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    balance = Column(Float, nullable=False, default=0.0)
    role = Column(String(20), nullable=False, default='user')
    
    # relationships
    portfolios = relationship('PortfolioModel', back_populates='owner', cascade='all, delete-orphan')
    transactions = relationship('TransactionModel', back_populates='user', cascade='all, delete-orphan')

# Portfolio table
class PortfolioModel(Base):
    __tablename__ = 'portfolios'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    investment_strategy = Column(String(100))
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    # relationships
    owner = relationship('UserModel', back_populates='portfolios')
    investments = relationship('InvestmentModel', back_populates='portfolio', cascade='all, delete-orphan')
    transactions = relationship('TransactionModel', back_populates='portfolio', cascade='all, delete-orphan')

# Security table
class SecurityModel(Base):
    __tablename__ = 'securities'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(10), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    reference_price = Column(Float, nullable=False)
    
    # relationships
    investments = relationship('InvestmentModel', back_populates='security')
    transactions = relationship('TransactionModel', back_populates='security')

# Investment table (portfolio holdings)
class InvestmentModel(Base):
    __tablename__ = 'investments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    portfolio_id = Column(Integer, ForeignKey('portfolios.id', ondelete='CASCADE'), nullable=False)
    security_id = Column(Integer, ForeignKey('securities.id', ondelete='CASCADE'), nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    
    # relationships
    portfolio = relationship('PortfolioModel', back_populates='investments')
    security = relationship('SecurityModel', back_populates='investments')

# Transaction type enum
class TransactionType(enum.Enum):
    BUY = "BUY"
    SELL = "SELL"

# Transaction history table
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
    
    # relationships
    user = relationship('UserModel', back_populates='transactions')
    portfolio = relationship('PortfolioModel', back_populates='transactions')
    security = relationship('SecurityModel', back_populates='transactions')

