import os
path = '/opt/astro'
for root, dirs, files in os.walk(path):
    # Don't recurse too deep
    depth = root[len(path):].count(os.sep)
    if depth > 2:
        continue
    print(f"\n{root}")
    for d in sorted(dirs):
        print(f"  [DIR]  {d}")
    for f in sorted(files):
        if not f.endswith('.png') and not f.endswith('.svg'):
            print(f"  [FILE] {f}")
