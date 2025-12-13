"""
MySQL Connection Tester for Kiwi Portfolio API
Run this to test different MySQL passwords and find the correct one
"""
import pymysql
import sys
def test_connection(password):
    """Test MySQL connection with given password"""
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password=password,
            database='kiwi_portfolio'
        )
        connection.close()
        return True, "Connection successful!"
    except pymysql.err.OperationalError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"
def main():
    print("=" * 60)
    print("MySQL Connection Tester")
    print("=" * 60)
    # Common passwords to try
    common_passwords = [
        "",           # Empty password
        "password",   # Default in config
        "root",       # Common default
        "mysql",      # Another common default
        "admin",      # Sometimes used
        "123456",     # Weak but sometimes used in dev
    ]
    print("\nTesting common passwords...")
    print("-" * 60)
    for pwd in common_passwords:
        pwd_display = f'"{pwd}"' if pwd else "(empty string)"
        success, message = test_connection(pwd)
        if success:
            print(f"✅ SUCCESS with password: {pwd_display}")
            print(f"\n🎉 Use this in your environment:")
            print(f"   set DB_PASSWORD={pwd}")
            print(f"   python run.py")
            return 0
        else:
            print(f"❌ FAILED with password: {pwd_display}")
            print(f"   Error: {message}")
    print("\n" + "=" * 60)
    print("❌ None of the common passwords worked.")
    print("\nNext steps:")
    print("1. Enter your MySQL password manually when prompted")
    print("2. Or reset MySQL root password")
    print("3. Or create a new MySQL user")
    print("=" * 60)
    # Manual entry
    print("\n")
    manual_password = input("Enter MySQL root password to test (or press Enter to skip): ")
    if manual_password:
        success, message = test_connection(manual_password)
        if success:
            print(f"\n✅ SUCCESS!")
            print(f"Use this command: set DB_PASSWORD={manual_password}")
            return 0
        else:
            print(f"\n❌ Failed: {message}")
    return 1
if __name__ == "__main__":
    sys.exit(main())
