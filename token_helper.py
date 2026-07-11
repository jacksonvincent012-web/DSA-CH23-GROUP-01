import urllib.request, json

BASE = "http://localhost:5000"

req = urllib.request.Request(f"{BASE}/api/auth/login",
    data=json.dumps({"email":"admin@stockquery.io","password":"admin123"}).encode(),
    headers={"Content-Type": "application/json"})
token = json.loads(urllib.request.urlopen(req).read())["access_token"]
print(token)
