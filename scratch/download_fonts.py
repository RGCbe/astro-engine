import urllib.request, os, sys

runtime_dir = r"f:/astro/runtime"
os.makedirs(runtime_dir, exist_ok=True)

fonts = {
    "PlayfairDisplay-Regular.ttf": "https://github.com/google/fonts/raw/main/ofl/playfairdisplay/PlayfairDisplay-Regular.ttf",
    "PlayfairDisplay-Bold.ttf": "https://github.com/google/fonts/raw/main/ofl/playfairdisplay/PlayfairDisplay-Bold.ttf",
}

for name, url in fonts.items():
    out_path = os.path.join(runtime_dir, name)
    try:
        print(f"Downloading {name}...")
        urllib.request.urlretrieve(url, out_path)
        print(f"Saved to {out_path}")
    except Exception as e:
        print(f"Failed to download {name}: {e}")
        sys.exit(1)
print("All fonts downloaded.")
