from pydantic import BaseModel


class ErrorResponse(BaseModel):
    error: str
    detail: str


class CreateUserRequest(BaseModel):
    username: str
    password: str
    firstname: str
    lastname: str
    balance: float


class CreatePortfolioRequest(BaseModel):
    username: str
    name: str
    description: str


class BuyTradeRequest(BaseModel):
    ticker: str
    portfolio_id: int
    quantity: int


class SellTradeRequest(BaseModel):
    ticker: str
    portfolio_id: int
    quantity: int


class GrantAccessRequest(BaseModel):
    username: str
    role: str
