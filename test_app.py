"""
Simple test script to verify Flask application starts correctly
"""
import sys
print("=" * 60)
print("Testing Flask Application Setup")
print("=" * 60)
# Test 1: Import Flask modules
print("\n1. Testing Flask imports...")
try:
    from flask import Flask, Blueprint, request, jsonify
    print("   ✓ Flask imports successful")
except ImportError as e:
    print(f"   ✗ Flask import failed: {e}")
    sys.exit(1)
# Test 2: Import flask_sqlalchemy
print("\n2. Testing Flask-SQLAlchemy import...")
try:
    from flask_sqlalchemy import SQLAlchemy
    print("   ✓ Flask-SQLAlchemy import successful")
except ImportError as e:
    print(f"   ✗ Flask-SQLAlchemy import failed: {e}")
    sys.exit(1)
# Test 3: Import application modules
print("\n3. Testing application module imports...")
try:
    from app import create_app
    print("   ✓ create_app imported successfully")
except ImportError as e:
    print(f"   ✗ Application import failed: {e}")
    print(f"   Error details: {e}")
    sys.exit(1)
# Test 4: Create application instance
print("\n4. Testing application creation...")
try:
    app = create_app()
    print("   ✓ Flask application created successfully")
    print(f"   App name: {app.name}")
except Exception as e:
    print(f"   ✗ Application creation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
# Test 5: Check routes
print("\n5. Checking registered routes...")
try:
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append(f"{rule.rule} [{', '.join(rule.methods - {'HEAD', 'OPTIONS'})}]")
    if routes:
        print(f"   ✓ Found {len(routes)} routes:")
        for route in sorted(routes):
            print(f"      - {route}")
    else:
        print("   ⚠ No routes registered (blueprint might not be registered)")
except Exception as e:
    print(f"   ✗ Route check failed: {e}")
# Test 6: Check database configuration
print("\n6. Checking database configuration...")
try:
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', 'NOT SET')
    if 'NOT SET' in db_uri:
        print("   ✗ SQLALCHEMY_DATABASE_URI not configured")
    else:
        # Hide password in output
        safe_uri = db_uri.split('@')[0].split(':')[0:2]
        print(f"   ✓ Database configured: {safe_uri[0]}://[user]:[password]@...")
except Exception as e:
    print(f"   ✗ Configuration check failed: {e}")
print("\n" + "=" * 60)
print("Application test complete!")
print("=" * 60)
print("\nTo start the server, run: python run.py")
print("Then visit: http://127.0.0.1:5000/api/users")
print("=" * 60)
