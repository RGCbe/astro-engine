# Atro Vedic Engine — User Guide

**For:** Vedic astrology enthusiasts, jyotish students, and curious readers.
**You don't need to be a programmer** to use this engine, but you do need to be comfortable copy-pasting commands into a terminal once.

> **See also:** [MODULE_INDEX.md](../runtime/MODULE_INDEX.md) (technical inventory) · [UNIFIED_ARCHITECTURE.md](UNIFIED_ARCHITECTURE.md) (system design) · [API_REFERENCE.md](API_REFERENCE.md) (every function)

---

## Table of Contents

1. [What is the Atro Engine?](#what-is-the-atro-engine)
2. [Installing the Engine](#installing-the-engine)
3. [Creating Your Birth Chart](#creating-your-birth-chart)
4. [Quick Start](#quick-start)
5. [The 9 CLI Modes](#the-9-cli-modes)
6. [Reading the PDF Report](#reading-the-pdf-report)
7. [Running the Web Server](#running-the-web-server)
8. [Interpreting Yoga Severity](#interpreting-yoga-severity)
9. [Interpreting Dasha Periods](#interpreting-dasha-periods)
10. [Interpreting Transit Triggers](#interpreting-transit-triggers)
11. [FAQ](#frequently-asked-questions)
12. [Sanskrit Glossary](#sanskrit-glossary)

---

## What is the Atro Engine?

Atro is a Vedic astrology engine that takes a birth chart and produces a full reading — not a horoscope app's three-paragraph summary, but a deep reading the way a senior jyotish scholar would do it: chart-by-chart, with classical sources cited, every yoga checked, every dasha mapped, every transit watched.

**What it covers (today):**

- All 9 traditional grahas (Sun → Ketu)
- 16 divisional charts (D1, D2, D3, D4, D7, D9, D10, D12, D16, D20, D24, D27, D30, D40, D45, D60)
- 5 dasha systems (Vimshottari at 4 levels, Ashtottari, Yogini, Char, Mudda)
- 45+ named yogas (Pancha Mahapurusha, Raja Yoga, Dhana Yoga, Doshas, Nabhasa, etc.)
- Full Shadbala (6-fold strength) — research-grade
- Full Ashtakavarga (Bhinna + Sarva + Sodhita reductions + Kakshya bala)
- 8-Kuta marriage compatibility (Ashtakuta — 36 points)
- Annual chart (Tajik / Varshaphala)
- Eclipse impact analysis
- Sade Sati cycle map
- KP (Krishnamurti Paddhati) sub-lord chart
- Jaimini system (Karakas, Padas, Argala)
- Lal Kitab karmic debts + remedies
- Bhrigu Nadi rules + Atmakaraka soul mission
- Medical astrology (body × planet × house)
- Numerology (Mulanka, Bhagyanka, Name)
- 28 Tajik sahams (sensitive points)
- Special lagnas (Hora, Ghatika, Bhava, Indu, Pranapada, Chandra, Surya)
- Upagrahas (Gulika, Mandi, Dhuma, etc.)
- Prashna (horary chart) with KP verdict
- Muhurta (auspicious date finder)
- Multi-language support (English + Tamil)
- 38 classical books in the corpus, 11,692 indexed passages

**What it produces:**

- A ~55-page PDF report (~150 KB)
- A JSON dump of every analysis result
- A live FastAPI server with `/api/jathagam` endpoint
- Console summaries for quick reading
- 30/90/365-day forecasts with day-by-day verdicts

**What it isn't:**

- A horoscope app (no daily push notifications)
- A natal chart calculator alone (it's a full reading engine)
- A web service (not hosted publicly — it runs on your computer)

---

## Installing the Engine

### Prerequisites

You need:
- **Python 3.10 or newer** (check with `python --version`)
- **pip** (comes with Python)
- About 500 MB free disk space (for the corpus + ephemeris files)

### Step 1 — Get the Code

The engine lives at `F:/Atro/` on the developer's machine. If you have the project folder, you're set. Otherwise, clone or copy the entire `F:/Atro/` directory.

### Step 2 — Install Dependencies

Open a terminal in the `F:/Atro/` folder and run:

```bash
pip install -r requirements.txt
```

This installs:
- `pyswisseph` — Swiss Ephemeris (planetary positions)
- `reportlab` — PDF generation
- `fastapi` — web server
- `uvicorn` — ASGI runner
- `pydantic` — data validation

### Step 3 — Verify

Run:
```bash
python runtime/atro_cli.py --chart manoj --mode check
```

You should see:
```
=== ENGINE INTEGRITY CHECK for Manoj ===
Engine version: v13.0
Modules total: 50
  OK:    50
  ERROR: 0
✓ All modules running cleanly.
```

If you see errors, see [FAQ](#frequently-asked-questions).

---

## Creating Your Birth Chart

The engine reads charts from JSON files in `F:/Atro/charts/`. To add yours:

### What You Need

You need to know:
- **Date of birth** (day, month, year)
- **Time of birth** (hour and minute, ideally accurate to within 5 minutes)
- **Place of birth** (latitude and longitude — Google "[city] latitude longitude")

### Option A — Use a Sample Chart Generator

If you're comfortable running scripts, use one of the demo files in `runtime/`:

```bash
python runtime/compute_sree.py
```

This generates `charts/sree_chart.json` from hardcoded birth data. Modify `compute_sree.py` (open in any text editor) to use **your** birth data, then run again.

### Option B — Hand-Write the JSON

Create a file `F:/Atro/charts/yourname_chart.json`:

```json
{
  "name": "Your Name",
  "birth": {
    "year": 1990,
    "month": 6,
    "day": 15,
    "hour": 14,
    "min": 30,
    "lat": 13.0827,
    "lon": 80.2707,
    "place": "Chennai"
  },
  "lagna": "Leo",
  "lagna_idx": 4,
  "lagna_lord": "Sun",
  "ayanamsa": 23.85,
  "positions": {
    "Sun":     {"rasi": "Taurus", "rasi_idx": 1, "house": 10, "degree": 10.5, "nakshatra": "Krittika"},
    "Moon":    {"rasi": "Cancer", "rasi_idx": 3, "house": 12, "degree": 18.3, "nakshatra": "Ashlesha"},
    "Mars":    {"rasi": "Leo", "rasi_idx": 4, "house": 1, "degree": 5.0, "nakshatra": "Magha"},
    "Mercury": {"rasi": "Taurus", "rasi_idx": 1, "house": 10, "degree": 22.0, "nakshatra": "Rohini"},
    "Jupiter": {"rasi": "Cancer", "rasi_idx": 3, "house": 12, "degree": 8.5, "nakshatra": "Pushya"},
    "Venus":   {"rasi": "Aries", "rasi_idx": 0, "house": 9, "degree": 14.0, "nakshatra": "Bharani"},
    "Saturn":  {"rasi": "Capricorn", "rasi_idx": 9, "house": 6, "degree": 25.0, "nakshatra": "Dhanishta"},
    "Rahu":    {"rasi": "Aquarius", "rasi_idx": 10, "house": 7, "degree": 12.0, "nakshatra": "Shatabhisha"},
    "Ketu":    {"rasi": "Leo", "rasi_idx": 4, "house": 1, "degree": 12.0, "nakshatra": "Magha"}
  },
  "moon_rasi": "Cancer",
  "janma_nakshatra": "Ashlesha",
  "janma_nakshatra_lord": "Mercury"
}
```

You can get the planetary positions from any online Vedic chart calculator (use **Lahiri ayanamsa**) like AstroSage, Drik Panchang, or Prokerala. Copy the values into the JSON exactly. Save the file.

### Option C — Use the FastAPI Server (easiest if you want to skip JSON entirely)

See [Running the Web Server](#running-the-web-server). The API computes positions for you from just date/time/place.

---

## Quick Start

Once your chart JSON is in `F:/Atro/charts/`, you can run any of the 9 modes. The simplest is `summary`:

```bash
python runtime/atro_cli.py --chart yourname --mode summary
```

You'll see something like:

```
╔══════════════════════════════════════════════════════════════
║  YOUR NAME — VEDIC ENGINE SUMMARY  (engine v13.0)
╚══════════════════════════════════════════════════════════════
  As of: 2026-05-06 14:30
  Born:  15-06-1990 14:30 | Chennai
  Lagna: Leo | Moon: Cancer | Nakshatra: Ashlesha

  ★ 8 ACTIVE YOGAS
      ★★★★★ Gaja-Kesari Yoga
      ★★★★  Budha-Aditya Yoga
      ★★★★  Vipareeta Raja Yoga
      ★★★   Saraswati Yoga
      ★★    Chandra-Mangala Yoga
  ⊙ CURRENT DASHA: Mercury (until 2028-04-12)
    └ AD: Saturn
  ⏳ Sade Sati: Setting Phase (last 2.5 years)
  📅 Life events flagged: 14 bands
  💍 Spouse type: Cancer-quality, Education
     Marriage window: 2027-2030 (Mercury MD, Venus AD)
  🔢 Mulanka: 6 (Venus) | Bhagyanka: 3

  Modules ok: 50/50
```

If the chart didn't load, you may have used the wrong filename. Try:
```bash
python runtime/atro_cli.py --chart yourname.json --mode summary
# or
python runtime/atro_cli.py --chart "yourname_chart" --mode summary
```

---

## The 9 CLI Modes

The CLI accepts:
```bash
python runtime/atro_cli.py --chart NAME --mode MODE [--out FILE] [--chart2 NAME] [--days N]
```

### 1. `summary` (default)

Quick console output, ~30 lines. Best for "what's going on right now."

```bash
python runtime/atro_cli.py --chart yourname --mode summary
```

### 2. `pdf`

Generates a full ~55-page PDF report with 18 life-domain pages, 9 Maha Dasha chapters, charts, EXPECT/WATCH tables, snapshots.

```bash
python runtime/atro_cli.py --chart yourname --mode pdf
# Output: reports/YOURNAME_FULL_REPORT.pdf
```

You can override the output filename:
```bash
python runtime/atro_cli.py --chart yourname --mode pdf --out my_report.pdf
```

### 3. `json`

Dumps the full analysis as JSON. Good for feeding into other tools or just inspecting every value the engine knows.

```bash
python runtime/atro_cli.py --chart yourname --mode json
# Output: reports/yourname_analysis.json
```

### 4. `present`

The "right now" reading — current dasha, transits hitting, sade sati phase, active yogas, one-paragraph synthesis.

```bash
python runtime/atro_cli.py --chart yourname --mode present
```

### 5. `forecast`

Day-by-day forecast with verdict per day:

```bash
python runtime/atro_cli.py --chart yourname --mode forecast --days 30
```

Output:
```
=== 30-DAY FORECAST for Your Name ===
   2026-05-06 (Tue)        +1  Favorable for travel    Mercury MD / Saturn AD
   2026-05-07 (Wed)        +2  Excellent — push        Mercury MD / Saturn AD
 ★ 2026-05-08 (Thu)        +3  Outstanding             Mercury MD / Saturn AD
   2026-05-09 (Fri)         0  Neutral                 Mercury MD / Saturn AD
 ▼ 2026-05-10 (Sat)        -2  Avoid major decisions   Mercury MD / Saturn AD
   ...
```

`★` marks best days. `▼` marks worst days. Default is 30 days; use `--days 90` or `--days 365` for longer.

### 6. `events`

Lifetime events table — when each major life event is most likely:

```bash
python runtime/atro_cli.py --chart yourname --mode events
```

Output:
```
=== LIFETIME EVENTS for Your Name (14 bands) ===

AGE  WINDOW              SEV  EVENT
  1  Aug 1996            ★★★★★ Father — accident/health
  6  Jul 1996 - Mar 2002  ★★★★ Family financial loss
 12  Jul 2002 - Aug 2010  ★★★★ Multiple home relocations
 14  Aug 2010             ★★★★ Built new house
 17  Apr 2012             ★★★ Lost legal case + completed school
 27  Jun 2024 - Dec 2027  ★★★★ Career breakthrough
 30  Mar 2027 - Aug 2030  ★★★★ Marriage
 ...
```

### 7. `yogas`

List all active yogas with severity stars and book sources:

```bash
python runtime/atro_cli.py --chart yourname --mode yogas
```

Output:
```
=== 8 ACTIVE YOGAS for Your Name ===

  ★★★★★ ☆☆☆☆☆ Gaja-Kesari Yoga                      (wealth + reputation)
        Source: BPHS Ch. 36, Saravali Ch. 17
  ★★★★ ☆☆☆☆☆ Budha-Aditya Yoga                       (intellect + speech)
        Source: Phaladeepika
  ★★★★ ☆☆☆☆☆ Vipareeta Raja Yoga (Sarala)            (rise from defeat)
        Source: BPHS Ch. 35
  ...
```

### 8. `match`

Compatibility match between two charts. Both charts must already exist:

```bash
python runtime/atro_cli.py --chart boy --chart2 girl --mode match
```

Output:
```
=== ASHTAKUTA MATCH ===

  Boy:  John (Leo / Magha)
  Girl: Priya (Aries / Ashwini)

  Varna (1)             █ 1
  Vasya (2)             ██ 2
  Tara (3)              ██░ 2
  Yoni (4)              ███░ 3
  Graha-Maitri (5)      ████░ 4
  Gana (6)              ██████ 6
  Bhakoot (7)           ███████ 7
  Nadi (8)              ████████ 8

  TOTAL: 33/36 (91.7%) — Excellent match
```

### 9. `check`

Engine integrity check — runs every module and reports which work/fail. Use this if you suspect a bug.

```bash
python runtime/atro_cli.py --chart yourname --mode check
```

---

## Reading the PDF Report

The PDF (~55 pages, 977 elements, ~150 KB) is the most comprehensive output. Here's what each section means:

### Page 1 — Cover & Snapshot
- Birth data summary (date, time, place)
- Lagna, Moon sign, Janma Nakshatra
- Active Maha Dasha + sub-period
- Top 5 yogas
- "Currently active" Vipareeta or major yoga callout
- Marriage window (future) box

### Pages 2-19 — Domain Pages (one per life area)
Each domain page has:
1. **Snapshot card** — bullet facts (e.g., "7th lord is Saturn in 6H — delays in marriage")
2. **Intro paragraph** — chart-specific narrative (not a template)
3. **EXPECT / WATCH tables** — what to expect, what to watch out for, in current and future MDs
4. **Yoga callouts** — yogas affecting this domain

The 18 domains (in order):
1. Self & Personality
2. Parents (Father / Mother)
3. Siblings
4. Education
5. Marriage
6. Children
7. Career & Profession
8. Wealth & Finances
9. Health & Body
10. Travel
11. Property & Home
12. Status & Public Image
13. Friends & Social Circle
14. Spirituality
15. Talents & Innate Skills
16. Past Lives & Karma
17. Annual Chart (current year)
18. Specific Concerns

### Pages 20-50ish — Maha Dasha Chapters (9 chapters, one per planet's MD)

Each MD chapter has:
- **Snapshot card** — MD start/end, age range, dignity of lord, theme
- **Intro narrative** — what this MD means for THIS chart (not template)
- **EXPECT / WATCH tables** — the 2-column expect/watch breakdown
- **Sub-period commentary** for each AD inside the MD (Antardasha)
- **Currently-active highlight** if you're in this MD now

### Final Pages — Closing
- Yoga catalog (all detected yogas with book citations)
- Remedies (per affliction + Lal Kitab debts)
- Numerology snapshot
- Disclaimer

### How to Read It

**First 15 minutes:** Read Page 1 + the Domain Page for your most pressing concern (Marriage / Career / Health / etc.).

**Next 30 minutes:** Read the chapter for your *current* Maha Dasha. This is what's happening now.

**When you have time:** Skim all 18 domain pages — astrology surprises you. The Talents / Past Lives / Spirituality pages often reveal more than the obvious ones.

---

## Running the Web Server

If you'd rather make HTTP calls than run the CLI, start the FastAPI server:

```bash
python main.py
# OR
uvicorn main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

Now you can POST to the chart endpoint. Example using `curl`:

```bash
curl -X POST http://127.0.0.1:8000/api/jathagam \
  -H "Content-Type: application/json" \
  -d '{
    "year": 1990,
    "month": 6,
    "day": 15,
    "time": "14:30",
    "lat": 13.0827,
    "lon": 80.2707
  }'
```

Or open `http://127.0.0.1:8000/docs` in your browser — FastAPI auto-generates an interactive UI where you can fill in the form and click "Try it out."

The response is a single big JSON dict with:
- `lagnam`, `navamsa_lagnam`, `arudha_lagna` (your ascendants)
- `panchangam` (tithi, vara, yoga, karana, nakshatra of birth)
- `current_dasha`, `current_antardasha`, `current_pratyantar_dasha`
- `all_planet_positions` (with D9, D10, D60, dignity, nakshatra)
- `house_predictions` (per-planet with multi-book corpus citations)
- `detected_yogas` (with book evidence)
- `shadbala` (6-fold strength)
- `ashtakavarga` (bindus per house, total)
- `gochar` (today's transits with rules)
- `kp_analysis` (KP sub-lord layer)
- `advanced_reading_html` (rich HTML for embedding in a frontend)
- `synthesis` (final integrated text)

---

## Interpreting Yoga Severity

Yogas in the engine come with a **severity score from 1 to 5**:

| Score | Meaning |
|---|---|
| **★★★★★ (5)** | Strongly active — full classical conditions met. The yoga's effect WILL show up. |
| **★★★★ (4)** | Active — conditions met but with one minor compromise (planet retrograde, slightly off-degree, etc.). The effect will show but maybe muted. |
| **★★★ (3)** | Moderately active — conditions partially met. The seed is there but needs a transit/dasha trigger to bloom. |
| **★★ (2)** | Weak — barely qualifies. Look for the effect in specific years rather than continuously. |
| **★ (1)** | Trace — academic interest only. Probably won't manifest in life. |

**Rule of thumb:** focus on the 4-and-5-star yogas. They're what makes your chart YOUR chart.

A few specific yoga families to know:

- **Pancha Mahapurusha (Ruchaka, Bhadra, Hamsa, Malavya, Shasha)** — born great. Indicates exceptional ability in the planet's domain. Mars Ruchaka = warrior/athlete/surgeon. Jupiter Hamsa = teacher/sage.
- **Raja Yoga** — political or organizational rise. The chart shows authority potential.
- **Dhana Yoga** — wealth combinations. Specific years/dashas activate the wealth.
- **Doshas (Manglik, Pitra, Matra, Kaal-Sarpa)** — karmic impediments. Don't panic — most have classical cancellations. The engine checks for cancellations automatically and tells you the *net* result.
- **Vipareeta Raja Yoga** — rise from defeat. A blessing in disguise (often comes after a setback).

---

## Interpreting Dasha Periods

A **Dasha** is a planetary period — a window of life when one specific planet is "running the show" for you.

The most-used system is **Vimshottari Dasha**, which runs across a 120-year cycle and is broken into 4 levels:

- **Maha Dasha (MD)** — the major life chapter. Ranges from 6 to 20 years depending on the planet.
- **Antar Dasha (AD)** — the sub-chapter inside an MD. Ranges from a few months to a few years.
- **Pratyantar Dasha (PD)** — the sub-sub-chapter. Days to months.
- **Sookshma Dasha (SD)** — the moment-level chapter. Hours to days.

The engine computes all 4 levels.

### What Each Lord Means

When the engine says "your current MD is Mercury," that means Mercury's archetypal themes dominate this chapter:

| MD Lord | Themes |
|---|---|
| **Sun** | Authority, status, government work, soul-purpose, father |
| **Moon** | Mother, emotions, public-facing roles, home life |
| **Mars** | Action, conflict, real estate, surgery, sports, aggression |
| **Mercury** | Communication, business, learning, travel, siblings, intellect |
| **Jupiter** | Wisdom, teaching, marriage, children, religion, expansion |
| **Venus** | Love, marriage, art, luxury, vehicles, sensual life |
| **Saturn** | Discipline, hardship, service, longevity, delays, profession-mastery |
| **Rahu** | Worldly ambition, foreign matters, technology, obsession, sudden gains |
| **Ketu** | Detachment, spirituality, loss, research, moksha |

### How the Engine Reads a Dasha

The engine looks at:
1. **Where the MD lord sits in your chart** (which house, sign, dignity)
2. **Whether the MD lord is afflicted or strong** (Shadbala)
3. **Yogas the MD lord participates in**
4. **Transits hitting the MD lord during this period**
5. **The AD lord modifying the MD theme**

It then writes the EXPECT / WATCH tables for that period. Read those carefully — they're chart-specific, not template.

### "I'm in Saturn MD — am I doomed?"

No. Saturn MDs CAN be hard, but only if Saturn is afflicted. If Saturn is **own sign** (Capricorn or Aquarius), **exalted** (Libra), or part of a Raja Yoga, Saturn MD is *the best 19 years of your life* — you mature, build, and earn lasting respect. Read the chapter, not the planet name.

---

## Interpreting Transit Triggers

A **transit** is the position of a planet RIGHT NOW, regardless of when you were born. Saturn is moving through Pisces today (May 2026). That's a transit.

The engine flags transits that "trigger" something in your natal chart — meaning a transiting planet is exactly aspecting (within 2.5° of) a natal point that matters.

### The 4 Trigger Types

1. **Transit conjunct natal planet** — strongest. Re-activates that planet's themes.
2. **Transit aspecting natal planet** — moderate. Echoes that planet's themes.
3. **Transit through natal house** — runs that house's affairs for the duration.
4. **Transit through natal nakshatra** — fine-grained activation (especially Saturn over your Janma Nakshatra → Sade Sati core phase).

### Saturn Transits Specifically

Saturn moves slowly (2.5 years per sign), so its transits are the most important. The engine specifically tracks:

- **Sade Sati** — Saturn's 7.5-year passage through 12th, 1st, 2nd from Moon. A major life-restructuring period.
- **Saturn Return** — Saturn's return to its natal position (every ~29.5 years). Hits at age ~28 (first), ~58 (second), ~88 (third). Each one is a profound "who am I really" moment.
- **Saturn over natal Sun** — challenges to authority, ego, father themes.
- **Saturn over natal Moon** — emotional gravity, mother themes.

### What to Do With Trigger Info

Don't react to every trigger. The engine fires many — most are noise. Look for:
- **Multiple triggers stacking the same week** — that's a real life-event window.
- **Slow-planet triggers (Saturn, Jupiter, Rahu, Ketu)** — those last weeks/months and are when "things actually happen."
- **Fast-planet triggers (Sun, Moon, Mars, Mercury, Venus)** — those last hours/days and color the day, not the year.

---

## Frequently Asked Questions

### "Can I trust the engine over a real astrologer?"

The engine has been **validated against 6 real-life events on Manoj's chart** (father accident, family loss, relocations, marriage, etc. — see [MODULE_INDEX.md](../runtime/MODULE_INDEX.md#verified-test-cases)). It rivals any computer-generated chart you'll find online. But:

- A real astrologer adds **synthesis intuition** the engine can't (yet).
- The engine is conservative — it won't claim things it can't justify from classical sources.
- Use the engine to *prepare* for an astrologer consult, not replace one.

### "Why is my Lagna different here vs. AstroSage?"

You probably used different ayanamsa values. The engine uses **Lahiri** (the most common in India). AstroSage may use Lahiri or KP-Lahiri. Krishnamurti uses KP. Check your input chart's `ayanamsa` field — should be ~23.85 for ~2026 birth dates with Lahiri.

### "The engine says I have Manglik Dosha — am I going to harm my spouse?"

Almost certainly not. The engine reports the dosha AND its cancellations. Most Manglik doshas are cancelled by:
- Spouse also being Manglik
- Mars in own sign or exalted
- Mars aspected by Jupiter
- Both partners being Manglik

Read the full Manglik report (in the PDF, Doshas section). If the engine says "Manglik but cancelled — net effect: nil" — believe it.

### "How accurate are the event predictions?"

For **major events with strong dasha + transit confluence (4-5 stars)** — fairly reliable. The window is usually right within ±18 months.

For **3-star events** — interpret as "favorable terrain" not "guarantee." Free will and effort matter.

For **1-2 star events** — don't bother. The engine is just noting weak echoes.

### "Why does the report mention 'Tier 1 / Tier 2 / Tier 3'?"

Those are internal coverage tiers. The engine has full coverage for some traditions (Tier 1: BPHS, Saravali, Phaladeepika, Jaimini basics) and partial for others (Tier 2: KP detail, Lal Kitab full, Tajik annual). Don't worry about tier labels in normal reading — they're for the developer.

### "Can I add more books to the corpus?"

Yes. Drop a `.txt` (or `.pdf` extracted to `.txt`) in `F:/Atro/books/` and run:
```bash
python runtime/book_corpus_indexer.py
```
This rebuilds the index. The new book's passages become citable in the next report.

### "Is the engine free / open-source?"

It's a personal-use project. Not currently published. Contact the maintainer for licensing.

### "I'm getting an error when I run the CLI"

Most common errors:
- `ModuleNotFoundError: No module named 'swisseph'` → run `pip install pyswisseph`
- `FileNotFoundError: No chart found for 'yourname'` → your JSON isn't in `F:/Atro/charts/`. Check the filename matches.
- `KeyError: 'positions'` → your chart JSON is missing the `positions` field. See [Creating Your Birth Chart](#creating-your-birth-chart).
- Encoding errors on Windows → run `chcp 65001` in your terminal first to switch to UTF-8.

### "Tamil report?"

Use the engine module:
```python
from engine.client_report_v2_ta import generate_client_report_v2_ta
md = generate_client_report_v2_ta(chart)
print(md)
```
This returns a Tamil markdown report.

### "Can I run this on a server?"

Yes — `main.py` is a FastAPI app. Deploy with `uvicorn main:app --host 0.0.0.0 --port 8000` behind a reverse proxy. The engine itself is stateless, so it scales horizontally.

---

## Sanskrit Glossary

A reference for terms used in reports and this guide.

| Term | Meaning |
|---|---|
| **Antar Dasha (AD)** | Sub-period inside a Maha Dasha. |
| **Argala** | "Intervention" — a planet's influence on another house from a specific position (Jaimini concept). |
| **Arudha Pada** | Image of a house — how the world sees that area of life. |
| **Ashtakavarga** | Bindu (point) system showing planetary strength per sign. |
| **Atmakaraka** | "Soul significator" — the planet with the highest degree in the chart. Indicates soul's mission. |
| **Ayanamsa** | The offset between tropical and sidereal zodiac — about 23.85° in 2026 (Lahiri value). |
| **Bhava** | House (1-12). |
| **Bhinna Ashtakavarga** | Per-planet bindu chart. |
| **Chara Karaka** | "Variable significator" — the 8 highest-degree planets get karaka roles in Jaimini. |
| **Darakaraka (DK)** | Lowest-degree planet; signifies spouse. |
| **Dasha** | Planetary period. The most-used is Vimshottari. |
| **Dignity** | A planet's strength based on the sign it's in (Exalted / Own / Friend / Neutral / Enemy / Debilitated). |
| **Drishti** | Aspect — how a planet "looks at" other houses/planets. |
| **Dusthana** | "Bad" houses — 6, 8, 12. |
| **Gochar** | Transit. |
| **Janma Nakshatra** | Birth nakshatra (constellation the Moon was in at birth). |
| **Karaka** | Significator. Sun = soul, Moon = mind, Mars = energy, etc. |
| **Karakamsa** | Atmakaraka's position in the D9 chart — soul's deeper mission. |
| **Kendra** | Angular houses — 1, 4, 7, 10. Strong houses. |
| **Kuta** | Compatibility unit. Ashtakuta = 8 kutas summing to 36 points. |
| **Lagna** | Ascendant — the rising sign at birth. |
| **Lahiri** | The most common ayanamsa system in India. |
| **Maha Dasha (MD)** | Major planetary period. Ranges 6-20 years. |
| **Manglik Dosha** | Mars in 1, 2, 4, 7, 8, 12 — flagged for marriage compatibility. |
| **Marakesha** | Death-causing planets (in longevity analysis). |
| **Muhurta** | Auspicious moment for an event. |
| **Mulanka** | Numerology birth-day number. |
| **Mooltrikona** | A specific degree-range where a planet has special strength. |
| **Nakshatra** | One of 27 lunar mansions (each 13°20' of the zodiac). |
| **Nabhasa Yoga** | A family of 32 yogas based on the geometric pattern of all 7 visible planets. |
| **Navamsa (D9)** | The 9th divisional chart — most important after D1. Marriage and dharma. |
| **Padas** | Quarter-divisions of a nakshatra (each 3°20'). |
| **Panchanga** | 5-fold time analysis: Tithi, Vara, Yoga, Karana, Nakshatra. |
| **Parashari** | The astrology system from Brihat Parashara Hora Shastra (BPHS). The mainstream Vedic system. |
| **Phaladeepika** | Classical text by Mantreswara — major source for yogas. |
| **Pratyantar Dasha (PD)** | Sub-sub-period (under MD/AD). |
| **Prashna** | Horary chart — answers a question by casting at the moment of asking. |
| **Rahu / Ketu** | The lunar nodes — points where Moon's orbit crosses the ecliptic. Karmic indicators. |
| **Raja Yoga** | "Royal combination" — kendra-trikona lord combinations indicating rise. |
| **Rasi** | Sign. |
| **Sade Sati** | Saturn's 7.5-year transit through 12th-1st-2nd from Moon. |
| **Sahams** | 28 Tajik sensitive points (Punya, Vidya, Vivaha, Putra, etc.) |
| **Sarva Ashtakavarga** | Combined bindu chart across all planets. |
| **Saravali** | Classical text by Kalyana Varma — major source for yogas. |
| **Shadbala** | "6-fold strength" — composite strength score for each planet. |
| **Sookshma Dasha (SD)** | The 4th level of Vimshottari (after MD/AD/PD). |
| **Tajik** | Annual chart system — uses solar return + sahams + Mudda dasha. |
| **Tithi** | Lunar day (1-15 in each paksha). Each tithi has a specific quality. |
| **Trikona** | Trine houses — 1, 5, 9. Auspicious houses. |
| **Upachaya** | "Increasing" houses — 3, 6, 10, 11. Improve over time. |
| **Upagrahas** | Sub-grahas (Gulika, Mandi, Dhuma, etc.) — abstract sensitive points. |
| **Vara** | Day of the week. Each ruled by a planet. |
| **Vargottama** | A planet in the same sign in D1 and D9. Strong indicator. |
| **Varshaphala** | Annual chart — analysis of one specific year. |
| **Vimshottari** | The 120-year dasha system. The default in mainstream Vedic. |
| **Vipareeta Raja Yoga** | "Reverse Raja Yoga" — dusthana lords in dusthanas indicate rise from defeat. |
| **Yoga** | Combination — a specific planetary pattern with a named effect. (NOT the physical practice — though both are connected). |
| **Yoni** | "Womb" — animal nature attribute of nakshatras, used in Yoni Kuta. |

---

## Where to Go Next

- **For developers:** Read [API_REFERENCE.md](API_REFERENCE.md) and [UNIFIED_ARCHITECTURE.md](UNIFIED_ARCHITECTURE.md). Then explore `runtime/engine_orchestrator.py` to see how all 50 modules wire together.
- **For students of jyotish:** Read the PDF report from end to end. Then start adding charts of family/friends and compare what the engine says against what you know about them. That's the fastest way to learn yoga interpretation.
- **For curious readers:** Run the `summary` mode for yourself and 3-4 family members. Note which yogas keep showing up and which don't. Astrology becomes real when you see it consistently across people you know.

The engine is built to be a research tool, not an oracle. Use it as one input among many. Trust your own intuition above all software.

---

*"The stars impel, they do not compel."* — classical jyotish dictum.
