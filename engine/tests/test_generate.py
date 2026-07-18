from engine.reading import generate_reading

class SimpleChart:
    def __init__(self):
        self.name = "Test"
        self.lagna_lon = 45.0
        self.lagna_sign = "Taurus"
        self.lagna_lord = "Venus"
        self.lagna_nakshatra = "Rohini"
        self.positions = {"Sun": 10, "Moon": 20, "Mars": 30, "Mercury": 40, "Jupiter": 50, "Venus": 60, "Saturn": 70, "Rahu": 80, "Ketu": 260}
        self.house_of = {"Sun": 1, "Moon": 1, "Mars": 1, "Mercury": 1, "Jupiter": 1, "Venus": 1, "Saturn": 1, "Rahu": 1, "Ketu": 7}
        self.nakshatras = {k: {"sign": "Aries", "name": "Ashvini", "pada": 1, "lord": "Ketu"} for k in self.positions}
        self.current_md = "Venus"
        self.current_ad = "Venus"
        self.current_md_end = "2030-01-01"
        self.vimshottari_periods = []
        self.yogas = []
        self.vargas = {}
        self.vargottama = []
        self.bala_summary = {"strongest": [], "weakest": []}

chart = SimpleChart()
try:
    r = generate_reading(chart)
    print("SUCCESS")
except Exception as e:
    import traceback
    traceback.print_exc()
