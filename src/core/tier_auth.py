from src.core.config import get_api_keys, get_cors_origins
import copy

def cors_allowed_origins() -> list:
    return get_cors_origins()

def resolve_user_tier(data) -> str:
    """Tier from validated api_key only. Ignores client user_tier."""
    api_key = getattr(data, "api_key", None)
    if not api_key:
        return "free"
    registry = get_api_keys()
    return registry.get(api_key, "free")

def gate_jathagam_payload(res: dict, tier: str) -> dict:
    if tier in ("professional", "enterprise"):
        # Unlocked!
        return res
    
    gated = copy.deepcopy(res)
    
    if tier == "free":
        # Free Tier Restrictions:
        # 1. Truncate dasha schedule to 1 year max
        if "dasha_schedule" in gated and isinstance(gated["dasha_schedule"], list):
            import datetime as dt
            now = dt.date.today()
            one_year_later = now + dt.timedelta(days=365)
            filtered_schedule = []
            for item in gated["dasha_schedule"]:
                try:
                    end_str = item.get("end")
                    if end_str:
                        end_dt = dt.datetime.strptime(end_str.split(" ")[0], "%Y-%m-%d").date()
                        if end_dt <= one_year_later:
                            filtered_schedule.append(item)
                        else:
                            item_copy = copy.deepcopy(item)
                            item_copy["end"] = "LOCKED - Upgrade to Pro"
                            item_copy["subperiods"] = []
                            filtered_schedule.append(item_copy)
                            break
                except Exception:
                    filtered_schedule.append(item)
            gated["dasha_schedule"] = filtered_schedule[:3] 
        
        # 2. Hide advanced analytical structures
        gated["kp_analysis"] = {
            "status": "locked",
            "message": "Krishnamurti Paddhati (KP) cuspal sub-lords analysis is available only for Pro members."
        }
        gated["shadbala"] = {
            "status": "locked",
            "message": "Shadbala detailed strength vectors are locked. Upgrade to Pro."
        }
        gated["ashtakavarga"] = {
            "status": "locked",
            "message": "Bhinnashtakavarga & Sarvashtakavarga point grids are locked. Upgrade to Pro."
        }
        gated["advanced_reading_html"] = (
            "<div class='locked-preview' style='padding: 20px; text-align: center; border: 1px dashed rgba(255,255,255,0.15); border-radius: 8px; background: rgba(255,255,255,0.02);'>"
            "<h3 style='color: #00e5ff; margin-bottom: 10px;'>Premium Detailed Scripture Analysis Locked</h3>"
            "<p style='color: #a0aec0; font-size: 14px;'>Upgrade your account to Professional Pro to unlock 15,581 classical rules and 12-page PDF downloads!</p>"
            "</div>"
        )
        
        # 3. Limit house predictions and yogas
        if "house_predictions" in gated and isinstance(gated["house_predictions"], list):
            kept = [
                r for r in gated["house_predictions"]
                if isinstance(r, dict) and r.get("house") is not None and int(r["house"]) <= 3
            ]
            for h in range(4, 13):
                kept.append({
                    "planet": "",
                    "house": h,
                    "status": "locked",
                    "message": f"House {h} detailed predictions are locked. Upgrade to Pro to read.",
                })
            gated["house_predictions"] = kept

        if "detected_yogas" in gated and isinstance(gated["detected_yogas"], list):
            gated["detected_yogas"] = gated["detected_yogas"][:2]
            
    elif tier == "premium":
        gated["kp_analysis"] = {
            "status": "locked",
            "message": "KP Sub-lord charts are locked. Upgrade to Professional Pro."
        }
        gated["ashtakavarga"] = {
            "status": "locked",
            "message": "Ashtakavarga grids require Professional Pro."
        }
        gated["advanced_reading_html"] = (
            "<div class='locked-preview' style='padding: 20px; text-align: center; border: 1px dashed rgba(255,255,255,0.15); border-radius: 8px; background: rgba(255,255,255,0.02);'>"
            "<h3 style='color: #00e5ff; margin-bottom: 10px;'>Professional Scripture Badges & PDF Download Locked</h3>"
            "<p style='color: #a0aec0; font-size: 14px;'>Upgrade to Professional Pro to download complete report and see verbatim citations.</p>"
            "</div>"
        )
        
    return gated
