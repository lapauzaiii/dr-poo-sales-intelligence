"""Conservative equipment identification for authorized permit records.

A lift station is not inferred from a septic classification or a dosing tank.
"""
import re

def classify_equipment(record):
    text = " ".join(str(record.get(k) or "") for k in (
        "system_type", "equipment_type", "description", "notes",
        "atu_make_model", "pump_station_type")).lower()
    if re.search(r"\b(lift station|sewage pumping station|wastewater pump station)\b", text):
        return {"type": "lift_station", "confidence": "explicit_text", "review_required": True}
    if record.get("atu_make_model") or re.search(
        r"\b(aerobic treatment unit|atu|performance.based treatment system|pbts)\b", text
    ):
        return {"type": "advanced_treatment_unit", "confidence": "explicit_text", "review_required": True}
    return {"type": "unknown", "confidence": "none", "review_required": False}
