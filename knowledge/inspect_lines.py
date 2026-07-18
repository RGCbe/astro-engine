import sys

path = sys.argv[3] if len(sys.argv) > 3 else '/opt/astro/runtime/event_predictor_v2.py'
lines = open(path, 'r', encoding='utf-8').read().splitlines()

start = int(sys.argv[1]) if len(sys.argv) > 1 else 460
end = int(sys.argv[2]) if len(sys.argv) > 2 else 500

for i in range(start - 1, min(end, len(lines))):
    print(f"{i+1}: {lines[i]}")
