from datetime import datetime
from typing import Literal


class Transaction:
    def __init__(
        self,
        id: int,
        timestamp: datetime,
        type: Literal["BUY", "SELL"],
        portfolio_id: int,
        ticker: str,
        quantity: int,
        price: float,
        subtotal: float,
    ):
        """Transaction domain model for audit purposes."""
        self.id = id
        self.timestamp = timestamp
        self.type = type.upper()  # Ensure BUY/SELL is uppercase
        self.portfolio_id = portfolio_id
        self.ticker = ticker.upper()  # Ensure ticker is uppercase
        self.quantity = quantity
        self.price = float(price)
        self.subtotal = float(subtotal)

    def __str__(self):
        """String representation for debugging."""
        return (
            f"<Transaction {self.id}: {self.type} {self.quantity} {self.ticker} "
            f"@ ${self.price:.2f} = ${self.subtotal:.2f} [{self.timestamp}]>"
        )

    def to_dict(self) -> dict:
        """Serialize transaction for persistence."""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "type": self.type,
            "portfolio_id": self.portfolio_id,
            "ticker": self.ticker,
            "quantity": self.quantity,
            "price": self.price,
            "subtotal": self.subtotal,
        }

    @staticmethod
    def from_dict(d: dict) -> "Transaction":
        """Deserialize a Transaction from dict."""
        # Parse timestamp from ISO format string
        timestamp_str = d.get("timestamp", "")
        if isinstance(timestamp_str, str):
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        else:
            timestamp = datetime.now()

        return Transaction(
            int(d.get("id", 0)),
            timestamp,
            d.get("type", "BUY"),
            int(d.get("portfolio_id", 0)),
            d.get("ticker", ""),
            int(d.get("quantity", 0)),
            float(d.get("price", 0.0)),
            float(d.get("subtotal", 0.0)),
        )