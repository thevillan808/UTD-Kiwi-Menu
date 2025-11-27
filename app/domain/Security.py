class Security:
    def __init__(self, ticker: str, name: str, reference_price: float):
        """Security domain model."""
        self.ticker = ticker.upper()  # Ensure tickers are uppercase
        self.name = name
        self.reference_price = float(reference_price)

    def __str__(self):
        """String representation for debugging."""
        return f"<Security: {self.ticker} - {self.name} @ ${self.reference_price:.2f}>"

    def to_dict(self) -> dict:
        """Serialize security for persistence."""
        return {
            "ticker": self.ticker,
            "name": self.name,
            "reference_price": self.reference_price,
        }

    @staticmethod
    def from_dict(d: dict) -> "Security":
        """Deserialize a Security from dict."""
        return Security(
            d.get("ticker", ""),
            d.get("name", ""),
            float(d.get("reference_price", 0.0)),
        )