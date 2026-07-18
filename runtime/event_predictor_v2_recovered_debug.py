# Source Generated with Decompyle++
# File: event_predictor_v2.cpython-312.pyc (Python 3.12)

"""Event Predictor v2 — refined accuracy.

Improvements over v1:
  - 13 event patterns (was 5)
  - Tightened thresholds — fewer false positives
  - Age-aware filters
  - Pattern-specific cooldown (don't re-fire same event in consecutive months)
  - Explicit 'why this NOT that' reasoning
"""
import datetime as dt
import sys
sys.path.insert(0, '.')
from granular_dasha import build_full_timeline, lookup
from transit_engine import detect_triggers, transit_positions
from comprehensive_yogas import detect_all_classical_yogas as detect_all_yogas
from vedic_core import RASIS, RASI_LORDS, DIGNITIES

def _h(pos, p):
    if p in pos:
        return pos[p]['house']


def _dig(pos, p):
    if p in pos:
        return DIGNITIES.get((p, pos[p]['rasi']), 'neutral')


def _occ(pos, h):
    pass
# WARNING: Decompyle incomplete


def _lord(lagna_idx, h):
    return RASI_LORDS[RASIS[(lagna_idx + h - 1) % 12]]


def _pv(auspicious, inauspicious = (False, False)):
    if inauspicious:
        return 'inauspicious'
    if auspicious:
        return 'auspicious'
    return 'neutral'


def event_father(chart, ds, tr, yogas, age):
    '''Father health/career event. Pitra Dosha boosts but is not required.
    Catches childhood losses (Rahman age 9 1976) via Sun + 9H affliction alone.
    '''
    pyoga = (lambda .0: pass# WARNING: Decompyle incomplete
)(yogas(), None)
    pos = chart['positions']
    lagna_idx = chart.get('lagna_idx', 0)
    h9_lord = _lord(lagna_idx, 9)
    score = 0
    why = []
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    pd = ds.get(3, { }).get('pd')
    if pyoga:
        score += 2
        why.append('Pitra Dosha base')
    sun_periods = [
        md == 'Sun',
        ad == 'Sun',
        pd == 'Sun']
    if any(sun_periods):
        score += 3
        if sun_periods[0]:
            pass
        elif sun_periods[1]:
            pass
        
        'MD'(f'''AD{'PD'}''')
    if md == h9_lord:
        score += 4
        why.append(f'''9L ({h9_lord}) MD — father-house fully activated (entire MD period)''')
    elif ad == h9_lord:
        score += 2
        why.append(f'''9L ({h9_lord}) AD''')
    elif pd == h9_lord:
        score += 1
        why.append(f'''9L ({h9_lord}) PD''')
    if ad == 'Jupiter' and md == h9_lord:
        score += 2
        why.append('9L MD + Jupiter AD — father-karaka double activation')
    elif md == 'Jupiter' and age > 40:
        score += 1
        why.append('Jupiter MD — father-life-cycle (mature)')
    if md == 'Ketu':
        score += 2
        why.append('Ketu MD — activates H4 karma')
    if md == 'Saturn' and age < 15:
        score += 2
        why.append('Saturn MD in childhood — paternal stress')
    sun_dig = _dig(pos, 'Sun') if pos.get('Sun') else None
    if sun_dig == 'Debil':
        score += 2
        why.append('Sun debilitated natally — fragile father karma')
    sret = (lambda .0: pass# WARNING: Decompyle incomplete
)(tr(), None)
    if sret:
        score += 4
        why.append(f'''Saturn Return (orb {sret['orb']}°)''')
    sat_sun = (lambda .0: pass# WARNING: Decompyle incomplete
)(tr(), None)
    if sat_sun:
        score += 3
        why.append(f'''Saturn over Sun (orb {sat_sun['orb']}°)''')
    mars_sun = (lambda .0: pass# WARNING: Decompyle incomplete
)(tr(), None)
    if mars_sun:
        score += 2
        why.append(f'''Mars on Sun (orb {mars_sun['orb']}°)''')
    rahu_on_sun = (lambda .0: pass# WARNING: Decompyle incomplete
)(tr(), None)
    if rahu_on_sun:
        score += 2
        why.append('Rahu on natal Sun')
    h8_lord = _lord(lagna_idx, 8)
    if md == h9_lord and ad in (h8_lord, 'Saturn', 'Ketu', 'Mars'):
        score += 3
        why.append(f'''9L MD + {ad} AD — father-life / loss of father window''')
    if ad == h8_lord and md in ('Sun', h9_lord, 'Saturn'):
        score += 2
        why.append(f'''8L ({h8_lord}) AD — father transition''')
    if score < 4:
        return None
    if md == h9_lord:
        md == h9_lord
    father_loss = ad in (h8_lord, 'Saturn', 'Ketu', 'Mars')
    return {
        'event': 'Father — health / career / life event',
        'category': 'father',
        'severity': min(5, score // 2),
        'predicted_valence': _pv(inauspicious = father_loss),
        'yoga': pyoga['name'] if pyoga else None,
        'why': why,
        'source': 'Sun + 9L + Saturn transits (BPHS Shapit Yogas + Phaladeepika Ch.13)' }


def event_self_accident(chart, ds, tr, yogas, age):
    '''Self-accident / hospitalization / surgery / serious illness — expanded.
    Catches: Saturn-Mercury (Amitabh Coolie 1982), Ketu-Mercury (Amitabh COVID 2020).
    '''
    pass
# WARNING: Decompyle incomplete


def event_marriage(chart, ds, tr, yogas, age):
    '''Marriage — 7L + Venus + Jupiter timing (BPHS Ch. 80).
    Age 18-75 (product gate). Chart-strong early windows 16-17 surface via
    event_age_policy as early_exception; ages <16 are not scored here.
    Threshold 3. Requires >=1 primary indicator (score >= 2).
    PRIMARY (+2): 7L in MD/AD/PD, Venus MD, 7L transit Jupiter(MED+), Rahu/Ketu 5H/7H as AD+Venus active.
    SECONDARY (+1): Venus AD/PD, Jupiter MD/AD karaka, Venus dispositor MD, Venus transit, Jupiter transit.
    '''
    pass
# WARNING: Decompyle incomplete


def event_career_breakthrough(chart, ds, tr, yogas, age):
    '''Career breakthrough — modern + classical rules.
    Catches: traditional 10L activations + Rahu/Saturn rules for modern careers
    (tech/foreign/govt/sports/film) when those planets are in career-significant houses.
    '''
    pass
# WARNING: Decompyle incomplete


def event_education_milestone(chart, ds, tr, yogas, age):
    if age < 5 or age > 25:
        return None
    pos = chart['positions']
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Mercury':
        score += 2
        why.append('Mercury MD')
    elif ad == 'Mercury':
        score += 2
        why.append('Mercury AD')
    if md == 'Jupiter':
        score += 2
        why.append('Jupiter MD — higher education')
    elif ad == 'Jupiter':
        score += 1
        why.append('Jupiter AD')
    chart.get('lagna_idx', 0) = None if md == 'Venus' else score += 1
    h5_lord = _lord(lagna_idx, 5)
    h9_lord = _lord(lagna_idx, 9)
    if md == h5_lord:
        score += 2
        why.append(f'''5L ({h5_lord}) MD — education lord active''')
    elif ad == h5_lord:
        score += 1
        why.append(f'''5L ({h5_lord}) AD''')
    if md == h9_lord:
        score += 2
        why.append(f'''9L ({h9_lord}) MD — higher education lord active''')
    elif ad == h9_lord:
        score += 1
        why.append(f'''9L ({h9_lord}) AD''')
    if age < 12 and score < 2:
        return None
    if age >= 12 and score < 3:
        return None
    return {
        'event': 'Education milestone / exam result / new course / qualification',
        'category': 'education',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': 'Mercury-Jupiter dasha rules (BPHS Ch. 47)' }


def event_foreign_travel(chart, ds, tr, yogas, age):
    '''Foreign travel / overseas opportunity / relocation / sea-voyage.
    Catches Gandhi London 1888 (age 18, Mercury MD), South Africa 1893 (age 23), return 1915 (age 45).
    '''
    if age < 12:
        return None
    pos = chart['positions']
    rahu_h = _h(pos, 'Rahu')
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    pd = ds.get(3, { }).get('pd')
    score = 0
    why = []
    if md == 'Rahu':
        score += 3
        why.append('Rahu MD — foreign activation')
    elif ad == 'Rahu':
        score += 2
        why.append('Rahu AD')
    elif pd == 'Rahu':
        score += 1
        why.append('Rahu PD')
    if rahu_h in (9, 12):
        score += 1
        why.append(f'''natal Rahu in foreign-house ({rahu_h})''')
    lagna_idx = chart['lagna_idx']
    h9_lord = _lord(lagna_idx, 9)
    h12_lord = _lord(lagna_idx, 12)
    h3_lord = _lord(lagna_idx, 3)
    pd = ds.get(3, { }).get('pd')
    if md in (h9_lord, h12_lord):
        score += 3
        why.append('9L/12L MD — foreign-house activated (full activation)')
    elif ad in (h9_lord, h12_lord):
        score += 2
        why.append('9L/12L AD')
    elif pd in (h9_lord, h12_lord):
        score += 1
        why.append('9L/12L PD')
    if md == 'Mercury' and ad == 'Mercury' or pd == 'Mercury':
        score += 1
        why.append('Mercury (travel karaka) active')
    if (md == h3_lord or ad in (h9_lord, h12_lord, 'Rahu') or md in (h9_lord, h12_lord, 'Rahu')) and ad == h3_lord:
        score += 2
        why.append('3L journey-house + foreign-house combo')
    if md == 'Mercury' and ad in ('Rahu', h9_lord, h12_lord, h3_lord):
        score += 2
        why.append(f'''Mercury MD + foreign-AD ({ad})''')
    if md == 'Moon' and ad == 'Rahu':
        score += 2
        why.append('Moon MD + Rahu AD — unconventional travel')
    if md == 'Saturn' and ad in ('Rahu', h12_lord, h9_lord):
        score += 1
        why.append(f'''Saturn MD + {ad} AD — long migration''')
    if md == 'Venus' and ad in (h9_lord, h12_lord, 'Moon', 'Mercury'):
        score += 1
        why.append(f'''Venus MD + {ad} AD — prestige/festival travel''')
    if md == h3_lord or ad == h3_lord:
        score += 2
        why.append(f'''3L ({h3_lord}) — journey / relocation active''')
    if md == 'Mercury' and age <= 30:
        score += 2
        why.append('Mercury MD in youth — study / voyage abroad')
    if score < 3:
        return None
    return {
        'event': 'Foreign travel / overseas opportunity / relocation',
        'category': 'travel',
        'severity': min(5, score // 2 + 1),
        'predicted_valence': _pv(auspicious = True),
        'yoga': None,
        'why': why,
        'source': 'Rahu + 9L/12L/3L + Mercury timing (Hora Sara + BPHS travel rules)' }


def event_wealth_peak(chart, ds, tr, yogas, age):
    if age < 22 or age > 75:
        return None
    dyoga = (lambda .0: pass# WARNING: Decompyle incomplete
)(yogas(), None)
    pos = chart['positions']
    lagna_idx = chart['lagna_idx']
    h2_lord = _lord(lagna_idx, 2)
    h11_lord = _lord(lagna_idx, 11)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md in (h2_lord, h11_lord):
        score += 3
        why.append('wealth-house lord MD')
    elif ad in (h2_lord, h11_lord):
        score += 2
        why.append('wealth-house lord AD')
    if md == 'Jupiter' or ad == 'Jupiter':
        score += 1
        why.append('Jupiter active')
    if md == 'Venus' or ad == 'Venus':
        score += 1
        why.append('Venus active')
    if md == h11_lord or ad == h11_lord:
        score += 2
        why.append(f'''11L ({h11_lord}) — gains / corporate inflow''')
    if md == 'Jupiter' and ad in (h11_lord, 'Rahu', h2_lord):
        score += 2
        why.append(f'''Jupiter MD + {ad} AD — major wealth expansion''')
    if dyoga:
        score += 1
        why.append('Dhana Yoga base')
    if score < 3:
        return None
    return {
        'event': 'Wealth peak / income increase / investment gain / property',
        'category': 'wealth',
        'severity': min(5, score // 2 + 1),
        'yoga': dyoga['name'] if dyoga else None,
        'why': why,
        'source': 'Dhana Yoga + 2L/11L periods (Phaladeepika Ch. 14)' }


def event_wealth_loss(chart, ds, tr, yogas, age):
    '''Wealth setback / bankruptcy / loss / financial scandal.
    Catches: Amitabh ABCL bankruptcy 1997 (age 55, Rahu MD), gambling losses, market crash hits.
    '''
    pass
# WARNING: Decompyle incomplete


def event_property(chart, ds, tr, yogas, age):
    '''Property / vehicle / asset purchase. Catches Vijay bungalow 2010 (Ketu/Rahu/Venus age 35).'''
    if age < 22 or age > 78:
        return None
    pos = chart['positions']
    lagna_idx = chart['lagna_idx']
    h4_lord = _lord(lagna_idx, 4)
    h2_lord = _lord(lagna_idx, 2)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    pd = ds.get(3, { }).get('pd')
    score = 0
    why = []
    if md == h4_lord:
        score += 3
        why.append(f'''4L ({h4_lord}) MD''')
    elif ad == h4_lord:
        score += 2
        why.append(f'''4L ({h4_lord}) AD''')
    elif pd == h4_lord:
        score += 1
        why.append(f'''4L ({h4_lord}) PD''')
    if md == h2_lord or ad == h2_lord:
        score += 1
        why.append(f'''2L ({h2_lord}) active — funds for asset''')
    if (md == 'Mars' or ad == 'Mars') and _h(pos, 'Mars') in (1, 4, 10):
        score += 1
        why.append('Mars in property house active')
    if md == 'Saturn' and _h(pos, 'Saturn') in (4, 10):
        score += 1
        why.append('Saturn supports asset-building')
    if md == 'Venus' and ad == 'Venus' or pd == 'Venus':
        score += 1
        why.append('Venus (comfort karaka) active')
    if md in ('Rahu', 'Ketu'):
        if ad == 'Venus' or pd == 'Venus':
            score += 2
            why.append(f'''{md} MD + Venus active — luxury/large-scale acquisition''')
    if (md == 'Jupiter' or ad == 'Jupiter') and _h(pos, 'Jupiter') in (4, 2, 11):
        score += 1
        why.append('Jupiter in benefic-wealth house active')
    h11_lord = _lord(lagna_idx, 11)
    if md in (h4_lord, h11_lord):
        if ad == 'Venus' or pd == 'Venus':
            score += 2
            why.append('4L/11L + Venus — luxury home / landmark asset')
    if score < 3:
        return None
    return {
        'event': 'Property / vehicle / major asset acquisition',
        'category': 'property',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '4L + 2L + Venus comfort + Rahu-Venus luxury (BPHS Ch.23 + Phaladeepika Ch.10)' }


def event_child_birth(chart, ds, tr, yogas, age):
    """Child birth — 5L + Jupiter + 5H occupants + dispositor.
    Catches Vijay's son 2000 (Mercury/Rahu) + daughter 2005 (Mercury/Saturn).
    """
    if age < 18 or age > 60:
        return None
    pos = chart['positions']
    lagna_idx = chart['lagna_idx']
    h5_lord = _lord(lagna_idx, 5)
    h9_lord = _lord(lagna_idx, 9)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    pd = ds.get(3, { }).get('pd')
    score = 0
    why = []
    if md == h5_lord:
        score += 2
        why.append(f'''5L ({h5_lord}) MD''')
    elif ad == h5_lord:
        score += 2
        why.append(f'''5L ({h5_lord}) AD''')
    elif pd == h5_lord:
        score += 1
        why.append(f'''5L ({h5_lord}) PD''')
    if md == 'Jupiter' or ad == 'Jupiter':
        score += 2
        why.append('Jupiter (Putrakaraka) active in MD/AD')
    elif pd == 'Jupiter':
        score += 1
        why.append('Jupiter PD')
    if (md == 'Moon' or ad == 'Moon') and _h(pos, 'Moon') in (5, 9, 11):
        score += 1
        why.append('Moon active in benefic house')
    if _h(pos, 'Rahu') == 5:
        if md == 'Rahu' or ad == 'Rahu':
            score += 2
            why.append('Rahu in 5H + active in dasha — unconventional child')
    if h5_lord in pos:
        h5l_sign = pos[h5_lord]['rasi_idx']
        disp = [
            'Mars',
            'Venus',
            'Mercury',
            'Moon',
            'Sun',
            'Mercury',
            'Venus',
            'Mars',
            'Jupiter',
            'Saturn',
            'Saturn',
            'Jupiter'][h5l_sign]
        if md == disp:
            score += 1
            why.append(f'''5L dispositor ({disp}) MD''')
    if md == 'Mercury' and ad in (h5_lord, 'Jupiter', 'Venus'):
        score += 1
        why.append(f'''Mercury MD + benefic AD ({ad})''')
    if md == h9_lord and ad in ('Jupiter', 'Moon', h5_lord):
        score += 3
        why.append(f'''9L MD + {ad} AD — progeny / lineage expansion''')
    if md == 'Moon' and ad == h5_lord:
        score += 2
        why.append(f'''Moon MD + 5L ({h5_lord}) AD — childbirth window''')
    if score < 3:
        return None
    return {
        'event': 'Child birth / pregnancy / family expansion',
        'category': 'children',
        'severity': min(5, score // 2 + 1),
        'predicted_valence': _pv(auspicious = True),
        'yoga': None,
        'why': why,
        'source': '5L + Jupiter + dispositor + Rahu-5H rules (BPHS Ch.80 Putra Bhava)' }


def event_spiritual(chart, ds, tr, yogas, age):
    '''Spiritual shift / religious conversion / pilgrimage / guru bond.
    Catches Rahman 1989 conversion to Islam (age 22, Rahu MD).
    '''
    if age < 12:
        return None
    pos = chart['positions']
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    pd = ds.get(3, { }).get('pd')
    score = 0
    why = []
    if md == 'Ketu':
        score += 3
        why.append('Ketu MD — natural spiritual deepening')
    elif ad == 'Ketu':
        score += 2
        why.append('Ketu AD — spiritual influence')
    elif pd == 'Ketu':
        score += 1
        why.append('Ketu PD')
    ketu_rasi = pos.get('Ketu', { }).get('rasi') if 'Ketu' in pos else None
    if ketu_rasi:
        sign_lords = {
            'Aries': 'Mars',
            'Taurus': 'Venus',
            'Gemini': 'Mercury',
            'Cancer': 'Moon',
            'Leo': 'Sun',
            'Virgo': 'Mercury',
            'Libra': 'Venus',
            'Scorpio': 'Mars',
            'Sagittarius': 'Jupiter',
            'Capricorn': 'Saturn',
            'Aquarius': 'Saturn',
            'Pisces': 'Jupiter' }
        ketu_disp = sign_lords.get(ketu_rasi)
        if ketu_disp:
            if md == ketu_disp or ad == ketu_disp:
                score += 2
                why.append(f'''MD/AD lord is dispositor of Ketu ({ketu_disp}) — activates spiritual house''')
                if md == 'Saturn' and ad == ketu_disp:
                    score += 2
                    why.append('Saturn MD + Ketu dispositor AD — disciplined spiritual conversion')
    if md == 'Jupiter':
        score += 2
        why.append('Jupiter MD — wisdom + religious expansion')
    elif ad == 'Jupiter' and md in ('Rahu', 'Ketu', 'Saturn'):
        score += 2
        why.append(f'''{md} MD + Jupiter AD — guru-led spiritual turn''')
    if md == 'Rahu' and ad in ('Jupiter', 'Ketu', 'Mercury'):
        score += 3
        why.append(f'''Rahu MD + {ad} AD — radical religious shift / conversion''')
    if md == 'Saturn' and ad in ('Ketu', 'Jupiter'):
        score += 2
        why.append(f'''Saturn MD + {ad} AD — disciplined sadhana''')
    lagna_idx = chart.get('lagna_idx', 0)
    h9_lord = _lord(lagna_idx, 9)
    if ad == 'Jupiter':
        if md == h9_lord or md == 'Venus':
            score += 2
            why.append('Jupiter AD with dharma-lord MD — ideological / political launch')
    if md == h9_lord:
        if ad == 'Jupiter' or pd == 'Jupiter':
            score += 2
            why.append(f'''9L ({h9_lord}) MD + Jupiter active — dharma mission''')
    if _h(pos, 'Ketu') in (1, 4, 5, 8, 9, 12):
        score += 1
        why.append('natal Ketu in spiritual house')
    if _h(pos, 'Jupiter') in (9, 12):
        score += 1
        why.append('Jupiter in dharma/moksha house')
    if score < 4:
        return None
    return {
        'event': 'Spiritual deepening / religious shift / conversion / pilgrimage',
        'category': 'spirituality',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': 'Ketu/Jupiter/Rahu dasha pairs (Hora Sara Ch.25 + BPHS dharma yogas)' }


def event_health_self(chart, ds, tr, yogas, age):
    if age < 12:
        return None
    rogayoga = (lambda .0: pass# WARNING: Decompyle incomplete
)(yogas(), None)
    pos = chart['positions']
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    asc_lord = chart.get('lagna_lord')
    score = 0
    why = []
    if asc_lord and md == asc_lord and _dig(pos, asc_lord) == 'Debil':
        score += 3
        why.append(f'''weak lagna lord ({asc_lord}) MD''')
    if md in ('Saturn', 'Rahu', 'Ketu') and ad in ('Saturn', 'Rahu', 'Ketu'):
        score += 2
        why.append('malefic-malefic dasha stack')
    sade = (lambda .0: pass# WARNING: Decompyle incomplete
)(tr(), None)
    if sade and 'On Moon' in sade['label']:
        score += 2
        why.append('Sade Sati peak phase')
    if rogayoga:
        score += 1
        why.append('Roga Yoga base')
    if score < 5:
        return None
    return {
        'event': 'Personal health crisis — chronic flare / hospitalization / surgery',
        'category': 'health_self',
        'severity': min(5, score // 2 + 1),
        'yoga': rogayoga['name'] if rogayoga else None,
        'why': why,
        'source': 'Roga Yoga + Sade Sati rules' }


def event_relationship_break(chart, ds, tr, yogas, age):
    if age < 18 or age > 75:
        return None
    pos = chart['positions']
    lagna_idx = chart['lagna_idx']
    h7_lord = _lord(lagna_idx, 7)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md in ('Saturn', 'Rahu', 'Ketu') and ad == h7_lord:
        score += 3
        why.append('malefic MD + 7L AD')
    sat_venus = (lambda .0: pass# WARNING: Decompyle incomplete
)(tr(), None)
    if sat_venus:
        score += 2
        why.append('Saturn over Venus')
    if md == 'Ketu':
        if ad == 'Venus' or ad == h7_lord:
            score += 2
            why.append('Ketu MD + Venus/7L AD = separation tone')
    if score < 5:
        return None
    return {
        'event': 'Relationship break / emotional rupture / partner-related stress',
        'category': 'relationship_break',
        'severity': min(5, score // 2),
        'yoga': None,
        'why': why,
        'source': '7L + Ketu/Saturn afflicting Venus' }


def event_mother(chart, ds, tr, yogas, age):
    matr = (lambda .0: pass# WARNING: Decompyle incomplete
)(yogas(), None)
    if not matr:
        return None
    pos = chart['positions']
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Moon' or ad == 'Moon':
        score += 2
        why.append('Moon period')
    if md and md in pos and pos[md]['house'] == 4:
        score += 2
        why.append(f'''MD ({md}) in 4H''')
    elif ad and ad in pos and pos[ad]['house'] == 4:
        score += 2
        why.append(f'''AD ({ad}) in 4H''')
    moon_house = pos.get('Moon', { }).get('house') if 'Moon' in pos else None
    if moon_house:
        if md and md in pos and pos[md]['house'] == moon_house and md != 'Moon':
            score += 2
            why.append(f'''MD ({md}) conjoined with Moon''')
        elif ad and ad in pos and pos[ad]['house'] == moon_house and ad != 'Moon':
            score += 2
            why.append(f'''AD ({ad}) conjoined with Moon''')
    sat_moon = (lambda .0: pass# WARNING: Decompyle incomplete
)(tr(), None)
    if sat_moon:
        score += 3
        why.append('Saturn on Moon')
    sade = (lambda .0: pass# WARNING: Decompyle incomplete
)(tr(), None)
    if sade:
        score += 1
        why.append(sade['label'])
    if score < 4:
        return None
    return {
        'event': 'Mother health / wellbeing event',
        'category': 'mother',
        'severity': min(5, score // 2),
        'yoga': matr['name'],
        'why': why,
        'source': 'Matra Dosha (BPHS Shapit Yogas) + Sade Sati activation' }


def event_honor_recognition(chart, ds, tr, yogas, age):
    '''Award/honor/title window — Sun karaka + Jupiter MD/AD + late-life award boost.'''
    if age < 16 or age > 85:
        return None
    pos = chart['positions']
    lagna_idx = chart['lagna_idx']
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    pd = ds.get(3, { }).get('pd')
    score = 0
    why = []
    sun_h = pos.get('Sun', { }).get('house', 0)
    if md == 'Sun':
        score += 3
        why.append('Sun MD (honor-karaka)')
    elif ad == 'Sun':
        score += 2
        why.append('Sun AD')
    elif pd == 'Sun':
        score += 1
        why.append('Sun PD')
    if md == 'Jupiter':
        score += 3
        why.append('Jupiter MD — wisdom-recognition')
    elif ad == 'Jupiter':
        score += 2
        why.append('Jupiter AD — late-career award trigger')
    elif pd == 'Jupiter':
        score += 1
        why.append('Jupiter PD')
    if md in ('Ketu', 'Saturn') and ad == 'Jupiter' and age >= 60:
        score += 2
        why.append(f'''{md} MD + Jupiter AD at age {int(age)} — life-achievement award''')
    sun_rasi = pos.get('Sun', { }).get('rasi', '')
    if not sun_rasi in ('Leo', 'Aries'):
        sun_rasi in ('Leo', 'Aries')
    sun_strong = sun_h in (1, 4, 7, 9, 10)
    if sun_strong:
        score += 1
        why.append('Sun strong in chart')
    raja = (lambda .0: pass# WARNING: Decompyle incomplete
)(yogas(), None)
    if raja:
        h10_lord = _lord(lagna_idx, 10)
        h9_lord = _lord(lagna_idx, 9)
        if md in (h10_lord, h9_lord) or ad in (h10_lord, h9_lord):
            score += 2
            why.append('Raja Yoga lord activates')
    jup_to_sun = (lambda .0: pass# WARNING: Decompyle incomplete
)(tr(), None)
    if jup_to_sun:
        score += 2
        why.append('Jupiter transits Sun (award trigger)')
    hamsa = (lambda .0: pass# WARNING: Decompyle incomplete
)(yogas(), None)
    if hamsa and md in ('Jupiter', 'Mercury', 'Mars', 'Venus', 'Saturn'):
        score += 1
        why.append(f'''{hamsa['name']} matures via {md} MD''')
    if score < 3:
        return None
    return {
        'event': 'Award / honor / public recognition (Padma, Filmfare, Doctorate, Bharat Ratna)',
        'category': 'honor',
        'severity': min(5, score // 2 + 1),
        'yoga': { }.get('name') if raja or hamsa else None,
        'why': why,
        'source': 'Sun karaka + Jupiter transit + Mahapurusha/Raja Yoga maturation' }


def event_widowhood(chart, ds, tr, yogas, age):
    """Spouse death / separation / divorce — 7L afflicted in dasha + Mars/Saturn/Ketu transits.
    Catches: Rekha's husband Mukesh Agarwal suicide (1990-10), Rahman separation 2024 age 57.
    """
    pass
# WARNING: Decompyle incomplete


def event_self_death(chart, ds, tr, yogas, age):
    '''Death of native — Maraka period (2L/7L), severe 8H activation,
    chronic-illness terminal phase, or assassination via Mars-Saturn-Ketu malefic transit.
    Catches: Indira assassination 1984 (age 66, Rahu MD), Jobs cancer 2011 (age 56, Rahu MD),
    Lata COVID 2022 (age 92, Mercury MD), Hawking 2018 (age 76, Sun MD), Gandhi assassination 1948 (age 78).
    '''
    if age < 30:
        return None
    pos = chart['positions']
    lagna_idx = chart['lagna_idx']
    h2_lord = _lord(lagna_idx, 2)
    h7_lord = _lord(lagna_idx, 7)
    h8_lord = _lord(lagna_idx, 8)
    h12_lord = _lord(lagna_idx, 12)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    pd = ds.get(3, { }).get('pd')
    score = 0
    why = []
    if md in (h2_lord, h7_lord):
        score += 3
        why.append(f'''Maraka {md} ({'2L' if md == h2_lord else '7L'}) MD''')
    elif ad in (h2_lord, h7_lord):
        score += 2
        why.append('Maraka AD')
    if md == h8_lord and ad in ('Saturn', 'Rahu', 'Ketu', 'Mars'):
        score += 3
        why.append(f'''8L ({h8_lord}) MD + malefic AD — Ayur exhaustion''')
    elif ad == h8_lord and md in ('Saturn', 'Rahu', 'Ketu'):
        score += 2
        why.append('8L AD + malefic MD')
    if md == h12_lord:
        score += 1
        why.append(f'''12L ({h12_lord}) MD — body-exit hint''')
    if md in ('Rahu', 'Ketu') and age >= 50:
        score += 2
        why.append(f'''{md} MD at age {age}+ — node-induced exit-window''')
    if md == 'Mars' and ad == 'Saturn' and age >= 45:
        score += 3
        why.append('Mars MD + Saturn AD — violent / terminal culmination')
    if md == 'Saturn' and ad == 'Mars' and age >= 45:
        score += 2
        why.append('Saturn MD + Mars AD — fatal stress culmination')
    if age >= 70 and md in (h2_lord, h7_lord, h8_lord):
        score += 2
        why.append(f'''Maraka/Ayur lord {md} MD in advanced age''')
    if md == 'Saturn' and age >= 70:
        score += 2
        why.append('Saturn MD in advanced age — natural end')
    if md == 'Sun' and age >= 70:
        score += 1
        why.append('Sun MD in advanced age')
    sade = (lambda .0: pass# WARNING: Decompyle incomplete
)(tr(), None)
    if sade and age >= 60:
        score += 1
        why.append('Sade Sati in old age')
    mars_moon = (lambda .0: pass# WARNING: Decompyle incomplete
)(tr(), None)
    if mars_moon:
        score += 1
        why.append('Mars over Moon — vitality crisis')
    sat_moon = (lambda .0: pass# WARNING: Decompyle incomplete
)(tr(), None)
    if sat_moon:
        score += 1
        why.append('Saturn over Moon — chronic exhaustion')
    if score < 4:
        return None
    return {
        'event': 'Critical health crisis / terminal-phase indicator / Maraka period',
        'category': 'death_self',
        'severity': min(5, score // 2 + 1),
        'predicted_valence': _pv(inauspicious = True),
        'yoga': None,
        'why': why,
        'source': 'Maraka 2L/7L + 8L Ayur + node-induced exit (BPHS Ch.45-46 Ayurdaya)' }


def event_siblings(chart, ds, tr, yogas, age):
    '''3H sibling events — birth, marriage, illness, death. Mars + 3L activation.'''
    if age < 5 or age > 75:
        return None
    pos = chart['positions']
    lagna_idx = chart['lagna_idx']
    h3_lord = _lord(lagna_idx, 3)
    h11_lord = _lord(lagna_idx, 11)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    pd = ds.get(3, { }).get('pd')
    score = 0
    why = []
    if md == h3_lord:
        score += 3
        why.append(f'''3L ({h3_lord}) MD — sibling karma active''')
    elif ad == h3_lord:
        score += 2
        why.append(f'''3L ({h3_lord}) AD''')
    if md == h11_lord or ad == h11_lord:
        score += 1
        why.append(f'''11L ({h11_lord}) (elder sibling) active''')
    if md == 'Mars' or ad == 'Mars':
        score += 2
        why.append('Mars (sibling karaka) active')
    if _h(pos, 'Mars') == 3:
        score += 1
        why.append('Mars in 3H natally')
    if score < 4:
        return None
    return {
        'event': 'Sibling event — birth / marriage / health / death',
        'category': 'siblings',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '3L + Mars karaka (BPHS Ch.13, Phaladeepika)' }


def event_vehicle_purchase(chart, ds, tr, yogas, age):
    '''4H vehicle / luxury — Venus + 4L + Mars.'''
    if age < 18 or age > 70:
        return None
    pos = chart['positions']
    lagna_idx = chart['lagna_idx']
    h4_lord = _lord(lagna_idx, 4)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    pd = ds.get(3, { }).get('pd')
    score = 0
    why = []
    if md == h4_lord:
        score += 3
        why.append(f'''4L ({h4_lord}) MD — vehicle-house active''')
    elif ad == h4_lord:
        score += 2
        why.append(f'''4L ({h4_lord}) AD''')
    if md == 'Venus' or ad == 'Venus':
        score += 2
        why.append('Venus (vehicle karaka) active')
    if pd == 'Venus':
        score += 1
        why.append('Venus PD')
    if md == 'Mars' and _h(pos, 'Mars') in (4, 11):
        score += 1
        why.append('Mars-4H/11H')
    if score < 4:
        return None
    return {
        'event': 'Vehicle / luxury asset purchase',
        'category': 'vehicle',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '4L + Venus karaka (BPHS Ch.23 + Phaladeepika)' }


def event_business_start(chart, ds, tr, yogas, age):
    '''10H business launch — Mercury + 10L + 11L.'''
    if age < 18 or age > 65:
        return None
    pos = chart['positions']
    lagna_idx = chart['lagna_idx']
    h10_lord = _lord(lagna_idx, 10)
    h11_lord = _lord(lagna_idx, 11)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    pd = ds.get(3, { }).get('pd')
    score = 0
    why = []
    if md == h10_lord:
        score += 3
        why.append(f'''10L ({h10_lord}) MD — career-launch''')
    elif ad == h10_lord:
        score += 2
        why.append('10L AD')
    if md == h11_lord or ad == h11_lord:
        score += 1
        why.append('11L (gains) active')
    if md == 'Mercury' or ad == 'Mercury':
        score += 1
        why.append('Mercury (commerce) active')
    if md == 'Rahu' and _h(pos, 'Rahu') in (10, 11, 3):
        score += 2
        why.append('Rahu MD + commerce houses')
    if score < 4:
        return None
    return {
        'event': 'Business launch / self-employment start',
        'category': 'business',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '10L + 11L + Mercury (BPHS Ch.25 Karma)' }


def event_promotion(chart, ds, tr, yogas, age):
    '''Career promotion / authority increase — 10L+11L+Sun.'''
    if age < 22 or age > 65:
        return None
    lagna_idx = chart['lagna_idx']
    h10_lord = _lord(lagna_idx, 10)
    h11_lord = _lord(lagna_idx, 11)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h10_lord and ad == h11_lord:
        score += 4
        why.append('10L MD + 11L AD — promotion')
    elif md == h11_lord and ad == h10_lord:
        score += 3
        why.append('11L MD + 10L AD')
    elif md in (h10_lord, h11_lord):
        score += 2
        why.append('career-house lord MD')
    if md == 'Sun' or ad == 'Sun':
        score += 1
        why.append('Sun (authority) active')
    if md == 'Jupiter' or ad == 'Jupiter':
        score += 1
        why.append('Jupiter active')
    if score < 4:
        return None
    return {
        'event': 'Career promotion / authority increase',
        'category': 'promotion',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '10L + 11L combination + Sun authority (Phaladeepika Ch.7)' }


def event_legal_dispute(chart, ds, tr, yogas, age):
    '''6H disputes — Mars + 6L + Saturn malefic stacks.'''
    if age < 18:
        return None
    pos = chart['positions']
    lagna_idx = chart['lagna_idx']
    h6_lord = _lord(lagna_idx, 6)
    h8_lord = _lord(lagna_idx, 8)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    pd = ds.get(3, { }).get('pd')
    score = 0
    why = []
    if md == h6_lord:
        score += 3
        why.append(f'''6L ({h6_lord}) MD — dispute/disease/debt''')
    elif ad == h6_lord:
        score += 2
        why.append('6L AD')
    if md == h8_lord:
        score += 1
        why.append(f'''8L ({h8_lord}) MD''')
    if md in ('Mars', 'Saturn') and ad in ('Mars', 'Saturn', 'Rahu'):
        score += 2
        why.append(f'''{md} MD + {ad} AD — malefic stack''')
    if md == 'Rahu' and ad in (h6_lord, 'Saturn'):
        score += 2
        why.append('Rahu MD + 6L/Saturn')
    sat_to_lagna = (lambda .0: pass# WARNING: Decompyle incomplete
)(tr(), None)
    if sat_to_lagna:
        score += 1
        why.append('Saturn over Sun — government conflict')
    if score < 5:
        return None
    return {
        'event': 'Legal dispute / IT raid / court case / debt crisis',
        'category': 'legal_dispute',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '6L + Mars-Saturn (BPHS Ch.40 Roga + 6H rules)' }


def event_inheritance(chart, ds, tr, yogas, age):
    '''8H sudden gain — inheritance, insurance, gambling, hidden gains.'''
    if age < 25 or age > 80:
        return None
    lagna_idx = chart['lagna_idx']
    h8_lord = _lord(lagna_idx, 8)
    h11_lord = _lord(lagna_idx, 11)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h8_lord and ad == 'Jupiter':
        score += 4
        why.append('8L MD + Jupiter AD — inheritance combo')
    elif md == h8_lord:
        score += 2
        why.append(f'''8L ({h8_lord}) MD''')
    elif ad == h8_lord:
        score += 1
        why.append('8L AD')
    if md == h11_lord or ad == h11_lord:
        score += 1
        why.append('11L (gains) active')
    if md == 'Jupiter' and ad == h11_lord:
        score += 1
        why.append('Jupiter MD + 11L AD — Dhana boost')
    if score < 4:
        return None
    return {
        'event': 'Inheritance / insurance / sudden gain',
        'category': 'inheritance',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '8L + 11L + Jupiter (BPHS Ch.36 Sudden Gains)' }


def event_speculation_gain(chart, ds, tr, yogas, age):
    '''5H/11H speculation — lottery, stocks, crypto, racing.'''
    if age < 18 or age > 70:
        return None
    pos = chart['positions']
    lagna_idx = chart['lagna_idx']
    h5_lord = _lord(lagna_idx, 5)
    h11_lord = _lord(lagna_idx, 11)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h5_lord and ad == h11_lord:
        score += 4
        why.append('5L MD + 11L AD — speculation peak')
    elif md == h11_lord and ad == h5_lord:
        score += 3
        why.append('11L MD + 5L AD')
    if md == 'Jupiter':
        if ad == h5_lord or ad == h11_lord:
            score += 2
            why.append('Jupiter MD + 5L/11L AD')
    if md == 'Rahu' and ad in (h5_lord, h11_lord):
        score += 2
        why.append('Rahu MD + speculation house — sudden gain')
    if _h(pos, 'Rahu') in (5, 11):
        score += 1
        why.append('Rahu in 5H/11H — gambler signature')
    if score < 5:
        return None
    return {
        'event': 'Speculation / lottery / stock-market gain',
        'category': 'speculation_gain',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '5L + 11L + Rahu (BPHS Ch.20)' }


def event_speculation_loss(chart, ds, tr, yogas, age):
    '''5H/8H/12H speculation loss — investment crash, gambling loss.'''
    if age < 18 or age > 70:
        return None
    lagna_idx = chart['lagna_idx']
    h5_lord = _lord(lagna_idx, 5)
    h8_lord = _lord(lagna_idx, 8)
    h12_lord = _lord(lagna_idx, 12)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h12_lord and ad == h5_lord:
        score += 3
        why.append('12L MD + 5L AD — speculation drain')
    if md == h8_lord and ad == h5_lord:
        score += 3
        why.append('8L MD + 5L AD — sudden 5H loss')
    if md == 'Rahu' and ad in (h5_lord, h12_lord):
        score += 2
        why.append('Rahu MD + loss-house — bubble pop')
    if md == 'Saturn' and ad == h5_lord:
        score += 1
        why.append('Saturn MD + 5L AD')
    if score < 5:
        return None
    return {
        'event': 'Speculation / investment loss / market crash hit',
        'category': 'speculation_loss',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '5L + 8L + 12L + Rahu (BPHS Ch.40 Loss Yogas)' }


def event_in_law_event(chart, ds, tr, yogas, age):
    """In-law events — 2H/7H/11H combinations (spouse's family)."""
    if age < 18 or age > 80:
        return None
    lagna_idx = chart['lagna_idx']
    h2_lord = _lord(lagna_idx, 2)
    h7_lord = _lord(lagna_idx, 7)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h7_lord and ad == h2_lord:
        score += 3
        why.append('7L MD + 2L AD — in-law family event')
    if md == h2_lord and ad == h7_lord:
        score += 3
        why.append('2L MD + 7L AD')
    if md == 'Jupiter' or ad == 'Jupiter':
        score += 1
        why.append('Jupiter active')
    if score < 4:
        return None
    return {
        'event': 'In-law family event — birth / death / wedding / dispute',
        'category': 'in_law_event',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '2L + 7L (Phaladeepika Ch.13)' }


def event_friend_loss(chart, ds, tr, yogas, age):
    '''11H friend loss / network shrink.'''
    if age < 18 or age > 80:
        return None
    lagna_idx = chart['lagna_idx']
    h11_lord = _lord(lagna_idx, 11)
    h12_lord = _lord(lagna_idx, 12)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h12_lord and ad == h11_lord:
        score += 3
        why.append('12L MD + 11L AD — friend-loss')
    if md == 'Ketu' and ad == h11_lord:
        score += 2
        why.append('Ketu MD + 11L AD — sudden separation')
    if md == 'Saturn' and ad == h11_lord:
        score += 2
        why.append('Saturn MD + 11L AD')
    if score < 4:
        return None
    return {
        'event': 'Loss of friends / network contraction',
        'category': 'friend_loss',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '12L + 11L Ketu Saturn (BPHS Ch.45)' }


def event_partnership_formation(chart, ds, tr, yogas, age):
    '''7H business partnership formation — Venus + 7L + Mercury.'''
    if age < 22 or age > 65:
        return None
    lagna_idx = chart['lagna_idx']
    h7_lord = _lord(lagna_idx, 7)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h7_lord:
        score += 3
        why.append(f'''7L ({h7_lord}) MD — partnership house''')
    elif ad == h7_lord:
        score += 2
        why.append('7L AD')
    if md == 'Venus' or ad == 'Venus':
        score += 1
        why.append('Venus active')
    if md == 'Mercury' and ad == h7_lord:
        score += 1
        why.append('Mercury MD + 7L AD — contract')
    if score < 4:
        return None
    return {
        'event': 'Business partnership / public contract / venture formation',
        'category': 'partnership',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '7L + Venus + Mercury (BPHS Ch.13)' }


def event_partnership_break(chart, ds, tr, yogas, age):
    '''7H partnership dissolution — Mars/Saturn/Ketu + 7L stress.'''
    if age < 22 or age > 75:
        return None
    lagna_idx = chart['lagna_idx']
    h7_lord = _lord(lagna_idx, 7)
    h12_lord = _lord(lagna_idx, 12)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md in ('Saturn', 'Ketu', 'Mars') and ad == h7_lord:
        score += 3
        why.append(f'''{md} MD + 7L AD — partnership fracture''')
    if md == h12_lord and ad == h7_lord:
        score += 2
        why.append('12L MD + 7L AD — loss of partner')
    if score < 4:
        return None
    return {
        'event': 'Business partnership dissolution / split with partner',
        'category': 'partnership_break',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '7L afflicted + Mars/Saturn (BPHS Ch.13)' }


def event_pet_acquisition(chart, ds, tr, yogas, age):
    '''6H pet acquisition — Mercury (animals) + 6L.'''
    if age < 5 or age > 80:
        return None
    lagna_idx = chart['lagna_idx']
    h6_lord = _lord(lagna_idx, 6)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h6_lord and ad in ('Mercury', 'Venus'):
        score += 3
        why.append('6L MD + benefic AD — pet')
    elif md == 'Mercury' or ad == 'Mercury':
        score += 1
        why.append('Mercury active')
    if md == 'Ketu' and ad in ('Mercury', h6_lord):
        score += 2
        why.append('Ketu MD — animal/companion')
    if score < 4:
        return None
    return {
        'event': 'Pet acquisition / animal companion',
        'category': 'pet_acquisition',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '6L + Mercury + Ketu (BPHS Ch.45)' }


def event_charity_donation(chart, ds, tr, yogas, age):
    '''12H major donation / philanthropy — Jupiter + 12L + 9L.'''
    if age < 25:
        return None
    lagna_idx = chart['lagna_idx']
    h9_lord = _lord(lagna_idx, 9)
    h12_lord = _lord(lagna_idx, 12)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Jupiter' and ad in (h9_lord, h12_lord):
        score += 3
        why.append('Jupiter MD + dharma-house AD')
    if md == h12_lord:
        score += 2
        why.append('12L MD — outflow of resources')
    if md == h9_lord and ad == 'Jupiter':
        score += 2
        why.append('9L MD + Jupiter AD — dharma')
    if score < 4:
        return None
    return {
        'event': 'Major charitable donation / philanthropy / foundation',
        'category': 'charity',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': 'Jupiter + 9L + 12L (BPHS Ch.40 Daana)' }


def event_visa_grant(chart, ds, tr, yogas, age):
    '''9H/12H visa / passport / immigration approval.'''
    if age < 16:
        return None
    lagna_idx = chart['lagna_idx']
    h9_lord = _lord(lagna_idx, 9)
    h12_lord = _lord(lagna_idx, 12)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md in (h9_lord, h12_lord):
        score += 2
        why.append('foreign-house lord MD')
    if md == 'Rahu' and ad in (h9_lord, h12_lord, 'Mercury'):
        score += 3
        why.append(f'''Rahu MD + foreign-AD ({ad}) — visa/immigration''')
    if md == 'Mercury' and ad in (h9_lord, h12_lord):
        score += 2
        why.append('Mercury MD + 9L/12L AD')
    if score < 4:
        return None
    return {
        'event': 'Visa / passport / immigration approval',
        'category': 'visa',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '9L + 12L + Rahu (BPHS Ch.13)' }


def event_eclipse_impact(chart, ds, tr, yogas, age):
    '''Solar/Lunar eclipse over natal Sun/Moon/Lagna — life inflection.'''
    if age < 5:
        return None
    score = 0
    why = []
    eclipse_sun = (lambda .0: pass# WARNING: Decompyle incomplete
)(tr(), None)
    eclipse_moon = (lambda .0: pass# WARNING: Decompyle incomplete
)(tr(), None)
    if eclipse_sun:
        score += 4
        why.append(f'''Eclipse over natal {eclipse_sun.get('natal')}''')
    if eclipse_moon:
        score += 3
        why.append('Eclipse over natal Moon — emotional inflection')
    rahu_to_sun = (lambda .0: pass# WARNING: Decompyle incomplete
)(tr(), None)
    if rahu_to_sun:
        score += 2
        why.append(f'''Node transit over {rahu_to_sun.get('natal')}''')
    if score < 4:
        return None
    return {
        'event': 'Eclipse impact — major life inflection / hidden revelation',
        'category': 'eclipse_impact',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': 'Eclipse over natal sensitive points (Phaladeepika Ch.27)' }


def event_saturn_return(chart, ds, tr, yogas, age):
    '''Saturn return — 28-30, 56-60, 84-90 year cycles.'''
    if not  <= 27, age or 27, age <= 31:
        pass
    
    if not  <= 55, age or 55, age <= 61:
        pass
    
    if not  <= 83, age or 83, age <= 91:
        return None
        return None
    [
        'Saturn return age-window — maturity inflection point'] = 4
    sret = (lambda .0: pass# WARNING: Decompyle incomplete
)(tr(), None)
    if sret:
        score += 2
        why.append(f'''Saturn return active (orb {sret.get('orb', '?')}°)''')
    return {
        'event': 'Saturn return — major maturity / responsibility inflection',
        'category': 'saturn_return',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': "Saturn's 29.5-year orbital cycle (BPHS Ch.45 Ayur)" }


def event_jupiter_return(chart, ds, tr, yogas, age):
    '''Jupiter return — every ~12 years brings expansion.'''
    if age < 11:
        return None
    if age % 12 not in (11, 12, 0, 1):
        return None
    score = 3
    why = [
        f'''Jupiter return age-window (~{(age // 12) * 12})''']
    return {
        'event': 'Jupiter return — expansion / wisdom / opportunity cycle',
        'category': 'jupiter_return',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': "Jupiter's 12-year orbital cycle" }


def event_pregnancy(chart, ds, tr, yogas, age):
    '''5H pregnancy (distinct from birth) — fits gestation window.'''
    if age < 18 or age > 50:
        return None
    pos = chart['positions']
    lagna_idx = chart['lagna_idx']
    h5_lord = _lord(lagna_idx, 5)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    pd = ds.get(3, { }).get('pd')
    score = 0
    why = []
    if md == h5_lord or ad == h5_lord:
        score += 2
        why.append(f'''5L ({h5_lord}) active''')
    if md == 'Jupiter' or ad == 'Jupiter':
        score += 2
        why.append('Jupiter (Putrakaraka) active')
    if md == 'Moon' or ad == 'Moon':
        score += 1
        why.append('Moon (gestation karaka) active')
    if score < 4:
        return None
    return {
        'event': 'Pregnancy / conception',
        'category': 'pregnancy',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '5L + Jupiter + Moon (BPHS Ch.80 Putra Bhava)' }


def event_engagement(chart, ds, tr, yogas, age):
    '''7H engagement (distinct from marriage).'''
    if age < 18 or age > 60:
        return None
    lagna_idx = chart['lagna_idx']
    h7_lord = _lord(lagna_idx, 7)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    pd = ds.get(3, { }).get('pd')
    score = 0
    why = []
    if md == 'Venus' and ad == h7_lord:
        score += 3
        why.append('Venus MD + 7L AD — engagement window')
    if ad == 'Venus' and pd in (h7_lord, 'Jupiter'):
        score += 2
        why.append('Venus AD + 7L/Jupiter PD')
    if md == 'Jupiter' and ad == 'Venus':
        score += 2
        why.append('Jupiter MD + Venus AD')
    if score < 3:
        return None
    return {
        'event': 'Engagement / formal commitment to marry',
        'category': 'engagement',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': 'Venus + 7L + Jupiter (BPHS Ch.80 — pre-marriage signal)' }


def event_book_publication(chart, ds, tr, yogas, age):
    '''9H/3H publication / authorship / public writing.'''
    if age < 22:
        return None
    lagna_idx = chart['lagna_idx']
    h3_lord = _lord(lagna_idx, 3)
    h9_lord = _lord(lagna_idx, 9)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Mercury' and ad in (h3_lord, h9_lord):
        score += 3
        why.append('Mercury MD + writing-house AD')
    if md == h9_lord and ad == 'Mercury':
        score += 2
        why.append('9L MD + Mercury AD')
    if md == 'Jupiter' and ad == 'Mercury':
        score += 2
        why.append('Jupiter MD + Mercury AD — wisdom-publication')
    if score < 4:
        return None
    return {
        'event': 'Book publication / authored work release',
        'category': 'publication',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': 'Mercury + 3L + 9L + Jupiter (Saravali Ch.30)' }


def event_award_nomination(chart, ds, tr, yogas, age):
    '''11H award nomination (distinct from win).'''
    if age < 12:
        return None
    lagna_idx = chart['lagna_idx']
    h11_lord = _lord(lagna_idx, 11)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h11_lord:
        score += 2
        why.append(f'''11L ({h11_lord}) MD — recognition''')
    if md == 'Sun' or ad == 'Sun':
        score += 1
        why.append('Sun (honor karaka) active')
    if md == 'Jupiter' or ad == 'Jupiter':
        score += 1
        why.append('Jupiter active')
    if score < 3:
        return None
    return {
        'event': 'Award nomination / honor candidacy',
        'category': 'award_nomination',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '11L + Sun + Jupiter (Phaladeepika Ch.6)' }


def event_house_construction(chart, ds, tr, yogas, age):
    '''4H construction (distinct from purchase) — Saturn + Mars labor.'''
    if age < 22 or age > 75:
        return None
    pos = chart['positions']
    lagna_idx = chart['lagna_idx']
    h4_lord = _lord(lagna_idx, 4)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h4_lord and ad in ('Mars', 'Saturn'):
        score += 3
        why.append(f'''4L MD + {ad} AD — construction''')
    if md == 'Mars' and _h(pos, 'Mars') in (4, 10):
        score += 2
        why.append('Mars + property house active')
    if md == 'Saturn' and _h(pos, 'Saturn') in (4, 10):
        score += 1
        why.append('Saturn + property house')
    if score < 4:
        return None
    return {
        'event': 'House construction / land development',
        'category': 'construction',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '4L + Mars + Saturn (BPHS Ch.23)' }


def event_grandchildren_birth(chart, ds, tr, yogas, age):
    """9H grandchildren (5H from 5H = own children's children)."""
    if age < 40 or age > 90:
        return None
    lagna_idx = chart['lagna_idx']
    h9_lord = _lord(lagna_idx, 9)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h9_lord:
        score += 2
        why.append(f'''9L ({h9_lord}) MD — grandchild house (5H from 5H)''')
    if md == 'Jupiter' or ad == 'Jupiter':
        score += 2
        why.append('Jupiter (Putrakaraka) active')
    if score < 4:
        return None
    return {
        'event': 'Grandchildren birth / 3rd-generation arrival',
        'category': 'grandchildren',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '9L (5H from 5H) + Jupiter (BPHS Ch.80)' }


def event_brand_endorsement(chart, ds, tr, yogas, age):
    '''11H brand deal / sponsorship — modern fame-monetization event.'''
    if age < 18 or age > 70:
        return None
    lagna_idx = chart['lagna_idx']
    h2_lord = _lord(lagna_idx, 2)
    h11_lord = _lord(lagna_idx, 11)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h11_lord and ad in (h2_lord, 'Venus'):
        score += 3
        why.append('11L MD + 2L/Venus AD — endorsement')
    if md == 'Venus' and ad == h11_lord:
        score += 2
        why.append('Venus MD + 11L AD — beauty-brand')
    if md == 'Rahu' and ad in (h11_lord, 'Mercury'):
        score += 2
        why.append('Rahu MD + 11L/Mercury — modern brand')
    if score < 4:
        return None
    return {
        'event': 'Brand endorsement / sponsorship / advertising deal',
        'category': 'brand_deal',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '11L + 2L + Venus + Rahu (modern Phaladeepika ext.)' }


def event_political_office(chart, ds, tr, yogas, age):
    '''10H elected office (CM / PM / public role) — distinct from generic career band.'''
    if age < 28 or age > 90:
        return None
    lagna_idx = chart['lagna_idx']
    h10_lord = _lord(lagna_idx, 10)
    h9_lord = _lord(lagna_idx, 9)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    pd = ds.get(3, { }).get('pd')
    score = 0
    why = []
    if md == h10_lord and ad == 'Sun':
        score += 4
        why.append('10L MD + Sun AD — oath of office / authority')
    elif md == h10_lord and ad in ('Jupiter', 'Mercury'):
        score += 3
        why.append(f'''10L MD + {ad} AD — executive tenure''')
    elif md == h10_lord:
        score += 2
        why.append(f'''10L ({h10_lord}) MD — public office period''')
    if md == 'Sun' and ad == h10_lord:
        score += 3
        why.append('Sun MD + 10L AD — high office')
    if md == 'Jupiter' and ad in (h10_lord, h9_lord):
        score += 2
        why.append(f'''Jupiter MD + {ad} AD — dharma / state role''')
    if md == 'Saturn' and ad == h10_lord and age >= 45:
        score += 2
        why.append('Saturn MD + 10L AD — long-run executive peak')
    if pd == h10_lord and score >= 2:
        score += 1
        why.append('10L PD — office activation')
    sun_h10 = (lambda .0: pass# WARNING: Decompyle incomplete
)(tr(), None)
    if sun_h10:
        score += 1
        why.append('Sun transit 10th — public visibility')
    if score < 3:
        return None
    return {
        'event': 'Elected to public / political office',
        'category': 'political_office',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '10L + Sun + Jupiter + Saturn (BPHS Ch.25 + Saravali Raja Yogas)' }


def event_jail_confinement(chart, ds, tr, yogas, age):
    '''12H jail / detention / forced confinement — Saturn + Rahu + 12L.'''
    if age < 18:
        return None
    pos = chart['positions']
    lagna_idx = chart['lagna_idx']
    h6_lord = _lord(lagna_idx, 6)
    h12_lord = _lord(lagna_idx, 12)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h12_lord and ad in ('Saturn', 'Rahu', 'Ketu', 'Mars'):
        score += 4
        why.append(f'''12L MD + {ad} AD — confinement''')
    if md == 'Saturn' and ad == h6_lord:
        score += 2
        why.append('Saturn MD + 6L AD — institutional restraint')
    if md == 'Rahu' and ad == h12_lord:
        score += 2
        why.append('Rahu MD + 12L AD — sudden detention')
    if score < 5:
        return None
    return {
        'event': 'Jail / institutional confinement / detention / forced isolation',
        'category': 'jail',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '12L + 6L + Saturn + Rahu (BPHS Ch.45)' }


def event_tax_dispute(chart, ds, tr, yogas, age):
    '''6H government tax / IT raid issues.'''
    if age < 22:
        return None
    lagna_idx = chart['lagna_idx']
    h6_lord = _lord(lagna_idx, 6)
    h2_lord = _lord(lagna_idx, 2)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h6_lord and ad == h2_lord:
        score += 3
        why.append('6L MD + 2L AD — tax/wealth dispute')
    if md == 'Saturn' and ad == h2_lord:
        score += 2
        why.append('Saturn MD + 2L AD — slow money pressure')
    if md == 'Rahu' and ad in (h6_lord, 'Saturn'):
        score += 2
        why.append('Rahu MD + dispute lord')
    if score < 4:
        return None
    return {
        'event': 'Tax dispute / IT raid / government financial inquiry',
        'category': 'tax_dispute',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '6L + 2L + Saturn + Rahu (modern govt ext.)' }


def event_voice_career(chart, ds, tr, yogas, age):
    '''2H voice career — singing, dubbing, public speaking, news anchor.'''
    if age < 12 or age > 80:
        return None
    lagna_idx = chart['lagna_idx']
    h2_lord = _lord(lagna_idx, 2)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h2_lord and ad in ('Venus', 'Mercury'):
        score += 3
        why.append(f'''2L MD + {ad} AD — voice career''')
    if md == 'Venus' and ad == h2_lord:
        score += 2
        why.append('Venus MD + 2L AD — vocal arts')
    if md == 'Mercury' and ad == h2_lord:
        score += 2
        why.append('Mercury MD + 2L AD — speech/communication')
    if score < 4:
        return None
    return {
        'event': 'Voice career milestone — singing, dubbing, anchor, oratory',
        'category': 'voice_career',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '2L + Venus + Mercury (BPHS Ch.13)' }


def event_retirement(chart, ds, tr, yogas, age):
    '''10H/12H retirement from active career.'''
    if age < 50:
        return None
    lagna_idx = chart['lagna_idx']
    h10_lord = _lord(lagna_idx, 10)
    h12_lord = _lord(lagna_idx, 12)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h12_lord and ad == h10_lord:
        score += 3
        why.append('12L MD + 10L AD — career-exit')
    if md == 'Saturn' and age >= 60:
        score += 2
        why.append(f'''Saturn MD age {age} — natural retirement''')
    if md == 'Ketu' and ad == h10_lord:
        score += 2
        why.append('Ketu MD + 10L AD — detachment from career')
    if score < 4:
        return None
    return {
        'event': 'Retirement / career step-down / exit from public life',
        'category': 'retirement',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '12L + 10L + Saturn + Ketu (BPHS Ch.25)' }


def event_share_purchase(chart, ds, tr, yogas, age):
    '''5H/11H share/stock purchase or equity investment — Mercury + 5L + 11L.'''
    if age < 18 or age > 75:
        return None
    pos = chart['positions']
    lagna_idx = chart['lagna_idx']
    h5_lord = _lord(lagna_idx, 5)
    h11_lord = _lord(lagna_idx, 11)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    pd = ds.get(3, { }).get('pd')
    score = 0
    why = []
    if md == h5_lord:
        score += 3
        why.append(f'''5L ({h5_lord}) MD — investment house active''')
    elif ad == h5_lord:
        score += 2
        why.append('5L AD')
    if md == h11_lord or ad == h11_lord:
        score += 1
        why.append(f'''11L ({h11_lord}) (gains) active''')
    if md == 'Mercury' or ad == 'Mercury':
        score += 1
        why.append('Mercury (trading/shares) active')
    if md == 'Rahu' and ad in (h5_lord, h11_lord):
        score += 2
        why.append('Rahu MD + investment/gains house — speculative equity buy')
    if score < 4:
        return None
    return {
        'event': 'Share / stock purchase or major equity investment',
        'category': 'speculation_gain',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '5L + 11L + Mercury (Hora Sara Ch.20)' }


def event_birth_circumstances(chart, ds, tr, yogas, age):
    '''1H — premature / C-section / unusual birth.'''
    if age != 0:
        return None
    pos = chart['positions']
    score = 0
    why = []
    if _h(pos, 'Saturn') in (1, 8):
        score += 2
        why.append('Saturn in 1H/8H')
    if _h(pos, 'Mars') in (1, 8):
        score += 2
        why.append('Mars in 1H/8H — surgical')
    if _h(pos, 'Rahu') in (1, 8):
        score += 1
        why.append('Rahu in 1H/8H')
    if score < 3:
        return None
    return {
        'event': 'Birth circumstances — premature/C-section/unusual',
        'category': 'birth_circumstance',
        'severity': min(5, score),
        'yoga': None,
        'why': why,
        'source': '1H+8H natal malefics (BPHS Ch.4)' }


def event_personality_shift(chart, ds, tr, yogas, age):
    '''Identity reinvention — Saturn/Rahu MD + lagna lord AD.'''
    if age < 20:
        return None
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    asc_lord = chart.get('lagna_lord')
    score = 0
    why = []
    if md in ('Saturn', 'Rahu', 'Ketu') and ad == asc_lord:
        score += 3
        why.append(f'''{md} MD + lagna lord AD — identity shift''')
    if md == 'Rahu' and ad in ('Saturn', 'Ketu'):
        score += 2
        why.append('Rahu MD + Saturn/Ketu AD')
    if score < 3:
        return None
    return {
        'event': 'Major personality/identity reinvention',
        'category': 'personality_shift',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': 'Lagna lord + Saturn/Rahu (BPHS Ch.4)' }


def event_charisma_peak(chart, ds, tr, yogas, age):
    '''Charisma cycle — Moon + Venus + lagna lord active.'''
    if age < 18:
        return None
    pos = chart['positions']
    asc_lord = chart.get('lagna_lord')
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == asc_lord and ad in ('Moon', 'Venus', 'Jupiter'):
        score += 3
        why.append(f'''lagna lord MD + {ad} AD''')
    if md == 'Moon' and _h(pos, 'Moon') in (1, 4, 10):
        score += 2
        why.append('Moon kendra')
    if md == 'Venus' or ad == 'Venus':
        score += 1
        why.append('Venus active')
    if score < 4:
        return None
    return {
        'event': 'Charisma/personal magnetism peak',
        'category': 'charisma',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': 'Lagna+Moon+Venus (BPHS Ch.4)' }


def event_voice_loss(chart, ds, tr, yogas, age):
    '''2H voice issues.'''
    if age < 12:
        return None
    lagna_idx = chart['lagna_idx']
    h2_lord = _lord(lagna_idx, 2)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h2_lord and ad in ('Saturn', 'Mars', 'Rahu', 'Ketu'):
        score += 3
        why.append(f'''2L MD + {ad} AD''')
    if md in ('Saturn', 'Ketu') and ad == 'Venus':
        score += 2
        why.append(f'''{md}+Venus throat''')
    if score < 4:
        return None
    return {
        'event': 'Voice/throat issue — laryngitis/surgery',
        'category': 'voice_issue',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '2L+Venus+Saturn (BPHS Ch.13)' }


def event_dental_event(chart, ds, tr, yogas, age):
    '''2H dental.'''
    if age < 5:
        return None
    lagna_idx = chart['lagna_idx']
    h2_lord = _lord(lagna_idx, 2)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h2_lord and ad in ('Mars', 'Saturn'):
        score += 3
        why.append(f'''2L+{ad} dental''')
    if md == 'Mars' and ad == h2_lord:
        score += 2
        why.append('Mars MD+2L AD')
    if score < 4:
        return None
    return {
        'event': 'Dental event — tooth loss/extraction/RCT/surgery',
        'category': 'dental',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '2L+Mars (BPHS Ch.40)' }


def event_eye_problem(chart, ds, tr, yogas, age):
    '''Right (2H Sun) + Left (12H Moon) eye issues.'''
    if age < 18:
        return None
    pos = chart['positions']
    lagna_idx = chart['lagna_idx']
    h2_lord = _lord(lagna_idx, 2)
    h12_lord = _lord(lagna_idx, 12)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h2_lord and ad in ('Sun', 'Saturn'):
        score += 3
        why.append(f'''2L+{ad} right eye''')
    if md == h12_lord and ad in ('Moon', 'Saturn'):
        score += 3
        why.append(f'''12L+{ad} left eye''')
    if _h(pos, 'Sun') in (2, 12) and md == 'Saturn':
        score += 1
        why.append('Sun-2/12+Saturn')
    if score < 4:
        return None
    return {
        'event': 'Eye/vision issue — surgery/cataract',
        'category': 'eye_issue',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '2L+12L+Sun+Moon (BPHS Ch.40)' }


def event_diet_change(chart, ds, tr, yogas, age):
    '''2H + Jupiter/Ketu dharma-driven diet shift.'''
    if age < 12:
        return None
    lagna_idx = chart['lagna_idx']
    h2_lord = _lord(lagna_idx, 2)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h2_lord and ad in ('Jupiter', 'Ketu'):
        score += 3
        why.append(f'''2L+{ad} diet shift''')
    if md == 'Ketu' and ad == h2_lord:
        score += 2
        why.append('Ketu MD+2L AD')
    if md == 'Jupiter' and ad == h2_lord:
        score += 1
        why.append('Jupiter MD+2L AD')
    if score < 3:
        return None
    return {
        'event': 'Diet shift — fasting/vegetarian/allergy',
        'category': 'diet_change',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '2L+Jupiter+Ketu (Hora Sara)' }


def event_sibling_marriage(chart, ds, tr, yogas, age):
    '''3H sibling marriage.'''
    if age < 10 or age > 75:
        return None
    lagna_idx = chart['lagna_idx']
    h3_lord = _lord(lagna_idx, 3)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h3_lord and ad == 'Venus':
        score += 3
        why.append('3L+Venus sibling marriage')
    if md == 'Mars' and ad == 'Venus':
        score += 2
        why.append('Mars+Venus sibling-spouse')
    if score < 4:
        return None
    return {
        'event': 'Sibling marriage',
        'category': 'sibling_marriage',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '3L+Mars+Venus (BPHS Ch.13)' }


def event_sibling_death(chart, ds, tr, yogas, age):
    '''3H sibling death — 8H from 3H = 10H.'''
    if age < 18:
        return None
    lagna_idx = chart['lagna_idx']
    h3_lord = _lord(lagna_idx, 3)
    h10_lord = _lord(lagna_idx, 10)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h10_lord and ad in ('Mars', 'Saturn', 'Ketu'):
        score += 3
        why.append('10L (8H from 3H) + malefic')
    if md == 'Mars' and ad == h3_lord:
        score += 2
        why.append('Mars+3L sibling stress')
    if score < 4:
        return None
    return {
        'event': 'Sibling death/illness',
        'category': 'sibling_death',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '10L+Mars (BPHS Ch.45)' }


def event_hand_arm_injury(chart, ds, tr, yogas, age):
    '''3H hand/arm — Mars triggers.'''
    if age < 5:
        return None
    pos = chart['positions']
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Mars' and _h(pos, 'Mars') in (3, 6, 8):
        score += 3
        why.append('Mars MD+Mars in hand-houses')
    if md == 'Saturn' and _h(pos, 'Saturn') == 3:
        score += 1
        why.append('Saturn MD+3H')
    mars_to_mars = (lambda .0: pass# WARNING: Decompyle incomplete
)(tr(), None)
    if mars_to_mars:
        score += 1
        why.append('Mars over natal Mars')
    if score < 4:
        return None
    return {
        'event': 'Hand/arm/wrist injury',
        'category': 'hand_injury',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': 'Mars+3H (BPHS Ch.4)' }


def event_hearing_issue(chart, ds, tr, yogas, age):
    '''3H/11H ear.'''
    if age < 30:
        return None
    lagna_idx = chart['lagna_idx']
    h3_lord = _lord(lagna_idx, 3)
    h11_lord = _lord(lagna_idx, 11)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md in (h3_lord, h11_lord) and ad in ('Saturn', 'Ketu'):
        score += 3
        why.append(f'''ear-house+{ad}''')
    if score < 4:
        return None
    return {
        'event': 'Hearing issue — tinnitus/deafness/ear surgery',
        'category': 'hearing_issue',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '3L+11L+Saturn (BPHS Ch.4)' }


def event_sports_milestone(chart, ds, tr, yogas, age):
    '''Mars + 3H + Sun strong.'''
    if age < 8 or age > 50:
        return None
    pos = chart['positions']
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Mars' and _h(pos, 'Mars') in (1, 3, 10):
        score += 3
        why.append('Mars+warrior houses')
    if md == 'Sun' and _h(pos, 'Sun') in (1, 5, 10):
        score += 2
        why.append('Sun+leadership')
    if score < 4:
        return None
    return {
        'event': 'Sports/athletic milestone',
        'category': 'sports_milestone',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': 'Mars+Sun+3H (Saravali)' }


def event_writing_career(chart, ds, tr, yogas, age):
    '''Mercury writing-career.'''
    if age < 18:
        return None
    pos = chart['positions']
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Mercury' and _h(pos, 'Mercury') in (3, 5, 9):
        score += 3
        why.append('Mercury MD+writing houses')
    if md == 'Jupiter' and ad == 'Mercury':
        score += 2
        why.append('Jupiter+Mercury wisdom-writing')
    if score < 4:
        return None
    return {
        'event': 'Writing career milestone',
        'category': 'writing_career',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': 'Mercury+3H+Jupiter (Saravali)' }


def event_home_renovation(chart, ds, tr, yogas, age):
    '''4H renovation.'''
    if age < 22 or age > 80:
        return None
    lagna_idx = chart['lagna_idx']
    h4_lord = _lord(lagna_idx, 4)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h4_lord and ad == 'Mars':
        score += 3
        why.append('4L+Mars construction')
    if md == 'Mars' and ad in (h4_lord, 'Venus'):
        score += 2
        why.append(f'''Mars+{ad}''')
    if score < 4:
        return None
    return {
        'event': 'Home renovation/interior refurbishment',
        'category': 'renovation',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '4L+Mars+Venus (BPHS Ch.23)' }


def event_real_estate_dispute(chart, ds, tr, yogas, age):
    '''4H + 6H land dispute.'''
    if age < 22:
        return None
    lagna_idx = chart['lagna_idx']
    h4_lord = _lord(lagna_idx, 4)
    h6_lord = _lord(lagna_idx, 6)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h4_lord and ad == h6_lord:
        score += 4
        why.append('4L+6L land dispute')
    if md == h6_lord and ad == h4_lord:
        score += 3
        why.append('6L+4L')
    if md == 'Mars' and ad == h4_lord:
        score += 1
        why.append('Mars+4L heated')
    if score < 4:
        return None
    return {
        'event': 'Real estate/land/property dispute',
        'category': 'property_dispute',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '4L+6L+Mars (BPHS Ch.23)' }


def event_move_new_city(chart, ds, tr, yogas, age):
    '''4H + 12H relocation.'''
    if age < 16:
        return None
    lagna_idx = chart['lagna_idx']
    h4_lord = _lord(lagna_idx, 4)
    h12_lord = _lord(lagna_idx, 12)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h12_lord and ad == h4_lord:
        score += 4
        why.append('12L+4L move from home')
    if md == 'Rahu' and ad in (h4_lord, 'Mercury'):
        score += 2
        why.append('Rahu+4L/Mercury')
    if score < 4:
        return None
    return {
        'event': 'Relocation to new city/state',
        'category': 'relocation',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '4L+12L+Rahu (BPHS Ch.13)' }


def event_romance_affair(chart, ds, tr, yogas, age):
    '''Venus+Rahu+5H affair.'''
    if age < 18 or age > 70:
        return None
    pos = chart['positions']
    lagna_idx = chart['lagna_idx']
    h5_lord = _lord(lagna_idx, 5)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Venus' and ad == h5_lord:
        score += 3
        why.append('Venus+5L romance')
    if md == 'Rahu' and ad == 'Venus':
        score += 3
        why.append('Rahu+Venus unconventional')
    if md == h5_lord and _h(pos, 'Venus') in (5, 7, 11):
        score += 1
        why.append('5L+Venus love-house')
    if score < 4:
        return None
    return {
        'event': 'Romantic affair/love relationship',
        'category': 'romance',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '5L+Venus+Rahu (BPHS Ch.13)' }


def event_first_love(chart, ds, tr, yogas, age):
    '''Venus first activation.'''
    if age < 14 or age > 28:
        return None
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Venus' and age < 25:
        score += 3
        why.append('Venus MD in youth')
    if ad == 'Venus' and age < 22:
        score += 2
        why.append('Venus AD in adolescence')
    if score < 3:
        return None
    return {
        'event': 'First love/infatuation',
        'category': 'first_love',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': 'Venus first (Hora Sara)' }


def event_mantra_siddhi(chart, ds, tr, yogas, age):
    '''5H+Jupiter+Ketu spiritual fruit.'''
    if age < 20:
        return None
    pos = chart['positions']
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Jupiter' and ad == 'Ketu':
        score += 3
        why.append('Jupiter+Ketu siddhi')
    if md == 'Ketu' and ad == 'Jupiter':
        score += 3
        why.append('Ketu+Jupiter')
    if _h(pos, 'Jupiter') in (5, 9, 12) and md == 'Jupiter':
        score += 1
        why.append('Jupiter dharma-house')
    if score < 4:
        return None
    return {
        'event': 'Mantra siddhi/spiritual breakthrough',
        'category': 'mantra_siddhi',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': 'Jupiter+Ketu (Hora Sara Ch.25)' }


def event_creative_breakthrough(chart, ds, tr, yogas, age):
    '''5H+Venus/Mercury creative peak.'''
    if age < 16:
        return None
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    lagna_idx = chart['lagna_idx']
    h5_lord = _lord(lagna_idx, 5)
    score = 0
    why = []
    if md == 'Venus' and ad in (h5_lord, 'Mercury'):
        score += 3
        why.append(f'''Venus+{ad} creative''')
    if md == h5_lord and ad == 'Venus':
        score += 2
        why.append('5L+Venus')
    if score < 4:
        return None
    return {
        'event': 'Creative breakthrough — art/design/composition',
        'category': 'creative_breakthrough',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '5L+Venus+Mercury (Saravali)' }


def event_devotion_intensify(chart, ds, tr, yogas, age):
    '''Bhakti deepening.'''
    if age < 20:
        return None
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Jupiter' and ad in ('Ketu', 'Moon'):
        score += 3
        why.append(f'''Jupiter+{ad} devotion''')
    if md == 'Ketu' and ad == 'Jupiter':
        score += 2
        why.append('Ketu+Jupiter')
    if score < 3:
        return None
    return {
        'event': 'Devotion/bhakti intensification',
        'category': 'devotion',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': 'Jupiter+Ketu+Moon (Saravali)' }


def event_surgery_major(chart, ds, tr, yogas, age):
    '''8H+Mars.'''
    if age < 5:
        return None
    lagna_idx = chart['lagna_idx']
    h6_lord = _lord(lagna_idx, 6)
    h8_lord = _lord(lagna_idx, 8)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h8_lord and ad == 'Mars':
        score += 4
        why.append('8L+Mars major surgery')
    if md == 'Mars' and ad == h6_lord:
        score += 3
        why.append('Mars+6L surgical')
    if md == h6_lord and ad == 'Mars':
        score += 2
        why.append('6L+Mars')
    if score < 4:
        return None
    return {
        'event': 'Major surgery/operation',
        'category': 'major_surgery',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '6L+8L+Mars (BPHS Ch.40)' }


def event_lawsuit_won(chart, ds, tr, yogas, age):
    '''Jupiter favorable.'''
    if age < 22:
        return None
    lagna_idx = chart['lagna_idx']
    h6_lord = _lord(lagna_idx, 6)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Jupiter' and ad == h6_lord:
        score += 3
        why.append('Jupiter+6L favorable')
    if md == 'Mars' and ad == 'Jupiter':
        score += 2
        why.append('Mars+Jupiter winning')
    if score < 4:
        return None
    return {
        'event': 'Lawsuit/dispute won',
        'category': 'lawsuit_won',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': 'Jupiter+6L (BPHS Ch.40)' }


def event_lawsuit_lost(chart, ds, tr, yogas, age):
    '''6L+Saturn defeat.'''
    if age < 22:
        return None
    lagna_idx = chart['lagna_idx']
    h6_lord = _lord(lagna_idx, 6)
    h12_lord = _lord(lagna_idx, 12)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h6_lord and ad in ('Saturn', 'Ketu'):
        score += 3
        why.append(f'''6L+{ad} lost''')
    if md == h12_lord and ad == h6_lord:
        score += 3
        why.append('12L+6L loss+dispute')
    if score < 4:
        return None
    return {
        'event': 'Lawsuit/dispute lost',
        'category': 'lawsuit_lost',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '6L+Saturn (BPHS Ch.40)' }


def event_workplace_conflict(chart, ds, tr, yogas, age):
    '''6H+10H workplace dispute.'''
    if age < 18 or age > 65:
        return None
    lagna_idx = chart['lagna_idx']
    h6_lord = _lord(lagna_idx, 6)
    h10_lord = _lord(lagna_idx, 10)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h10_lord and ad == h6_lord:
        score += 3
        why.append('10L+6L workplace conflict')
    if md == 'Mars' and ad in (h6_lord, h10_lord):
        score += 2
        why.append('Mars+work/dispute')
    if score < 4:
        return None
    return {
        'event': 'Workplace conflict/office politics',
        'category': 'workplace_conflict',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '6L+10L+Mars (Phaladeepika)' }


def event_marriage_arranged(chart, ds, tr, yogas, age):
    '''Mercury+Saturn+7L formal.'''
    if age < 18 or age > 70:
        return None
    lagna_idx = chart['lagna_idx']
    h7_lord = _lord(lagna_idx, 7)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Mercury' and ad == h7_lord:
        score += 3
        why.append('Mercury+7L matchmaking')
    if md == 'Saturn' and ad == h7_lord:
        score += 2
        why.append('Saturn+7L formal')
    if score < 3:
        return None
    return {
        'event': 'Marriage — arranged/formal alliance',
        'category': 'marriage_arranged',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': 'Mercury+Saturn+7L (BPHS Ch.80)' }


def event_marriage_love(chart, ds, tr, yogas, age):
    '''Venus+Rahu+5L+7L.'''
    if age < 18 or age > 60:
        return None
    lagna_idx = chart['lagna_idx']
    h5_lord = _lord(lagna_idx, 5)
    h7_lord = _lord(lagna_idx, 7)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Venus' and ad == h7_lord:
        score += 4
        why.append('Venus+7L love marriage')
    if md == h5_lord and ad == h7_lord:
        score += 3
        why.append('5L+7L romance to marriage')
    if md == 'Rahu' and ad == 'Venus':
        score += 2
        why.append('Rahu+Venus unconventional')
    if score < 4:
        return None
    return {
        'event': 'Marriage — love/inter-caste/unconventional',
        'category': 'marriage_love',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '5L+7L+Venus+Rahu (BPHS Ch.80)' }


def event_second_marriage(chart, ds, tr, yogas, age):
    '''7H second activation.'''
    if age < 28 or age > 75:
        return None
    lagna_idx = chart['lagna_idx']
    h7_lord = _lord(lagna_idx, 7)
    h2_lord = _lord(lagna_idx, 2)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h7_lord and ad == h2_lord and age >= 40:
        score += 3
        why.append('7L+2L post-40 remarriage')
    if md == 'Venus' and ad in (h7_lord, h2_lord) and age >= 40:
        score += 2
        why.append('Venus+7L/2L post-40')
    if score < 4:
        return None
    return {
        'event': 'Second marriage/remarriage',
        'category': 'second_marriage',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '7L second+2L (BPHS Ch.80)' }


def event_spouse_health_crisis(chart, ds, tr, yogas, age):
    '''2L (8H from 7H) afflicted.'''
    if age < 22 or age > 80:
        return None
    lagna_idx = chart['lagna_idx']
    h7_lord = _lord(lagna_idx, 7)
    h2_lord = _lord(lagna_idx, 2)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h2_lord and ad in ('Saturn', 'Mars', 'Rahu', 'Ketu'):
        score += 3
        why.append(f'''2L+{ad} spouse health''')
    if md == h7_lord and ad in ('Saturn', 'Ketu'):
        score += 2
        why.append(f'''7L+{ad}''')
    if score < 4:
        return None
    return {
        'event': 'Spouse health crisis',
        'category': 'spouse_health',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '7L+2L (BPHS Ch.80)' }


def event_lottery_win(chart, ds, tr, yogas, age):
    '''5H+11H+Rahu sudden gain.'''
    if age < 18:
        return None
    pos = chart['positions']
    lagna_idx = chart['lagna_idx']
    h5_lord = _lord(lagna_idx, 5)
    h11_lord = _lord(lagna_idx, 11)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Rahu' and ad in (h5_lord, h11_lord):
        score += 4
        why.append(f'''Rahu+{ad} sudden lottery''')
    if md == h5_lord and ad == h11_lord:
        score += 3
        why.append('5L+11L')
    if _h(pos, 'Rahu') in (5, 11) and md == 'Rahu':
        score += 1
        why.append('Rahu-5H/11H natal')
    if score < 5:
        return None
    return {
        'event': 'Lottery/gambling sudden win',
        'category': 'lottery_win',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '5L+11L+Rahu (BPHS Ch.36)' }


def event_lottery_loss(chart, ds, tr, yogas, age):
    '''5H+12H Rahu gambling loss.'''
    if age < 18:
        return None
    lagna_idx = chart['lagna_idx']
    h5_lord = _lord(lagna_idx, 5)
    h12_lord = _lord(lagna_idx, 12)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Rahu' and ad == h12_lord:
        score += 3
        why.append('Rahu+12L gambling drain')
    if md == h5_lord and ad == h12_lord:
        score += 2
        why.append('5L+12L')
    if score < 4:
        return None
    return {
        'event': 'Lottery/gambling loss',
        'category': 'lottery_loss',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '5L+12L+Rahu (BPHS Ch.40)' }


def event_inheritance_land(chart, ds, tr, yogas, age):
    '''8H+4H ancestral land.'''
    if age < 25 or age > 85:
        return None
    lagna_idx = chart['lagna_idx']
    h4_lord = _lord(lagna_idx, 4)
    h8_lord = _lord(lagna_idx, 8)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h8_lord and ad == h4_lord:
        score += 4
        why.append('8L+4L land inheritance')
    if md == h4_lord and ad == 'Jupiter':
        score += 2
        why.append('4L+Jupiter')
    if score < 4:
        return None
    return {
        'event': 'Inheritance of ancestral land',
        'category': 'inheritance_land',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '4L+8L+Jupiter (BPHS Ch.23)' }


def event_insurance_claim(chart, ds, tr, yogas, age):
    '''8H+Saturn settlement.'''
    if age < 22:
        return None
    lagna_idx = chart['lagna_idx']
    h8_lord = _lord(lagna_idx, 8)
    h11_lord = _lord(lagna_idx, 11)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h8_lord and ad == h11_lord:
        score += 3
        why.append('8L+11L payout')
    if md == 'Saturn' and ad == h8_lord:
        score += 2
        why.append('Saturn+8L')
    if score < 4:
        return None
    return {
        'event': 'Insurance claim/settlement',
        'category': 'insurance_claim',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '8L+11L+Saturn (BPHS Ch.36)' }


def event_business_expansion(chart, ds, tr, yogas, age):
    '''10H+11H scale.'''
    if age < 25 or age > 70:
        return None
    lagna_idx = chart['lagna_idx']
    h10_lord = _lord(lagna_idx, 10)
    h11_lord = _lord(lagna_idx, 11)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h11_lord and ad == h10_lord:
        score += 4
        why.append('11L+10L gains-driven expansion')
    if md == h10_lord and ad == 'Jupiter':
        score += 3
        why.append('10L+Jupiter scale-up')
    if score < 4:
        return None
    return {
        'event': 'Business expansion',
        'category': 'business_expansion',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '10L+11L+Jupiter (BPHS Ch.25)' }


def event_business_closure(chart, ds, tr, yogas, age):
    '''10L+12L closure.'''
    if age < 25:
        return None
    lagna_idx = chart['lagna_idx']
    h10_lord = _lord(lagna_idx, 10)
    h12_lord = _lord(lagna_idx, 12)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h12_lord and ad == h10_lord:
        score += 4
        why.append('12L+10L closure')
    if md == 'Ketu' and ad == h10_lord:
        score += 2
        why.append('Ketu+10L exit')
    if score < 4:
        return None
    return {
        'event': 'Business closure/shutdown',
        'category': 'business_closure',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '10L+12L+Ketu (BPHS Ch.40)' }


def event_income_breakthrough(chart, ds, tr, yogas, age):
    '''2L+11L.'''
    if age < 18 or age > 75:
        return None
    lagna_idx = chart['lagna_idx']
    h2_lord = _lord(lagna_idx, 2)
    h11_lord = _lord(lagna_idx, 11)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h2_lord and ad == h11_lord:
        score += 4
        why.append('2L+11L income leap')
    if md == 'Jupiter' and ad in (h2_lord, h11_lord):
        score += 2
        why.append('Jupiter+wealth-house')
    if score < 4:
        return None
    return {
        'event': 'Income breakthrough',
        'category': 'income_breakthrough',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '2L+11L+Jupiter (Phaladeepika Ch.14)' }


def event_salary_raise(chart, ds, tr, yogas, age):
    '''10L+2L.'''
    if age < 22 or age > 70:
        return None
    lagna_idx = chart['lagna_idx']
    h2_lord = _lord(lagna_idx, 2)
    h10_lord = _lord(lagna_idx, 10)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h10_lord and ad == h2_lord:
        score += 3
        why.append('10L+2L salary up')
    if md == 'Jupiter' and ad == h10_lord:
        score += 2
        why.append('Jupiter+10L')
    if score < 3:
        return None
    return {
        'event': 'Salary raise/pay hike',
        'category': 'salary_raise',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '10L+2L (BPHS Ch.25)' }


def event_salary_cut(chart, ds, tr, yogas, age):
    '''10L+12L.'''
    if age < 22:
        return None
    lagna_idx = chart['lagna_idx']
    h10_lord = _lord(lagna_idx, 10)
    h12_lord = _lord(lagna_idx, 12)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h10_lord and ad == h12_lord:
        score += 3
        why.append('10L+12L pay cut')
    if md == 'Saturn' and ad == h10_lord:
        score += 2
        why.append('Saturn+10L')
    if score < 4:
        return None
    return {
        'event': 'Salary cut/pay reduction',
        'category': 'salary_cut',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '10L+12L+Saturn (BPHS Ch.40)' }


def event_loan_approval(chart, ds, tr, yogas, age):
    '''6L+Venus.'''
    if age < 22 or age > 75:
        return None
    lagna_idx = chart['lagna_idx']
    h6_lord = _lord(lagna_idx, 6)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h6_lord and ad in ('Venus', 'Jupiter'):
        score += 3
        why.append(f'''6L+{ad} loan approved''')
    if score < 3:
        return None
    return {
        'event': 'Loan/credit approval',
        'category': 'loan_approval',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '6L+Venus+Jupiter (Phaladeepika)' }


def event_loan_default(chart, ds, tr, yogas, age):
    '''6L+Saturn.'''
    if age < 22:
        return None
    lagna_idx = chart['lagna_idx']
    h6_lord = _lord(lagna_idx, 6)
    h12_lord = _lord(lagna_idx, 12)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h6_lord and ad in ('Saturn', 'Ketu'):
        score += 3
        why.append(f'''6L+{ad} default''')
    if md == h12_lord and ad == h6_lord:
        score += 3
        why.append('12L+6L debt cascade')
    if score < 4:
        return None
    return {
        'event': 'Loan default/debt crisis',
        'category': 'loan_default',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '6L+12L+Saturn (BPHS Ch.40)' }


def event_debt_freedom(chart, ds, tr, yogas, age):
    '''Jupiter+2L+11L.'''
    if age < 25:
        return None
    lagna_idx = chart['lagna_idx']
    h2_lord = _lord(lagna_idx, 2)
    h11_lord = _lord(lagna_idx, 11)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Jupiter' and ad in (h2_lord, h11_lord):
        score += 3
        why.append('Jupiter+wealth-house debt cleared')
    if score < 3:
        return None
    return {
        'event': 'Debt freedom/loans paid off',
        'category': 'debt_freedom',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': 'Jupiter+2L+11L (Saravali)' }


def event_franchise_open(chart, ds, tr, yogas, age):
    '''10L+11L+Rahu.'''
    if age < 28 or age > 65:
        return None
    lagna_idx = chart['lagna_idx']
    h10_lord = _lord(lagna_idx, 10)
    h11_lord = _lord(lagna_idx, 11)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Rahu' and ad in (h10_lord, h11_lord):
        score += 4
        why.append(f'''Rahu+{ad} franchise scale''')
    if score < 4:
        return None
    return {
        'event': 'Franchise/chain business open',
        'category': 'franchise',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '10L+11L+Rahu (modern)' }


def event_patent_grant(chart, ds, tr, yogas, age):
    '''5H+11H+Mercury.'''
    if age < 25:
        return None
    lagna_idx = chart['lagna_idx']
    h5_lord = _lord(lagna_idx, 5)
    h11_lord = _lord(lagna_idx, 11)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h5_lord and ad == 'Mercury':
        score += 3
        why.append('5L+Mercury IP')
    if md == 'Mercury' and ad == h11_lord:
        score += 2
        why.append('Mercury+11L')
    if score < 3:
        return None
    return {
        'event': 'Patent/IP/copyright grant',
        'category': 'patent',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '5L+11L+Mercury (modern)' }


def event_royalty_payment(chart, ds, tr, yogas, age):
    '''11L+5L+Mercury.'''
    if age < 22:
        return None
    lagna_idx = chart['lagna_idx']
    h5_lord = _lord(lagna_idx, 5)
    h11_lord = _lord(lagna_idx, 11)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h11_lord and ad == h5_lord:
        score += 3
        why.append('11L+5L royalty')
    if md == 'Mercury' and ad == h11_lord:
        score += 2
        why.append('Mercury+11L')
    if score < 4:
        return None
    return {
        'event': 'Royalty/recurring IP income',
        'category': 'royalty',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '5L+11L+Mercury (modern)' }


def event_sponsorship_deal(chart, ds, tr, yogas, age):
    '''11H+Venus.'''
    if age < 18:
        return None
    lagna_idx = chart['lagna_idx']
    h11_lord = _lord(lagna_idx, 11)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Venus' and ad == h11_lord:
        score += 3
        why.append('Venus+11L sponsor')
    if md == h11_lord and ad == 'Venus':
        score += 2
        why.append('11L+Venus')
    if score < 3:
        return None
    return {
        'event': 'Sponsorship deal',
        'category': 'sponsorship',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '11L+Venus (modern)' }


def event_subscriber_milestone(chart, ds, tr, yogas, age):
    '''11H+Rahu.'''
    if age < 16:
        return None
    lagna_idx = chart['lagna_idx']
    h11_lord = _lord(lagna_idx, 11)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Rahu' and ad == h11_lord:
        score += 3
        why.append('Rahu+11L viral following')
    if md == h11_lord and ad == 'Rahu':
        score += 2
        why.append('11L+Rahu')
    if score < 3:
        return None
    return {
        'event': 'Subscriber/follower milestone',
        'category': 'subscriber_milestone',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '11L+Rahu (modern)' }


def event_stock_crash_hit(chart, ds, tr, yogas, age):
    '''Saturn over 5L.'''
    pass
# WARNING: Decompyle incomplete


def event_crypto_gain(chart, ds, tr, yogas, age):
    '''Rahu+5H+11H modern.'''
    if age < 18:
        return None
    lagna_idx = chart['lagna_idx']
    h5_lord = _lord(lagna_idx, 5)
    h11_lord = _lord(lagna_idx, 11)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Rahu' and ad in (h5_lord, h11_lord):
        score += 3
        why.append(f'''Rahu+{ad} crypto/Defi gain''')
    if score < 3:
        return None
    return {
        'event': 'Crypto/Defi/digital asset gain',
        'category': 'crypto_gain',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': 'Rahu+5L+11L (modern)' }


def event_crypto_loss(chart, ds, tr, yogas, age):
    '''Rahu+Ketu+5H crypto loss.'''
    if age < 18:
        return None
    lagna_idx = chart['lagna_idx']
    h5_lord = _lord(lagna_idx, 5)
    h12_lord = _lord(lagna_idx, 12)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Rahu' and ad == h12_lord:
        score += 3
        why.append('Rahu+12L crypto loss')
    if md == 'Ketu' and ad == h5_lord:
        score += 2
        why.append('Ketu+5L sudden detachment')
    if score < 3:
        return None
    return {
        'event': 'Crypto/Defi loss',
        'category': 'crypto_loss',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': 'Rahu+Ketu+5L+12L (modern)' }


def event_bonus_windfall(chart, ds, tr, yogas, age):
    '''11H+Jupiter.'''
    if age < 22 or age > 70:
        return None
    lagna_idx = chart['lagna_idx']
    h11_lord = _lord(lagna_idx, 11)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Jupiter' and ad == h11_lord:
        score += 3
        why.append('Jupiter+11L bonus')
    if md == h11_lord and ad == 'Jupiter':
        score += 2
        why.append('11L+Jupiter')
    if score < 3:
        return None
    return {
        'event': 'Bonus/windfall',
        'category': 'bonus',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '11L+Jupiter (Phaladeepika)' }


def event_tax_refund(chart, ds, tr, yogas, age):
    '''2L+Mercury favorable.'''
    if age < 25:
        return None
    lagna_idx = chart['lagna_idx']
    h2_lord = _lord(lagna_idx, 2)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Mercury' and ad == h2_lord:
        score += 3
        why.append('Mercury+2L refund')
    if score < 3:
        return None
    return {
        'event': 'Tax refund/government payment',
        'category': 'tax_refund',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '2L+Mercury (BPHS Ch.6)' }


def event_property_loss(chart, ds, tr, yogas, age):
    '''4H+12H.'''
    if age < 22:
        return None
    lagna_idx = chart['lagna_idx']
    h4_lord = _lord(lagna_idx, 4)
    h12_lord = _lord(lagna_idx, 12)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h12_lord and ad == h4_lord:
        score += 4
        why.append('12L+4L property loss')
    if md == 'Saturn' and ad == h4_lord:
        score += 2
        why.append('Saturn+4L')
    if score < 4:
        return None
    return {
        'event': 'Property loss/forced sale',
        'category': 'property_loss',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '4L+12L+Saturn (BPHS Ch.40)' }


def event_land_acquisition(chart, ds, tr, yogas, age):
    '''4H+11H.'''
    if age < 25 or age > 75:
        return None
    lagna_idx = chart['lagna_idx']
    h4_lord = _lord(lagna_idx, 4)
    h11_lord = _lord(lagna_idx, 11)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h4_lord and ad == h11_lord:
        score += 4
        why.append('4L+11L land acquisition')
    if md == 'Jupiter' and ad == h4_lord:
        score += 2
        why.append('Jupiter+4L')
    if score < 4:
        return None
    return {
        'event': 'Land acquisition',
        'category': 'land_acquisition',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '4L+11L+Jupiter (BPHS Ch.23)' }


def event_plot_sale(chart, ds, tr, yogas, age):
    '''4L+2L.'''
    if age < 25:
        return None
    lagna_idx = chart['lagna_idx']
    h2_lord = _lord(lagna_idx, 2)
    h4_lord = _lord(lagna_idx, 4)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h4_lord and ad == h2_lord:
        score += 3
        why.append('4L+2L property→cash')
    if score < 3:
        return None
    return {
        'event': 'Plot/property sale',
        'category': 'plot_sale',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '2L+4L (BPHS Ch.23)' }


def event_mortgage_finalize(chart, ds, tr, yogas, age):
    '''6H+Mercury.'''
    if age < 22:
        return None
    lagna_idx = chart['lagna_idx']
    h6_lord = _lord(lagna_idx, 6)
    h2_lord = _lord(lagna_idx, 2)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Mercury' and ad in (h6_lord, h2_lord):
        score += 3
        why.append(f'''Mercury+{ad} paperwork''')
    if score < 3:
        return None
    return {
        'event': 'Mortgage finalization/closing',
        'category': 'mortgage',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '2L+6L+Mercury (Phaladeepika)' }


def event_ancestral_inheritance(chart, ds, tr, yogas, age):
    '''4H+8H+Jupiter.'''
    if age < 30:
        return None
    lagna_idx = chart['lagna_idx']
    h4_lord = _lord(lagna_idx, 4)
    h8_lord = _lord(lagna_idx, 8)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Jupiter' and ad in (h4_lord, h8_lord):
        score += 4
        why.append(f'''Jupiter+{ad} ancestral wealth''')
    if md == h8_lord and ad == 'Jupiter':
        score += 3
        why.append('8L+Jupiter')
    if score < 4:
        return None
    return {
        'event': 'Ancestral inheritance/family fortune',
        'category': 'ancestral_inheritance',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '4L+8L+Jupiter (BPHS Ch.36)' }


def event_fortune_loss(chart, ds, tr, yogas, age):
    '''9H+12H bad-luck.'''
    if age < 25:
        return None
    lagna_idx = chart['lagna_idx']
    h9_lord = _lord(lagna_idx, 9)
    h12_lord = _lord(lagna_idx, 12)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h12_lord and ad == h9_lord:
        score += 4
        why.append('12L+9L fortune drains')
    if md == 'Ketu' and ad == h9_lord:
        score += 2
        why.append('Ketu+9L dharma loss')
    if score < 4:
        return None
    return {
        'event': 'Fortune loss/dharma test',
        'category': 'fortune_loss',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '9L+12L+Ketu (BPHS Ch.32)' }


def event_friend_acquisition(chart, ds, tr, yogas, age):
    '''11H new friends — Venus/Jupiter+11L.'''
    if age < 5:
        return None
    lagna_idx = chart['lagna_idx']
    h11_lord = _lord(lagna_idx, 11)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h11_lord and ad in ('Venus', 'Jupiter', 'Mercury'):
        score += 3
        why.append(f'''11L+{ad} new friends''')
    if score < 3:
        return None
    return {
        'event': 'New friend group/network expansion',
        'category': 'friend_gain',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '11L+Venus/Jupiter (BPHS Ch.6)' }


def event_betrayal_friend(chart, ds, tr, yogas, age):
    '''11L+12L+Ketu betrayal.'''
    if age < 18:
        return None
    lagna_idx = chart['lagna_idx']
    h11_lord = _lord(lagna_idx, 11)
    h12_lord = _lord(lagna_idx, 12)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Ketu' and ad == h11_lord:
        score += 3
        why.append('Ketu+11L betrayal')
    if md == h12_lord and ad == h11_lord:
        score += 2
        why.append('12L+11L friend loss')
    if score < 3:
        return None
    return {
        'event': 'Friend betrayal/network shock',
        'category': 'betrayal',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '11L+12L+Ketu (BPHS Ch.45)' }


def event_elder_sibling_birth(chart, ds, tr, yogas, age):
    '''11H elder sibling.'''
    if age != 0:
        return None
    pos = chart['positions']
    score = 0
    why = []
    if _h(pos, 'Jupiter') in (11, 3):
        score += 2
        why.append('Jupiter in 11H/3H')
    if score < 2:
        return None
    return {
        'event': 'Elder sibling birth (or natal indication)',
        'category': 'elder_sibling',
        'severity': min(5, score),
        'yoga': None,
        'why': why,
        'source': '11H+Jupiter (BPHS Ch.13)' }


def event_elder_sibling_marriage(chart, ds, tr, yogas, age):
    '''11L+Venus.'''
    if age < 10:
        return None
    lagna_idx = chart['lagna_idx']
    h11_lord = _lord(lagna_idx, 11)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h11_lord and ad == 'Venus':
        score += 3
        why.append('11L+Venus elder-sibling wedding')
    if score < 3:
        return None
    return {
        'event': 'Elder sibling marriage',
        'category': 'elder_sibling_marriage',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '11L+Venus (BPHS Ch.13)' }


def event_elder_sibling_death(chart, ds, tr, yogas, age):
    '''11L+8L.'''
    if age < 18:
        return None
    lagna_idx = chart['lagna_idx']
    h11_lord = _lord(lagna_idx, 11)
    h6_lord = _lord(lagna_idx, 6)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h6_lord and ad in ('Saturn', 'Mars', 'Ketu'):
        score += 3
        why.append(f'''6L(8 from 11)+{ad}''')
    if score < 4:
        return None
    return {
        'event': 'Elder sibling death',
        'category': 'elder_sibling_death',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '6L+malefic (BPHS Ch.45)' }


def event_father_in_law_event(chart, ds, tr, yogas, age):
    '''7H+9H+11H father-in-law (9th from 7th = 3H).'''
    if age < 20:
        return None
    lagna_idx = chart['lagna_idx']
    h7_lord = _lord(lagna_idx, 7)
    h3_lord = _lord(lagna_idx, 3)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h3_lord and ad in ('Sun', 'Saturn'):
        score += 3
        why.append(f'''3L(9 from 7)+{ad}''')
    if md == h7_lord and ad == 'Sun':
        score += 2
        why.append('7L+Sun')
    if score < 4:
        return None
    return {
        'event': 'Father-in-law event (illness/death/career)',
        'category': 'father_in_law',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '7L+3L (Phaladeepika)' }


def event_mother_in_law_event(chart, ds, tr, yogas, age):
    '''7H+4H mother-in-law (4th from 7th = 10H).'''
    if age < 20:
        return None
    lagna_idx = chart['lagna_idx']
    h7_lord = _lord(lagna_idx, 7)
    h10_lord = _lord(lagna_idx, 10)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h10_lord and ad in ('Moon', 'Saturn'):
        score += 3
        why.append(f'''10L(4 from 7)+{ad}''')
    if md == h7_lord and ad == 'Moon':
        score += 2
        why.append('7L+Moon')
    if score < 4:
        return None
    return {
        'event': 'Mother-in-law event',
        'category': 'mother_in_law',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '7L+10L (Phaladeepika)' }


def event_uncle_maternal_event(chart, ds, tr, yogas, age):
    '''4H+3H (3rd from 4H = 6H) — maternal uncle/aunt.'''
    if age < 5:
        return None
    lagna_idx = chart['lagna_idx']
    h4_lord = _lord(lagna_idx, 4)
    h6_lord = _lord(lagna_idx, 6)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h6_lord and ad == h4_lord:
        score += 3
        why.append('6L(3 from 4)+4L maternal uncle')
    if score < 3:
        return None
    return {
        'event': 'Maternal uncle/aunt event',
        'category': 'maternal_uncle',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '4L+6L (BPHS Ch.13)' }


def event_uncle_paternal_event(chart, ds, tr, yogas, age):
    '''9H+3H (3rd from 9H = 11H) — paternal uncle.'''
    if age < 5:
        return None
    lagna_idx = chart['lagna_idx']
    h9_lord = _lord(lagna_idx, 9)
    h11_lord = _lord(lagna_idx, 11)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h11_lord and ad == h9_lord:
        score += 3
        why.append('11L(3 from 9)+9L paternal uncle')
    if score < 3:
        return None
    return {
        'event': 'Paternal uncle event',
        'category': 'paternal_uncle',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '9L+11L (BPHS Ch.13)' }


def event_adoption(chart, ds, tr, yogas, age):
    '''5H+Rahu/Jupiter unconventional child path.'''
    if age < 22:
        return None
    lagna_idx = chart['lagna_idx']
    h5_lord = _lord(lagna_idx, 5)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Rahu' and ad == h5_lord:
        score += 3
        why.append('Rahu+5L unconventional child path')
    if md == 'Jupiter' and ad == 'Rahu':
        score += 2
        why.append('Jupiter+Rahu blessed-adoption')
    if score < 4:
        return None
    return {
        'event': 'Adoption/foster parenting',
        'category': 'adoption',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '5L+Rahu+Jupiter (Saravali)' }


def event_engagement_break(chart, ds, tr, yogas, age):
    '''7L+Saturn affliction.'''
    if age < 16 or age > 60:
        return None
    lagna_idx = chart['lagna_idx']
    h7_lord = _lord(lagna_idx, 7)
    h12_lord = _lord(lagna_idx, 12)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Saturn' and ad == h7_lord:
        score += 3
        why.append('Saturn+7L engagement break')
    if md == h12_lord and ad == 'Venus':
        score += 2
        why.append('12L+Venus loss of fiancé')
    if score < 4:
        return None
    return {
        'event': 'Engagement break / called-off wedding',
        'category': 'engagement_break',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '7L+Saturn+12L (BPHS Ch.80)' }


def event_divorce(chart, ds, tr, yogas, age):
    '''7L+12L break.'''
    if age < 22 or age > 75:
        return None
    lagna_idx = chart['lagna_idx']
    h7_lord = _lord(lagna_idx, 7)
    h12_lord = _lord(lagna_idx, 12)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h12_lord and ad == h7_lord:
        score += 4
        why.append('12L+7L divorce')
    if md == 'Saturn' and ad == h7_lord and age >= 30:
        score += 2
        why.append('Saturn+7L marriage stress')
    if score < 4:
        return None
    return {
        'event': 'Divorce/legal marriage dissolution',
        'category': 'divorce',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '7L+12L (BPHS Ch.80)' }


def event_widowhood_remarriage(chart, ds, tr, yogas, age):
    '''Widowhood + Venus second activation.'''
    if age < 35:
        return None
    lagna_idx = chart['lagna_idx']
    h7_lord = _lord(lagna_idx, 7)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Venus' and ad == h7_lord and age >= 40:
        score += 3
        why.append('Venus+7L post-widowhood remarriage')
    if score < 3:
        return None
    return {
        'event': 'Remarriage after widowhood',
        'category': 'widowhood_remarriage',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '7L second activation (BPHS)' }


def event_extramarital_affair(chart, ds, tr, yogas, age):
    '''5H+7H+Rahu.'''
    if age < 22 or age > 70:
        return None
    lagna_idx = chart['lagna_idx']
    h5_lord = _lord(lagna_idx, 5)
    h7_lord = _lord(lagna_idx, 7)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Rahu' and ad in (h5_lord, h7_lord):
        score += 3
        why.append(f'''Rahu+{ad} affair''')
    if md == 'Venus' and ad == h5_lord:
        score += 1
        why.append('Venus+5L secret love')
    if score < 4:
        return None
    return {
        'event': 'Extramarital affair / scandal',
        'category': 'affair',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '5L+7L+Rahu (BPHS Ch.13)' }


def event_grandchild_marriage(chart, ds, tr, yogas, age):
    """9H+5H grandchild's wedding."""
    if age < 55:
        return None
    lagna_idx = chart['lagna_idx']
    h9_lord = _lord(lagna_idx, 9)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h9_lord and ad == 'Venus':
        score += 3
        why.append('9L+Venus grandchild wedding')
    if score < 3:
        return None
    return {
        'event': 'Grandchild marriage',
        'category': 'grandchild_marriage',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '9L+Venus (BPHS Ch.80)' }


def event_great_grandparent_death(chart, ds, tr, yogas, age):
    """5H (5 from 9 = 13 = 1 from grandfather's POV)."""
    if age < 5:
        return None
    lagna_idx = chart['lagna_idx']
    h5_lord = _lord(lagna_idx, 5)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h5_lord and ad in ('Saturn', 'Ketu'):
        score += 2
        why.append(f'''5L+{ad}''')
    if score < 2:
        return None
    return {
        'event': 'Great-grandparent death',
        'category': 'great_grandparent',
        'severity': min(5, score),
        'yoga': None,
        'why': why,
        'source': 'Extended lineage (BPHS Ch.45)' }


def event_pet_death(chart, ds, tr, yogas, age):
    '''6L+8L pet loss.'''
    if age < 5:
        return None
    lagna_idx = chart['lagna_idx']
    h6_lord = _lord(lagna_idx, 6)
    h8_lord = _lord(lagna_idx, 8)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h8_lord and ad == h6_lord:
        score += 3
        why.append('8L+6L pet loss')
    if md == 'Ketu' and ad in (h6_lord, h8_lord):
        score += 2
        why.append(f'''Ketu+{ad}''')
    if score < 4:
        return None
    return {
        'event': 'Pet death/separation',
        'category': 'pet_death',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '6L+8L+Ketu (BPHS)' }


def event_loved_one_death(chart, ds, tr, yogas, age):
    '''Generic 8H+Maraka generic loss.'''
    if age < 15:
        return None
    lagna_idx = chart['lagna_idx']
    h8_lord = _lord(lagna_idx, 8)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h8_lord and ad in ('Saturn', 'Mars', 'Ketu'):
        score += 3
        why.append(f'''8L+{ad} loss''')
    if score < 4:
        return None
    return {
        'event': 'Death of close loved one (uncle/aunt/mentor)',
        'category': 'loved_one_death',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '8L+Maraka (BPHS Ch.45)' }


def event_distant_relative_death(chart, ds, tr, yogas, age):
    '''3H+8H distant family loss.'''
    if age < 15:
        return None
    lagna_idx = chart['lagna_idx']
    h3_lord = _lord(lagna_idx, 3)
    h8_lord = _lord(lagna_idx, 8)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h8_lord and ad == h3_lord:
        score += 2
        why.append('8L+3L distant relative')
    if score < 3:
        return None
    return {
        'event': 'Distant relative death',
        'category': 'distant_relative_death',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '3L+8L (BPHS Ch.13)' }


def event_neighbor_dispute(chart, ds, tr, yogas, age):
    '''3H+6H neighbor friction.'''
    if age < 18:
        return None
    lagna_idx = chart['lagna_idx']
    h3_lord = _lord(lagna_idx, 3)
    h6_lord = _lord(lagna_idx, 6)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h3_lord and ad == h6_lord:
        score += 3
        why.append('3L+6L neighbor dispute')
    if score < 3:
        return None
    return {
        'event': 'Neighbor/local dispute',
        'category': 'neighbor_dispute',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '3L+6L (BPHS Ch.13)' }


def event_business_partner_betrayal(chart, ds, tr, yogas, age):
    '''7L+12L.'''
    if age < 25:
        return None
    lagna_idx = chart['lagna_idx']
    h7_lord = _lord(lagna_idx, 7)
    h12_lord = _lord(lagna_idx, 12)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h12_lord and ad == h7_lord:
        score += 4
        why.append('12L+7L partner betrayal')
    if md == 'Rahu' and ad == h7_lord:
        score += 2
        why.append('Rahu+7L deception')
    if score < 4:
        return None
    return {
        'event': 'Business partner betrayal/fraud',
        'category': 'partner_betrayal',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '7L+12L+Rahu (BPHS Ch.13)' }


def event_business_partner_death(chart, ds, tr, yogas, age):
    '''7L+8L (2H from 7H = 8L for partner death).'''
    if age < 25:
        return None
    lagna_idx = chart['lagna_idx']
    h7_lord = _lord(lagna_idx, 7)
    h2_lord = _lord(lagna_idx, 2)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h2_lord and ad == h7_lord:
        score += 3
        why.append('2L(8 from 7)+7L partner death')
    if score < 4:
        return None
    return {
        'event': 'Business partner death',
        'category': 'partner_death',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '7L+2L (BPHS Ch.80)' }


def event_co_worker_event(chart, ds, tr, yogas, age):
    '''6H co-worker.'''
    if age < 18 or age > 65:
        return None
    lagna_idx = chart['lagna_idx']
    h6_lord = _lord(lagna_idx, 6)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h6_lord and ad in ('Saturn', 'Mercury'):
        score += 2
        why.append(f'''6L+{ad}''')
    if score < 2:
        return None
    return {
        'event': 'Co-worker/colleague significant event',
        'category': 'co_worker',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '6L (BPHS Ch.7)' }


def event_servant_event(chart, ds, tr, yogas, age):
    '''6H+Saturn — servant/employee hire/fire.'''
    if age < 25:
        return None
    lagna_idx = chart['lagna_idx']
    h6_lord = _lord(lagna_idx, 6)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h6_lord and ad == 'Saturn':
        score += 3
        why.append('6L+Saturn servant/employee')
    if score < 3:
        return None
    return {
        'event': 'Servant/household-staff event',
        'category': 'servant_event',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '6L+Saturn (BPHS Ch.13)' }


def event_landlord_dispute(chart, ds, tr, yogas, age):
    '''4H+6H landlord.'''
    if age < 20:
        return None
    lagna_idx = chart['lagna_idx']
    h4_lord = _lord(lagna_idx, 4)
    h6_lord = _lord(lagna_idx, 6)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h4_lord and ad == h6_lord:
        score += 3
        why.append('4L+6L landlord dispute')
    if score < 3:
        return None
    return {
        'event': 'Landlord/tenant dispute',
        'category': 'landlord_dispute',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '4L+6L (BPHS Ch.23)' }


def event_tenant_event(chart, ds, tr, yogas, age):
    '''4H+6H+11H — own rental income.'''
    if age < 25:
        return None
    lagna_idx = chart['lagna_idx']
    h4_lord = _lord(lagna_idx, 4)
    h11_lord = _lord(lagna_idx, 11)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h11_lord and ad == h4_lord:
        score += 3
        why.append('11L+4L rental income')
    if score < 3:
        return None
    return {
        'event': 'Tenant rental income/eviction',
        'category': 'tenant_event',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '4L+11L (BPHS Ch.23)' }


def event_uncle_aunt_event(chart, ds, tr, yogas, age):
    '''3H+11H general uncle/aunt.'''
    if age < 5:
        return None
    lagna_idx = chart['lagna_idx']
    h3_lord = _lord(lagna_idx, 3)
    h11_lord = _lord(lagna_idx, 11)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md in (h3_lord, h11_lord) and ad in ('Mercury', 'Jupiter'):
        score += 2
        why.append('3/11L+benefic')
    if score < 2:
        return None
    return {
        'event': 'Uncle/aunt event (general)',
        'category': 'uncle_aunt',
        'severity': min(5, score),
        'yoga': None,
        'why': why,
        'source': '3L+11L (BPHS Ch.13)' }


def event_cousin_event(chart, ds, tr, yogas, age):
    '''3H+11H cousin marriage/event.'''
    if age < 10:
        return None
    lagna_idx = chart['lagna_idx']
    h11_lord = _lord(lagna_idx, 11)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h11_lord and ad == 'Venus':
        score += 2
        why.append('11L+Venus cousin wedding')
    if score < 2:
        return None
    return {
        'event': 'Cousin event (marriage/birth/death)',
        'category': 'cousin',
        'severity': min(5, score),
        'yoga': None,
        'why': why,
        'source': '3L+11L (BPHS Ch.13)' }


def event_step_family_event(chart, ds, tr, yogas, age):
    '''2H+Rahu unconventional family.'''
    if age < 5:
        return None
    pos = chart['positions']
    lagna_idx = chart['lagna_idx']
    h2_lord = _lord(lagna_idx, 2)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Rahu' and ad == h2_lord:
        score += 3
        why.append('Rahu+2L step-family')
    if score < 3:
        return None
    return {
        'event': 'Step-family event (parent remarriage etc.)',
        'category': 'step_family',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '2L+Rahu (BPHS Ch.13)' }


def event_first_job(chart, ds, tr, yogas, age):
    '''10L initial activation.'''
    if age < 16 or age > 35:
        return None
    lagna_idx = chart['lagna_idx']
    h10_lord = _lord(lagna_idx, 10)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h10_lord and age < 30:
        score += 3
        why.append('10L MD young — first job')
    if ad == h10_lord and age < 25:
        score += 2
        why.append('10L AD adolescent')
    if score < 3:
        return None
    return {
        'event': 'First job / career launch',
        'category': 'first_job',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '10L initial (BPHS Ch.25)' }


def event_job_change(chart, ds, tr, yogas, age):
    '''10L MD shift + Mercury.'''
    if age < 22 or age > 65:
        return None
    lagna_idx = chart['lagna_idx']
    h10_lord = _lord(lagna_idx, 10)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Mercury' and ad == h10_lord:
        score += 3
        why.append('Mercury+10L job switch')
    if md == h10_lord and ad == 'Rahu':
        score += 2
        why.append('10L+Rahu unconventional switch')
    if score < 3:
        return None
    return {
        'event': 'Job change / employer switch',
        'category': 'job_change',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '10L+Mercury (BPHS Ch.25)' }


def event_profession_switch(chart, ds, tr, yogas, age):
    '''10L+9L deep career pivot.'''
    if age < 25:
        return None
    lagna_idx = chart['lagna_idx']
    h9_lord = _lord(lagna_idx, 9)
    h10_lord = _lord(lagna_idx, 10)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h9_lord and ad == h10_lord:
        score += 4
        why.append('9L+10L profession pivot')
    if md == 'Rahu' and ad == h10_lord:
        score += 2
        why.append('Rahu+10L radical switch')
    if score < 4:
        return None
    return {
        'event': 'Profession switch (entire career pivot)',
        'category': 'profession_switch',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '9L+10L+Rahu (BPHS Ch.25)' }


def event_promotion_executive(chart, ds, tr, yogas, age):
    '''10L+11L+Sun strong.'''
    if age < 35:
        return None
    lagna_idx = chart['lagna_idx']
    h10_lord = _lord(lagna_idx, 10)
    h11_lord = _lord(lagna_idx, 11)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Sun' and ad in (h10_lord, h11_lord):
        score += 3
        why.append(f'''Sun+{ad} executive''')
    if md == h11_lord and ad == 'Sun':
        score += 2
        why.append('11L+Sun')
    if score < 4:
        return None
    return {
        'event': 'Promotion to executive / VP / SVP',
        'category': 'promotion_executive',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '10L+11L+Sun (Saravali)' }


def event_board_role(chart, ds, tr, yogas, age):
    '''10L+11L+Jupiter board appointment.'''
    if age < 40:
        return None
    lagna_idx = chart['lagna_idx']
    h10_lord = _lord(lagna_idx, 10)
    h11_lord = _lord(lagna_idx, 11)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Jupiter' and ad in (h10_lord, h11_lord):
        score += 4
        why.append(f'''Jupiter+{ad} board''')
    if score < 4:
        return None
    return {
        'event': 'Board / advisory appointment',
        'category': 'board_role',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '10L+11L+Jupiter (BPHS Ch.25)' }


def event_founder_role(chart, ds, tr, yogas, age):
    '''10L+5L creative-founder.'''
    if age < 25 or age > 65:
        return None
    lagna_idx = chart['lagna_idx']
    h5_lord = _lord(lagna_idx, 5)
    h10_lord = _lord(lagna_idx, 10)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h5_lord and ad == h10_lord:
        score += 4
        why.append('5L+10L creative founder')
    if md == 'Mercury' and ad == h10_lord:
        score += 2
        why.append('Mercury+10L startup')
    if score < 4:
        return None
    return {
        'event': 'Founder / startup CEO role',
        'category': 'founder_role',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '5L+10L+Mercury (BPHS Ch.25)' }


def event_ceo_role(chart, ds, tr, yogas, age):
    '''10L+Sun+Saturn.'''
    if age < 40:
        return None
    lagna_idx = chart['lagna_idx']
    h10_lord = _lord(lagna_idx, 10)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h10_lord and ad == 'Sun':
        score += 4
        why.append('10L+Sun CEO')
    if md == 'Saturn' and ad == h10_lord and age >= 50:
        score += 2
        why.append('Saturn+10L mature-CEO')
    if score < 4:
        return None
    return {
        'event': 'CEO appointment / chief executive role',
        'category': 'ceo_role',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '10L+Sun+Saturn (Saravali)' }


def event_consultant_phase(chart, ds, tr, yogas, age):
    '''10L+Mercury consultant phase.'''
    if age < 30:
        return None
    lagna_idx = chart['lagna_idx']
    h10_lord = _lord(lagna_idx, 10)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Mercury' and ad == h10_lord:
        score += 3
        why.append('Mercury+10L consulting')
    if score < 3:
        return None
    return {
        'event': 'Consultant / freelance phase begins',
        'category': 'consultant',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': 'Mercury+10L (BPHS Ch.25)' }


def event_corporate_scandal(chart, ds, tr, yogas, age):
    '''10H+12H+Rahu scandal.'''
    if age < 30:
        return None
    lagna_idx = chart['lagna_idx']
    h10_lord = _lord(lagna_idx, 10)
    h12_lord = _lord(lagna_idx, 12)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Rahu' and ad == h10_lord:
        score += 4
        why.append('Rahu+10L scandal/fraud')
    if md == h12_lord and ad == h10_lord:
        score += 2
        why.append('12L+10L career loss')
    if score < 4:
        return None
    return {
        'event': 'Corporate scandal / fraud expose',
        'category': 'corporate_scandal',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '10L+12L+Rahu (BPHS Ch.40)' }


def event_fame_peak(chart, ds, tr, yogas, age):
    '''1H+10H+Moon fame peak.'''
    if age < 20:
        return None
    pos = chart['positions']
    asc_lord = chart.get('lagna_lord')
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Moon' and ad == asc_lord:
        score += 3
        why.append('Moon+lagna lord fame')
    if md == 'Sun' and _h(pos, 'Sun') in (1, 10):
        score += 2
        why.append('Sun MD+kendra')
    if md == 'Jupiter' and ad == 'Moon':
        score += 2
        why.append('Jupiter+Moon mass appeal')
    if score < 4:
        return None
    return {
        'event': 'Fame peak / mass public appeal',
        'category': 'fame_peak',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '1H+10H+Moon (BPHS Ch.4)' }


def event_fame_loss(chart, ds, tr, yogas, age):
    '''10H+12H+Ketu fame loss.'''
    if age < 25:
        return None
    lagna_idx = chart['lagna_idx']
    h10_lord = _lord(lagna_idx, 10)
    h12_lord = _lord(lagna_idx, 12)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Ketu' and ad == h10_lord:
        score += 3
        why.append('Ketu+10L fame detachment')
    if md == h12_lord and ad == h10_lord:
        score += 2
        why.append('12L+10L scandal loss')
    if score < 4:
        return None
    return {
        'event': 'Fame loss / scandal / cancellation',
        'category': 'fame_loss',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '10L+12L+Ketu (BPHS Ch.40)' }


def event_government_position(chart, ds, tr, yogas, age):
    '''10H+Sun+Saturn.'''
    if age < 25:
        return None
    lagna_idx = chart['lagna_idx']
    h10_lord = _lord(lagna_idx, 10)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Sun' and ad == h10_lord:
        score += 4
        why.append('Sun+10L govt position')
    if md == 'Saturn' and ad == h10_lord and age >= 35:
        score += 2
        why.append('Saturn+10L bureaucratic')
    if score < 4:
        return None
    return {
        'event': 'Government position / public office',
        'category': 'government_position',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '10L+Sun+Saturn (Saravali)' }


def event_diplomatic_role(chart, ds, tr, yogas, age):
    '''7H+9H ambassador/diplomat.'''
    if age < 30:
        return None
    lagna_idx = chart['lagna_idx']
    h7_lord = _lord(lagna_idx, 7)
    h9_lord = _lord(lagna_idx, 9)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h9_lord and ad == h7_lord:
        score += 4
        why.append('9L+7L diplomatic posting')
    if score < 4:
        return None
    return {
        'event': 'Diplomatic / ambassador role',
        'category': 'diplomatic',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '7L+9L (BPHS Ch.13)' }


def event_military_role(chart, ds, tr, yogas, age):
    '''3H+6H+Mars military/police.'''
    if age < 18 or age > 60:
        return None
    pos = chart['positions']
    lagna_idx = chart['lagna_idx']
    h6_lord = _lord(lagna_idx, 6)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Mars' and _h(pos, 'Mars') in (3, 6, 10):
        score += 4
        why.append('Mars+warrior houses')
    if md == h6_lord and ad == 'Mars':
        score += 2
        why.append('6L+Mars service')
    if score < 4:
        return None
    return {
        'event': 'Military / police / security career milestone',
        'category': 'military',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '3L+6L+Mars (Saravali)' }


def event_judicial_role(chart, ds, tr, yogas, age):
    '''9H+Jupiter judge/lawyer.'''
    if age < 28:
        return None
    lagna_idx = chart['lagna_idx']
    h9_lord = _lord(lagna_idx, 9)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Jupiter' and ad == h9_lord:
        score += 4
        why.append('Jupiter+9L judicial')
    if score < 4:
        return None
    return {
        'event': 'Judicial / legal career milestone',
        'category': 'judicial',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '9L+Jupiter (BPHS Ch.32)' }


def event_teaching_role(chart, ds, tr, yogas, age):
    '''2H+5H+Jupiter teaching.'''
    if age < 22:
        return None
    lagna_idx = chart['lagna_idx']
    h5_lord = _lord(lagna_idx, 5)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Jupiter' and ad == h5_lord:
        score += 3
        why.append('Jupiter+5L teaching')
    if md == h5_lord and ad == 'Mercury':
        score += 2
        why.append('5L+Mercury instructor')
    if score < 3:
        return None
    return {
        'event': 'Teaching career / professor / mentor role',
        'category': 'teaching',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '5L+Jupiter (BPHS Ch.13)' }


def event_research_role(chart, ds, tr, yogas, age):
    '''8H+Mercury+Saturn research.'''
    if age < 25:
        return None
    lagna_idx = chart['lagna_idx']
    h8_lord = _lord(lagna_idx, 8)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h8_lord and ad in ('Mercury', 'Saturn'):
        score += 3
        why.append(f'''8L+{ad} research''')
    if md == 'Saturn' and ad == 'Mercury':
        score += 2
        why.append('Saturn+Mercury investigation')
    if score < 4:
        return None
    return {
        'event': 'Research / academic / investigation role',
        'category': 'research',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '8L+Mercury+Saturn (BPHS Ch.30)' }


def event_medical_career(chart, ds, tr, yogas, age):
    '''8H+Saturn+Sun medical.'''
    if age < 25:
        return None
    lagna_idx = chart['lagna_idx']
    h8_lord = _lord(lagna_idx, 8)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h8_lord and ad in ('Sun', 'Saturn', 'Mars'):
        score += 3
        why.append(f'''8L+{ad} medical''')
    if score < 3:
        return None
    return {
        'event': 'Medical / healing career milestone',
        'category': 'medical_career',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '8L+Sun (BPHS Ch.30)' }


def event_law_career(chart, ds, tr, yogas, age):
    '''9H+Jupiter+Mercury legal.'''
    if age < 25:
        return None
    lagna_idx = chart['lagna_idx']
    h9_lord = _lord(lagna_idx, 9)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Jupiter' and ad == 'Mercury':
        score += 3
        why.append('Jupiter+Mercury law')
    if md == h9_lord and ad == 'Mercury':
        score += 2
        why.append('9L+Mercury legal practice')
    if score < 3:
        return None
    return {
        'event': 'Law / advocate career milestone',
        'category': 'law_career',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '9L+Jupiter+Mercury (BPHS Ch.32)' }


def event_finance_career(chart, ds, tr, yogas, age):
    '''2H+11H+Mercury finance.'''
    if age < 22:
        return None
    lagna_idx = chart['lagna_idx']
    h2_lord = _lord(lagna_idx, 2)
    h11_lord = _lord(lagna_idx, 11)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Mercury' and ad in (h2_lord, h11_lord):
        score += 3
        why.append(f'''Mercury+{ad} finance''')
    if score < 3:
        return None
    return {
        'event': 'Finance / banking / trading career milestone',
        'category': 'finance_career',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '2L+11L+Mercury (BPHS Ch.13)' }


def event_tech_career(chart, ds, tr, yogas, age):
    '''Mercury+Rahu+11H tech.'''
    if age < 20:
        return None
    lagna_idx = chart['lagna_idx']
    h11_lord = _lord(lagna_idx, 11)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Rahu' and ad == 'Mercury':
        score += 3
        why.append('Rahu+Mercury tech')
    if md == 'Mercury' and ad == h11_lord:
        score += 2
        why.append('Mercury+11L modern career')
    if score < 3:
        return None
    return {
        'event': 'Tech / IT / digital career milestone',
        'category': 'tech_career',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': 'Mercury+Rahu+11L (modern)' }


def event_civil_service(chart, ds, tr, yogas, age):
    '''10H+Sun+Saturn civil service.'''
    if age < 22 or age > 65:
        return None
    lagna_idx = chart['lagna_idx']
    h10_lord = _lord(lagna_idx, 10)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Saturn' and ad == 'Sun' and age < 40:
        score += 3
        why.append('Saturn+Sun young civil service')
    if md == h10_lord and ad == 'Saturn':
        score += 2
        why.append('10L+Saturn bureaucratic')
    if score < 3:
        return None
    return {
        'event': 'Civil service / bureaucratic career',
        'category': 'civil_service',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '10L+Sun+Saturn (Saravali)' }


def event_singing_career(chart, ds, tr, yogas, age):
    '''2H+Venus singing.'''
    if age < 10:
        return None
    lagna_idx = chart['lagna_idx']
    h2_lord = _lord(lagna_idx, 2)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Venus' and ad == h2_lord:
        score += 3
        why.append('Venus+2L singing')
    if score < 3:
        return None
    return {
        'event': 'Singing career milestone',
        'category': 'singing_career',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '2L+Venus (BPHS Ch.13)' }


def event_dancing_career(chart, ds, tr, yogas, age):
    '''Venus+Moon dancing.'''
    if age < 8:
        return None
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Venus' and ad == 'Moon':
        score += 3
        why.append('Venus+Moon dance')
    if md == 'Moon' and ad == 'Venus':
        score += 2
        why.append('Moon+Venus expression')
    if score < 3:
        return None
    return {
        'event': 'Dance career milestone',
        'category': 'dancing',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': 'Venus+Moon (Saravali)' }


def event_acting_career(chart, ds, tr, yogas, age):
    '''5H+Venus+Rahu acting.'''
    if age < 8:
        return None
    lagna_idx = chart['lagna_idx']
    h5_lord = _lord(lagna_idx, 5)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Venus' and ad == h5_lord:
        score += 3
        why.append('Venus+5L acting')
    if md == 'Rahu' and ad == 'Venus':
        score += 2
        why.append('Rahu+Venus screen')
    if score < 3:
        return None
    return {
        'event': 'Acting / film / theatre milestone',
        'category': 'acting',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '5L+Venus+Rahu (Saravali)' }


def event_engineering_career(chart, ds, tr, yogas, age):
    '''Mercury+Saturn+Mars engineering.'''
    if age < 20:
        return None
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Mercury' and ad == 'Saturn':
        score += 3
        why.append('Mercury+Saturn engineering')
    if md == 'Mars' and ad == 'Mercury':
        score += 2
        why.append('Mars+Mercury technical')
    if score < 3:
        return None
    return {
        'event': 'Engineering / technical career milestone',
        'category': 'engineering',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': 'Mercury+Saturn+Mars (modern)' }


def event_pilgrimage(chart, ds, tr, yogas, age):
    '''9L+12L+Ketu pilgrimage.'''
    if age < 25:
        return None
    lagna_idx = chart['lagna_idx']
    h9_lord = _lord(lagna_idx, 9)
    h12_lord = _lord(lagna_idx, 12)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h9_lord and ad == 'Ketu':
        score += 3
        why.append('9L+Ketu pilgrimage')
    if md == 'Ketu' and ad == h12_lord:
        score += 2
        why.append('Ketu+12L sacred journey')
    if score < 3:
        return None
    return {
        'event': 'Pilgrimage to holy site',
        'category': 'pilgrimage',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '9L+12L+Ketu (Hora Sara Ch.25)' }


def event_guru_initiation(chart, ds, tr, yogas, age):
    '''5H+Jupiter+Ketu initiation.'''
    if age < 18:
        return None
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Jupiter' and ad == 'Ketu':
        score += 3
        why.append('Jupiter+Ketu initiation')
    if md == 'Ketu' and ad == 'Jupiter':
        score += 2
        why.append('Ketu+Jupiter guru')
    if score < 3:
        return None
    return {
        'event': 'Guru initiation / diksha received',
        'category': 'guru_initiation',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': 'Jupiter+Ketu (Hora Sara Ch.25)' }


def event_religious_conversion(chart, ds, tr, yogas, age):
    '''Jupiter MD shift or Rahu.'''
    if age < 15:
        return None
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Rahu' and ad == 'Jupiter':
        score += 3
        why.append('Rahu+Jupiter conversion')
    if md == 'Jupiter' and ad == 'Ketu':
        score += 2
        why.append('Jupiter+Ketu dharma-shift')
    if score < 3:
        return None
    return {
        'event': 'Religious conversion / faith change',
        'category': 'religious_conversion',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': 'Jupiter+Rahu+Ketu (Hora Sara)' }


def event_meditation_breakthrough(chart, ds, tr, yogas, age):
    '''12H+Ketu+Moon meditation depth.'''
    if age < 18:
        return None
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Ketu' and ad == 'Moon':
        score += 3
        why.append('Ketu+Moon meditative depth')
    if md == 'Moon' and ad == 'Ketu':
        score += 2
        why.append('Moon+Ketu psychic opening')
    if score < 3:
        return None
    return {
        'event': 'Meditation / sadhana breakthrough',
        'category': 'meditation',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '12L+Ketu+Moon (BPHS)' }


def event_kundalini_awakening(chart, ds, tr, yogas, age):
    '''Saturn+Ketu deep awakening.'''
    if age < 25:
        return None
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Saturn' and ad == 'Ketu':
        score += 4
        why.append('Saturn+Ketu kundalini')
    if score < 4:
        return None
    return {
        'event': 'Kundalini awakening / deep energetic shift',
        'category': 'kundalini',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': 'Saturn+Ketu (Tantra)' }


def event_psychic_experience(chart, ds, tr, yogas, age):
    '''Ketu+Rahu+Moon psychic event.'''
    if age < 10:
        return None
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Ketu' and ad == 'Rahu':
        score += 3
        why.append('Ketu+Rahu psychic axis')
    if md == 'Moon' and ad in ('Ketu', 'Rahu'):
        score += 2
        why.append(f'''Moon+{ad} psychic flash''')
    if score < 3:
        return None
    return {
        'event': 'Psychic / paranormal experience',
        'category': 'psychic_experience',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': 'Ketu+Rahu+Moon (BPHS)' }


def event_past_life_recall(chart, ds, tr, yogas, age):
    '''Ketu+12H past life surfacing.'''
    if age < 25:
        return None
    lagna_idx = chart['lagna_idx']
    h12_lord = _lord(lagna_idx, 12)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Ketu' and ad == h12_lord:
        score += 3
        why.append('Ketu+12L past-life')
    if score < 3:
        return None
    return {
        'event': 'Past-life recall / karmic memory surfacing',
        'category': 'past_life',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': 'Ketu+12L (Hora Sara)' }


def event_dream_significant(chart, ds, tr, yogas, age):
    '''Moon+Ketu+12H prophetic dream.'''
    if age < 12:
        return None
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Moon' and ad == 'Ketu':
        score += 3
        why.append('Moon+Ketu prophetic dream')
    if score < 3:
        return None
    return {
        'event': 'Significant prophetic dream / vision',
        'category': 'prophetic_dream',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': 'Moon+Ketu (Hora Sara)' }


def event_temple_visit_major(chart, ds, tr, yogas, age):
    '''9H+Jupiter major temple.'''
    if age < 16:
        return None
    lagna_idx = chart['lagna_idx']
    h9_lord = _lord(lagna_idx, 9)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Jupiter' and ad == h9_lord:
        score += 3
        why.append('Jupiter+9L major temple')
    if score < 3:
        return None
    return {
        'event': 'Major temple / shrine visit',
        'category': 'temple_visit',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '9L+Jupiter (Saravali)' }


def event_chant_completion(chart, ds, tr, yogas, age):
    '''5H+Jupiter mantra completion.'''
    if age < 18:
        return None
    lagna_idx = chart['lagna_idx']
    h5_lord = _lord(lagna_idx, 5)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Jupiter' and ad == h5_lord:
        score += 3
        why.append('Jupiter+5L chant completion')
    if score < 3:
        return None
    return {
        'event': 'Mantra/chant completion (anusthana fulfilled)',
        'category': 'chant_completion',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '5L+Jupiter (Saravali)' }


def event_mantra_initiation(chart, ds, tr, yogas, age):
    '''5H+Jupiter mantra received.'''
    if age < 16:
        return None
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Jupiter' and ad == 'Ketu':
        score += 3
        why.append('Jupiter+Ketu mantra received')
    if score < 3:
        return None
    return {
        'event': 'Mantra initiation / personal bija given',
        'category': 'mantra_initiation',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': 'Jupiter+Ketu (Hora Sara)' }


def event_yagna_performance(chart, ds, tr, yogas, age):
    '''9H+Jupiter+5H yagna/homa.'''
    if age < 22:
        return None
    lagna_idx = chart['lagna_idx']
    h9_lord = _lord(lagna_idx, 9)
    h5_lord = _lord(lagna_idx, 5)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Jupiter' and ad in (h5_lord, h9_lord):
        score += 3
        why.append(f'''Jupiter+{ad} yagna''')
    if score < 3:
        return None
    return {
        'event': 'Yagna / homa / fire ritual performance',
        'category': 'yagna',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '9L+Jupiter+5L (Hora Sara)' }


def event_diksha_received(chart, ds, tr, yogas, age):
    '''5H+Jupiter+Ketu formal initiation.'''
    if age < 16:
        return None
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Jupiter' and ad == 'Ketu':
        score += 3
        why.append('Jupiter+Ketu diksha')
    if md == 'Ketu' and ad == 'Jupiter':
        score += 3
        why.append('Ketu+Jupiter spiritual order')
    if score < 3:
        return None
    return {
        'event': 'Diksha / formal spiritual initiation',
        'category': 'diksha',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': 'Jupiter+Ketu (Hora Sara)' }


def event_renunciation(chart, ds, tr, yogas, age):
    '''12H+Ketu sannyasa.'''
    if age < 30:
        return None
    lagna_idx = chart['lagna_idx']
    h12_lord = _lord(lagna_idx, 12)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Ketu' and ad == h12_lord:
        score += 4
        why.append('Ketu+12L renunciation')
    if md == 'Saturn' and ad == 'Ketu' and age >= 50:
        score += 2
        why.append('Saturn+Ketu vairagya')
    if score < 4:
        return None
    return {
        'event': 'Renunciation / sannyasa / monastic vow',
        'category': 'renunciation',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '12L+Ketu+Saturn (Hora Sara)' }


def event_monastic_phase(chart, ds, tr, yogas, age):
    '''12H+Ketu+Saturn monk-life.'''
    if age < 30:
        return None
    lagna_idx = chart['lagna_idx']
    h12_lord = _lord(lagna_idx, 12)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Saturn' and ad == h12_lord:
        score += 3
        why.append('Saturn+12L disciplined retreat')
    if md == 'Ketu' and ad == 'Saturn':
        score += 2
        why.append('Ketu+Saturn austere')
    if score < 3:
        return None
    return {
        'event': 'Monastic / ashram retreat phase',
        'category': 'monastic',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '12L+Ketu+Saturn (Hora Sara)' }


def event_oracle_dream(chart, ds, tr, yogas, age):
    '''Moon+Mercury+Ketu prophetic dream.'''
    if age < 14:
        return None
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Mercury' and ad == 'Ketu':
        score += 3
        why.append('Mercury+Ketu oracle')
    if score < 3:
        return None
    return {
        'event': 'Oracle / prophetic vision',
        'category': 'oracle',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': 'Moon+Mercury+Ketu (Hora Sara)' }


def event_synchronicity_peak(chart, ds, tr, yogas, age):
    '''Ketu strong synchronicity period.'''
    if age < 18:
        return None
    pos = chart['positions']
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Ketu' and _h(pos, 'Ketu') in (1, 5, 9, 12):
        score += 3
        why.append('Ketu+spiritual house')
    if score < 3:
        return None
    return {
        'event': 'Synchronicity peak / spiritual alignment',
        'category': 'synchronicity',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': 'Ketu strong (Hora Sara)' }


def event_divine_intervention(chart, ds, tr, yogas, age):
    '''9H+Jupiter favorable.'''
    if age < 20:
        return None
    lagna_idx = chart['lagna_idx']
    h9_lord = _lord(lagna_idx, 9)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Jupiter' and ad == h9_lord:
        score += 3
        why.append('Jupiter+9L grace')
    if score < 3:
        return None
    return {
        'event': 'Divine intervention / lucky break / grace moment',
        'category': 'divine_grace',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '9L+Jupiter (BPHS Ch.32)' }


def event_curse_lifted(chart, ds, tr, yogas, age):
    '''6H exit+Jupiter favorable.'''
    if age < 25:
        return None
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Jupiter' and ad == 'Ketu':
        score += 3
        why.append('Jupiter+Ketu curse lifted')
    if score < 3:
        return None
    return {
        'event': 'Curse / dosha lifted / karmic resolution',
        'category': 'curse_lifted',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': 'Jupiter+Ketu (Lal Kitab)' }


def event_blessing_received(chart, ds, tr, yogas, age):
    '''9H+11H+Jupiter blessing.'''
    if age < 5:
        return None
    lagna_idx = chart['lagna_idx']
    h9_lord = _lord(lagna_idx, 9)
    h11_lord = _lord(lagna_idx, 11)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Jupiter' and ad in (h9_lord, h11_lord):
        score += 3
        why.append(f'''Jupiter+{ad} blessing''')
    if score < 3:
        return None
    return {
        'event': 'Major blessing received (from elder/saint)',
        'category': 'blessing',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '9L+11L+Jupiter (Saravali)' }


def event_atonement_phase(chart, ds, tr, yogas, age):
    '''12H+Saturn+Jupiter atonement.'''
    if age < 30:
        return None
    lagna_idx = chart['lagna_idx']
    h12_lord = _lord(lagna_idx, 12)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Saturn' and ad == 'Jupiter':
        score += 3
        why.append('Saturn+Jupiter atonement')
    if md == h12_lord and ad == 'Jupiter':
        score += 2
        why.append('12L+Jupiter prayascittam')
    if score < 3:
        return None
    return {
        'event': 'Atonement / prayaschittam / karmic clearing phase',
        'category': 'atonement',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '12L+Saturn+Jupiter (BPHS)' }


def event_karma_purification(chart, ds, tr, yogas, age):
    '''Saturn+Ketu+12H deep clearing.'''
    if age < 28:
        return None
    lagna_idx = chart['lagna_idx']
    h12_lord = _lord(lagna_idx, 12)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Saturn' and ad == 'Ketu':
        score += 4
        why.append('Saturn+Ketu karma cleansing')
    if md == 'Ketu' and ad == h12_lord:
        score += 2
        why.append('Ketu+12L purification')
    if score < 4:
        return None
    return {
        'event': 'Deep karma purification phase',
        'category': 'karma_purification',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '12L+Saturn+Ketu (Hora Sara)' }


def event_moksha_pursuit(chart, ds, tr, yogas, age):
    '''12H+Ketu liberation pursuit.'''
    if age < 35:
        return None
    lagna_idx = chart['lagna_idx']
    h12_lord = _lord(lagna_idx, 12)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Ketu' and ad == h12_lord:
        score += 4
        why.append('Ketu+12L moksha')
    if score < 4:
        return None
    return {
        'event': 'Moksha pursuit / liberation-oriented phase',
        'category': 'moksha',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '12L+Ketu (Hora Sara)' }


def event_book_dharma(chart, ds, tr, yogas, age):
    '''9H+Jupiter dharma book publishing.'''
    if age < 30:
        return None
    lagna_idx = chart['lagna_idx']
    h9_lord = _lord(lagna_idx, 9)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Jupiter' and ad == h9_lord:
        score += 3
        why.append('Jupiter+9L dharma book')
    if score < 3:
        return None
    return {
        'event': 'Dharma / philosophical book / scripture work',
        'category': 'book_dharma',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '9L+Jupiter (Saravali Ch.30)' }


def event_prophetic_vision(chart, ds, tr, yogas, age):
    '''Moon+Ketu prophecy.'''
    if age < 20:
        return None
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Moon' and ad == 'Ketu':
        score += 4
        why.append('Moon+Ketu prophecy')
    if score < 3:
        return None
    return {
        'event': 'Prophetic vision / revelation',
        'category': 'prophecy',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': 'Moon+Ketu (Hora Sara)' }


def event_astral_travel(chart, ds, tr, yogas, age):
    '''12H+Ketu OBE.'''
    if age < 20:
        return None
    lagna_idx = chart['lagna_idx']
    h12_lord = _lord(lagna_idx, 12)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Ketu' and ad == h12_lord:
        score += 3
        why.append('Ketu+12L astral travel')
    if score < 3:
        return None
    return {
        'event': 'Astral travel / OBE / lucid spiritual experience',
        'category': 'astral_travel',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '12L+Ketu (Hora Sara)' }


def event_divine_call(chart, ds, tr, yogas, age):
    '''9H+Jupiter+Ketu calling.'''
    if age < 18:
        return None
    lagna_idx = chart['lagna_idx']
    h9_lord = _lord(lagna_idx, 9)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Jupiter' and ad == 'Ketu':
        score += 3
        why.append('Jupiter+Ketu divine call')
    if md == h9_lord and ad == 'Ketu':
        score += 2
        why.append('9L+Ketu dharma call')
    if score < 3:
        return None
    return {
        'event': 'Divine call / vocation revelation',
        'category': 'divine_call',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '9L+Jupiter+Ketu (Hora Sara)' }


def event_religious_persecution(chart, ds, tr, yogas, age):
    '''6H+12H+Saturn persecution for beliefs.'''
    if age < 18:
        return None
    lagna_idx = chart['lagna_idx']
    h6_lord = _lord(lagna_idx, 6)
    h12_lord = _lord(lagna_idx, 12)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == h6_lord and ad == h12_lord:
        score += 3
        why.append('6L+12L persecuted')
    if score < 3:
        return None
    return {
        'event': 'Religious / ideological persecution',
        'category': 'persecution',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '6L+12L+Saturn (BPHS Ch.40)' }


def event_oracle_consult(chart, ds, tr, yogas, age):
    '''9H+Jupiter+Ketu consult astrologer.'''
    if age < 15:
        return None
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Jupiter' and ad == 'Mercury':
        score += 2
        why.append('Jupiter+Mercury seek wisdom')
    if md == 'Ketu' and ad == 'Jupiter':
        score += 2
        why.append('Ketu+Jupiter oracle visit')
    if score < 3:
        return None
    return {
        'event': 'Oracle / astrologer consultation',
        'category': 'oracle_consult',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '9L+Jupiter+Ketu (Hora Sara)' }


def event_temple_donation(chart, ds, tr, yogas, age):
    '''12H+Jupiter major donation.'''
    if age < 25:
        return None
    lagna_idx = chart['lagna_idx']
    h12_lord = _lord(lagna_idx, 12)
    md = ds.get(1, { }).get('md')
    ad = ds.get(2, { }).get('ad')
    score = 0
    why = []
    if md == 'Jupiter' and ad == h12_lord:
        score += 3
        why.append('Jupiter+12L temple donation')
    if score < 3:
        return None
    return {
        'event': 'Major temple / charity donation',
        'category': 'temple_donation',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': '12L+Jupiter (Saravali)' }

ALL_PATTERNS_V2 = [][event_father][event_mother][event_self_accident][event_marriage][event_career_breakthrough][event_honor_recognition][event_education_milestone][event_foreign_travel][event_wealth_peak][event_wealth_loss][event_property][event_child_birth][event_spiritual][event_health_self][event_relationship_break][event_widowhood][event_self_death][event_siblings][event_vehicle_purchase][event_business_start][event_promotion][event_legal_dispute][event_inheritance][event_speculation_gain][event_speculation_loss][event_in_law_event][event_friend_loss][event_partnership_formation][event_partnership_break][event_pet_acquisition][event_charity_donation][event_visa_grant][event_eclipse_impact][event_saturn_return][event_jupiter_return][event_pregnancy][event_engagement][event_book_publication][event_award_nomination][event_house_construction][event_grandchildren_birth][event_brand_endorsement][event_political_office][event_jail_confinement][event_tax_dispute][event_voice_career][event_retirement][event_share_purchase][event_birth_circumstances][event_personality_shift][event_charisma_peak][event_voice_loss][event_dental_event][event_eye_problem][event_diet_change][event_sibling_marriage][event_sibling_death][event_hand_arm_injury][event_hearing_issue][event_sports_milestone][event_writing_career][event_home_renovation][event_real_estate_dispute][event_move_new_city][event_romance_affair][event_first_love][event_mantra_siddhi][event_creative_breakthrough][event_devotion_intensify][event_surgery_major][event_lawsuit_won][event_lawsuit_lost][event_workplace_conflict][event_marriage_arranged][event_marriage_love][event_second_marriage][event_spouse_health_crisis][event_lottery_win][event_lottery_loss][event_inheritance_land][event_insurance_claim][event_business_expansion][event_business_closure][event_income_breakthrough][event_salary_raise][event_salary_cut][event_loan_approval][event_loan_default][event_debt_freedom][event_franchise_open][event_patent_grant][event_royalty_payment][event_sponsorship_deal][event_subscriber_milestone][event_stock_crash_hit][event_crypto_gain][event_crypto_loss][event_bonus_windfall][event_tax_refund][event_property_loss][event_land_acquisition][event_plot_sale][event_mortgage_finalize][event_ancestral_inheritance][event_fortune_loss][event_friend_acquisition][event_betrayal_friend][event_elder_sibling_birth][event_elder_sibling_marriage][event_elder_sibling_death][event_father_in_law_event][event_mother_in_law_event][event_uncle_maternal_event][event_uncle_paternal_event][event_adoption][event_engagement_break][event_divorce][event_widowhood_remarriage][event_extramarital_affair][event_grandchild_marriage][event_great_grandparent_death][event_pet_death][event_loved_one_death][event_distant_relative_death][event_neighbor_dispute][event_business_partner_betrayal][event_business_partner_death][event_co_worker_event][event_servant_event][event_landlord_dispute][event_tenant_event][event_uncle_aunt_event][event_cousin_event][event_step_family_event][event_first_job][event_job_change][event_profession_switch][event_promotion_executive][event_board_role][event_founder_role][event_ceo_role][event_consultant_phase][event_corporate_scandal][event_fame_peak][event_fame_loss][event_government_position][event_diplomatic_role][event_military_role][event_judicial_role][event_teaching_role][event_research_role][event_medical_career][event_law_career][event_finance_career][event_tech_career][event_civil_service][event_singing_career][event_dancing_career][event_acting_career][event_engineering_career][event_pilgrimage][event_guru_initiation][event_religious_conversion][event_meditation_breakthrough][event_kundalini_awakening][event_psychic_experience][event_past_life_recall][event_dream_significant][event_temple_visit_major][event_chant_completion][event_mantra_initiation][event_yagna_performance][event_diksha_received][event_renunciation][event_monastic_phase][event_oracle_dream][event_synchronicity_peak][event_divine_intervention][event_curse_lifted][event_blessing_received][event_atonement_phase][event_karma_purification][event_moksha_pursuit][event_book_dharma][event_prophetic_vision][event_astral_travel][event_divine_call][event_religious_persecution][event_oracle_consult][event_temple_donation]

try:
    from claude_categories import ALL_CATALOG_PATTERNS
    ALL_PATTERNS_V2 = ALL_PATTERNS_V2 + ALL_CATALOG_PATTERNS
    
    def _age_at(d, chart):
        b = chart['birth']
        return (d - dt.datetime(b['year'], b['month'], b['day'])).days / 365.25

    
    def scan_year_v2(chart, year, sample_days, min_severity = (10, 2)):
        timeline = build_full_timeline(chart, levels = 3)
        yogas = detect_all_yogas(chart)
        events_by_window = { }
        d = dt.datetime(year, 1, 1)
        end = dt.datetime(year, 12, 31)
    # WARNING: Decompyle incomplete

    
    def scan_lifetime_v2(chart, year_from, year_to, sample_days, min_severity = (10, 2)):
        all_events = []
        for year in range(year_from, year_to + 1):
            ev = scan_year_v2(chart, year, sample_days = sample_days, min_severity = min_severity)
            for k, v in ev.items():
                v['year'] = year
                all_events.append(v)
        return all_events

    
    def collapse_consecutive(events):
        '''Merge consecutive-year same-event windows into single lifecycle bands.'''
        by_event = { }
        for ev in events:
            by_event.setdefault(ev['event'], []).append(ev)
        bands = []
    # WARNING: Decompyle incomplete

    _PRIMARY_KEYWORDS = ('7L (', 'Venus MD', '10L (', 'Jupiter transits natal 7L', 'as AD', 'benefic-stack', 'Moon MD +', 'Saturn MD')
    _SECONDARY_KEYWORDS = ('Venus AD', 'Venus PD', 'Jupiter MD', 'Jupiter AD', 'Venus dispositor', 'Jupiter transit', 'Venus transit', 'Sun activates', 'MD + Venus PD')
    _RANK_CONFIG = {
        'marriage': {
            'keep_top': 3,
            'rename_after': 'Relationship deepening / second-marriage potential',
            'rename_cat': 'relationship_phase' },
        'career': {
            'keep_top': 8,
            'rename_after': None,
            'rename_cat': None },
        'honor': {
            'keep_top': 6,
            'rename_after': None,
            'rename_cat': None },
        'wealth': {
            'keep_top': 5,
            'rename_after': None,
            'rename_cat': None },
        'health': {
            'keep_top': 4,
            'rename_after': None,
            'rename_cat': None },
        'death': {
            'keep_top': 3,
            'rename_after': None,
            'rename_cat': None },
        'accident': {
            'keep_top': 4,
            'rename_after': None,
            'rename_cat': None },
        'children': {
            'keep_top': 3,
            'rename_after': None,
            'rename_cat': None },
        'spiritual': {
            'keep_top': 3,
            'rename_after': None,
            'rename_cat': None },
        'travel': {
            'keep_top': 4,
            'rename_after': None,
            'rename_cat': None },
        'education': {
            'keep_top': 4,
            'rename_after': None,
            'rename_cat': None },
        '_default': {
            'keep_top': 4,
            'rename_after': None,
            'rename_cat': None } }
    
    def _score_window(band):
        '''Compute composite confidence score from an event band.

    score = ((primaries × 3) + secondaries + transit_boost) × density_factor + severity

    DENSITY PENALTY: long bands (>18 months) get progressively diluted.
    Reason: a 4-year span with one primary indicator should NOT outrank a
    2-month window with one primary indicator — the latter is more precise
    and astrologically more meaningful as a "peak moment" prediction.
    '''
        if not band.get('max_why'):
            band.get('max_why')
            if not band.get('why'):
                band.get('why')
        why = []
        if isinstance(why, str):
            why = [
                why]
        primaries = (lambda .0: pass# WARNING: Decompyle incomplete
)(why())
        secondaries = (lambda .0: pass# WARNING: Decompyle incomplete
)(why())
        transit_boost = 1 if (lambda .0: pass# WARNING: Decompyle incomplete
)(why()) else 0
        if not band.get('max_sev', band.get('severity', 3)):
            band.get('max_sev', band.get('severity', 3))
        sev = 3
        ws = band.get('window_start')
        we = band.get('window_end')
        
        try:
            duration_months = max((we - ws).days / 30, 1)
            density_factor = min(1, 18 / duration_months)
            base = primaries * 3 + secondaries + transit_boost
            return round(base * density_factor + sev, 1)
        except Exception:
            duration_months = 12
            continue


    
    def _stars(score):
        if score >= 9:
            return ('⭐⭐⭐', 'STRONG')
        if score >= 6:
            return ('⭐⭐', 'MODERATE')
        return ('⭐', 'POSSIBLE')

    
    def rank_and_consume(bands):
        '''Rank event windows by score + apply per-category keep limits.

    For marriage: top window stays "Marriage"; subsequent windows whose peak
    is AFTER the top window\'s peak get renamed to "Relationship phase".

    Returns ranked list with new fields: score, stars, confidence, rank.
    '''
        if not bands:
            return []
        by_cat = None
        for b in bands:
            if not b.get('category'):
                b.get('category')
            cat = '_default'
            by_cat.setdefault(cat, []).append(b)
        ranked_all = []
        for cat, lst in by_cat.items():
            cfg = _RANK_CONFIG.get(cat, _RANK_CONFIG['_default'])
            for b in lst:
                b['score'] = _score_window(b)
                (b['stars'], b['confidence']) = _stars(b['score'])
            lst.sort(key = (lambda b: (-b['score'], b['window_start'])))
            kept = lst[:cfg['keep_top']]
            if cfg['rename_after'] and len(kept) > 1:
                top = kept[0]
                top_peak = top['window_start']
                for i, b in enumerate(kept[1:], start = 2):
                    if not b['window_start'] > top_peak:
                        continue
                    b['event'] = cfg['rename_after']
                    b['category'] = cfg['rename_cat']
            for i, b in enumerate(kept, start = 1):
                b['rank'] = i
            ranked_all.extend(kept)
        return sorted(ranked_all, key = (lambda b: b['window_start']))

    if __name__ == '__main__':
        import json
        sys.stdout.reconfigure(encoding = 'utf-8')
        chart = json.load(open('../charts/manoj_chart.json', encoding = 'utf-8'))
        print('Scanning Manoj 1996-2050 with v2 predictor...')
        events = scan_lifetime_v2(chart, 1996, 2050, sample_days = 10, min_severity = 4)
        bands = collapse_consecutive(events)
        print(f'''
{len(bands)} life-event bands detected (severity 4+ only):
''')
        print(f'''{'AGE':<5}{'WINDOW':<22}{'SEV':<7}{'CATEGORY':<14}{'EVENT':<50}''')
        print('--------------------------------------------------------------------------------------------------')
        for b in bands:
            age = _age_at(b['window_start'], chart)
            wf = b['window_start'].strftime('%b %Y')
            wt = b['window_end'].strftime('%b %Y')
            win = f'''{wf} - {wt}''' if wf != wt else wf
            sev = '*' * b['max_sev']
            print(f'''{age:<5.0f}{win:<22}{sev:<7}{b['category']:<14}{b['event'][:48]}''')
        return None
    return None
except Exception:
    _e = [][event_father][event_mother][event_self_accident][event_marriage][event_career_breakthrough][event_honor_recognition][event_education_milestone][event_foreign_travel][event_wealth_peak][event_wealth_loss][event_property][event_child_birth][event_spiritual][event_health_self][event_relationship_break][event_widowhood][event_self_death][event_siblings][event_vehicle_purchase][event_business_start][event_promotion][event_legal_dispute][event_inheritance][event_speculation_gain][event_speculation_loss][event_in_law_event][event_friend_loss][event_partnership_formation][event_partnership_break][event_pet_acquisition][event_charity_donation][event_visa_grant][event_eclipse_impact][event_saturn_return][event_jupiter_return][event_pregnancy][event_engagement][event_book_publication][event_award_nomination][event_house_construction][event_grandchildren_birth][event_brand_endorsement][event_political_office][event_jail_confinement][event_tax_dispute][event_voice_career][event_retirement][event_share_purchase][event_birth_circumstances][event_personality_shift][event_charisma_peak][event_voice_loss][event_dental_event][event_eye_problem][event_diet_change][event_sibling_marriage][event_sibling_death][event_hand_arm_injury][event_hearing_issue][event_sports_milestone][event_writing_career][event_home_renovation][event_real_estate_dispute][event_move_new_city][event_romance_affair][event_first_love][event_mantra_siddhi][event_creative_breakthrough][event_devotion_intensify][event_surgery_major][event_lawsuit_won][event_lawsuit_lost][event_workplace_conflict][event_marriage_arranged][event_marriage_love][event_second_marriage][event_spouse_health_crisis][event_lottery_win][event_lottery_loss][event_inheritance_land][event_insurance_claim][event_business_expansion][event_business_closure][event_income_breakthrough][event_salary_raise][event_salary_cut][event_loan_approval][event_loan_default][event_debt_freedom][event_franchise_open][event_patent_grant][event_royalty_payment][event_sponsorship_deal][event_subscriber_milestone][event_stock_crash_hit][event_crypto_gain][event_crypto_loss][event_bonus_windfall][event_tax_refund][event_property_loss][event_land_acquisition][event_plot_sale][event_mortgage_finalize][event_ancestral_inheritance][event_fortune_loss][event_friend_acquisition][event_betrayal_friend][event_elder_sibling_birth][event_elder_sibling_marriage][event_elder_sibling_death][event_father_in_law_event][event_mother_in_law_event][event_uncle_maternal_event][event_uncle_paternal_event][event_adoption][event_engagement_break][event_divorce][event_widowhood_remarriage][event_extramarital_affair][event_grandchild_marriage][event_great_grandparent_death][event_pet_death][event_loved_one_death][event_distant_relative_death][event_neighbor_dispute][event_business_partner_betrayal][event_business_partner_death][event_co_worker_event][event_servant_event][event_landlord_dispute][event_tenant_event][event_uncle_aunt_event][event_cousin_event][event_step_family_event][event_first_job][event_job_change][event_profession_switch][event_promotion_executive][event_board_role][event_founder_role][event_ceo_role][event_consultant_phase][event_corporate_scandal][event_fame_peak][event_fame_loss][event_government_position][event_diplomatic_role][event_military_role][event_judicial_role][event_teaching_role][event_research_role][event_medical_career][event_law_career][event_finance_career][event_tech_career][event_civil_service][event_singing_career][event_dancing_career][event_acting_career][event_engineering_career][event_pilgrimage][event_guru_initiation][event_religious_conversion][event_meditation_breakthrough][event_kundalini_awakening][event_psychic_experience][event_past_life_recall][event_dream_significant][event_temple_visit_major][event_chant_completion][event_mantra_initiation][event_yagna_performance][event_diksha_received][event_renunciation][event_monastic_phase][event_oracle_dream][event_synchronicity_peak][event_divine_intervention][event_curse_lifted][event_blessing_received][event_atonement_phase][event_karma_purification][event_moksha_pursuit][event_book_dharma][event_prophetic_vision][event_astral_travel][event_divine_call][event_religious_persecution]
    _e = None
    del _e
    continue
    _e = None
    del _e

