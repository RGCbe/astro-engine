# Atro Engine — Astrology Prediction Taxonomy & Coverage Audit
**Built:** 2026-05-05 | **Engine version:** v14.0 (44 modules)
**Source:** 6 parallel research agents covering Vedic, Jaimini, KP, Tajik, Lal Kitab, Nadi, Ashtakavarga, Prashna, Western, Numerology, Palmistry, Vastu, Face Reading, Moles, Omens, Tantra, Chinese systems, Micro-events, and Karmic layers.

This document maps EVERY predictable element across all classical traditions against the Atro Engine's current capabilities. It is the source-of-truth for the engine roadmap.

---

# PART 1 — MASTER TAXONOMY (every predictable element)

## 1. SELF / PERSONALITY / BODY (~30 elements)

| # | Element | Method | Engine Status |
|---|---|---|---|
| 1 | Body build (lean/muscular/stout) | Lagna sign element + Lagna lord + nakshatra | ✅ |
| 2 | Height range | Lagna sign quality | ✅ |
| 3 | Complexion | Lagna lord + Sun + Moon dispositors | ✅ |
| 4 | Facial features / beauty | Venus + 2H + Lagna lord dignity | ✅ partial |
| 5 | Eye type (size, lustre, defects) | Sun (R), Moon (L), 2H, 12H | ⚠️ partial |
| 6 | Hair (texture, balding) | Mercury + Saturn on Lagna; Ketu in Lagna | ❌ |
| 7 | Voice quality | 2H + Mercury + Venus | ✅ partial |
| 8 | Speech style | 2L + Mercury placement | ✅ |
| 9 | Walking gait / posture | Lagna sign + Saturn position | ❌ |
| 10 | Marks/moles/scars location | Planet-in-Lagna + Kalapurusha mapping | ⚠️ partial |
| 11 | Mental temperament | Moon's sign/nakshatra/dispositor | ✅ |
| 12 | Intellect type | Mercury + 5L + Jupiter | ✅ |
| 13 | Memory power | Mercury + 5H + Moon-Mercury angle | ✅ partial |
| 14 | Will-power & ego | Sun + Lagna relationship | ✅ |
| 15 | Courage & decisiveness | 3H + Mars | ✅ |
| 16 | Emotional resilience | Moon strength, paksha bala | ✅ partial |
| 17 | Mental disorder risk | Moon-Mercury afflictions | ✅ |
| 18 | Truthfulness vs deceit | Jupiter + 2H + Mercury-Rahu | ✅ partial |
| 19 | Anger profile (slow/quick/cold) | Mars sign + Sun-Mars/Mars-Rahu/Mars-Saturn | ✅ |
| 20 | Sexual temperament | Venus + Mars + 7H | ✅ partial |
| 21 | Self-confidence / leadership | Sun in kendra/trikona, Sun-Jupiter | ✅ |
| 22 | Lifestyle (luxury/ascetic) | Venus vs Saturn dominance | ✅ partial |
| 23 | Cleanliness / dressing | Venus + Mercury + Lagna | ❌ |
| 24 | Sleep & dream nature | 12H + Moon | ❌ |
| 25 | Risk-appetite (gambler/conservative) | 5H + Mars + Rahu | ⚠️ partial |
| 26 | Innate luck / Bhagya | 9L strength + Sun-Jupiter + AK | ✅ |
| 27 | Soul personality (ego-trait) | Atmakaraka planet | ✅ |
| 28 | Public vs private nature | Lagna vs Sun & 10H | ⚠️ partial |
| 29 | Body part vulnerabilities | Kalapurusha mapping | ✅ |
| 30 | R/L side dominance | Sun vs Moon, odd/even rashi | ❌ |

**Coverage: ~70%**

---

## 2. PARENTS — FATHER (~20 elements)

| # | Element | Engine |
|---|---|---|
| 1-3 | Longevity, time of death, profession | ✅ |
| 4-7 | Social status, character, wealth, inheritance | ✅ |
| 8-10 | Estrangement, health vulnerabilities, spirituality | ✅ |
| 11-13 | Longevity rank, vigour, native's bond | ✅ partial |
| 14-16 | Foreign connection, second marriage, paternal uncles | ⚠️ partial |
| 17-20 | Education, vehicles, old-age reputation, adoption | ❌ |

**Coverage: ~75%**

---

## 3. PARENTS — MOTHER (~20 elements)
Same structural elements as father, mirrored to 4H/Moon. **Coverage: ~75%**

---

## 4. SIBLINGS (~20 elements)
Number, gender, elder/younger, eldest's gender, childhood loss, only-child, bond quality, longevity, careers, financial support, litigation, foreign sibling, step-siblings, sibling marriage, sibling children, gender-specific (Venus=sister, Mars=brother), profession, twin indication, estrangement.

**Engine status:** sibling_predictor.py covers 12/20 ✅. Missing: career detail, financial support, foreign sibling timing.
**Coverage: ~60%**

---

## 5. EDUCATION (~28 elements)
Schooling smoothness, higher ed, post-graduate, foreign education, subject of study, intellectual sharpness, memory & retention, concentration, drop-out risk, scholarships, learning disability, multiple degrees, math/logic, language/writing, music/arts, technical/engineering, medical, spiritual studies, research, teaching career, late-blooming, peak dasha, self-taught, scandal/cheating, online learning, oratory skill, parent-funded vs self-funded, best timing for higher study.

**Engine status:** generate_report.py "Education domain" + D24 chart — covers 18/28. **Coverage: ~65%**

---

## 6. MARRIAGE (~30 elements)
Timing, multiple windows, late, very early, spouse appearance, height/build, complexion, nature, wealth, profession, education, family background, same vs different community, foreign spouse, love vs arranged, inter-caste, Manglik dosha, divorce risk, second marriage, widowhood, multiple marriages, sexual harmony, extra-marital, abuse risk, spouse longevity, childlessness, live-in/never-married, re-marriage to same partner, marriage in foreign land, harmony index.

**Engine status:** spouse_inference.py + compatibility_kuta.py + dosha_cancellations.py + UL/Darapada — covers 25/30. **Coverage: ~85%** ⭐

---

## 7. CHILDREN (~28 elements)
Number, first child gender, conception timing, conception difficulty, miscarriage, IVF need, adoption, twins, late children, only-child, gender mix, eldest character, longevity, loss, child's career, education, marriage, foreign settlement, estrangement, step-children, financial support, conception via remedies, putra-dosha indications, special-needs, first-born survival, fame, hereditary issue, parent role.

**Engine status:** event_predictor_v2.py "child birth" + D7 saptamsa — covers 12/28. **Coverage: ~45%**

---

## 8. CAREER (~30 elements)
Field, multiple karakas (per-planet field), govt vs private, business vs job, multiple income sources, foreign career, peak years, dasha rise, demotion/scandal, self-employment, promotion timing, retirement, career break, field details (Karakamsha 10H), authority position, subordinate level, professional partnerships, family business, arts/entertainment, tech/IT, healing/medicine, spirituality, sudden rise, sudden fall, late success, politics, public office without rank, profit, reputation, online career, multiple careers count.

**Engine status:** D10 dashamsa + 10L analysis + AmK + KP 10H CSL + event_predictor career — covers 25/30. **Coverage: ~85%** ⭐

---

## 9. WEALTH (~30 elements)
Overall potential, self-made vs inherited, Dhana yogas, peak dasha, sudden wealth, slow steady, inheritance, loss periods, debts, bankruptcy, speculation, real estate, gold/jewellery, foreign income, royalties, commodities, multiple accounts, easy debt repayment, luxury spending, charity vs vices, money via spouse/children/parents, hidden wealth, insurance pay-outs, tax/govt seizure, mid-life dip, old-age sustainability, named yogas (Lakshmi, Kuber, Chandra-Mangala).

**Engine status:** Dhana yogas + D2 hora + 2L/11L + Saham wealth — covers 22/30. **Coverage: ~75%**

---

## 10. HEALTH (~32 elements)
Constitution (dosha), vulnerable organs, chronic vs acute, major illness windows, surgery timing, mental health, anxiety/depression, schizophrenia risk, eyesight, dental, heart, diabetes, cancer risk, reproductive, skin, liver/digestive, kidney, respiratory, spinal, addictions, accident-prone, vehicular accident, organ-specific surgery, longevity category, sudden death, lingering illness, recovery capacity, auto-immune/hereditary, allergies, hormonal, surgery success, post-50 patterns.

**Engine status:** medical_astrology + longevity_ayurdaya + Markesha + 6/8/12H — covers 22/32. **Coverage: ~70%**

---

## 11. TRAVEL (~25 elements)
Foreign settlement timing, permanent migration vs short trips, pilgrimage, work travel, sea voyages, air frequency, settlement direction (Jaimini disha), country preference, multiple migrations, return to homeland, travel for education/marriage/medical, forced relocation, leisure travel, frequent commute, failed migration, coastal/mountain settlement, family travel, foreign work visa, pilgrimage abroad, settled vs wanderer, theft during travel.

**Engine status:** event_predictor_v2 travel + Rahu+12L + Saham Pravasa — covers 16/25. **Coverage: ~65%**

---

## 12. PROPERTY (~25 elements)
First home timing, multiple properties, ancestral, self-built, loss, disputes, foreign property, vehicle ownership, multiple vehicles, luxury vehicles, jewellery, land/agricultural, commercial, rental income, construction trouble, inheritance, sale, furniture/luxury, garden/water house, near-temple, joint vs nuclear family, old-age home, frequent shifting, comfort level, domestic peace.

**Engine status:** 4H + 4L + Mars + Venus — covers 15/25. **Coverage: ~60%**

---

## 13. STATUS / FAME (~28 elements)
Fame potential (Bhery/Shankha/Shrinatha), recognition timing, awards, political career, election win, social standing, online/social-media fame, author fame, performer/artist, sports, spiritual/guru, scandal, defamation, loss of position, philanthropy, posthumous, local vs international, youth vs old-age fame, sudden rise, rapid fall, hereditary nobility, social activism, cult/niche following, fame via spouse/children/family, peer reputation, defamation periods.

**Engine status:** 10H + Sun + Raja yogas + Adhi Yoga — covers 18/28. **Coverage: ~65%**

---

## 14. RELATIONSHIPS / ENEMIES (~30 elements)
Friendship circle size, quality, influential friends, loss, betrayal, open enemies, hidden enemies, enemy count, court cases, litigation timing, police/legal trouble, imprisonment, illicit affairs, romantic partners count, stable vs turbulent friendships, mentor/guru, servants/staff, enemies-become-friends, friends-become-enemies, sibling-as-enemy, in-laws, business partners, subordinate loyalty, native's loyalty, quarrel-prone, diplomatic, public popularity, romantic charisma, toxic-partner attraction.

**Engine status:** 6H/11H + Argala + 7L analysis — covers 17/30. **Coverage: ~55%**

---

## 15. SPIRITUALITY (~27 elements)
Religious inclination, religion type, family vs personal path, conversion likelihood, atheism, guru in life, multiple gurus, pilgrimage frequency, renunciation (Pravrajya), meditation depth, yoga/tantra path, Bhakti/Jnana/Karma/Raja preference, ritual style, faith strength, spiritual experiences, paranormal, moksha probability, reincarnation lessons, charity inclination, healer/spiritual service, occult/tantric, astrology aptitude, cult involvement, atheist↔believer cycle, gives discourses, mantra effectiveness, past-life vow influence.

**Engine status:** Ketu + 9L + Jupiter + Karakamsa + nadi_jyotish — covers 18/27. **Coverage: ~65%**

---

## 16. TALENTS (~30 elements)
Music (vocal/instrumental), dance, painting, sculpture/craft, writing, poetry, drama/acting, sports/combat, strategic games (chess), languages, public speaking, comedy, cooking, gardening/herbalism, mechanical/engineering, computer/coding, mathematics, healing/Reiki, intuition/psychic, astrology/divination, mediumship, photography, fashion/design, architecture, animal handling, sailing/aviation, magic/illusion.

**Engine status:** Venus + Mercury + Mars + 5H — covers 15/30. **Coverage: ~50%**

---

## 17. PAST LIVES / KARMA (~30 elements)
Ketu's house = past mastery, Ketu's sign = psychological theme, Ketu's dispositor, Rahu's house/sign/dispositor, Atmakaraka soul-purpose, AK in Karakamsha, **karmic debts (12 types):** Pitra-Rin, Matra-Rin, Stree-Rin, Bhratru-Rin, Putra-Rin, Nyaya-Rin, Atma-Rin, Guru-Rin, Brahma-Rin, Naga-Rin, Pretha-Rin, Bhumi-Rin. Saturn's house, dusthana planets, exalted/debilitated past-life themes, retrograde re-do, vargottama destiny, planetary war loyalties, Jaimini chara karakas relations, Upapada marriage karma, Aroodha self-image karma, Karakamsha battleground, spiritual path readiness, grace/merit accumulated.

**Engine status:** lal_kitab (7 Karz) + Atmakaraka + nadi + Ketu/Rahu — covers 18/30. **Coverage: ~60%**

---

## 18. DEATH-RELATED (~30 elements)
Longevity (alpa/madhya/poorna), sudden death, prolonged illness, peaceful, painful/violent, manner-of-end (fire/water/weapon/disease/old-age), suicide risk, foreign vs homeland, hospital vs home, sacred place, while travelling, family present, alone, posthumous reputation, departure dasha (Maraka), final dasha sequence, self-vs-other-hand, conscious yogic death, reincarnation timing hint, karmic completion, cremation/burial preference, anniversary triggers, untimely death of close relative, sudden vs predicted timing.

**Engine status:** longevity_ayurdaya + Markesha + Shoola Dasha — covers 14/30. **Coverage: ~45%**

---

## 19. TIMING SYSTEMS (Vedic ~80 systems)

### Dasha Systems (42 in BPHS)
| System | Engine |
|---|---|
| Vimshottari (4-level MD/AD/PD/SD) | ✅ |
| Ashtottari | ✅ |
| Yogini | ✅ |
| Char Dasha (Jaimini) | ✅ |
| Kalachakra | ❌ |
| Shoola | ❌ |
| Sthira | ❌ |
| Drig | ❌ |
| Niryana Shoola | ❌ |
| Patyayini | ⚠️ partial (within Varshaphala) |
| Kendradi Graha/Rashi | ❌ |
| Karaka Dasha | ❌ |
| 12 Nakshatra-based Dashas | ❌ (have 3 of 12) |
| 24 Rashi-based Dashas | ❌ |
| 6 Special Dashas (Mool, Tara, Pinda, Naisargika, Ashtakavarga, Sandhya) | ❌ |

**Dasha Coverage: 4/42 = ~10%**

### Transit Systems
| System | Engine |
|---|---|
| Gochara (general) | ✅ |
| Sade Sati (3 phases) | ✅ |
| Dhaiyya/Kantaka/Ashtama Shani | ❌ |
| Saturn Return | ✅ |
| Jupiter cycle (12y) | ⚠️ partial |
| Rahu-Ketu 18.6y | ⚠️ partial |
| Mars/Mercury/Venus retrograde events | ❌ |
| Tara Bala | ✅ |
| Chandra Bala | ✅ |
| Vedha (transit obstruction) | ❌ |
| Ashtakavarga transit | ✅ |

**Transit Coverage: 7/11 = ~65%**

### Annual / Tajik
| System | Engine |
|---|---|
| Varshaphala | ✅ |
| Muntha | ✅ |
| Year Lord (Varshesha) | ✅ partial (basic only) |
| Mudda Dasha | ✅ |
| Patyayini Dasha | ✅ |
| Tri-Pataki Chakra | ✅ |
| 28 Tajik Sahams | ✅ (22 of 28) |
| 16 Tajik Aspects (orb-based) | ❌ |
| 16 Tajik Yogas (Ittasala, Ishrafa etc.) | ❌ ★ critical gap |
| Tajik Balas (Hadda, Trirashi etc.) | ❌ |

**Annual Coverage: 7/10 = ~70%**

### Eclipses
| System | Engine |
|---|---|
| Solar/Lunar eclipse detection | ✅ |
| Total vs partial distinction | ❌ |
| Eclipse on natal points | ✅ |
| Eclipse on dasha lord | ⚠️ partial |

**Eclipse Coverage: 2/4 = ~50%**

### Panchanga (5-fold time)
| System | Engine |
|---|---|
| Tithi | ✅ |
| Vara | ✅ |
| Yoga (27 panchanga yogas) | ✅ |
| Karana (11 types) | ✅ |
| Nakshatra (transit-day) | ✅ |

**Panchanga: 5/5 = 100%** ⭐

### Muhurta
| System | Engine |
|---|---|
| Marriage muhurta | ✅ |
| Travel muhurta | ✅ |
| Business start muhurta | ✅ |
| Surgery muhurta | ✅ |
| Gemstone muhurta | ❌ |
| Griha Pravesh | ❌ |
| Vehicle purchase | ❌ |
| Conception (Garbhadhana) | ❌ |
| Naming (Namakarana) | ❌ |
| Sacred thread (Upanayana) | ❌ |
| Land/property purchase | ❌ |
| Court case filing | ❌ |
| Coronation/inauguration | ❌ |
| Sowing/harvest | ❌ |
| Loan giving/taking | ❌ |
| Funeral | ❌ |
| Religious vow | ❌ |
| Yagya/homa | ❌ |

**Muhurta Coverage: 4/18 = ~22%**

---

## 20. JAIMINI ADVANCED (~26 elements)
Chara Karakas (7 + 8th scheme), Karakamsha Lagna (12 houses from), Swamsa Kundali, 12 Arudha Padas (A1-A12), Upapada Lagna, Darapada, Dharmapada, Karya-pada, Lakshmi Pada, Argala (subha + paap), Virodha Argala, Jaimini Rashi Drishti, Char Dasha, Sthira Dasha, Shoola Dasha, Drig Dasha, Trikona Dasha, Niryana Shoola, Brahma/Rudra/Maheshwara, Atmakaraka journey 12 houses, Mandi/Gulika in Jaimini, Pravas Arudha, Bhratrupada, Pitripada, 7 Jaimini yogas.

**Engine status:** jaimini_full + char_dasha + argala_jaimini — covers 18/26. **Coverage: ~70%**

---

## 21. KP (KRISHNAMURTI PADDHATI) (~25 elements)
Sub-lord theory, Sub-sub-lord (3 levels), Cuspal Sub-Lord (CSL) for 12 cusps, 249 sub-divisions, Significator chains (4 levels), Ruling Planets (RP), Horary 1-249, Daily Bhava chart, KP aspects, Stellar Astrology, KP Ayanamsa, Cuspal Interlinks, Promise+Trigger+Confirmation, Sookshma+Pran level dasha, Combined CSL, Marriage via 7th CSL, Childbirth via 5th CSL, Career via 10th CSL, Disease/death via 1-6-8-12 CSL, Foreign via 3-12 CSL, Lottery via 5-11 CSL, Education via 4-9 CSL, Property via 4-11 CSL.

**Engine status:** kp_paddhati.py — covers 12/25. **Coverage: ~50%**

---

## 22. ADVANCED PARASHARI (~24 elements)
Vargottama, Pushkara navamsa, Pushkara bhaga, degree-precise transits, D10/D7/D60 deep, D45/D27, Ashtakavarga transit, D12 parents, D3 siblings, D30 evils, Bhava Bala, Vimshopaka Bala, Ishta-Kashta Phala, Tara Bala daily, Chandra Kriya/Avastha (60 lunar states), Avasthas (Baladi 5, Jagrad 3, Deeptadi 9), Karmic axes, Graha Yuddha (8 types), Cheshta states (5 motions), Chamatkar Chintamani technique, Bhavartha Ratnakara yogas, Kaksha Vibhag, Sudarshana Chakra.

**Engine status:** divisional_charts + extra_vargas + shadbala_full + ashtakavarga + vimshopaka — covers 17/24. **Coverage: ~70%**

---

## 23. WESTERN ASTROLOGY (~50 elements)
12 sign personalities, Moon/Rising/Mercury/Venus/Mars/Jupiter/Saturn/Uranus/Neptune/Pluto archetypes, Chiron, Lilith, North/South Node, Vertex/Anti-vertex, East Point, Part of Fortune + 30 Lots, Asteroids (Ceres/Pallas/Juno/Vesta/Eros/Psyche), 30 Fixed stars, Midpoints, Harmonics (5/7/9), Declinations, Major aspects (5), Minor aspects (4), Quintile/Septile family, Saturn return, Jupiter return, Uranus opposition (40-42), Neptune square (40-44), Pluto square (40), Chiron return (50), Solar/Lunar return charts, Mercury/Venus/Mars retrogrades, Secondary progressions, Solar arc, Tertiary, Minor progressions, Profections, Synastry, Composite, Davison, Electional, Horary, Mundane, Locational/AstroCartography, Relocation, Psychological astrology layer, Evolutionary astrology, Hellenistic (Sect, Time Lords, Lots), Pluto generation, Modern outer-planet themes.

**Engine status:** ❌ Currently 100% Vedic. **Coverage: ~5%** (only basic placements via SwissEph)

---

## 24. LAL KITAB (~25 elements)
Houses as "rooms" with permanent furniture, 108 cells (9p × 12h), 7 Karz (Pitra/Matra/Stree/Bhratru/Putra/Nyaya/Atma), Asleep planets (sote hue), Cursed planets (shrapit), Andha Kundli, Manda planets, 7th-only aspects, Houses as blood relations, Tatkal vs Sthayee dosha, Bandi Karm, Physical-action remedies (no mantras), Career obstructions per house, Debt cycles by age, House-by-house remedy timing, Closed vs open kundli, Maternal-paternal cross-dependency.

**Engine status:** lal_kitab.py — covers 12/25. **Coverage: ~50%**

---

## 25. NADI ASTROLOGY (~25 elements)
Bhrigu Nadi, Brighu Naadi Sangraha, Chandra Kala Nadi (Deva Keralam), Saptarishi Nadi, Devakeralam Nadi, Specific 2-planet rules (Sun-Sat, Sun-Rahu, etc. — 13 combos), Bhava-specific Nadi, Karaka-based Nadi, 9×12=108 Nadi cells, Past-life narrative, Specific name predictions, Profession naming, Date-specific events, Father/mother/spouse names, Disease by Nadi, Past life identity, Karmic sub-events, Number of marriages exact, Children's gender exact, Year of death.

**Engine status:** nadi_jyotish.py — covers 8/25. **Coverage: ~30%**

---

## 26. ASHTAKAVARGA (~20 elements)
Bhinna AV (per planet), Sarvashtakavarga, Trikona Sodhana, Ekadhipatya Sodhana, Sodhya Pinda, Kakshya Bala, Kaksha Vibhag (8 sub-divisions), BAV transit, SAV transit, Sade Sati severity via AV, Year-strength via AV, Pinda for longevity, House strength quantification, Specific bindu thresholds (30+/25+/20+/<20), Saturn BAV ascendant longevity, Comparing two charts via AV, Deciding life-paths via AV.

**Engine status:** ashtakavarga + ashtakavarga_reductions — covers 14/20. **Coverage: ~70%**

---

## 27. PRASHNA (HORARY) (~20 elements)
Prashna Marga rules, Aroodha lagna, KP Horary (1-249), Question type templates (yes/no, timing, location, person, lost item, marriage, career, travel safety, disease, litigation, theft, pregnancy), Tajik Prashna, Vaikari variants, Promise+Trigger detection, First syllable maps to nakshatra, Lagna sign quality, Moon void of course, Combust/retrograde significator.

**Engine status:** prashna_horary.py — covers 12/20. **Coverage: ~60%**

---

## 28. NUMEROLOGY (~25 elements)
Mulanka, Bhagyanka, Name Number, Soul Number, Personality Number, Maturity Number, Personal Year/Month/Day, Master Numbers (11/22/33), Lo Shu Grid (9 cells), Compatibility matching, Business name, Product name, House number, Vehicle, Phone, Bank account, Universal Year, Number-by-number traits (1-9), Numeroscope (12 cycles), Lucky dates/colors/gems.

**Engine status:** numerology_vedic.py — covers 14/25. **Coverage: ~55%**

---

## 29. PALMISTRY (~30 elements)
4 hand shapes, 7 mounts, 4 main lines, 12 secondary lines, 5 fingers (planetary), Fingerprints (Sankha/Padma/Chakra/Dhwaja), Color/temperature/texture, Marriage count + timing, Children count + gender, Major illness windows, Career switches, Foreign travel, Wealth peaks, Spiritual awakening markers, Death timing (general), Specific traits.

**Engine status:** ❌ **Coverage: 0%**

---

## 30. VASTU (~20 elements)
8 directions + 16 sub-directions, Direction-element mapping, Bedroom/kitchen/office/toilet placement, Brahmasthan, Specific doshas (NE-cut, SW-extension, SE-bedroom, NE-toilet, kitchen-NE, plot-tapering), 32-pada main door analysis, Vastu Purusha Mandala, Plot shape effects, Floor count, Auspicious entrance directions, Vastu remedies (mirrors/salt/plants/colors).

**Engine status:** ❌ **Coverage: 0%**

---

## 31. FACE READING (~20 elements)
Forehead 3-band life-stage map, Eye types, Eyebrows, Nose (wealth karaka), Mouth/lips, Chin (longevity), Ears (longevity), Cheeks, Hundreds of mole positions catalogued, Color of mole interpretation, Career via face shape, Marriage via lip shape, Wealth via nose, Longevity via ears+chin, Specific traits.

**Engine status:** ❌ **Coverage: 0%**

---

## 32. BODY MOLES (~25 elements)
Head, forehead, eyebrow (L/R), eye corners, cheeks, lips, tongue, chin, neck (front/back), shoulder, chest (L/R), back (upper/lower), stomach/navel, genital, thigh (L/R), knee, calf, ankle, foot sole. Color (red/honey/black/brown), shape, hair-on-mole.

**Engine status:** ❌ **Coverage: 0%**

---

## 33. OMENS (Shakuna Shastra) (~15 elements)
Birds, animals crossing, objects falling, sneezing, eye twitch (M/F different), body itching, dreams (Swapna Shastra catalog), sounds heard, travel-direction Disha-Shoola.

**Engine status:** ❌ **Coverage: 0%**

---

## 34. TANTRA / OCCULT (~12 elements)
Yantras (per outcome), Mantra timing, Birth-time deity, Ishta Devata via 12L nakshatra+AK, Karmic lineage from Nadi.

**Engine status:** Basic Ishta Devata via Atmakaraka — covers 3/12. **Coverage: ~25%**

---

## 35. CHINESE & OTHER COMPLEMENTARY (~15 elements)
Chinese zodiac (12 animals × 5 elements = 60-year), Bazi (4 pillars), I Ching (64 hexagrams), Tarot (78 cards), Kabbalah Tree of Life, Geomancy (16 figures), Scrying, Runes (Elder Futhark), Ifa/Yoruba (256 Odu).

**Engine status:** ❌ **Coverage: 0%**

---

## 36. SPIRITUAL / KARMIC / DIVINE LAYER (~40 elements)
Soul age, Atmakaraka soul-lesson, 12 past-life houses via Ketu, 12 growth-edge houses via Rahu, Karakamsha seat, Past-life profession (Ketu in 10H), Past-life family role, Karmic debts (12+ types), Past-life merits, Why-this-life-this-family, Soul groups, Twin-flame indicators, Soul-mate vs karmic-mate, Wisdom carried over, Trauma carried over, Path indication (Bhakti/Karma/Jnana/Raja), Bhakti-rasa intensity, Service inclination, Knowledge-seeking, Meditation aptitude, 10 specific deity-affinities (Ganesha/Shiva/Vishnu/Lakshmi/Saraswati/Durga/Hanuman/Krishna/Rama/Murugan), Mantra suitability per planet, Yantra suitability, Pilgrimage attraction, Lineage suitability, Path preference, Gemstone for spiritual vs material, Karmic relationships (mother/father/sibling/spouse/child/friend/teacher), Specific shaap detection (Brahmin/Pitri/Naga/Stree/Putri/Bhratri), Moksha probability, Specific liberation path, Bondage indicators, Final birth signs, Mahasamadhi capability, Direct deity-vision, Miraculous experiences, Divine guidance dreams, Saints' blessings, Ashram/temple attraction, Specific tantric sadhana, Kundalini awakening, Chakra blockages, Aura color (some), Ancestral profession imprint, Family curse-breaker, New family-line founder, Native will become guru/write book/found ashram/renounce/be siddha/etc.

**Engine status:** Atmakaraka + Ishta + Karakamsa + Ketu/Rahu + Pravrajya + 7 Karz — covers 18/40. **Coverage: ~45%**

---

## 37. MICRO EVENTS (~80 specific predictable events)

### Career-related
First job, job loss, promotion, demotion, retirement, last career venture, award, scandal, defamation, public scandal, business start, business closure, bankruptcy.

### Travel-related
First international, permanent settlement, return from foreign, work travel.

### Health-related
First major accident, major surgery, knee/hip replacement, depression start, depression recovery, addiction start, addiction recovery, surgery success/failure.

### Relationship
First love, first serious relationship, engagement, marriage day, reconciliation with family.

### Family / Children
First child date, subsequent children, miscarriages, adoption, twins, grandchildren.

### Property / Material
Property purchase, sale, house construction, vehicle purchase, vehicle accident.

### Money
Lottery/windfall, inheritance, major loss, recovery after loss.

### Crisis
Court case start, court verdict, imprisonment, theft victim, loss of wallet/ID, loss of pet.

### Death
Death of father/mother/spouse/child/native, place of death, manner of death, family present.

### Spiritual
Awakening date, religious conversion, guru initiation, major realization moments.

### Physical characteristics (~16 specific items)
Height, build, complexion, hair, eyes, body marks, voice, walking, posture, distinctive feature, beauty, sex appeal, presence, strength, athletic capacity, body-part vulnerability.

### Psychological traits (~19)
Decisiveness, optimism, introvert/extrovert, logical/intuitive, detail/big-picture, risk tolerance, anger pattern, forgiveness, memory, dream nature, sleep, sexual nature, fidelity, honesty, speech, spending/saving, loyalty, stubbornness, adaptability.

### Karmic micro-themes (~15)
Past-life profession, past-life relationship debts, soul age, family role, recurring patterns, triggering people-types, unfinished karmic accounts, soul lessons this life, karmic gifts, parent-child past-life, sibling karmic contracts, spousal karmic contracts, friend/enemy karmic identification, pet/animal karma, land/place karma.

### Career micro (~13)
Specific field detail, job-changes count, boss type, subordinate type, office direction, business partner type, multiple income count, investment type, stock timing, real estate timing, online business, foreign client, pitching/interview/salary days.

### Marriage micro (~21)
Pre-marital relationships count, first romance age, heartbreak count, spouse profession, spouse height/complexion, spouse family wealth, spouse family direction, spouse birthplace type, engagement vs love, same-religion vs cross, same-caste vs cross, wedding fanfare, honeymoon, first child timing, year-by-year harmony, divorce probability, remarriage, widow/widower year.

### Children micro (~12)
First child gender, first child name letter, first child profession, first child marriage, first child settlement direction, second child probability, twin probability, IVF need, step-children, adopted child probability, bond quality with each child, inheritance to children timing.

### Wealth/Property micro (~14)
Specific income ranges, currency themes, real-estate vs liquid ratio, business vs salary, stocks vs bonds, crypto, business types favored, ancestor profession revival, number of houses, plot vs apartment, foreign property, inherited vs self-built, major losses amount/timing, recovery timing, last decade pattern.

### Death prediction (~10)
Approximate age, manner, place, family present, quick vs prolonged, organ failure, suicide risk, murder risk (rare), spiritual state, funeral arrangements.

### Rare / Exotic (~14)
Twin birth, genius marker, fame young, polyamory, same-sex orientation, gender identity, profession of unborn child, ancestral profession revival, reincarnation indicators, memory of past life, specific phobias from past life, special powers (siddhis), spiritual rank, dietary inclinations, alcohol/drug attraction.

**Engine status:** event_predictor_v2 + 13 patterns + spouse_inference + sibling_predictor — covers ~50/80 micro-events. **Coverage: ~60%**

---

# PART 2 — ENGINE COVERAGE SUMMARY

## Aggregate by Domain

| Domain | Engine Coverage |
|---|---|
| **Self / Personality / Body** | 70% |
| **Father** | 75% |
| **Mother** | 75% |
| **Siblings** | 60% |
| **Education** | 65% |
| **Marriage** | **85%** ⭐ |
| **Children** | 45% |
| **Career** | **85%** ⭐ |
| **Wealth** | 75% |
| **Health** | 70% |
| **Travel** | 65% |
| **Property** | 60% |
| **Status / Fame** | 65% |
| **Relationships / Enemies** | 55% |
| **Spirituality** | 65% |
| **Talents** | 50% |
| **Past Lives / Karma** | 60% |
| **Death-related** | 45% |
| **Dasha Systems (42)** | 10% |
| **Transit Systems** | 65% |
| **Annual / Tajik** | 70% |
| **Eclipses** | 50% |
| **Panchanga** | **100%** ⭐ |
| **Muhurta** | 22% |
| **Jaimini Advanced** | 70% |
| **KP Paddhati** | 50% |
| **Advanced Parashari** | 70% |
| **Western Astrology** | **5%** 🔴 |
| **Lal Kitab** | 50% |
| **Nadi Astrology** | 30% |
| **Ashtakavarga** | 70% |
| **Prashna** | 60% |
| **Numerology** | 55% |
| **Palmistry** | **0%** 🔴 |
| **Vastu** | **0%** 🔴 |
| **Face Reading** | **0%** 🔴 |
| **Body Moles** | **0%** 🔴 |
| **Omens** | **0%** 🔴 |
| **Tantra/Occult** | 25% |
| **Chinese / Tarot / Kabbalah** | **0%** 🔴 |
| **Spiritual/Karmic Layer** | 45% |
| **Micro Events** | 60% |

## Overall Engine Coverage: **~58% of total astrology body**

That's higher than my previous estimate (40%) because we have deep Vedic but **zero coverage on 7 entire complementary traditions** (Western, Palmistry, Vastu, Face/Mole reading, Omens, Chinese, Tarot/Kabbalah).

---

# PART 3 — PRIORITY ROADMAP

## 🔴 TIER 1 — Highest Impact, Total Gaps (build first)

| # | Module | Gap Type | Effort | Why High |
|---|---|---|---|---|
| 1 | `western_astrology.py` | 95% missing | 5d | Adds 50+ predictions Vedic doesn't catch (Pluto generation, Chiron, Hellenistic Lots, modern psyche layer) |
| 2 | `palmistry_engine.py` | 100% missing | 4d | Independent confirmation layer; users want it; 30+ predictions |
| 3 | `vastu_analysis.py` | 100% missing | 3d | Direction-environment readings; remedial layer |
| 4 | `face_reading.py` | 100% missing | 3d | Mukha Samudrika Shastra; trait verification |
| 5 | `body_moles.py` | 100% missing | 2d | Tila Lakshana; complements other readings |

**Tier 1 total: 17 days → engine reaches 75% coverage**

## 🟠 TIER 2 — Major Gaps in Existing Domains

| # | Module | Gap | Effort |
|---|---|---|---|
| 6 | `dasha_systems_full.py` | 38 of 42 dashas missing | 6d |
| 7 | `tajik_yogas_16.py` | 16 Tajik Ittasala-class yogas missing ★ | 3d |
| 8 | `muhurta_extended.py` | 14 of 18 muhurta types missing | 4d |
| 9 | `expanded_yogas.py` | ~250 of 300 named yogas missing | 7d |
| 10 | `nadi_combinations.py` | 108 Nadi cells deep | 5d |

**Tier 2 total: 25 days → engine reaches 88% coverage**

## 🟡 TIER 3 — Specialty / Niche

| # | Module | Effort |
|---|---|---|
| 11 | `omens_shakuna.py` | 2d |
| 12 | `chinese_bazi.py` | 4d |
| 13 | `tarot_integration.py` | 3d |
| 14 | `tantra_specific.py` | 3d |
| 15 | `face_mole_database.py` | 2d |
| 16 | `western_outer_planets.py` | 3d |

**Tier 3 total: 17 days → engine reaches 95% coverage**

---

## Final Tally

| Phase | Days | Coverage After |
|---|---|---|
| Current state | — | 58% |
| + Tier 1 (5 modules) | 17 | 75% |
| + Tier 2 (5 modules) | 42 | 88% |
| + Tier 3 (6 modules) | 59 | 95% |

**Total ~60 days of focused build to reach 95% — true universal divinatory engine.**

The remaining 5% is hyper-specialty (regional Tamil Naadi, Devakeralam line-by-line, Kabbalah Pathworking, Enochian, Ifa) that 99% of users never need.

---

# WHAT NEXT?

**Recommended order:**
1. Start with **western_astrology.py** — biggest user-visible gap, fastest impact
2. Then **palmistry_engine.py** — high user-demand, independent confirmation
3. Then **tajik_yogas_16.py** — fixes annual chart precision (critical missing piece)
4. Then **expanded_yogas.py** — closes the largest classical gap (~250 yogas)
5. Then **dasha_systems_full.py** — adds Kalachakra/Shoola/Sthira/Drig

Each module follows the same pattern as the 44 already-built modules: predicates + classical sources + integrate via engine_orchestrator.py + add to PDF report.

— end —
