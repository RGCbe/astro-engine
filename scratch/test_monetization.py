#!/usr/bin/env python3
"""Monetization Gating Verification Suite"""
import requests
import json
import sys

# Reconfigure stdout to UTF-8 to prevent cp1252 Windows encoding errors
sys.stdout.reconfigure(encoding='utf-8')

BASE = "http://localhost:8000"
ok = 0
total = 0

def test_endpoint(name, method, url, payload=None, expected_status=200):
    global ok, total
    total += 1
    try:
        if method == "GET":
            r = requests.get(url, timeout=10)
        else:
            r = requests.post(url, json=payload, timeout=20)
        
        if r.status_code == expected_status:
            print(f"  ✅ {name}: HTTP {r.status_code} (Expected {expected_status})")
            ok += 1
            try:
                return r.json()
            except Exception:
                return r.text
        else:
            print(f"  ❌ {name}: HTTP {r.status_code} (Expected {expected_status}) — {r.text[:200]}")
            return None
    except Exception as e:
        print(f"  ❌ {name}: {e}")
        return None

print("=" * 60)
print("Atro Monetization & Gating Verification Suite")
print("=" * 60)

# 1. Health Check
print("\n[1] Health Check")
test_endpoint("GET /health", "GET", f"{BASE}/health", expected_status=200)

# 2. Free Tier Jathagam Payload Restricting
print("\n[2] Free Tier /api/jathagam Payload Verification")
free_jathagam = test_endpoint("POST /api/jathagam (Free Tier)", "POST", f"{BASE}/api/jathagam", {
    "year": 1990, "month": 5, "day": 10, "time": "10:30",
    "lat": 13.0827, "lon": 80.2707
}, expected_status=200)

if free_jathagam:
    total += 1
    kp = free_jathagam.get("kp_analysis", {})
    ab = free_jathagam.get("ashtakavarga", {})
    yogas = free_jathagam.get("detected_yogas", [])
    schedule = free_jathagam.get("dasha_schedule", [])
    
    kp_locked = kp.get("status") == "locked"
    ab_locked = ab.get("status") == "locked"
    yogas_limited = len(yogas) <= 2
    schedule_limited = len(schedule) <= 3
    
    if kp_locked and ab_locked and yogas_limited and schedule_limited:
        print("  ✅ Free Jathagam: Gating constraints successfully applied (KP/Ashtakavarga locked, Yogas/Schedule truncated)")
        ok += 1
    else:
        print(f"  ❌ Free Jathagam Gating: kp_locked={kp_locked}, ab_locked={ab_locked}, yogas_limited={yogas_limited}, schedule_limited={schedule_limited}")

# 3. Professional Tier Jathagam Payload Unlocked
print("\n[3] Professional Tier /api/jathagam Payload Verification")
pro_jathagam = test_endpoint("POST /api/jathagam (Pro Tier)", "POST", f"{BASE}/api/jathagam", {
    "year": 1990, "month": 5, "day": 10, "time": "10:30",
    "lat": 13.0827, "lon": 80.2707, "api_key": "atro_pro_dev_key"
}, expected_status=200)

if pro_jathagam:
    total += 1
    kp = pro_jathagam.get("kp_analysis", {})
    ab = pro_jathagam.get("ashtakavarga", {})
    yogas = pro_jathagam.get("detected_yogas", [])
    
    kp_unlocked = "status" not in kp or kp.get("status") != "locked"
    ab_unlocked = "status" not in ab or ab.get("status") != "locked"
    
    if kp_unlocked and ab_unlocked:
        print("  ✅ Pro Jathagam: All advanced calculations cleanly unlocked and populated")
        ok += 1
    else:
        print(f"  ❌ Pro Jathagam: Failed to unlock. kp={kp.get('status')}, ab={ab.get('status')}")

# 4. Restricted PDF Downloads
print("\n[4] PDF Downloader Authorization Gating")
# Free user should get 403 Forbidden
test_endpoint("POST /api/download-pdf (Free User)", "POST", f"{BASE}/api/download-pdf", {
    "year": 1990, "month": 5, "day": 10, "time": "10:30",
    "lat": 13.0827, "lon": 80.2707
}, expected_status=403)

# Pro user should get 200 OK (will return application/pdf)
test_endpoint("POST /api/download-pdf (Pro User)", "POST", f"{BASE}/api/download-pdf", {
    "year": 1990, "month": 5, "day": 10, "time": "10:30",
    "lat": 13.0827, "lon": 80.2707, "api_key": "atro_pro_dev_key"
}, expected_status=200)

# 5. Restricted Matchmaking Scores
print("\n[5] Matchmaking API Gating")
free_match = test_endpoint("POST /api/astrology/match (Free User)", "POST", f"{BASE}/api/astrology/match", {
    "boy_year": 1992, "boy_month": 6, "boy_day": 15, "boy_time": "08:30", "boy_lat": 13.0827, "boy_lon": 80.2707,
    "girl_year": 1994, "girl_month": 3, "girl_day": 22, "girl_time": "14:15", "girl_lat": 13.0827, "girl_lon": 80.2707,
}, expected_status=200)

if free_match:
    total += 1
    k = free_match.get("kuta", {})
    scores = k.get("scores", {})
    locked = scores.get("graha_maitri", {}).get("score") == "🔒"
    dosha_locked = k.get("nadi_dosha") == "LOCKED - Upgrade to Pro"
    boy_mangal_locked = free_match.get("boy_mangal_dosha", {}).get("is_mangalik") == "LOCKED"
    
    if locked and dosha_locked and boy_mangal_locked:
        print("  ✅ Match Gating: Ashta Koota score details and Mangal Dosha successfully locked")
        ok += 1
    else:
        print(f"  ❌ Match Gating Failure: locked={locked}, dosha_locked={dosha_locked}, boy_mangal_locked={boy_mangal_locked}")

# 6. Restricted Muhurta Windows
print("\n[6] Muhurta Finder Gating")
free_muhurta = test_endpoint("POST /api/astrology/muhurta (Free User)", "POST", f"{BASE}/api/astrology/muhurta", {
    "start_date": "2026-06-01", "end_date": "2026-06-07",
    "lat": 13.0827, "lon": 80.2707, "activity": "marriage"
}, expected_status=200)

if free_muhurta:
    total += 1
    windows = free_muhurta.get("windows", [])
    limited = len(windows) <= 1
    cleared = len(windows) > 0 and not windows[0].get("accepted_factors")
    
    if limited and cleared:
        print("  ✅ Muhurta Gating: Truncated to 1 window and cleared analytical breakdowns")
        ok += 1
    else:
        print(f"  ❌ Muhurta Gating Failure: limited={limited}, cleared={cleared}")

# 7. Restricted Prashna Horary
print("\n[7] Prashna horary Authorization Gating")
# Free user should get 403 Forbidden
test_endpoint("POST /api/astrology/prashna (Free User)", "POST", f"{BASE}/api/astrology/prashna", {
    "topic": "career", "lat": 13.0827, "lon": 80.2707
}, expected_status=403)

# Pro user should get 200 OK
test_endpoint("POST /api/astrology/prashna (Pro User)", "POST", f"{BASE}/api/astrology/prashna", {
    "topic": "career", "lat": 13.0827, "lon": 80.2707, "api_key": "atro_pro_dev_key"
}, expected_status=200)

# 8. Restricted Pure Classical & Hybrid timelines
print("\n[8] Pure Scriptural & Hybrid Timelines Gating")
test_endpoint("POST /api/astrology/pure-classical (Free User)", "POST", f"{BASE}/api/astrology/pure-classical", {
    "year": 1990, "month": 5, "day": 10, "time": "10:30", "lat": 13.0827, "lon": 80.2707,
    "start_year": 2026, "end_year": 2030
}, expected_status=403)

test_endpoint("POST /api/astrology/hybrid (Free User)", "POST", f"{BASE}/api/astrology/hybrid", {
    "year": 1990, "month": 5, "day": 10, "time": "10:30", "lat": 13.0827, "lon": 80.2707,
    "start_year": 2026, "end_year": 2030
}, expected_status=403)

test_endpoint("POST /api/astrology/hybrid (Pro User)", "POST", f"{BASE}/api/astrology/hybrid", {
    "year": 1990, "month": 5, "day": 10, "time": "10:30", "lat": 13.0827, "lon": 80.2707,
    "start_year": 2026, "end_year": 2030, "api_key": "atro_pro_dev_key"
}, expected_status=200)

print("\n" + "=" * 60)
print(f"MONETIZATION RESULT: {ok}/{total} validations passed")
print("=" * 60)
sys.exit(0 if ok == total else 1)
