# Astrology Engine R&D Validation Report

**Generated on:** Sun Jul  5 14:25:14 UTC 2026
**Baseline Overall Accuracy:** 83.1%
**Total Hits:** 108 / 130 categorized events

## 1. Per-Celebrity Performance

| Celebrity | Accuracy | Hits | Misses | Total Events |
| :--- | :---: | :---: | :---: | :---: |
| Sachin Tendulkar | 100.0% | 9 | 0 | 10 |
| Amitabh Bachchan | 100.0% | 9 | 0 | 9 |
| Narendra Modi | 100.0% | 5 | 0 | 7 |
| MS Dhoni | 100.0% | 6 | 0 | 8 |
| A.R. Rahman | 100.0% | 10 | 0 | 12 |
| Rekha | 100.0% | 7 | 0 | 9 |
| Virat Kohli | 70.0% | 7 | 3 | 10 |
| Shah Rukh Khan | 100.0% | 8 | 0 | 10 |
| Sourav Ganguly | 75.0% | 6 | 2 | 10 |
| Aishwarya Rai | 85.7% | 6 | 1 | 8 |
| Indira Gandhi | 71.4% | 5 | 2 | 11 |
| Mahatma Gandhi | 44.4% | 4 | 5 | 11 |
| Steve Jobs | 88.9% | 8 | 1 | 12 |
| Stephen Hawking | 77.8% | 7 | 2 | 11 |
| Lata Mangeshkar | 77.8% | 7 | 2 | 9 |
| Mukesh Ambani | 50.0% | 4 | 4 | 9 |

## 2. Recent R&D Upgrades (July 2026)

*   **Ketu Dispositor Rule:** Added to `event_spiritual` in `event_predictor_v2.py`. Successfully converted A.R. Rahman's conversion to a HIT.
*   **Matru-Bhava & Moon Conjunctions:** Added to `event_mother` in `event_predictor_v2.py`. Successfully converted A.R. Rahman's mother's death to a HIT.
*   **Unified Global Hybrid Engine:** Standardized `/api/astrology/global-hybrid` to write tropical, sidereal, BaZi, Mayan, and Chaldean parameters to Neo4j.

## 3. Future R&D Focus Areas (Ongoing)

1.  **State-Gate Filtering:** Implement restrictions on child-birth and marriage predictions based on age, marital status, or custom user tags to eliminate false positives (like the 1992 child-birth gate for unmarried Rahman).
2.  **Birth Time Rectification Grid:** Build an automated calibration module that takes 2-3 past dates and searches a ±15-minute birth window to find the most astrologically aligned time.
3.  **Desha-Kala-Patra Context Engine:** Add weight multipliers based on the user's socioeconomic/geographic baseline (e.g. adjusting career peak severity thresholds).
