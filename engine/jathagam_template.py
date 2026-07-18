# -*- coding: utf-8 -*-

"""

Part 1 of every client report: full jathagam (Manoj booklet layout + chart tables).



Part 2 (elsewhere): predictions grounded in this chart - see build_prediction_section_header().



Booklet page order: 1, 2, 3 (graha), 4, 5, 6 (bhava), 7 (shadbala), 8 (SAV), 9-12 (dasha tables), 13 (vidhi),

then full chart details (houses, functional lords, synthesis, current dasha).

"""

from __future__ import annotations



import datetime as dt

from typing import Any



from engine.report_chart_details import normalize_chart, build_chart_details_markdown



JATHAGAM_PAGE_ORDER = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13)

JATHAGAM_FRONT_PAGE_ORDER = JATHAGAM_PAGE_ORDER  # alias



PAGE_TITLES = {

    "en": {

        1: "Page 1 - Cover and birth record",

        2: "Page 2 - Panchanga and chart identity",

        3: "Page 3 - Graha positions (Nirayana)",

        4: "Page 4 - Rasi and Navamsa charts",

        5: "Page 5 - Rasi chart (D1)",

        6: "Page 6 - Twelve bhavas",

        7: "Page 7 - Shadbala",

        8: "Page 8 - Sarvashtakavarga",

        9: "Page 9 - Vimshottari Mahadasha",

        10: "Page 10 - Vimshottari Antardasha (1)",

        11: "Page 11 - Vimshottari Antardasha (2)",

        12: "Page 12 - Vimshottari Antardasha (3)",

        13: "Page 13 - Vidhi number and lucky elements",

    },

    "ta": {

        1: "\u0baa\u0b95\u0bcd\u0b95\u0bae\u0bcd 1 - \u0b85\u0b9f\u0bcd\u0b9f\u0bc8 \u0bae\u0bb1\u0bcd\u0bb1\u0bc1\u0bae\u0bcd \u0baa\u0bbf\u0bb1\u0baa\u0bcd\u0baa\u0bc1 \u0bb5\u0bbf\u0bb5\u0bb0\u0bae\u0bcd",

        2: "\u0baa\u0b95\u0bcd\u0b95\u0bae\u0bcd 2 - \u0baa\u0b9e\u0bcd\u0b9a\u0bbe\u0b99\u0bcd\u0b95\u0bae\u0bcd \u0bae\u0bb1\u0bcd\u0bb1\u0bc1\u0bae\u0bcd \u0b9c\u0bbe\u0ba4\u0b95 \u0b85\u0b9f\u0bc8\u0baf\u0bbe\u0bb3\u0bae\u0bcd",

        3: "\u0baa\u0b95\u0bcd\u0b95\u0bae\u0bcd 3 - \u0b95\u0bbf\u0bb0\u0b95 \u0ba8\u0bbf\u0bb2\u0bc8\u0b95\u0bb3\u0bcd",

        4: "\u0baa\u0b95\u0bcd\u0b95\u0bae\u0bcd 4 - \u0bb0\u0bbe\u0b9a\u0bbf \u0bae\u0bb1\u0bcd\u0bb1\u0bc1\u0bae\u0bcd \u0ba8\u0bb5\u0bbe\u0bae\u0bcd\u0b9a\u0bae\u0bcd \u0b9a\u0b95\u0bcd\u0b95\u0bb0\u0bae\u0bcd",

        5: "\u0baa\u0b95\u0bcd\u0b95\u0bae\u0bcd 5 - \u0bb0\u0bbe\u0b9a\u0bbf \u0b9a\u0b95\u0bcd\u0b95\u0bb0\u0bae\u0bcd (D1)",

        6: "\u0baa\u0b95\u0bcd\u0b95\u0bae\u0bcd 6 - 12 \u0baa\u0bbe\u0bb5\u0b99\u0bcd\u0b95\u0bb3\u0bcd",

        7: "\u0baa\u0b95\u0bcd\u0b95\u0bae\u0bcd 7 - \u0bb7\u0b9f\u0bcd\u0baa\u0bb2",

        8: "\u0baa\u0b95\u0bcd\u0b95\u0bae\u0bcd 8 - \u0b85\u0bb7\u0bcd\u0b9f\u0b95\u0bb5\u0bb0\u0bcd\u0b95\u0bae\u0bcd",

        9: "\u0baa\u0b95\u0bcd\u0b95\u0bae\u0bcd 9 - \u0bb5\u0bbf\u0bae\u0bcd\u0b9a\u0bcb\u0ba4\u0bcd\u0ba4\u0bbe\u0bb0\u0bbf \u0bae\u0b95\u0bbe \u0ba4\u0bbf\u0b9a\u0bc8",

        10: "\u0baa\u0b95\u0bcd\u0b95\u0bae\u0bcd 10 - \u0b85\u0ba4\u0bbf\u0ba4\u0bbe\u0bb0 \u0ba4\u0bbf\u0b9a\u0bc8 (1)",

        11: "\u0baa\u0b95\u0bcd\u0b95\u0bae\u0bcd 11 - \u0b85\u0ba4\u0bbf\u0ba4\u0bbe\u0bb0 \u0ba4\u0bbf\u0b9a\u0bc8 (2)",

        12: "\u0baa\u0b95\u0bcd\u0b95\u0bae\u0bcd 12 - \u0b85\u0ba4\u0bbf\u0ba4\u0bbe\u0bb0 \u0ba4\u0bbf\u0b9a\u0bc8 (3)",

        13: "\u0baa\u0b95\u0bcd\u0b95\u0bae\u0bcd 13 - \u0bb5\u0bbf\u0ba4\u0bbf \u0b8e\u0ba3\u0bcd \u0bae\u0bb1\u0bcd\u0bb1\u0bc1\u0bae\u0bcd \u0b85\u0ba4\u0bbf\u0bb7\u0bcd\u0b9f \u0b85\u0bae\u0bcd\u0b9a\u0b99\u0bcd\u0b95\u0bb3\u0bcd",

    },

}





def _L(lang: str, page: int) -> str:

    return PAGE_TITLES.get(lang, PAGE_TITLES["en"]).get(page, f"Page {page}")





def build_page1_cover(chart: dict[str, Any], lang: str = "ta") -> str:

    from engine.jathagam_extras import page1_extras, format_table_rows



    c = normalize_chart(chart)

    b = c["birth"]

    place = b.get("place", "") if lang == "ta" else b.get("place_en", b.get("place", ""))

    lines = [f"## {_L(lang, 1)}", ""]

    if lang == "ta":

        b_dt_str = b.get("datetime", "")
        if b_dt_str:
            b_dt = dt.datetime.fromisoformat(b_dt_str)
            d, m, y, h, mn = b_dt.day, b_dt.month, b_dt.year, b_dt.hour, b_dt.minute
        else:
            d, m, y, h, mn = b.get('day', 1), b.get('month', 1), b.get('year', 2000), b.get('hour', 0), b.get('min', 0)
            
        rows = [

            ("??????", f"**{c.get('name', '')}**"),

            ("????????? ?????", str(c.get("father_name", c.get("father", "-")))),

            ("?????? ?????", str(c.get("mother_name", c.get("mother", "-")))),

            ("?????? ????", f"{d:02d}-{m:02d}-{y} ({b.get('weekday', '')})"),

            ("?????? ?????", f"{h:02d}:{mn:02d} IST"),

        ]

        rows.extend(page1_extras(c, lang))

        rows += [

            ("\u0baa\u0bbf\u0bb1\u0ba8\u0bcd\u0ba4 \u0b8a\u0bb0\u0bcd", place),

            ("??????????", f"{b.get('lat', '')} ??????"),

            ("?????????????", f"{b.get('lon', '')} ???????"),

        ]

        lines += ["| ?????? | ??????? |", "|---|---|", format_table_rows(rows), ""]

    else:

        b_dt_str = b.get("datetime", "")
        if b_dt_str:
            b_dt = dt.datetime.fromisoformat(b_dt_str)
            d, m, y, h, mn = b_dt.day, b_dt.month, b_dt.year, b_dt.hour, b_dt.minute
        else:
            d, m, y, h, mn = b.get('day', 1), b.get('month', 1), b.get('year', 2000), b.get('hour', 0), b.get('min', 0)
            
        rows = [

            ("Native", f"**{c.get('name', '')}**"),

            ("Father", str(c.get("father_name", c.get("father", "-")))),

            ("Mother", str(c.get("mother_name", c.get("mother", "-")))),

            ("Date of birth", f"{d:02d}-{m:02d}-{y} ({b.get('weekday', '')})"),

            ("Time of birth", f"{h:02d}:{mn:02d} IST"),

        ]

        rows.extend(page1_extras(c, lang))

        rows += [

            ("Place", place),

            ("Latitude", f"{b.get('lat', '')} N"),

            ("Longitude", f"{b.get('lon', '')} E"),

        ]

        lines += ["| Field | Value |", "|---|---|", format_table_rows(rows), ""]

    return "\n".join(lines)





def build_page2_panchanga(chart: dict[str, Any], lang: str = "ta") -> str:

    from engine.jathagam_extras import page2_panchanga_rows, format_table_rows



    c = normalize_chart(chart)

    rows = page2_panchanga_rows(c, lang)

    lines = [f"## {_L(lang, 2)}", "", "| \u0bb5\u0bbf\u0bb5\u0bb0\u0bae\u0bcd | \u0bae\u0ba4\u0bbf\u0baa\u0bcd\u0baa\u0bc1 |" if lang == "ta" else "| Field | Value |", "|---|---|"]

    lines.append(format_table_rows(rows))

    lines.append("")

    return "\n".join(lines)





def build_page4_rasi_navamsa(chart: dict[str, Any], lang: str = "ta") -> str:

    from engine.jathagam_extras import birth_disha_iruppu
    from engine.report_chart_details import _sign_name

    c = normalize_chart(chart)

    lagna = c.get("lagna", "")

    lines = [f"## {_L(lang, 4)}", ""]

    if lang == "ta":

        lines += [

            f"**\u0bb0\u0bbe\u0b9a\u0bbf (D1) \u0bb2\u0b95\u0bcd\u0ba9\u0bae\u0bcd:** {_sign_name(lagna, 'ta')}",

            "",

            "\u0ba4\u0bc6\u0ba9\u0bcd\u0ba9\u0bbf\u0ba8\u0bcd\u0ba4\u0bbf\u0baf \u0baa\u0bc6\u0b9f\u0bcd\u0b9f\u0bbf \u0b9a\u0b95\u0bcd\u0b95\u0bb0\u0bae\u0bcd \u2014 PDF \u0bb5\u0bb0\u0bc8\u0baa\u0b9f\u0bae\u0bbe\u0b95.",

            "",

            "| \u0bb5\u0bc0\u0b9f\u0bc1 | \u0bb0\u0bbe\u0b9a\u0bbf | \u0b95\u0bbf\u0bb0\u0b95\u0b99\u0bcd\u0b95\u0bb3\u0bcd |",

            "|---:|---|---|",

        ]

    else:

        lines += [

            f"**Rasi (D1) lagna:** {lagna}",

            "",

            "South-Indian box charts in PDF.",

            "",

            "| House | Sign | Planets |",

            "|---:|---|---|",

        ]

    lagna_idx = int(c.get("lagna_idx", 0))

    RASIS = [

        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",

        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",

    ]

    by_h: dict[int, list[str]] = {h: [] for h in range(1, 13)}

    for p, pd in (c.get("positions") or {}).items():

        if p == "Ketu":

            continue

        h = pd.get("house")

        if h:

            by_h[int(h)].append(p)

    for h in range(1, 13):

        sign = RASIS[(lagna_idx + h - 1) % 12]

        sign_label = _sign_name(sign, lang) if lang == "ta" else sign

        occ = ", ".join(by_h[h]) or "-"

        lines.append(f"| {h} | {sign_label} | {occ} |")

    disha = birth_disha_iruppu(c, lang)

    if disha:

        lines.extend(["", disha, ""])

    lines.append("")

    return "\n".join(lines)





def build_page5_rasi_d1(chart: dict[str, Any], lang: str = "ta") -> str:

    c = normalize_chart(chart)

    lines = [f"## {_L(lang, 5)}", ""]

    if lang == "ta":

        lines.append(f"**\u0bb0\u0bbe\u0b9a\u0bbf \u0b9a\u0b95\u0bcd\u0b95\u0bb0\u0bae\u0bcd (D1)** \u2014 \u0bb2\u0b95\u0bcd\u0ba9\u0bae\u0bcd {c.get('lagna', '')}")

    else:

        lines.append(f"**Rasi chart (D1)** - lagna {c.get('lagna', '')}")

    lines.append("")

    for p in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"):

        pd = (c.get("positions") or {}).get(p)

        if pd:

            lines.append(

                f"- {p}: house {pd.get('house')} {pd.get('rasi', '')} ({pd.get('deg', '')})"

            )

    lines.append("")

    return "\n".join(lines)





def build_page13_lucky(chart: dict[str, Any], lang: str = "ta") -> str:

    from engine.jathagam_extras import build_page13_tamil_numerology



    c = normalize_chart(chart)

    try:

        return build_page13_tamil_numerology(c, lang)

    except Exception as exc:

        return f"## {_L(lang, 13)}\n\n(Numerology unavailable: {exc})\n"





def build_page3_graha_table(chart: dict[str, Any], lang: str = "ta") -> str:

    from engine.report_chart_details import PLANET_ORDER, _nak_name, _planet_name, _sign_name



    c = normalize_chart(chart)

    lines = [f"## {_L(lang, 3)}", ""]

    from engine.jathagam_extras import navamsa_rasi_for_lon

    hdr = (

        "| Planet | Sign | House | Deg | Nakshatra | Pada | Navamsa |"

        if lang == "en"

        else "| \u0b95\u0bbf\u0bb0\u0b95\u0bae\u0bcd | \u0bb0\u0bbe\u0b9a\u0bbf | \u0bb5\u0bc0\u0b9f\u0bc1 | \u0baa\u0bbe\u0b95\u0bc8 | \u0ba8\u0b9f\u0bcd\u0b9a\u0ba4\u0bcd\u0ba4\u0bbf\u0bb0\u0bae\u0bcd | \u0baa\u0bbe\u0ba4\u0bae\u0bcd | \u0ba8\u0bb5\u0bbe\u0bae\u0bcd\u0b9a\u0bae\u0bcd |"

    )

    lines.append(hdr)

    lines.append("|---|---:|---:|---:|---|---:|---|" if lang == "en" else "|---|---:|---:|---:|---|---:|---|")

    for p in PLANET_ORDER:

        pd = (c.get("positions") or {}).get(p)

        if not pd:

            continue

        nav = pd.get("navamsa_rasi") or navamsa_rasi_for_lon(float(pd.get("lon_abs") or pd.get("lon") or 0))

        lines.append(

            f"| {_planet_name(p, lang)} | {_sign_name(pd.get('rasi', ''), lang)} | "

            f"{pd.get('house', '')} | {pd.get('deg', '')} | "

            f"{_nak_name(pd.get('nak', ''), lang)} | {pd.get('pada', '')} | "

            f"{_sign_name(nav, lang)} |"

        )

    lines.append("")

    return "\n".join(lines)





def build_page6_bhava(chart: dict[str, Any], lang: str = "ta") -> str:
    from engine.jathagam_pages_advanced import build_page6_bhava_cusps
    return build_page6_bhava_cusps(chart, lang, _L(lang, 6))


def build_page7_shadbala(chart: dict[str, Any], lang: str = "ta") -> str:
    from engine.jathagam_pages_advanced import build_page7_shadbala_table
    return build_page7_shadbala_table(chart, lang, _L(lang, 7))


def build_page8_ashtakavarga(chart: dict[str, Any], lang: str = "ta") -> str:
    from engine.jathagam_pages_advanced import build_page8_sav_table
    return build_page8_sav_table(chart, lang, _L(lang, 8))


def build_page9_dasha(chart: dict[str, Any], lang: str = "ta") -> str:
    from engine.jathagam_pages_advanced import build_page9_maha_dasha
    return build_page9_maha_dasha(chart, lang, _L(lang, 9))


def build_pages_10_12_dasha(chart: dict[str, Any], lang: str = "ta") -> str:
    from engine.jathagam_pages_advanced import build_pages_10_12_antardasha
    p10, p11, p12 = build_pages_10_12_antardasha(
        chart, lang, (_L(lang, 10), _L(lang, 11), _L(lang, 12))
    )
    return "\n\n".join([p10, p11, p12])





def build_jathagam_part1_header(lang: str) -> str:

    if lang == "ta":

        return (

            "# \u0baa\u0b95\u0bc1\u0ba4\u0bbf 1 \u2014 \u0b9c\u0bbe\u0ba4\u0b95\u0bae\u0bcd\n\n"

            "> \u0bae\u0bc1\u0bb4\u0bc1 \u0b9a\u0b95\u0bcd\u0b95\u0bb0 \u0bb5\u0bbf\u0bb5\u0bb0\u0b99\u0bcd\u0b95\u0bb3\u0bcd. "

            "\u0b95\u0ba3\u0bbf\u0baa\u0bcd\u0baa\u0bc1\u0b95\u0bb3\u0bcd \u0b87\u0ba8\u0bcd\u0ba4 \u0b9c\u0bbe\u0ba4\u0b95\u0ba4\u0bcd\u0ba4\u0bbf\u0bb2\u0bcd \u0ba4\u0bca\u0b9f\u0b99\u0bcd\u0b95\u0bbf\u0baf\u0bbe\u0b95 \u0b87\u0bb0\u0bc1\u0b95\u0bcd\u0b95\u0bbf\u0ba9\u0bcd\u0bb1\u0ba9.\n\n"

        )

    return "# Part 1 - Jathagam\n\n> Full birth chart. Part 2 predictions use this chart.\n\n"





def build_jathagam_full(

    chart: Any,

    lang: str = "ta",

    *,

    when: dt.datetime | None = None,

) -> str:

    """Part 1: full jathagam for every report."""

    parts = [

        build_jathagam_part1_header(lang),

        build_page1_cover(chart, lang),

        build_page2_panchanga(chart, lang),

        build_page3_graha_table(chart, lang),

        build_page4_rasi_navamsa(chart, lang),

        build_page5_rasi_d1(chart, lang),

        build_page6_bhava(chart, lang),

        build_page7_shadbala(chart, lang),

        build_page8_ashtakavarga(chart, lang),

        build_page9_dasha(chart, lang),

        build_pages_10_12_dasha(chart, lang),

        build_page13_lucky(chart, lang),

        build_chart_details_markdown(

            chart, lang, when=when, include_synthesis=True, include_current_dasha=True

        ),

        "---",

        "",

        "**End of jathagam**" if lang == "en" else "**\u0b9c\u0bbe\u0ba4\u0b95\u0bae\u0bcd \u0bae\u0bc1\u0b9f\u0bbf\u0bb5\u0bc1**",

        "",

    ]

    return "\n".join(parts)





def build_prediction_section_header(lang: str = "ta") -> str:

    if lang == "ta":

        return (

            "# \u0baa\u0b95\u0bc1\u0ba4\u0bbf 2 \u2014 \u0b95\u0ba3\u0bbf\u0baa\u0bcd\u0baa\u0bc1 \u0b85\u0bb1\u0bbf\u0b95\u0bcd\u0b95\u0bc8\n\n"

            "> \u0bae\u0bc7\u0bb2\u0bc8 \u0b9c\u0bbe\u0ba4\u0b95\u0ba4\u0bcd\u0ba4\u0bbf\u0bb2\u0bcd \u0b87\u0bb0\u0bc1\u0ba8\u0bcd\u0ba4 \u0b95\u0bbe\u0bb2 \u0b95\u0ba3\u0bbf\u0baa\u0bcd\u0baa\u0bc1\u0b95\u0bb3\u0bcd.\n\n---\n\n"

        )

    return "# Part 2 - Prediction report\n\n> Based on the jathagam above.\n\n---\n\n"





def build_jathagam_reference(chart: Any, lang: str = "ta", **kw: Any) -> str:

    return build_jathagam_full(chart, lang, **kw)





def build_jathagam_front_matter(

    chart: Any,

    lang: str = "ta",

    *,

    when: dt.datetime | None = None,

) -> str:

    return build_jathagam_full(chart, lang, when=when)

