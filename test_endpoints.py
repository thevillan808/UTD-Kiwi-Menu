import urllib.request
import json

print("Testing Flask API endpoints...")
print("=" * 60)

# Test GET /api/users
try:
    print("\n1. Testing GET /api/users")
    with urllib.request.urlopen('http://127.0.0.1:5000/api/users') as response:
        status = response.status
        data = response.read().decode('utf-8')
        print(f"   Status Code: {status}")
        print(f"   Response: {data[:200]}")
        if status == 200:
            print("   ✓ SUCCESS")
        else:
            print(f"   ✗ FAILED with status {status}")
except Exception as e:
    print(f"   ✗ ERROR: {e}")

# Test GET /api/portfolios
try:
    print("\n2. Testing GET /api/portfolios")
    with urllib.request.urlopen('http://127.0.0.1:5000/api/portfolios') as response:
        status = response.status
        data = response.read().decode('utf-8')
        print(f"   Status Code: {status}")
        print(f"   Response: {data[:200]}")
        if status == 200:
            print("   ✓ SUCCESS")
        else:
            print(f"   ✗ FAILED with status {status}")
except Exception as e:
    print(f"   ✗ ERROR: {e}")

# Test GET /api/securities
try:
    print("\n3. Testing GET /api/securities")
    with urllib.request.urlopen('http://127.0.0.1:5000/api/securities') as response:
        status = response.status
        data = response.read().decode('utf-8')
        print(f"   Status Code: {status}")
        print(f"   Response: {data[:200]}")
        if status == 200:
            print("   ✓ SUCCESS")
        else:
            print(f"   ✗ FAILED with status {status}")
except Exception as e:
    print(f"   ✗ ERROR: {e}")

print("\n" + "=" * 60)
print("API testing complete!")
