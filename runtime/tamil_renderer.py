"""
Tamil text renderer for ReportLab using uharfbuzz shaping + fontTools glyph outlines.

ReportLab's default text rendering doesn't shape complex scripts (Tamil combining
vowels, conjuncts, ligatures don't render correctly). This module uses HarfBuzz
to shape Tamil text into glyph IDs + positions, then draws each glyph as Bezier
paths on the Canvas.

Public API:
  - TamilLine(text, font_size=11, color=black) — single-line Flowable
  - shape_tamil(text, font_size=11) → list of (glyph_outline, x, y) tuples
  - draw_tamil(canvas, text, x, y, font_size) — draw text at position
"""
import os
from pathlib import Path
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
from reportlab.platypus.flowables import Flowable
from reportlab.lib.colors import black
from reportlab.pdfgen.canvas import Canvas

_FONT_DIR = Path(__file__).resolve().parent

# ─── Font registry (one-time load per font file) ─────────────────────────────
_FONTS = {}  # name → {'hb_font', 'tt_font', 'glyph_set', 'upem'}

def register_tamil_font(name, ttf_path):
    """Load a font for Tamil shaping + register with ReportLab pdfmetrics
    so invisible-text layer works (needs the font in canvas's text engine).
    """
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont as RLTTFont

    ttf_path = Path(ttf_path)
    if not ttf_path.is_absolute():
        ttf_path = _FONT_DIR / ttf_path
    with open(ttf_path, "rb") as f:
        data = f.read()
    blob = hb.Blob(data)
    face = hb.Face(blob)
    hb_font = hb.Font(face)
    tt_font = TTFont(str(ttf_path))
    glyph_set = tt_font.getGlyphSet()
    _FONTS[name] = {
        "hb_font": hb_font,
        "tt_font": tt_font,
        "glyph_set": glyph_set,
        "upem": face.upem,
    }
    # Register with ReportLab's pdfmetrics so canvas.setFont(name) works
    try:
        pdfmetrics.registerFont(RLTTFont(name, str(ttf_path)))
    except Exception:
        pass  # already registered


# Auto-register Noto Sans Tamil
register_tamil_font("Tamil", "NotoSansTamil-Regular.ttf")
register_tamil_font("Tamil-Bold", "NotoSansTamil-Bold.ttf")

# Auto-register Outfit for premium Latin / numeric typography in Tamil reports
register_tamil_font("Outfit", "Outfit-Regular.ttf")
register_tamil_font("Outfit-Bold", "Outfit-Bold.ttf")
register_tamil_font("Outfit-Medium", "Outfit-Medium.ttf")
register_tamil_font("Outfit-Light", "Outfit-Light.ttf")

# Auto-register Noto Sans Devanagari for premium Devanagari shaping in Hindi reports
register_tamil_font("Devanagari", "NotoSansDevanagari-Regular.ttf")
register_tamil_font("Devanagari-Bold", "NotoSansDevanagari-Bold.ttf")


class _BezierPen(BasePen):
    """Pen that emits Bezier path commands into a ReportLab Canvas path."""
    def __init__(self, glyph_set, path, scale=1.0, dx=0, dy=0):
        super().__init__(glyph_set)
        self.path = path
        self.scale = scale
        self.dx = dx
        self.dy = dy
    def _moveTo(self, pt):
        self.path.moveTo(pt[0]*self.scale + self.dx, pt[1]*self.scale + self.dy)
    def _lineTo(self, pt):
        self.path.lineTo(pt[0]*self.scale + self.dx, pt[1]*self.scale + self.dy)
    def _curveToOne(self, p1, p2, p3):
        self.path.curveTo(
            p1[0]*self.scale + self.dx, p1[1]*self.scale + self.dy,
            p2[0]*self.scale + self.dx, p2[1]*self.scale + self.dy,
            p3[0]*self.scale + self.dx, p3[1]*self.scale + self.dy,
        )
    def _closePath(self):
        self.path.close()


def measure_tamil(text, font_name="Tamil", font_size=11):
    """Return (width_in_points, height_in_points) for shaped text."""
    if font_name not in _FONTS:
        font_name = "Tamil"
    f = _FONTS[font_name]
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(f["hb_font"], buf, {})
    positions = buf.glyph_positions
    scale = font_size / f["upem"]
    width = sum(p.x_advance for p in positions) * scale
    # Approximate height = font_size (caps + ascent + descent)
    return width, font_size * 1.4


def draw_tamil(canvas, text, x, y, font_name="Tamil", font_size=11, color=None):
    """Draw shaped Tamil text at position (x, y) on the given canvas.
    Returns the total x_advance (line width).

    Two-layer rendering:
      1. VISIBLE: draws each shaped HarfBuzz glyph as Bezier paths (correct shaping)
      2. INVISIBLE: also draws the original Unicode text in rendering mode 3
         (invisible) so the PDF is text-searchable + copy-pasteable.
    """
    if font_name not in _FONTS:
        font_name = "Tamil"
    f = _FONTS[font_name]
    if color is not None:
        canvas.setFillColor(color)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(f["hb_font"], buf, {})
    infos = buf.glyph_infos
    positions = buf.glyph_positions
    scale = font_size / f["upem"]
    cur_x = x
    cur_y = y
    for info, pos in zip(infos, positions):
        glyph_id = info.codepoint
        glyph_name = f["tt_font"].getGlyphName(glyph_id)
        if glyph_name in f["glyph_set"]:
            glyph = f["glyph_set"][glyph_name]
            path = canvas.beginPath()
            pen = _BezierPen(f["glyph_set"], path, scale,
                              cur_x + pos.x_offset * scale,
                              cur_y + pos.y_offset * scale)
            glyph.draw(pen)
            canvas.drawPath(path, fill=1, stroke=0)
        cur_x += pos.x_advance * scale
        cur_y += pos.y_advance * scale
    total_advance = cur_x - x

    # ── Hidden text layer for search/select ──
    # Render mode 3 = invisible. Text in PDF stream so search/select works.
    try:
        canvas.saveState()
        text_obj = canvas.beginText(x, y)
        text_obj.setFont(font_name, font_size)
        text_obj.setTextRenderMode(3)  # invisible
        text_obj.textOut(text)
        canvas.drawText(text_obj)
        canvas.restoreState()
    except Exception as _e:
        import sys
        sys.stderr.write(f"[tamil_renderer] hidden-text failed: {_e}\n")

    return total_advance


# ─── Mixed Tamil/Latin handling ───────────────────────────────────────────────

def _char_script(c):
    o = ord(c)
    if 0x0B80 <= o <= 0x0BFF:
        return "tamil"
    elif 0x0900 <= o <= 0x097F:
        return "devanagari"
    else:
        return "latin"


def _segment_mixed(text):
    """Split text into runs of Tamil vs Devanagari vs Latin. Returns list of (run, script)."""
    if not text: return []
    runs = []
    cur = []
    cur_script = _char_script(text[0])
    for c in text:
        scr = _char_script(c)
        # Treat digits, spaces, punctuation as neutral - keep them in current run
        if c.isascii() and (c.isdigit() or c.isspace() or c in ".,;:!?-/()'\"#$%&+*=<>[]{}|\\@"):
            cur.append(c)
        elif scr == cur_script:
            cur.append(c)
        else:
            if cur:
                runs.append(("".join(cur), cur_script))
            cur = [c]
            cur_script = scr
    if cur:
        runs.append(("".join(cur), cur_script))
    return runs


def draw_mixed(canvas, text, x, y, font_size=11,
                tamil_font="Tamil", latin_font="Outfit", color=None):
    """Draw mixed Tamil+Devanagari+Latin text. Returns total width."""
    if color is not None:
        canvas.setFillColor(color)
    cur_x = x
    for run, script in _segment_mixed(text):
        if script == "tamil":
            w = draw_tamil(canvas, run, cur_x, y, tamil_font, font_size, color)
            cur_x += w
        elif script == "devanagari":
            dev_font = "Devanagari-Bold" if "bold" in tamil_font.lower() else "Devanagari"
            w = draw_tamil(canvas, run, cur_x, y, dev_font, font_size, color)
            cur_x += w
        else:
            canvas.setFont(latin_font, font_size)
            canvas.drawString(cur_x, y, run)
            cur_x += canvas.stringWidth(run, latin_font, font_size)
    return cur_x - x


def measure_mixed(text, font_size=11, tamil_font="Tamil", latin_font="Outfit",
                   stub_canvas=None):
    """Width of mixed Tamil+Devanagari+Latin text."""
    from reportlab.pdfbase import pdfmetrics
    total = 0
    for run, script in _segment_mixed(text):
        if script == "tamil":
            w, _ = measure_tamil(run, tamil_font, font_size)
            total += w
        elif script == "devanagari":
            dev_font = "Devanagari-Bold" if "bold" in tamil_font.lower() else "Devanagari"
            w, _ = measure_tamil(run, dev_font, font_size)
            total += w
        else:
            total += pdfmetrics.stringWidth(run, latin_font, font_size)
    return total


# ─── Flowable that wraps + draws Tamil text ──────────────────────────────────

class TamilParagraph(Flowable):
    """A Flowable for mixed Tamil+Latin text with auto-wrapping.

    Args:
        text: str — Tamil + Latin content
        font_size: int — font size in points
        leading: float — line height multiplier (default 1.5)
        color: ReportLab color (default black)
        bold: bool — use Tamil-Bold + Outfit-Bold
        align: 'left' / 'center' / 'right'
    """
    def __init__(self, text, font_size=11, leading=1.5, color=None,
                 bold=False, align="left", indent=0, space_after=4):
        super().__init__()
        self.text = text
        self.font_size = font_size
        self.leading = leading
        self.color = color if color is not None else black
        self.tamil_font = "Tamil-Bold" if bold else "Tamil"
        self.latin_font = "Outfit-Bold" if bold else "Outfit"
        self.align = align
        self.indent = indent
        self.space_after = space_after
        self._lines = None
        self._line_widths = None
        self._wrap_width = None

    def _wrap_text(self, available_width):
        """Word-wrap text to fit available_width. Stores lines + widths."""
        # Split on whitespace, treating each word as a unit
        # Then assemble lines based on width
        words = self.text.split(" ")
        lines = []
        line_widths = []
        cur_line = []
        cur_width = 0
        space_w = measure_mixed(" ", self.font_size, self.tamil_font, self.latin_font)
        for word in words:
            if not word:
                continue
            w = measure_mixed(word, self.font_size, self.tamil_font, self.latin_font)
            if cur_line and (cur_width + space_w + w) > available_width:
                lines.append(" ".join(cur_line))
                line_widths.append(cur_width)
                cur_line = [word]
                cur_width = w
            else:
                if cur_line:
                    cur_width += space_w + w
                    cur_line.append(word)
                else:
                    cur_line = [word]
                    cur_width = w
        if cur_line:
            lines.append(" ".join(cur_line))
            line_widths.append(cur_width)
        self._lines = lines
        self._line_widths = line_widths
        self._wrap_width = available_width

    def wrap(self, availWidth, availHeight):
        eff_w = availWidth - self.indent
        if self._wrap_width != eff_w:
            self._wrap_text(eff_w)
        h = len(self._lines) * self.font_size * self.leading + self.space_after
        return (availWidth, h)

    def draw(self):
        c = self.canv
        c.saveState()
        line_h = self.font_size * self.leading
        # ReportLab origin is bottom-left of flowable; we draw from top
        # Total drawing area height = num_lines * line_h
        n = len(self._lines)
        y_top = n * line_h  # top of text area
        for i, (line, w) in enumerate(zip(self._lines, self._line_widths)):
            # Y: baseline of line i (top line is i=0)
            y = y_top - (i + 1) * line_h + line_h * 0.25  # baseline offset

            # Compute x based on alignment
            if self.align == "justify" and i < n - 1:
                words = [wd for wd in line.split(" ") if wd]
                if len(words) > 1:
                    total_words_w = sum(measure_mixed(wd, self.font_size, self.tamil_font, self.latin_font) for wd in words)
                    extra_space = self._wrap_width - total_words_w
                    gap = extra_space / (len(words) - 1)
                    cur_x = self.indent
                    for wd in words:
                        w_wd = draw_mixed(c, wd, cur_x, y, self.font_size,
                                           self.tamil_font, self.latin_font, self.color)
                        cur_x += w_wd + gap
                    continue

            if self.align == "center":
                x = self.indent + (self._wrap_width - w) / 2
            elif self.align == "right":
                x = self.indent + self._wrap_width - w
            else:
                x = self.indent
            
            draw_mixed(c, line, x, y, self.font_size,
                        self.tamil_font, self.latin_font, self.color)
        c.restoreState()


# ─── Self-test ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.lib.colors import HexColor
    from reportlab.platypus import SimpleDocTemplate, Spacer

    INDIGO = HexColor("#312e81")
    GOLD = HexColor("#b88a37")
    GREY = HexColor("#6b6b6b")

    flow = [
        TamilParagraph("தமிழ் வேத ஜாதகம் - ஆழ்ந்த பகுப்பாய்வு",
                        font_size=22, bold=True, color=INDIGO, align="center", leading=1.4),
        TamilParagraph("சரியான தமிழ் ஃபாண்ட் வடிவமைப்பு + இணைப்பு",
                        font_size=12, color=GREY, align="center"),
        Spacer(1, 0.5*cm),
        TamilParagraph("முழு வாழ்க்கை ஜாதகம் - ஆழ்ந்த பகுப்பாய்வு",
                        font_size=14, bold=True),
        TamilParagraph("ஜாதகர் பெயர்: மனோஜ்குமார்",
                        font_size=12),
        TamilParagraph("பிறந்த தேதி: 25-05-1996 (சனிக்கிழமை) நேரம்: இரவு 8:25 மணி",
                        font_size=11),
        TamilParagraph("பிறந்த ஊர்: கோவில்பாளையம், கோயம்புத்தூர்",
                        font_size=11),
        Spacer(1, 0.3*cm),
        TamilParagraph("கிரக நிலைகள்:", font_size=14, bold=True, color=INDIGO),
        TamilParagraph("• சூரியன் - ரிஷபம் ராசி, ரோகிணி நட்சத்திரம், 10°51'", font_size=11),
        TamilParagraph("• சந்திரன் - சிம்மம் ராசி, மகம் நட்சத்திரம் (4 ஆம் பாதம்), 11°11'", font_size=11),
        TamilParagraph("• செவ்வாய் - மேஷம் ராசி, பரணி நட்சத்திரம், 23°09'", font_size=11),
        TamilParagraph("• புதன் - மேஷம் ராசி, பரணி நட்சத்திரம், 26°00'", font_size=11),
        TamilParagraph("• குரு - தனுசு ராசி, பூராடம் நட்சத்திரம், 23°09'", font_size=11),
        TamilParagraph("• சுக்கிரன் - மிதுனம் ராசி, மிருகசிரஷம் நட்சத்திரம், 03°54'", font_size=11),
        TamilParagraph("• சனி - மீனம் ராசி, உத்திரட்டாதி நட்சத்திரம், 11°14'", font_size=11),
        TamilParagraph("• ராகு - கன்னி ராசி, ஹஸ்தம் நட்சத்திரம், 20°55'", font_size=11),
        TamilParagraph("• கேது - மீனம் ராசி, ரேவதி நட்சத்திரம், 20°55'", font_size=11),
        Spacer(1, 0.4*cm),
        TamilParagraph("உங்களின் லக்னம் தனுசு ஆகும். இதன் அதிபதி குரு. தற்போது நீங்கள் "
                        "சந்திரன் தசையில் இருக்கிறீர்கள் (2023 முதல் 2033 வரை). இந்த "
                        "தசையின் கருப்பொருள் உணர்ச்சி வளர்ச்சி, குடும்பம் மற்றும் "
                        "பொது அறிமுகம் ஆகும். தாயார் முக்கியமாகும் காலம்.",
                        font_size=11, leading=1.6),
    ]

    import os
    out_dir = "reports"
    if not os.path.exists(out_dir):
        out_dir = "../reports"
    doc = SimpleDocTemplate(f"{out_dir}/_tamil_shaped_test.pdf", pagesize=A4,
                             leftMargin=2*cm, rightMargin=2*cm,
                             topMargin=2*cm, bottomMargin=2*cm)
    doc.build(flow)
    print(f"Saved: {out_dir}/_tamil_shaped_test.pdf")
