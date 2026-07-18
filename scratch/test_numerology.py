"""
Numerology Engine Verification Test Suite.
Verifies the new GAC Unified Numerology Engine API route.
"""
import sys
import os
from fastapi.testclient import TestClient

# Ensure engine is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

client = TestClient(app)

def test_manoj_numerology():
    print("[TEST] Testing Numerology Engine with Manoj profile...")
    payload = {
        "name": "Manoj",
        "date": "1996-05-25",
        "target_date": "2026-05-26"
    }
    response = client.post("/api/astrology/numerology", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["framework"] == "GAC Unified Multi-Paradigm Numerology Engine"
    calc = data["calculations"]
    
    # 1. Tamil Chaldæan Verification
    tamil = calc["tamil_chaldean"]
    assert tamil["vidhi_number"] == 7
    assert tamil["vidhi_planet"] == "Ketu"
    assert tamil["bhagya_number"] == 1
    assert tamil["bhagya_planet"] == "Sun"
    assert tamil["lucky_gemstone"] == "Vaidooryam (Cat's Eye)"
    assert tamil["deity"] == "Indra / Ganesha"
    assert tamil["higher_deity"] == "Chitragupta"
    
    # 2. Pythagorean Verification
    pyth = calc["pythagorean_triad"]
    # Manoj: M=4, A=1, N=5, O=6, J=1. Sum = 4+1+5+6+1 = 17 -> 1+7 = 8.
    assert pyth["expression_number"] == 8
    
    # 3. Lo Shu Grid Verification
    lo_shu = calc["lo_shu_grid"]
    grid = lo_shu["grid"]
    # 1996-05-25 -> Digits: 1, 9, 9, 6, 5, 2, 5.
    # Digit counts: 1:1, 2:1, 5:2, 6:1, 9:2.
    assert lo_shu["digit_counts"]["5"] == 2
    assert lo_shu["digit_counts"]["9"] == 2
    assert 4 in lo_shu["missing_numbers"]
    
    # 4. Temporal Cycles Verification
    cycles = calc["temporal_cycles"]
    # Personal Year = day(25) + month(5) + target_year(2026) -> 25+5+2026 = 2056 -> 2+0+5+6 = 13 -> 1+3 = 4.
    assert cycles["personal_year"] == 4
    
    print("[SUCCESS] Manoj numerology profile verified successfully!")

def test_vijay_numerology():
    print("[TEST] Testing Numerology Engine with Joseph Vijay profile...")
    payload = {
        "name": "Joseph Vijay",
        "date": "1974-06-22",
        "target_date": "2026-05-26"
    }
    response = client.post("/api/astrology/numerology", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    calc = data["calculations"]
    
    # Tamil Verification
    tamil = calc["tamil_chaldean"]
    assert tamil["vidhi_number"] == 4
    assert tamil["bhagya_number"] == 4
    
    # Pythagorean Verification
    pyth = calc["pythagorean_triad"]
    print(f"Joseph Vijay pyth details: {pyth}")
    # Under Pythagorean mapping:
    # J(1)+O(6)+S(1)+E(5)+P(7)+H(8) = 28 -> 10 -> 1
    # V(4)+I(9)+J(1)+A(1)+Y(7) = 22 (Master Number)
    # Total sum of name letters = 28 + 22 = 50 -> 5 + 0 = 5
    assert pyth["expression_number"] == 5
    
    # Lo Shu Grid Verification
    lo_shu = calc["lo_shu_grid"]
    assert lo_shu["digit_counts"]["2"] == 2
    
    print("[SUCCESS] Joseph Vijay numerology profile verified successfully!")

if __name__ == "__main__":
    test_manoj_numerology()
    test_vijay_numerology()
    print("\n[ALL NUMEROLOGY TESTS PASSED 100%]")
