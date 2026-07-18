import urllib.request, os, zipfile, io, sys

runtime_dir = r"f:/astro/runtime"
os.makedirs(runtime_dir, exist_ok=True)

zip_url = "https://fonts.google.com/download?family=Playfair%20Display"
zip_path = os.path.join(runtime_dir, "playfair_display.zip")

try:
    print(f"Downloading Playfair Display zip from {zip_url}...")
    urllib.request.urlretrieve(zip_url, zip_path)
    print(f"Saved zip to {zip_path}")
except Exception as e:
    print(f"Failed to download zip: {e}")
    sys.exit(1)

# Extract needed TTF files
try:
    with zipfile.ZipFile(zip_path, 'r') as z:
        for member in z.namelist():
            if member.endswith('PlayfairDisplay-Regular.ttf') or member.endswith('PlayfairDisplay-Bold.ttf'):
                print(f"Extracting {member}...")
                z.extract(member, runtime_dir)
                # Move to root of runtime
                src = os.path.join(runtime_dir, member)
                dst = os.path.join(runtime_dir, os.path.basename(member))
                os.replace(src, dst)
    print("Font files extracted successfully.")
    # Cleanup zip
    os.remove(zip_path)
except Exception as e:
    print(f"Failed to extract fonts: {e}")
    sys.exit(1)
