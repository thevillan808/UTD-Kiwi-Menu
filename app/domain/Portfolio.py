from typing import Optional, Dict, Any
from ..exceptions import (
    ValidationException,
    InvalidPortfolioDataException,
    DataCorruptionException
)


class Portfolio:
    def __init__(
        self,
        id: int,
        name: str,
        description: str,
        investment_strategy: str,
        owner_username: str,  # renamed from 'user' to match requirements
        holdings: Dict[str, int] = None,
    ):
        """Portfolio domain model."""
        # Validate ID
        if not isinstance(id, int) or id < 0:
            raise ValidationException("Portfolio ID must be a non-negative integer", "INVALID_PORTFOLIO_ID")
        
        # Validate name
        if not name or not isinstance(name, str) or not name.strip():
            raise InvalidPortfolioDataException("Portfolio name must be a non-empty string", "INVALID_PORTFOLIO_NAME")
        
        # Validate owner_username
        if not owner_username or not isinstance(owner_username, str) or not owner_username.strip():
            raise InvalidPortfolioDataException("Portfolio owner username must be a non-empty string", "INVALID_OWNER_USERNAME")
        
        # Validate holdings
        if holdings is not None:
            if not isinstance(holdings, dict):
                raise InvalidPortfolioDataException("Holdings must be a dictionary", "INVALID_HOLDINGS_TYPE")
            
            for symbol, quantity in holdings.items():
                if not isinstance(symbol, str) or not symbol.strip():
                    raise InvalidPortfolioDataException("Stock symbols must be non-empty strings", "INVALID_STOCK_SYMBOL")
                
                if not isinstance(quantity, int) or quantity < 0:
                    raise InvalidPortfolioDataException("Stock quantities must be non-negative integers", "INVALID_STOCK_QUANTITY")
        
        self.id = id
        self.name = name.strip()
        self.description = description.strip() if description else ""
        self.investment_strategy = investment_strategy.strip() if investment_strategy else ""
        self.owner_username = owner_username.strip()
        self.holdings = holdings if holdings is not None else {}

    def to_dict(self) -> Dict[str, Any]:
        """Serialize portfolio for persistence."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "investment_strategy": self.investment_strategy,
            "owner_username": self.owner_username,
            "holdings": self.holdings,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Portfolio":
        """Deserialize a Portfolio from dict."""
        try:
            if not isinstance(d, dict):
                raise DataCorruptionException("Portfolio data must be a dictionary", "INVALID_PORTFOLIO_DATA_TYPE")
            
            # Validate required fields
            if "id" not in d:
                raise DataCorruptionException("Missing required field: id", "MISSING_PORTFOLIO_ID")
            
            if "name" not in d:
                raise DataCorruptionException("Missing required field: name", "MISSING_PORTFOLIO_NAME")
            
            # Handle both old (user) and new (owner_username) format for backward compatibility
            owner_username = d.get("owner_username") or d.get("user", "")
            if not owner_username:
                raise DataCorruptionException("Missing required field: owner_username", "MISSING_OWNER_USERNAME")
            
            # Validate and convert ID
            try:
                portfolio_id = int(d.get("id"))
            except (ValueError, TypeError):
                raise DataCorruptionException("Portfolio ID must be a valid integer", "INVALID_PORTFOLIO_ID_TYPE")
            
            return Portfolio(
                portfolio_id,
                d.get("name", ""),
                d.get("description", ""),
                d.get("investment_strategy", ""),
                owner_username,
                d.get("holdings", {}),
            )
            
        except (ValidationException, InvalidPortfolioDataException, DataCorruptionException):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            raise DataCorruptionException(f"Failed to deserialize portfolio data: {str(e)}", "PORTFOLIO_DESERIALIZATION_FAILED")
