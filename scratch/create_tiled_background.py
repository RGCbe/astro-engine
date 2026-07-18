import os
from PIL import Image

pattern_path = "C:/Users/chive/.gemini/antigravity/brain/667a9de7-343e-423f-9a9b-ba7fe1ceeda7/mystical_seamless_pattern_1784028556382.png"
output_path_runtime = "f:/astro/runtime/mystical_tiled_background.png"
output_path_artifacts = "C:/Users/chive/.gemini/antigravity/brain/667a9de7-343e-423f-9a9b-ba7fe1ceeda7/mystical_tiled_background.png"

if not os.path.exists(pattern_path):
    print(f"Error: {pattern_path} not found!")
    exit(1)

# Target size at ~150 DPI for A4 (1240 x 1754 pixels)
target_width = 1240
target_height = 1754

# Load pattern and convert to RGBA
pattern = Image.open(pattern_path).convert("RGBA")
datas = pattern.getdata()

# Key out cream background to transparent
new_data = []
for item in datas:
    # item is (r, g, b, a)
    # If it is very bright (cream/white), make it transparent
    if item[0] > 220 and item[1] > 210 and item[2] > 190:
        new_data.append((255, 255, 255, 0))  # Transparent
    else:
        new_data.append(item)  # Keep line art

pattern.putdata(new_data)
pattern_w, pattern_h = pattern.size

# Create a new transparent image
tiled_img = Image.new("RGBA", (target_width, target_height), (255, 255, 255, 0))

# Tile the transparent pattern
for x in range(0, target_width, pattern_w):
    for y in range(0, target_height, pattern_h):
        tiled_img.paste(pattern, (x, y), pattern)  # Use pattern as mask for alpha pasting

# Save output to runtime and artifacts
tiled_img.save(output_path_runtime, "PNG")
tiled_img.save(output_path_artifacts, "PNG")

print("Tiled transparent A4 background image successfully created!")
