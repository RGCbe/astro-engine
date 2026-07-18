import re

path = '/opt/astro/runtime/event_predictor_v2_recovered_debug.py'
lines = open(path, 'r', encoding='utf-8').read().splitlines()

print(f"Total lines in decompiled file: {len(lines)}")

# Find all function definitions and their line numbers
for i, line in enumerate(lines):
    if line.startswith('def '):
        if i + 1 < 2000:
            print(f"Line {i+1}: {line}")
