#!/bin/bash
# Atro Engine - Continuous Machine Learning Loop Scheduler
# Add this to crontab: 0 2 * * * /opt/astro/runtime/auto_train.sh >> /opt/astro/logs/ml_loop.log 2>&1

echo "========================================"
echo "Starting Atro ML Optimization Loop"
echo "Time: $(date)"
echo "========================================"

# Navigate to working directory
cd /opt/astro/

# Activate environment if applicable (adjust path as needed)
# source venv/bin/activate

# Run the gatekeeper manager
python3 runtime/weight_manager.py

echo "Optimization Loop Complete: $(date)"
echo "========================================"
