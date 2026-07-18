#!/bin/bash
# Generate Tamil PDF for any chart - the new standard format
# Usage: bash gen_tamil.sh <chart_slug>
#   eg: bash gen_tamil.sh sachin_tendulkar
cd "$(dirname "$0")"
slug=$1
if [ -z "$slug" ]; then
    echo "Usage: $0 <chart_slug>"
    echo "Available charts:"
    ls ../charts/*_chart.json | xargs -n1 basename | sed 's/_chart.json//' | sed 's/^/  /'
    exit 1
fi
upper=$(echo "$slug" | tr '[:lower:]' '[:upper:]')
python generate_tamil_pdf.py --chart "../charts/${slug}_chart.json" --out "../reports/${upper}_TAMIL.pdf"
