#!/usr/bin/env python3
"""AstroMystic AI — Automated Instagram Carousel & Slide Generator"""
import os
import sys
import json
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# Reconfigure stdout to UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# Coordinates and Fonts configurations
WIDTH, HEIGHT = 1080, 1920
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Try to load premium TTF fonts, fallback to default if not present
def get_fonts():
    try:
        # Check standard Windows fonts
        font_path = "C:\\Windows\\Fonts\\Outfit-Bold.ttf"
        if not os.path.exists(font_path):
            font_path = "C:\\Windows\\Fonts\\arialbd.ttf"
            
        font_path_reg = "C:\\Windows\\Fonts\\Outfit-Regular.ttf"
        if not os.path.exists(font_path_reg):
            font_path_reg = "C:\\Windows\\Fonts\\arial.ttf"
            
        font_title = ImageFont.truetype(font_path, 72)
        font_header = ImageFont.truetype(font_path, 48)
        font_body = ImageFont.truetype(font_path_reg, 32)
        font_sub = ImageFont.truetype(font_path_reg, 24)
        return font_title, font_header, font_body, font_sub
    except Exception:
        # Ultimate fallback to default Pillow fonts
        f = ImageFont.load_default()
        return f, f, f, f

# Helper to draw a sleek deep-space radial gradient background
def draw_cosmic_background():
    img = Image.new("RGBA", (WIDTH, HEIGHT), (5, 5, 15, 255)) # Deep dark indigo
    draw = ImageDraw.Draw(img)
    
    # Draw soft glowing nebulae at the center and bottom
    for r in range(500, 0, -2):
        alpha = int(120 * (1 - r/500))
        # Center glow (Cyan)
        draw.ellipse([WIDTH//2 - r, HEIGHT//3 - r, WIDTH//2 + r, HEIGHT//3 + r], 
                     fill=(0, 229, 255, alpha))
        
        # Bottom glow (Violet)
        draw.ellipse([WIDTH//2 - r, HEIGHT - r, WIDTH//2 + r, HEIGHT + r], 
                     fill=(147, 51, 234, alpha // 2))
        
    # Apply heavy blur to blend nebulae smoothly
    img = img.filter(ImageFilter.GaussianBlur(40))
    return img

# Helper to draw a glassmorphic panel with borders and soft inner shadows
def draw_glass_card(draw, x1, y1, x2, y2, border_color=(0, 229, 255, 120), fill_color=(255, 255, 255, 15)):
    # Draw soft card fill
    draw.rounded_rectangle([x1, y1, x2, y2], radius=24, fill=fill_color)
    # Draw thin glowing border
    draw.rounded_rectangle([x1, y1, x2, y2], radius=24, outline=border_color, width=2)

# Helper to draw an authentic South Indian Style Vedic Birth Chart (12 compartments)
def draw_south_indian_chart(draw, x_offset, y_offset, size, planets_data, lagnam):
    # Size defines width & height of the chart box
    cell_size = size // 4
    
    # Draw the main outer square and 4x4 grid lines
    draw.rectangle([x_offset, y_offset, x_offset + size, y_offset + size], outline=(255, 255, 255, 150), width=3)
    
    # Grid lines
    for i in range(1, 4):
        draw.line([x_offset + i * cell_size, y_offset, x_offset + i * cell_size, y_offset + size], fill=(255, 255, 255, 80), width=1)
        draw.line([x_offset, y_offset + i * cell_size, x_offset + size, y_offset + i * cell_size], fill=(255, 255, 255, 80), width=1)
        
    # Hollow out the inner 2x2 cells (classic South Indian chart structure has an empty center)
    draw.rectangle([x_offset + cell_size, y_offset + cell_size, x_offset + 3*cell_size, y_offset + 3*cell_size], 
                   fill=(15, 15, 30, 255), outline=(255, 255, 255, 150), width=2)
    
    # Write "AstroMystic AI" in the center empty box
    _, _, font_body, font_sub = get_fonts()
    draw.text((x_offset + size//2 - 60, y_offset + size//2 - 25), "D1 CHART", fill=(0, 229, 255, 220), font=font_body)
    draw.text((x_offset + size//2 - 75, y_offset + size//2 + 10), f"Lagna: {lagnam}", fill=(255, 255, 255, 150), font=font_sub)

    # South Indian house order coordinates (12 compartments clockwise starting from top-second cell)
    house_coords = [
        (1, 0), (2, 0), (3, 0), # Top row (Pisces, Aries, Taurus, Gemini)
        (3, 1), (3, 2), (3, 3), # Right col
        (2, 3), (1, 3), (0, 3), # Bottom row
        (0, 2), (0, 1), (0, 0)  # Left col
    ]
    
    # Signs order: Aries, Taurus, Gemini, Cancer, Leo, Virgo, Libra, Scorpio, Sagittarius, Capricorn, Aquarius, Pisces
    # On a South Indian chart, Pisces is at coordinate (0, 0), Aries is at (1, 0), etc.
    rasi_cells = {
        "Aries": (1, 0), "Taurus": (2, 0), "Gemini": (3, 0), "Cancer": (3, 1),
        "Leo": (3, 2), "Virgo": (3, 3), "Libra": (2, 3), "Scorpio": (1, 3),
        "Sagittarius": (0, 3), "Capricorn": (0, 2), "Aquarius": (0, 1), "Pisces": (0, 0)
    }
    
    # Map planets to their respective rasis
    rasi_planets = {r: [] for r in rasi_cells.keys()}
    for p, pdata in planets_data.items():
        if p in ("Gulika", "Mandi"):
            continue
        rasi = pdata.get("rasi")
        if rasi in rasi_planets:
            # Abbreviate planet name (e.g. Mercury -> Mer, Moon -> Mon)
            abb = p[:3] if p != "Rahu" else "Rah"
            if p == "Ketu": abb = "Ket"
            rasi_planets[rasi].append(abb)
            
    # Draw planets in their cell locations
    for rasi, cell in rasi_cells.items():
        cx, cy = cell
        px = x_offset + cx * cell_size + 10
        py = y_offset + cy * cell_size + 10
        
        # Draw Rasi label (first 2 letters, e.g. Ar, Ta, Ge)
        draw.text((px, py), rasi[:2], fill=(255, 255, 255, 80), font=font_sub)
        
        # Write planets in cell
        p_list = rasi_planets[rasi]
        for idx, p_abb in enumerate(p_list):
            p_x = px + 5 + (idx % 2) * 55
            p_y = py + 25 + (idx // 2) * 25
            
            # Highlight lagna lord or key nodes
            color = (0, 229, 255, 255) if p_abb in ("Rah", "Ket") else (255, 215, 0, 255)
            draw.text((p_x, p_y), p_abb, fill=color, font=font_sub)


# Main Slide Builder
def generate_launch_carousels():
    print("[+] Launching AstroMystic Asset Engine...")
    
    # Fetch actual sample coordinates from the local server to show real, live calculations
    print("[+] Fetching real-time chart data from local server...")
    try:
        r = requests.post("http://localhost:8000/api/jathagam", json={
            "year": 1990, "month": 5, "day": 10, "time": "10:30",
            "lat": 13.0827, "lon": 80.2707, "api_key": "atro_pro_dev_key"
        }, timeout=5)
        astro_data = r.json()
        print("  [OK] Successfully retrieved real-time calculations!")
    except Exception as e:
        print(f"  [Warning] Local server query failed ({e}). Falling back to static mockup data.")
        # Static mock fallback so code never breaks if local server is down
        astro_data = {
            "lagnam": "Cancer",
            "janma_nakshatra": "Anuradha",
            "all_planet_positions": {
                "Sun": {"rasi": "Aries", "longitude": 25.4, "nakshatra_lord": "Venus"},
                "Moon": {"rasi": "Scorpio", "longitude": 12.8, "nakshatra_lord": "Saturn"},
                "Rahu": {"rasi": "Capricorn", "longitude": 18.2, "nakshatra_lord": "Moon"},
                "Ketu": {"rasi": "Cancer", "longitude": 18.2, "nakshatra_lord": "Mercury"}
            }
        }
        
    font_title, font_header, font_body, font_sub = get_fonts()
    
    # ─── SLIDE 1: Title & Brand Introduction ──────────────────────────────────
    print("[+] Renders Slide 1: Welcome Slide...")
    slide1 = draw_cosmic_background()
    draw1 = ImageDraw.Draw(slide1)
    
    # Draw premium card
    draw_glass_card(draw1, 100, 450, 980, 1450)
    
    # Logo & text
    draw1.text((WIDTH//2 - 200, 200), "🪐", fill=(0, 229, 255, 255), font=font_title)
    draw1.text((WIDTH//2 - 220, 520), "AstroMystic AI", fill=(0, 229, 255, 255), font=font_header)
    draw1.text((WIDTH//2 - 190, 600), "Astrology Redefined", fill=(255, 255, 255, 180), font=font_sub)
    
    body_text = (
        "Ancient Vedic Wisdom\n"
        "Conjoined with High-Precision\n"
        "Neural Calculations.\n\n"
        "✨ Discover Your Blueprint\n"
        "✨ Calculate Auspicious Windows\n"
        "✨ 100% Scripture Verified"
    )
    draw1.text((150, 750), body_text, fill=(255, 255, 255, 230), font=font_body, spacing=15)
    
    # Footer CTA
    draw_glass_card(draw1, 150, 1600, 930, 1720, border_color=(147, 51, 234, 180), fill_color=(147, 51, 234, 30))
    draw1.text((WIDTH//2 - 180, 1635), "SWIPE FOR BLUEPRINT 👉", fill=(255, 255, 255, 255), font=font_body)
    
    slide1.save(os.path.join(OUTPUT_DIR, "slide1_title.png"))
    
    # ─── SLIDE 2: Interactive Kundali Chart Slide ──────────────────────────────
    print("[+] Renders Slide 2: Real-time Vedic Chart...")
    slide2 = draw_cosmic_background()
    draw2 = ImageDraw.Draw(slide2)
    
    draw_glass_card(draw2, 80, 300, 1000, 1500)
    
    draw2.text((WIDTH//2 - 180, 360), "Your Celestial Grid", fill=(0, 229, 255, 255), font=font_header)
    draw2.text((WIDTH//2 - 260, 430), "Vedic D1 Natal Chart Placement", fill=(255, 255, 255, 150), font=font_sub)
    
    # Draw South Indian Chart
    planets = astro_data.get("all_planet_positions", {})
    lagnam = astro_data.get("lagnam", "Cancer")
    draw_south_indian_chart(draw2, 140, 550, 800, planets, lagnam)
    
    details_text = (
        f"Lagnam: {lagnam} Lagna\n"
        f"Janma Nakshatra: {astro_data.get('janma_nakshatra', 'Anuradha')}\n"
        f"Current Dasha: {astro_data.get('current_dasha', 'Mercury')}"
    )
    draw2.text((150, 1370), details_text, fill=(255, 255, 255, 220), font=font_body, spacing=10)
    
    # Footer CTA
    draw_glass_card(draw2, 150, 1600, 930, 1720, border_color=(147, 51, 234, 180), fill_color=(147, 51, 234, 30))
    draw2.text((WIDTH//2 - 180, 1635), "SWIPE FOR ELECTIONAL 👉", fill=(255, 255, 255, 255), font=font_body)
    
    slide2.save(os.path.join(OUTPUT_DIR, "slide2_chart.png"))
    
    # ─── SLIDE 3: Matchmaking Grid (Ashta Koota) ────────────────────────────────
    print("[+] Renders Slide 3: Matchmaking & Koota Score Slide...")
    slide3 = draw_cosmic_background()
    draw3 = ImageDraw.Draw(slide3)
    
    draw_glass_card(draw3, 80, 300, 1000, 1500)
    
    draw3.text((WIDTH//2 - 190, 360), "Ashta Koota Match", fill=(0, 229, 255, 255), font=font_header)
    draw3.text((WIDTH//2 - 250, 430), "36 Points Cosmic Compatibility Grid", fill=(255, 255, 255, 150), font=font_sub)
    
    # Draw Score Circle Gauge
    gauge_x, gauge_y, gauge_r = WIDTH//2, 750, 180
    draw3.ellipse([gauge_x - gauge_r, gauge_y - gauge_r, gauge_x + gauge_r, gauge_y + gauge_r], 
                  outline=(255, 255, 255, 50), width=15)
    # Draw green/glow arc representing excellent compatibility score (28/36 points)
    draw3.arc([gauge_x - gauge_r, gauge_y - gauge_r, gauge_x + gauge_r, gauge_y + gauge_r], 
             start=-90, end=190, fill=(0, 229, 255, 255), width=18)
    
    # Compatibility details in center
    draw3.text((gauge_x - 70, gauge_y - 50), "28 / 36", fill=(0, 229, 255, 255), font=font_header)
    draw3.text((gauge_x - 55, gauge_y + 15), "EXCELLENT", fill=(255, 215, 0, 255), font=font_sub)
    
    koota_text = (
        "✓ Graha Maitri (Friendship): 5 / 5\n"
        "✓ Nadi Dosha (Physiology): 8 / 8 (No Dosha)\n"
        "✓ Bhakoot Compatibility: 7 / 7\n"
        "✓ Mangal Dosha: Neutralized (No Affliction)"
    )
    draw3.text((150, 1050), koota_text, fill=(255, 255, 255, 220), font=font_body, spacing=15)
    
    # Footer CTA
    draw_glass_card(draw3, 150, 1600, 930, 1720, border_color=(147, 51, 234, 180), fill_color=(147, 51, 234, 30))
    draw3.text((WIDTH//2 - 160, 1635), "SWIPE FOR ACCESS 👉", fill=(255, 255, 255, 255), font=font_body)
    
    slide3.save(os.path.join(OUTPUT_DIR, "slide3_match.png"))
    
    # ─── SLIDE 4: Call-To-Action (Web Link In Bio) ──────────────────────────────
    print("[+] Renders Slide 4: Call-to-Action / Web Launch Slide...")
    slide4 = draw_cosmic_background()
    draw4 = ImageDraw.Draw(slide4)
    
    draw_glass_card(draw4, 80, 300, 1000, 1500)
    
    draw4.text((WIDTH//2 - 200, 380), "Cast Your Chart", fill=(0, 229, 255, 255), font=font_header)
    draw4.text((WIDTH//2 - 210, 450), "Access Astromystic tools now", fill=(255, 255, 255, 150), font=font_sub)
    
    # Visual illustration of dashboard (glowing elements)
    draw_glass_card(draw4, 140, 600, 940, 1050, border_color=(0, 229, 255, 255), fill_color=(255, 255, 255, 8))
    
    draw4.text((180, 640), "🪐 AstroMystic Sacred Tools", fill=(0, 229, 255, 255), font=font_body)
    draw4.text((180, 710), "✓ Full D1 / D9 Navamsha Charts", fill=(255, 255, 255, 220), font=font_sub)
    draw4.text((180, 760), "✓ Precise Placidus House Cusps", fill=(255, 255, 255, 220), font=font_sub)
    draw4.text((180, 810), "✓ Jaimini, Tajika & Nadi engines", fill=(255, 255, 255, 220), font=font_sub)
    draw4.text((180, 860), "✓ Auspicious Muhurta Time Finder", fill=(255, 255, 255, 220), font=font_sub)
    draw4.text((180, 910), "✓ Prashna instant Horary oracle", fill=(255, 255, 255, 220), font=font_sub)
    draw4.text((180, 960), "✓ Premium 12-page PDF Download", fill=(255, 255, 255, 220), font=font_sub)
    
    action_text = (
        "Scan the QR code in our stories\n"
        "or click the link below to get instant\n"
        "unlocked access!"
    )
    draw4.text((WIDTH//2 - 230, 1150), action_text, fill=(255, 255, 255, 180), font=font_body, spacing=10)
    
    # Final neon launch button
    draw_glass_card(draw4, 150, 1600, 930, 1720, border_color=(0, 229, 255, 255), fill_color=(0, 229, 255, 40))
    draw4.text((WIDTH//2 - 160, 1635), "LINK IN INSTAGRAM BIO 🪐", fill=(255, 255, 255, 255), font=font_body)
    
    slide4.save(os.path.join(OUTPUT_DIR, "slide4_cta.png"))
    
    print(f"[+] SUCCESS: 4 high-definition carousel slides compiled in: {OUTPUT_DIR}/")

if __name__ == "__main__":
    generate_launch_carousels()
