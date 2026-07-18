"""COMPLETE Tamil-Jadhagam PDF — page 1 traditional sheet + ALL 23 prediction domains.

Domains covered (per spec):
  1. Self & Personality (Lagna, Atmakaraka, body type, intellect, ego)
  2. Family — Parents (longevity, health, bond, loss timing)
  3. Family — Siblings (number, relationship, success)
  4. Education (primary, higher, foreign, technical, arts)
  5. Marriage (timing, spouse character, profession, doshas, divorce risk)
  6. Children (number, gender, success, late arrival)
  7. Career & Profession (field, timeline, govt vs private, promotions)
  8. Wealth (potential, sources, inheritance, debt, peaks)
  9. Health (constitution, predispositions, surgery, longevity, type of death)
 10. Travel & Foreign Influence
 11. Property & Assets
 12. Social Status, Fame, Power
 13. Relationships & Enemies
 14. Spirituality (religion, guru, moksha)
 15. Talents & Skills (music, sports, writing, languages)
 16. Past Lives & Karma (Pitri/Matri rin, Bhagya)
 17. Annual Predictions (Varshaphala — current year theme)
 18. Daily/Muhurta principles
 19. Specific yogas detected from chart
 20. Chara Karakas (AK/AmK/BK/MK/PK/GK/DK)
 21. Nakshatra-level personality
 22. Specific event probabilities (lottery, imprisonment, etc.)
 23. Lifetime karmic themes summary

PLUS each Maha Dasha as its own chapter page (9 chapters).

Output: ATRO_ROOT/reports/<NAME>_FULL_REPORT.pdf
"""
import json, sys, math, argparse
from pathlib import Path
import datetime as dt
import os as _os

# Robust import bootstrap: guarantee both the project root (for `engine.*`) and
# this runtime/ dir (for flat modules like `vedic_core`) are importable, no matter
# what CWD or invocation style is used. Without this, `from engine.shadbala import ...`
# below only resolves by accidental side-effect of an earlier import mutating sys.path.
_HERE = _os.path.dirname(_os.path.abspath(__file__))
_ROOT = _os.path.dirname(_HERE)
for _p in (_ROOT, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from vedic_core import RASIS, RASI_LORDS, DIGNITIES

sys.stdout.reconfigure(encoding="utf-8")

# ─── Register Premium Fonts ───
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

_RUNTIME_DIR = os.path.dirname(os.path.abspath(__file__))
try:
    # Register Outfit
    pdfmetrics.registerFont(TTFont("Outfit", os.path.join(_RUNTIME_DIR, "Outfit-Regular.ttf")))
    pdfmetrics.registerFont(TTFont("Outfit-Bold", os.path.join(_RUNTIME_DIR, "Outfit-Bold.ttf")))
    pdfmetrics.registerFont(TTFont("Outfit-Medium", os.path.join(_RUNTIME_DIR, "Outfit-Medium.ttf")))
    pdfmetrics.registerFont(TTFont("Outfit-Light", os.path.join(_RUNTIME_DIR, "Outfit-Light.ttf")))
    # Register Noto Sans Devanagari (for Hindi support)
    pdfmetrics.registerFont(TTFont("NotoSansDevanagari", os.path.join(_RUNTIME_DIR, "NotoSansDevanagari-Regular.ttf")))
    pdfmetrics.registerFont(TTFont("NotoSansDevanagari-Bold", os.path.join(_RUNTIME_DIR, "NotoSansDevanagari-Bold.ttf")))
    
    # Overwrite Helvetica globally with Outfit for ultimate premium visual styling!
    pdfmetrics.registerFont(TTFont("Helvetica", os.path.join(_RUNTIME_DIR, "Outfit-Regular.ttf")))
    pdfmetrics.registerFont(TTFont("Helvetica-Bold", os.path.join(_RUNTIME_DIR, "Outfit-Bold.ttf")))
    pdfmetrics.registerFont(TTFont("Helvetica-Oblique", os.path.join(_RUNTIME_DIR, "Outfit-Light.ttf")))
except Exception as e:
    sys.stderr.write(f"[generate_report] Font registration failed: {e}\n")

import os
ATRO = Path(os.environ.get("ATRO_ROOT", Path(__file__).resolve().parent.parent))
CHARTS = Path(os.environ.get("ATRO_CHARTS", ATRO / "charts"))
REPORTS = Path(os.environ.get("ATRO_REPORTS", ATRO / "reports"))
REPORTS.mkdir(parents=True, exist_ok=True)

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (Paragraph, Spacer, PageBreak, Table, TableStyle,
                                  Flowable, BaseDocTemplate, PageTemplate, Frame,
                                  NextPageTemplate, KeepTogether)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, white
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY, TA_RIGHT

# ─── PALETTE ────────────────────────────────────────────
INDIGO=HexColor("#1a1d3a"); GOLD=HexColor("#c9a032"); GOLD_LT=HexColor("#e5cd6c")
GOLD_DK=HexColor("#8a6a18"); CREAM=HexColor("#faf6e8"); CREAM_2=HexColor("#fff8e1")
PURPLE=HexColor("#5d2e8c"); MAROON=HexColor("#7d1f3d"); GREY_DK=HexColor("#2a2a2a")
GREY_MD=HexColor("#5a5a5a"); GREY_LT=HexColor("#e8e6e2")
GREEN_BG=HexColor("#e6f5ec"); RED_BG=HexColor("#fbe6ec")
SHEET_BG=HexColor("#fdfaf2"); SHEET_LINE=HexColor("#444444")
RED_INK=HexColor("#c0392b"); BLUE_INK=HexColor("#1f3a4a")

PLANET_COLOR={"Mercury":HexColor("#0d8a8a"),"Ketu":HexColor("#5a3a8c"),
              "Venus":HexColor("#d65a8c"),"Sun":HexColor("#e07a1f"),
              "Moon":HexColor("#7798bd"),"Mars":HexColor("#b91c4f"),
              "Rahu":HexColor("#3d4f7a"),"Jupiter":HexColor("#c9802a"),
              "Saturn":HexColor("#1f3a4a")}
PLANET_GLYPH={"Mercury":"☿","Ketu":"☋","Venus":"♀","Sun":"☉","Moon":"☾",
              "Mars":"♂","Rahu":"☊","Jupiter":"♃","Saturn":"♄"}
PLANET_SHORT={"Sun":"Su","Moon":"Mo","Mars":"Ma","Mercury":"Me","Jupiter":"Ju",
              "Venus":"Ve","Saturn":"Sa","Rahu":"Ra","Ketu":"Ke"}

RASI_SHORT=["Ari","Tau","Gem","Can","Leo","Vir","Lib","Sco","Sag","Cap","Aqu","Pis"]

ICON={"career":"♛","wealth":"❖","health":"❣","marriage":"❀","family":"✦",
      "spirit":"☸","ok":"✓","warn":"!","star":"★","starlt":"☆",
      "self":"☥","education":"📖","children":"⚭","travel":"✈",
      "property":"⌂","status":"⚜","talent":"♪","past":"☯",
      "annual":"⊙","muhurta":"⌛","prashna":"?"}

VIMSHOTTARI_YEARS={"Ketu":7,"Venus":20,"Sun":6,"Moon":10,"Mars":7,"Rahu":18,"Jupiter":16,"Saturn":19,"Mercury":17}
VIMSHOTTARI_ORDER=["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"]
NAK_LORDS_27=["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"]*3
HOUSE_THEMES={1:"self, body, personality",2:"wealth, family, speech",
              3:"siblings, courage, communication",4:"home, mother, comforts",
              5:"children, creativity, intelligence",6:"work, enemies, health",
              7:"spouse, partnerships, business",8:"transformation, occult, longevity",
              9:"dharma, fortune, father, foreign",10:"career, fame, status",
              11:"gains, friends, elder siblings",12:"loss, foreign, spirituality"}
PLANET_ARCHETYPES={"Sun":"father, authority, ego, leadership, government, soul",
                    "Moon":"mother, mind, emotions, public, comforts",
                    "Mars":"siblings, courage, energy, conflict, real estate, surgery",
                    "Mercury":"intellect, speech, commerce, writing, communication",
                    "Jupiter":"wisdom, dharma, children, wealth, expansion",
                    "Venus":"spouse, luxury, arts, beauty, vehicles, comforts",
                    "Saturn":"discipline, longevity, servants, delays, sorrow",
                    "Rahu":"foreign, unconventional, technology, sudden gain",
                    "Ketu":"spirituality, detachment, past karma, moksha"}

NAKSHATRA_PERSONALITY = {
    "Ashwini":"pioneer, healer, fast action, warrior energy",
    "Bharani":"intense, transformative, sexual energy, restraint",
    "Krittika":"sharp, cutting, purifying, fiery leader",
    "Rohini":"beauty, luxury, growth, sensual, fertile",
    "Mrigashira":"seeker, curious, gentle, eternal student",
    "Ardra":"emotional storm, breakthrough through crisis, intense",
    "Punarvasu":"renewal, return, optimist, spiritual",
    "Pushya":"nourisher, loyal, traditional, religious",
    "Ashlesha":"intuitive, hypnotic, snake energy, secretive",
    "Magha":"kingly, ancestor-aware, leadership, royal lineage",
    "Purva Phalguni":"pleasure, creative, charming, romantic",
    "Uttara Phalguni":"helpful, friendly, generous, balanced",
    "Hasta":"skilled, dexterous, healing hands, craftsman",
    "Chitra":"artistic, brilliant, designer, attractive",
    "Swati":"independent, balanced, diplomatic, breeze-like",
    "Vishakha":"goal-oriented, achiever, two-faced, focused",
    "Anuradha":"devoted, friendly, loyal, success through cooperation",
    "Jyeshtha":"elder, protective, controlling, responsible",
    "Mula":"root, destruction-and-rebirth, philosophical, fierce",
    "Purva Ashadha":"invincible, ambitious, debate, water-strong",
    "Uttara Ashadha":"final victory, eternal goal, leadership, ethical",
    "Shravana":"listener, learner, traditional knowledge, fame",
    "Dhanishta":"musical, wealthy, generous, group leader",
    "Shatabhisha":"healer, mystic, secretive, hundred remedies",
    "Purva Bhadrapada":"intense, fierce, two-faced, transformative",
    "Uttara Bhadrapada":"deep wisdom, quiet, spiritual, serpent of depth",
    "Revati":"nurturing, prosperous, last journey, completion"
}


def hexstr(c): return "#"+c.hexval()[2:]


# ─── STYLES ────────────────────────────────────────
body=ParagraphStyle("body",fontSize=10.5,alignment=TA_JUSTIFY,
    textColor=GREY_DK,spaceAfter=6,fontName="Helvetica",leading=15)
body_small=ParagraphStyle("bs",fontSize=9.5,alignment=TA_LEFT,
    textColor=GREY_DK,fontName="Helvetica",leading=14,spaceAfter=4)
h1=ParagraphStyle("h1",fontSize=22,alignment=TA_LEFT,textColor=INDIGO,
    spaceAfter=4,spaceBefore=12,fontName="Helvetica-Bold",leading=28)
h1_sub=ParagraphStyle("h1s",fontSize=10.5,alignment=TA_LEFT,textColor=GOLD_DK,
    spaceAfter=14,fontName="Helvetica-Oblique",leading=14)
h2=ParagraphStyle("h2",fontSize=14,alignment=TA_LEFT,textColor=PURPLE,
    spaceAfter=8,spaceBefore=12,fontName="Helvetica-Bold",leading=18)
h3=ParagraphStyle("h3",fontSize=11,alignment=TA_LEFT,textColor=MAROON,
    spaceAfter=4,spaceBefore=6,fontName="Helvetica-Bold",leading=14)


# ─── FLOWABLES ─────────────────────────────────────
class Rule(Flowable):
    def __init__(self,w,c=GOLD,th=0.6):
        Flowable.__init__(self); self.w=w; self.c=c; self.th=th
    def wrap(self,*a): return (self.w,self.th)
    def draw(self):
        self.canv.setStrokeColor(self.c); self.canv.setLineWidth(self.th)
        self.canv.line(0,0,self.w,0)


SOUTH_INDIAN_LAYOUT={11:(0,0),0:(0,1),1:(0,2),2:(0,3),
                      10:(1,0),3:(1,3),9:(2,0),4:(2,3),
                      8:(3,0),7:(3,1),6:(3,2),5:(3,3)}


class SouthIndianChart(Flowable):
    def __init__(self, size, positions, lagna_idx, title="RASI"):
        Flowable.__init__(self)
        self.size=size; self.height=size; self.width=size
        self.positions=positions; self.lagna_idx=lagna_idx; self.title=title
    def wrap(self,*a): return (self.width,self.height)
    def draw(self):
        c=self.canv; cell=self.size/4
        c.setStrokeColor(GOLD); c.setLineWidth(2.2)
        c.rect(0,0,self.size,self.size,fill=0,stroke=1)
        c.setStrokeColor(SHEET_LINE); c.setLineWidth(0.6)
        c.line(cell,0,cell,self.size); c.line(cell*3,0,cell*3,self.size)
        c.line(cell*2,cell*3,cell*2,self.size); c.line(cell*2,0,cell*2,cell)
        c.line(0,cell*3,self.size,cell*3); c.line(0,cell,self.size,cell)
        c.line(0,cell*2,cell,cell*2); c.line(cell*3,cell*2,self.size,cell*2)
        c.setFillColor(GOLD); c.rect(cell,cell,cell*2,cell*2,fill=1,stroke=0)
        c.setFillColor(INDIGO); c.setFont("Helvetica-Bold",14)
        c.drawCentredString(self.size/2,self.size/2+4,self.title)
        c.setFont("Helvetica-Oblique",8)
        c.drawCentredString(self.size/2,self.size/2-12,"South Indian")
        from collections import defaultdict
        by_rasi=defaultdict(list)
        for p,ri in self.positions.items(): by_rasi[ri].append(p)
        for rasi_idx,(row,col) in SOUTH_INDIAN_LAYOUT.items():
            x=col*cell; y=(3-row)*cell
            if rasi_idx==self.lagna_idx:
                c.setFillColor(CREAM_2); c.rect(x,y,cell,cell,fill=1,stroke=0)
                c.setStrokeColor(SHEET_LINE); c.setLineWidth(0.6)
                c.rect(x,y,cell,cell,fill=0,stroke=1)
            c.setFillColor(GOLD_DK); c.setFont("Helvetica-Bold",7)
            c.drawString(x+4,y+cell-10,RASI_SHORT[rasi_idx])
            if rasi_idx==self.lagna_idx:
                c.setFillColor(RED_INK); c.setFont("Helvetica-Bold",8)
                c.drawRightString(x+cell-4,y+cell-10,"Lag")
            planets=by_rasi.get(rasi_idx,[])
            if planets:
                if len(planets)<=2: fsz=10; per=1
                elif len(planets)<=4: fsz=9; per=2
                else: fsz=8; per=2
                lh=fsz+4
                c.setFont("Helvetica-Bold",fsz)
                start_y=y+cell-22
                for i,p in enumerate(planets):
                    rr=i//per; cc=i%per
                    px=x+6+cc*(cell/per-4); py=start_y-rr*lh
                    c.setFillColor(PLANET_COLOR.get(p,BLUE_INK))
                    c.drawString(px,py,PLANET_SHORT.get(p,p[:2]))


class HeaderBar(Flowable):
    def __init__(self,width,name,bd,bt,bp,wd):
        Flowable.__init__(self); self.width=width; self.height=60
        self.name=name; self.bd=bd; self.bt=bt; self.bp=bp; self.wd=wd
    def wrap(self,*a): return (self.width,self.height)
    def draw(self):
        c=self.canv
        c.setFillColor(INDIGO); c.rect(0,0,self.width,self.height,fill=1,stroke=0)
        c.setFillColor(GOLD)
        c.rect(0,self.height-3,self.width,3,fill=1,stroke=0)
        c.rect(0,0,self.width,2,fill=1,stroke=0)
        c.setFillColor(GOLD); c.setFont("Helvetica-Bold",22)
        c.drawString(20,self.height/2+4,self.name)
        c.setFillColor(GOLD_LT); c.setFont("Helvetica-Oblique",9)
        c.drawString(20,self.height/2-14,"VEDIC ASTROLOGY · BIRTH CHART READING")
        c.setFillColor(CREAM); c.setFont("Helvetica-Bold",10)
        c.drawRightString(self.width-20,self.height-20,
                          f"{self.bd}  ·  {self.bt}  ·  {self.wd}")
        c.setFillColor(GOLD_LT); c.setFont("Helvetica",9)
        c.drawRightString(self.width-20,self.height-36,self.bp)
        c.drawRightString(self.width-20,self.height-50,
                          f"Generated: {dt.datetime.now().strftime('%d-%b-%Y')}")


class TimelineBar(Flowable):
    def __init__(self,w,dashas,age):
        Flowable.__init__(self); self.width=w; self.height=130
        self.dashas=dashas; self.age=age
        self.total=max(d[2] for d in dashas)
    def wrap(self,*a): return (self.width,self.height)
    def draw(self):
        c=self.canv
        c.setFillColor(INDIGO); c.setFont("Helvetica-Bold",11)
        c.drawString(0,self.height-12,"LIFE TIMELINE")
        c.setFillColor(GOLD_DK); c.setFont("Helvetica-Oblique",9)
        c.drawString(0,self.height-26,"Vimshottari Maha Dasha sequence")
        bar_y=50; bar_h=38; bar_w=self.width
        for lord,af,at in self.dashas:
            xf=bar_w*(af/self.total); xt=bar_w*(at/self.total); sw=xt-xf
            c.setFillColor(PLANET_COLOR.get(lord,GREY_MD))
            c.rect(xf,bar_y,sw,bar_h,fill=1,stroke=0)
            if sw>40:
                c.setFillColor(white); c.setFont("Helvetica-Bold",14)
                c.drawCentredString(xf+sw/2,bar_y+bar_h/2+5,PLANET_GLYPH.get(lord,""))
                c.setFont("Helvetica-Bold",8)
                c.drawCentredString(xf+sw/2,bar_y+bar_h/2-8,lord)
                c.setFont("Helvetica",7)
                c.drawCentredString(xf+sw/2,bar_y-10,f"{af:.0f}-{at:.0f}")
            elif sw>22:
                c.setFillColor(white); c.setFont("Helvetica-Bold",11)
                c.drawCentredString(xf+sw/2,bar_y+bar_h/2+3,PLANET_GLYPH.get(lord,""))
                c.setFont("Helvetica-Bold",7)
                c.drawCentredString(xf+sw/2,bar_y+bar_h/2-8,lord[:3])
                c.setFont("Helvetica",6)
                c.drawCentredString(xf+sw/2,bar_y-9,f"{af:.0f}-{at:.0f}")
            else:
                c.setFillColor(white); c.setFont("Helvetica-Bold",8)
                c.drawCentredString(xf+sw/2,bar_y+bar_h/2-3,PLANET_GLYPH.get(lord,""))
        x_now=bar_w*(self.age/self.total)
        c.setStrokeColor(GOLD); c.setFillColor(GOLD); c.setLineWidth(2.5)
        c.line(x_now,bar_y-6,x_now,bar_y+bar_h+12)
        path=c.beginPath()
        path.moveTo(x_now-7,bar_y+bar_h+12); path.lineTo(x_now+7,bar_y+bar_h+12)
        path.lineTo(x_now,bar_y+bar_h+20); path.close()
        c.drawPath(path,fill=1,stroke=0)
        c.setFillColor(GOLD); c.setFont("Helvetica-Bold",10)
        c.drawCentredString(x_now,bar_y+bar_h+28,f"NOW · age {self.age:.0f}")


class ChapterHeader(Flowable):
    def __init__(self,w,num,planet,dates,ages,theme):
        Flowable.__init__(self); self.width=w; self.height=110
        self.num=num; self.planet=planet; self.dates=dates
        self.ages=ages; self.theme=theme
    def wrap(self,*a): return (self.width,self.height)
    def draw(self):
        c=self.canv; accent=PLANET_COLOR.get(self.planet,INDIGO)
        c.setFillColor(INDIGO); c.rect(0,0,self.width,self.height,fill=1,stroke=0)
        c.setFillColor(accent); c.rect(0,0,12,self.height,fill=1,stroke=0)
        c.setFillColor(GOLD)
        c.rect(0,self.height-3,self.width,3,fill=1,stroke=0)
        c.rect(0,0,self.width,2,fill=1,stroke=0)
        c.setFillColor(accent); c.setFont("Helvetica-Bold",70)
        c.drawRightString(self.width-28,24,PLANET_GLYPH.get(self.planet,""))
        c.setFillColor(GOLD_LT); c.setFont("Helvetica-Bold",10)
        c.drawString(34,self.height-26,f"CHAPTER {self.num}")
        c.setFillColor(CREAM); c.setFont("Helvetica-Bold",28)
        c.drawString(34,self.height-58,self.planet.upper())
        c.setFillColor(GOLD_LT); c.setFont("Helvetica-Bold",12)
        c.drawString(34,self.height-78,"PERIOD")
        c.setFillColor(CREAM); c.setFont("Helvetica",10)
        c.drawString(34,self.height-94,f"{self.dates}    Age {self.ages}")
        c.setFillColor(GOLD_LT); c.setFont("Helvetica-Oblique",10)
        c.drawString(34,14,self.theme.upper())


class DomainHeader(Flowable):
    """Big header for each prediction domain (Self, Family, Career, etc.)"""
    def __init__(self,w,icon,number,title,subtitle):
        Flowable.__init__(self); self.width=w; self.height=70
        self.icon=icon; self.number=number; self.title=title; self.subtitle=subtitle
    def wrap(self,*a): return (self.width,self.height)
    def draw(self):
        c=self.canv
        c.setFillColor(CREAM); c.rect(0,0,self.width,self.height,fill=1,stroke=0)
        c.setFillColor(GOLD); c.rect(0,0,4,self.height,fill=1,stroke=0)
        c.rect(0,self.height-1.5,self.width,1.5,fill=1,stroke=0)
        c.rect(0,0,self.width,1.5,fill=1,stroke=0)
        c.setFillColor(GOLD_DK); c.setFont("Helvetica-Bold",36)
        c.drawString(20,18,self.icon)
        c.setFillColor(GOLD_DK); c.setFont("Helvetica-Bold",10)
        c.drawString(80,self.height-22,f"DOMAIN {self.number}")
        c.setFillColor(INDIGO); c.setFont("Helvetica-Bold",18)
        c.drawString(80,28,self.title)
        c.setFillColor(GOLD_DK); c.setFont("Helvetica-Oblique",10)
        c.drawString(80,12,self.subtitle)


# ─── DASHA / CHART ANALYSIS ──────────────────────
def vimshottari(chart):
    moon=chart["positions"]["Moon"]
    moon_lon=moon.get("lon_abs") or moon.get("lon") or (
        RASIS.index(moon["rasi"])*30+moon.get("deg",0))
    nak_idx=int(moon_lon//(360/27))
    progress=(moon_lon-nak_idx*(360/27))/(360/27)
    nak_lord=NAK_LORDS_27[nak_idx]
    md_remaining=VIMSHOTTARI_YEARS[nak_lord]*(1-progress)
    b=chart["birth"]
    birth_dt=dt.datetime(b["year"],b["month"],b["day"],b["hour"],b["min"])
    mds=[]; cur=nak_lord; cur_start=birth_dt; cur_yrs=md_remaining
    for _ in range(9):
        cur_end=cur_start+dt.timedelta(days=cur_yrs*365.25)
        mds.append({"lord":cur,"start":cur_start,"end":cur_end,"years":cur_yrs,
                    "age_from":(cur_start-birth_dt).days/365.25,
                    "age_to":(cur_end-birth_dt).days/365.25})
        idx=(VIMSHOTTARI_ORDER.index(cur)+1)%9
        cur=VIMSHOTTARI_ORDER[idx]; cur_start=cur_end; cur_yrs=VIMSHOTTARI_YEARS[cur]
    today=dt.datetime.now()
    cur_md=None; cur_ad=None; sub_dashas=[]
    for md in mds:
        md_idx=VIMSHOTTARI_ORDER.index(md["lord"])
        sub_start=md["start"]
        md_subs=[]
        for k in range(9):
            sp=VIMSHOTTARI_ORDER[(md_idx+k)%9]
            sy=md["years"]*VIMSHOTTARI_YEARS[sp]/120
            sub_end=sub_start+dt.timedelta(days=sy*365.25)
            md_subs.append({"md":md["lord"],"ad":sp,"start":sub_start,"end":sub_end,"years":sy})
            sub_start=sub_end
        if md["start"]<=today<=md["end"]:
            cur_md=md
            for s in md_subs:
                if s["start"]<=today<=s["end"]: cur_ad=s; break
        sub_dashas.append({"md":md["lord"],"subs":md_subs})
    return mds,cur_md,cur_ad,sub_dashas


def detect_yogas(chart):
    pos=chart["positions"]; yogas=[]
    MAHAPURUSHA={"Mars":"Ruchaka","Mercury":"Bhadra","Jupiter":"Hamsa","Venus":"Malavya","Saturn":"Sasa"}
    for p,name in MAHAPURUSHA.items():
        if p not in pos: continue
        h=pos[p]["house"]; r=pos[p]["rasi"]
        if h not in [1,4,7,10]: continue
        d=DIGNITIES.get((p,r))
        if d in ["Own","Exalted","Exalted/Own"]:
            yogas.append({"name":f"{name.upper()} YOGA","place":f"{p} ({d}) in {r} kendra (H{h})",
                          "conf":4,"planet":p,
                          "desc":f"Mahapurusha Yoga. {p} in own/exalted in kendra brings {name.lower()}-quality life — disciplined success, recognition, longevity, prosperity in {PLANET_ARCHETYPES[p].split(',')[0]}."})
    if "Moon" in pos and "Jupiter" in pos:
        diff=((pos["Jupiter"]["house"]-pos["Moon"]["house"])%12)+1
        if diff in [1,4,7,10]:
            yogas.append({"name":"GAJA KESARI YOGA","place":f"Jupiter in kendra ({diff}) from Moon",
                          "conf":4,"planet":"Jupiter",
                          "desc":"Wisdom, wealth, fame, generous nature, success in education, respected status, divine grace."})
    if "Sun" in pos and "Mercury" in pos and pos["Sun"]["rasi_idx"]==pos["Mercury"]["rasi_idx"]:
        yogas.append({"name":"BUDHA-ADITYA YOGA","place":f"Sun + Mercury in {pos['Sun']['rasi']}",
                      "conf":3,"planet":"Mercury",
                      "desc":"Sharp intellect, eloquent speech, communication-driven success, public recognition through skill."})
    if "Moon" in pos and "Mars" in pos:
        if pos["Moon"]["rasi_idx"]==pos["Mars"]["rasi_idx"] or abs(pos["Moon"]["rasi_idx"]-pos["Mars"]["rasi_idx"])==6:
            yogas.append({"name":"CHANDRA-MANGALA YOGA","place":"Moon + Mars conjunct or 7th apart",
                          "conf":3,"planet":"Mars",
                          "desc":"Wealth via mother, real estate, business acumen, courage in money matters."})
    if "Rahu" in pos and "Ketu" in pos:
        ri=pos["Rahu"]["rasi_idx"]; ki=pos["Ketu"]["rasi_idx"]; between=0
        for p in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]:
            if p in pos:
                pi=pos[p]["rasi_idx"]
                if ri<ki:
                    if ri<pi<ki: between+=1
                else:
                    if pi>ri or pi<ki: between+=1
        if between==7:
            yogas.append({"name":"KAAL SARPA YOGA","place":f"All 7 planets between Rahu (H{pos['Rahu']['house']}) and Ketu (H{pos['Ketu']['house']})",
                          "conf":3,"planet":"Rahu",
                          "desc":"Karmic life pattern. Repeated themes around control, foreign culture, hidden truths. Mastery through awareness."})
    lagnesh=chart.get("lagna_lord")
    if lagnesh and lagnesh in pos:
        lh=pos[lagnesh]["house"]
        if lh in [1,4,5,7,9,10]:
            yogas.append({"name":f"LAGNESH IN H{lh}","place":f"{lagnesh} (lagna lord) in {pos[lagnesh]['rasi']}, House {lh}",
                          "conf":3,"planet":lagnesh,
                          "desc":f"Self/identity expressed through {HOUSE_THEMES[lh]}. Strong placement — life-force directed toward this domain."})
    for p,pd in pos.items():
        d=DIGNITIES.get((p,pd["rasi"]))
        if d=="Exalted":
            yogas.append({"name":f"{p.upper()} EXALTED","place":f"{p} in {pd['rasi']}, H{pd['house']}",
                          "conf":4,"planet":p,
                          "desc":f"{p}'s significations operate at maximum strength. House {pd['house']} ({HOUSE_THEMES[pd['house']]}) gets a powerful boost."})
        elif d=="Debil":
            yogas.append({"name":f"{p.upper()} DEBILITATED","place":f"{p} in {pd['rasi']}, H{pd['house']}",
                          "conf":3,"planet":p,
                          "desc":f"{p}'s significations weakened. House {pd['house']} faces challenges — Neecha-bhanga can convert this to Vipareeta Raja Yoga."})
    return yogas


def chara_karakas(chart):
    """Compute Chara Karakas — planets sorted by degree (excluding Ketu)."""
    pos=chart["positions"]
    plist=[]
    for p in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu"]:
        if p in pos:
            deg=pos[p]["deg"]
            if p=="Rahu": deg=30-deg  # Rahu uses reverse degree
            plist.append((p,deg))
    plist.sort(key=lambda x:-x[1])
    roles=["Atmakaraka (AK)","Amatyakaraka (AmK)","Bhratrukaraka (BK)",
           "Matrukaraka (MK)","Putrakaraka (PK)","Gnatikaraka (GK)","Darakaraka (DK)"]
    return [(roles[i],plist[i][0],plist[i][1]) for i in range(min(len(roles),len(plist)))]


def to_para(text,style):
    if not text: return Paragraph("",style)
    t=str(text)
    # Render the entities the report uses as REAL glyphs before escaping bare
    # "&" — otherwise the escape turns them into literal "&nbsp;"/"&bull;" text
    # that was printing on every page (client flagged it 2026-06-15).
    t=t.replace("&nbsp;"," ").replace("&bull;","•")
    t=t.replace("&amp;","&AMP;").replace("&","&amp;").replace("&AMP;","&amp;")
    t=t.replace("\n","<br/>")
    return Paragraph(t,style)


explain_style=ParagraphStyle("explain",fontSize=10,alignment=TA_JUSTIFY,
    textColor=GREY_DK,fontName="Helvetica",leading=15,spaceAfter=0)

def explainer(story,label="WHAT THIS MEANS"):
    """Plain-language 'story' callout — gold-accented box that makes a technical
    section client-readable (client revision 2026-06-15)."""
    s=str(story).replace("&amp;","&AMP;").replace("&","&amp;").replace("&AMP;","&amp;")
    cell=[Paragraph(f"<font color='{hexstr(GOLD_DK)}' size='8'><b>{label}</b></font>",body_small),
          Paragraph(s,explain_style)]
    t=Table([[cell]],colWidths=[A4[0]-5*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),CREAM_2),
        ("LINEBEFORE",(0,0),(0,-1),3,GOLD),
        ("BOX",(0,0),(-1,-1),0.5,GOLD_LT),
        ("LEFTPADDING",(0,0),(-1,-1),12),("RIGHTPADDING",(0,0),(-1,-1),12),
        ("TOPPADDING",(0,0),(-1,-1),9),("BOTTOMPADDING",(0,0),(-1,-1),9),
        ("VALIGN",(0,0),(-1,-1),"TOP")]))
    return [t,Spacer(1,0.35*cm)]


# ─── 23 DOMAIN PREDICTIONS ─────────────────────────────
def all_predictions(chart):
    """All domain predictions — prediction text only, no astrological technical terms shown to user."""
    pos=chart["positions"]
    lagna_idx=chart["lagna_idx"]
    moon=pos["Moon"]
    pred={}
    mds,_,_,_=vimshottari(chart)

    def lord_of(house):
        sign=RASIS[(lagna_idx+house-1)%12]
        return RASI_LORDS[sign]

    def occupants(house):
        return [p for p,pd in pos.items() if pd["house"]==house]

    def lord_house(house):
        l=lord_of(house)
        return pos[l]["house"] if l in pos else None

    # ── 1. SELF & PERSONALITY ──
    nak=chart["janma_nakshatra"]
    ak_planet=chara_karakas(chart)[0][1]
    sun_dig=DIGNITIES.get(("Sun",pos["Sun"]["rasi"]),"neutral")
    merc_dig=DIGNITIES.get(("Mercury",pos["Mercury"]["rasi"]),"neutral")
    sat_dig=DIGNITIES.get(("Saturn",pos["Saturn"]["rasi"]),"neutral")
    jup_dig=DIGNITIES.get(("Jupiter",pos["Jupiter"]["rasi"]),"neutral")
    LAGNA_BODY={
        "Aries":"medium build, athletic, sharp features, scar or mark on the head; impulsive walk",
        "Taurus":"thick-set, strong neck, attractive face, slow and steady gait",
        "Gemini":"tall thin frame, expressive hands, animated speech, restless",
        "Cancer":"round face, fair complexion, soft body, emotional eyes",
        "Leo":"tall, broad shoulders, kingly posture, magnetic presence",
        "Virgo":"medium height, slender, refined features, careful walk",
        "Libra":"well-proportioned, attractive, graceful, charming smile",
        "Scorpio":"medium-strong build, intense eyes, secretive expression",
        "Sagittarius":"tall, broad and generous build, jovial face, philosophical look",
        "Capricorn":"thin frame, prominent bones, serious expression, slow walk",
        "Aquarius":"tall thin frame, unusual features, distinctive look",
        "Pisces":"medium, soft body, dreamy eyes, gentle expression",
    }
    pred["self"]=[
        f"<b>Physical appearance</b> — {LAGNA_BODY.get(chart['lagna'],'')}. "
        f"The body carries this signature throughout life — in build, in gait, and in first impression.",

        f"<b>Core personality</b> — {NAKSHATRA_PERSONALITY.get(nak,'')}. "
        f"This is the deepest personality layer — the part that never changes regardless of circumstances or age.",

        f"<b>Mind and thinking style</b> — " + (
        "You think rapidly and analytically. Strong at reasoning, facts, and logical argument. Arguments and analysis come naturally."
        if merc_dig in ["Own","Exalted","Exalted/Own"] else
        "You are intuitive and experiential — you learn best through doing and feeling, not through books or theory alone."
        if merc_dig=="Debil" else
        "Your mind is balanced — you move comfortably between feeling and analysis depending on the situation."),

        f"<b>Emotional nature</b> — " + (
        "Passionate and expressive — emotions run hot, enthusiasm ignites quickly, and you bring fire to everything you care about."
        if moon["rasi"] in ["Aries","Leo","Sagittarius"] else
        "Steady and practical — emotions run deep but are rarely displayed. You need stability and dislike sudden change."
        if moon["rasi"] in ["Taurus","Virgo","Capricorn"] else
        "Curious and social — you process emotions through communication and connection. Boredom is your true enemy."
        if moon["rasi"] in ["Gemini","Libra","Aquarius"] else
        "Deeply sensitive and intuitive — you feel everything intensely. Your emotional world is rich but sometimes overwhelming."),

        f"<b>Soul's core purpose</b> — Your life revolves around the themes of {PLANET_ARCHETYPES.get(ak_planet,'')}. "
        f"Every major experience — whether lucky or painful — is nudging you toward mastery in this domain.",

        f"<b>Discipline and wisdom</b> — " + (
        "You have a naturally disciplined character — structure and hard work come built-in. You are the person others rely on for consistency."
        if sat_dig in ["Own","Exalted"] else
        "Discipline is your life's greatest teacher — you will be tested repeatedly in this area, and each test builds character."
        if sat_dig=="Debil" else
        "Your sense of discipline is moderate — functional but not exceptional.") + " " + (
        "Your moral compass is strong — a natural ethical sense that guides decisions even under pressure."
        if jup_dig in ["Own","Exalted"] else
        "Developing wisdom and ethical clarity is an ongoing process — lessons come through experience rather than being inborn."
        if jup_dig=="Debil" else
        "Wisdom and good judgment are available to you when genuinely sought."),

        f"<b>How you communicate</b> — " + (
        "Eloquent, polished, and persuasive — words are your tool. People listen when you speak."
        if lord_of(2) in ["Mercury","Venus","Jupiter"] else
        "Direct and frank — you say what you mean without decoration, which people either love or find too blunt."
        if lord_of(2) in ["Mars","Sun"] else
        "Measured and careful — you think before you speak, and when you do, it carries weight."),

        f"<b>Learning and intellect</b> — " + (
        "You learn fastest through reading, research, and analytical breakdown. Academic environments suit you well."
        if pos["Mercury"]["rasi"] in ["Gemini","Virgo"] else
        "You learn through emotion, intuition, and lived experience. Facts alone do not move you — stories and meaning do."
        if pos["Mercury"]["rasi"] in ["Cancer","Scorpio","Pisces"] else
        "You learn through observation and hands-on practice. You need to see things in action."),

        f"<b>Self-confidence</b> — " + (
        "Natural, healthy self-confidence — comfortable with authority and leadership without being arrogant."
        if sun_dig in ["Own","Exalted"] else
        "Your confidence comes and goes — you sometimes undersell yourself. Learning to claim your authority fully is a key life task."
        if sun_dig=="Debil" else
        "Your sense of self is balanced — confident enough to lead when needed, humble enough to follow."),

        f"<b>Will power and action</b> — " + (
        "Strong decisive will — you act first and adjust later. Hesitation is rare; momentum is your natural state."
        if pos["Mars"]["house"] in [1,3,6,10,11] else
        "Reflective will — you plan carefully before acting. Not impulsive, but deliberate and strategic when you move."),

        f"<b>Memory and retention</b> — " + (
        "Sharp, retentive memory — you hold onto details, faces, conversations, and facts with ease. People are often surprised by what you recall."
        if abs(pos["Mercury"]["rasi_idx"]-pos["Moon"]["rasi_idx"])<=2 else
        "Selective emotional memory — you remember deeply what matters to your heart, but routine details pass through."),
    ]

    # ── 2. PARENTS ──
    h9_occ=occupants(9); h9_lord=lord_of(9); h9_lord_h=lord_house(9)
    h4_occ=occupants(4); h4_lord=lord_of(4); h4_lord_h=lord_house(4)
    sun_h=pos["Sun"]["house"]; sun_dig=DIGNITIES.get(("Sun",pos["Sun"]["rasi"]),"neutral")
    moon_h=pos["Moon"]["house"]; moon_dig=DIGNITIES.get(("Moon",moon["rasi"]),"neutral")
    pred["parents"]=[
        f"<b>Father's overall life</b> — " + (
        "Your father had a strong, commanding presence — likely involved in authority, government, or leadership-type work. He carried himself with dignity and was respected in his field or community."
        if sun_dig in ["Own","Exalted","Exalted/Own"] else
        "Your father faced significant challenges in health, career, or personal life. There may have been periods of illness or difficulty that tested him. His journey had a teaching quality for you."
        if sun_dig=="Debil" else
        "Your father was a stable, hardworking figure — not highly dramatic, but consistent and reliable. His influence on your life came more through example than through wealth or power."),

        f"<b>Father's health and longevity</b> — " + (
        "Your father is likely to enjoy good health and long life — his vitality is well-supported."
        if sun_dig in ["Own","Exalted","Exalted/Own"] else
        "Your father's health is an area of concern — illnesses, chronic issues, or a shorter life are possibilities to be aware of. Extra care and timely medical attention are advised."
        if sun_dig=="Debil" else
        "Your father's health follows normal cycles — not exceptional worry, but regular monitoring is wise.") + " " + (
        "The broader indicators reinforce a stable life journey for him."
        if h9_lord_h in [1,4,5,7,9,10,11] else
        "Some periods in his life bring significant tests or disruptions — the chart shows this as part of his journey."),

        f"<b>Father's profession and status</b> — " + (
        "Your father is naturally drawn to authority, leadership, or government service. He carries himself as someone in charge, and others recognise that naturally."
        if sun_h in [1,10] else
        "Your father's career was tied to social connections, partnerships, or trade. He dealt with the public or worked in a people-facing role."
        if sun_h in [7,11] else
        "Your father's work involved communication, teaching, or creative expression — he may have been a writer, teacher, or skilled specialist."
        if sun_h in [3,5] else
        "Your father's career had its challenges — possibly self-made through difficult circumstances."
        if sun_h in [6,8,12] else
        "Your father had a well-balanced career path — steady rather than spectacular, building over time."),

        f"<b>Mother's overall life</b> — " + (
        "Your mother has a powerful nurturing energy — likely a devoted, loving, and deeply present mother who shaped your emotional world profoundly. Her influence on you is immense and long-lasting."
        if moon_dig in ["Own","Exalted","Exalted/Own"] else
        "Your relationship with your mother carries complexity — there may have been emotional distance, separation, or a difficult beginning. The bond, while present, had to be worked for on both sides."
        if moon_dig=="Debil" else
        "Your mother was a balanced, supportive presence — warm and caring without being overwhelming. A quiet strength behind the scenes of your life."),

        f"<b>Bond with your mother</b> — " + (
        "Deep and lifelong emotional bond with your mother. She is your emotional anchor and safe harbour. Her guidance shaped your inner world more than almost anything else."
        if moon_h in [1,4,5,9] else
        "Your mother's influence is strongest in your public life and social success — she may have pushed you toward achievement and visibility."
        if moon_h in [10,11] else
        "The mother relationship has a karmic, transformative quality — lessons in letting go, growth through separation, or a spiritual dimension to the bond."
        if moon_h in [6,8,12] else
        "Warm and reliable mother bond — present when needed, giving space when appropriate."),

        f"<b>Father-child relationship</b> — " + (
        "Your father was a strong authority figure — respected but possibly experienced as distant or commanding. The relationship held high expectations."
        if sun_h in [1,4,7,10] else
        "Your father and you had a warm connection built around learning, travel, or shared philosophies. He was more a friend or guide than a stern authority."
        if sun_h in [3,5,9,11] else
        "The father relationship carried its challenges — distance, illness, absence, or difficult circumstances. Yet these experiences shaped your independence."),

        f"<b>Parental bond comparison</b> — " + (
        "You were clearly closer to your mother — she was the emotional centre of home life while your father was more peripheral or demanding."
        if moon_h in [1,4] and sun_h in [6,8,12] else
        "Both parents were significant but in different ways — your father shaped your outer ambition while your mother shaped your inner world."
        if sun_h in [1,10] and moon_h in [4,9] else
        "Both parental bonds were present and functional — a relatively stable home environment overall."),

        f"<b>Inheritance from parents</b> — " + (
        "Strong indicators of inheritance — family property, ancestral wealth, or meaningful financial legacy from one or both parents."
        if h4_lord_h in [2,11] or h9_lord_h in [2,11] else
        "Inheritance is modest — wealth in your life will largely be self-built rather than received from the family."),

        f"<b>Parental influence across life</b> — "
        f"Parental influence is strongest during the early years and resurfaces during periods of major transition. "
        f"Watch especially for health events in the parents during the dasha periods of the lords of the 4th and 9th houses.",
    ]

    # ── 3. SIBLINGS ──
    h3_occ=occupants(3); h3_lord=lord_of(3); h3_lord_h=lord_house(3)
    h11_occ=occupants(11); h11_lord=lord_of(11); h11_lord_h=lord_house(11)
    mars_h=pos["Mars"]["house"]; mars_dig=DIGNITIES.get(("Mars",pos["Mars"]["rasi"]),"neutral")
    pred["siblings"]=[
        f"<b>Siblings overview</b> — " + (
        "You are likely to have active sibling dynamics — at least one sibling who plays a notable role in your life."
        if h3_occ or h11_occ else
        "You may be an only child, or if siblings exist they play a less central role in your life journey."),

        f"<b>Relationship quality with siblings</b> — " + (
        "Strong, supportive, and protective sibling relationships. You have each other's backs. The bond may be tested but ultimately holds firm."
        if mars_dig in ["Own","Exalted","Exalted/Own"] else
        "Sibling dynamics carry friction, competition, or periods of estrangement. Communication and deliberate effort are needed to maintain bonds."
        if mars_dig=="Debil" else
        "Balanced sibling relationships — neither overly close nor distant. You support each other when it matters."),

        f"<b>Younger siblings' life path</b> — "
        f"Your younger sibling(s) tend toward careers or life paths involving " + (
        "wealth, family, or communication." if h3_lord_h in [2,3] else
        "home, creativity, or stability." if h3_lord_h in [4,5] else
        "partnership, foreign work, or transformation." if h3_lord_h in [7,8,12] else
        "career, public recognition, or social achievement." if h3_lord_h in [10,11] else
        "challenges that build character.") +
        " Their success and yours are often interlinked.",

        f"<b>Elder siblings' role in your life</b> — " + (
        "Elder siblings or cousins are sources of gain, support, and friendship for you — they open doors or provide encouragement at key moments."
        if h11_lord_h in [1,2,5,11] else
        "Elder siblings follow a largely independent path — you respect each other but live separate lives."
        if h11_lord_h in [6,8,12] else
        "Elder siblings are present in the background — helpful occasionally but not a primary source of support."),

        f"<b>Your own courage and initiative</b> — " + (
        "Bold and action-oriented — you confront challenges head-on, are not easily intimidated, and have natural leadership energy."
        if mars_h in [1,3,6,10] else
        "Thoughtful and measured — you plan before you act. Your strength lies in strategy, not brute force."
        if mars_h in [4,7] else
        "Courage is built through experience rather than innate — you grow bolder as you mature and accumulate wins."),

        f"<b>Sibling wellbeing</b> — " + (
        "The chart shows no major red flags for sibling health or longevity — overall positive trajectory."
        if mars_dig not in ["Debil"] and mars_h not in [6,8,12] else
        "There may be health concerns for a sibling at some point in life — worth ensuring regular contact and care."),

        f"<b>When sibling themes peak</b> — "
        f"Sibling-related events — their marriages, career shifts, migrations, or health events — "
        f"come into strong focus during the active dasha periods tied to the 3rd and 11th houses. "
        f"These are natural times for sibling bonding or resolution of old tensions.",
    ]

    # ── 4. EDUCATION ──
    h5_occ=occupants(5); h5_lord=lord_of(5); h5_lord_h=lord_house(5)
    merc_h=pos["Mercury"]["house"]; merc_dig=DIGNITIES.get(("Mercury",pos["Mercury"]["rasi"]),"neutral")
    jup_h=pos["Jupiter"]["house"]; jup_dig=DIGNITIES.get(("Jupiter",pos["Jupiter"]["rasi"]),"neutral")
    rahu_h=pos["Rahu"]["house"]
    pred["education"]=[
        f"<b>Early schooling experience</b> — " + (
        "Smooth, supported school years — good environment, helpful teachers, and steady academic progress."
        if h4_lord_h in [1,4,5,9,10,11] else
        "Early schooling had disruptions — multiple schools, difficult peers, or an environment that wasn't ideal. You had to work harder than others."
        if h4_lord_h in [6,8,12] else
        "Ordinary school experience — neither exceptionally good nor particularly difficult."),

        f"<b>Learning ability and style</b> — " + (
        "Rapid, analytical mind — you excelled in subjects requiring precision and logical reasoning. Mathematics, science, and structured argument are natural strengths."
        if merc_dig in ["Own","Exalted","Exalted/Own"] else
        "Intuitive, experiential learner — you grasped subjects you cared about deeply while struggling with rote memorisation. You think in concepts and patterns, not facts."
        if merc_dig=="Debil" else
        "Balanced learning capacity — you adapt to different subjects and handle both analytical and creative tasks."),

        f"<b>Higher education</b> — " + (
        "Strong higher education indicators — you likely completed a degree or advanced qualification, possibly with distinction. Academic achievement was a real chapter in your story."
        if h9_lord_h in [1,5,9,10,11] else
        "Higher education faced obstacles — financial, motivational, or circumstantial. You may have taken a non-linear path, or substituted experience for formal degrees."
        if h9_lord_h in [6,8,12] else
        "Moderate higher education journey — you completed what was needed, though not the most glamorous academic experience."),

        f"<b>Subjects and specialisation</b> — " + (
        "Technical, scientific, or mathematical fields are your strongest domains. Engineering, computers, finance, law — anything requiring systematic thinking."
        if pos["Mercury"]["rasi"] in ["Gemini","Virgo"] else
        "Humanities, arts, psychology, or spiritual subjects draw you — you understand people, meaning, and beauty better than algorithms."
        if pos["Mercury"]["rasi"] in ["Cancer","Scorpio","Pisces"] else
        "Practical, applied fields — business, administration, or trades where you can learn and produce simultaneously."),

        f"<b>Foreign education or study abroad</b> — " + (
        "Strong possibility of studying abroad or through foreign-origin institutions and knowledge systems."
        if rahu_h in [9,12] or h9_lord_h in [12] else
        "Education is primarily domestic — foreign study may have been considered but not the primary path."),

        f"<b>Lifelong learning</b> — " + (
        "Your love of learning does not stop with formal education — you are a natural lifelong student. Books, courses, mentors, and new ideas feed your mind well into later decades."
        if jup_dig in ["Own","Exalted"] or jup_h in [1,5,9] else
        "Formal education may have ended early — further learning comes through work and experience rather than structured programmes."),

        f"<b>Creative and artistic education</b> — " + (
        "Strong aptitude for arts, music, or creative pursuits — these could have been developed through education or were self-taught."
        if h5_occ and any(p in h5_occ for p in ["Venus","Moon","Mercury"]) else
        "Technical or intellectual tracks dominated education — arts were a side interest rather than a central pursuit."),

        f"<b>Peak academic years</b> — "
        f"Academic success peaks during Mercury and Jupiter dasha periods — the natural education engines of the chart. "
        f"Results in formal examinations, certifications, or competitive selections tend to come in these windows.",
    ]

    # ── 5. MARRIAGE ──
    h7_occ=occupants(7); h7_lord=lord_of(7); h7_lord_h=lord_house(7)
    ven_h=pos["Venus"]["house"]; ven_dig=DIGNITIES.get(("Venus",pos["Venus"]["rasi"]),"neutral")
    is_manglik=pos["Mars"]["house"] in [1,2,4,7,8,12]
    now_m=dt.datetime.now()
    marriage_windows=[]
    for md in mds:
        if md["lord"] in ["Venus","Jupiter","Moon"] and md["end"]>now_m:
            is_active=md["start"]<=now_m<=md["end"]
            marriage_windows.append((md["lord"],md["start"].strftime("%b %Y"),md["end"].strftime("%b %Y"),is_active))
    SPOUSE_SIGN_NATURE={
        "Aries":"energetic, independent, pioneering, sometimes impatient",
        "Taurus":"steady, sensual, loyal, comfort-loving, stubborn at times",
        "Gemini":"witty, communicative, social, changeable",
        "Cancer":"nurturing, emotional, home-loving, protective",
        "Leo":"charismatic, proud, generous, dramatic",
        "Virgo":"analytical, service-oriented, health-conscious, sometimes critical",
        "Libra":"charming, diplomatic, artistic, balance-seeking",
        "Scorpio":"intense, loyal, secretive, transformative",
        "Sagittarius":"philosophical, adventurous, freedom-loving, direct",
        "Capricorn":"ambitious, disciplined, career-focused, reserved",
        "Aquarius":"independent, unconventional, humanitarian, intellectual",
        "Pisces":"empathetic, spiritual, creative, sensitive",
    }
    h7_sign=RASIS[(lagna_idx+6)%12]
    spouse_nature=SPOUSE_SIGN_NATURE.get(h7_sign,"balanced and adaptable")
    pred["marriage"]=[
        f"<b>Marriage timing</b> — " + (
        "The chart supports marriage in the mid-to-late 20s or early 30s — a natural window within favourable planetary periods."
        if ven_h in [1,2,5,7,11] else
        "Marriage may come slightly later than peers — the chart suggests taking time to develop individually before the right partner arrives."
        if ven_h in [6,8,12] else
        "Marriage timing is average — within the normal window for your social context.") + (
        " The current period is an active marriage window." if any(w[3] for w in marriage_windows) else ""),

        f"<b>Upcoming marriage windows</b> — " + (
        "; ".join(f"{w[0]} period {w[1]}–{w[2]}" + (" ★ NOW" if w[3] else "") for w in marriage_windows[:3])
        if marriage_windows else
        "Major Venus/Jupiter/Moon periods have mostly passed — marriage is still possible through Antar Dasha activations."),

        f"<b>Spouse personality</b> — Your partner is likely to be {spouse_nature}. "
        f"The 7th house sign gives the primary personality template of the life partner.",

        f"<b>Spouse background and appearance</b> — " + (
        "Your spouse is likely to be attractive, charming, and artistic — someone who draws attention naturally."
        if ven_dig in ["Own","Exalted","Exalted/Own"] else
        "Your spouse may come from a challenging background or carry their own life burdens — this becomes a shared journey of growth."
        if ven_dig=="Debil" else
        "Your spouse is likely pleasant and balanced — a reliable life companion.") + (
        " They may come from a different region, culture, or background than your own family." if h7_lord_h in [9,12] else ""),

        f"<b>Marriage quality and happiness</b> — " + (
        "A harmonious, long-lasting marriage is strongly indicated — the chart supports a loving and supportive partnership."
        if ven_dig in ["Own","Exalted","Exalted/Own"] and h7_lord_h in [1,2,4,5,7,9,10,11] else
        "Marriage goes through real challenges — possibly financial strain, communication difficulties, or differences in values. Success requires conscious effort from both sides."
        if ven_dig=="Debil" or h7_lord_h in [6,8,12] else
        "Marriage is stable and functional — a reliable partnership built on mutual respect."),

        f"<b>Mars and marriage intensity</b> — " + (
        "Mars influences the marriage zone — intensity, passion, and directness define the partnership dynamic. A partner who can match your energy is essential."
        if is_manglik else
        "No Mars intensity influence on the marriage house — partnership energies are more harmonious by default."),

        f"<b>Possibility of second relationship</b> — " + (
        "The chart suggests the possibility of a second significant relationship in life — either a second marriage or a major committed partnership after the first."
        if h7_lord_h in [8,12] or (h7_occ and any(p in h7_occ for p in ["Saturn","Rahu"])) else
        "The chart indicates one primary, lasting marriage — serial relationships are not the chart's pattern."),

        f"<b>Spouse's career</b> — " + (
        "Your spouse is likely to have an independent career or business — a professionally active and ambitious partner."
        if h7_lord_h in [3,6,10,11] else
        "Your spouse may be in a creative, healing, or service-oriented field — teacher, doctor, artist, or social worker type."
        if h7_lord_h in [4,5,9] else
        "Your spouse's career follows a conventional or family-supported path."),
    ]

    # ── 6. CHILDREN ──
    h5_occ=occupants(5); h5_lord=lord_of(5); h5_lord_h=lord_house(5)
    jup_h=pos["Jupiter"]["house"]; jup_dig=DIGNITIES.get(("Jupiter",pos["Jupiter"]["rasi"]),"neutral")
    pred["children"]=[
        f"<b>Children — likelihood and ease</b> — " + (
        "Strong, easy conception indicators — children come naturally and early in marriage. Fertility is not a concern in this chart."
        if jup_dig in ["Own","Exalted"] and h5_lord_h in [1,5,9,11] else
        "Conception may require some patience — the chart suggests delayed children or possible need for medical support. This does not mean no children — the journey may take longer."
        if jup_dig=="Debil" or h5_lord_h in [6,8,12] else
        "Children arrive in normal course — no exceptional ease or difficulty indicated."),

        f"<b>Number of children</b> — " + (
        "The chart suggests 2–3 children are well-supported."
        if not h5_occ or jup_h in [1,5,9,11] else
        "One or two children is the natural indication — quality of the parent-child bond matters more than quantity."),

        f"<b>Children's character</b> — " + (
        "Children are likely to be intelligent, academically gifted, or artistic — they will make the family proud through achievements."
        if any(p in h5_occ for p in ["Jupiter","Mercury","Venus","Moon"]) else
        "Children will be energetic and strong-willed — their path requires a firm but loving guiding hand."
        if any(p in h5_occ for p in ["Mars","Sun"]) else
        "Children follow a straightforward, steady path — solid contributors to the family."),

        f"<b>Timing of first child</b> — " + (
        "First child typically arrives within 1–3 years of marriage, in a Jupiter or Venus sub-period."
        if jup_dig in ["Own","Exalted"] else
        "First child may come after age 30 or after a waiting period — the chart suggests the right time is when life circumstances are stable."
        if h5_lord_h in [6,8,12] or jup_dig=="Debil" else
        "First child comes in normal timing — within the first few years of marriage, in a favourable dasha."),

        f"<b>Parent-child bond</b> — " + (
        "Deep, devoted, and fulfilling parent-child relationship — children bring profound joy and are a central life theme. You are made to be a parent."
        if jup_dig in ["Own","Exalted"] or h5_lord_h in [1,4,5,9] else
        "The parent-child relationship, while loving, may carry challenges — children might be demanding or need extra support. The bond grows through these trials."
        if h5_lord_h in [6,8,12] else
        "A warm, balanced parent-child dynamic — you provide structure and love in equal measure."),

        f"<b>Children's success</b> — " + (
        "Children are likely to find success in their careers and social standing — they bring honour to the family name."
        if h5_lord_h in [9,10,11] else
        "Children may face their own life challenges — their path requires more patience from you. The reward comes later."
        if h5_lord_h in [6,8,12] else
        "Children's success is steady and self-built — not dramatic, but solid."),

        f"<b>Spiritual connection through children</b> — "
        f"Children serve as a spiritual mirror and karmic teacher — your deepest growth as a person comes through the experience of parenthood. "
        f"This is a marked theme in the chart.",
    ]

    # ── 7. CAREER & PROFESSION ──
    h10_occ=occupants(10); h10_lord=lord_of(10); h10_lord_h=lord_house(10)
    h6_lord=lord_of(6); h6_lord_h=lord_house(6)
    karakas_list=chara_karakas(chart)
    karaka_amk=karakas_list[1][1] if len(karakas_list)>1 else "Mercury"
    CAREER_BY_PLANET={
        "Sun":"government, administration, politics, leadership, medicine",
        "Moon":"public service, hospitality, nursing, import-export, real estate",
        "Mars":"engineering, military, police, surgery, real estate, sports",
        "Mercury":"IT, finance, accounting, writing, teaching, commerce, consulting",
        "Jupiter":"education, law, banking, religion, advisory roles",
        "Venus":"arts, fashion, entertainment, luxury goods, design, hospitality",
        "Saturn":"mining, agriculture, construction, labour management, research",
        "Rahu":"technology, foreign companies, unconventional fields, media",
        "Ketu":"research, spirituality, medicine, mystical arts",
    }
    pred["career"]=[
        f"<b>Natural career domain</b> — Your strongest professional fields are: "
        f"{CAREER_BY_PLANET.get(h10_lord,'general management and leadership')}. "
        f"These are the arenas where your natural talents and chart energy converge.",

        f"<b>Soul's career calling</b> — Beyond the practical field, your deeper professional calling involves "
        f"{CAREER_BY_PLANET.get(karaka_amk,'advisory and wisdom-sharing roles')}. "
        f"This is what gives your work meaning beyond the paycheck.",

        f"<b>Job vs. business</b> — " + (
        "You are built for independent work — entrepreneurship, consulting, or leadership. A salaried routine constrains you. Business or a senior position with autonomy is where you thrive."
        if h10_lord_h in [1,3,7,10] else
        "You perform best in an established organisational structure — a career with seniority, team support, and a clear growth ladder suits you more than starting from scratch."
        if h10_lord_h in [4,5,9] else
        "You can succeed in either — the path that fits your life phase is the right one."),

        f"<b>Career trajectory</b> — " + (
        "Strong upward career trajectory — promotions, recognition, and increasing authority are well-marked. The career builds in visible steps."
        if h10_lord_h in [1,4,9,10,11] else
        "Career has a non-linear path — setbacks and rebuilds are part of the story. The eventual position is often better than what the early years suggested."
        if h10_lord_h in [6,8,12] else
        "Steady, moderate career growth — consistent advancement without dramatic highs or lows."),

        f"<b>Government vs. private sector</b> — " + (
        "Strong government or public sector alignment — stability, authority, and public trust are your career environment."
        if h10_lord in ["Sun","Saturn","Jupiter"] else
        "Private sector, business, or entrepreneurship is the natural domain — you flourish outside bureaucratic structures."
        if h10_lord in ["Mercury","Venus","Rahu"] else
        "You can function in either — the sector matters less than the role and autonomy within it."),

        f"<b>Career peak years</b> — "
        f"Career peaks typically come during the Maha Dasha or Antar Dasha of the 10th lord. "
        f"These are the years when the professional story accelerates — promotions, launches, public recognition, or major role changes.",

        f"<b>Foreign career opportunities</b> — " + (
        "Strong foreign career component — working abroad, for foreign companies, or in internationally-oriented roles is a marked possibility."
        if pos["Rahu"]["house"] in [9,10,12] or h10_lord_h in [12] else
        "Career is primarily domestic — international work is supplemental to the main professional story."),

        f"<b>Authority and leadership</b> — " + (
        "Natural leadership capacity — people follow you without being asked. Management and leadership roles come because others recognise your capacity."
        if h10_lord in ["Sun","Jupiter","Mars"] or h10_lord_h in [1,4,10] else
        "Leadership grows through expertise — you earn authority through knowledge and track record rather than through born charisma."),

        f"<b>Career in later life</b> — " + (
        "Later career years (post-45) bring the greatest recognition. The early years build the foundation; the second half delivers the rewards."
        if jup_dig in ["Own","Exalted"] else
        "Career activity may gradually reduce in later years — a natural pull toward quieter work or semi-retirement. A healthy transition."),
    ]

    # ── 8. WEALTH ──
    h2_occ=occupants(2); h2_lord=lord_of(2); h2_lord_h=lord_house(2)
    h11_lord=lord_of(11); h11_lord_h=lord_house(11)
    ven_dig=DIGNITIES.get(("Venus",pos["Venus"]["rasi"]),"neutral")
    pred["wealth"]=[
        f"<b>Wealth potential overall</b> — " + (
        "High wealth potential — the chart supports significant financial accumulation. Multiple income sources are indicated."
        if jup_dig in ["Own","Exalted"] and h2_lord_h in [1,2,5,9,10,11] else
        "Wealth requires sustained effort — the chart shows financial challenges that must be overcome through discipline and conservative investment. Avoid speculation."
        if jup_dig=="Debil" else
        "Moderate wealth — you will build a comfortable life but significant riches require deliberate effort and smart financial decisions."),

        f"<b>Primary income source</b> — " + (
        "Career and profession is the primary wealth engine — steady, structured income that grows with seniority and expertise."
        if h2_lord_h in [6,10] else
        "Business and self-generated income is the primary wealth path — entrepreneurial activity, trading, or consulting."
        if h2_lord_h in [3,7] else
        "Wealth comes through multiple streams — property, investments, family money, and career income all contribute."
        if h2_lord_h in [2,11] else
        "Income is tied to partnerships, foreign work, or unconventional sources."),

        f"<b>Inheritance and family wealth</b> — " + (
        "Meaningful family inheritance — either in money, property, or valuable assets that come to you in due course."
        if h2_lord_h in [2,4,9] else
        "Wealth is primarily self-built — what the family provides is support and values, not money."),

        f"<b>Peak wealth years</b> — "
        f"Wealth peaks are most prominent during Venus, Jupiter, and the 2nd/11th house lord periods in the Vimshottari sequence. "
        f"Invest during these periods rather than spending excessively.",

        f"<b>Debt and financial risk</b> — " + (
        "Low debt risk — you are naturally inclined toward financial prudence."
        if h2_lord_h not in [6,8,12] and sat_dig not in ["Debil"] else
        "Debt is a real risk — possible financial overextension or loans that become burdens. Conservative financial planning is essential. Avoid co-signing for others."),

        f"<b>Best investments</b> — " + (
        "Property, gold, and traditional investments are your strongest wealth-builders. Real estate especially is well-indicated."
        if pos["Mars"]["house"] in [1,4,10] or pos["Saturn"]["house"] in [4,10] else
        "Stocks, business equity, or knowledge-based investments are better for you than physical assets alone."),

        f"<b>Financial life in later years</b> — " + (
        "Comfortable and secure financial life in later years — the chart supports building enough to live well without financial anxiety in old age."
        if jup_dig in ["Own","Exalted"] or h11_lord_h in [1,2,9,11] else
        "Later financial years require pre-planning — creating a pension, investment corpus, or property that yields income is essential. Don't leave this to chance."),

        f"<b>Overall wealth verdict</b> — " + (
        "A wealth-building chart — a financially comfortable and eventually prosperous life through sustained, disciplined effort."
        if jup_h in [1,4,5,7,9,11] else
        "Wealth comes but not without effort and some setbacks. Those who plan carefully do well."),
    ]

    # ── 9. HEALTH ──
    h6_occ=occupants(6); h8_occ=occupants(8); h8_lord=lord_of(8)
    asc_lord=chart.get("lagna_lord","Jupiter")
    asc_lord_dig=DIGNITIES.get((asc_lord,pos[asc_lord]["rasi"]),"neutral") if asc_lord in pos else "neutral"
    pred["health"]=[
        f"<b>Overall constitution</b> — " + (
        "Robust health constitution — natural resistance to illness, good immunity, and generally high energy. You bounce back from illness faster than most."
        if asc_lord_dig in ["Own","Exalted","Exalted/Own"] else
        "Sensitive health constitution — more susceptible to environmental, emotional, and dietary triggers. Your body requires careful maintenance."
        if asc_lord_dig=="Debil" else
        "Average constitution — neither unusually strong nor fragile. Health responds well to standard care and regular habits."),

        f"<b>Body's vulnerable zones</b> — "
        f"The most common health challenges are tied to " + (
        "digestion, stomach, and emotional or stress-linked conditions."
        if chart["lagna"] in ["Cancer","Virgo"] else
        "joints, bones, skin, and chronic conditions."
        if chart["lagna"] in ["Capricorn","Aquarius"] else
        "head, blood pressure, and heat-related conditions."
        if chart["lagna"] in ["Aries","Leo","Scorpio"] else
        "lungs, throat, and respiratory issues."
        if chart["lagna"] in ["Taurus","Gemini","Libra"] else
        "liver, thighs, and excess-related conditions."),

        f"<b>Mental health and emotional balance</b> — " + (
        "Strong psychological resilience — you can handle significant stress without breaking. Mental health is one of your genuine strengths."
        if moon_dig in ["Own","Exalted","Exalted/Own"] else
        "Mental and emotional vulnerability is present — anxiety, overthinking, or mood instability can be recurring challenges. Mindfulness, routine, and social connection are protective factors."
        if moon_dig=="Debil" else
        "Emotionally balanced most of the time, with some sensitivity to stress. Standard self-care keeps you on an even keel."),

        f"<b>Surgery or hospitalisation risk</b> — " + (
        "The chart does not flag major surgery or hospitalisation risk above average — standard medical care is the relevant approach."
        if not h8_occ and pos["Mars"]["house"] not in [6,8,12] else
        "There is some indication of a significant medical event — possibly surgery, hospitalisation, or intensive treatment. This is not permanent; it is a defined period followed by recovery."),

        f"<b>Longevity indicators</b> — " + (
        "Strong longevity indicators — the chart supports a long life with productive years well into old age."
        if asc_lord_dig in ["Own","Exalted"] and jup_dig not in ["Debil"] else
        "Longevity requires conscious health investment — proactive health management is genuinely important."
        if asc_lord_dig=="Debil" else
        "Average to moderate longevity — taking care of the body, especially between ages 35–55, directly influences the later decades."),

        f"<b>Diet and lifestyle recommendations</b> — " + (
        "You thrive on regularity — consistent meal times, adequate sleep, and a structured daily routine protect your health better than any medicine."
        if chart["lagna"] in ["Virgo","Capricorn","Taurus"] else
        "Your health is strongly tied to your emotional state — stress management is non-negotiable. When you are at peace emotionally, the body responds well."
        if chart["lagna"] in ["Cancer","Scorpio","Pisces"] else
        "Physical activity is your health lifeline — the body needs movement and regular exercise to stay in balance. A sedentary lifestyle is your primary health risk."),

        f"<b>Health in peak years (25–45)</b> — " + (
        "Peak working years are generally healthy — the body supports the demands placed on it during this period."
        if asc_lord_dig not in ["Debil"] else
        "Watch health carefully during high-pressure work periods — the body absorbs professional stress and needs deliberate recovery time."),

        f"<b>Ageing and health after 50</b> — " + (
        "Health holds up well into later years with reasonable care."
        if jup_dig in ["Own","Exalted"] else
        "After 50, preventive health focus becomes essential — joints, heart, and digestion are areas to monitor proactively."),
    ]

    # ── 10. TRAVEL & FOREIGN ──
    h12_occ=occupants(12); h12_lord=lord_of(12); h12_lord_h=lord_house(12)
    pred["travel"]=[
        f"<b>Foreign travel pattern</b> — " + (
        "Significant international travel and foreign connection is marked — this is someone whose life story includes meaningful time in foreign lands."
        if rahu_h in [9,12] or h12_lord_h in [1,9,12] else
        "Travel is present but not a defining life theme — domestic or regional movement is more prominent than international."),

        f"<b>Foreign settlement possibility</b> — " + (
        "Genuine possibility of living abroad for an extended period — foreign residence, work, or even permanent settlement in another country is supported by the chart."
        if pos["Rahu"]["house"] in [9,12] and h12_lord_h in [1,4,12] else
        "Foreign settlement is not strongly marked — you may travel significantly but home base remains in the country of origin."),

        f"<b>Career-driven travel</b> — " + (
        "Career and foreign opportunities are linked — professional growth often involves crossing borders, working with international clients, or relocating for work."
        if h10_lord_h in [9,12] or pos["Rahu"]["house"]==10 else
        "Career growth is primarily domestic — international work is supplemental to the main professional story."),

        f"<b>Pilgrimage and spiritual travel</b> — " + (
        "A strong pull toward sacred places, pilgrimage sites, or spiritually significant travel. At least one major pilgrimage or spiritually transformative journey is marked in the chart."
        if h9_lord_h in [9,12] or pos["Jupiter"]["house"] in [9,12] else
        "Religious travel is occasional rather than a defining theme."),

        f"<b>Age of significant foreign travel</b> — "
        f"Foreign travel becomes significant typically in the Rahu or 12th lord Maha Dasha period. "
        f"For many, this corresponds to the late 20s or 30s — a natural expansion phase.",

        f"<b>Travel challenges and returns</b> — " + (
        "Travel is generally smooth and rewarding — journeys open doors rather than creating problems."
        if h12_lord_h not in [6,8] else
        "Some journeys bring complications — visa issues, unexpected delays, or health challenges abroad. Travel with extra preparation and flexibility."),

        f"<b>Connection to foreign cultures</b> — " + (
        "A natural affinity for foreign cultures, languages, and ways of life — you assimilate well in different environments and often feel more at home abroad than expected."
        if pos["Rahu"]["house"] in [1,9,12] else
        "You appreciate foreign exposure but the heart remains rooted — home culture and family ties pull you back consistently."),
    ]

    # ── 11. PROPERTY & ASSETS ──
    h4_occ=occupants(4); h4_lord=lord_of(4); h4_lord_h=lord_house(4)
    pred["property"]=[
        f"<b>Home ownership</b> — " + (
        "Strong property ownership indicators — you are likely to own your home and possibly additional property. Real estate is part of your wealth story."
        if h4_lord_h in [1,2,4,5,9,10,11] and pos["Mars"]["house"] in [1,4,10] else
        "Property ownership comes eventually but may require patience — possibly renting through early and middle years before owning in the 35–45 window."
        if h4_lord_h in [6,8,12] else
        "Standard property journey — ownership comes at the right life stage without exceptional difficulty."),

        f"<b>Ancestral property</b> — " + (
        "Some ancestral property is indicated — either inherited land, home, or family assets that come to you in due course."
        if h4_lord_h in [2,4,9] else
        "Ancestral property is not a major factor — what you own, you build yourself through your own earnings."),

        f"<b>Multiple properties</b> — " + (
        "The chart supports owning more than one property in life — a primary home plus investment property or land is achievable."
        if jup_dig in ["Own","Exalted"] and pos["Mars"]["house"] in [1,4,7,10] else
        "One good home is the chart's realistic indication — multi-property portfolios require deliberate saving and planning."),

        f"<b>Vehicles and luxury assets</b> — " + (
        "Comfortable vehicle ownership — you will drive good vehicles as a natural part of your lifestyle, not just as a necessity."
        if ven_dig in ["Own","Exalted"] else
        "Vehicles are functional tools rather than status symbols — practical choices over luxury."),

        f"<b>Home environment quality</b> — " + (
        "Your home is a place of comfort, beauty, and emotional restoration — you invest in making your living space genuinely pleasant."
        if h4_lord_h in [1,4,5] and ven_dig in ["Own","Exalted"] else
        "Home is functional and adequate — not a luxury priority, but it serves your needs well."),

        f"<b>Property in foreign lands</b> — " + (
        "Some possibility of owning or holding property abroad — through work placement, investment, or foreign residence."
        if pos["Rahu"]["house"] in [4,12] else
        "Property is domestic — no strong indicator of foreign real estate."),

        f"<b>Best timing for property purchase</b> — "
        f"Property acquisition is best attempted during Jupiter, Venus, or Saturn Maha Dasha periods — "
        f"these are the natural asset-building windows in the chart.",
    ]

    # ── 12. SOCIAL STATUS, FAME, POWER ──
    h10_occ=occupants(10); h10_lord=lord_of(10); h10_lord_h=lord_house(10)
    sun_h=pos["Sun"]["house"]
    pred["status"]=[
        f"<b>Fame and public recognition</b> — " + (
        "Genuine fame potential — this chart can achieve widespread recognition, public honour, or significant social standing. The name carries weight."
        if h10_lord_h in [1,9,10,11] and sun_dig in ["Own","Exalted"] else
        "Local or professional recognition is more strongly marked than broad fame — respected in your field or community."
        if h10_lord_h in [1,5,9] else
        "Fame is not the primary chart theme — you build reputation through work rather than through visibility."),

        f"<b>Authority and leadership capacity</b> — " + (
        "Natural authority — people follow you without being asked. Leadership positions arrive because others recognise your capacity."
        if h10_lord in ["Sun","Jupiter","Mars"] or sun_dig in ["Own","Exalted"] else
        "Leadership comes through expertise — you earn respect through proven capability rather than natural charisma."),

        f"<b>Career recognition timing</b> — " + (
        "Recognition tends to come in the 35–50 age range — the career builds for years before the public rewards begin. Early patience is rewarded substantially later."
        if h10_lord_h in [4,8,9] else
        "Recognition can come relatively early — the chart supports visibility even in the 25–35 window if the right opportunities are pursued actively."),

        f"<b>Government honours and awards</b> — " + (
        "Some possibility of formal honours, awards, or government recognition during a peak career period."
        if sun_dig in ["Own","Exalted"] and h10_lord_h in [1,9,10] else
        "Formal awards are not strongly marked — recognition in this chart comes through peer respect and professional reputation."),

        f"<b>Social standing in community</b> — " + (
        "Respected and well-regarded in your social circle and community — people trust your judgment and seek your opinion."
        if jup_dig in ["Own","Exalted"] or h10_lord_h in [1,4,9] else
        "Social standing is average — neither exceptionally prominent nor marginal. You move comfortably in your social environment."),

        f"<b>Online presence and media</b> — " + (
        "The chart supports public visibility in media, online platforms, or content creation — a voice that others listen to."
        if pos["Rahu"]["house"] in [3,10,11] else
        "Media presence is not a natural chart strength — professional accomplishment, not public personality, is the better route to recognition."),

        f"<b>Reputation and character</b> — " + (
        "Low reputation-damage risk — the chart does not indicate major scandals or falls from grace. Character remains intact."
        if h10_lord_h not in [6,8,12] and pos["Saturn"]["house"] not in [1,10] else
        "There is a risk period where reputation faces challenge — maintaining ethical standards during Saturn transit periods is essential."),
    ]

    # ── 13. RELATIONSHIPS & ENEMIES ──
    h7_lord=lord_of(7); h7_lord_h=lord_house(7)
    h6_lord=lord_of(6); h6_lord_h=lord_house(6)
    pred["relationships"]=[
        f"<b>Friendship and social network</b> — " + (
        "Wide, warm, and loyal social network — you attract friends naturally and maintain long-term friendships with ease. Your circle is a genuine source of support and joy."
        if jup_dig in ["Own","Exalted"] or h11_lord_h in [1,2,5,11] else
        "Selective and smaller friendship circle — you prefer a few deep relationships over many shallow ones. Quality matters far more than quantity."
        if h11_lord_h in [6,8,12] else
        "Balanced social life — functional friendships that serve both connection and practical purposes."),

        f"<b>Romantic nature</b> — " + (
        "Romantic and expressive in love — you fall deeply and commit fully. Love is one of life's great themes for you."
        if ven_dig in ["Own","Exalted"] else
        "Cautious in romance — you protect your heart and need trust to be established before opening emotionally. When you do commit, it is wholehearted."
        if ven_dig=="Debil" else
        "Balanced approach to romance — neither impulsively romantic nor emotionally guarded."),

        f"<b>Enemies and opposition</b> — " + (
        "Few significant enemies — you do not invite conflict and your chart does not attract serious opposition."
        if pos["Mars"]["house"] not in [1,7] and h6_lord_h not in [1,7] else
        "You will face real opponents in life — people who actively work against your interests. Navigate opposition strategically rather than emotionally."),

        f"<b>Hidden enemies</b> — " + (
        "Some risk of betrayal or hidden opposition — someone in your inner circle may work against you at some point. Discretion about personal plans is wise."
        if pos["Saturn"]["house"] in [4,7,12] or pos["Rahu"]["house"] in [7,12] else
        "Hidden enemies are not a major chart theme — most opposition you face is visible and manageable."),

        f"<b>Legal disputes</b> — " + (
        "Moderate legal dispute risk — some involvement with legal matters in one chapter of life. Property, business, or family law is the likely domain."
        if h6_lord_h in [1,7,10] else
        "Legal disputes are not a featured life theme — conflicts generally resolve through negotiation rather than formal proceedings."),

        f"<b>Trust and betrayal patterns</b> — " + (
        "Your trust is strong but sometimes misplaced — you see the best in people, which is beautiful but occasionally exploited. Trusting your instincts about character is a key life lesson."
        if moon_dig in ["Own","Exalted"] else
        "You are naturally guarded with trust — it takes time for others to earn your full confidence. This protects you from betrayal but can slow meaningful connections."),

        f"<b>Forgiveness and reconciliation</b> — " + (
        "You have a healthy capacity for forgiveness — broken relationships can often be repaired with you through honest conversation."
        if jup_dig in ["Own","Exalted"] else
        "Old wounds take time to heal with you — forgiveness is a deliberate act that requires real effort. The effort is worth it."),
    ]

    # ── 14. SPIRITUALITY ──
    h9_occ=occupants(9); h9_lord=lord_of(9); h9_lord_h=lord_house(9)
    h12_occ=occupants(12); h12_lord=lord_of(12); h12_lord_h=lord_house(12)
    ketu_h=pos["Ketu"]["house"]
    pred["spirituality"]=[
        f"<b>Spiritual orientation</b> — " + (
        "Deeply spiritual by nature — religion, philosophy, or inner seeking is a genuine life theme. You have a contemplative dimension that runs through everything you do."
        if ketu_h in [1,4,5,8,9,12] or h9_lord_h in [9,12] else
        "Religious participation is conventional and family-tradition oriented — you follow inherited practices with respect but are not driven to deep independent seeking."),

        f"<b>Religious practice style</b> — " + (
        "Ritual, mantra, and structured devotion resonate with you — you connect to the divine through form, discipline, and repetition."
        if chart["lagna"] in ["Taurus","Virgo","Capricorn","Scorpio"] else
        "You connect to the divine through nature, silence, and direct inner experience rather than elaborate ritual."
        if chart["lagna"] in ["Cancer","Pisces","Sagittarius"] else
        "Your spirituality is philosophically oriented — you seek to understand the underlying principles rather than just practise surface rituals."),

        f"<b>Guru and teacher relationship</b> — " + (
        "A significant spiritual teacher or guru figure is part of your life journey — someone who transforms your understanding of existence at a pivotal moment."
        if jup_dig in ["Own","Exalted"] or h9_lord_h in [9] else
        "Spiritual learning for you is more through books, solo inquiry, and life experience than through a single revered teacher."),

        f"<b>Meditation and inner practice</b> — " + (
        "Natural meditator — inner stillness is accessible to you when you commit to the practice. You are capable of genuine depth in contemplative work."
        if ketu_h in [1,8,12] or chart["lagna"] in ["Pisces","Scorpio"] else
        "Meditation is not your natural spiritual channel — you connect better through active service, devotion, or philosophical study."),

        f"<b>Moksha and liberation orientation</b> — " + (
        "The chart has a marked spiritual liberation component — in later life, worldly ambitions naturally give way to a deeper pull toward meaning, service, and inner peace."
        if ketu_h in [8,12] or h12_lord_h in [12] else
        "Moksha is not the dominant chart theme — this is a life oriented toward dharmic engagement with the world, not withdrawal from it."),

        f"<b>Charity and service</b> — " + (
        "Genuine charitable impulse — giving back and serving those less fortunate are natural expressions of your values."
        if jup_dig in ["Own","Exalted"] or h12_lord_h in [9,12] else
        "Charity is occasional rather than a core life expression — you give when moved but it is not a defining theme."),

        f"<b>Spiritual timing</b> — "
        f"Spiritual depth typically increases markedly during Ketu and Jupiter Maha Dasha periods — "
        f"natural times for retreats, life-review, philosophical change, or religious commitment intensification.",
    ]

    # ── 15. TALENTS & SKILLS ──
    h5_occ=occupants(5); h3_occ=occupants(3); h3_lord=lord_of(3)
    ven_h=pos["Venus"]["house"]
    pred["talents"]=[
        f"<b>Musical and artistic talent</b> — " + (
        "Strong musical and artistic talent — whether as a performer, composer, or deeply appreciative listener, music is woven into your soul. Creative arts in general are a genuine gift."
        if ven_dig in ["Own","Exalted"] or ven_h in [1,2,5] else
        "Aesthetic appreciation is present but performing arts are not the primary talent — you enjoy art more as a consumer than as creator."),

        f"<b>Writing and communication talent</b> — " + (
        "Natural writer and communicator — words come easily, arguments form cleanly, and your ability to express complex ideas accessibly is above average."
        if merc_dig in ["Own","Exalted","Exalted/Own"] or merc_h in [1,3,5] else
        "Communication is functional rather than exceptional — writing and speaking work as tools but are not standout gifts."),

        f"<b>Technical and analytical talent</b> — " + (
        "Strong technical capacity — you can handle complex systems, numbers, and analytical problems with genuine aptitude. Engineering, computing, mathematics, or strategic planning are natural domains."
        if merc_dig in ["Own","Exalted","Exalted/Own"] and chart["lagna"] in ["Gemini","Virgo","Capricorn","Aquarius"] else
        "Technical ability is adequate rather than exceptional — you can learn technical skills but they are not your primary edge."),

        f"<b>Sports and physical talent</b> — " + (
        "Athletic ability is genuinely present — coordination, physical drive, and competitive spirit make you effective in sport or physical disciplines."
        if mars_dig in ["Own","Exalted","Exalted/Own"] or pos["Mars"]["house"] in [1,3,6] else
        "Sports are enjoyable but not a standout talent — casual participation rather than competitive achievement."),

        f"<b>Teaching and mentoring talent</b> — " + (
        "Natural teacher and mentor — you have an ability to explain, inspire, and develop others that is a genuine gift. Students and juniors respond well to your guidance."
        if jup_dig in ["Own","Exalted"] or jup_h in [1,5,9] else
        "Teaching is possible but not an innate gift — you prefer doing to teaching."),

        f"<b>Intuitive and psychic sensitivity</b> — " + (
        "Unusually strong intuition — a sense for reading situations, people, and upcoming events that others do not have. This can be developed into a real practical skill."
        if ketu_h in [1,4,8,12] or chart["lagna"] in ["Cancer","Scorpio","Pisces"] else
        "Intuition operates at a normal level — useful but not a defining gift."),

        f"<b>Language and multilingual capacity</b> — " + (
        "Natural language ability — learning foreign languages comes relatively easily. You may become genuinely proficient in more than two languages through life."
        if merc_h in [3,9] or pos["Rahu"]["house"] in [3,9] else
        "Language facility is average — you learn what you need but not beyond practical necessity."),

        f"<b>Hidden or undeveloped talents</b> — "
        f"The chart suggests talents in the creative and intuitive domains that may be undeveloped — "
        f"perhaps suppressed in favour of practical career demands. These deserve deliberate cultivation, especially in the second half of life.",
    ]

    # ── 16. PAST LIVES & KARMA ──
    ketu_h=pos["Ketu"]["house"]; rahu_h=pos["Rahu"]["house"]
    sat_h=pos["Saturn"]["house"]
    pred["past_lives"]=[
        f"<b>Past life skills</b> — "
        f"You come into this life with already-developed skills in the domain of {HOUSE_THEMES.get(ketu_h,'?')}. "
        f"These come almost too naturally — which can create a paradox of competence without fulfilment. The soul has been here before.",

        f"<b>Soul's current growth edge</b> — "
        f"This lifetime's growth challenge is in the domain of {HOUSE_THEMES.get(rahu_h,'?')}. "
        f"This is where you will stretch, fail, obsess, and eventually master something unfamiliar to the soul. "
        f"It may feel unnatural but it is where growth happens.",

        f"<b>Debt to father lineage</b> — " + (
        "Indicators of father-lineage karmic debt are present — this shows up as challenges related to father, authority, or career that have a karmic resolution quality. Past-life issues with authority are being healed in this lifetime."
        if sun_h in [6,8,12] or sun_dig=="Debil" else
        "No strong father-lineage karmic debt — the paternal line karma is relatively clear in this chart."),

        f"<b>Debt to mother lineage</b> — " + (
        "Some mother-lineage karmic pattern is present — the mother relationship or feminine-lineage themes carry a dimension requiring healing through patience and forgiveness."
        if moon_dig=="Debil" or moon_h in [6,8,12] else
        "Mother-lineage karma is relatively resolved — the maternal bond in this life is more choice than karmic obligation."),

        f"<b>Relational karmic debt</b> — " + (
        "A past-life relational debt pattern is indicated — this shows up as complex romantic or partner dynamics in this lifetime. The soul is working through something unfinished from a past bond."
        if ven_dig=="Debil" or h7_lord_h in [6,8,12] else
        "Relationship karma is relatively clean — romantic bonds in this life are more choice than karmic obligation."),

        f"<b>Inherited merit from past lives</b> — " + (
        "Strong inherited merit is present — the soul carries significant positive karma that shows up as unexpected help, fortunate timing, and a sense that the universe looks out for you at critical moments."
        if jup_dig in ["Own","Exalted"] or h9_lord_h in [9,11] else
        "Merit from past lives is moderate — what you receive in grace is balanced by what you must earn through effort. The universe is fair rather than generous."),

        f"<b>Karmic life pattern overall</b> — "
        f"This is a soul in active, engaged karmic processing — not a quiet life, but a meaningful one filled with significant lessons, "
        f"meaningful relationships, and the sense that events happen for a reason. The spiritual dimension of life is never far.",

        f"<b>How to resolve karmic debt</b> — "
        f"Service, charity, ritual for ancestors (especially on eclipse days and Amavasya), "
        f"and healing the specific relationships indicated by the problem planets are the most effective remedial paths in this chart.",
    ]

    # ── 17. ANNUAL PREDICTIONS ──
    today_ann=dt.datetime.now()
    b_ann=chart["birth"]
    birth_dt_ann=dt.datetime(b_ann["year"],b_ann["month"],b_ann["day"],b_ann["hour"],b_ann["min"])
    age_now=(today_ann-birth_dt_ann).days/365.25
    muntha_house=int(age_now%12)+1
    cur_md_lord=None; cur_md_years=None
    for md in mds:
        if md["start"]<=today_ann<=md["end"]:
            cur_md_lord=md["lord"]; cur_md_years=md["years"]; break
    pred["annual"]=[
        f"<b>Current year focus</b> — "
        f"The yearly activation falls on the domain of {HOUSE_THEMES.get(muntha_house,'?')} this year. "
        f"Events related to these themes are more likely and more significant during this annual cycle.",

        f"<b>Maha Dasha context</b> — " + (
        f"You are currently in the {cur_md_lord} Maha Dasha — a {cur_md_years:.1f}-year period shaped by {PLANET_ARCHETYPES.get(cur_md_lord,'')} themes. The annual layer runs inside this larger context."
        if cur_md_lord else
        "Your current Maha Dasha context provides the backdrop for all annual events — the yearly shifts are sub-themes within the larger period."),

        f"<b>This year's opportunity</b> — " + (
        "Career advancement and public recognition — push for visible achievements this year."
        if muntha_house in [10,11] else
        "Relationship building and partnership — important connections are made this year."
        if muntha_house in [7,9] else
        "Home, family, and property decisions — a good year for domestic investment."
        if muntha_house in [4,5] else
        "Inner reflection and spiritual growth — less external action, more inner consolidation."
        if muntha_house in [8,12] else
        "Health, service, and daily routine improvements — a foundational year for long-term wellbeing."),

        f"<b>This year's caution</b> — "
        f"The current annual cycle also activates a challenge zone — be cautious in decisions involving "
        f"{HOUSE_THEMES.get((muntha_house+5)%12+1,'?')} and avoid reckless commitments in this domain.",

        f"<b>Best months this year</b> — "
        f"The months when Jupiter and Venus transit favourable positions from your natal Moon tend to be "
        f"the peak months for any major initiative, decision, or life event this year.",

        f"<b>Annual wealth cycle</b> — " + (
        "Financially strong year — potential for income increase or windfall. A year to take calculated financial risks."
        if muntha_house in [2,11] else
        "Moderate financial activity — maintain and don't over-extend."
        if muntha_house in [1,4,5] else
        "Watch for unexpected expenses — financial conservatism and an emergency fund are important this cycle."),

        f"<b>Relationships this year</b> — " + (
        "Partnership and social themes are highlighted — marriage, business partnerships, or important new relationships are potential features this cycle."
        if muntha_house in [7,11] else
        "This is more an introspective than socially expansive year — existing relationships deepen while new connections are fewer."),

        f"<b>Health this year</b> — " + (
        "No major health flag this year — routine maintenance and standard care are sufficient."
        if muntha_house not in [6,8,12] else
        "Pay attention to health signals this year — do not ignore symptoms or postpone medical check-ups."),
    ]

    # ── 18. SPECIFIC EVENT PROBABILITIES ──
    pred["specific"]=[
        f"<b>Financial windfall or sudden gain</b> — " + (
        "Some probability of a significant unexpected financial event — inheritance, prize, unexpected business opportunity, or investment payoff during a Jupiter or Venus peak period."
        if jup_dig in ["Own","Exalted"] or (pos["Rahu"]["house"] in [2,11] and jup_h in [1,5,9,11]) else
        "Windfalls are not strongly marked — wealth in this chart is earned through effort rather than arriving unexpectedly. Stay cautious of get-rich-quick temptation."),

        f"<b>Legal or court matter risk</b> — " + (
        "Some legal involvement is possible in life — property, business, or family disputes that enter the formal legal system. Professional legal advice when needed is important."
        if h6_lord_h in [1,7,10] or pos["Saturn"]["house"] in [7,6] else
        "Legal disputes are not a significant life feature — conflicts resolve through negotiation rather than formal proceedings."),

        f"<b>Political career possibility</b> — " + (
        "The chart has markers for possible political involvement or significant public leadership — either direct political career or major influence in organisational leadership."
        if sun_dig in ["Own","Exalted"] and h10_lord_h in [1,9,10] else
        "Political career is not well-indicated — leadership expressed through professional excellence rather than political office."),

        f"<b>Accident or injury risk</b> — " + (
        "Some elevated accident risk during Mars-activated periods. Caution with vehicles, machinery, or physical risk during these windows."
        if mars_dig=="Debil" or pos["Mars"]["house"] in [6,8,12] else
        "Accident risk is at normal average level — standard caution and safety practices are sufficient."),

        f"<b>Legal restriction or imprisonment risk</b> — " + (
        "No strong indicator of imprisonment or severe legal restriction. The chart does not show this as a likely life feature."
        if h12_lord_h not in [1,6] and pos["Saturn"]["house"] not in [1,12] else
        "There is some indicator of legal restriction risk in certain periods — extreme caution around legal compliance, especially during Saturn-Rahu activations."),

        f"<b>Major medical event</b> — " + (
        "A significant health event at some point in life is a possibility — surgery, serious illness, or extended recovery. Being forewarned allows proactive care."
        if h8_occ or (pos["Mars"]["house"] in [6,8] and pos["Saturn"]["house"] in [6,8]) else
        "No major medical event is strongly marked — health journey follows a relatively normal trajectory."),

        f"<b>Relationship separation risk</b> — " + (
        "The chart shows some risk of marital tension or separation — incompatibility, third-party influence, or a major life disruption. Relationships require conscious maintenance."
        if ven_dig=="Debil" or h7_lord_h in [6,8,12] else
        "Marital stability is well-supported — separation is not a marked chart feature."),

        f"<b>Spiritual awakening event</b> — " + (
        "A genuine spiritual awakening or life-reorientation event is marked — likely during Ketu or Saturn Maha Dasha. The life before and after will feel qualitatively different."
        if ketu_h in [1,4,8,9,12] else
        "Spiritual development is gradual rather than a dramatic awakening — steady growth in wisdom rather than a crisis-led revelation."),
    ]

    return pred




































# ─── PAGE TEMPLATES ────────────────────────────────────
def page1_layout(c,doc):
    c.saveState()
    c.setFillColor(SHEET_BG); c.rect(0,0,A4[0],A4[1],fill=1,stroke=0)
    
    # Draw background watermark
    import os
    bg_pattern_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mystical_tiled_background.png")
    if os.path.exists(bg_pattern_path):
        c.saveState()
        c.setFillAlpha(0.07)  # Visible yet subtle background watermark
        w_x = 2.0 * cm
        w_y = 2.0 * cm
        w_w = A4[0] - 4.0 * cm
        w_h = A4[1] - 4.0 * cm
        c.drawImage(bg_pattern_path, w_x, w_y, width=w_w, height=w_h, mask='auto')
        c.restoreState()

    c.setStrokeColor(GOLD); c.setLineWidth(2)
    c.rect(20,20,A4[0]-40,A4[1]-40,fill=0,stroke=1)
    c.setStrokeColor(GOLD_LT); c.setLineWidth(0.5)
    c.rect(28,28,A4[0]-56,A4[1]-56,fill=0,stroke=1)
    c.setFillColor(GOLD_DK); c.setFont("Helvetica-Oblique",7)
    c.drawCentredString(A4[0]/2,28,
        "Generated by Atro Vedic Engine · 34 classical books · 8,239 rules · 3-engine ephemeris parity")
    c.restoreState()


def content_page(c,doc):
    c.saveState()
    c.setFillColor(SHEET_BG); c.rect(0,0,A4[0],A4[1],fill=1,stroke=0)
    
    # Draw background watermark
    import os
    bg_pattern_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mystical_tiled_background.png")
    if os.path.exists(bg_pattern_path):
        c.saveState()
        c.setFillAlpha(0.07)  # Visible yet subtle background watermark
        w_x = 0.95 * cm
        w_y = 0.95 * cm
        w_w = A4[0] - 1.9 * cm
        w_h = A4[1] - 1.9 * cm
        c.drawImage(bg_pattern_path, w_x, w_y, width=w_w, height=w_h, mask='auto')
        c.restoreState()

    # Draw borders on content pages
    c.setStrokeColor(GOLD); c.setLineWidth(1.0)
    c.rect(0.8 * cm, 0.8 * cm, A4[0] - 1.6 * cm, A4[1] - 1.6 * cm, fill=False, stroke=True)
    c.setStrokeColor(INDIGO); c.setLineWidth(0.5)
    c.rect(0.95 * cm, 0.95 * cm, A4[0] - 1.9 * cm, A4[1] - 1.9 * cm, fill=False, stroke=True)

    c.setFillColor(INDIGO); c.rect(0,A4[1]-32,A4[0],32,fill=1,stroke=0)
    c.setFillColor(GOLD); c.rect(0,A4[1]-34,A4[0],2,fill=1,stroke=0)
    c.setFillColor(CREAM); c.setFont("Helvetica-Bold",9)
    c.drawString(2.5*cm,A4[1]-21,doc._person_name+" · LIFE TIMELINE")
    c.setFont("Helvetica-Oblique",8); c.setFillColor(GOLD_LT)
    c.drawRightString(A4[0]-2.5*cm,A4[1]-21,"Vedic Astrology Reading")
    c.setFillColor(INDIGO); c.rect(0,0,A4[0],26,fill=1,stroke=0)
    c.setFillColor(GOLD); c.rect(0,26,A4[0],1.5,fill=1,stroke=0)
    c.setFillColor(CREAM); c.setFont("Helvetica",9)
    c.drawCentredString(A4[0]/2,10,f"— {doc.page} —")
    c.setFont("Helvetica-Oblique",7); c.setFillColor(GOLD_LT)
    c.drawString(2.5*cm,10,"ATRO ENGINE")
    c.drawRightString(A4[0]-2.5*cm,10,"© CONFIDENTIAL")
    c.restoreState()


# ─── BUILD JADHAGAM PAGE 1 ─────────────────────────────
def build_page1(chart,mds,cur_ad):
    flow=[]
    b=chart["birth"]
    weekday=b.get("weekday",""); birth_date=f"{b['day']:02d}-{b['month']:02d}-{b['year']}"
    birth_time=f"{b['hour']:02d}:{b['min']:02d} IST"; birth_place=b.get("place","")
    flow.append(HeaderBar(A4[0]-4*cm,chart["name"],birth_date,birth_time,birth_place,weekday))
    flow.append(Spacer(1,0.4*cm))

    # Center the zodiac character illustration
    import os
    from reportlab.platypus import Image as RLImage
    runtime_dir = os.path.dirname(os.path.abspath(__file__))
    rasi_clean = str(chart.get("moon_rasi", "")).strip().lower()
    img_name = f"{rasi_clean}_character.png"
    img_path = os.path.join(runtime_dir, img_name)
    fallback_path = os.path.join(runtime_dir, "zodiac_flat_icon.png")
    
    selected_path = None
    if os.path.exists(img_path):
        selected_path = img_path
    elif os.path.exists(fallback_path):
        selected_path = fallback_path
        
    if selected_path:
        flow.append(RLImage(selected_path, width=2.5*cm, height=2.5*cm, hAlign="CENTER"))
        flow.append(Spacer(1,0.3*cm))

    moon=chart["positions"]["Moon"]
    items=[
        ("Lagna",chart["lagna"]),
        ("Moon Rasi",chart["moon_rasi"]),
        ("Nakshatra",f"{chart['janma_nakshatra']} pada {moon.get('pada','?')}"),
        ("Nak Lord",chart["janma_nakshatra_lord"]),
        ("Lagna Lord",chart.get("lagna_lord","—")),
        ("Day",weekday or "—"),
        ("Ayanamsa",f"{chart.get('ayanamsa','—'):.4f}deg" if isinstance(chart.get('ayanamsa'),(int,float)) else "—"),
    ]
    rows=[]
    for lbl,val in items:
        rows.append([
            Paragraph(f"<font color='#c0392b' size='8'><b>{lbl.upper()}</b></font>",body_small),
            Paragraph(f"<font color='#1f3a4a' size='9'><b>{val}</b></font>",body_small),
        ])
    # Bigger details box: 5.5cm wide so values don't wrap
    details_t=Table(rows,colWidths=[2.2*cm,3.3*cm],rowHeights=[0.78*cm]*len(rows))
    details_t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),SHEET_BG),
        ("BOX",(0,0),(-1,-1),1.2,GOLD),
        ("LINEBELOW",(0,0),(-1,-2),0.3,GREY_LT),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5),
    ]))

    pos_for_chart={p:pd["rasi_idx"] for p,pd in chart["positions"].items()}
    # Slightly smaller charts to fit larger details
    rasi_chart=SouthIndianChart(6.8*cm,pos_for_chart,chart["lagna_idx"],"RASI / D1")
    bhava_chart=SouthIndianChart(6.8*cm,pos_for_chart,chart["lagna_idx"],"BHAVA")

    main_grid=Table([[details_t,rasi_chart,bhava_chart]],
                    colWidths=[5.5*cm,6.8*cm,6.8*cm],rowHeights=[6.8*cm])
    main_grid.setStyle(TableStyle([
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("LEFTPADDING",(0,0),(-1,-1),2),("RIGHTPADDING",(0,0),(-1,-1),2),
        ("TOPPADDING",(0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),0),
    ]))
    flow.append(main_grid)
    flow.append(Spacer(1,0.4*cm))

    today_str=dt.datetime.now().strftime("%d-%b-%Y")
    today=dt.datetime.now()
    if cur_ad:
        cur_md_yrs=VIMSHOTTARI_YEARS.get(cur_ad["md"],0)
        ad_yrs=round((cur_ad["end"]-cur_ad["start"]).days/365.25,2)
        cur_rows=[["NOW: "+today_str,""],["Maha Dasha",f"{cur_ad['md']} ({cur_md_yrs}y)"],
                  ["Antar Dasha",cur_ad['ad']],["From",cur_ad['start'].strftime("%d-%b-%Y")],
                  ["To",cur_ad['end'].strftime("%d-%b-%Y")],["Duration",f"{ad_yrs}y"]]
        md_idx=VIMSHOTTARI_ORDER.index(cur_ad["md"])
        cur_md_data=next((m for m in mds if m["lord"]==cur_ad["md"]),None)
        next_rows=[["NEXT",""]]
        if cur_md_data:
            sub_start=cur_md_data["start"]
            for k in range(9):
                sp=VIMSHOTTARI_ORDER[(md_idx+k)%9]
                sy=cur_md_data["years"]*VIMSHOTTARI_YEARS[sp]/120
                sub_end=sub_start+dt.timedelta(days=sy*365.25)
                if sub_start>today:
                    next_rows.extend([["Maha Dasha",cur_ad["md"]],["Antar Dasha",sp],
                                       ["From",sub_start.strftime("%d-%b-%Y")],
                                       ["To",sub_end.strftime("%d-%b-%Y")]])
                    break
                sub_start=sub_end
        if len(next_rows)==1:
            next_md=next((m for m in mds if m["start"]>today),None)
            if next_md:
                next_rows.extend([["Maha Dasha",next_md["lord"]],["Antar Dasha",next_md["lord"]],
                                   ["From",next_md["start"].strftime("%d-%b-%Y")],
                                   ["To",next_md["end"].strftime("%d-%b-%Y")]])
    else:
        cur_rows=[["No active dasha",""]]; next_rows=[["—",""]]

    def dasha_t(rows,header_color=INDIGO,col_widths=None):
        styled=[]
        for i,(l,r) in enumerate(rows):
            styled.append([
                Paragraph(f"<font size='8'><b>{l}</b></font>",
                    ParagraphStyle("d",fontName="Helvetica-Bold",leading=11,
                                    textColor=CREAM if i==0 else BLUE_INK)),
                Paragraph(f"<font size='8'>{r}</font>",
                    ParagraphStyle("dv",fontName="Helvetica",leading=11,
                                    textColor=CREAM if i==0 else GREY_DK)),
            ])
        while len(styled)<7:
            styled.append([Paragraph("",body_small),Paragraph("",body_small)])
        cw = col_widths or [2.3*cm,3.5*cm]
        t=Table(styled,colWidths=cw,rowHeights=[0.78*cm]*len(styled))
        t.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0),header_color),
            ("BACKGROUND",(0,1),(-1,-1),SHEET_BG),
            ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
            ("LEFTPADDING",(0,0),(-1,-1),6),("RIGHTPADDING",(0,0),(-1,-1),6),
            ("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3),
            ("LINEABOVE",(0,0),(-1,0),1.5,GOLD),
            ("LINEBELOW",(0,-1),(-1,-1),1.5,GOLD),
            ("BOX",(0,0),(-1,-1),0.5,SHEET_LINE),
        ]))
        return t

    cur_t=dasha_t(cur_rows); next_t=dasha_t(next_rows)
    favorable=[m for m in mds if m["lord"] in ["Venus","Jupiter","Moon"] and m["end"]>today][:3]
    marriage_rows=[["MARRIAGE WINDOWS (FUTURE)",""]]
    for i,md in enumerate(favorable,1):
        is_active=md["start"]<=today<=md["end"]
        marker=" ★" if is_active else ""
        # For currently active MD, clip displayed start to today (don't show past start)
        display_start=today if is_active else md["start"]
        marriage_rows.append([f"#{i} {md['lord']}{marker}",
                               f"{display_start.strftime('%b %Y')} - {md['end'].strftime('%b %Y')}"])
    while len(marriage_rows)<6: marriage_rows.append(["",""])
    marriage_t=dasha_t(marriage_rows,header_color=MAROON)

    row2=Table([[cur_t,next_t,marriage_t]],colWidths=[6.4*cm,6.4*cm,6.4*cm])
    row2.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),
                               ("LEFTPADDING",(0,0),(-1,-1),3),("RIGHTPADDING",(0,0),(-1,-1),3)]))
    flow.append(row2)
    flow.append(Spacer(1,0.4*cm))

    pos=chart["positions"]
    def asp(p):
        ph=pos[p]["house"]
        if p=="Jupiter": return [(ph+4-1)%12+1,(ph+6)%12+1,(ph+8)%12+1]
        elif p=="Mars": return [(ph+3-1)%12+1,(ph+6)%12+1,(ph+7)%12+1]
        elif p=="Saturn": return [(ph+2-1)%12+1,(ph+6)%12+1,(ph+9)%12+1]
        return []
    aj=asp("Jupiter"); am=asp("Mars"); ass=asp("Saturn")
    asp_rows=[["GRAHA ASPECTS",""],
              [f"Jupiter H{pos['Jupiter']['house']}",f"H{aj[0]}, H{aj[1]}, H{aj[2]}"],
              [f"Mars H{pos['Mars']['house']}",f"H{am[0]}, H{am[1]}, H{am[2]}"],
              [f"Saturn H{pos['Saturn']['house']}",f"H{ass[0]}, H{ass[1]}, H{ass[2]}"]]
    asp_t=dasha_t(asp_rows,header_color=PURPLE)

    pl_houses=[pd["house"] for p,pd in pos.items() if p!="Ketu"]
    kc=sum(1 for h in pl_houses if h in [1,4,7,10])
    tc=sum(1 for h in pl_houses if h in [1,5,9])
    uc=sum(1 for h in pl_houses if h in [3,6,10,11])
    dc=sum(1 for h in pl_houses if h in [6,8,12])
    yoga_rows=[["HOUSE GROUPS",""],["Trikona (1-5-9)",f"{tc} planets"],
               ["Kendra (1-4-7-10)",f"{kc} planets"],
               ["Upachaya (3-6-10-11)",f"{uc} planets"]]
    yoga_t=dasha_t(yoga_rows,header_color=GOLD_DK)

    notes_rows=[["KEY MARKERS",""],
                ["Lagnesh",f"{chart.get('lagna_lord','?')} in H{pos[chart['lagna_lord']]['house']}" if chart.get('lagna_lord') in pos else "—"],
                ["Moon Pada",f"{moon.get('pada','?')}"],
                ["Dusthana planets",f"{dc}"]]
    notes_t=dasha_t(notes_rows,header_color=BLUE_INK)

    row3=Table([[asp_t,yoga_t,notes_t]],colWidths=[6.4*cm,6.4*cm,6.4*cm])
    row3.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),
                               ("LEFTPADDING",(0,0),(-1,-1),3),("RIGHTPADDING",(0,0),(-1,-1),3)]))
    flow.append(row3)
    return flow


# ─── DOMAIN PAGE BUILDER ───────────────────────────────
def domain_page(icon,number,title,subtitle,items,intro_paragraph=None):
    elems=[]
    elems.append(DomainHeader(A4[0]-5*cm,icon,number,title,subtitle))
    elems.append(Spacer(1,0.5*cm))
    if intro_paragraph:
        elems.append(Paragraph(intro_paragraph,body))
        elems.append(Spacer(1,0.4*cm))
    for it in items:
        # Each "item" is a full paragraph with bold lead phrase
        elems.append(Paragraph(it,body))
        elems.append(Spacer(1,0.15*cm))
    return elems


def chapter_with_narrative(num,planet,dates,ages,theme,chart,sub_dashas,today,is_current):
    """Deep-narrative chapter (v2-style) with EXPECT/WATCH columns + sub-period table."""
    elems=[]
    pos=chart["positions"]
    elems.append(ChapterHeader(A4[0]-5*cm,num,planet,dates,ages,theme))
    elems.append(Spacer(1,0.5*cm))

    # Snapshot card: status / focus / theme
    is_cur_str = "CURRENT" if is_current else f"{(dt.datetime.strptime(dates.split(' — ')[1],'%Y') - dt.datetime.strptime(dates.split(' — ')[0],'%Y')).days/365.25:.1f}y" if " — " in dates else "—"
    snap_focus = f"H{pos[planet]['house']} ({pos[planet]['rasi']})" if planet in pos else "—"
    snap_theme = ", ".join(PLANET_ARCHETYPES.get(planet,'').split(",")[:2])
    snap_facts = [("STATUS", "★ CURRENT ★" if is_current else "—"),
                   ("FOCUS", snap_focus),
                   ("THEME", snap_theme)]
    snap = snapshot_card(snap_facts)
    elems.append(snap)
    elems.append(Spacer(1,0.5*cm))

    # ─── DEEP NARRATIVE INTRO (v2 style) ───
    if planet in pos:
        ph=pos[planet]["house"]
        pr=pos[planet]["rasi"]
        d=DIGNITIES.get((planet,pr),'neutral')
        archetypes=PLANET_ARCHETYPES.get(planet,'')

        # Build rich intro paragraph
        intro_parts=[]
        if planet=="Sun":
            intro_parts.append(f"The Sun is the natural king of the chart and in this period sits in <b>{pr}</b> "
                               f"in House {ph}.")
        elif planet=="Moon":
            intro_parts.append(f"The Moon governs the mind, public role, and emotional life. Here it sits in "
                               f"<b>{pr}</b> in House {ph}.")
        elif planet=="Mars":
            intro_parts.append(f"Mars rules energy, action, courage, and conflict. In this chart Mars sits in "
                               f"<b>{pr}</b> in House {ph}.")
        elif planet=="Mercury":
            intro_parts.append(f"Mercury governs intellect, communication, commerce, and learning. It sits in "
                               f"<b>{pr}</b> in House {ph}.")
        elif planet=="Jupiter":
            intro_parts.append(f"Jupiter is the great benefic — wisdom, dharma, expansion, children. "
                               f"It sits in <b>{pr}</b> in House {ph}.")
        elif planet=="Venus":
            intro_parts.append(f"Venus rules love, marriage, comforts, arts, vehicles. It sits in <b>{pr}</b> "
                               f"in House {ph}.")
        elif planet=="Saturn":
            intro_parts.append(f"Saturn rules discipline, longevity, perseverance, delays, sorrow. "
                               f"It sits in <b>{pr}</b> in House {ph}.")
        elif planet=="Rahu":
            intro_parts.append(f"Rahu — the north node, the shadow planet of obsession, foreign influence, "
                               f"unconventional paths. It sits in <b>{pr}</b> in House {ph}.")
        elif planet=="Ketu":
            intro_parts.append(f"Ketu — the south node, planet of detachment, spirituality, past karma. "
                               f"It sits in <b>{pr}</b> in House {ph}.")

        # Add dignity context
        if d=="Exalted":
            intro_parts.append(f"<b>{planet} is EXALTED</b> in this sign — its strongest possible dignity. "
                               f"All themes of {planet}'s archetype ({archetypes}) operate at peak strength during this period.")
        elif d in ["Own","Exalted/Own"]:
            intro_parts.append(f"<b>{planet} is in its own sign</b> — comfortable, productive, no major struggles. "
                               f"It can fully express its themes ({archetypes}).")
        elif d=="Debil":
            intro_parts.append(f"<b>{planet} is DEBILITATED</b> — operating in its weakest sign. The themes of "
                               f"{archetypes} face challenges in this period; conscious effort needed.")
        else:
            intro_parts.append(f"{planet} operates in {pr} with neutral dignity — neither boosted nor weakened by sign.")

        # Add house meaning + house karaka effects
        intro_parts.append(f"This period merges {planet}'s natural significations with the affairs of "
                           f"<b>House {ph} ({HOUSE_THEMES.get(ph,'?')})</b>. "
                           f"Practically, this means {planet}'s themes will play out through this domain in life.")

        # Add specific 8th-house / 6th / 12th warning
        if ph in [6,8,12]:
            intro_parts.append(f"<i>Note: House {ph} is one of the dusthana (challenging) houses. "
                               f"This period brings tests and transformations through {HOUSE_THEMES.get(ph,'?')}, "
                               f"but also growth through what one survives.</i>")

        # Length & current marker
        intro_parts.append(f"This Maha Dasha lasts {sub_dashas[0]['md_years']} approximately, "
                           f"covering ages {ages}.")
        if is_current:
            intro_parts.append(f"<b>You are currently inside this period</b> — the sub-periods below show "
                               f"the unfolding within it.")

        elems.append(Paragraph(" ".join(intro_parts), body))
    else:
        elems.append(Paragraph(f"This {planet} period covers ages {ages}, from {dates}.", body))
    elems.append(Spacer(1,0.4*cm))

    # ─── EXPECT vs WATCH columns ───
    expect, watch = build_expect_watch(planet, chart)
    if expect or watch:
        elems.append(expect_watch_table(expect, watch))
        elems.append(Spacer(1,0.4*cm))

    # ─── SUB-PERIOD TABLE ───
    elems.append(Paragraph(f"<b>Sub-Periods (Antar Dashas) within this {planet} MD:</b>", h3))
    sub_rows=[["AD","FROM","TO","YEARS","STATUS"]]
    for s in sub_dashas:
        cur_marker="▶ NOW" if s["start"]<=today<=s["end"] else ""
        sub_rows.append([
            Paragraph(f"<font color='{hexstr(PLANET_COLOR.get(s['ad'],INDIGO))}' size='12'><b>{PLANET_GLYPH.get(s['ad'],'')}</b></font> <b>{s['ad']}</b>",body_small),
            Paragraph(s['start'].strftime("%d %b %Y"),body_small),
            Paragraph(s['end'].strftime("%d %b %Y"),body_small),
            Paragraph(f"{s['years']:.2f}",body_small),
            Paragraph(f"<b>{cur_marker}</b>",body_small),
        ])
    st=Table(sub_rows,colWidths=[3*cm,3*cm,3*cm,2*cm,3.5*cm])
    st.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),INDIGO),("TEXTCOLOR",(0,0),(-1,0),CREAM),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,0),8),
        ("LINEBELOW",(0,0),(-1,0),1,GOLD),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[white,GREY_LT]),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
        ("LEFTPADDING",(0,0),(-1,-1),8),
    ]))
    elems.append(st)

    # ─── If current MD: detailed sub-period commentary ───
    if is_current:
        elems.append(Spacer(1,0.4*cm))
        elems.append(Paragraph("<b>Sub-period commentary — what each Antar brings:</b>", h3))
        for s in sub_dashas:
            ad=s['ad']
            ad_archetype=PLANET_ARCHETYPES.get(ad,'')
            cur_marker=" <b>← CURRENT</b>" if s["start"]<=today<=s["end"] else ""
            past_marker=" (past)" if s["end"]<today else ""
            text=(f"<b>{planet}-{ad}</b> &nbsp; {s['start'].strftime('%b %Y')} - {s['end'].strftime('%b %Y')}"
                  f"{cur_marker}{past_marker}: " +
                  ("identity strengthens, public role, possible authority offered" if ad=='Sun' else
                   "emotional shifts, mother-related events, public visibility" if ad=='Moon' else
                   "energetic action, possible conflict, accidents possible, real estate decisions" if ad=='Mars' else
                   "communication-driven success, deals, sibling reconnection" if ad=='Mercury' else
                   "expansion, dharma, children if applicable, wisdom + wealth" if ad=='Jupiter' else
                   "marriage / comforts / arts / vehicles peak" if ad=='Venus' else
                   "slow period, hard work, delays, eventual stability" if ad=='Saturn' else
                   "foreign / unconventional / tech opportunities, possibly confused decisions" if ad=='Rahu' else
                   "spiritual deepening, detachment, sudden changes"))
            elems.append(Paragraph(text, body_small))
            elems.append(Spacer(1,0.1*cm))
    return elems


def build_expect_watch(planet, chart):
    """Build EXPECT/WATCH columns for a Maha Dasha period — chart specific."""
    expect=[]; watch=[]
    pos=chart["positions"]
    if planet not in pos:
        return expect, watch
    ph=pos[planet]["house"]
    pr=pos[planet]["rasi"]
    d=DIGNITIES.get((planet,pr),'neutral')

    # Dignity-driven expectations
    if d=="Exalted":
        expect.append(f"{planet} is EXALTED — peak strength all period")
        expect.append(f"Best results in House {ph} affairs")
    elif d in ["Own","Exalted/Own"]:
        expect.append(f"{planet} in own sign — comfortable, productive")
    elif d=="Debil":
        watch.append(f"{planet} is DEBILITATED — challenges in its themes")
        watch.append(f"Need conscious effort in {HOUSE_THEMES.get(ph,'?')}")

    # House-specific
    if ph==1: expect.append("Self/identity strongly developed")
    elif ph==2: expect.append("Wealth + family + speech themes activated"); expect.append("Possible income upgrade")
    elif ph==3: expect.append("Sibling/courage/communication peak"); watch.append("Sibling friction possible")
    elif ph==4: expect.append("Home, mother, comfort focus"); expect.append("Property purchase possible"); watch.append("Property/family disputes possible")
    elif ph==5: expect.append("Children, creativity, intelligence peak"); expect.append("Romance / love affair window")
    elif ph==6: watch.append("Workplace stress, enemies, health watch"); expect.append("Service/work career activates"); watch.append("6th house = digestion/legal/disputes")
    elif ph==7: expect.append("Marriage / partnership themes peak"); expect.append("Spouse-related events")
    elif ph==8: watch.append("Transformation period — old patterns end"); watch.append("Possible inheritance or surgery"); expect.append("Research, occult, depth-psychology")
    elif ph==9: expect.append("Dharma, foreign travel, father, luck peak"); expect.append("Pilgrimage or spiritual teacher")
    elif ph==10: expect.append("Career, fame, public role peak"); expect.append("Authority offered or claimed")
    elif ph==11: expect.append("Gains, friends, network expansion"); expect.append("Income from multiple sources")
    elif ph==12: watch.append("Loss / expenditure / isolation themes"); expect.append("Spiritual deepening, foreign settlement")

    # Planet-specific generic
    if planet=="Sun":
        watch.append("Father health watch")
        watch.append("Ego conflicts in workplace possible")
    elif planet=="Moon":
        expect.append("Public visibility, emotional rebalance")
        watch.append("Mother health watch")
    elif planet=="Mars":
        watch.append("Accidents, anger, surgery possible")
        expect.append("Bold action, real estate gains, independence")
    elif planet=="Mercury":
        expect.append("Communication, commerce, learning peaks")
        expect.append("Writing/teaching/consulting opportunities")
    elif planet=="Jupiter":
        expect.append("Wisdom, wealth, children, dharma peak")
        expect.append("Major life expansion + recognition")
    elif planet=="Venus":
        expect.append("Marriage, comforts, arts, vehicles")
        watch.append("Indulgence excess possible")
    elif planet=="Saturn":
        watch.append("Slow period, hard work, delays")
        expect.append("Discipline pays off long-term")
        watch.append("Sade Sati activation if Saturn near Moon")
    elif planet=="Rahu":
        expect.append("Foreign / unconventional / tech opportunities")
        watch.append("Confusion, scandal risk if reckless")
    elif planet=="Ketu":
        expect.append("Spiritual deepening, detachment, research")
        watch.append("Sudden changes, pause periods")

    return expect, watch


def expect_watch_table(expect_rows, watch_rows):
    """Two-column EXPECT vs WATCH layout."""
    data = [[
        Paragraph("<font color='#0a7a3a' size='12'><b>✓  EXPECT</b></font>", body_small),
        Paragraph("<font color='#b91c4f' size='12'><b>!  WATCH</b></font>", body_small),
    ]]
    n = max(len(expect_rows), len(watch_rows), 1)
    for i in range(n):
        e = expect_rows[i] if i < len(expect_rows) else ""
        w = watch_rows[i] if i < len(watch_rows) else ""
        data.append([
            Paragraph(f"&nbsp;&nbsp;&bull; &nbsp;{e}" if e else "", body),
            Paragraph(f"&nbsp;&nbsp;&bull; &nbsp;{w}" if w else "", body),
        ])
    cw = (A4[0] - 5*cm) / 2
    t = Table(data, colWidths=[cw, cw])
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(0,0),GREEN_BG),
        ("BACKGROUND",(1,0),(1,0),RED_BG),
        ("BACKGROUND",(0,1),(0,-1),HexColor("#f6fbf8")),
        ("BACKGROUND",(1,1),(1,-1),HexColor("#fdf4f6")),
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("TOPPADDING",(0,0),(-1,0),12),("BOTTOMPADDING",(0,0),(-1,0),12),
        ("TOPPADDING",(0,1),(-1,-1),8),("BOTTOMPADDING",(0,1),(-1,-1),8),
        ("LEFTPADDING",(0,0),(-1,-1),14),("RIGHTPADDING",(0,0),(-1,-1),14),
        ("LINEAFTER",(0,0),(0,-1),1.5,GOLD),
    ]))
    return t


def snapshot_card(facts):
    label_row=[]; value_row=[]
    for lbl,val in facts:
        label_row.append(Paragraph(
            f"<font color='#8a6a18' size='8'><b>{lbl.upper()}</b></font>",body_small))
        value_row.append(Paragraph(
            f"<font color='#1a1d3a' size='12'><b>{val}</b></font>",body_small))
    cw=(A4[0]-5*cm)/3
    t=Table([label_row,value_row],colWidths=[cw,cw,cw],rowHeights=[18,38])
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),CREAM_2),
        ("LINEABOVE",(0,0),(-1,0),2.5,GOLD),
        ("LINEBELOW",(0,-1),(-1,-1),2.5,GOLD),
        ("LINEAFTER",(0,0),(-2,-1),0.6,GOLD_LT),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8),
        ("LEFTPADDING",(0,0),(-1,-1),14),("RIGHTPADDING",(0,0),(-1,-1),14),
    ]))
    return t


# ─── BUILD FULL DOC ────────────────────────────────────
class _Skip(Exception):
    """Skip a report section gated off in the SHOW config (client revision)."""



def build_truth_report_section(chart):
    from reportlab.platypus import HRFlowable
    from reportlab.lib.enums import TA_CENTER
    flow = []
    tr = chart.get("truth_report")
    if not tr:
        return flow
    
    flow.append(PageBreak())
    flow.append(to_para("KNOWLEDGE-GRAPH TRUTH REPORT", h1))
    flow.append(to_para("Evidence-based synthesis & traceability audit", h1_sub))
    flow.append(HRFlowable(width="100%", thickness=0.8, color=GOLD, spaceAfter=8))
    
    # Metadata summary table
    state = tr.get("report_state", "unknown").upper()
    g_sum = tr.get("graph_summary", {})
    nodes = g_sum.get("nodes", 0)
    edges = g_sum.get("edges", 0)
    claims_count = g_sum.get("claims", 0)
    
    meta_rows = [
        [Paragraph("<b>Report State:</b>", body_small), Paragraph(state, body_small),
         Paragraph("<b>Graph Size:</b>", body_small), Paragraph(f"{nodes} nodes, {edges} edges", body_small)],
        [Paragraph("<b>Verification Level:</b>", body_small), Paragraph("Corpus Cross-Reference (Traceable)", body_small),
         Paragraph("<b>Active Claims:</b>", body_small), Paragraph(str(claims_count), body_small)]
    ]
    t_meta = Table(meta_rows, colWidths=[3.2*cm, 3.8*cm, 3.2*cm, 3.8*cm])
    t_meta.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, GREY_LT),
        ("BACKGROUND", (0,0), (-1,-1), SHEET_BG),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
    ]))
    flow.append(t_meta)
    flow.append(Spacer(1, 0.4*cm))
    
    # 1. Chart Facts
    flow.append(to_para("<b>Calculated Chart Facts (Reproducible):</b>", h2))
    facts = tr.get("chart_facts", [])
    if facts:
        for f in facts:
            lbl = f.get("label", "")
            flow.append(to_para(f"&nbsp;&bull; {lbl}", body))
    else:
        flow.append(to_para("No facts registered in the graph.", body))
    flow.append(Spacer(1, 0.4*cm))
    
    # 2. Active Claims
    flow.append(to_para("<b>Synthesized Claims & Evidence Trails:</b>", h2))
    claims = tr.get("claims", [])
    if claims:
        for c in claims:
            topic = c.get("topic", "").replace("_", " ").upper()
            status = c.get("status", "").upper()
            band = c.get("confidence_band", "").upper()
            statement = c.get("statement", "")
            
            color = "#0a7a3a" if status == "SUPPORTED" else ("#d97706" if status in ("TENTATIVE", "MIXED") else "#c0392b")
            
            flow.append(to_para(f"<b>Theme: {topic}</b> &nbsp;&nbsp; [<font color='{color}'><b>{status} / {band}</b></font>]", h3))
            flow.append(to_para(statement, body))
            
            why = c.get("why", {})
            supports = why.get("supports", [])
            contradictions = why.get("contradictions", [])
            citations = why.get("citations", [])
            
            if supports:
                flow.append(to_para("&nbsp;&nbsp;<b>Supported by:</b>", body_small))
                for s in supports:
                    clean_s = s.replace("fact:", "Fact: ").replace("method_finding:", "Finding: ").replace("method:", "Method: ")
                    flow.append(to_para(f"&nbsp;&nbsp;&nbsp;&nbsp;&bull; {clean_s}", body_small))
            
            if contradictions:
                flow.append(to_para("&nbsp;&nbsp;<b>Contradicted by:</b>", body_small))
                for ct in contradictions:
                    clean_ct = ct.replace("fact:", "Fact: ").replace("method_finding:", "Finding: ").replace("method:", "Method: ")
                    flow.append(to_para(f"&nbsp;&nbsp;&nbsp;&nbsp;&bull; {clean_ct}", body_small, textColor=RED))
            
            if citations:
                flow.append(to_para("&nbsp;&nbsp;<b>Traceable Citations:</b>", body_small))
                for cit in citations:
                    clean_cit = cit.replace("citation:", "")
                    flow.append(to_para(f"&nbsp;&nbsp;&nbsp;&nbsp;&bull; {clean_cit}", body_small, textColor=PURPLE))
            flow.append(Spacer(1, 0.3*cm))
    else:
        flow.append(to_para("No active claims generated for this chart.", body))
    flow.append(Spacer(1, 0.4*cm))
    
    # 3. Method Coverage
    flow.append(to_para("<b>Method Coverage & Availability:</b>", h2))
    cov = tr.get("method_coverage", {})
    if cov:
        cov_rows = [["METHOD FAMILY", "STATUS", "SAFE CODE"]]
        for method, info in sorted(cov.items()):
            state = info.get("state", "").upper()
            code = info.get("safe_code", "OK")
            color = "#0a7a3a" if state == "AVAILABLE" else "#c0392b"
            cov_rows.append([
                Paragraph(f"<b>{method.upper()}</b>", body_small),
                Paragraph(f"<font color='{color}'><b>{state}</b></font>", body_small),
                Paragraph(code, body_small)
            ])
        t_cov = Table(cov_rows, colWidths=[5.0*cm, 4.0*cm, 5.0*cm])
        t_cov.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), INDIGO),
            ("TEXTCOLOR", (0,0), (-1,0), CREAM),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [white, GREY_LT]),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("TOPPADDING", (0,0), (-1,-1), 4),
            ("BOTTOMPADDING", (0,0), (-1,-1), 4),
            ("LEFTPADDING", (0,0), (-1,-1), 6),
            ("GRID", (0,0), (-1,-1), 0.5, SAND_DK),
        ]))
        flow.append(t_cov)
        
    return flow


def generate(chart_path,out_name):
    chart=json.load(open(chart_path,encoding="utf-8"))
    out_path=REPORTS/out_name

    doc=BaseDocTemplate(str(out_path),pagesize=A4,
        leftMargin=2*cm,rightMargin=2*cm,topMargin=2*cm,bottomMargin=1.8*cm)
    doc._person_name=chart["name"].upper()

    p1_frame=Frame(2*cm,1.5*cm,A4[0]-4*cm,A4[1]-3.5*cm,id="p1",
                    leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)
    p1_tmpl=PageTemplate(id="p1",frames=[p1_frame],onPage=page1_layout)
    content_frame=Frame(2.5*cm,1.8*cm,A4[0]-5*cm,A4[1]-4.5*cm,id="content",
                         leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)
    content_tmpl=PageTemplate(id="content",frames=[content_frame],onPage=content_page)
    doc.addPageTemplates([p1_tmpl,content_tmpl])

    mds,cur_md,cur_ad,sub_dashas=vimshottari(chart)
    yogas=detect_yogas(chart)
    karakas=chara_karakas(chart)
    preds=all_predictions(chart)
    today=dt.datetime.now()
    b=chart["birth"]
    age_now=(today-dt.datetime(b["year"],b["month"],b["day"])).days/365.25

    flow=[]

    # ─── SECTION VISIBILITY (client revision 2026-06-15) ──────────────────
    # Trim deep/technical pages the client found unnecessary. Flip a key to
    # True to restore that section. Helper modules are untouched — this only
    # gates page output. "thirty_day" kept ON (client said "wait"/hold).
    SHOW={
        "sahams":False, "eclipse":False, "thirty_day":True,
        "tara_chakra":False, "full_shadbala":False, "vimshopaka":False,
        "tri_pataki":False, "varshaphala_internal":False, "jaimini_dashas":False,
        "muhurta_windows":False, "special_lagnas":False,
    }

    # ─── PAGE 1: Jadhagam ───
    flow.extend(build_page1(chart,mds,cur_ad))
    flow.append(NextPageTemplate("content"))
    flow.append(PageBreak())

    # ─── PAGE 2: Life Map ───
    flow.append(to_para("THE LIFE MAP",h1))
    flow.append(to_para("Vimshottari Maha Dasha sequence · current position marked",h1_sub))
    timeline_data=[(md["lord"],int(md["age_from"]),int(md["age_to"])) for md in mds]
    flow.append(TimelineBar(A4[0]-5*cm,timeline_data,age_now))
    flow.append(Spacer(1,0.6*cm))
    rows=[["#","LORD","FROM","TO","AGES","YEARS"]]
    for i,md in enumerate(mds,1):
        is_cur=md["start"]<=today<=md["end"]
        marker=" ▶ NOW" if is_cur else ""
        rows.append([Paragraph(f"<b>{i}</b>",body),
            Paragraph(f"<font color='{hexstr(PLANET_COLOR.get(md['lord'],INDIGO))}' size='14'><b>{PLANET_GLYPH.get(md['lord'],'')}</b></font> <b>{md['lord']}</b>{marker}",body),
            Paragraph(md["start"].strftime("%d-%b-%Y"),body),
            Paragraph(md["end"].strftime("%d-%b-%Y"),body),
            Paragraph(f"{md['age_from']:.1f} → {md['age_to']:.1f}",body),
            Paragraph(f"{md['years']:.1f}",body)])
    t=Table(rows,colWidths=[0.8*cm,4.5*cm,2.8*cm,2.8*cm,2.5*cm,1.4*cm])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),INDIGO),
        ("TEXTCOLOR",(0,0),(-1,0),CREAM),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("FONTSIZE",(0,0),(-1,0),9),("LINEBELOW",(0,0),(-1,0),1,GOLD),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[white,GREY_LT]),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6),
        ("LEFTPADDING",(0,0),(-1,-1),8)]))
    flow.append(t)
    flow.append(PageBreak())

    # ─── CHAR DASHA + SAHAMS + ARGALA + ECLIPSE + TRANSIT FORECAST ───
    try:
        from char_dasha import char_dasha
        cd_timeline=char_dasha(chart)
        flow.append(to_para("CHAR DASHA — Jaimini Sign-Based Timeline",h1))
        flow.append(to_para("Sign-period dasha system from Jaimini Sutras",h1_sub))
        rows=[["#","SIGN","LORD","LORD POS","FROM","TO","YRS","AGES"]]
        for i,d in enumerate(cd_timeline,1):
            rows.append([str(i),d["sign"],d["lord"],d["lord_position"],
                         d["start"].strftime("%Y-%m"),d["end"].strftime("%Y-%m"),
                         f"{d['years']}",f"{d['age_from']:.0f}-{d['age_to']:.0f}"])
        t=Table(rows,colWidths=[0.8*cm,2.6*cm,2.0*cm,2.6*cm,2.0*cm,2.0*cm,1.2*cm,2.0*cm])
        t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),INDIGO),
            ("TEXTCOLOR",(0,0),(-1,0),CREAM),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
            ("FONTSIZE",(0,0),(-1,-1),8),("LINEBELOW",(0,0),(-1,0),1,GOLD),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[white,GREY_LT]),
            ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
            ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5)]))
        flow.append(t)
        flow.append(PageBreak())
    except Exception as exc:
        print(f"[char_dasha] WARNING: {exc}")

    try:
        if not SHOW["sahams"]: raise _Skip("disabled in SHOW")
        from sahams import compute_sahams
        sahs=compute_sahams(chart)
        flow.append(to_para("SAHAMS — 28 Sensitive Points (Tajik tradition)",h1))
        flow.append(to_para("Calculated longitudes for specific life themes",h1_sub))
        rows=[["SAHAM","SIGN","DEG","HOUSE","LORD"]]
        for name,data in sahs.items():
            rows.append([name,data["sign"],f"{data['deg']:.2f}°",f"H{data['house']}",data["lord"]])
        t=Table(rows,colWidths=[5.5*cm,3.0*cm,1.8*cm,1.5*cm,2.0*cm])
        t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),INDIGO),
            ("TEXTCOLOR",(0,0),(-1,0),CREAM),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
            ("FONTSIZE",(0,0),(-1,-1),8),("LINEBELOW",(0,0),(-1,0),1,GOLD),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[white,GREY_LT]),
            ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
            ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4)]))
        flow.append(t)
        flow.append(PageBreak())
    except Exception as exc:
        print(f"[sahams] WARNING: {exc}")

    try:
        if not SHOW["eclipse"]: raise _Skip("disabled in SHOW")
        from eclipse_impact import upcoming_eclipses_impact
        ec=upcoming_eclipses_impact(chart, years_ahead=5)
        flow.append(to_para("ECLIPSE IMPACT — Next 5 Years",h1))
        flow.append(to_para("Solar/Lunar eclipses + their impact on natal chart",h1_sub))
        if ec:
            for e in ec[:8]:
                imp_color="#c0392b" if "VERY HIGH" in e["impact_level"] or "HIGH" in e["impact_level"] else "#5a5a5a"
                flow.append(to_para(
                    f"<b>{e['type']} eclipse — {e['datetime']}</b> &nbsp;"
                    f"<font color='{imp_color}'><b>[{e['impact_level']}]</b></font><br/>"
                    f"&nbsp;&nbsp;Falls in House {e['house_sun']} ({e['house_sun_theme']}) &bull; "
                    f"distance from natal Moon: {e['distance_from_natal_moon']}°",body_small))
                flow.append(Spacer(1,0.15*cm))
        else:
            flow.append(to_para("No major eclipses calculable in this window.",body_small))
        flow.append(PageBreak())
    except Exception as exc:
        print(f"[eclipse] WARNING: {exc}")

    try:
        if not SHOW["thirty_day"]: raise _Skip("disabled in SHOW")
        from transit_forecast import forecast_period
        cur=dt.datetime.now()
        fc=forecast_period(chart, cur, 30)
        flow.append(to_para("30-DAY FORECAST — Day-by-Day",h1))
        flow.append(to_para(f"Daily prediction starting {cur.strftime('%Y-%m-%d')}",h1_sub))
        rows=[["DATE","SCORE","VERDICT","DASHA","NAKSHATRA"]]
        for f in fc:
            rows.append([f["date"][:11],f"{f['score']:+d}",f["verdict"][:18],
                         f["md_ad"][:15],f["panchanga"]["nakshatra"][:12]])
        t=Table(rows,colWidths=[2.6*cm,1.5*cm,3.5*cm,3.5*cm,3.0*cm])
        t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),INDIGO),
            ("TEXTCOLOR",(0,0),(-1,0),CREAM),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
            ("FONTSIZE",(0,0),(-1,-1),7),("LINEBELOW",(0,0),(-1,0),1,GOLD),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[white,GREY_LT]),
            ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
            ("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3)]))
        flow.append(t)
        flow.append(PageBreak())
    except Exception as exc:
        print(f"[transit_forecast] WARNING: {exc}")

    # ─── TIER 5: TARA CHAKRA + FULL SHADBALA + VIMSHOPAKA + TRI-PATAKI ───
    try:
        if not SHOW["tara_chakra"]: raise _Skip("disabled in SHOW")
        from tara_chakra import tara_chakra_summary
        tc=tara_chakra_summary(chart)
        if tc:
            flow.append(to_para("TARA CHAKRA — Full Nakshatra Reading",h1))
            flow.append(to_para("Deity, Gana, Yoni, Nadi, Body Part, Element of Janma Nakshatra",h1_sub))
            for k in ["name","number","lord","pada","deity","gana","yoni","nadi","mukha","direction","symbol","body_part","color","element"]:
                if k in tc:
                    flow.append(to_para(f"&nbsp;&bull; <b>{k.replace('_',' ').title()}:</b> {tc[k]}",body_small))
            flow.append(Spacer(1,0.3*cm))
            flow.append(to_para(f"<i>{tc['interpretation']}</i>",body_small))
            flow.append(PageBreak())
    except Exception as exc:
        print(f"[tara_chakra] WARNING: {exc}")

    try:
        if not SHOW["full_shadbala"]: raise _Skip("disabled in SHOW")
        from shadbala_full import compute_shadbala_full
        sbf=compute_shadbala_full(chart)
        flow.append(to_para("FULL SHADBALA — 30+ Sub-Components",h1))
        flow.append(to_para("Sthana + Kala + Dig + Cheshta + Naisargika + Drik (BPHS Ch. 27)",h1_sub))
        rows=[["Planet","Sthana","Kala","Dig","Cheshta","Naisarg","Drik","Total Rupas","Ratio","Status"]]
        for p,b in sbf.items():
            stt="STRONG" if b["is_strong"] else "weak"
            rows.append([p,f"{b['sthana_bala']:.0f}",f"{b['kala_bala']:.0f}",f"{b['dig_bala']:.0f}",
                         f"{b['cheshta_bala']:.0f}",f"{b['naisargika_bala']:.0f}",f"{b['drik_bala']:.0f}",
                         f"{b['total_rupas']:.2f}",f"{b['ratio']:.2f}",stt])
        t=Table(rows,colWidths=[1.7*cm,1.2*cm,1.2*cm,1.0*cm,1.4*cm,1.5*cm,1.0*cm,1.7*cm,1.2*cm,1.5*cm])
        t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),INDIGO),
            ("TEXTCOLOR",(0,0),(-1,0),CREAM),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
            ("FONTSIZE",(0,0),(-1,-1),7),("LINEBELOW",(0,0),(-1,0),1,GOLD),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[white,GREY_LT]),
            ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
            ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4)]))
        flow.append(t)
        flow.append(PageBreak())
    except Exception as exc:
        print(f"[shadbala_full] WARNING: {exc}")

    try:
        if not SHOW["vimshopaka"]: raise _Skip("disabled in SHOW")
        from vimshopaka_bala import compute_vimshopaka
        vp=compute_vimshopaka(chart)
        flow.append(to_para("VIMSHOPAKA BALA — Varga-Based Strength (out of 20)",h1))
        flow.append(to_para("Composite strength across 10 vargas (Dasavarga)",h1_sub))
        rows=[["Planet","Total /20","Ratio","Verdict"]]
        for p,b in vp.items():
            rows.append([p,f"{b['total_vimshopaka']:.2f}",f"{b['ratio']:.2f}",b["verdict"]])
        t=Table(rows,colWidths=[2.5*cm,2.5*cm,2.0*cm,5.0*cm])
        t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),INDIGO),
            ("TEXTCOLOR",(0,0),(-1,0),CREAM),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
            ("FONTSIZE",(0,0),(-1,-1),9),("LINEBELOW",(0,0),(-1,0),1,GOLD),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[white,GREY_LT]),
            ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
            ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5)]))
        flow.append(t)
        flow.append(PageBreak())
    except Exception as exc:
        print(f"[vimshopaka] WARNING: {exc}")

    try:
        if not SHOW["tri_pataki"]: raise _Skip("disabled in SHOW")
        from tri_pataki_chakra import tri_pataki
        tp=tri_pataki(chart)
        if tp:
            flow.append(to_para("TRI-PATAKI CHAKRA — Today's Transit Grid",h1))
            flow.append(to_para("Each planet's Tara strength relative to natal Moon nakshatra",h1_sub))
            rows=[["Planet","Current Nakshatra","Offset","Tara Type","Verdict"]]
            for p,g in tp.items():
                rows.append([p,g["current_nak"],str(g["offset_from_natal_moon"]),
                             g["tara_type"],g["verdict"]])
            t=Table(rows,colWidths=[2.0*cm,4.0*cm,1.8*cm,2.8*cm,2.5*cm])
            t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),INDIGO),
                ("TEXTCOLOR",(0,0),(-1,0),CREAM),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
                ("FONTSIZE",(0,0),(-1,-1),8),("LINEBELOW",(0,0),(-1,0),1,GOLD),
                ("ROWBACKGROUNDS",(0,1),(-1,-1),[white,GREY_LT]),
                ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
                ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5)]))
            flow.append(t)
            flow.append(PageBreak())
    except Exception as exc:
        print(f"[tri_pataki] WARNING: {exc}")

    try:
        if not SHOW["varshaphala_internal"]: raise _Skip("disabled in SHOW")
        from varshaphala_dashas import annual_dashas_summary
        cur_year=dt.datetime.now().year
        vad=annual_dashas_summary(chart, cur_year)
        if "error" not in vad:
            flow.append(to_para("VARSHAPHALA INTERNAL DASHAS",h1))
            flow.append(to_para(f"Mudda + Patyayini for year {cur_year}",h1_sub))
            flow.append(to_para(f"<b>Annual Lagna Lord:</b> {vad['annual_lagna_lord']}",body))
            flow.append(to_para(f"<b>Solar Return:</b> {vad['solar_return']}",body))
            flow.append(Spacer(1,0.3*cm))
            flow.append(to_para("<b>MUDDA DASHA (Vimshottari-style year-sub-dasha):</b>",body))
            for d in vad["mudda_dasha"]:
                flow.append(to_para(
                    f"&nbsp;&bull; {d['lord']:10s} &nbsp; "
                    f"{d['start'].strftime('%Y-%m-%d')} → {d['end'].strftime('%Y-%m-%d')} ({d['days']:.0f} days)",
                    body_small))
            flow.append(Spacer(1,0.3*cm))
            flow.append(to_para("<b>PATYAYINI DASHA (strength-proportional):</b>",body))
            for d in vad["patyayini_dasha"]:
                flow.append(to_para(
                    f"&nbsp;&bull; {d['planet']:10s} (str={d['strength']}) &nbsp; "
                    f"{d['start'].strftime('%Y-%m-%d')} → {d['end'].strftime('%Y-%m-%d')} ({d['days']:.0f} days)",
                    body_small))
            flow.append(PageBreak())
    except Exception as exc:
        print(f"[varshaphala_dashas] WARNING: {exc}")

    # ─── JAIMINI DASHA SYSTEMS — 5 advanced rashi-based dashas ───
    try:
        if not SHOW["jaimini_dashas"]: raise _Skip("disabled in SHOW")
        from dasha_systems_full import all_advanced_dashas
        ad=all_advanced_dashas(chart)
        flow.append(to_para("JAIMINI DASHA SYSTEMS",h1))
        flow.append(to_para("5 advanced rashi-based timelines (BPHS Ch. 50-52, Jaimini Sutras)",h1_sub))
        flow.append(to_para(
            "These five dasha systems supplement Vimshottari with rashi-based timing. "
            "Kalachakra reveals the soul's 100-year sweep; Shoola/Sthira/Drig give house-themed timing; "
            "Niryana Shoola tracks longevity-windows via Markesha planets.",body))
        flow.append(Spacer(1,0.3*cm))
        DASHA_DISPLAY_NAMES={
            "kalachakra":"KALACHAKRA DASHA (Wheel of Time, ~100 years)",
            "shoola":"SHOOLA DASHA (Jaimini, seeded on 7H from Lagna)",
            "sthira":"STHIRA DASHA (Fixed, starts at Lagna)",
            "drig":"DRIG DASHA (Aspect-based, seeded on 9H from Atmakaraka)",
            "niryana_shoola":"NIRYANA SHOOLA (Longevity / Markesha-watch)",
        }
        for key,timeline in ad.items():
            display=DASHA_DISPLAY_NAMES.get(key,key.upper())
            flow.append(to_para(f"<b>{display}</b>",h3))
            rows=[["SIGN","LORD","START","END","YEARS","AGE"]]
            for d in timeline[:8]:
                rows.append([
                    Paragraph(d["sign"],body_small),
                    Paragraph(d["lord"],body_small),
                    Paragraph(d["start"].strftime("%Y-%m-%d"),body_small),
                    Paragraph(d["end"].strftime("%Y-%m-%d"),body_small),
                    Paragraph(f"{d['years']:.1f}y",body_small),
                    Paragraph(f"{d['age_from']:.0f}-{d['age_to']:.0f}",body_small),
                ])
            t=Table(rows,colWidths=[2.5*cm,2.0*cm,2.5*cm,2.5*cm,1.5*cm,2.0*cm])
            t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),INDIGO),
                ("TEXTCOLOR",(0,0),(-1,0),CREAM),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
                ("FONTSIZE",(0,0),(-1,-1),8),("LINEBELOW",(0,0),(-1,0),1,GOLD),
                ("ROWBACKGROUNDS",(0,1),(-1,-1),[white,GREY_LT]),
                ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
                ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4)]))
            flow.append(t)
            flow.append(Spacer(1,0.25*cm))
        flow.append(PageBreak())
    except Exception as exc:
        print(f"[jaimini_dashas_full] WARNING: {exc}")

    # ─── PRESENT MOMENT SYNTHESIS — what's happening RIGHT NOW ───
    try:
        from present_moment import present_moment_reading
        pm=present_moment_reading(chart)
        flow.append(to_para("PRESENT MOMENT — WHAT'S HAPPENING RIGHT NOW",h1))
        flow.append(to_para(f"Synthesis as of {pm['as_of']} | Age {pm['age']}",h1_sub))

        # Client revision: predictions-only, table format (no raw technical dump).
        flow.extend(explainer(
            "Your <b>'right now' snapshot</b> — where you stand in life's bigger cycles today and what "
            "the current phase is bringing. The table lists the live influences acting on you now; the "
            "<b>bottom line</b> at the end is the summary reading.","RIGHT NOW"))

        # one compact context line — which periods are running
        parts=[]
        for lvl,d in pm.get("dashas",{}).items():
            if isinstance(d,dict): parts.append(f"<b>{lvl}</b> {d['lords']}")
        if parts:
            flow.append(to_para("Active periods &nbsp;—&nbsp; "+" &nbsp;·&nbsp; ".join(parts),body_small))
            flow.append(Spacer(1,0.3*cm))

        # predictions table — what each live influence MEANS for the client
        rows=[["WHAT'S ACTIVE NOW","WHAT IT MEANS FOR YOU"]]
        vp=pm.get("varshaphala",{})
        if isinstance(vp,dict) and "muntha_house" in vp:
            rows.append([to_para("This year's focus",body_small),
                         to_para(f"The year centres on <b>House {vp['muntha_house']}</b> "
                                 f"({vp.get('muntha_sign','')}) matters, led by {vp.get('year_lord','')}.",body_small)])
        ss=pm.get("sade_sati")
        if ss and str(ss)!="?":
            rows.append([to_para("Saturn's 7.5-year cycle",body_small),to_para(str(ss),body_small)])
        for t in pm.get("active_transits",[]):
            rows.append([to_para(f"<font color='#c0392b'><b>[{t.get('severity','')}]</b></font> influence",body_small),
                         to_para(t.get("label",""),body_small)])
        if len(rows)>1:
            tbl=Table(rows,colWidths=[5.0*cm,8.5*cm])
            tbl.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),INDIGO),
                ("TEXTCOLOR",(0,0),(-1,0),CREAM),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
                ("FONTSIZE",(0,0),(-1,0),9),("LINEBELOW",(0,0),(-1,0),1,GOLD),
                ("ROWBACKGROUNDS",(0,1),(-1,-1),[white,GREY_LT]),
                ("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),8),
                ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6)]))
            flow.append(tbl)
            flow.append(Spacer(1,0.4*cm))

        # bottom-line prediction in plain words
        if pm.get("synthesis"):
            flow.extend(explainer(pm["synthesis"],"THE BOTTOM LINE"))
        flow.append(PageBreak())
    except Exception as exc:
        print(f"[present_moment] WARNING: {exc}")
        import traceback; traceback.print_exc()

    # ─── MUHURTA RECOMMENDATIONS — 5 best dates per major event-type ───
    try:
        if not SHOW["muhurta_windows"]: raise _Skip("disabled in SHOW")
        from muhurta_extended import ALL_MUHURTAS
        flow.append(to_para("MUHURTA RECOMMENDATIONS — UPCOMING WINDOWS",h1))
        flow.append(to_para("Best 5 upcoming dates for each of 14 major life events (next 90 days)",h1_sub))
        flow.append(to_para(
            "Each rite/event below has its own classical rules (tithi + nakshatra + vara + paksha). "
            "We scan the next 90 days and rank each by score. The top 5 candidates per event are listed.",body))
        flow.append(Spacer(1,0.3*cm))
        MUHURTA_LABELS={
            "gemstone":"Gemstone Wearing (Ratna-Dharana)",
            "griha-pravesh":"House-Warming (Griha Pravesh)",
            "garbhadhana":"Conception (Garbhadhana)",
            "namakarana":"Naming Ceremony",
            "upanayana":"Sacred-Thread Initiation (Upanayana)",
            "annaprashana":"First Feeding (Annaprashana)",
            "chudakarana":"First Haircut (Chudakarana)",
            "vidyarambha":"Education Start (Vidyarambha)",
            "vahana":"Vehicle Purchase",
            "bhumi":"Land / Property Purchase",
            "vyavahara":"Court / Litigation",
            "rajyabhisheka":"Promotion / Coronation",
            "rina":"Loan / Borrowing",
            "dahana":"Cremation / Funeral",
        }
        today_dt=dt.datetime.now()
        for evt_key,fn in ALL_MUHURTAS.items():
            label=MUHURTA_LABELS.get(evt_key,evt_key.title())
            best_dates=[]
            for offset in range(0,90):
                cand=today_dt+dt.timedelta(days=offset)
                try:
                    res=fn(chart,cand,_suppress_better=True)
                    best_dates.append((cand,res["score"],res["verdict"]))
                except Exception:
                    continue
            best_dates.sort(key=lambda x:-x[1])
            top5=best_dates[:5]
            flow.append(to_para(f"<b>{label}</b>",h3))
            rows=[["DATE","WEEKDAY","SCORE","VERDICT"]]
            for d,s,v in top5:
                rows.append([
                    Paragraph(d.strftime("%Y-%m-%d"),body_small),
                    Paragraph(d.strftime("%A"),body_small),
                    Paragraph(f"{s}/100",body_small),
                    Paragraph(v,body_small),
                ])
            t=Table(rows,colWidths=[3.2*cm,2.8*cm,2.0*cm,3.2*cm])
            t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),INDIGO),
                ("TEXTCOLOR",(0,0),(-1,0),CREAM),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
                ("FONTSIZE",(0,0),(-1,-1),8),("LINEBELOW",(0,0),(-1,0),1,GOLD),
                ("ROWBACKGROUNDS",(0,1),(-1,-1),[white,GREY_LT]),
                ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
                ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4)]))
            flow.append(t)
            flow.append(Spacer(1,0.2*cm))
        flow.append(PageBreak())
    except Exception as exc:
        print(f"[muhurta_extended] WARNING: {exc}")

    # ─── SPECIAL LAGNAS ───
    try:
        if not SHOW["special_lagnas"]: raise _Skip("disabled in SHOW")
        from special_lagnas import all_special_lagnas
        sl=all_special_lagnas(chart)
        flow.append(to_para("SPECIAL LAGNAS — 8 Ascendants for Layered Reading",h1))
        flow.append(to_para("Each Lagna reveals a specific life domain (BPHS Ch. 4-5)",h1_sub))
        for key,data in sl.items():
            if data:
                flow.append(to_para(
                    f"<b>{data['name']}</b> — {data['rasi']} (lord: {data.get('lord','?')})<br/>"
                    f"<font color='#5d2e8c' size='9'><i>Purpose: {data['purpose']}</i></font>",
                    body_small))
                flow.append(Spacer(1,0.15*cm))
        flow.append(PageBreak())
    except Exception as exc:
        print(f"[special_lagnas] WARNING: {exc}")

    # ─── DOSHAS + CANCELLATIONS ───
    try:
        from dosha_cancellations import all_doshas_summary
        ds=all_doshas_summary(chart)
        flow.append(to_para("DOSHAS — Detection + Classical Cancellations",h1))
        flow.append(to_para("Manglik, Kaal Sarpa, etc. — with classical exception rules",h1_sub))
        for name,d in ds.items():
            if d is None: continue
            flow.append(to_para(f"<b>{name.upper()}:</b> {d.get('verdict','?')}",body))
            if d.get("cancellations"):
                for c in d["cancellations"]:
                    flow.append(to_para(f"&nbsp;&bull; <font color='#0a7a3a'>{c}</font>",body_small))
            flow.append(Spacer(1,0.2*cm))
        flow.append(PageBreak())
    except Exception as exc:
        print(f"[doshas] WARNING: {exc}")

    # ─── SPOUSE INFERENCE ───
    try:
        from spouse_inference import infer_spouse
        sp=infer_spouse(chart)
        flow.append(to_para("SPOUSE INFERENCE — Comprehensive Partner Description",h1))
        flow.append(to_para("D1 + D9 + Venus + DK + Upapada combined",h1_sub))
        flow.extend(explainer(
            "This is a <b>composite sketch</b> of your life-partner and marriage, cross-read from five "
            "independent layers of the chart. No single line is the whole picture — read them together as "
            "one portrait. The table gives the technical anchors; the lines below translate them into a "
            "real description of the person, their background and the likely timing."))
        rows=[
            ["Indicator","Value"],
            ["7th House Sign", sp["h7_sign"]],
            ["7th House Lord", f"{sp['h7_lord']} (in House {sp['h7_lord_house']})"],
            ["Darakaraka (Spouse Karaka)", sp["darakaraka"]],
            ["DK in D9 (Navamsa)", str(sp["darakaraka_in_d9"])],
            ["D9 7th House Sign", str(sp["d9_7th_sign"])],
            ["Upapada Lagna (UL)", sp["upapada_lagna"]],
        ]
        t=Table(rows,colWidths=[5.0*cm,8.0*cm])
        t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),INDIGO),
            ("TEXTCOLOR",(0,0),(-1,0),CREAM),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
            ("FONTSIZE",(0,0),(-1,-1),9),("LINEBELOW",(0,0),(-1,0),1,GOLD),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[white,GREY_LT]),
            ("VALIGN",(0,0),(-1,-1),"MIDDLE"),("LEFTPADDING",(0,0),(-1,-1),8),
            ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5)]))
        flow.append(t)
        flow.append(Spacer(1,0.4*cm))
        flow.append(to_para(f"<b>Personality:</b> {sp['personality']}",body))
        flow.append(to_para(f"<b>Karmic archetype:</b> {sp['dk_archetype']}",body))
        flow.append(to_para(f"<b>Appearance:</b> {sp['appearance']}",body))
        flow.append(to_para(f"<b>Background:</b> {sp['background']}",body))
        flow.append(to_para(f"<b>Career field:</b> {sp['career_field']}",body))
        flow.append(to_para(f"<b>Marriage window:</b> {sp['marriage_window']}",body))
        flow.append(PageBreak())
    except Exception as exc:
        print(f"[spouse] WARNING: {exc}")

    # ─── NUMEROLOGY (advanced multi-paradigm engine) ───
    try:
        from engine.numerology_engine import compute_numerology_report
        _b=chart["birth"]
        _nr=compute_numerology_report(chart.get("name",""),
              f"{_b['year']:04d}-{_b['month']:02d}-{_b['day']:02d}",
              dt.datetime.now().date().isoformat())["calculations"]
        tc=_nr["tamil_chaldean"]; py=_nr["pythagorean_triad"]; ls=_nr["lo_shu_grid"]; cyc=_nr["temporal_cycles"]
        flow.append(to_para("NUMEROLOGY — Multi-Paradigm Analysis",h1))
        flow.append(to_para("Tamil-Chaldean + Pythagorean + Lo Shu grid + personal cycles",h1_sub))
        flow.append(to_para(f"<b>Vidhi (Driver):</b> {tc['vidhi_number']} ({tc['vidhi_planet']}) &nbsp;&bull;&nbsp; "
                            f"<b>Bhagya (Destiny):</b> {tc['bhagya_number']} ({tc['bhagya_planet']})",body))
        flow.append(to_para(f"<b>Expression:</b> {py['expression_number']} &nbsp;&bull;&nbsp; "
                            f"<b>Soul Urge:</b> {py['soul_urge_number']} &nbsp;&bull;&nbsp; "
                            f"<b>Personality:</b> {py['personality_number']}",body))
        if py.get('soul_urge_note'):
            flow.append(to_para(f"<i>{py['soul_urge_note']}</i>",body_small))
        flow.append(Spacer(1,0.25*cm))
        flow.append(to_para(f"<b>Personal Year {cyc['personal_year']}</b> ({cyc.get('target_date','')}): "
                            f"{cyc.get('personal_year_meaning','')} &nbsp;(Month {cyc.get('personal_month','?')}, "
                            f"Day {cyc.get('personal_day','?')})",body))
        flow.append(Spacer(1,0.25*cm))
        flow.append(to_para("<b>Lo Shu Grid</b> — number frequencies (cream = present, doubled = stronger; missing = life lessons):",body))
        _counts={int(k):int(v) for k,v in (ls.get("digit_counts",{}) or {}).items()}
        _LAYOUT=[[4,9,2],[3,5,7],[8,1,6]]
        _grid=[[Paragraph(f"<b>{str(num)*_counts.get(num,0) if _counts.get(num,0) else num}</b>",body)
                for num in _row] for _row in _LAYOUT]
        _gt=Table(_grid,colWidths=[1.7*cm]*3,rowHeights=[1.1*cm]*3,hAlign="LEFT")
        _gst=[("GRID",(0,0),(-1,-1),0.8,GOLD),("ALIGN",(0,0),(-1,-1),"CENTER"),("VALIGN",(0,0),(-1,-1),"MIDDLE")]
        for _ri,_row in enumerate(_LAYOUT):
            for _ci,num in enumerate(_row):
                _gst.append(("BACKGROUND",(_ci,_ri),(_ci,_ri), CREAM if _counts.get(num,0)>0 else white))
        _gt.setStyle(TableStyle(_gst))
        flow.append(_gt)
        flow.append(to_para(f"<b>Missing:</b> {', '.join(str(m) for m in ls.get('missing_numbers',[])) or 'none'}",body_small))
        flow.append(Spacer(1,0.25*cm))
        flow.append(to_para(f"<b>Lucky days:</b> {', '.join(tc.get('lucky_days',[]))} &nbsp;&bull;&nbsp; "
                            f"<b>Direction:</b> {tc.get('lucky_direction','')} &nbsp;&bull;&nbsp; "
                            f"<b>Dates:</b> {', '.join(str(d) for d in tc.get('lucky_dates',[]))}",body_small))
        flow.append(to_para(f"<b>Colour:</b> {tc.get('lucky_color','')} &nbsp;&bull;&nbsp; "
                            f"<b>Gemstone:</b> {tc.get('lucky_gemstone','')} &nbsp;&bull;&nbsp; "
                            f"<b>Deity:</b> {tc.get('deity','')}",body_small))
        flow.append(PageBreak())
    except Exception as exc:
        print(f"[numerology] WARNING: {exc}")
        import traceback; traceback.print_exc()

    # ─── SHADBALA + JAIMINI + LONGEVITY + MEDICAL + LAL KITAB + NADI ───
    try:
        from engine.shadbala import compute_shadbala
        sb=compute_shadbala(chart)
        flow.append(to_para("SHADBALA — PLANETARY STRENGTHS",h1))
        flow.append(to_para("Six-fold classical strength calculation per BPHS Ch. 27",h1_sub))
        flow.extend(explainer(
            "Think of this as each planet's <b>fitness score</b>. Shadbala measures how much real "
            "power a planet has to deliver its results — from where it sits, the birth time, its "
            "direction and its motion. Read the <b>Total</b> column first: higher means that planet "
            "has more say in your life, and <b>STRONG</b> means it can fully give its results. The "
            "six columns before it simply show where that strength comes from."))
        rows=[["Planet","Sthana","Dig","Kala","Cheshta","Naisargika","Drik","Total","Status"]]
        for p,b in sb.items():
            stt="STRONG" if b["is_strong"] else "weak"
            rows.append([p,f"{b['sthana']:.0f}",f"{b['dig']:.0f}",f"{b['kala']:.0f}",
                         f"{b['cheshta']:.0f}",f"{b['naisargika']:.1f}",f"{b['drik']:.0f}",
                         f"{b['total_rupas']:.2f}",stt])
        t=Table(rows,colWidths=[2.0*cm,1.5*cm,1.3*cm,1.3*cm,1.5*cm,1.7*cm,1.3*cm,1.5*cm,1.6*cm])
        t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),INDIGO),
            ("TEXTCOLOR",(0,0),(-1,0),CREAM),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
            ("FONTSIZE",(0,0),(-1,-1),8),("LINEBELOW",(0,0),(-1,0),1,GOLD),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[white,GREY_LT]),
            ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
            ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5)]))
        flow.append(t)
        flow.append(PageBreak())
    except Exception as exc:
        print(f"[shadbala] WARNING: {exc}")

    try:
        from jaimini_full import jaimini_summary
        js=jaimini_summary(chart)
        flow.append(to_para("JAIMINI ANALYSIS — Padas, Karakamsa, Upapada",h1))
        flow.append(to_para("Soul-purpose + spouse + arudha indicators (Jaimini Sutras)",h1_sub))
        flow.append(to_para("<b>Chara Karakas (sorted by degree):</b>",body))
        for k in js["chara_karakas"]:
            flow.append(to_para(f"&nbsp;&bull; <b>{k['role']}</b> — {k['planet']} @ {k['degree']}°",body_small))
        flow.append(Spacer(1,0.3*cm))
        flow.append(to_para(f"<b>Upapada Lagna (UL):</b> {js['upapada_lagna_UL']} — primary spouse indicator",body_small))
        flow.append(to_para(f"<b>Darapada (A7):</b> {js['darapada_A7']} — public face of marriage",body_small))
        flow.append(to_para(f"<b>Karakamsa in D9:</b> {js['karakamsa_in_d9']} — soul's sign",body_small))
        flow.append(Spacer(1,0.3*cm))
        flow.append(to_para("<b>All 12 Arudha Padas:</b>",body))
        for h_label,sign in js["arudha_padas"].items():
            flow.append(to_para(f"&nbsp;&bull; {h_label}: {sign}",body_small))
        flow.append(PageBreak())
    except Exception as exc:
        print(f"[jaimini] WARNING: {exc}")

    try:
        from longevity_ayurdaya import longevity_analysis
        la=longevity_analysis(chart)
        flow.append(to_para("LONGEVITY (AYURDAYA) — Three-Fold Calculation",h1))
        flow.append(to_para("Markesha + Pinda + Naisargika lifespan estimation (BPHS Ch. 90)",h1_sub))
        flow.extend(explainer(
            "These numbers are <b>not</b> a prediction of how long you will live — no honest astrologer "
            "claims that. Ayurdaya is a classical <b>vitality estimate</b>, built three different ways "
            "and then averaged, used to spot the life-phases that need extra care for health and energy. "
            "Read the years as a strength-of-constitution indicator, not a deadline. The Markesha planets "
            "below simply flag the periods where rest, check-ups and caution matter most."))
        flow.append(to_para(f"<b>Naisargika Ayurdaya:</b> {la['naisargika_years']} years",body))
        flow.append(to_para(f"<b>Pinda Ayurdaya:</b> {la['pinda_years']} years",body))
        flow.append(to_para(f"<b>Average estimate:</b> {la['average_years']} years &nbsp; &bull; <b>{la['category']}</b>",body))
        flow.append(Spacer(1,0.3*cm))
        flow.append(to_para("<b>Markesha (death-causing) planets:</b>",body))
        for m in la["markesha_planets"]:
            primary="PRIMARY" if m["primary"] else "secondary"
            flow.append(to_para(f"&nbsp;&bull; <b>{m['planet']}</b> — {m['type']} ({primary})",body_small))
        flow.append(Spacer(1,0.3*cm))
        flow.append(to_para(f"<i>{la['interpretation']}</i>",body_small))
        flow.append(to_para(
            "<font color='#5a5a5a' size='8'><i>Note: Ayurdaya calculation is sensitive and approximate. "
            "Vedic tradition emphasizes spiritual preparation over anxiety about timing.</i></font>",body_small))
        flow.append(PageBreak())
    except Exception as exc:
        print(f"[longevity] WARNING: {exc}")

    try:
        from medical_astrology import medical_analysis
        ma=medical_analysis(chart)
        flow.append(to_para("MEDICAL ASTROLOGY — Body & Health Predispositions",h1))
        flow.append(to_para("Per-planet & per-house disease tendencies",h1_sub))
        flow.extend(explainer(
            "This is about <b>tendencies, not diagnoses</b>. Your chart leans toward a certain body-type "
            "(constitution) and points to a few areas worth extra attention over life — think of it as a "
            "'where to be proactive' map. It does <b>not</b> mean these problems will happen; it means good "
            "diet, awareness and timely check-ups in these areas pay off. Always read it alongside a real doctor."))
        flow.append(to_para(f"<b>Constitution:</b> {ma['constitution']}",body))
        flow.append(Spacer(1,0.2*cm))
        if ma["vulnerable_houses"]:
            flow.append(to_para("<b>Vulnerable houses (malefics in dusthana):</b>",body))
            for v in ma["vulnerable_houses"]:
                flow.append(to_para(
                    f"&nbsp;&bull; <b>House {v['house']}</b> — {v['body_area']}<br/>"
                    f"&nbsp;&nbsp;&nbsp;<font color='#c0392b'>Malefics here: {', '.join(v['malefics'])}</font>",body_small))
        if ma["disease_predispositions"]:
            flow.append(Spacer(1,0.3*cm))
            flow.append(to_para("<b>Disease predispositions:</b>",body))
            for d in ma["disease_predispositions"]:
                flow.append(to_para(
                    f"&nbsp;&bull; <b>{d['planet']}</b> in H{d['house']}: {d['diseases']}<br/>"
                    f"&nbsp;&nbsp;&nbsp;<font color='#5d2e8c'>Affects: {d['affected_area']}</font>",body_small))
        flow.append(PageBreak())
    except Exception as exc:
        print(f"[medical] WARNING: {exc}")

    try:
        from engine.lal_kitab import lal_kitab_summary
        lk=lal_kitab_summary(chart)
        flow.append(to_para("LAL KITAB — Karz Analysis & Asleep Planets",h1))
        flow.append(to_para("Lal Kitab tradition — 7 karmic debt patterns",h1_sub))
        flow.extend(explainer(
            "Lal Kitab reads the chart like a <b>ledger of inherited karmic 'debts' (karz)</b> — patterns "
            "carried from family or past actions that quietly drain one area of life until they are settled. "
            "The good news: each debt has a simple, practical remedy (a donation, an act of service, an "
            "offering) — no expensive rituals. 'Asleep' planets are strengths you already have but aren't "
            "using yet; small physical actions 'wake' them."))
        if lk["active_karz"]:
            flow.append(to_para(f"<b>Active karz patterns ({len(lk['active_karz'])}):</b>",body))
            for k in lk["active_karz"]:
                flow.append(to_para(f"<b>{k['karz']}</b>",body))
                flow.append(to_para(f"<font color='#5d2e8c' size='9'>Trigger: {k['trigger']}</font>",body_small))
                flow.append(to_para(f"<font color='#0a7a3a' size='9'>Remedy: {k['remedy']}</font>",body_small))
                flow.append(Spacer(1,0.2*cm))
        else:
            flow.append(to_para("No major karz patterns detected.",body))
        if lk["asleep_planets"]:
            flow.append(to_para(f"<b>Asleep (sote hue) planets:</b> {', '.join(lk['asleep_planets'])}",body_small))
            flow.append(to_para(
                "<i>Asleep planets need 'waking' via Lal Kitab remedies — physical actions like donations, hospitality, water-offerings.</i>",
                body_small))
        flow.append(PageBreak())
    except Exception as exc:
        print(f"[lal_kitab] WARNING: {exc}")

    try:
        from nadi_jyotish import nadi_analysis
        nj=nadi_analysis(chart)
        flow.append(to_para("NADI JYOTISH — Soul-Purpose Reading",h1))
        flow.append(to_para("Bhrigu Nadi tradition — karmic combinations & soul mission",h1_sub))
        flow.append(to_para(f"<b>Atmakaraka:</b> {nj['atmakaraka_planet']}",body))
        flow.append(to_para(f"<b>Soul Mission:</b> <i>{nj['soul_mission']}</i>",body_small))
        flow.append(Spacer(1,0.2*cm))
        flow.append(to_para(f"<b>Karmic Verdict:</b> {nj['karmic_verdict']}",body_small))
        if nj["nadi_combinations"]:
            flow.append(Spacer(1,0.3*cm))
            flow.append(to_para(f"<b>Significant Nadi combinations ({len(nj['nadi_combinations'])}):</b>",body))
            for n in nj["nadi_combinations"]:
                flow.append(to_para(f"<b>{n['combination']}</b> in House {n['house']}",body_small))
                flow.append(to_para(f"<i>{n['reading']}</i>",body_small))
                flow.append(Spacer(1,0.15*cm))
        flow.append(PageBreak())
    except Exception as exc:
        print(f"[nadi] WARNING: {exc}")

    try:
        from varshaphala import varshaphala_timeline
        b_v=chart["birth"]
        cur_year=dt.datetime.now().year
        timeline=varshaphala_timeline(chart, cur_year-1, cur_year+10)
        flow.append(to_para("VARSHAPHALA — Year-by-Year Forecast",h1))
        flow.append(to_para("Tajik annual chart system (Solar Return)",h1_sub))
        rows=[["YEAR","ANNUAL LAGNA","MUNTHA H","MUNTHA SIGN","YEAR LORD"]]
        for tl in timeline:
            if "error" in tl: continue
            rows.append([str(tl["year"]),tl["annual_lagna"],f"H{tl['muntha_house']}",tl["muntha_sign"],tl["year_lord"]])
        if len(rows)>1:
            t=Table(rows,colWidths=[2.0*cm,3.5*cm,2.0*cm,3.5*cm,3.0*cm])
            t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),INDIGO),
                ("TEXTCOLOR",(0,0),(-1,0),CREAM),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
                ("FONTSIZE",(0,0),(-1,-1),9),("LINEBELOW",(0,0),(-1,0),1,GOLD),
                ("ROWBACKGROUNDS",(0,1),(-1,-1),[white,GREY_LT]),
                ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
                ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5)]))
            flow.append(t)
        flow.append(PageBreak())
    except Exception as exc:
        print(f"[varshaphala] WARNING: {exc}")

    # ─── TAJIK YOGAS — 16 Persian-tradition Itthasala-family yogas + 5 balas ───
    try:
        from tajik_yogas_16 import detect_all_tajik_yogas, all_balas
        ty=detect_all_tajik_yogas(chart)
        bs=all_balas(chart)
        flow.append(to_para("TAJIK YOGAS — Persian Annual Astrology",h1))
        flow.append(to_para(
            f"{len(ty)} Tajik aspect-yogas detected | "
            f"5 Balas computed (Source: Tajika Neelakanthi, Varshaphal Raman)",h1_sub))
        flow.append(to_para(
            "Tajik tradition uses tighter aspect orbs (12° conj, 9° trine, 7° square, 6° sextile) "
            "and identifies 'Itthasala' (applying) and 'Iisarafa' (separating) family yogas. "
            "These are most relevant during the annual Varshaphala chart.",body))
        flow.append(Spacer(1,0.3*cm))
        if not ty:
            flow.append(to_para("No prominent Tajik yogas in the natal chart aspect-grid.",body))
        for y in ty[:25]:
            sev_stars="★"*y["severity"]+"☆"*(5-y["severity"])
            planets=", ".join(y["planets"])
            rows=[
                [Paragraph(f"<b>{y['name']}</b> &nbsp; <font color='#c9a032'>{sev_stars}</font>",body)],
                [Paragraph(f"<font color='#5d2e8c' size='9'><i>Type: {y['type']} | Planets: {planets}</i></font>",body_small)],
                [Paragraph(y["interpretation"],body)],
            ]
            t=Table(rows,colWidths=[A4[0]-5*cm])
            t.setStyle(TableStyle([
                ("BACKGROUND",(0,0),(-1,-1),CREAM),
                ("LINEBEFORE",(0,0),(0,-1),3,GOLD),
                ("VALIGN",(0,0),(-1,-1),"TOP"),
                ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
                ("LEFTPADDING",(0,0),(-1,-1),12),("RIGHTPADDING",(0,0),(-1,-1),12)]))
            flow.append(t)
            flow.append(Spacer(1,0.15*cm))
        # Tajik Balas table
        flow.append(Spacer(1,0.4*cm))
        flow.append(to_para("<b>TAJIK BALAS — 5 strengths per planet</b>",h3))
        rows=[["Planet","Hadda","Trirashi","Drekkana","Navamsha","Mooladhipati","Total"]]
        for p,bv in bs.items():
            rows.append([p,str(bv["hadda"]),str(bv["trirashi"]),str(bv["drekkana"]),
                         str(bv["navamsha"]),str(bv["mooladhipati"]),str(bv["total"])])
        t=Table(rows,colWidths=[2.0*cm,1.6*cm,1.8*cm,1.8*cm,1.8*cm,2.2*cm,1.6*cm])
        t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),INDIGO),
            ("TEXTCOLOR",(0,0),(-1,0),CREAM),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
            ("FONTSIZE",(0,0),(-1,-1),9),("LINEBELOW",(0,0),(-1,0),1,GOLD),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[white,GREY_LT]),
            ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
            ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5)]))
        flow.append(t)
        flow.append(PageBreak())
    except Exception as exc:
        print(f"[tajik_yogas] WARNING: {exc}")

    # ─── BOOK CORPUS STATISTICS PAGE ───
    try:
        from pathlib import Path as _Path
        import json as _json
        idx_path=_Path(__file__).parent/"book_corpus_index.json"
        xref_path=_Path(__file__).parent/"book_cross_reference.json"
        if idx_path.exists():
            corpus=_json.loads(idx_path.read_text(encoding="utf-8"))
            from collections import Counter
            book_counts=Counter(e["book"] for e in corpus)
            high_q=sum(1 for e in corpus if e.get("quality",0)>=0.6)
            scripts=Counter()
            for e in corpus:
                for s in e.get("scripts",[]):
                    scripts[s]+=1
            flow.append(to_para("CLASSICAL CORPUS — BOOKS THIS ENGINE READS FROM",h1))
            flow.append(to_para(
                f"{len(corpus):,} indexed passages from {len(book_counts)} classical texts | "
                f"{high_q:,} high-quality verses | scripts: {', '.join(scripts.keys())}",h1_sub))
            flow.append(to_para("<b>Books in corpus (by passage count):</b>",body))
            for bk,cnt in book_counts.most_common(25):
                bk_pretty=bk.replace("_"," ").replace("v2","").strip()
                flow.append(to_para(f"&nbsp;&bull; <b>{bk_pretty}</b> — {cnt:,} passages",body_small))
            flow.append(Spacer(1,0.4*cm))
            # Cross-reference matrix
            if xref_path.exists():
                xref=_json.loads(xref_path.read_text(encoding="utf-8"))
                flow.append(to_para("<b>Cross-reference depth (how many books cover each topic):</b>",body))
                sorted_xref=sorted(xref.items(),key=lambda kv:-kv[1]["total_passages"])
                for topic,data in sorted_xref[:25]:
                    topic_pretty=topic.replace("_"," ").title()
                    top_books=", ".join(b[0].replace("_"," ")[:18] for b in data["top_sources"][:3])
                    flow.append(to_para(
                        f"&nbsp;&bull; <b>{topic_pretty}</b>: {data['total_passages']:,} passages from "
                        f"{data['books_covering']} books &nbsp;<font size='7' color='#5a5a5a'>(top: {top_books})</font>",
                        body_small))
            flow.append(PageBreak())
    except Exception as exc:
        print(f"[corpus_stats] WARNING: {exc}")

    # ─── DIVISIONAL CHARTS PAGE — D9 / D10 / D60 ───
    try:
        from divisional_charts import full_varga_analysis
        varga_analysis=full_varga_analysis(chart)
        flow.append(to_para("DIVISIONAL CHARTS — D9 / D10 / D60",h1))
        flow.append(to_para("Navamsa (marriage) · Dashamsa (career) · Shashtiamsa (past karma)",h1_sub))
        for varga_key,data in varga_analysis.items():
            flow.append(to_para(f"<b>{data['varga']}</b> — <i>{data['purpose']}</i>",h2))
            details=[]
            for k,v in data.items():
                if k in ("varga","purpose","interpretation","citations"): continue
                if v is None or v == []: continue
                if isinstance(v,list):
                    details.append(f"<b>{k.replace('_',' ').title()}:</b> {', '.join(str(x) for x in v)}")
                else:
                    details.append(f"<b>{k.replace('_',' ').title()}:</b> {v}")
            for d in details:
                flow.append(to_para(f"&nbsp;&nbsp;&bull; {d}",body_small))
            if data.get("interpretation"):
                flow.append(Spacer(1,0.15*cm))
                flow.append(to_para("<b>Reading:</b>",body_small))
                for n in data["interpretation"]:
                    flow.append(to_para(f"&nbsp;&nbsp;<font color='#1a1d3a'>{n}</font>",body_small))
            # Classical citations from indexed books
            if data.get("citations"):
                flow.append(Spacer(1,0.15*cm))
                books=sorted({c["book"].replace("_"," ").replace("v2","").strip()
                              for c in data["citations"] if c.get("book")})
                flow.append(to_para(
                    "<font color='#5d2e8c' size='8'>Verified in classical corpus: "
                    f"<b>{', '.join(books)}</b></font>",body_small))
            flow.append(Spacer(1,0.4*cm))
        flow.append(PageBreak())
    except Exception as exc:
        print(f"[divisional_charts] WARNING: {exc}")
        import traceback; traceback.print_exc()

    # ─── SADE SATI PAGE — 7.5 year Saturn cycles ───
    try:
        from sade_sati import compute_sade_sati_periods
        sade_periods=compute_sade_sati_periods(chart, years_horizon=80)
        if sade_periods:
            flow.append(to_para("SADE SATI — 7.5 YEAR SATURN CYCLES",h1))
            flow.append(to_para("Saturn transits through 12th, 1st, 2nd from natal Moon",h1_sub))
            b_s=chart["birth"]
            birth_dt_s=dt.datetime(b_s["year"],b_s["month"],b_s["day"])
            today_s=dt.datetime.now()
            sade_rows=[["AGE","PHASE","FROM","TO","DUR","STATUS"]]
            for sp in sade_periods:
                age_start=(sp["start"]-birth_dt_s).days/365.25
                is_now=sp["start"]<=today_s<=sp["end"]
                status="★ NOW" if is_now else "past" if sp["end"]<today_s else "future"
                yrs=sp["duration_days"]/365.25
                sade_rows.append([
                    Paragraph(f"<b>{age_start:.1f}</b>",body_small),
                    Paragraph(sp["phase"][:35],body_small),
                    Paragraph(sp["start"].strftime("%b %Y"),body_small),
                    Paragraph(sp["end"].strftime("%b %Y"),body_small),
                    Paragraph(f"{yrs:.1f}y",body_small),
                    Paragraph(f"<font color='{'#c0392b' if is_now else '#5a5a5a'}'>{status}</font>",body_small),
                ])
            t=Table(sade_rows,colWidths=[1.2*cm,5.5*cm,2.4*cm,2.4*cm,1.5*cm,2.0*cm])
            t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),INDIGO),
                ("TEXTCOLOR",(0,0),(-1,0),CREAM),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
                ("FONTSIZE",(0,0),(-1,0),8),("LINEBELOW",(0,0),(-1,0),1,GOLD),
                ("ROWBACKGROUNDS",(0,1),(-1,-1),[white,GREY_LT]),
                ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
                ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
                ("LEFTPADDING",(0,0),(-1,-1),6)]))
            flow.append(t)
            flow.append(Spacer(1,0.3*cm))
            flow.append(to_para(
                "<i>Sade Sati is the classical 7.5-year Saturn cycle through 12th, 1st, and 2nd houses from natal Moon. "
                "Each phase brings tests, restructuring, and karmic processing. The Peak phase (Saturn ON natal Moon sign) is "
                "typically the most intense; Setting phase (2nd from Moon) is finalisation/consolidation.</i>",
                ParagraphStyle("foot",parent=body_small,textColor=GREY_MD)))
            flow.append(PageBreak())
    except Exception as exc:
        print(f"[sade_sati] WARNING: {exc}")

    # ─── ASPECTS PAGE — Vedic special drishti ───
    try:
        from aspects_engine import detect_significant_aspects
        from book_citation import cite_for_aspect
        aspects=detect_significant_aspects(chart, severity_min=3)
        if aspects:
            flow.append(to_para("VEDIC ASPECTS — DRISHTI ANALYSIS",h1))
            flow.append(to_para("Mars (4-7-8), Jupiter (5-7-9), Saturn (3-7-10), Rahu/Ketu (5-7-9) special aspects",h1_sub))
            for a in sorted(aspects,key=lambda x:-x["severity"]):
                sev_stars="*"*a["severity"]+"."*(5-a["severity"])
                flow.append(to_para(
                    f"<b>{a['aspecting']} (H{a['aspecting_house']})</b> aspects "
                    f"<b>{a['target']} (H{a['target_house']})</b> &nbsp;"
                    f"<font color='#c9a032' size='10'><b>{sev_stars}</b></font>",body))
                flow.append(to_para(f"<font color='#1a1d3a' size='9'>{a['effect']}</font>",body_small))
                flow.append(to_para(f"<font color='#5a5a5a' size='8'>Source: {a['source']}</font>",body_small))
                flow.append(Spacer(1,0.2*cm))
            # Append book citations from corpus
            asp_cits=cite_for_aspect()
            if asp_cits:
                flow.append(Spacer(1,0.3*cm))
                books=sorted({c["book"].replace("_"," ").replace("v2","").strip()
                              for c in asp_cits if c.get("book")})
                flow.append(to_para(
                    "<font color='#5d2e8c' size='8'>Verified in classical corpus: "
                    f"<b>{', '.join(books)}</b></font>",body_small))
            flow.append(PageBreak())
    except Exception as exc:
        print(f"[aspects_engine] WARNING: {exc}")

    # ─── CONJUNCTION ANALYSIS PAGE ───
    try:
        from conjunction_effects import detect_conjunctions
        from book_citation import cite_for_conjunction
        conjs=detect_conjunctions(chart)
        if conjs:
            flow.append(to_para("PLANETARY CONJUNCTIONS — DEEP ANALYSIS",h1))
            flow.append(to_para("Every 2-planet conjunction analyzed with classical effects + house modifier",h1_sub))
            for c in sorted(conjs,key=lambda x:-x["severity"]):
                p1,p2=c["pair"]
                sev_stars="*"*c["severity"]+"."*(5-c["severity"])
                rel_color={"friend":"#0a7a3a","enemy":"#c0392b","neutral":"#5a5a5a"}.get(c["relationship"],"#5a5a5a")
                flow.append(to_para(
                    f"<b>{p1} + {p2} in House {c['house']}</b> &nbsp;"
                    f"<font color='{rel_color}' size='9'>({c['relationship'].upper()}, orb {c['distance_deg']}°)</font> &nbsp;"
                    f"<font color='#c9a032' size='10'><b>{sev_stars}</b></font>",body))
                flow.append(to_para(f"<font color='#1a1d3a' size='9'><b>EFFECT:</b> {c['general_effect']}</font>",body_small))
                flow.append(to_para(f"<font color='#5d2e8c' size='9'><i>LOCATION: {c['house_effect']}</i></font>",body_small))
                flow.append(to_para(f"<font color='#5a5a5a' size='8'>Source: {c['source']}</font>",body_small))
                flow.append(Spacer(1,0.3*cm))
            # Append book citations from corpus
            con_cits=cite_for_conjunction()
            if con_cits:
                flow.append(Spacer(1,0.3*cm))
                books=sorted({c["book"].replace("_"," ").replace("v2","").strip()
                              for c in con_cits if c.get("book")})
                flow.append(to_para(
                    "<font color='#5d2e8c' size='8'>Verified in classical corpus: "
                    f"<b>{', '.join(books)}</b></font>",body_small))
            flow.append(PageBreak())
    except Exception as exc:
        print(f"[conjunction_effects] WARNING: {exc}")

    # ─── EVENT TIMELINE PAGE — v2 auto-detected major life events ───
    try:
        from event_predictor_v2 import scan_lifetime_v2, collapse_consecutive, rank_and_consume, _age_at as _age_event
        from comprehensive_yogas import detect_all_classical_yogas as detect_all_yogas
        flow.append(to_para("MAJOR LIFE EVENTS — AUTO-DETECTED TIMELINE",h1))
        flow.append(to_para("Yoga + Dasha + Transit fusion engine",h1_sub))

        # Active yogas table
        ev_yogas=detect_all_yogas(chart)
        if ev_yogas:
            flow.append(to_para("<b>Active Predispositions (Yogas) in this chart:</b>",body))
            for y in ev_yogas:
                stars="*"*y["severity"]+"."*(5-y["severity"])
                flow.append(to_para(
                    f"&nbsp;&bull; <b>{y['name']}</b> ({y['name_translation']}) — severity {stars} ({y['severity']}/5)<br/>"
                    f"&nbsp;&nbsp;&nbsp;<font color='#5d2e8c' size='9'><i>{y['interpretation']}</i></font><br/>"
                    f"&nbsp;&nbsp;&nbsp;<font color='#5a5a5a' size='8'>Source: {y['source']}</font>",
                    body_small))
            flow.append(Spacer(1,0.4*cm))

        # Lifetime scan v2 — collapsed bands
        b_e=chart["birth"]
        events=scan_lifetime_v2(chart, b_e["year"], b_e["year"]+80, sample_days=10, min_severity=3)
        all_bands=collapse_consecutive(events)
        bands=rank_and_consume(all_bands) if all_bands else []
        flow.append(to_para(f"<b>{len(bands)} ranked life-event windows (top by category, severity 3+):</b>",body))
        rows=[["AGE","WINDOW","EVENT","CONFIDENCE","WHY THIS NOW"]]
        for b in bands:
            age=_age_event(b["window_start"], chart)
            wf=b["window_start"].strftime("%b %Y"); wt=b["window_end"].strftime("%b %Y")
            window_text=f"{wf} - {wt}" if wf != wt else wf
            stars=b.get("stars","*")
            conf=b.get("confidence","")
            score=b.get("score",0)
            conf_color="#16a34a" if score>=9 else ("#d97706" if score>=6 else "#a16207")
            why_text=" + ".join((b.get("max_why") or b.get("why") or [])[:2])[:75]
            rows.append([
                Paragraph(f"<b>{age:.0f}</b>",body_small),
                Paragraph(window_text,body_small),
                Paragraph(b["event"][:40],body_small),
                Paragraph(f"<font color='{conf_color}'><b>{stars}</b> {conf}<br/><font size='6'>score {score}</font></font>",body_small),
                Paragraph(f"<font size='7'>{why_text}</font>",body_small),
            ])
        if len(rows)>1:
            t=Table(rows,colWidths=[1.0*cm,2.6*cm,5.4*cm,1.7*cm,5.3*cm])
            t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),INDIGO),
                ("TEXTCOLOR",(0,0),(-1,0),CREAM),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
                ("FONTSIZE",(0,0),(-1,0),8),("LINEBELOW",(0,0),(-1,0),1,GOLD),
                ("ROWBACKGROUNDS",(0,1),(-1,-1),[white,GREY_LT]),
                ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
                ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
                ("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5)]))
            flow.append(t)
            flow.append(Spacer(1,0.3*cm))
            flow.append(to_para(
                "<i>Note: each event is generated by combining (1) classical yogas active in your chart, "
                "(2) which Mahadasha/Antardasha is running at that date, and (3) which transits are crossing "
                "your natal points. Severity 4-5 means high-conviction prediction; 3 means moderate; "
                "lower severity events have been filtered out for clarity.</i>",
                ParagraphStyle("foot",parent=body_small,textColor=GREY_MD)))
        else:
            flow.append(to_para("No high-severity events detected in scan window.",body))
        flow.append(PageBreak())
    except Exception as exc:
        print(f"[event_predictor] WARNING: {exc}")
        import traceback; traceback.print_exc()

    # ─── 23 DOMAIN PAGES ───
    DOMAINS=[
        (ICON["self"],"1","SELF & PERSONALITY","Lagna · Atmakaraka · Body · Intellect","self"),
        (ICON["family"],"2","PARENTS","Father · Mother · Bond · Longevity","parents"),
        (ICON["family"],"3","SIBLINGS","Number · Relationship · Success","siblings"),
        (ICON["education"],"4","EDUCATION","Primary · Higher · Specialized · Foreign","education"),
        (ICON["marriage"],"5","MARRIAGE","Timing · Spouse · Doshas · Compatibility","marriage"),
        (ICON["children"],"6","CHILDREN","Number · Gender · Success · Late Arrival","children"),
        (ICON["career"],"7","CAREER & PROFESSION","Field · Timeline · Job vs Business","career"),
        (ICON["wealth"],"8","WEALTH","Potential · Sources · Inheritance · Peaks","wealth"),
        (ICON["health"],"9","HEALTH","Constitution · Disease · Surgery · Longevity","health"),
        (ICON["travel"],"10","TRAVEL & FOREIGN","Settlement · Pilgrimage · Career Abroad","travel"),
        (ICON["property"],"11","PROPERTY & ASSETS","House · Land · Vehicles · Inheritance","property"),
        (ICON["status"],"12","SOCIAL STATUS, FAME, POWER","Recognition · Authority · Reputation","status"),
        (ICON["family"],"13","RELATIONSHIPS & ENEMIES","Friends · Enemies · Love · Trust","relationships"),
        (ICON["spirit"],"14","SPIRITUALITY","Religion · Guru · Practice · Moksha","spirituality"),
        (ICON["talent"],"15","TALENTS & SKILLS","Music · Sports · Writing · Languages","talents"),
        (ICON["past"],"16","PAST LIVES & KARMA","Pitri/Matri rin · Bhagya · Soul Path","past_lives"),
        (ICON["annual"],"17","ANNUAL PREDICTIONS (Varshaphala)","Muntha · Yearly Theme · Tajik","annual"),
        (ICON["prashna"],"18","SPECIFIC EVENT PROBABILITIES","Lottery · Imprisonment · Politics · Court","specific"),
    ]
    for icon,num,title,sub,key in DOMAINS:
        items=preds.get(key,[])
        if items:
            flow.extend(domain_page(icon,num,title,sub,items))
            flow.append(PageBreak())

    # ─── YOGAS PAGE ───
    flow.append(to_para("THE YOGAS THAT DEFINE THIS LIFE",h1))
    flow.append(to_para(f"{len(yogas)} configurations detected from chart placements",h1_sub))
    if not yogas:
        flow.append(to_para("No special yogas detected.",body))
    for y in yogas:
        accent=PLANET_COLOR.get(y["planet"],GOLD)
        glyph=PLANET_GLYPH.get(y["planet"],"")
        stars="★"*y["conf"]+"☆"*(4-y["conf"])
        confs={4:"CANONICAL",3:"STRONG",2:"MODERATE",1:"ANECDOTAL"}[y["conf"]]
        rows=[
            [Paragraph(f"<font color='#1a1d3a' size='14'><b>{y['name']}</b></font>",body),
             Paragraph(f"<font color='{hexstr(accent)}' size='28'><b>{glyph}</b></font>",
                       ParagraphStyle("g",alignment=TA_RIGHT,leading=32))],
            [Paragraph(f"<font color='#5d2e8c' size='10'><i>{y['place']}</i></font>",body),""],
            [Paragraph(f"<font color='#c9a032' size='12'><b>{stars}</b></font> &nbsp;<font color='#5a5a5a' size='9'><i>{confs}</i></font>",body_small),""],
            [Paragraph(y["desc"],body),""],
        ]
        t=Table(rows,colWidths=[(A4[0]-5*cm)*0.78,(A4[0]-5*cm)*0.22])
        t.setStyle(TableStyle([("SPAN",(0,1),(1,1)),("SPAN",(0,2),(1,2)),("SPAN",(0,3),(1,3)),
            ("BACKGROUND",(0,0),(-1,-1),CREAM),("LINEBEFORE",(0,0),(0,-1),4,GOLD),
            ("VALIGN",(0,0),(0,0),"MIDDLE"),("VALIGN",(1,0),(1,0),"MIDDLE"),
            ("VALIGN",(0,1),(-1,-1),"TOP"),
            ("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8),
            ("LEFTPADDING",(0,0),(-1,-1),16),("RIGHTPADDING",(0,0),(-1,-1),16)]))
        flow.append(t); flow.append(Spacer(1,0.3*cm))
    flow.append(PageBreak())

    # ─── EXTENDED CLASSICAL YOGAS — top 20 from 357-rule library ───
    try:
        from expanded_yogas import detect_all_expanded_yogas, yoga_count_summary
        ey=detect_all_expanded_yogas(chart)
        ey_summary=yoga_count_summary()
        flow.append(to_para("EXTENDED CLASSICAL YOGAS",h1))
        flow.append(to_para(
            f"{len(ey)} active from {ey_summary['total']}-rule library | "
            f"Bhavartha Ratnakara, Saravali, Phaladeepika, Jataka Parijata, BPHS Ch. 38, Brihat Jataka",h1_sub))
        flow.append(to_para(
            "Beyond the major yogas already shown, classical Jyotish recognizes hundreds of named patterns "
            "across 18 categories: Daridra (poverty), Putra (children), Roga (disease), Sadhu (spiritual), "
            "Career, Marriage, Travel, Nabhasa, Dhana (wealth), Arishta (afflictions), Raja (royal), "
            "Vipareeta Raja, Pravrajya (renunciation), Solar/Lunar full sets, Dhana Bhava, Dushtha. "
            f"Top 20 active for this chart shown below.",body))
        flow.append(Spacer(1,0.3*cm))
        if not ey:
            flow.append(to_para(f"No additional extended yogas active in the {ey_summary['total']}-rule library.",body))
        # Sort by severity descending, take top 20
        ey_sorted=sorted(ey,key=lambda x:-x.get("severity",0))[:20]
        for y in ey_sorted:
            sev_stars="★"*y.get("severity",1)+"☆"*(5-y.get("severity",1))
            cat=y.get("category","")
            domain=y.get("domain","")
            triggers=", ".join(y.get("triggers",[])[:3])
            rows=[
                [Paragraph(f"<b>{y['name']}</b> &nbsp; <font color='#c9a032'>{sev_stars}</font>",body)],
                [Paragraph(f"<font color='#5d2e8c' size='9'><i>Category: {cat} | Domain: {domain} | Source: {y.get('source','classical')}</i></font>",body_small)],
                [Paragraph(f"<font color='#5a5a5a' size='9'>Triggers: {triggers}</font>",body_small)],
                [Paragraph(y.get("interpretation","")[:340],body)],
            ]
            t=Table(rows,colWidths=[A4[0]-5*cm])
            t.setStyle(TableStyle([
                ("BACKGROUND",(0,0),(-1,-1),CREAM),
                ("LINEBEFORE",(0,0),(0,-1),3,GOLD),
                ("VALIGN",(0,0),(-1,-1),"TOP"),
                ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),
                ("LEFTPADDING",(0,0),(-1,-1),12),("RIGHTPADDING",(0,0),(-1,-1),12)]))
            flow.append(t)
            flow.append(Spacer(1,0.12*cm))
        flow.append(PageBreak())
    except Exception as exc:
        print(f"[expanded_yogas] WARNING: {exc}")

    # ─── EXTENDED DASHA SYSTEMS — 30 classical dashas beyond Vimshottari ───
    try:
        from dasha_systems_extended import all_extended_dashas, applicable_dashas, lookup_active
        ext_dashas=all_extended_dashas(chart)
        applic=applicable_dashas(chart)
        flow.append(to_para("THIRTY EXTENDED DASHA SYSTEMS",h1))
        flow.append(to_para(
            f"{len(ext_dashas)} computed | {len(applic)} classically applicable to this chart | "
            f"BPHS Ch. 47-50, Jaimini Sutras Ch. 2, Madhviya commentary",h1_sub))
        flow.append(to_para(
            "Beyond Vimshottari (the 120-year main system shown above), classical Jyotish defines "
            "42 dasha systems across three families: Conditional Nakshatra Dashas (used only when birth "
            "occurs under specific nakshatras or planetary conditions), Jaimini Rasi Dashas (sign-based "
            "timelines), and Graha Dashas (planet-based timelines). Each measures a different dimension "
            "of timing — wealth, longevity, dharma, spirituality, or social standing. Currently active "
            "periods for this chart across all 30 systems shown below.",body))
        flow.append(Spacer(1,0.3*cm))

        today=dt.datetime.now()
        # Build a compact "active now" table covering all 30 dashas
        active_rows=[["DASHA SYSTEM","ACTIVE NOW","RUNS UNTIL","NOTES"]]
        for name,timeline in ext_dashas.items():
            rec=lookup_active(timeline,today)
            if rec:
                active_lord=rec.get("sign") or rec.get("planet") or "?"
                end_str=rec["end"].strftime("%Y-%m-%d") if "end" in rec else "?"
                notes=rec.get("notes","")[:35]
                applicable_marker="" if name in applic else "  (not applicable to chart)"
                active_rows.append([
                    name.replace("_"," ").title(),
                    f"{active_lord}{applicable_marker}",
                    end_str,
                    notes,
                ])
        adt=Table(active_rows,colWidths=[5*cm,5.5*cm,3*cm,4*cm])
        adt.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0),INDIGO),
            ("TEXTCOLOR",(0,0),(-1,0),white),
            ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
            ("FONTSIZE",(0,0),(-1,-1),8),
            ("BACKGROUND",(0,1),(-1,-1),CREAM),
            ("GRID",(0,0),(-1,-1),0.3,GOLD_DK),
            ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
            ("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4),
            ("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3),
        ]))
        flow.append(adt)
        flow.append(Spacer(1,0.3*cm))

        # Applicability list — which dashas truly apply
        flow.append(to_para("<b>CLASSICALLY APPLICABLE DASHAS (filtered by birth conditions)</b>",h3))
        applicable_text=", ".join(name.replace("_"," ").title() for name in sorted(applic.keys()))
        flow.append(to_para(applicable_text,body))
        flow.append(Spacer(1,0.2*cm))

        # Detailed top-3 timelines for the chart's most-applicable dashas
        flow.append(to_para("<b>SAMPLE TIMELINES — first 5 entries each, top 3 systems</b>",h3))
        priority=["brahma","sudarshan_chakra","naisargika","tara","trikona"]
        shown=0
        for pname in priority:
            if shown >= 3: break
            if pname not in ext_dashas: continue
            timeline=ext_dashas[pname]
            if not timeline: continue
            rows=[[pname.replace("_"," ").upper(),"START","END","YRS","AGE"]]
            for rec in timeline[:5]:
                lord_str=rec.get("sign") or rec.get("planet") or "?"
                start_str=rec["start"].strftime("%Y-%m-%d")
                end_str=rec["end"].strftime("%Y-%m-%d")
                yrs=f"{rec.get('years',0):.1f}"
                ages=f"{rec.get('age_from',0)}-{rec.get('age_to',0)}"
                rows.append([lord_str,start_str,end_str,yrs,ages])
            tbl=Table(rows,colWidths=[4*cm,3*cm,3*cm,1.5*cm,2*cm])
            tbl.setStyle(TableStyle([
                ("BACKGROUND",(0,0),(-1,0),PURPLE),
                ("TEXTCOLOR",(0,0),(-1,0),white),
                ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
                ("FONTSIZE",(0,0),(-1,-1),8),
                ("BACKGROUND",(0,1),(-1,-1),CREAM_2),
                ("GRID",(0,0),(-1,-1),0.3,GOLD_DK),
                ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
                ("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4),
            ]))
            flow.append(tbl)
            flow.append(Spacer(1,0.2*cm))
            shown += 1

        flow.append(PageBreak())
    except Exception as exc:
        print(f"[extended_dashas] WARNING: {exc}")

    # ─── PLANETARY AVASTHAS — 4 classical state systems ───
    try:
        from avasthas_engine import all_avasthas, avastha_summary
        av=all_avasthas(chart)
        avs=avastha_summary(chart)
        flow.append(to_para("PLANETARY AVASTHAS — Four-Layer State Analysis",h1))
        flow.append(to_para(
            f"9 planets x 4 systems = 36 state readings | Total chart strength: "
            f"{avs.get('total_strength_pct',0):.1f}% | "
            "Phaladeepika Ch. 8, BPHS Ch. 45",h1_sub))
        flow.append(to_para(
            "Avasthas describe the moment-to-moment psychological 'state' of each planet at birth: "
            "Baladi (life-stage 0-30 deg), Jagradadi (wakefulness via dignity), Deeptadi (9-fold dignity), "
            "Lajjitadi (interactive shame/pride/hunger). Together they reveal which planets fire fully "
            "and which sleep through their dasha periods.",body))
        flow.append(Spacer(1,0.3*cm))

        # 4-state grid: 1 row per planet, columns = Baladi / Jagradadi / Deeptadi / Lajjitadi
        avrows=[["PLANET","BALADI (5)","JAGRADADI (3)","DEEPTADI (9)","LAJJITADI (6)"]]
        planet_order=["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu","Ketu"]
        for p in planet_order:
            if p not in av: continue
            ps=av[p]
            b=ps.get("baladi",{}); j=ps.get("jagradadi",{}); d=ps.get("deeptadi",{}); l=ps.get("lajjitadi",{})
            avrows.append([
                p,
                f"{b.get('state','?')} ({b.get('strength_pct',0)}%)",
                f"{j.get('state','?')} ({j.get('strength_pct',0)}%)",
                f"{d.get('state','?')} ({d.get('strength_pct',0)}%)",
                f"{l.get('state','?')} ({l.get('strength_pct',0)}%)",
            ])
        avt=Table(avrows,colWidths=[2.2*cm,3.5*cm,3.5*cm,3.5*cm,3.5*cm])
        avt.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0),INDIGO),
            ("TEXTCOLOR",(0,0),(-1,0),white),
            ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
            ("FONTSIZE",(0,0),(-1,-1),8),
            ("BACKGROUND",(0,1),(-1,-1),CREAM),
            ("GRID",(0,0),(-1,-1),0.3,GOLD_DK),
            ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
            ("LEFTPADDING",(0,0),(-1,-1),3),("RIGHTPADDING",(0,0),(-1,-1),3),
            ("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3),
        ]))
        flow.append(avt)
        flow.append(Spacer(1,0.3*cm))

        # Summary
        if avs:
            flow.append(to_para(
                f"<b>Strongest planet:</b> {avs.get('strongest_planet','?')} | "
                f"<b>Weakest planet:</b> {avs.get('weakest_planet','?')} | "
                f"<b>Total chart vitality:</b> {avs.get('total_strength_pct',0):.1f}%",body))
            for rec in avs.get("recommendations",[])[:5]:
                flow.append(to_para(f"&bull; {rec}",body))
        flow.append(PageBreak())
    except Exception as exc:
        print(f"[avasthas] WARNING: {exc}")

    # ─── ADVANCED JAIMINI DASHAS — 7 sutra-based timing systems ───
    try:
        from jaimini_full import all_jaimini_dashas_full
        jd=all_jaimini_dashas_full(chart)
        flow.append(to_para("ADVANCED JAIMINI DASHAS — Seven Sutra-Based Timelines",h1))
        flow.append(to_para(
            f"{len(jd)} timelines | Karaka Kendradi, Padakrama, Lagna Kendradi, Brahma, Mandooka, "
            f"Yogardha, Sthira-Jaimini | Source: Jaimini Sutras Ch. 2",h1_sub))
        flow.append(to_para(
            "Beyond Vimshottari and Char Dasha, Jaimini Sutras Ch. 2 defines seven additional timing "
            "systems each anchored on a different chart-point: Atmakaraka, Lagna, 7th-from-AK, 5th-from-AK, "
            "or fixed quality of the rashi. Each captures a different dimension of fate-unfoldment. "
            "Active-now for each system shown below.",body))
        flow.append(Spacer(1,0.3*cm))

        today=dt.datetime.now()
        jdrows=[["DASHA SYSTEM","ACTIVE NOW","STARTED","ENDS","YEARS"]]
        for dname,timeline in jd.items():
            if not timeline: continue
            active=None
            for rec in timeline:
                if rec.get("start") and rec.get("end") and rec["start"] <= today <= rec["end"]:
                    active=rec; break
            if not active: continue
            lord=active.get("planet") or active.get("sign") or active.get("lord","?")
            jdrows.append([
                dname.replace("_"," ").title(),
                str(lord),
                active["start"].strftime("%Y-%m-%d"),
                active["end"].strftime("%Y-%m-%d"),
                f"{active.get('years',0):.1f}",
            ])
        jdt=Table(jdrows,colWidths=[5*cm,4*cm,3*cm,3*cm,1.8*cm])
        jdt.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0),MAROON),
            ("TEXTCOLOR",(0,0),(-1,0),white),
            ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
            ("FONTSIZE",(0,0),(-1,-1),8),
            ("BACKGROUND",(0,1),(-1,-1),CREAM_2),
            ("GRID",(0,0),(-1,-1),0.3,GOLD_DK),
            ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
            ("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4),
        ]))
        flow.append(jdt)
        flow.append(PageBreak())
    except Exception as exc:
        print(f"[jaimini_advanced] WARNING: {exc}")

    # ─── CHAMATKAR CHINTAMANI — Bhattaji's 108-verse character reading ───
    try:
        from chamatkar_chintamani import chamatkar_reading, chamatkar_summary
        cc=chamatkar_reading(chart)
        ccs=chamatkar_summary(chart)
        flow.append(to_para("CHAMATKAR CHINTAMANI — Verse Readings",h1))
        flow.append(to_para(
            "Bhattaji's 17th-century classical | 9 planets x 12 houses = 108 verses | "
            "Each planet's natal house picks a poetic character verse",h1_sub))
        flow.append(to_para(
            "Where BPHS gives mechanical planet-in-house effects, Chamatkar Chintamani delivers a "
            "poetic 4-line verse capturing the LIVED character of each combination. Below: a verse "
            "for each of the nine natal placements.",body))
        flow.append(Spacer(1,0.3*cm))

        # Top synthesis
        if ccs:
            kw=", ".join(ccs.get("personality_keywords",[])[:10])
            flow.append(to_para(f"<b>Personality keywords (top 10):</b> {kw}",body))
            life_arc=ccs.get("core_life_arc","")
            if life_arc:
                flow.append(to_para(f"<b>Core life arc:</b> {life_arc[:400]}",body))
            flow.append(Spacer(1,0.3*cm))

        # Per-planet verse cards
        for r in cc:
            p=r.get("planet","?"); h=r.get("house","?")
            accent=PLANET_COLOR.get(p,GOLD)
            glyph=PLANET_GLYPH.get(p,"")
            sansk=r.get("verse_sanskrit","")[:200]
            trans=r.get("verse_translation","")[:380]
            themes=", ".join(r.get("character_themes",[])[:5])
            ampl=r.get("amplification","moderate")
            rows=[[
                Paragraph(f"<font color='{hexstr(accent)}' size='18'><b>{glyph}</b></font>",
                          ParagraphStyle("g",alignment=TA_CENTER,leading=22)),
                Paragraph(f"<b>{p}</b> in House {h} &nbsp; <font color='#7d1f3d' size='8'>[{ampl}]</font>",body),
            ],["",
                Paragraph(f"<font color='#5d2e8c' size='8'><i>{sansk}</i></font>",body_small),
            ],["",
                Paragraph(trans,body),
            ],["",
                Paragraph(f"<font color='#5a5a5a' size='8'>Themes: {themes}</font>",body_small),
            ]]
            t=Table(rows,colWidths=[1.2*cm,A4[0]-5*cm-1.2*cm])
            t.setStyle(TableStyle([("SPAN",(0,0),(0,3)),
                ("BACKGROUND",(0,0),(-1,-1),CREAM),
                ("LINEBEFORE",(0,0),(0,-1),3,accent),
                ("VALIGN",(0,0),(0,-1),"MIDDLE"),("VALIGN",(1,0),(-1,-1),"TOP"),
                ("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3),
                ("LEFTPADDING",(0,0),(-1,-1),10)]))
            flow.append(t)
            flow.append(Spacer(1,0.1*cm))
        flow.append(PageBreak())
    except Exception as exc:
        print(f"[chamatkar] WARNING: {exc}")

    # ─── NADI CELL NARRATIVE — full 108-cell-aware reading ───
    try:
        from nadi_full import complete_nadi_analysis
        nf=complete_nadi_analysis(chart)
        flow.append(to_para("NADI CELL NARRATIVE — 108-Cell Reading",h1))
        flow.append(to_para(
            "Bhrigu Nadi style sentence-prose for every planet placement | "
            f"{len(nf['two_planet_rules_detected'])} 2-planet rules + 9 karaka readings",h1_sub))
        flow.append(to_para(
            "Naadi Jyotish reads each planet-house combination as a specific sentence describing "
            "the karaka's manifestation. Sources: Bhrigu Nadi, Chandra Kala Nadi, Saptarishi Nadi.",body))
        flow.append(Spacer(1,0.3*cm))

        # Per-planet 108-cell narrative
        flow.append(to_para("<b>9-PLANET NAADI READING</b>",h3))
        for planet,info in nf["narrative_108_cells"].items():
            accent=PLANET_COLOR.get(planet,GOLD)
            glyph=PLANET_GLYPH.get(planet,"")
            rows=[[
                Paragraph(f"<font color='{hexstr(accent)}' size='18'><b>{glyph}</b></font>",
                          ParagraphStyle("g",alignment=TA_CENTER,leading=22)),
                Paragraph(f"<b>{planet}</b> in House {info['house']} ({info['rasi']})",body),
            ],["",
                Paragraph(f"<font color='#5d2e8c' size='9'><i>{info.get('archetype','')}</i></font>",body_small),
            ],["",
                Paragraph(info["reading"],body),
            ]]
            t=Table(rows,colWidths=[1.2*cm,A4[0]-5*cm-1.2*cm])
            t.setStyle(TableStyle([("SPAN",(0,0),(0,2)),
                ("BACKGROUND",(0,0),(-1,-1),CREAM),
                ("LINEBEFORE",(0,0),(0,-1),3,accent),
                ("VALIGN",(0,0),(0,-1),"MIDDLE"),("VALIGN",(1,0),(-1,-1),"TOP"),
                ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),
                ("LEFTPADDING",(0,0),(-1,-1),10)]))
            flow.append(t)
            flow.append(Spacer(1,0.1*cm))

        # 2-planet conjunction rules
        if nf["two_planet_rules_detected"]:
            flow.append(Spacer(1,0.3*cm))
            flow.append(to_para("<b>2-PLANET NAADI CONJUNCTIONS DETECTED</b>",h3))
            for r in nf["two_planet_rules_detected"]:
                flow.append(to_para(
                    f"<b>{r['combination']} (House {r['house']}):</b><br/>"
                    f"<i>{r['reading']}</i>",body))
                flow.append(Spacer(1,0.15*cm))

        # Karaka readings
        flow.append(Spacer(1,0.3*cm))
        flow.append(to_para("<b>KARAKA-AGENT READINGS — Strong / Weak per planet</b>",h3))
        for p,info in nf["karaka_readings"].items():
            accent=PLANET_COLOR.get(p,GOLD)
            tone_color="#0a7a3a" if info["tone"]=="strong" else ("#c0392b" if info["tone"]=="weak" else "#5a5a5a")
            tone_label=info["tone"].upper()
            flow.append(to_para(
                f"<font color='{hexstr(accent)}'><b>{p}</b></font> "
                f"({info['agent_of']}) — H{info['house']}, {info['rasi']}, {info['dignity']} "
                f"<font color='{tone_color}'>[{tone_label}]</font><br/>"
                f"<i>{info['reading']}</i>",body_small))
            flow.append(Spacer(1,0.1*cm))
        flow.append(PageBreak())
    except Exception as exc:
        print(f"[nadi_full] WARNING: {exc}")

    # ─── CHARA KARAKAS PAGE ───
    flow.append(to_para("CHARA KARAKAS",h1))
    flow.append(to_para("Soul indicators — 7 roles by descending degree",h1_sub))
    karaka_meanings={
        "Atmakaraka (AK)":"Soul indicator — core life purpose",
        "Amatyakaraka (AmK)":"Mind/career — profession theme",
        "Bhratrukaraka (BK)":"Siblings — brother/cousin patterns",
        "Matrukaraka (MK)":"Mother — mother relationship + comforts",
        "Putrakaraka (PK)":"Children — children + creativity",
        "Gnatikaraka (GK)":"Enemies/disease — health + obstacles",
        "Darakaraka (DK)":"Spouse — partner type + marriage",
    }
    rows=[["KARAKA","PLANET","DEGREE","MEANING"]]
    pos=chart["positions"]
    for role,planet,deg in karakas:
        glyph_color=hexstr(PLANET_COLOR.get(planet,GREY_DK))
        rows.append([
            Paragraph(f"<b>{role}</b>",body_small),
            Paragraph(f"<font color='{glyph_color}' size='14'><b>{PLANET_GLYPH.get(planet,'')}</b></font> {planet}",body_small),
            Paragraph(f"{deg:.2f}°",body_small),
            Paragraph(karaka_meanings.get(role,""),body_small),
        ])
    t=Table(rows,colWidths=[3.5*cm,3*cm,2*cm,7.5*cm])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),INDIGO),
        ("TEXTCOLOR",(0,0),(-1,0),CREAM),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("FONTSIZE",(0,0),(-1,0),9),("LINEBELOW",(0,0),(-1,0),1,GOLD),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[white,GREY_LT]),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7),
        ("LEFTPADDING",(0,0),(-1,-1),10)]))
    flow.append(t)
    flow.append(PageBreak())

    # ─── NAKSHATRA DETAIL PAGE ───
    flow.append(to_para("NAKSHATRA DETAIL",h1))
    flow.append(to_para("Personality archetype from Janma Nakshatra",h1_sub))
    nak=chart["janma_nakshatra"]
    moon=chart["positions"]["Moon"]
    pada=moon.get("pada","?")
    flow.append(to_para(
        f"<b>Janma Nakshatra:</b> {nak} (pada {pada})<br/>"
        f"<b>Lord:</b> {chart.get('janma_nakshatra_lord','?')}<br/>"
        f"<b>Personality archetype:</b> {NAKSHATRA_PERSONALITY.get(nak,'(no specific data)')}<br/>"
        f"<b>Vimshottari period:</b> {VIMSHOTTARI_YEARS.get(chart.get('janma_nakshatra_lord','Ketu'),'?')} years",body))
    flow.append(Spacer(1,0.4*cm))
    flow.append(to_para("All 27 nakshatras have distinct personalities. Each pada (¼ of nakshatra = 3°20') refines further. Yours is shaped by:",body))
    flow.append(to_para(
        f"&bull; Nakshatra ruler: <b>{chart.get('janma_nakshatra_lord','?')}</b><br/>"
        f"&bull; Pada {pada} adds further nuance<br/>"
        f"&bull; The deity of {nak} influences temperament<br/>"
        f"&bull; This is one of 108 distinct personality types in classical Jyotish",body))
    flow.append(PageBreak())

    # ─── DASHA CHAPTERS — DEEP NARRATIVE V2-STYLE ───
    for i,md in enumerate(mds,1):
        is_cur=md["start"]<=today<=md["end"]
        # Inject md_years into sub_dashas list for chapter_with_narrative to read
        subs=sub_dashas[i-1]["subs"]
        for s in subs:
            s["md_years"]=f"{md['years']:.1f} years"
        chapter_elems=chapter_with_narrative(
            num=str(i),
            planet=md["lord"],
            dates=f"{md['start'].strftime('%Y')} — {md['end'].strftime('%Y')}",
            ages=f"{md['age_from']:.0f} to {md['age_to']:.0f}",
            theme=", ".join(PLANET_ARCHETYPES.get(md['lord'],"").split(",")[:3]),
            chart=chart,
            sub_dashas=subs,
            today=today,
            is_current=is_cur,
        )
        flow.extend(chapter_elems)
        flow.append(PageBreak())

    # ─── HOUSES 1-12 DEEP DIVE ───
    flow.append(to_para("ALL 12 HOUSES — DEEP DIVE",h1))
    flow.append(to_para("What each house holds and what it activates",h1_sub))
    pos=chart["positions"]
    rows=[["H","SIGN","LORD","LORD SITS","OCCUPANTS","KEY THEME"]]
    for h in range(1,13):
        sign_idx=(chart["lagna_idx"]+h-1)%12
        sign=RASIS[sign_idx]; lord=RASI_LORDS[sign]
        lh=pos[lord]["house"] if lord in pos else "?"
        occ=[p for p,pd in pos.items() if pd["house"]==h]
        occ_str=", ".join(occ) if occ else "(empty)"
        glyph_color=hexstr(PLANET_COLOR.get(lord,GREY_DK))
        rows.append([
            Paragraph(f"<b>{h}</b>",body_small),
            Paragraph(sign,body_small),
            Paragraph(f"<font color='{glyph_color}' size='12'><b>{PLANET_GLYPH.get(lord,'')}</b></font> {lord}",body_small),
            Paragraph(f"H{lh}",body_small),
            Paragraph(occ_str,body_small),
            Paragraph(HOUSE_THEMES[h],body_small),
        ])
    t=Table(rows,colWidths=[0.7*cm,2.2*cm,2.5*cm,1.5*cm,3.5*cm,5.6*cm])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),INDIGO),
        ("TEXTCOLOR",(0,0),(-1,0),CREAM),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("FONTSIZE",(0,0),(-1,0),8),("LINEBELOW",(0,0),(-1,0),1,GOLD),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[white,GREY_LT]),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6),
        ("LEFTPADDING",(0,0),(-1,-1),6)]))
    flow.append(t)
    flow.append(PageBreak())

    # ─── REMEDIES (UPAYAS) ───
    flow.append(to_para("REMEDIES (UPAYAS)",h1))
    flow.append(to_para("Per-planet remedial measures from classical sources",h1_sub))
    REMEDIES = {
        "Sun":("Ruby gemstone (red); Surya Namaskar at sunrise; Aditya Hridayam stotra; "
               "donate wheat/copper on Sundays; respect father and elders; offer water to Sun at sunrise.",1.0),
        "Moon":("Pearl gemstone (white); chant Chandra mantra; donate rice/silver/milk on Mondays; "
                "respect mother; visit Shiva temples; meditate on full moon nights.",1.0),
        "Mars":("Red coral gemstone; Hanuman Chalisa daily; donate red lentils/jaggery on Tuesdays; "
                "blood donation; visit Subramanya / Murugan temples.",1.0),
        "Mercury":("Emerald gemstone (green); Vishnu Sahasranama; donate green moong dal on Wednesdays; "
                   "education-related charity; chant Budha mantra.",1.0),
        "Jupiter":("Yellow sapphire (Pukhraj); Brihaspati mantra Thursdays; donate yellow dal/turmeric/"
                   "books; respect gurus and teachers; visit Vishnu temples.",1.0),
        "Venus":("Diamond / white sapphire; Lakshmi mantras Fridays; donate white cloth/sugar/curd; "
                 "respect women; offer worship at Lakshmi or Saraswati shrines.",1.0),
        "Saturn":("Blue sapphire (Neelam — caution, test first); Shani Stotra Saturdays; "
                  "donate black sesame/oil/iron; serve elderly and laborers; visit Shani temples.",1.0),
        "Rahu":("Hessonite (Gomedha); Durga mantras; donate black blanket, sesame; serve outcastes; "
                "fast on Saturdays; visit Bhairava temples.",1.0),
        "Ketu":("Cat's eye (Lehsuniya); Ganesha mantras; donate multi-color cloth; serve animals; "
                "spiritual practice; visit Ganesha temples.",1.0),
    }
    # Recommend remedies for: planets in dusthana (6/8/12), debilitated, or in challenging house for the chart
    recommend_for=set()
    for p,pd in pos.items():
        if p in ["Rahu","Ketu"]:
            if pd["house"] in [6,8,12]: recommend_for.add(p)
        else:
            d=DIGNITIES.get((p,pd["rasi"]))
            if d=="Debil": recommend_for.add(p)
            if pd["house"] in [6,8,12]: recommend_for.add(p)
    if not recommend_for:
        recommend_for={"Jupiter","Saturn"}  # always good general remedies

    flow.append(to_para(
        f"<b>Most relevant for this chart:</b> {', '.join(sorted(recommend_for))} "
        f"(planets in challenging houses or weakened by dignity)",body))
    flow.append(Spacer(1,0.3*cm))
    for p in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu","Ketu"]:
        rem,_=REMEDIES[p]
        is_priority=p in recommend_for
        accent=PLANET_COLOR.get(p,GOLD)
        prefix="★ PRIORITY: " if is_priority else ""
        rows=[[
            Paragraph(f"<font color='{hexstr(accent)}' size='20'><b>{PLANET_GLYPH.get(p,'')}</b></font>",
                      ParagraphStyle("g",alignment=TA_CENTER,leading=24)),
            Paragraph(f"<b>{prefix}{p}</b>",ParagraphStyle("t",fontName="Helvetica-Bold",
                      fontSize=11,textColor=INDIGO if not is_priority else MAROON))
        ],["",Paragraph(rem,body)]]
        bg=CREAM_2 if is_priority else CREAM
        t=Table(rows,colWidths=[1.2*cm,A4[0]-5*cm-1.2*cm])
        t.setStyle(TableStyle([("SPAN",(0,0),(0,1)),
            ("BACKGROUND",(0,0),(-1,-1),bg),
            ("LINEBEFORE",(0,0),(0,-1),4,accent),
            ("VALIGN",(0,0),(0,-1),"MIDDLE"),("VALIGN",(1,0),(-1,-1),"TOP"),
            ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6),
            ("LEFTPADDING",(0,0),(-1,-1),10)]))
        flow.append(t); flow.append(Spacer(1,0.15*cm))
    flow.append(PageBreak())

    # ─── AUSPICIOUS MUHURTA PRINCIPLES ───
    flow.append(to_para("MUHURTA — AUSPICIOUS TIMING",h1))
    flow.append(to_para("Best moments for major life events",h1_sub))
    moon_rasi=chart["moon_rasi"]
    moon_nak=chart["janma_nakshatra"]
    flow.append(to_para(
        f"<b>For {chart['name']}, the following Muhurta rules apply:</b><br/><br/>"
        f"&bull; <b>Marriage Muhurta</b> — best when Moon is favorable (currently Moon in <b>{moon_rasi}</b>, nakshatra <b>{moon_nak}</b>); "
        f"avoid Moon in 4th, 8th, 12th from natal Moon. Best months: avoid Mala Masa (Adhik). "
        f"Tarabala must be auspicious.<br/><br/>"
        f"&bull; <b>Griha Pravesh (House Warming)</b> — Vaisakha, Jyestha, Magha months ideal. "
        f"Avoid Bhadra, Vishti karana. Moon should be in own/exalted/friendly sign.<br/><br/>"
        f"&bull; <b>Vyapara (Business Start)</b> — Mercury hora; favourable on Wednesdays. "
        f"Strong 11th lord transit needed. Avoid Saturn-Mars activation periods.<br/><br/>"
        f"&bull; <b>Vahana (Vehicle Purchase)</b> — Venus hora on Friday; Moon in fixed signs (Taurus, Leo, Scorpio, Aquarius).<br/><br/>"
        f"&bull; <b>Yatra (Travel)</b> — Mercury or Jupiter day; avoid Tuesday/Saturday for distant travel. "
        f"Direction matters: Disha Shoola check.<br/><br/>"
        f"&bull; <b>Shastra (Surgery)</b> — Krishna paksha (waning Moon) preferred; avoid Vishti karana. "
        f"Mars must not aspect 6th from Moon.<br/><br/>"
        f"&bull; <b>Dhana (Financial transactions)</b> — Wednesday/Thursday; Moon in 2nd/11th from natal.<br/><br/>"
        f"&bull; <b>Namakaran (Naming Ceremony)</b> — 10th, 12th, 16th day after birth. Avoid Bhadra.<br/><br/>"
        f"&bull; <b>Annaprashana (First feeding)</b> — 6-8 months after birth. Avoid Saturday.<br/><br/>"
        f"&bull; <b>Upanayana (Sacred thread)</b> — Spring months for boys; Jupiter must be strong.",body))
    flow.append(PageBreak())

    # ─── LIFETIME KARMIC THEMES SUMMARY ───
    flow.append(to_para("LIFETIME KARMIC THEMES",h1))
    flow.append(to_para("The patterns running through every period of life",h1_sub))
    pos=chart["positions"]
    themes=[]
    # Theme 1: Atmakaraka journey
    ak=karakas[0][1] if karakas else "?"
    themes.append(("Soul Path",
        f"Atmakaraka <b>{ak}</b> defines the soul's evolutionary journey. "
        f"All life experiences filter through {PLANET_ARCHETYPES.get(ak,'')} themes.",ak))
    # Theme 2: Lagnesh placement
    lagnesh=chart.get('lagna_lord')
    if lagnesh and lagnesh in pos:
        lh=pos[lagnesh]["house"]
        themes.append(("Identity Direction",
            f"Lagna lord <b>{lagnesh}</b> sits in House {lh} ({HOUSE_THEMES[lh]}). "
            f"Self-expression flows through this domain.",lagnesh))
    # Theme 3: Sun in house — father/career theme
    sh=pos["Sun"]["house"]
    themes.append(("Father / Authority",
        f"Sun in House {sh} ({HOUSE_THEMES[sh]}). Father's role and authority experiences "
        f"manifest here.","Sun"))
    # Theme 4: Moon in house — emotional theme
    mh=pos["Moon"]["house"]
    themes.append(("Emotional Anchor",
        f"Moon in House {mh} ({HOUSE_THEMES[mh]}). Emotional life and mother-bond center "
        f"on this house.","Moon"))
    # Theme 5: Saturn in house — discipline + delays
    satch=pos["Saturn"]["house"]
    themes.append(("Discipline / Delays",
        f"Saturn in House {satch} ({HOUSE_THEMES[satch]}). Hardest tests and longest-lasting "
        f"rewards come through this domain.","Saturn"))
    # Theme 6: Jupiter in house — wisdom + expansion
    jh=pos["Jupiter"]["house"]
    themes.append(("Wisdom / Expansion",
        f"Jupiter in House {jh} ({HOUSE_THEMES[jh]}). Where life expands, blesses, "
        f"protects from harm.","Jupiter"))
    # Theme 7: Rahu — foreign / unconventional path
    rh=pos["Rahu"]["house"]
    themes.append(("Foreign / Unconventional",
        f"Rahu in House {rh} ({HOUSE_THEMES[rh]}). Karmic destiny pulls toward unconventional, "
        f"foreign, or technology-driven path in this domain.","Rahu"))
    # Theme 8: Ketu — past karma / detachment
    kh=pos["Ketu"]["house"]
    themes.append(("Past Karma Cleared",
        f"Ketu in House {kh} ({HOUSE_THEMES[kh]}). Past-life skills already mastered here — "
        f"detachment from this domain serves spiritual growth.","Ketu"))
    # Theme 9: Marriage / partnership
    h7_lord=RASI_LORDS[RASIS[(chart["lagna_idx"]+6)%12]]
    themes.append(("Partnership Pattern",
        f"7th lord <b>{h7_lord}</b> placed in H{pos[h7_lord]['house'] if h7_lord in pos else '?'}. "
        f"Spouse and partnership themes activated through Venus in H{pos['Venus']['house']}.","Venus"))
    # Theme 10: Career direction
    h10_lord=RASI_LORDS[RASIS[(chart["lagna_idx"]+9)%12]]
    themes.append(("Career Direction",
        f"10th lord <b>{h10_lord}</b> sits in H{pos[h10_lord]['house'] if h10_lord in pos else '?'}. "
        f"Career manifests through this house's themes.","Mercury"))

    for i,(title,desc,planet) in enumerate(themes,1):
        accent=PLANET_COLOR.get(planet,GOLD)
        glyph=PLANET_GLYPH.get(planet,"")
        rows=[[
            Paragraph(f"<font color='{hexstr(accent)}' size='22'><b>{glyph}</b></font>",
                      ParagraphStyle("g",alignment=TA_CENTER,leading=26)),
            Paragraph(f"<font color='#5d2e8c' size='12'><b>{i}. {title}</b></font>",body),
        ],["",Paragraph(desc,body)]]
        t=Table(rows,colWidths=[1.2*cm,A4[0]-5*cm-1.2*cm])
        t.setStyle(TableStyle([("SPAN",(0,0),(0,1)),
            ("BACKGROUND",(0,0),(-1,-1),white),
            ("LINEBEFORE",(0,0),(0,-1),4,accent),
            ("VALIGN",(0,0),(0,-1),"MIDDLE"),("VALIGN",(1,0),(-1,-1),"TOP"),
            ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),8),
            ("LEFTPADDING",(0,0),(0,-1),10),("LEFTPADDING",(1,0),(-1,-1),12),
            ("RIGHTPADDING",(0,0),(-1,-1),10),
            ("LINEBELOW",(0,-1),(-1,-1),0.4,GREY_LT)]))
        flow.append(t)
    flow.append(PageBreak())

    # ─── UPAGRAHAS — Gulika, Mandi, Dhuma & shadow points ───
    try:
        from upagrahas import compute_upagrahas
        ug = compute_upagrahas(chart)
        flow.append(to_para("UPAGRAHAS — SHADOW PLANETS",h1))
        flow.append(to_para("Gulika · Mandi · Dhuma · Vyatipata · Parivesha · Upaketu · Yamakantaka",h1_sub))
        flow.append(to_para(
            "Upagrahas are sensitive shadow points derived from planetary positions and the birth time. "
            "They are not visible planets but carry malefic or transformative influences in the houses they occupy. "
            "Gulika (son of Saturn) and Mandi (son of Mars) are the most powerful — their house placement "
            "indicates where hidden obstacles, poison, and suffering can manifest.",body))
        flow.append(Spacer(1,0.3*cm))
        UG_MEANING = {
            "Gulika":   "Son of Saturn — malefic influence; poison, delays, hidden enemies in its house",
            "Mandi":    "Son of Mars — karma, past-life debts; disease/conflict if afflicted",
            "Dhuma":    "Smoky point — confusion, deception, hidden matters in its house",
            "Vyatipata":"Calamity indicator — sudden reversals when activated by transit",
            "Parivesha":"Halo/rainbow point — illusions and false hopes in its domain",
            "Indrachapa":"Bow of Indra — competitive pressure and ego battles",
            "Upaketu":  "Comet-like — erratic events; spiritual disruption when activated",
            "Yamakantaka":"Yama's staff — karmic correction and dharmic enforcement",
        }
        rows=[["UPAGRAHA","SIGN","HOUSE","DEGREE","SIGNIFICANCE"]]
        for nm, info in ug.items():
            rows.append([
                Paragraph(f"<b>{nm}</b>",body_small),
                Paragraph(info.get("rasi","?"),body_small),
                Paragraph(f"H{info.get('house','?')}",body_small),
                Paragraph(f"{info.get('deg',0):.2f}°",body_small),
                Paragraph(f"<font size='8'>{UG_MEANING.get(nm,'')}</font>",body_small),
            ])
        t=Table(rows,colWidths=[2.8*cm,2.5*cm,1.2*cm,1.5*cm,8.0*cm])
        t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),INDIGO),
            ("TEXTCOLOR",(0,0),(-1,0),CREAM),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
            ("FONTSIZE",(0,0),(-1,0),8),("LINEBELOW",(0,0),(-1,0),1,GOLD),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[white,GREY_LT]),
            ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
            ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6),
            ("LEFTPADDING",(0,0),(-1,-1),6)]))
        flow.append(t)
        flow.append(Spacer(1,0.3*cm))
        # Highlight Gulika & Mandi
        g=ug.get("Gulika",{}); m=ug.get("Mandi",{})
        if g:
            flow.append(to_para(
                f"<b>⚠ Gulika</b> in House {g.get('house','?')} ({g.get('rasi','?')}) — "
                f"This house carries latent Saturnine obstacles. Events here require extra care, patience, "
                f"and ethical conduct to avoid setbacks or hidden poison (legal, physical, or financial).",body_small))
        if m:
            flow.append(to_para(
                f"<b>⚠ Mandi</b> in House {m.get('house','?')} ({m.get('rasi','?')}) — "
                f"Past-life karmic debts manifest through this house. Physical health matters and conflicts "
                f"in this domain need conscious management.",body_small))
        flow.append(PageBreak())
    except Exception as exc:
        print(f"[upagrahas] WARNING: {exc}")

    # ─── ASHTAKAVARGA — Bhinna + Sarva point scores ───
    try:
        from engine.ashtakavarga import compute_bhinna_ashtakavarga
        bav = compute_bhinna_ashtakavarga(chart)
        flow.append(to_para("ASHTAKAVARGA — EIGHT-SOURCE STRENGTH MATRIX",h1))
        flow.append(to_para("Bindus per house for each planet — classical strength grid from BPHS Ch. 66-68",h1_sub))
        flow.append(to_para(
            "Ashtakavarga divides the zodiac into benefic/malefic contributions from each planet + Lagna. "
            "Each house gets 0-8 bindus (strength points) per planet. "
            "4+ bindus = favourable transit; below 4 = challenges during that planet's transit through that house. "
            "The Sarva (total) score shows overall zodiacal strength.",body))
        flow.append(Spacer(1,0.3*cm))
        # Compute sarva (sum across all planets per house)
        sarva=[0]*12
        for p,scores in bav.items():
            for h in range(1,13):
                sarva[h-1]+=scores.get(f"house_{h}",0)
        # Header
        planet_list=[p for p in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"] if p in bav]
        header=["HOUSE"]+planet_list+["SARVA TOTAL"]
        rows=[header]
        for h in range(1,13):
            sign_idx=(chart["lagna_idx"]+h-1)%12
            sign=RASIS[sign_idx]
            row=[Paragraph(f"<b>H{h}</b><font size='7'> {sign[:3]}</font>",body_small)]
            for p in planet_list:
                score=bav[p].get(f"house_{h}",0)
                color="#0a7a3a" if score>=5 else ("#d97706" if score>=4 else "#c0392b")
                row.append(Paragraph(f"<font color='{color}'><b>{score}</b></font>",
                    ParagraphStyle("c",alignment=TA_CENTER,fontSize=9,leading=12)))
            sv=sarva[h-1]
            sv_color="#0a7a3a" if sv>=28 else ("#d97706" if sv>=22 else "#c0392b")
            row.append(Paragraph(f"<font color='{sv_color}'><b>{sv}</b></font>",
                ParagraphStyle("c",alignment=TA_CENTER,fontSize=10,leading=12)))
            rows.append(row)
        # Add total row
        tot_row=[Paragraph("<b>TOTAL</b>",body_small)]
        for p in planet_list:
            tot_row.append(Paragraph(f"<b>{bav[p].get('total',0)}</b>",
                ParagraphStyle("c",alignment=TA_CENTER,fontSize=9,leading=12)))
        grand=sum(sarva)
        tot_row.append(Paragraph(f"<b>{grand}</b>",
            ParagraphStyle("c",alignment=TA_CENTER,fontSize=10,leading=12)))
        rows.append(tot_row)
        col_w=[1.5*cm]+[1.3*cm]*len(planet_list)+[1.8*cm]
        t=Table(rows,colWidths=col_w)
        t.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0),INDIGO),("TEXTCOLOR",(0,0),(-1,0),CREAM),
            ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,0),8),
            ("LINEBELOW",(0,0),(-1,0),1,GOLD),
            ("BACKGROUND",(0,-1),(-1,-1),GREY_LT),("FONTNAME",(0,-1),(-1,-1),"Helvetica-Bold"),
            ("ROWBACKGROUNDS",(0,1),(-1,-2),[white,GREY_LT]),
            ("ALIGN",(1,0),(-1,-1),"CENTER"),
            ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
            ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
            ("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4),
            ("GRID",(0,0),(-1,-1),0.3,GREY_LT)]))
        flow.append(t)
        flow.append(Spacer(1,0.3*cm))
        # Identify strongest / weakest houses
        sv_max_h=sarva.index(max(sarva))+1; sv_min_h=sarva.index(min(sarva))+1
        flow.append(to_para(
            f"<b>Strongest house:</b> H{sv_max_h} with <b>{max(sarva)}</b> bindus — "
            f"planetary transits through this house bring the most benefit and life advancement.<br/>"
            f"<b>Weakest house:</b> H{sv_min_h} with <b>{min(sarva)}</b> bindus — "
            f"transits here require caution; external support helps navigate challenges.<br/>"
            f"<b>Grand total:</b> {grand} bindus — "
            f"{'Above average strength (>280 = excellent)' if grand>280 else 'Average range (220-280 = balanced)' if grand>220 else 'Below average — focused remedies recommended'}.",
            body_small))
        flow.append(PageBreak())
    except Exception as exc:
        print(f"[ashtakavarga] WARNING: {exc}")

    # ─── SAMUDRIKA LAKSHANA — Face & Body Reading ───
    try:
        from face_reading import face_reading_summary
        fr = face_reading_summary(chart)
        flow.append(to_para("SAMUDRIKA LAKSHANA — FACE & BODY READING",h1))
        flow.append(to_para("Physical features predicted from planetary chart | Classical Samudrika Shastra",h1_sub))
        flow.append(to_para(
            "Samudrika Shastra predicts physical appearance from the horoscope — not as a certainty but "
            "as the 'default template' when nature has free rein. The dominant planets shape face, body, "
            "complexion, and expressions. Cross-verify these patterns against your own features.",body))
        flow.append(Spacer(1,0.3*cm))
        FACE_LABELS = {
            "predicted_face_shape":"Face Shape",
            "predicted_eye_size":"Eye Character",
            "predicted_nose_type":"Nose Type",
            "predicted_lip_type":"Lip Fullness",
            "predicted_chin_strength":"Chin / Jaw",
            "predicted_complexion":"Complexion",
            "dominant_feature":"Dominant Feature",
            "interpretation":"Overall Reading",
            "verification_tip":"Verification Tip",
        }
        for key,label in FACE_LABELS.items():
            val=fr.get(key)
            if not val: continue
            if isinstance(val,list): val=", ".join(val)
            is_main = key in ("interpretation","verification_tip")
            flow.append(to_para(
                f"<b>{label}:</b> {val}",
                body if is_main else body_small))
            flow.append(Spacer(1,0.1*cm))
        flow.append(PageBreak())
    except Exception as exc:
        print(f"[face_reading] WARNING: {exc}")

    # ─── PALMISTRY — Hand & Palm Reading from Chart ───
    try:
        from palmistry_engine import palmistry_summary
        pm = palmistry_summary(chart)
        flow.append(to_para("PALMISTRY — HAND & PALM PREDICTIONS",h1))
        flow.append(to_para("Expected hand shape, mounts, lines, and marriage lines | Classical Hasta Samudrika",h1_sub))
        flow.append(to_para(
            "Classical Hasta Samudrika (hand analysis) is derived from the same planetary signatures "
            "as the horoscope. Strong Jupiter shows a developed Jupiter mount; strong Venus shows "
            "a full Venus mount; Sun in 5th/10th shows a clear Apollo line. These are predicted "
            "tendencies, not certainties — confirm against your actual hand.",body))
        flow.append(Spacer(1,0.3*cm))
        PALM_LABELS = {
            "expected_hand_shape":("Hand Type", True),
            "dominant_mounts_predicted":("Dominant Mounts (developed)", True),
            "dominant_lines_predicted":("Key Lines Present", False),
            "fingerprint_pattern_predicted":("Fingerprint Pattern", False),
            "marriage_lines_count_expected":("Marriage Line Count", False),
        }
        for key,(label,bold) in PALM_LABELS.items():
            val=pm.get(key)
            if val is None: continue
            if isinstance(val,list): val="; ".join(str(x) for x in val)
            flow.append(to_para(
                f"{'<b>' if bold else ''}{label}:{'</b>' if bold else ''} {val}",body_small))
            flow.append(Spacer(1,0.1*cm))
        # Extra keys
        for k,v in pm.items():
            if k in PALM_LABELS: continue
            if not v: continue
            if isinstance(v,list): v="; ".join(str(x) for x in v)
            flow.append(to_para(f"<b>{k.replace('_',' ').title()}:</b> {str(v)[:200]}",body_small))
            flow.append(Spacer(1,0.08*cm))
        flow.append(PageBreak())
    except Exception as exc:
        print(f"[palmistry] WARNING: {exc}")

    # ─── VASTU SHASTRA — Directional Analysis ───
    try:
        from vastu_shastra import vastu_summary
        vs = vastu_summary(chart)
        flow.append(to_para("VASTU SHASTRA — DIRECTIONAL HARMONY",h1))
        flow.append(to_para("Ideal house directions, room placement, and doshas for this lagna",h1_sub))
        flow.append(to_para(
            "Vastu Shastra aligns living spaces with planetary energies for maximum well-being. "
            "Each planet governs a cardinal/diagonal direction. The native's chart determines which "
            "directions are most beneficial and which room placements best support health, wealth, and harmony.",body))
        flow.append(Spacer(1,0.3*cm))
        pnd=vs.get("primary_native_direction")
        if pnd:
            flow.append(to_para(f"<b>Your primary power direction:</b> <font color='#5d2e8c'>{pnd}</font>",body))
        # Ranked directions table
        rd=vs.get("ranked_directions",[])
        if rd:
            flow.append(Spacer(1,0.2*cm))
            flow.append(to_para("<b>Direction Ranking (higher = more beneficial):</b>",body_small))
            rows=[["DIRECTION","SCORE","RULING PLANET","USE FOR"]]
            dir_uses={"East":"Office, Study, Pooja room","West":"Children's room, Storage",
                      "North":"Treasury, Finance, Locker","South":"Bedroom, Rest",
                      "Northeast":"Pooja/Meditation room","Northwest":"Guest room, Garage",
                      "Southeast":"Kitchen, Fire elements","Southwest":"Master bedroom, Heavy furniture"}
            for d in rd:
                dn=d.get("direction","?"); sc=d.get("score",0)
                color="#0a7a3a" if sc>=7 else ("#d97706" if sc>=5 else "#c0392b")
                rows.append([
                    Paragraph(f"<b>{dn}</b>",body_small),
                    Paragraph(f"<font color='{color}'><b>{sc}/10</b></font>",
                        ParagraphStyle("c",alignment=TA_CENTER,fontSize=9,leading=12)),
                    Paragraph(d.get("planet",d.get("ruler","?")),body_small),
                    Paragraph(dir_uses.get(dn.split(" (")[0].strip(),""),body_small),
                ])
            t=Table(rows,colWidths=[3.5*cm,1.8*cm,2.5*cm,6.2*cm])
            t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),INDIGO),
                ("TEXTCOLOR",(0,0),(-1,0),CREAM),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
                ("FONTSIZE",(0,0),(-1,0),8),("LINEBELOW",(0,0),(-1,0),1,GOLD),
                ("ROWBACKGROUNDS",(0,1),(-1,-1),[white,GREY_LT]),
                ("ALIGN",(1,0),(1,-1),"CENTER"),
                ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
                ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6),
                ("LEFTPADDING",(0,0),(-1,-1),6)]))
            flow.append(t)
        # Ideal room placements
        rp=vs.get("ideal_room_placements",{})
        if rp:
            flow.append(Spacer(1,0.3*cm))
            flow.append(to_para("<b>Ideal Room Placements:</b>",body_small))
            for room,info in list(rp.items())[:8]:
                ideal=info.get("ideal","?") if isinstance(info,dict) else str(info)
                reason=info.get("reason","") if isinstance(info,dict) else ""
                flow.append(to_para(
                    f"&nbsp;&bull; <b>{room}:</b> {ideal}"+(f" — <i>{reason[:80]}</i>" if reason else ""),
                    body_small))
        # Doshas
        doshas=vs.get("common_doshas_to_check",[])
        if doshas:
            flow.append(Spacer(1,0.2*cm))
            flow.append(to_para("<b>Common Vastu Doshas to Check:</b>",body_small))
            for d in (doshas if isinstance(doshas,list) else [doshas])[:5]:
                flow.append(to_para(f"&nbsp;&bull; {d}",body_small))
        flow.append(PageBreak())
    except Exception as exc:
        print(f"[vastu_shastra] WARNING: {exc}")

    # ─── CLOSING ───
    flow.append(Spacer(1,4*cm))
    flow.append(to_para("END OF READING",h1))
    flow.append(to_para(
        "Generated by Atro Vedic Engine · 34 classical Jyotish texts · 8,239 rules · "
        "Lahiri True Sidereal · Cross-validated to 0.011° precision.",body))
    flow.append(Spacer(1,0.5*cm))
    flow.append(to_para(
        "<i>Vedic astrology shows tendencies and probabilities, not certainties. "
        "Free will and conscious action shape how each indicated event unfolds.</i>",
        ParagraphStyle("c",parent=body,alignment=TA_CENTER,textColor=PURPLE)))

    
    # ─── TRUTH REPORT SECTION ───
    try:
        truth_flow = build_truth_report_section(chart)
        flow.extend(truth_flow)
    except Exception as exc:
        print(f"[truth_report] WARNING: {exc}")

    print(f"Building PDF for {chart['name']} with {len(flow)} elements...")

    doc.build(flow)
    sz=out_path.stat().st_size/1024
    print(f"DONE: {out_path}  ({sz:.0f} KB)")


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--chart",required=True)
    ap.add_argument("--out",default=None)
    args=ap.parse_args()
    cp=Path(args.chart)
    if not cp.is_absolute():
        for cand in [CHARTS/args.chart, ATRO/args.chart, Path.cwd()/args.chart]:
            if cand.exists():
                cp=cand; break
    chart_path=cp
    if not args.out:
        cd=json.load(open(chart_path,encoding="utf-8"))
        nc=cd["name"].upper().replace(" ","_").replace(".","")
        args.out=f"{nc}_FULL_REPORT.pdf"
    generate(chart_path,args.out)


if __name__=="__main__":
    main()
