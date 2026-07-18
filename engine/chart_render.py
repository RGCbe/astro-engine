"""
Chart visualization — pure-Python SVG renderers for North/South Indian charts.

No external GUI dependencies. Output is a self-contained SVG string that
renders in any browser, can be embedded in markdown, or piped to a file.

North Indian (Bandhu chakra): diamond layout, lagna fixed at top, signs
    rotate counter-clockwise. Used in Bengal, Bihar, UP, Punjab.

South Indian (Rasi chakra): 4×4 fixed grid, Aries always top-left of inner
    cells, signs fixed by position. Used in Tamil Nadu, Kerala, Karnataka,
    Andhra. Lagna is marked with "AS" (Asc).

East Indian (Bengali style): square with diagonal lines — not implemented
    here (rare in modern usage).

API:
    render_north(chart) → SVG string
    render_south(chart) → SVG string
    save(svg_str, path) → write file
"""
from __future__ import annotations

from engine.i18n import translate

SIGN_NAMES = (
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
)
SIGN_SHORT = ("Ar", "Ta", "Ge", "Cn", "Le", "Vi",
              "Li", "Sc", "Sg", "Cp", "Aq", "Pi")
PLANET_SHORT = {
    "Sun": "Su", "Moon": "Mo", "Mars": "Ma", "Mercury": "Me",
    "Jupiter": "Ju", "Venus": "Ve", "Saturn": "Sa",
    "Rahu": "Ra", "Ketu": "Ke",
}


# ─── South Indian (4x4 grid) ───────────────────────────────────────────────
# Layout (sign indices):
#     +----+----+----+----+
#     | Pi | Ar | Ta | Ge |
#     +----+----+----+----+
#     | Aq |    |    | Cn |
#     +----+----+----+----+
#     | Cp |    |    | Le |
#     +----+----+----+----+
#     | Sg | Sc | Li | Vi |
#     +----+----+----+----+
SOUTH_GRID = {
    11: (0, 0), 0: (1, 0), 1: (2, 0), 2: (3, 0),
    10: (0, 1),                             3: (3, 1),
    9:  (0, 2),                             4: (3, 2),
    8:  (0, 3), 7: (1, 3), 6: (2, 3), 5: (3, 3),
}


def render_south(chart, lang: str = "en", size: int = 480) -> str:
    """Render a South Indian style D1 chart as SVG."""
    cell = size // 4
    cells: dict[int, list[str]] = {i: [] for i in range(12)}
    # Place planets by sign
    for planet, lon in chart.positions.items():
        sign = int(lon // 30)
        short = PLANET_SHORT.get(planet, planet[:2])
        cells[sign].append(short)
    lagna_sign = int(chart.lagna_lon // 30)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 {size} {size}" style="font-family:sans-serif">',
        f'<rect x="0" y="0" width="{size}" height="{size}" '
        f'fill="white" stroke="black" stroke-width="2"/>',
        # Inner box (the empty 2×2 center)
        f'<rect x="{cell}" y="{cell}" width="{2*cell}" height="{2*cell}" '
        f'fill="#fafafa" stroke="black" stroke-width="1"/>',
    ]
    # Vertical/horizontal lines for the outer ring
    for i in range(1, 4):
        parts.append(f'<line x1="{i*cell}" y1="0" x2="{i*cell}" y2="{cell}" stroke="black"/>')
        parts.append(f'<line x1="{i*cell}" y1="{3*cell}" x2="{i*cell}" y2="{size}" stroke="black"/>')
        parts.append(f'<line x1="0" y1="{i*cell}" x2="{cell}" y2="{i*cell}" stroke="black"/>')
        parts.append(f'<line x1="{3*cell}" y1="{i*cell}" x2="{size}" y2="{i*cell}" stroke="black"/>')

    # Cell labels & planets
    for sign_idx, (col, row) in SOUTH_GRID.items():
        x = col * cell + 4
        y = row * cell + 14
        sign_label = translate("sign", SIGN_NAMES[sign_idx], lang) if lang != "en" else SIGN_SHORT[sign_idx]
        parts.append(f'<text x="{x}" y="{y}" font-size="10" fill="#888">{sign_label}</text>')
        # Asc marker
        if sign_idx == lagna_sign:
            parts.append(
                f'<text x="{col*cell + cell - 16}" y="{row*cell + 14}" '
                f'font-size="11" font-weight="bold" fill="red">As</text>'
            )
        # Planet symbols
        planets = cells.get(sign_idx, [])
        for j, p in enumerate(planets):
            px = col * cell + 8 + (j % 2) * 28
            py = row * cell + 30 + (j // 2) * 16
            parts.append(
                f'<text x="{px}" y="{py}" font-size="13" font-weight="bold">{p}</text>'
            )

    # Title
    parts.append(
        f'<text x="{size//2}" y="{size//2}" text-anchor="middle" '
        f'font-size="14" fill="#666">D1 — {chart.name or "(unnamed)"}</text>'
    )
    parts.append(
        f'<text x="{size//2}" y="{size//2 + 18}" text-anchor="middle" '
        f'font-size="11" fill="#888">South Indian style</text>'
    )
    parts.append('</svg>')
    return "".join(parts)


# ─── North Indian (diamond) ────────────────────────────────────────────────
# 12 houses, lagna fixed at TOP. Signs rotate.
# Layout (house positions in unit square):
#     - H1 = top-center diamond
#     - H2 = upper-left
#     - H3 = left-upper outer
#     - H4 = left-center diamond (= lagna's 4th house)
#     - H5 = left-lower outer
#     - H6 = lower-left
#     - H7 = bottom-center diamond
#     ... etc clockwise
#
# We'll use polygon coordinates that mimic the classical Bandhu chakra.
def render_north(chart, lang: str = "en", size: int = 480) -> str:
    """Render a North Indian (diamond) style D1 chart as SVG."""
    cells: dict[int, list[str]] = {i: [] for i in range(1, 13)}
    lagna_sign = int(chart.lagna_lon // 30)
    for planet, lon in chart.positions.items():
        sign = int(lon // 30)
        house = ((sign - lagna_sign) % 12) + 1
        cells[house].append(PLANET_SHORT.get(planet, planet[:2]))

    s = size
    # 4 inner-diamond houses (1, 4, 7, 10) — rotated squares
    # 8 outer triangular houses
    # We'll define each house as a polygon + a centroid for text.
    cx, cy = s/2, s/2
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" '
        f'viewBox="0 0 {s} {s}" style="font-family:sans-serif">',
        f'<rect x="0" y="0" width="{s}" height="{s}" fill="white" stroke="black" stroke-width="2"/>',
        # Outer square with two diagonals creates 4 triangles
        f'<line x1="0" y1="0" x2="{s}" y2="{s}" stroke="black"/>',
        f'<line x1="{s}" y1="0" x2="0" y2="{s}" stroke="black"/>',
        # Inner diamond connecting midpoints
        f'<polygon points="{s/2},0 {s},{s/2} {s/2},{s} 0,{s/2}" '
        f'fill="none" stroke="black" stroke-width="1.5"/>',
    ]

    # Centroids for each of the 12 houses (North Indian convention,
    # lagna at top, going clockwise but North uses a specific order).
    # House → (x, y) for text label. Standard layout:
    #   H1 = top-center (above inner diamond)
    #   H2 = upper-left small triangle
    #   H3 = upper-left larger triangle (between H2 and H4)
    #   H4 = left-center (left of inner diamond)
    #   ... etc
    centroids = {
        1:  (cx, s/4),                  # top
        2:  (s/4, s/8),                 # upper-left small
        3:  (s/8, s/4),                 # upper-left larger
        4:  (s/4, cy),                  # left-center
        5:  (s/8, 3*s/4),               # lower-left larger
        6:  (s/4, 7*s/8),               # lower-left small
        7:  (cx, 3*s/4),                # bottom
        8:  (3*s/4, 7*s/8),             # lower-right small
        9:  (7*s/8, 3*s/4),             # lower-right larger
        10: (3*s/4, cy),                # right-center
        11: (7*s/8, s/4),               # upper-right larger
        12: (3*s/4, s/8),               # upper-right small
    }

    for house, (x, y) in centroids.items():
        sign_idx = (lagna_sign + house - 1) % 12
        sign_label = translate("sign", SIGN_NAMES[sign_idx], lang) if lang != "en" else SIGN_SHORT[sign_idx]
        # Sign label
        parts.append(
            f'<text x="{x}" y="{y - 18}" text-anchor="middle" '
            f'font-size="10" fill="#888">{sign_label}</text>'
        )
        # House number (small)
        parts.append(
            f'<text x="{x - 18}" y="{y - 18}" text-anchor="middle" '
            f'font-size="9" fill="#bbb">{house}</text>'
        )
        # Planets
        planets = cells.get(house, [])
        for j, p in enumerate(planets):
            row = j // 2
            col = j % 2
            px = x - 14 + col * 28
            py = y + 4 + row * 14
            parts.append(
                f'<text x="{px}" y="{py}" font-size="12" font-weight="bold">{p}</text>'
            )
        # Asc marker on H1
        if house == 1:
            parts.append(
                f'<text x="{x + 22}" y="{y - 18}" font-size="11" '
                f'font-weight="bold" fill="red">As</text>'
            )

    parts.append(
        f'<text x="{cx}" y="{s - 8}" text-anchor="middle" '
        f'font-size="11" fill="#666">D1 — {chart.name or "(unnamed)"} '
        f'· North Indian style</text>'
    )
    parts.append('</svg>')
    return "".join(parts)


# ─── Save helper ───────────────────────────────────────────────────────────
def save(svg_str: str, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg_str)
