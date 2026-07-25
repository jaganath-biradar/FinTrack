import httpx
import time

# Wait for server to be ready
time.sleep(3)

try:
    r = httpx.get("http://127.0.0.1:8000/login", follow_redirects=False, timeout=10)
    print(f"GET /login -> {r.status_code}")
    if r.status_code >= 500:
        print("ERROR:", r.text[:500])
    else:
        print("✓ SUCCESS: Login page is working!")
        
    # Test register
    r = httpx.get("http://127.0.0.1:8000/register", follow_redirects=False, timeout=10)
    print(f"GET /register -> {r.status_code}")
    if r.status_code >= 500:
        print("ERROR:", r.text[:500])
    else:
        print("✓ SUCCESS: Register page is working!")
        
except Exception as e:
    print(f"ERROR: {e}")
