#!/usr/bin/env python3
"""Phase 18 Verification: Match, Muhurta, Prashna endpoints."""
import requests, json, sys

BASE = "http://localhost:8000"
ok = 0
total = 0

def test(name, method, url, payload=None):
    global ok, total
    total += 1
    try:
        if method == "GET":
            r = requests.get(url, timeout=15)
        else:
            r = requests.post(url, json=payload, timeout=30)
        if r.status_code == 200:
            data = r.json()
            print(f"  ✅ {name}: HTTP {r.status_code}")
            ok += 1
            return data
        else:
            print(f"  ❌ {name}: HTTP {r.status_code} — {r.text[:200]}")
            return None
    except Exception as e:
        print(f"  ❌ {name}: {e}")
        return None

print("=" * 60)
print("Phase 18 Verification Suite")
print("=" * 60)

# 1. Health
print("\n[1] Health Check")
test("GET /health", "GET", f"{BASE}/health")

# 2. Tools page
print("\n[2] Tools Page (HTML)")
r = requests.get(f"{BASE}/tools", timeout=10)
total += 1
if r.status_code == 200 and "Kundali Match" in r.text:
    print(f"  ✅ GET /tools: HTML served ({len(r.text)} bytes)")
    ok += 1
else:
    print(f"  ❌ GET /tools: {r.status_code}")

# 3. Kundali Match
print("\n[3] Kundali Match API")
match_data = test("POST /api/astrology/match", "POST", f"{BASE}/api/astrology/match", {
    "boy_year": 1992, "boy_month": 6, "boy_day": 15,
    "boy_time": "08:30", "boy_lat": 13.0827, "boy_lon": 80.2707,
    "girl_year": 1994, "girl_month": 3, "girl_day": 22,
    "girl_time": "14:15", "girl_lat": 13.0827, "girl_lon": 80.2707,
})
if match_data:
    k = match_data["kuta"]
    print(f"     Score: {k['total']['score']}/{k['total']['max']} — {k['verdict']}")
    print(f"     Boy: {k['boy_moon_sign']} ({k['boy_nakshatra']})")
    print(f"     Girl: {k['girl_moon_sign']} ({k['girl_nakshatra']})")
    print(f"     Nadi Dosha: {k['nadi_dosha']} | Bhakoot Dosha: {k['bhakoot_dosha']}")
    print(f"     Boy Mangalik: {match_data['boy_mangal_dosha']['is_mangalik']}")
    print(f"     Girl Mangalik: {match_data['girl_mangal_dosha']['is_mangalik']}")

# 4. Muhurta
print("\n[4] Muhurta Finder API")
muhurta_data = test("POST /api/astrology/muhurta", "POST", f"{BASE}/api/astrology/muhurta", {
    "start_date": "2026-06-01",
    "end_date": "2026-06-07",
    "lat": 13.0827, "lon": 80.2707,
    "activity": "marriage",
    "top_n": 5,
})
if muhurta_data:
    print(f"     Activity: {muhurta_data['activity']}")
    print(f"     Windows found: {len(muhurta_data['windows'])}")
    for i, w in enumerate(muhurta_data['windows'][:3]):
        print(f"     #{i+1}: {w['datetime']} — Score {w['score']} ({w['verdict']})")

# 5. Prashna
print("\n[5] Prashna Kundali API")
prashna_data = test("POST /api/astrology/prashna", "POST", f"{BASE}/api/astrology/prashna", {
    "topic": "career",
    "lat": 13.0827, "lon": 80.2707,
})
if prashna_data:
    p = prashna_data["prashna"]
    print(f"     Verdict: {p['kp_verdict']['verdict']}")
    print(f"     Lagna: {p['lagna']}")
    print(f"     Cusp Sub-Lord: {p['kp_verdict']['cusp_sublord']}")
    print(f"     Ruling Planets: {', '.join(p['ruling_planets'])}")

print("\n" + "=" * 60)
print(f"RESULT: {ok}/{total} tests passed")
print("=" * 60)
sys.exit(0 if ok == total else 1)
