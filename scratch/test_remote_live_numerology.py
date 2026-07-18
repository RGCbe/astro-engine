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

# Payload
payload = {
    "name": "Joseph Vijay",
    "date": "1974-06-22",
    "target_date": "2026-05-26"
}

print("=== VERIFYING LIVE NUMEROLOGY ENDPOINT ON VPS ===")
ok = test_remote_route("http://46.28.44.225:8000/api/astrology/numerology", payload)

if not ok:
    print("\nRunning loopback verification via SSH...")
    ssh_cmd = [
        "ssh", "root@46.28.44.225",
        "curl -s -X POST -H 'Content-Type: application/json' -d '{\"name\":\"Joseph Vijay\",\"date\":\"1974-06-22\",\"target_date\":\"2026-05-26\"}' http://localhost:8000/api/astrology/numerology"
    ]
    r = subprocess.run(ssh_cmd, capture_output=True, text=True, encoding="utf-8")
    if r.returncode == 0:
        try:
            data = json.loads(r.stdout)
            print(f"[SSH SUCCESS] Numerology live endpoint verified: {data['framework']}")
            print(f"  Vidhi Number: {data['calculations']['tamil_chaldean']['vidhi_number']}")
            print(f"  Pythagorean Expression: {data['calculations']['pythagorean_triad']['expression_number']}")
            print(f"  Lo Shu Grid: {data['calculations']['lo_shu_grid']['grid']}")
        except Exception as err:
            print(f"[SSH FAIL] Parsing error: {err}. Output: {r.stdout[:200]}")
    else:
        print(f"[SSH FAIL] SSH curl execution failed: {r.stderr}")
