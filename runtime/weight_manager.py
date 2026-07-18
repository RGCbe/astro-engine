import os
import sys
import json
import subprocess
from pathlib import Path
from optimizer_loop import run_optimizer, evaluate_accuracy, load_verified_charts
from category_engine import WEIGHTS_PATH, DEFAULT_WEIGHTS

def gatekeeper_check():
    print("=== ATRO WEIGHT MANAGER GATEKEEPER ===")
    
    # 1. Load current baseline
    charts = load_verified_charts()
    
    if WEIGHTS_PATH.exists():
        try:
            baseline_weights = json.load(open(WEIGHTS_PATH, "r", encoding="utf-8"))
        except:
            baseline_weights = DEFAULT_WEIGHTS
    else:
        baseline_weights = DEFAULT_WEIGHTS
        
    print("Evaluating current production baseline...")
    baseline_acc = evaluate_accuracy(baseline_weights, charts)
    print(f"Production Baseline Accuracy: {baseline_acc*100:.2f}%")
    
    # 2. Run Optimizer
    print("\nStarting Optimization Loop (3 iterations)...")
    optimized_weights = run_optimizer(iterations=3)
    
    # optimizer_loop automatically evaluates and saves the best it found to WEIGHTS_PATH
    # Let's re-verify it here just to be safe
    new_acc = evaluate_accuracy(optimized_weights, charts)
    
    # 3. Decision Gate
    if new_acc > baseline_acc:
        print(f"\n[SUCCESS] New weights are superior ({new_acc*100:.2f}% > {baseline_acc*100:.2f}%)")
        print("Deploying to production and hot-reloading PM2...")
        
        # Save to production weights (in our case WEIGHTS_PATH is the production source)
        with open(WEIGHTS_PATH, "w", encoding="utf-8") as f:
            json.dump(optimized_weights, f, indent=4)
            
        # Hot reload PM2 (VPS specific)
        try:
            subprocess.run(["pm2", "reload", "astro-engine"], check=True)
            print("PM2 Reloaded Successfully.")
        except Exception as e:
            print(f"Note: PM2 reload skipped/failed (expected if running locally). Error: {e}")
            
    else:
        print(f"\n[NO DEPLOYMENT] Optimization did not beat baseline ({new_acc*100:.2f}% <= {baseline_acc*100:.2f}%)")
        # Rollback weights file to baseline
        with open(WEIGHTS_PATH, "w", encoding="utf-8") as f:
            json.dump(baseline_weights, f, indent=4)
        print("Rolled back to baseline weights.")

if __name__ == "__main__":
    gatekeeper_check()
