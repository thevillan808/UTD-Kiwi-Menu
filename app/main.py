from .cli.menu_printer import print_menu, route
from .cli import constants
from rich.console import Console
from .config import db

_console = Console()

def main():
	# Session-aware loop: start at LOGIN_MENU and, after successful login, go to MAIN_MENU.
	current_menu = constants.LOGIN_MENU
	logged_in = False
	while True:
		try:
			user_input = print_menu(current_menu)
		except EOFError:
			_console.print("[yellow]Input closed. Exiting...[/]")
			break

		try:
			selection = int(user_input.strip())
		except Exception:
			_console.print(f"[red]Invalid input: {user_input}[/]")
			continue

		result = route(current_menu, selection)

		# Handle navigation sentinels
		if current_menu == constants.LOGIN_MENU:
			if selection == 1 and result == "LOGIN_SUCCESS":
				logged_in = True
				current_menu = constants.MAIN_MENU
				continue
			if selection == 0:
				_console.print("[yellow]Exiting...[/]")
				break

		# If an action returned BACK, go to main menu if logged in, otherwise login
		if result == "BACK":
			current_menu = constants.MAIN_MENU if logged_in else constants.LOGIN_MENU
			continue

		# If user logged out, stop session and go to login
		if not db.get_current_user():
			logged_in = False
			current_menu = constants.LOGIN_MENU
			continue

		# default: stay on main menu when logged in
		if logged_in:
			current_menu = constants.MAIN_MENU
		else:
			current_menu = constants.LOGIN_MENU


if __name__ == "__main__":
	main()
