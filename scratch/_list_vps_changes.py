import os
import time

now = time.time()
opt_astro = "/opt/astro"

# Walk through opt_astro and find files modified in last 10 days
modified_files = []
for root, dirs, files in os.walk(opt_astro):
    # Skip directories we don't care about
    if any(p in root for p in ["venv", ".git", "__pycache__"]):
        continue
    for f in files:
        filepath = os.path.join(root, f)
        try:
            mtime = os.path.getmtime(filepath)
            age_days = (now - mtime) / (24 * 3600)
            if age_days < 10:
                modified_files.append((filepath, mtime, age_days))
        except Exception:
            pass

# Sort by modification time (most recent first)
modified_files.sort(key=lambda x: x[1], reverse=True)

print("FILES MODIFIED ON VPS IN THE LAST 10 DAYS:")
print("=" * 60)
for path, mtime, age in modified_files:
    print(f"{path} -> Modified: {time.ctime(mtime)} ({age:.1f} days ago)")
