# Full Event Catalog — Classical Jyotish & This Engine

**Audience:** Product, QA, clients  
**Related:** [ENGINE_PURPOSE_AND_ACTOR_EVENTS.md](./ENGINE_PURPOSE_AND_ACTOR_EVENTS.md)  
**Master list:** [ATRO_FULL_CATEGORY_LIST.md](../ATRO_FULL_CATEGORY_LIST.md) (~402 aspirational categories)

| Layer | Count |
|-------|------:|
| Imperative event_* in event_predictor_v2.py | **190** functions / **189** category slugs |
| Catalog SSOT (category_catalog.py) | **314** patterns total |
| Declarative-only (auto-compiled) | **~124** |
| English PDF domain pages rendered | **18** of 23 spec sections |
| Scorer ground-truth keys | **14** (CATEGORY_KEYWORDS) |

**Coverage:** ~314 / ~402 classical areas have an engine hook (~78%); movie_release / ilm_outcome still **missing**.

**Declarative slugs** (saham_kalatra, nadi_conjunction, d45_total_life_sub, …): see 
untime/category_catalog.py — full alphabetical list in repo root master doc.

------

## Part 1 � Classical life areas (what Jyotish can address)

| Area | Examples (English) | Tamil theme |
|------|-------------------|-------------|
| **Self** | Personality, body, accidents, charisma, reinvention | ?????, ???? |
| **Parents** | Father/mother health, death, relationship | ?????, ???? |
| **Siblings** | Birth, marriage, death of siblings | ??????? |
| **Education** | School, degree, exams, foreign study | ????? |
| **Marriage** | Timing, spouse, love vs arranged, divorce, affair | ???????? |
| **Children** | Birth, pregnancy, adoption, grandchildren | ?????? |
| **Career** | Job, promotion, business, fame, acting, tech, law | ?????? |
| **Wealth** | Gains, loss, loan, tax, crypto, lottery, inheritance | ??????? |
| **Health** | Illness, surgery, dental, eye, diet | ?????????? |
| **Property** | House, land, vehicle, renovation, dispute | ?????? |
| **Travel** | Foreign, visa, relocation, pilgrimage | ????? |
| **Legal** | Court win/loss, jail, tax dispute | ?????? |
| **Spirituality** | Guru, diksha, mantra, moksha, temple | ???????? |
| **Social** | Friends, enemies, fame, honor, political office | ?????? |
| **Death** | Self, spouse, relatives (timing tendency � not exact date) | ????? |
| **Timing** | Dasha, transit, Sade Sati, eclipse, Saturn/Jupiter return | ????? |

---

## Part 2 � Engine categories (`event_predictor_v2`) � all 189

**Status:** **Implemented** in production scorer path (unless noted).  
**Missing for actors:** `movie_release`, `film_outcome` � use `career` / `acting` / `fame_peak` / `fame_loss` today.

### Self & health
`birth_circumstance`, `personality_shift`, `charisma`, `self_accident`, `health_self`, `major_surgery`, `dental`, `eye_issue`, `hearing_issue`, `hand_injury`, `voice_issue`, `diet_change`, `death_self`

### Parents & extended family
`father`, `mother`, `father_in_law`, `mother_in_law`, `maternal_uncle`, `paternal_uncle`, `elder_sibling`, `elder_sibling_marriage`, `elder_sibling_death`, `siblings`, `sibling_marriage`, `sibling_death`, `grandchildren`, `grandchild_marriage`, `great_grandparent`, `cousin`, `uncle_aunt`, `step_family`, `in_law_event`, `loved_one_death`, `distant_relative_death`, `adoption`

### Marriage & relationships
`marriage`, `marriage_arranged`, `marriage_love`, `second_marriage`, `engagement`, `engagement_break`, `divorce`, `widowhood`, `widowhood_remarriage`, `relationship_break`, `romance`, `first_love`, `affair`, `spouse_health`, `partnership`, `partnership_break`, `partner_betrayal`, `partner_death`

### Children
`children`, `pregnancy`

### Education
`education`

### Career (incl. entertainment)
`career`, `first_job`, `job_change`, `profession_switch`, `promotion`, `promotion_executive`, `business`, `business_expansion`, `business_closure`, `founder_role`, `ceo_role`, `board_role`, `consultant`, `retirement`, `workplace_conflict`, `corporate_scandal`, `fame_peak`, `fame_loss`, `acting`, `singing_career`, `dancing`, `voice_career`, `writing_career`, `sports_milestone`, `tech_career`, `finance_career`, `law_career`, `medical_career`, `teaching`, `research`, `engineering`, `civil_service`, `military`, `judicial`, `government_position`, `diplomatic`, `political_office`, `brand_deal`, `sponsorship`, `subscriber_milestone`, `publication`, `award_nomination`, `honor`

### Wealth & assets
`wealth`, `wealth_loss`, `income_breakthrough`, `salary_raise`, `salary_cut`, `bonus`, `speculation_gain`, `speculation_loss`, `lottery_win`, `lottery_loss`, `stock_crash`, `crypto_gain`, `crypto_loss`, `loan_approval`, `loan_default`, `debt_freedom`, `tax_dispute`, `tax_refund`, `inheritance`, `inheritance_land`, `ancestral_inheritance`, `insurance_claim`, `fortune_loss`, `property`, `property_loss`, `property_dispute`, `land_acquisition`, `plot_sale`, `construction`, `renovation`, `mortgage`, `vehicle`, `franchise`, `patent`, `royalty`

### Travel & legal
`travel`, `relocation`, `visa`, `legal_dispute`, `lawsuit_won`, `lawsuit_lost`, `jail`, `neighbor_dispute`, `landlord_dispute`, `tenant_event`

### Spirituality
`spirituality`, `pilgrimage`, `temple_visit`, `temple_donation`, `guru_initiation`, `diksha`, `mantra_initiation`, `mantra_siddhi`, `chant_completion`, `yagna`, `meditation`, `kundalini`, `devotion`, `religious_conversion`, `renunciation`, `monastic`, `book_dharma`, `past_life`, `prophetic_dream`, `oracle`, `oracle_consult`, `psychic_experience`, `moksha`, `divine_grace`, `divine_call`, `blessing`, `karma_purification`, `curse_lifted`, `atonement`, `astral_travel`, `synchronicity`, `prophecy`, `creative_breakthrough`

### Pets & misc social
`pet_acquisition`, `pet_death`, `friend_gain`, `friend_loss`, `betrayal`, `charity`, `co_worker`, `servant_event`

### Astro timing signals
`eclipse_impact`, `saturn_return`, `jupiter_return`

### Saham / advanced (partial labels)
Patterns may emit corpus-specific slugs (e.g. `saham_kalatra`, `nadi_conjunction`) � map to marriage/career in Tamil reports via `tamil_translations.CATEGORY_TA`.

---

## Part 3 � English PDF domains (`generate_report.py`)

18 domain chapters (each holds many sub-predictions):

1. Self & personality  
2. Parents  
3. Siblings  
4. Education  
5. Marriage  
6. Children  
7. Career & profession  
8. Wealth  
9. Health  
10. Travel & foreign  
11. Property & assets  
12. Social status, fame, power  
13. Relationships & enemies  
14. Spirituality  
15. Talents & skills  
16. Past lives & karma  
17. Annual predictions (Varshaphala)  
18. Specific event probabilities  

Plus: yogas, dasha chapters, life-event bands from `event_predictor_v2`.

---

## Part 4 � Not predictable / ethics (do not sell)

| Topic | Why |
|-------|-----|
| Exact death date/time | Ethics + uncertainty |
| Medical diagnosis | Not a doctor |
| Guaranteed lottery win | No guarantee |
| Exact marriage hour | Only bands |
| 100% certain future | Dasha permits/denies, not fate |

---

## Part 5 � Planned / missing

| Event | Status |
|-------|--------|
| `movie_release` | **Not in engine** � use `career` / `acting` |
| `film_outcome` (hit/flop) | **Partial** � valence from text only |
| Family ripple (baby born ? native 5H+7H+11H bundle) | **Not implemented** |
| Linked spouse/child charts | **Not implemented** |

---

## Regenerate category list

```bash
python F:\astro\scratch\_extract_categories.py
```
