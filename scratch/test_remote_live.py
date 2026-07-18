import json
import urllib.request
import subprocess

def test_remote_route(url, payload):
    headers = {"Content-Type": "application/json"}
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            body = response.read().decode("utf-8")
            data = json.loads(body)
            print(f"[DIRECT SUCCESS] {url} responded: {data.get('framework')}")
            return True
    except Exception as e:
        print(f"[DIRECT FAIL] {url} connection failed: {e}. Falling back to SSH loopback...")
        return False

# Payloads
western_payload = {
    "date": "1974-06-22",
    "time": "12:00",
    "tz_hours": 5.5,
    "lat": 13.0827,
    "lon": 80.2707,
    "age": 52
}
chinese_payload = {
    "date": "1974-06-22",
    "time": "12:00",
    "tz_hours": 5.5
}
mayan_payload = {
    "date": "2012-12-21"
}

print("=== VERIFYING LIVE GAC ENDPOINTS ON VPS ===")
w_ok = test_remote_route("http://46.28.44.225:8000/api/astrology/western", western_payload)
c_ok = test_remote_route("http://46.28.44.225:8000/api/astrology/chinese", chinese_payload)
m_ok = test_remote_route("http://46.28.44.225:8000/api/astrology/mayan", mayan_payload)

# If direct HTTP requests fail (e.g. port 8000 firewall), run verification via SSH loopback
if not (w_ok and c_ok and m_ok):
    print("\nRunning loopback verification via SSH...")
    
    # We will run a python one-liner on the remote machine that imports the endpoints and checks them
    ssh_cmd = [
        "ssh", "root@46.28.44.225",
        "curl -s -X POST -H 'Content-Type: application/json' -d '{\"date\":\"1974-06-22\",\"time\":\"12:00\",\"tz_hours\":5.5,\"lat\":13.0827,\"lon\":80.2707,\"age\":52}' http://localhost:8000/api/astrology/western"
    ]
    r = subprocess.run(ssh_cmd, capture_output=True, text=True, encoding="utf-8")
    if r.returncode == 0:
        try:
            data = json.loads(r.stdout)
            print(f"[SSH SUCCESS] Western live endpoint verified: {data['framework']}")
            print(f"  Lot of Fortune: {data['calculations']['lots']['Part of Fortune']}")
        except Exception as err:
            print(f"[SSH FAIL] Parsing error: {err}. Output: {r.stdout[:200]}")
    else:
        print(f"[SSH FAIL] SSH curl execution failed: {r.stderr}")
