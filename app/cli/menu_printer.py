from typing import Dict, Callable
from rich.console import Console
from rich.table import Table
from . import constants
from ..domain.MenuFunctions import MenuFunctions
from .. import data_access as db
from ..service import portfolio_service

_console = Console()

# Menus
_menus: Dict[int, str] = {
    constants.LOGIN_MENU: """----
Welcome to Kiwi
----
1. Login
0. Exit
""",
    constants.MAIN_MENU: """----
Main Menu
----
1. Manage Users (Admin Only)
2. Portfolios
3. Market Place
0. Logout
""",
    # update Main Menu text to include View Portfolios (option 4)
    # (we'll update the string below in-place when constructing menus)
    constants.MANAGE_USERS_MENU: """----
Manage Users
----
1. View users
2. Add user
3. Delete user
4. Change role
0. Back to main menu
"""
,
    # PORTFOLIO_MENU removed — use VIEW_PORTFOLIO_MENU as the single portfolios menu
    constants.MARKETPLACE_MENU: """----
Market Place
----
1. List market
2. Buy
3. Sell
4. Toggle live prices
0. Back to main menu
""",
    constants.VIEW_PORTFOLIO_MENU: """----
Portfolio Menu
----
1. View my portfolios
2. Create new portfolio
3. Sell investment
0. Back to main menu
""",
}

# ---------- Stub Functions (replace later with MenuFunctions methods) ----------
def _do_login():
    # Prompt for username and password and authenticate.
    username = _console.input("Username: ")
    password = _console.input("Password: ")
    user = db.authenticate(username, password)
    if user is None:
        _console.print(f"[red]Login failed: invalid username or password.[/]")
        return None
    db.set_current_user(user)
    _console.print(f"[green]Welcome, {user.first_name}![/]")
    # return a sentinel indicating successful login
    return "LOGIN_SUCCESS"

def _logout():
    db.set_current_user(None)
    _console.print("[yellow]Logging out...[/]")

def _manage_users():
    # Permission check: only admin allowed
    current = db.get_current_user()
    if not current or current.role != "admin":
        _console.print("[red]Insufficient permissions to manage users.[/]")
        return
    # show manage users menu
    sel = print_menu(constants.MANAGE_USERS_MENU)
    try:
        s = int(sel.strip())
    except Exception:
        _console.print(f"[red]Invalid selection: {sel}[/]")
        return
    route(constants.MANAGE_USERS_MENU, s)


def _manage_portfolios():
    # kept for compatibility but forwards to the unified portfolios menu
    return _view_portfolios_menu()


def _market_place():
    current = db.get_current_user()
    if not current:
        _console.print("[red]Not logged in.[/]")
        return
    sel = print_menu(constants.MARKETPLACE_MENU)
    try:
        s = int(sel.strip())
    except ValueError:
        _console.print(f"[red]Invalid selection: {sel}[/]")
        return
    return route(constants.MARKETPLACE_MENU, s)


def _view_portfolios_menu():
    sel = print_menu(constants.VIEW_PORTFOLIO_MENU)
    try:
        s = int(sel.strip())
    except Exception:
        _console.print(f"[red]Invalid selection: {sel}[/]")
        return
    return route(constants.VIEW_PORTFOLIO_MENU, s)


def _toggle_live_prices():
    # flip the flag and report current status
    current = portfolio_service.is_using_live_prices()
    portfolio_service.enable_live_prices(not current)
    status = "enabled" if portfolio_service.is_using_live_prices() else "disabled"
    _console.print(f"[green]Live prices {status}[/]")

def _view_users():
    mf = menu_funcs
    mf.view_users()


def _view_my_portfolio():
    current = db.get_current_user()
    if not current:
        _console.print("[red]Not logged in.[/]")
        return
    menu_funcs.view_portfolio(current.username)


def _portfolio_buy():
    current = db.get_current_user()
    if not current:
        _console.print("[red]Not logged in.[/]")
        return
    symbol = _console.input("Symbol (e.g. AAPL): ").strip().upper()
    try:
        qty = int(_console.input("Quantity: ").strip())
    except Exception:
        _console.print("[red]Invalid quantity.[/]")
        return
    try:
        portfolio_id = int(_console.input("Portfolio ID: ").strip())
    except Exception:
        _console.print("[red]Invalid portfolio ID.[/]")
        return
    ok, reason = menu_funcs.buy_to_portfolio(current.username, symbol, qty, portfolio_id)
    if ok:
        _console.print(f"[green]Bought {qty} {symbol} for portfolio {portfolio_id}[/]")
    else:
        _console.print(f"[red]Buy failed: {reason}[/]")


def _portfolio_sell():
    current = db.get_current_user()
    if not current:
        _console.print("[red]Not logged in.[/]")
        return
    symbol = _console.input("Symbol (e.g. AAPL): ").strip().upper()
    try:
        qty = int(_console.input("Quantity: ").strip())
    except Exception:
        _console.print("[red]Invalid quantity.[/]")
        return
    try:
        portfolio_id = int(_console.input("Portfolio ID: ").strip())
    except Exception:
        _console.print("[red]Invalid portfolio ID.[/]")
        return
    sale_price_input = _console.input("Sale price (leave blank for current): ").strip()
    sale_price = None
    if sale_price_input:
        try:
            sale_price = float(sale_price_input)
        except Exception:
            _console.print("[yellow]Invalid sale price, using current price.[/]")
            sale_price = None
    ok, reason = menu_funcs.sell_from_portfolio(current.username, symbol, qty, portfolio_id, sale_price)
    if ok:
        _console.print(f"[green]Sold {qty} {symbol} from portfolio {portfolio_id}[/]")
    else:
        _console.print(f"[red]Sell failed: {reason}[/]")


def _liquidate_investments():
    current = db.get_current_user()
    if not current:
        _console.print("[red]Not logged in.[/]")
        return
    report = portfolio_service.liquidate_investments(current.username)
    # handle special short-circuit reports
    if report.get("error") == "user_not_found":
        _console.print("[red]User not found.[/]")
        return
    if report.get("status") == "no_holdings":
        _console.print("[yellow]No holdings to liquidate.[/]")
        return

    # report per-symbol results
    for sym, data in report.items():
        if not isinstance(data, dict):
            continue
        if data.get("ok"):
            _console.print(f"[green]Sold {data.get('sold')} {sym}[/]")
        else:
            reason = data.get("reason") or "unknown"
            _console.print(f"[red]Failed to sell {sym}: {reason}[/]")


def _sell_investment():
    current = db.get_current_user()
    if not current:
        _console.print("[red]Not logged in.[/]")
        return
    
    try:
        # Show available portfolios first
        _console.print("\n[cyan]Available Portfolios:[/]")
        _list_portfolios_with_values()
        
        # Prompt for Portfolio ID
        portfolio_id_str = input("\nEnter Portfolio ID: ").strip()
        if not portfolio_id_str:
            _console.print("[red]Portfolio ID is required.[/]")
            return
        
        try:
            portfolio_id = int(portfolio_id_str)
        except ValueError:
            _console.print("[red]Portfolio ID must be a number.[/]")
            return
        
        # Prompt for Ticker
        ticker = input("Enter Ticker symbol: ").strip().upper()
        if not ticker:
            _console.print("[red]Ticker symbol is required.[/]")
            return
        
        # Prompt for Quantity
        quantity_str = input("Enter Quantity to sell: ").strip()
        if not quantity_str:
            _console.print("[red]Quantity is required.[/]")
            return
        
        try:
            quantity = int(quantity_str)
            if quantity <= 0:
                _console.print("[red]Quantity must be positive.[/]")
                return
        except ValueError:
            _console.print("[red]Quantity must be a positive number.[/]")
            return
        
        # Prompt for Sale price
        sale_price_str = input("Enter Sale price per unit: ").strip()
        if not sale_price_str:
            _console.print("[red]Sale price is required.[/]")
            return
        
        try:
            sale_price = float(sale_price_str)
            if sale_price <= 0:
                _console.print("[red]Sale price must be positive.[/]")
                return
        except ValueError:
            _console.print("[red]Sale price must be a positive number.[/]")
            return
        
        # Call the sell function
        result = menu_funcs.sell_from_portfolio(current.username, ticker, quantity, portfolio_id, sale_price)
        
        if result:
            _console.print(f"[green]Successfully sold {quantity} shares of {ticker} from portfolio {portfolio_id} at ${sale_price:.2f} per share.[/]")
        else:
            _console.print(f"[red]Failed to sell {ticker} from portfolio {portfolio_id}.[/]")
            
    except KeyboardInterrupt:
        _console.print("\n[yellow]Operation cancelled.[/]")
    except Exception as e:
        _console.print(f"[red]Error during sell operation: {str(e)}[/]")


def _list_portfolios():
    ports = portfolio_service.list_portfolios()
    table = Table(title="Portfolios")
    table.add_column("ID", style="cyan")
    table.add_column("Name")
    table.add_column("Owner")
    table.add_column("Strategy")
    for p in ports:
        table.add_row(str(p.id), p.name, p.owner_username, p.investment_strategy)
    _console.print(table)


def _list_portfolios_with_values():
    current = db.get_current_user()
    if not current:
        _console.print("[red]Not logged in.[/]")
        return
    
    ports = portfolio_service.list_portfolios()
    # Filter portfolios to only show the current user's portfolios
    user_ports = [p for p in ports if p.owner_username == current.username]
    
    table = Table(title=f"My Portfolios ({current.username})")
    table.add_column("ID", style="cyan")
    table.add_column("Owner Username")
    table.add_column("Name")
    table.add_column("Total Holdings Value", justify="right", style="green")
    
    # Get price map for calculating total values
    price_map = portfolio_service.get_price_map()
    
    if not user_ports:
        _console.print(f"[yellow]No portfolios found for user {current.username}.[/]")
        return
    
    for p in user_ports:
        # Calculate total value of holdings
        total_value = 0.0
        for symbol, quantity in (p.holdings or {}).items():
            price = price_map.get(symbol, 0.0)
            total_value += price * quantity
        
        table.add_row(
            str(p.id), 
            p.owner_username, 
            p.name, 
            f"${total_value:.2f}"
        )
    
    _console.print(table)


def create_portfolio():
    current = db.get_current_user()
    if not current:
        _console.print("[red]You must be logged in to create a portfolio.[/]")
        return
    name = _console.input("Portfolio name: ")
    desc = _console.input("Description: ")
    strat = _console.input("Investment strategy: ")
    p = portfolio_service.create_portfolio(name, desc, strat, current.username)
    _console.print(f"[green]Created portfolio id={p.id} for user {current.username}[/]")


def _view_portfolio_by_id():
    try:
        pid = int(_console.input("Portfolio id: ").strip())
    except Exception:
        _console.print("[red]Invalid id.[/]")
        return
    p = portfolio_service.get_portfolio(pid)
    if not p:
        _console.print(f"[red]Portfolio {pid} not found.[/]")
        return
    table = Table(title=f"Portfolio {pid}")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("ID", str(p.id))
    table.add_row("Name", p.name)
    table.add_row("Description", p.description)
    table.add_row("Strategy", p.investment_strategy)
    table.add_row("Owner", p.owner_username)
    _console.print(table)


def _update_portfolio():
    try:
        pid = int(_console.input("Portfolio id to update: ").strip())
    except Exception:
        _console.print("[red]Invalid id.[/]")
        return
    p = portfolio_service.get_portfolio(pid)
    if not p:
        _console.print(f"[red]Portfolio {pid} not found.[/]")
        return
    name = _console.input(f"Name [{p.name}]: ") or p.name
    desc = _console.input(f"Description [{p.description}]: ") or p.description
    strat = _console.input(f"Strategy [{p.investment_strategy}]: ") or p.investment_strategy
    current = db.get_current_user()
    actor = current.username if current else None
    ok = portfolio_service.update_portfolio(pid, actor, name=name, description=desc, investment_strategy=strat)
    if ok:
        _console.print(f"[green]Portfolio {pid} updated.[/]")
    else:
        _console.print(f"[red]Failed to update portfolio {pid}[/]")


def _delete_portfolio():
    try:
        pid = int(_console.input("Portfolio id to delete: ").strip())
    except Exception:
        _console.print("[red]Invalid id.[/]")
        return
    current = db.get_current_user()
    actor = current.username if current else None
    ok = portfolio_service.delete_portfolio(pid, actor)
    if ok:
        _console.print(f"[green]Portfolio {pid} deleted.[/]")
    else:
        _console.print(f"[red]Portfolio {pid} not found.[/]")

def _add_user():
    # interactive prompts
    username = _console.input("New username: ")
    if db.query_user(username):
        _console.print(f"[red]User '{username}' already exists.[/]")
        return
    password = _console.input("Password: ")
    first_name = _console.input("First name: ")
    last_name = _console.input("Last name: ")
    role = _console.input("Role (admin/user) [user]: ") or "user"
    ok = menu_funcs.add_user(username, password, first_name, last_name, role)
    if ok:
        _console.print(f"[green]User '{username}' created with role '{role}'[/]")
    else:
        _console.print(f"[red]Failed to create user '{username}'[/]")

def _delete_user():
    username = _console.input("Username to delete: ")
    confirm = _console.input(f"Are you sure you want to delete '{username}'? (y/N): ")
    if confirm.lower() != 'y':
        _console.print("[yellow]Delete cancelled.[/]")
        return False
    ok = menu_funcs.delete_user(username)
    if ok:
        _console.print(f"[green]User '{username}' deleted.[/]")
    else:
        _console.print(f"[red]Cannot delete '{username}' - user not found or deletion would leave no admins.[/]")

    return ok


def _change_role():
    username = _console.input("Username to change role: ")
    new_role = _console.input("New role (admin/user): ")
    ok = menu_funcs.change_role(username, new_role)
    if ok:
        _console.print(f"[green]User '{username}' role changed to '{new_role}'[/]")
    else:
        _console.print(f"[red]User '{username}' not found or role invalid.[/]")

# Optional: you can inject these later from MenuFunctions
menu_funcs = MenuFunctions(executor=None, printer=_console.print, navigator=None)
# allow menu_funcs to navigate if needed
# navigator will be assigned after route is defined to avoid forward reference

# ---------- Router ----------
# router[menu_id][selection] -> callable
_router: Dict[int, Dict[int, Callable[[], None]]] = {
    constants.LOGIN_MENU: {
        1: _do_login,
        0: _logout,
    },
    constants.MAIN_MENU: {
        1: _manage_users,
        2: _view_portfolios_menu,
        3: _market_place,
        0: _logout,
    },
    # constants.PORTFOLIO_MENU removed; use VIEW_PORTFOLIO_MENU below
    constants.MARKETPLACE_MENU: {
        1: lambda: menu_funcs.list_market()(db.get_current_user().username if db.get_current_user() else None),
        2: _portfolio_buy,
        3: _portfolio_sell,
        4: _toggle_live_prices,
        0: lambda: "BACK",
    },
    constants.VIEW_PORTFOLIO_MENU: {
        1: _list_portfolios_with_values,
        2: create_portfolio,
        3: _sell_investment,
        0: lambda: "BACK",
    },
    constants.MANAGE_USERS_MENU: {
        1: _view_users,
        2: _add_user,
        3: _delete_user,
        4: _change_role,
        0: lambda: "BACK",
    },
}

# ---------- Public API ----------
def print_menu(menu_id: int) -> str:
    _console.print(_menus[menu_id])
    return _console.input(">> ")

def route(menu_id: int, user_selection: int) -> None:
    action = _router.get(menu_id, {}).get(user_selection)
    if action:
        try:
            return action()
        except Exception as e:
            _console.print(f"[red]Error while executing action: {e}[/]")
            return None
    else:
        _console.print(f"[red]Invalid selection: {user_selection}[/]")
        return None

# now that route exists, allow MenuFunctions to use it as navigator
menu_funcs.navigator = route
