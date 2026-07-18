import urllib.request, os, sys

runtime_dir = r"f:/astro/runtime"
os.makedirs(runtime_dir, exist_ok=True)

fonts = {
    "PlayfairDisplay-Regular.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/playfairdisplay/PlayfairDisplay-Regular.ttf",
    "PlayfairDisplay-Bold.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/playfairdisplay/PlayfairDisplay-Bold.ttf",
}

for name, url in fonts.items():
    out_path = os.path.join(runtime_dir, name)
    try:
        print(f"Downloading {name} from {url}...")
        urllib.request.urlretrieve(url, out_path)
        print(f"Saved {out_path}")
    except Exception as e:
        print(f"Failed to download {name}: {e}")
        sys.exit(1)
print("All fonts downloaded successfully.")
