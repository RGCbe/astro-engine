import sys
import os
import time
import json
import glob
from pathlib import Path

# Add project root and engine to path
_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "engine"))

from runtime.category_engine import category_engine_instance

def run_benchmark():
    print("="*60)
    print("AstroReport OS — V2 Probabilistic Benchmark Suite")
    print("="*60)
    
    charts_dir = _ROOT / "charts"
    chart_files = glob.glob(str(charts_dir / "*.json"))
    
    # Filter out test folders or non-chart json
    valid_charts = []
    for cf in chart_files:
        if "facts" in cf.lower() or "anti" in cf.lower():
            continue
        valid_charts.append(cf)
        
    print(f"Discovered {len(valid_charts)} valid chart files for testing.\n")
    
    metrics = {
        "total_charts_processed": 0,
        "total_execution_time_sec": 0.0,
        "total_events_generated": 0,
        "confidence_bands": {"Strong": 0, "Moderate": 0, "Weak": 0},
        "contradictions_flagged": 0,
        "avg_time_per_chart_sec": 0.0
    }
    
    start_time_global = time.time()
    
    for chart_path in valid_charts:
        try:
            with open(chart_path, "r", encoding="utf-8") as f:
                chart = json.load(f)
                
            name = chart.get("name", os.path.basename(chart_path))
            birth_year = chart["birth"]["year"]
            
            # For speed in benchmark, scan a 1-year window from age 25 to 26
            scan_start = birth_year + 25
            scan_end = birth_year + 26
            
            print(f"Scanning {name} ({scan_start}-{scan_end})...", end=" ", flush=True)
            
            start_time_chart = time.time()
            events = category_engine_instance.scan_lifetime(
                chart, 
                scan_start, 
                scan_end, 
                sample_days=14, 
                min_probability=0.2 # low threshold to catch all data
            )
            chart_time = time.time() - start_time_chart
            
            # Update metrics
            metrics["total_charts_processed"] += 1
            metrics["total_execution_time_sec"] += chart_time
            metrics["total_events_generated"] += len(events)
            
            for ev in events:
                band = ev.get("confidence_band", "Weak")
                if band in metrics["confidence_bands"]:
                    metrics["confidence_bands"][band] += 1
                if ev.get("contradictions", False):
                    metrics["contradictions_flagged"] += 1
                    
            print(f"[{len(events)} events] in {chart_time:.2f}s")
            
        except Exception as e:
            print(f"ERROR processing {os.path.basename(chart_path)}: {e}")
            
    # Finalize Metrics
    total_time = time.time() - start_time_global
    if metrics["total_charts_processed"] > 0:
        metrics["avg_time_per_chart_sec"] = metrics["total_execution_time_sec"] / metrics["total_charts_processed"]
        
    print("\n" + "="*60)
    print("BENCHMARK TELEMETRY RESULTS")
    print("="*60)
    print(f"Total Charts Processed : {metrics['total_charts_processed']}")
    print(f"Total Execution Time   : {total_time:.2f} seconds")
    print(f"Avg Time Per Chart     : {metrics['avg_time_per_chart_sec']:.2f} seconds")
    print(f"Total Events Generated : {metrics['total_events_generated']}")
    print(f"Contradictions Caught  : {metrics['contradictions_flagged']} ({(metrics['contradictions_flagged']/max(1, metrics['total_events_generated']))*100:.1f}%)")
    print("\nConfidence Band Distribution:")
    print(f"  - Strong   : {metrics['confidence_bands']['Strong']}")
    print(f"  - Moderate : {metrics['confidence_bands']['Moderate']}")
    print(f"  - Weak     : {metrics['confidence_bands']['Weak']}")
    
    # Save baseline to scratch
    baseline_path = _ROOT / "scratch" / "benchmark_baseline.json"
    with open(baseline_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=4)
    print(f"\nBaseline telemetry saved to {baseline_path}")

if __name__ == "__main__":
    run_benchmark()
