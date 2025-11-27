# --- Standard library imports ---
from typing import Callable, Optional

# --- Third-party imports ---
from rich.table import Table
from rich.console import Console

# --- Internal imports (app) ---
from .. import db
from ..domain.User import User
from ..service import user_service, portfolio_service


class MenuFunctions:
    def sell_from_portfolio(self, username: str, symbol: str, qty: int, portfolio_id: int, sale_price: float = None):
        """Sell a quantity of symbol for a user from a specific portfolio."""
        return portfolio_service.sell_from_portfolio(username, symbol, qty, portfolio_id, sale_price)
    def buy_to_portfolio(self, username: str, symbol: str, qty: int, portfolio_id: int):
        """Buy a quantity of symbol for a user into a specific portfolio."""
        return portfolio_service.buy_to_portfolio(username, symbol, qty, portfolio_id)
    def __init__(
        self,
        executor: Optional[Callable] = None,
        printer: Optional[Callable] = None,
        navigator: Optional[Callable] = None,
    ):
        self.executor = executor
        self.printer = printer
        self.navigator = navigator

    def view_users(self):
        """Render a table of all users to the configured printer."""
        users = user_service.list_users()
        table = Table(title="Users")
        table.add_column("Username", style="cyan", no_wrap=True)
        table.add_column("First Name", style="magenta")
        table.add_column("Last Name", style="magenta")
        table.add_column("Balance", justify="right")
        table.add_column("Role", style="green")

        for u in users:
            table.add_row(u.username, u.first_name, u.last_name, f"{u.balance:.2f}", u.role)

        if self.printer:
            self.printer(table)
        else:
            Console().print(table)

    # ---------- Portfolio / Marketplace ----------
    def view_portfolio(self, username: str):
        """Render a portfolio table for a user."""
        user = user_service.get_user(username)
        if not user:
            if self.printer:
                self.printer(f"[red]User '{username}' not found.[/]")
            return
        table = Table(title=f"Portfolio: {username}")
        table.add_column("Symbol", style="cyan")
        table.add_column("Quantity", justify="right")
        table.add_column("Estimated Value", justify="right")
        # price lookup -- use centralized provider so mocking/live switch is easy
        price_map = portfolio_service.get_price_map()

        total = 0.0
        for sym, qty in (user.portfolio or {}).items():
            price = price_map.get(sym, 0.0)
            value = price * qty
            total += value
            table.add_row(sym, str(qty), f"{value:.2f}")
        table.add_row("", "Total", f"{total:.2f}")

        if self.printer:
            self.printer(table)
        else:
            Console().print(table)

    def list_market(self):
        # static market for demo (uses mocked prices). Keep at least 3 securities.
        def _render_for(username: str | None = None):
            """Internal renderer for the market table. If username provided, shows owned counts."""
            table = Table(title="Market Place")
            table.add_column("Symbol", style="cyan")
            table.add_column("Price", justify="right")
            table.add_column("Owned", justify="right")
            price_map = portfolio_service.get_price_map()
            market = list(price_map.items())
            owned_map = {}
            if username:
                u = user_service.get_user(username)
                if u:
                    owned_map = u.portfolio or {}

            for s, p in market:
                owned = owned_map.get(s, 0)
                table.add_row(s, f"{p:.2f}", str(owned))
            if self.printer:
                self.printer(table)
            else:
                Console().print(table)

        # keep backwards compatibility: if printer was called without args, render global market
        # API: list_market(username=None)
        return _render_for

    def buy(self, username: str, symbol: str, qty: int) -> bool:
        """Buy a quantity of symbol for a user."""
        # returns (ok, reason)
        return portfolio_service.buy(username, symbol, qty)

    def sell(self, username: str, symbol: str, qty: int) -> bool:
        """Sell a quantity of symbol for a user."""
        # returns (ok, reason)
        return portfolio_service.sell(username, symbol, qty)

    def add_user(self, username: str, password: str, first_name: str, last_name: str, role: str = "user") -> bool:
        """Add a user via the user service."""
        return user_service.add_user(username, password, first_name, last_name, role)

    def get_price_map(self) -> dict:
        """Return the current price map (mocked or live depending on service flag)."""
        return portfolio_service.get_price_map()

    def delete_user(self, username: str) -> bool:
        """Delete a user via the user service."""
        return user_service.delete_user(username)

    def change_role(self, username: str, new_role: str) -> bool:
        """Change a user's role via the user service."""
        return user_service.change_role(username, new_role)
