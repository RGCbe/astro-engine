# Corpus Quality Audit — v3 Re-Scoring

Source: `book_corpus_index_v2.json` (11,692 passages, 38 books, 72 topics).

Output: `book_corpus_index_v3.json` with new field `quality_v3` (0.0–1.0).

## 1. Score Distribution (v2 vs v3)

| Bucket | v2 count | v2 % | v3 count | v3 % |
|---|---:|---:|---:|---:|
| > 0.85 (excellent) | 1,691 | 14.5% | 3,651 | 31.2% |
| 0.70 – 0.85 (high) | 2,254 | 19.3% | 4,130 | 35.3% |
| 0.50 – 0.70 (good) | 2,670 | 22.8% | 2,348 | 20.1% |
| 0.30 – 0.50 (medium) | 2,722 | 23.3% | 1,071 | 9.2% |
| 0.15 – 0.30 (poor) | 1,011 | 8.6% | 328 | 2.8% |
| < 0.15 (junk) | 1,344 | 11.5% | 164 | 1.4% |

**v2 mean** = 0.537, **v3 mean** = 0.737.

**v2 median** = 0.560, **v3 median** = 0.780.

## 2. Per-Book Quality Ranking

Books ordered by mean v3 quality. `n` = passage count, `HQ`/`MED`/`LOW` are >0.7 / 0.3-0.7 / <0.3.

| Rank | Book | n | mean | median | HQ | MED | LOW | %HQ |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | `BPHS_Sharma_Vol1` | 90 | 0.931 | 0.960 | 87 | 2 | 1 | 96.7% |
| 2 | `Saravali` | 468 | 0.917 | 0.950 | 447 | 19 | 2 | 95.5% |
| 3 | `Brihat_Parashara_v2` | 1,183 | 0.852 | 0.908 | 1,020 | 142 | 21 | 86.2% |
| 4 | `Raman_HowToJudge` | 482 | 0.852 | 0.860 | 464 | 15 | 3 | 96.3% |
| 5 | `Brighu_Naadi_Sangraha` | 29 | 0.832 | 0.860 | 25 | 4 | 0 | 86.2% |
| 6 | `BPHS1` | 578 | 0.825 | 0.838 | 509 | 67 | 2 | 88.1% |
| 7 | `Jataka_Parijata` | 141 | 0.825 | 0.854 | 118 | 19 | 4 | 83.7% |
| 8 | `Raman_Notable_Horoscopes` | 537 | 0.822 | 0.850 | 500 | 32 | 5 | 93.1% |
| 9 | `Prashna_Marga` | 424 | 0.822 | 0.852 | 358 | 63 | 3 | 84.4% |
| 10 | `Brihat_Jataka_Sastri` | 66 | 0.812 | 0.842 | 57 | 8 | 1 | 86.4% |
| 11 | `Laghu_Parashari` | 216 | 0.802 | 0.834 | 183 | 30 | 3 | 84.7% |
| 12 | `Bhavartha_Ratnakara_Raman` | 52 | 0.794 | 0.800 | 37 | 14 | 1 | 71.2% |
| 13 | `Jaimini_Sutras` | 213 | 0.793 | 0.822 | 168 | 44 | 1 | 78.9% |
| 14 | `Hora_Sara` | 368 | 0.790 | 0.808 | 306 | 60 | 2 | 83.2% |
| 15 | `KP_Reader_3_Predictive` | 736 | 0.778 | 0.796 | 575 | 154 | 7 | 78.1% |
| 16 | `Tajik_Adawal_Encyclopedia` | 223 | 0.766 | 0.814 | 158 | 58 | 7 | 70.9% |
| 17 | `BPHS2` | 563 | 0.757 | 0.818 | 415 | 116 | 32 | 73.7% |
| 18 | `Phaladeepika` | 460 | 0.751 | 0.800 | 332 | 101 | 27 | 72.2% |
| 19 | `Raman_AstrologyForBeginners` | 113 | 0.731 | 0.798 | 76 | 32 | 5 | 67.3% |
| 20 | `Unknown_6945` | 16 | 0.722 | 0.837 | 12 | 2 | 2 | 75.0% |
| 21 | `KP_Reader_6_Horary` | 452 | 0.718 | 0.744 | 281 | 163 | 8 | 62.2% |
| 22 | `Uttara_Kalamrita` | 212 | 0.691 | 0.717 | 111 | 93 | 8 | 52.4% |
| 23 | `KP_Reader_2_Fundamentals` | 569 | 0.681 | 0.708 | 294 | 268 | 7 | 51.7% |
| 24 | `Yavanajataka_2` | 996 | 0.662 | 0.710 | 514 | 395 | 87 | 51.6% |
| 25 | `Varshaphal_Raman` | 71 | 0.609 | 0.690 | 35 | 22 | 14 | 49.3% |
| 26 | `surya_siddhanta_english_text` | 812 | 0.593 | 0.635 | 233 | 536 | 43 | 28.7% |
| 27 | `Aryabhatiya_v1` | 303 | 0.593 | 0.638 | 100 | 178 | 25 | 33.0% |
| 28 | `Surya_Siddhanta` | 805 | 0.589 | 0.616 | 221 | 536 | 48 | 27.5% |
| 29 | `Aryabhatiya_v2` | 218 | 0.545 | 0.574 | 40 | 156 | 22 | 18.3% |
| 30 | `Vedanga_Jyotisa` | 102 | 0.528 | 0.619 | 29 | 55 | 18 | 28.4% |
| 31 | `Muhurtha_Chintamani` | 4 | 0.485 | 0.510 | 0 | 4 | 0 | 0.0% |
| 32 | `Yavanajataka_1` | 83 | 0.464 | 0.496 | 5 | 62 | 16 | 6.0% |
| 33 | `Pancha_Siddhantika` | 23 | 0.436 | 0.478 | 0 | 18 | 5 | 0.0% |
| 34 | `Bhrigu_Samhita` | 18 | 0.296 | 0.250 | 0 | 7 | 11 | 0.0% |
| 35 | `Sarvartha_Chintamani` | 10 | 0.282 | 0.275 | 0 | 5 | 5 | 0.0% |
| 36 | `Brihat_Jataka` | 18 | 0.281 | 0.300 | 0 | 10 | 8 | 0.0% |
| 37 | `Chamatkar_Chintamani` | 1 | 0.268 | 0.268 | 0 | 0 | 1 | 0.0% |
| 38 | `Lal_Kitab_Original` | 37 | 0.132 | 0.150 | 0 | 0 | 37 | 0.0% |

### Top 5 Highest-Quality Books

1. **BPHS_Sharma_Vol1** — mean=0.931, HQ=87/90 (97%)
2. **Saravali** — mean=0.917, HQ=447/468 (96%)
3. **Brihat_Parashara_v2** — mean=0.852, HQ=1,020/1,183 (86%)
4. **Raman_HowToJudge** — mean=0.852, HQ=464/482 (96%)
5. **Brighu_Naadi_Sangraha** — mean=0.832, HQ=25/29 (86%)

### Bottom 5 Noisiest Books

(lowest mean score — these books contribute least useful verbatim citation material)

1. **Bhrigu_Samhita** — mean=0.296, n=18, 17/18 (94%) score below 0.5
2. **Sarvartha_Chintamani** — mean=0.282, n=10, 10/10 (100%) score below 0.5
3. **Brihat_Jataka** — mean=0.281, n=18, 18/18 (100%) score below 0.5
4. **Chamatkar_Chintamani** — mean=0.268, n=1, 1/1 (100%) score below 0.5
5. **Lal_Kitab_Original** — mean=0.132, n=37, 37/37 (100%) score below 0.5

## 3. Per-Topic Coverage

Topics ranked by count of high-quality (>0.7) passages.

| Rank | Topic | total n | HQ | MED | LOW | %HQ |
|---:|---|---:|---:|---:|---:|---:|
| 1 | `property` | 5,487 | 4,579 | 825 | 83 | 83.5% |
| 2 | `moon` | 5,702 | 4,386 | 1,199 | 117 | 76.9% |
| 3 | `marriage` | 5,090 | 4,318 | 701 | 71 | 84.8% |
| 4 | `sun` | 6,010 | 4,312 | 1,576 | 122 | 71.7% |
| 5 | `saturn` | 4,384 | 3,765 | 571 | 48 | 85.9% |
| 6 | `jupiter` | 4,424 | 3,757 | 604 | 63 | 84.9% |
| 7 | `mars` | 4,277 | 3,657 | 559 | 61 | 85.5% |
| 8 | `venus` | 4,062 | 3,501 | 499 | 62 | 86.2% |
| 9 | `mercury` | 3,849 | 3,264 | 518 | 67 | 84.8% |
| 10 | `wealth` | 3,443 | 2,872 | 508 | 63 | 83.4% |
| 11 | `aspect` | 2,984 | 2,699 | 273 | 12 | 90.4% |
| 12 | `health` | 2,736 | 2,287 | 422 | 27 | 83.6% |
| 13 | `dasha` | 2,659 | 2,250 | 343 | 66 | 84.6% |
| 14 | `kp_paddhati` | 3,399 | 2,103 | 1,114 | 182 | 61.9% |
| 15 | `rahu` | 2,221 | 1,958 | 233 | 30 | 88.2% |
| 16 | `children` | 2,153 | 1,822 | 302 | 29 | 84.6% |
| 17 | `death` | 2,237 | 1,745 | 441 | 51 | 78.0% |
| 18 | `conjunction` | 1,733 | 1,409 | 311 | 13 | 81.3% |
| 19 | `spirituality` | 1,739 | 1,395 | 317 | 27 | 80.2% |
| 20 | `enemies` | 1,541 | 1,267 | 249 | 25 | 82.2% |
| 21 | `travel` | 1,606 | 1,250 | 332 | 24 | 77.8% |
| 22 | `father` | 1,542 | 1,248 | 260 | 34 | 80.9% |
| 23 | `navamsa_d9` | 1,319 | 1,216 | 93 | 10 | 92.2% |
| 24 | `education` | 1,799 | 1,210 | 533 | 56 | 67.3% |
| 25 | `remedies` | 1,717 | 1,193 | 461 | 63 | 69.5% |
| 26 | `ketu` | 1,298 | 1,138 | 133 | 27 | 87.7% |
| 27 | `fame` | 1,331 | 1,110 | 208 | 13 | 83.4% |
| 28 | `mother` | 1,304 | 1,072 | 209 | 23 | 82.2% |
| 29 | `career` | 1,250 | 1,045 | 191 | 14 | 83.6% |
| 30 | `siblings` | 1,216 | 1,040 | 168 | 8 | 85.5% |
| 31 | `speech` | 844 | 634 | 179 | 31 | 75.1% |
| 32 | `lagna_lord` | 628 | 577 | 51 | 0 | 91.9% |
| 33 | `transit` | 674 | 542 | 116 | 16 | 80.4% |
| 34 | `panch_mahapurusha` | 469 | 290 | 150 | 29 | 61.8% |
| 35 | `drekkana_d3` | 301 | 255 | 34 | 12 | 84.7% |
| 36 | `ashtakavarga` | 334 | 254 | 64 | 16 | 76.0% |
| 37 | `jaimini` | 290 | 228 | 58 | 4 | 78.6% |
| 38 | `raja_yoga` | 191 | 169 | 18 | 4 | 88.5% |
| 39 | `atmakaraka` | 172 | 163 | 9 | 0 | 94.8% |
| 40 | `varshaphala` | 225 | 147 | 67 | 11 | 65.3% |
| 41 | `neecha_bhanga` | 135 | 132 | 3 | 0 | 97.8% |
| 42 | `prashna` | 199 | 126 | 65 | 8 | 63.3% |
| 43 | `vimshottari` | 182 | 119 | 42 | 21 | 65.4% |
| 44 | `dashamsa_d10` | 143 | 114 | 21 | 8 | 79.7% |
| 45 | `lunar_yoga` | 128 | 103 | 20 | 5 | 80.5% |
| 46 | `solar_yoga` | 197 | 97 | 83 | 17 | 49.2% |
| 47 | `trimsamsa_d30` | 97 | 86 | 9 | 2 | 88.7% |
| 48 | `nabhasa` | 84 | 71 | 11 | 2 | 84.5% |
| 49 | `muhurta` | 138 | 70 | 60 | 8 | 50.7% |
| 50 | `dwadasamsa_d12` | 77 | 66 | 7 | 4 | 85.7% |
| 51 | `dhana_yoga` | 69 | 59 | 7 | 3 | 85.5% |
| 52 | `kalachakra_dasha` | 67 | 56 | 11 | 0 | 83.6% |
| 53 | `shashtiamsa_d60` | 62 | 54 | 7 | 1 | 87.1% |
| 54 | `putrakaraka` | 54 | 51 | 3 | 0 | 94.4% |
| 55 | `shapit_yoga` | 69 | 51 | 17 | 1 | 73.9% |
| 56 | `gaja_kesari` | 47 | 40 | 7 | 0 | 85.1% |
| 57 | `parivartana` | 43 | 40 | 2 | 1 | 93.0% |
| 58 | `matrukaraka` | 37 | 37 | 0 | 0 | 100.0% |
| 59 | `kemadruma` | 36 | 32 | 3 | 1 | 88.9% |
| 60 | `vipareeta` | 36 | 30 | 6 | 0 | 83.3% |
| 61 | `amatyakaraka` | 24 | 24 | 0 | 0 | 100.0% |
| 62 | `bhratrukaraka` | 18 | 17 | 1 | 0 | 94.4% |
| 63 | `budha_aditya` | 20 | 16 | 4 | 0 | 80.0% |
| 64 | `saptamsa_d7` | 21 | 15 | 5 | 1 | 71.4% |
| 65 | `amala_yoga` | 14 | 13 | 1 | 0 | 92.9% |
| 66 | `saraswati_yoga` | 17 | 11 | 6 | 0 | 64.7% |
| 67 | `shodasamsa_d16` | 14 | 9 | 5 | 0 | 64.3% |
| 68 | `yogini_dasha` | 8 | 8 | 0 | 0 | 100.0% |
| 69 | `chara_dasha` | 10 | 8 | 2 | 0 | 80.0% |
| 70 | `gnatikaraka` | 6 | 6 | 0 | 0 | 100.0% |
| 71 | `darakaraka` | 3 | 3 | 0 | 0 | 100.0% |
| 72 | `sade_sati` | 1 | 0 | 1 | 0 | 0.0% |

### Top 10 Well-Covered Topics (by HQ count)

1. `property` — 4,579 HQ (83% of 5,487)
2. `moon` — 4,386 HQ (77% of 5,702)
3. `marriage` — 4,318 HQ (85% of 5,090)
4. `sun` — 4,312 HQ (72% of 6,010)
5. `saturn` — 3,765 HQ (86% of 4,384)
6. `jupiter` — 3,757 HQ (85% of 4,424)
7. `mars` — 3,657 HQ (86% of 4,277)
8. `venus` — 3,501 HQ (86% of 4,062)
9. `mercury` — 3,264 HQ (85% of 3,849)
10. `wealth` — 2,872 HQ (83% of 3,443)

### Top 10 Under-Covered Topics (17 topics with <50 HQ)

1. `sade_sati` — only **0** HQ (of 1 total)
2. `darakaraka` — only **3** HQ (of 3 total)
3. `gnatikaraka` — only **6** HQ (of 6 total)
4. `yogini_dasha` — only **8** HQ (of 8 total)
5. `chara_dasha` — only **8** HQ (of 10 total)
6. `shodasamsa_d16` — only **9** HQ (of 14 total)
7. `saraswati_yoga` — only **11** HQ (of 17 total)
8. `amala_yoga` — only **13** HQ (of 14 total)
9. `saptamsa_d7` — only **15** HQ (of 21 total)
10. `budha_aditya` — only **16** HQ (of 20 total)

## 4. Sample Passages

### 4.1 Excellent (score > 0.85) — 5 examples

**[Bhavartha_Ratnakara_Raman@20800]** v3=**1.000** (v2=1.00) tags=['conjunction', 'marriage', 'education', 'health', 'death']

> various combinations which render Mars the lord of lagna (a) capable of inflicting death and (b) capable of conferring yoga or fame. Summarising the above we find that:  1. Death occurs in the Mars Dasa by diseases pertaining to the head if Mars is associated with 6th and 8th lords. It is not clear as to what the author means when he refers to Mars being in association with 8th…

**[Bhavartha_Ratnakara_Raman@22100]** v3=**1.000** (v2=1.00) tags=['marriage', 'wealth', 'siblings', 'children', 'property']

> of the various technicalities of the astrological science.  3. Stanza 9 says that Kuja can become Yogaharaka if he is in the 2nd with Jupiter and Venus, while the 10th sloka says that the above yoga gets cancelled if the combination occurs in the 3rd house. Venus is lord of the 2nd while Jupiter is lord of the 9th. Mars is lord of lagna. This combination of the lords of lagna, …

**[Bhavartha_Ratnakara_Raman@23400]** v3=**1.000** (v2=1.00) tags=['conjunction', 'marriage', 'wealth', 'siblings', 'children']

> asara and Lomasa say that the native will not have much happiness from children and that the first child does not live. "LAGNESA PANCHAMA MANEE SUTHASOWAHYAMCHA MADHYAMAL PRADHAMAPATHYA NASASYAD KRODHI RAJAPRAVESAH" Kuja may become a Yogakaraka but may render the native unhappy in respect of children.  6. Stanza 7 reveals that only in regard to Mesha lagna lord of 2nd in the 12…

**[Bhavartha_Ratnakara_Raman@40300]** v3=**1.000** (v2=1.00) tags=['conjunction', 'aspect', 'marriage', 'wealth', 'mother']

> a very important combination and is full of significance Saturn destroys the indications of the bhava in which he is situated except the 8th house If he is in the 2nd, you will see that the native will never save any money in spite of big earnings He will die a pauper or in very adverse financial circumstances Of course there are exceptions to this rule when Saturn is a yogakar…

**[BPHS1@42900]** v3=**1.000** (v2=0.81) tags=['marriage', 'father', 'property', 'panch_mahapurusha', 'dasha']

> ate to the presiding deity. In this case, Subrahmanya is the deity .and the name can be Kumara (gqn) or Guha (gq). Similar deductions can be suitably made in other cases. If the .Mars K&\iu^*  MercurY i*J-"' IuPiter lpudt,t.. Saturn 30  Brilnt parasara Hora Sastra initial letter belongs to a planet without dignity, it will bring bad lupk. Likewise, the Nakshatras too have presi…

### 4.2 Junk (score < 0.15) — 5 examples

**[Aryabhatiya_v1@0]** v3=**0.000** (v2=0.00) tags=['kp_paddhati']

> # Aryabhatiya_v1.pdf — OCR by Tesseract (eng+hin+san, DPI 200)    ====== PAGE 1 ======  ARYABHATIYA  OF ARYABHATA  Critically edited  with Introduction, English Translation, Notes, Comments and Indexes  By KRIPA SHANKAR SHUKLA  Deptt. of Mathematics and Astronomy University of Lucknow `  in collaboration with  K. V. SARMA V. V. 8, Institute of Sanskrit and Indological Studies P…

**[Aryabhatiya_v1@470600]** v3=**0.000** (v2=0.00) tags=['wealth']

> year in Hindu astronomy’, JC, 8 (1941) 114-16,  Levin, G.M. Bongard : Aryabhata and Lokayatas’, Paper presented at the Seminar on Aryabhata, INSA, New Delhi, Nov. 1976.  Mazumdar, N.K. : ‘Aryabhata’s rule in relation to indeterminate equations of the first degree’, BCMS, 3 (1911-12) 11-19.  Midonick, H. (Edr.): The Treasury of mathematics, Penguin Books, vol. I, 1968, pp. 219-2…

**[Aryabhatiya_v2@2600]** v3=**0.000** (v2=0.00) tags=['father', 'remedies']

> ning ८० (6 : ५6६ OOH  Qdiios प्णुएटुणुत ‘yeorwyed) ६9081 ‘ON “WnpueAlIy, “qsuy ‘soy 0 “AINA शण्णशञ्र : ए SIN 1 WuvNS¥Ha JO ‘WOD FHL HLIM WAILVHAVAUY  --- Page 5 --- CONTENTS  Page  FOREWORD ३३ INTRODUCTION रचा Introductory ० xvii  1. Bhaskara I eee xviii 1. A Saivite Hindu vee ऋषा,  2. Bhaskara’s date बह xix 1. Datta’s conjecture tee XX  2. Bhaskara I not a direct pupil of Arya…

**[Aryabhatiya_v2@228800]** v3=**0.000** (v2=0.00) tags=['remedies', 'kp_paddhati']

> zing Committee for the 1500th Birth Anniversary of Aryabhata I, who have taken keen interest in this work and have gladly offered all possible help and advice from time to time. They have, indeed, earned the gratitude of all scholars working in the field of Indian mathematics and astronomy. My first and most cordial thanks are offered to them.  T have great pleasure in expressi…

**[Aryabhatiya_v2@778700]** v3=**0.000** (v2=0.00) tags=['father']

> atantra, Gitika, Svatantrantara Aryabhatiyah (=followers of  Aryabhata 1), 88  ASmaka (Aryabhata 1), 148, 155  Asmakasya genitam, 138  Asmakiya (=follower of Arya- bhata 1), 146  Asmakiyam ( = Aryabhatiyam), 140, 147, 148  Astadhyayi (of Panini), 3, 8, 9, 23, 55, 63, 125, 218  459०1६4, 17  Bhagavadgita, 24, 198  शावा [का (वाक्व, 222  Bhata-Sastra (= Aryabhatiya), 137 .  Bhata-t…

### 4.3 Borderline (0.40 – 0.60) — 5 examples

**[Aryabhatiya_v1@5200]** v3=**0.436** (v2=0.00) tags=['conjunction', 'death', 'kp_paddhati']

> ractions Reduction of two fractions to a common denominator ,,, Method of inversion Unknown quantities from sums of all but one Unknown quantities from equal sums Meeting of two moving bodies wee Pulveriser Residual pulveriser Non-residual puiveriser  गा, KALAKRIYA OR THE RECKONING OF TIME  Time divisions and circular divisions Conjunctions of two planets in a yuga Vyatipatas i…

**[Brihat_Parashara_v2@1582100]** v3=**0.518** (v2=0.01) tags=['career', 'death', 'property', 'remedies', 'moon']

> ne karsha (equal in weight to the  former silver rupee) of gold or of weight one can afford. The idol should-  (1) Have a New Moon on the forehead,  (2) have a white garland round the neck,  (3) have three eyes (one being on, he forehead),  (4) be dressed in white robes,   (5) be seated on a bull, and   (6) be two armed, and  (7) carry Vara (वर) and Abhaya (अभय).   Page 822    …

**[Prashna_Marga@19500]** v3=**0.540** (v2=0.16) tags=['travel', 'jupiter', 'moon']

> ll —  290 Predicting floods —  292 Adverse winds —  294 CHAPTER XXVI (Koopa Prasna) Hints for discovering water layers —  295 Indicative signs —  296 Dearth of water —  297 Gupti chakra —  298  Existence of submerged wells —  303 Taste of the water —  305 Vastu Purusha —  306 Clues from plants —  306 Depth of the water layer —  307 CHAPTER XXVII (Bhojana Prasna) Menu at meals —…

**[surya_siddhanta_english_text@1146600]** v3=**0.524** (v2=0.08) tags=['father', 'moon']

> gitude, polar—term how employed in thia work, viii. In; polar longitudes of aster- 00 n. Puranic geography, xii. 44 n. Minute of arc, i. 28. Mitra, divinity of 17th asterisiu, 222. 44 ", Month—civil, i. 12: lunar, i. 13; number in an Age, i. 35 ; names of those com- posing the year, i. 51 n, xiv. 16 n ; how derived, xiv. 16 n ; divisions of lunar month, i. 51 n : intercalary mo…

**[Tajik_Adawal_Encyclopedia@273000]** v3=**0.570** (v2=0.37) tags=['conjunction', 'aspect', 'marriage', 'wealth', 'spirituality']

> 12 mental tension & losses. 4. Afflicted Sun in 12 the year   190 Encyclopedia of Vedic Astrology: Tajik Shastra and Annual Horoscopy Mo 24:47 Mun As 21:49 Ve4:12 Su3:06 Ju28:1 5. S u n  as year lord in 12 afflicted to losses through servants & subordinates. 6. I f  12 Saturn 5,1 Moon occupies 12th house, there would be loss of money through misplaced trust. 7. Mars & Saturn to…

## 5. Recommendations

### 5.1 Recommended quality threshold

- threshold **0.50** → retains **10,129** / 11,692 = 86.6%
- threshold **0.55** → retains **9,855** / 11,692 = 84.3%
- threshold **0.60** → retains **9,440** / 11,692 = 80.7%
- threshold **0.65** → retains **8,756** / 11,692 = 74.9%
- threshold **0.70** → retains **7,781** / 11,692 = 66.5%

**Recommendation: use ≥ 0.55 for citation-grade quoting** (balances retention with verbatim hygiene). For semi-automatic surface display use ≥ 0.40. For lookup/cross-reference (where junk is tolerable), all passages are kept.

### 5.2 Books needing re-extraction

- `Bhrigu_Samhita` — mean=0.296, 11/18 (61%) below 0.3. Likely OCR issues; consider re-running Tesseract with better DPI or page-deskew, or replacing source PDF.
- `Sarvartha_Chintamani` — mean=0.282, 5/10 (50%) below 0.3. Likely OCR issues; consider re-running Tesseract with better DPI or page-deskew, or replacing source PDF.
- `Brihat_Jataka` — mean=0.281, 8/18 (44%) below 0.3. Likely OCR issues; consider re-running Tesseract with better DPI or page-deskew, or replacing source PDF.
- `Chamatkar_Chintamani` — mean=0.268, 1/1 (100%) below 0.3. Likely OCR issues; consider re-running Tesseract with better DPI or page-deskew, or replacing source PDF.
- `Lal_Kitab_Original` — mean=0.132, 37/37 (100%) below 0.3. Likely OCR issues; consider re-running Tesseract with better DPI or page-deskew, or replacing source PDF.

### 5.3 Topics needing additional source books

Topics with too few high-quality passages — predictions on these aspects rely on a thin corpus and may need a dedicated source PDF added (e.g. Vimshottari Padhati for `vimshottari`, Kala Chakra Dasha by Sanjay Rath for `chara_dasha`, Brihat Jataka chapter on female charts for `darakaraka`):

- `sade_sati` — only **0** HQ (of 1 tagged); insufficient for confident citation.
- `darakaraka` — only **3** HQ (of 3 tagged); insufficient for confident citation.
- `gnatikaraka` — only **6** HQ (of 6 tagged); insufficient for confident citation.
- `yogini_dasha` — only **8** HQ (of 8 tagged); insufficient for confident citation.
- `chara_dasha` — only **8** HQ (of 10 tagged); insufficient for confident citation.
- `shodasamsa_d16` — only **9** HQ (of 14 tagged); insufficient for confident citation.
- `saraswati_yoga` — only **11** HQ (of 17 tagged); insufficient for confident citation.
- `amala_yoga` — only **13** HQ (of 14 tagged); insufficient for confident citation.
- `saptamsa_d7` — only **15** HQ (of 21 tagged); insufficient for confident citation.
- `budha_aditya` — only **16** HQ (of 20 tagged); insufficient for confident citation.
- `bhratrukaraka` — only **17** HQ (of 18 tagged); insufficient for confident citation.
- `amatyakaraka` — only **24** HQ (of 24 tagged); insufficient for confident citation.
- `vipareeta` — only **30** HQ (of 36 tagged); insufficient for confident citation.
- `kemadruma` — only **32** HQ (of 36 tagged); insufficient for confident citation.
- `matrukaraka` — only **37** HQ (of 37 tagged); insufficient for confident citation.

**Suggested additions (priority):**

1. `Sade Sati` (Saturn transit over Moon) — only **1** HQ. Add B.V. Raman's *Studies in Jaimini Astrology* or *The Saturn Transit* by Komilla Sutton.
2. `Yogini Dasha` — only 8 HQ. Add Sanjay Rath's *Yogini Dasha* monograph.
3. `Chara Dasha` (Jaimini) — only 9 HQ. Add Sanjay Rath's *Jaimini Maharishi's Upadesha Sutras*.
4. `Saraswati / Amala / Budha-Aditya yogas` — combined <60 HQ. Add a yoga-encyclopedia (e.g. K.N. Rao's *Yogas in Astrology* or Phaladeepika ch. 6 re-extraction).
5. `Saptamsa D7 / Shodasamsa D16 / Vimshamsa D20` — divisional charts thinly covered. Add Sanjay Rath's *Vargas* / Iranganti Rangacharya's divisional manual.

### 5.4 General notes

- The v2 scorer's mean (0.537) was inflated by a generous 0.30 baseline + small reward terms. v3 is harsher on OCR garbage and produces a more useful 3-bucket separation.
- Devanagari-only passages with broken character runs are now down-weighted explicitly (avg run length < 3).
- Mojibake / replacement-character (`U+FFFD`) ratio penalty added.
- Single-letter-word ratio penalty captures OCR fragmentation.
- ToC dot-leaders (`.....`) and page-header markers explicitly downscored.
