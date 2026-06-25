import traceback
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app, raise_server_exceptions=False)

paths = [
    "/",
    "/login",
    "/register",
    "/dashboard",
    "/budget",
    "/expenses",
    "/income",
    "/investments",
    "/savings-goals",
    "/reports",
    "/settings",
    "/static/css/style.css",
    "/static/js/app.js",
]

print("=" * 60)
for path in paths:
    try:
        r = client.get(path, follow_redirects=False)
        loc = r.headers.get("location", "")
        print(f"{r.status_code}  {path}  {loc}")
        if r.status_code == 500:
            print(f"  >>> 500 BODY: {r.text[:500]}")
    except Exception as e:
        print(f"EXCEPTION on {path}: {e}")
        traceback.print_exc()
print("=" * 60)

# Test login flow
print("\n--- Testing login form ---")
r = client.post(
    "/auth/login-form",
    data={"username": "test@test.com", "password": "wrongpass"},
    follow_redirects=False,
)
print(f"POST /auth/login-form (bad creds) -> {r.status_code}  {r.headers.get('location','')}")

# Test register flow
print("\n--- Testing register form ---")
r = client.post(
    "/auth/register-form",
    data={"full_name": "Test User", "email": "newuser@test.com", "password": "testpass123"},
    follow_redirects=False,
)
print(f"POST /auth/register-form -> {r.status_code}  {r.headers.get('location','')}")

# Test API routes unauthenticated
print("\n--- API routes (no auth) ---")
for api_path in ["/api/expenses/", "/api/income/", "/api/budgets/", "/api/investments/"]:
    r = client.get(api_path, follow_redirects=False)
    print(f"GET {api_path} -> {r.status_code}  {r.text[:100]}")

print("\nDone.")
