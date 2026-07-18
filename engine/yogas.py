"""
engine/yogas.py — Compatibility shim for shadbala.py and other modules
that import classical dignitary constants.

These constants are the single source of truth for:
  - Exaltation/Debilitation signs per planet
  - Own signs per planet
  - Sign lords
  - The 12-sign ordered list
"""

from engine.constants import (
    SIGNS_TAMIL as SIGNS,
    SIGN_LORDS_TAMIL as SIGN_LORDS,
    EXALTATION_TAMIL as EXALTATION,
    DEBILITATION_TAMIL as DEBILITATION,
    OWN_SIGNS_TAMIL as OWN_SIGNS,
)


# ============================================================
# UNIFIED detect_all() — bridges engine/ + runtime/ yoga libraries
# ============================================================
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), "..", "runtime"))


def detect_all(chart):
    """Run all yoga detectors across engine/ + runtime/. Returns flat list.

    Sources:
      - engine/yogas_extended.py: 12 bhava yogas, parivartana, amala, vasumat, pushkala, mahabhagya
      - engine/yogas_nabhasa.py: rajju, nala, mala, sarpa-nabhasa, sankhya
      - runtime/comprehensive_yogas.py: 27 classical yogas (Mahapurusha, Lunar, Solar, Conjunction, Raja, Vipareeta, Wealth, Doshas, Nabhasa-base)
      - runtime/yoga_library_v2.py: 14+ extended yogas (Adhi, Saraswati, Lakshmi-full, Maha-Bhagya, Pravrajya, etc.)
    """
    yogas = []

    # Engine internal yogas
    try:
        from engine import yogas_extended as _ye
        yogas.extend(_ye.detect_12_bhava_yogas(chart) or [])
        yogas.extend(_ye.detect_parivartana_yogas(chart) or [])
        for fn_name in ["detect_amala_yoga", "detect_vasumat_yoga", "detect_pushkala_yoga", "detect_mahabhagya_yoga"]:
            fn = getattr(_ye, fn_name, None)
            if fn:
                try:
                    r = fn(chart) if "mahabhagya" not in fn_name else fn(chart, None)
                    if r: yogas.append(r)
                except Exception:
                    pass
    except Exception as e:
        pass

    try:
        from engine import yogas_nabhasa as _yn
        for fn_name in ["detect_rajju_yoga", "detect_nala_yoga", "detect_mala_yoga", "detect_sarpa_nabhasa_yoga"]:
            fn = getattr(_yn, fn_name, None)
            if fn:
                try:
                    r = fn(chart)
                    if r: yogas.append(r)
                except Exception:
                    pass
        try:
            yogas.extend(_yn.detect_sankhya_yogas(chart) or [])
        except Exception:
            pass
    except Exception:
        pass

    # Runtime/ unified yogas (50+ from comprehensive + library_v2)
    try:
        from comprehensive_yogas import detect_all_classical_yogas as _runtime_yogas
        yogas.extend(_runtime_yogas(chart))
    except Exception:
        pass

    try:
        from yoga_library_v2 import detect_extra_yogas as _runtime_extra
        yogas.extend(_runtime_extra(chart))
    except Exception:
        pass

    return yogas
