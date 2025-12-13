
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .db import db


# User table
class UserModel(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    balance = db.Column(db.Float, nullable=False, default=0.0)
    role = db.Column(db.String(20), nullable=False, default='user')
    portfolios = db.relationship('PortfolioModel', back_populates='owner', cascade='all, delete-orphan')
    transactions = db.relationship('TransactionModel', back_populates='user', cascade='all, delete-orphan')

    def __init__(self, username, password, first_name, last_name, balance=0.0, role='user'):
        self.username = username
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.balance = balance
        self.role = role


# Portfolio table
class PortfolioModel(db.Model):
    __tablename__ = 'portfolios'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    investment_strategy = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    owner = db.relationship('UserModel', back_populates='portfolios')
    investments = db.relationship('InvestmentModel', back_populates='portfolio', cascade='all, delete-orphan')
    transactions = db.relationship('TransactionModel', back_populates='portfolio', cascade='all, delete-orphan')

    def __init__(self, name, description, investment_strategy, user_id):
        self.name = name
        self.description = description
        self.investment_strategy = investment_strategy
        self.user_id = user_id


# Security table
class SecurityModel(db.Model):
    __tablename__ = 'securities'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ticker = db.Column(db.String(10), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    reference_price = db.Column(db.Float, nullable=False)
    investments = db.relationship('InvestmentModel', back_populates='security')
    transactions = db.relationship('TransactionModel', back_populates='security')

    def __init__(self, ticker, name, reference_price):
        self.ticker = ticker
        self.name = name
        self.reference_price = reference_price


# Investment table (portfolio holdings)
class InvestmentModel(db.Model):
    __tablename__ = 'investments'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolios.id', ondelete='CASCADE'), nullable=False)
    security_id = db.Column(db.Integer, db.ForeignKey('securities.id', ondelete='CASCADE'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    portfolio = db.relationship('PortfolioModel', back_populates='investments')
    security = db.relationship('SecurityModel', back_populates='investments')

    def __init__(self, portfolio_id, security_id, quantity=0):
        self.portfolio_id = portfolio_id
        self.security_id = security_id
        self.quantity = quantity


# Transaction type enum
class TransactionType(enum.Enum):
    BUY = "BUY"
    SELL = "SELL"

# Transaction history table
class TransactionModel(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolios.id', ondelete='CASCADE'), nullable=False)
    security_id = db.Column(db.Integer, db.ForeignKey('securities.id', ondelete='CASCADE'), nullable=False)
    transaction_type = db.Column(db.Enum(TransactionType), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user = db.relationship('UserModel', back_populates='transactions')
    portfolio = db.relationship('PortfolioModel', back_populates='transactions')
    security = db.relationship('SecurityModel', back_populates='transactions')

    def __init__(self, user_id, portfolio_id, security_id, transaction_type, quantity, price, timestamp=None):
        self.user_id = user_id
        self.portfolio_id = portfolio_id
        self.security_id = security_id
        self.transaction_type = transaction_type
        self.quantity = quantity
        self.price = price
        self.timestamp = timestamp or datetime.utcnow()

