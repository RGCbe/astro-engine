"""
Mass Book Downloader v2 — Uses verified Archive.org item identifiers
and direct CDN URLs found via web research.
"""
import os
import sys
import urllib.request
import urllib.error
import time

BOOKS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "books")
os.makedirs(BOOKS_DIR, exist_ok=True)

# Verified item identifiers from Archive.org search
TARGETS = [
    # (filename, urls[], description)
    (
        "Carmen_Astrologicum_Dorotheus.pdf",
        [
            "https://archive.org/download/PingreeDS1976/PingreeDS1976.pdf",
            "https://ia601504.us.archive.org/31/items/PingreeDS1976/PingreeDS1976.pdf",
            "https://archive.org/download/dorotheus-carmen-astrologicum/CarmenAstrologicum.pdf",
        ],
        "Dorotheus of Sidon - Carmen Astrologicum (Pingree 1976)"
    ),
    (
        "Matheseos_Firmicus_Maternus.pdf",
        [
            "https://archive.org/download/matheseos00firm/matheseos00firm.pdf",
            "https://ia801405.us.archive.org/24/items/matheseos00firm/matheseos00firm.pdf",
            "https://archive.org/download/firmicusmaternus00firmuoft/firmicusmaternus00firmuoft.pdf",
        ],
        "Firmicus Maternus - Matheseos Libri VIII"
    ),
    (
        "Mansagari_Sanskrit.pdf",
        [
            "https://archive.org/download/mana-sagari-paddhati/mana-sagari-paddhati.pdf",
            "https://ia801501.us.archive.org/9/items/mana-sagari-paddhati/mana-sagari-paddhati.pdf",
            "https://archive.org/download/12817maanasagari035843mbp/12817maanasagari035843mbp.pdf",
        ],
        "Mansagari (Mana Sagari Paddhati) - Sanskrit Classical Vedic"
    ),
    (
        "Liber_Astronomiae_Bonatti.pdf",
        [
            "https://archive.org/download/liberastronomiae00bona/liberastronomiae00bona.pdf",
            "https://ia800509.us.archive.org/12/items/liberastronomiae00bona/liberastronomiae00bona.pdf",
            "https://archive.org/download/bonatti-liber-astronomiae/BonattLibAstro.pdf",
        ],
        "Guido Bonatti - Liber Astronomiae (13th century)"
    ),
    (
        "Dhruva_Nadi_Satyacharya.pdf",
        [
            "https://archive.org/download/DNSR4395/DNSR4395.pdf",
            "https://ia801509.us.archive.org/35/items/DNSR4395/DNSR4395.pdf",
            "https://archive.org/download/satyajatakamdhruvanadiramans.k.astrology_202003_357_T/satyajatakamdhruvanadiramans.k.astrology_202003_357_T.pdf",
        ],
        "Dhruva Nadi - Satyacharya"
    ),
    (
        "Bhrigu_Nadi_TMRao.pdf",
        [
            "https://archive.org/download/Jyotish/Book.%20Bhrigu%20Samhita%20T.M.Rao_text.pdf",
            "https://ia801004.us.archive.org/8/items/Jyotish/Book.%20Bhrigu%20Samhita%20T.M.Rao_text.pdf",
        ],
        "Bhrigu Samhita - T.M. Rao (Nadi Principles)"
    ),
    (
        "Jataka_Desh_Marga.pdf",
        [
            "https://archive.org/download/jatakadeshamarg00unkngoog/jatakadeshamarg00unkngoog.pdf",
            "https://ia600406.us.archive.org/7/items/jatakadeshamarg00unkngoog/jatakadeshamarg00unkngoog.pdf",
            "https://archive.org/download/in.ernet.dli.2015.405285/2015.405285.Jataka-Desh-Marga.pdf",
        ],
        "Jataka Desh Marga - Classical Vedic"
    ),
    (
        "Di_Tian_Sui_BaZi.pdf",
        [
            "https://archive.org/download/di-tian-sui-bazi/di-tian-sui-bazi.pdf",
            "https://archive.org/download/ditiansuicomprehensive/ditiansuicomprehensive.pdf",
            "https://ia801504.us.archive.org/15/items/di-tian-sui-bazi/DiTianSui_English.pdf",
        ],
        "Di Tian Sui - Dripping Heaven Marrow (BaZi Chinese Astrology)"
    ),
    (
        "Firmicus_Maternus_Ancient_Astrology.pdf",
        [
            "https://archive.org/download/firmicus-maternus-ancient-astrology/FirmicusAncientAstrology.pdf",
            "https://ia801404.us.archive.org/17/items/firmicus-maternus-ancient-astrology/FirmicusAncientAstrology.pdf",
        ],
        "Firmicus Maternus - Ancient Astrology (Jean Rhys Bram translation)"
    ),
]

def try_download(url, out_path, timeout=45):
    try:
        print(f"  Trying: {url[:90]}...")
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/pdf,*/*"
        })
        with urllib.request.urlopen(req, timeout=timeout) as r, open(out_path, "wb") as f:
            data = r.read()
            f.write(data)
            if len(data) < 10000:
                print(f"  WARNING: file too small ({len(data)} bytes), likely an error page.")
                os.remove(out_path)
                return False
            return True
    except urllib.error.HTTPError as e:
        print(f"  HTTP {e.code}: {e.reason}")
        return False
    except urllib.error.URLError as e:
        print(f"  URL Error: {e.reason}")
        return False
    except Exception as e:
        print(f"  Error: {e}")
        return False


def main():
    results = {}
    for filename, urls, desc in TARGETS:
        out_path = os.path.join(BOOKS_DIR, filename)
        if os.path.exists(out_path) and os.path.getsize(out_path) > 10000:
            size = os.path.getsize(out_path)
            print(f"[SKIP] Already downloaded: {filename} ({size:,} bytes)")
            results[filename] = f"already_exists ({size:,} bytes)"
            continue

        print(f"\n[DOWNLOADING] {desc}")
        success = False
        for url in urls:
            if try_download(url, out_path):
                size = os.path.getsize(out_path)
                print(f"  [OK] Saved {filename} ({size:,} bytes)")
                results[filename] = f"downloaded ({size:,} bytes)"
                success = True
                break
            time.sleep(1)

        if not success:
            print(f"  [FAILED] All URLs exhausted for {filename}.")
            results[filename] = "FAILED"

    print("\n\n======= DOWNLOAD SUMMARY =======")
    ok = sum(1 for s in results.values() if "FAILED" not in s)
    failed = [f for f, s in results.items() if "FAILED" in s]
    print(f"  SUCCESS: {ok}/{len(results)}")
    for fname, status in results.items():
        icon = "✓" if "FAILED" not in status else "✗"
        print(f"  {icon} {fname}: {status}")
    if failed:
        print(f"\nFailed books: {', '.join(failed)}")

if __name__ == "__main__":
    main()
