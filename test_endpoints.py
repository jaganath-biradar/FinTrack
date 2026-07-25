import httpx
import json
import traceback

base_url = "http://127.0.0.1:8000"

paths = [
    ("/", "GET", None),
    ("/login", "GET", None),
    ("/dashboard", "GET", None),
    ("/expenses", "GET", None),
    ("/income", "GET", None),
    ("/budget", "GET", None),
    ("/investments", "GET", None),
    ("/savings-goals", "GET", None),
    ("/reports", "GET", None),
]

print("=" * 70)
print("Testing Application Endpoints")
print("=" * 70)

for path, method, data in paths:
    try:
        if method == "GET":
            r = httpx.get(f"{base_url}{path}", follow_redirects=False, timeout=5)
        print(f"{method:6} {path:25} -> {r.status_code}")
        
        if r.status_code >= 500:
            print(f"       ERROR RESPONSE:")
            print(f"       {r.text[:300]}")
            
    except Exception as e:
        print(f"{method:6} {path:25} -> EXCEPTION: {str(e)}")
        traceback.print_exc()

print("=" * 70)
