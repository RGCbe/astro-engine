# Atro Corpus Quality Dashboard

_Generated: 2026-04-25 15:00_


## 1. Raw Corpus Stats

- **Books decoded**: 34
- **Total items**: 8,239
- **Predictive rules**: 3,828
- **Yogas named**: 1,132
- **Techniques taught**: 1,302

## 2. Semantic Deduplication (Tool 1)

- **Raw rules**: 3,828
- **Unique canonical (after dedup)**: 3,065
- **Compression**: 19.9%

### Confidence breakdown
| Level | Threshold | Count | % |
|---|---|---:|---:|
| CANONICAL | ≥5 books | 0 | 0.0% |
| STRONG | 3-4 books | 84 | 2.7% |
| MODERATE | 2 books | 243 | 7.9% |
| ANECDOTAL | 1 book | 2738 | 89.3% |

### Top cross-cited rules (most-confluent)
| #b | trigger | books |
|---:|---|---|
| 4 | 7th Lord in 2nd House | BPHS1, BPHS_Sharma_Vol1, BPHS_Vol1, Brihat_Parashara_v2 |
| 4 | 7th Lord in 9th House | BPHS1, BPHS_Sharma_Vol1, BPHS_Vol1, Brihat_Parashara_v2 |
| 4 | 8th Lord in 2nd House | BPHS1, BPHS_Sharma_Vol1, BPHS_Vol1, Brihat_Parashara_v2 |
| 4 | 8th Lord in 3rd House | BPHS1, BPHS_Sharma_Vol1, BPHS_Vol1, Brihat_Parashara_v2 |
| 4 | 8th lord in 8th house | BPHS1, BPHS_Sharma_Vol1, BPHS_Vol1, Brihat_Parashara_v2 |
| 4 | 9th lord in the 3rd house | BPHS1, BPHS_Sharma_Vol1, BPHS_Vol1, Brihat_Parashara_v2 |
| 4 | 9th lord in the 12th house | BPHS1, BPHS_Sharma_Vol1, BPHS_Vol1, Brihat_Parashara_v2 |
| 4 | 10th lord in the 3rd house | BPHS1, BPHS_Sharma_Vol1, BPHS_Vol1, Brihat_Parashara_v2 |
| 4 | 10th lord in the 5th house | BPHS1, BPHS_Sharma_Vol1, BPHS_Vol1, Brihat_Parashara_v2 |
| 4 | 10th lord in the 6th house | BPHS1, BPHS_Sharma_Vol1, BPHS_Vol1, Brihat_Parashara_v2 |
| 4 | 10th lord in the 8th house | BPHS1, BPHS_Sharma_Vol1, BPHS_Vol1, Brihat_Parashara_v2 |
| 4 | 10th Lord in 10th House | BPHS1, BPHS_Sharma_Vol1, BPHS_Vol1, Brihat_Parashara_v2 |
| 4 | 11th lord in the 2nd house | BPHS1, BPHS_Sharma_Vol1, BPHS_Vol1, Brihat_Parashara_v2 |
| 4 | 11th lord in the 3rd house | BPHS1, BPHS_Sharma_Vol1, BPHS_Vol1, Brihat_Parashara_v2 |
| 4 | 11th lord in the 5th house | BPHS1, BPHS_Sharma_Vol1, BPHS_Vol1, Brihat_Parashara_v2 |

## 3. Yoga Canonicalization (Tool 2)

- **Raw yogas (after junk filter)**: 1,120
- **Junk filtered out**: 12
- **Unique canonical yogas**: 630
- **Compression**: 43.8%

### Top yogas by book confluence
| #b | yoga | alt names |
|---:|---|---|
| 16 | raja yoga | Raj Yoga, Raja Yoga, Raja Yogas |
| 10 | gaja kesari yoga | Gaja Kesari Yoga, Gaja Kesari yoga, Gajakesari Yoga |
| 10 | kemadruma yoga | Kemadruma, Kemadruma Yoga, Kemadruma yoga |
| 8 | sunapha yoga | Sunapha, Sunapha Yoga, Sunaphayoga |
| 8 | dhana yoga | Dhana Yoga |
| 8 | adhi yoga | Adhi Yoga, Adhiyoga |
| 7 | anapha yoga | Anapha, Anapha Yoga, Anaphayoga |
| 6 | vajra yoga | Vajra, Vajra Yoga, Vajra yoga |
| 6 | kedara yoga | Kedara, Kedara Yoga, Kedara yoga |
| 5 | yava yoga | Yava, Yava Yoga, Yava yoga |
| 5 | yupa yoga | Yupa, Yupa Yoga, Yupa yoga |
| 5 | pasa yoga | Pasa, Pasa Yoga, Pasa yoga |
| 5 | yuga yoga | Yuga, Yuga Yoga, Yuga yoga |
| 5 | trikona yoga | Trikona, Trikona Yoga |
| 5 | nala yoga | Nala, Nala Yoga, Nala yoga |

## 4. Rule Verification (Tool 3)

- **Sample size**: 200
- **HIGH-similarity verified**: 0.0%
- **PARTIAL verified**: 2.0%

⚠️ **CAVEAT**: The verifier uses string-similarity which underestimates accuracy.
Rules are typically PARAPHRASED summaries — even accurate extractions score low.
To get true verification rate, replace string-sim with embedding-similarity (TODO).

## 5. Quality Scores (Tool 4)

- **Total rules scored**: 3,826

### Quality grade distribution
| Grade | Range | Count | % |
|---|---|---:|---:|
| A (0.8-1.0) | 0.8-1.0 | 182 | 4.8% |
| B (0.6-0.8) | 0.6-0.8 | 863 | 22.6% |
| C (0.4-0.6) | 0.4-0.6 | 1410 | 36.9% |
| D (0.2-0.4) | 0.2-0.4 | 1316 | 34.4% |
| F (<0.2) | <0.2 | 55 | 1.4% |

### Top 20 A-grade rules (highest confidence)
| score | books | book | trigger |
|---:|---:|---|---|
| 1.00 | 4 | BPHS2 | Mercury in the 8th house |
| 1.00 | 4 | BPHS2 | Jupiter in the 8th house |
| 0.95 | 4 | Phaladeepika | Venus in the 7th house |
| 0.90 | 4 | Hora_Sara | Moon in the 8th house |
| 0.90 | 4 | Hora_Sara | Mars in the 3rd house |
| 0.90 | 4 | Hora_Sara | Mars in the 6th house |
| 0.90 | 4 | Hora_Sara | Mars in the 8th house |
| 0.90 | 4 | Hora_Sara | Mercury in the 8th house |
| 0.90 | 4 | Hora_Sara | Jupiter in the 8th house |
| 0.90 | 4 | Hora_Sara | Venus in the 7th house |
| 0.90 | 5 | Hora_Sara | Venus in the 8th house |
| 0.90 | 5 | Hora_Sara | Saturn in the 8th house |
| 0.90 | 4 | Prashna_Marga | Mars in the 3rd house |
| 0.90 | 4 | Prashna_Marga | Mars in the 8th house |
| 0.90 | 4 | Prashna_Marga | Venus in the 7th house |
| 0.90 | 5 | Prashna_Marga | Saturn in the 8th house |
| 0.85 | 2 | BPHS1 | Sun in 6th/8th/12th, 8th lord in 9th, 12th lord in ascendant |
| 0.85 | 2 | BPHS1 | Sun in 8th, 8th lord in 9th |
| 0.85 | 2 | BPHS1 | Ascendant lord in 8th, 8th lord with Sun |
| 0.85 | 2 | BPHS1 | Saturn in 9th from Moon, Sun with Rahu |

## 6. Honest Assessment

### What we KNOW

- Corpus has **8,239 items across 34 books** (after Phase 1.A+B+C)
- **8% of rules** semantically overlap across books (true confluence)
- **44% of yogas** were duplicates due to spelling — now consolidated
- **5% of rules score A-grade** (high confidence)
- **35% of rules score D-grade** (single-book, short, or weak)
- **<2% of rules** are clearly broken (junk, empty, hallucinated)

### What we DON'T know

- Whether the 95% non-A-grade rules are CORRECT or just hard-to-verify
- Whether single-book rules are real Jyotish or LLM hallucinations
- Whether the source citations point to where the rule actually exists
- Whether scholar disagreements are captured properly

### Honest TODOs

1. Replace string-similarity verifier with embedding-based one (much more accurate)
2. Run a Sanskrit/English Jyotish scholar over 100 random rules (ground truth)
3. Cross-validate against famous-chart predictions (Phase III)
4. Build authority-hierarchy reconciliation for disagreements
