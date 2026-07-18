import json
import urllib.request
import subprocess

url = "http://46.28.44.225:8000/api/jathagam"
payload = {
    "year": 1990,
    "month": 5,
    "day": 15,
    "time": "10:30",
    "lat": 13.0827,
    "lon": 80.2707,
    "focus": "general"
}

headers = {"Content-Type": "application/json"}
req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)

print(f"Sending request to live VPS endpoint: {url} ...")
try:
    with urllib.request.urlopen(req, timeout=15) as response:
        status = response.getcode()
        body = response.read().decode("utf-8")
        data = json.loads(body)
        print(f"Status Code: {status}")
        if data.get("status") == "success":
            print("[SUCCESS] Live VPS API responded successfully!")
            print(f"Keys present: jaimini_analysis={ 'jaimini_analysis' in data }, tajika_analysis={ 'tajika_analysis' in data }, nadi_analysis={ 'nadi_analysis' in data }")
        else:
            print(f"[FAIL] Live VPS API responded with: {data}")
except Exception as e:
    print(f"HTTP Connection directly failed: {e}")
    print("Attempting validation via SSH command...")
    
    # Fallback: run curl over SSH via Python subprocess
    cmd = [
        "ssh", "root@46.28.44.225",
        "curl -s -X POST -H 'Content-Type: application/json' -d '{\"year\":1990,\"month\":5,\"day\":15,\"time\":\"10:30\",\"lat\":13.0827,\"lon\":80.2707,\"focus\":\"general\"}' http://localhost:8000/api/jathagam"
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if r.returncode == 0:
        try:
            data = json.loads(r.stdout)
            print("[SUCCESS] Live VPS API validated via SSH loopback curl!")
            print(f"Keys present:")
            print(f"  - jaimini_analysis: { 'jaimini_analysis' in data }")
            print(f"  - tajika_analysis:  { 'tajika_analysis' in data }")
            print(f"  - nadi_analysis:    { 'nadi_analysis' in data }")
            if 'jaimini_analysis' in data:
                print(f"Jaimini status: {data['jaimini_analysis'].get('status')}")
                print(f"Jaimini karakas computed: {len(data['jaimini_analysis'].get('summary', {}).get('chara_karakas', []))}")
            if 'tajika_analysis' in data:
                print(f"Tajika status: {data['tajika_analysis'].get('status')}")
                print(f"Tajika Varsha Lord: {data['tajika_analysis'].get('varshesha')}")
            if 'nadi_analysis' in data:
                print(f"Nadi status: {data['nadi_analysis'].get('status')}")
                print(f"Nadi narratives: {len(data['nadi_analysis'].get('narrative', {}))}")
        except Exception as err:
            print(f"JSON parsing error: {err}. Output was: {r.stdout[:200]}")
    else:
        print(f"SSH execution failed: {r.stderr}")
