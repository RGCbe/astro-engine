import sys
from pathlib import Path
from engine.known_charts import KNOWN_CHARTS
from engine.chart import compute_chart
from engine.reading import generate_reading

def main():
    print("Finding Steve Jobs in known charts...")
    jobs = next(c for c in KNOWN_CHARTS if "Steve Jobs" in c.name)
    
    bd = jobs.birthdata
    print(f"Computing chart for {jobs.name}...")
    chart = compute_chart(
        date=bd["date"], time=bd["time"], tz_hours=bd["tz"],
        lat=bd["lat"], lon=bd["lon"], place=bd["place"], name=jobs.name
    )
    
    print("Generating reading with Phase IV Evaluator...")
    reading = generate_reading(chart)
    
    out_path = Path(__file__).parent / "steve_jobs_reading.md"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(reading.to_markdown())
        
    print(f"Success! Reading saved to {out_path}")

if __name__ == "__main__":
    main()
