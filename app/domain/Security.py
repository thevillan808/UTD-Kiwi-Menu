class Security:
    def __init__(self, ticker: str, name: str, reference_price: float):
        self.ticker = ticker.upper()
        self.name = name
        self.reference_price = float(reference_price)

    def __str__(self):
        return f"<Security: {self.ticker} - {self.name} @ ${self.reference_price:.2f}>"

    def to_dict(self) -> dict:
        return {
            "ticker": self.ticker,
            "name": self.name,
            "reference_price": self.reference_price,
        }

    @staticmethod
    def from_dict(d: dict) -> "Security":
        return Security(
            d.get("ticker", ""),
            d.get("name", ""),
            float(d.get("reference_price", 0.0)),
        )