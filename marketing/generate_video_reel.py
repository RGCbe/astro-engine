#!/usr/bin/env python3
"""AstroMystic AI — Programmatic MP4 Reel Video Creator"""
import os
import sys
import numpy as np
from PIL import Image, ImageDraw
import imageio

# Reconfigure stdout to UTF-8
sys.stdout.reconfigure(encoding='utf-8')

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
VIDEO_PATH = os.path.join(OUTPUT_DIR, "crossover_reel.mp4")

SLIDES = [
    os.path.join(OUTPUT_DIR, "slide1_title.png"),
    os.path.join(OUTPUT_DIR, "slide2_chart.png"),
    os.path.join(OUTPUT_DIR, "slide3_match.png"),
    os.path.join(OUTPUT_DIR, "slide4_cta.png")
]

FPS = 30
SECONDS_PER_SLIDE = 3.0
TOTAL_FRAMES_PER_SLIDE = int(FPS * SECONDS_PER_SLIDE) # 90 frames

def create_mp4_reel():
    print("[+] Launching AstroMystic Video Compiler...")
    
    # Verify all input slides exist
    for slide in SLIDES:
        if not os.path.exists(slide):
            print(f"[-] Error: Slide image not found at: {slide}")
            print("[-] Please run 'python marketing/generate_reel.py' first to compile the slides.")
            sys.exit(1)
            
    print(f"[+] Compiling high-definition MP4 Reel video: {VIDEO_PATH} ...")
    
    try:
        # Get an FFMPEG writer from imageio. It will automatically handle downloading 
        # the lightweight binary if not already cached on the system.
        writer = imageio.get_writer(VIDEO_PATH, format="FFMPEG", mode="I", fps=FPS, 
                                    codec="h264", pixelformat="yuv420p", quality=8)
    except Exception as e:
        print(f"[-] FFMPEG writer initialization failed ({e}). Falling back to simple writer...")
        writer = imageio.get_writer(VIDEO_PATH, mode="I", fps=FPS)
        
    try:
        for idx, slide_path in enumerate(SLIDES):
            print(f"  [+] Processing Slide {idx + 1}/{len(SLIDES)}: {os.path.basename(slide_path)}")
            # Load slide using Pillow
            slide_img = Image.open(slide_path).convert("RGB")
            w, h = slide_img.size
            
            # Write 90 frames per slide with a subtle zoom animation
            for frame_idx in range(TOTAL_FRAMES_PER_SLIDE):
                # Calculate zoom factor: slowly scale from 1.0 (100%) to 1.05 (105%)
                progress = frame_idx / TOTAL_FRAMES_PER_SLIDE
                zoom = 1.0 + (0.04 * progress)
                
                # Crop and resize to create smooth zoom effect
                new_w, new_h = int(w / zoom), int(h / zoom)
                x_offset, y_offset = (w - new_w) // 2, (h - new_h) // 2
                
                cropped_img = slide_img.crop([x_offset, y_offset, x_offset + new_w, y_offset + new_h])
                resized_img = cropped_img.resize((w, h), Image.Resampling.LANCZOS)
                
                # Convert Pillow image to numpy array for imageio
                frame_np = np.array(resized_img)
                writer.append_data(frame_np)
                
        writer.close()
        print(f"\n[+] SUCCESS: High-definition 12-second MP4 Video Reel created successfully!")
        print(f"[+] Output File: {VIDEO_PATH} ({os.path.getsize(VIDEO_PATH) // 1024} KB)")
        
    except Exception as e:
        print(f"[-] Video compilation failed: {e}")
        # Make sure writer is closed safely
        try:
            writer.close()
        except Exception:
            pass
        sys.exit(1)

if __name__ == "__main__":
    create_mp4_reel()
