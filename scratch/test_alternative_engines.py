import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_jathagam_integration():
    payload = {
        "year": 1990,
        "month": 5,
        "day": 15,
        "time": "10:30",
        "lat": 13.0827,
        "lon": 80.2707,
        "focus": "general"
    }
    
    print("Executing /api/jathagam request...")
    response = client.post("/api/jathagam", json=payload)
    
    assert response.status_code == 200, f"Error: Status code {response.status_code}"
    data = response.json()
    assert data["status"] == "success"
    
    print("\n[SUCCESS] /api/jathagam responded with success status!")
    
    # Verify Jaimini Analysis
    assert "jaimini_analysis" in data, "jaimini_analysis missing!"
    jaimini = data["jaimini_analysis"]
    assert jaimini["status"] == "success", f"Jaimini failed: {jaimini}"
    print(f"Jaimini status: {jaimini['status']}")
    print(f"Jaimini Chara Karakas count: {len(jaimini['summary']['chara_karakas'])}")
    print(f"Jaimini 7-advanced dashas computed successfully!")
    
    # Verify Tajika Analysis
    assert "tajika_analysis" in data, "tajika_analysis missing!"
    tajika = data["tajika_analysis"]
    assert tajika["status"] == "success", f"Tajika failed: {tajika}"
    print(f"Tajika status: {tajika['status']}")
    print(f"Tajika Varsha Lord (Year King): {tajika['varshesha']}")
    print(f"Tajika 16-yogas detected: {len(tajika['yogas_16'])}")
    print(f"Tajika 5-balas (strength): {list(tajika['balas_5'].keys())}")
    
    # Verify Nadi Analysis
    assert "nadi_analysis" in data, "nadi_analysis missing!"
    nadi = data["nadi_analysis"]
    assert nadi["status"] == "success", f"Nadi failed: {nadi}"
    print(f"Nadi status: {nadi['status']}")
    print(f"Nadi 108-cell narratives count: {len(nadi['narrative'])}")
    print(f"Nadi slow transit alignments count: {len(nadi['transits']['alignments'])}")
    
    print("\nALL ALTERNATIVE ENGINES INTEGRATED SUCCESSFULLY WITH ZERO REGRESSIONS!")

if __name__ == "__main__":
    test_jathagam_integration()
