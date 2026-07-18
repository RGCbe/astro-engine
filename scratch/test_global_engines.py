"""
GAC Verification Test Suite.
Verifies Western, Chinese, and Mayan astrology endpoints under the FastAPI app.
"""
import sys
import os
from fastapi.testclient import TestClient

# Ensure engine is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

client = TestClient(app)

def test_western_endpoint():
    print("[TEST] Testing Western Astrology Engine...")
    payload = {
        "date": "1974-06-22",
        "time": "12:00",
        "tz_hours": 5.5,
        "lat": 13.0827,
        "lon": 80.2707,
        "age": 52
    }
    response = client.post("/api/astrology/western", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["framework"] == "Western Tropical"
    calc = data["calculations"]
    assert "ascendant" in calc
    assert "planets" in calc
    assert "aspects" in calc
    assert "lots" in calc
    assert "annual_profection" in calc
    
    # Sun is close to the Summer Solstice (June 21/22), so it is in late Gemini or early Cancer
    sun_info = calc["planets"]["Sun"]
    print(f"Sun details: {sun_info}")
    assert sun_info["sign"] in ["Gemini", "Cancer"]
    assert calc["lots"]["Sect"] == "Day"
    assert calc["annual_profection"]["Lord of the Year"] in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    
    print("[SUCCESS] Western Astrology Engine verified successfully!")

def test_chinese_endpoint():
    print("[TEST] Testing Chinese Astrology Engine...")
    payload = {
        "date": "1974-06-22",
        "time": "12:00",
        "tz_hours": 5.5
    }
    response = client.post("/api/astrology/chinese", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["framework"] == "Chinese BaZi & Zi Wei Dou Shu"
    calc = data["calculations"]
    
    # Verify pillars exist
    bazi = calc["bazi_pillars"]
    assert "Year" in bazi
    assert "Month" in bazi
    assert "Day" in bazi
    assert "Hour" in bazi
    
    # Verify Elements analysis
    elems = calc["elements_analysis"]
    assert "day_master" in elems
    assert "elements_distribution" in elems
    assert "self_strength" in elems
    assert sum(elems["elements_distribution"].values()) == 100.0
    
    # Verify Zi Wei Dou Shu
    zwds = calc["zi_wei_dou_shu"]
    assert "palaces_mapping" in zwds
    assert "major_stars_placement" in zwds
    
    print("[SUCCESS] Chinese Astrology Engine verified successfully!")

def test_mayan_endpoint():
    print("[TEST] Testing Mayan Astrology Engine...")
    
    # Historic test date: December 21, 2012 (End of 13th Bak'tun / Winter Solstice)
    # Should correspond to precisely 4 Ahau
    payload = {
        "date": "2012-12-21"
    }
    response = client.post("/api/astrology/mayan", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["framework"] == "Mayan Tzolk'in Calendar (GMT 584283 Correlation)"
    calc = data["calculations"]
    assert calc["julian_day_number"] == 2456283
    assert calc["day_glyph"]["name"] == "Ahau"
    assert calc["galactic_tone"]["tone"] == 4
    assert "4 Ahau (Magnetic Sun / Lord)" in calc["formatted"] or "4 Ahau" in calc["formatted"]
    
    print("[SUCCESS] Mayan Astrology Engine verified successfully!")

if __name__ == "__main__":
    test_western_endpoint()
    test_chinese_endpoint()
    test_mayan_endpoint()
    print("\n[ALL GAC TESTS PASSED 100%]")
