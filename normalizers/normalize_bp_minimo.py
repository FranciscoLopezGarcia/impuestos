import json
from pathlib import Path
from codigo.normalizers.utils import to_number
from codigo.paths import OUTPUTS_DIR

RAW = OUTPUTS_DIR / "raw_bp_determinativa.json"



def normalize_bp_minimo():
    data = json.loads(RAW.read_text(encoding="utf-8"))
    thresholds = data.get("thresholds", [])
    if not thresholds:
        return []

    latest = max(thresholds, key=lambda x: x.get("year") or 0)

    return [{
        "concepto": "BP_MINIMO_NO_IMPONIBLE",
        "impuesto": "BIENES_PERSONALES",
        "anio": latest.get("year"),
        "valor_raw": latest.get("amount_raw"),
        "valor_num": to_number(latest.get("amount_raw")),
        "unidad": "ARS",
        "fuente": "ARCA",
        "origen": "HTML_DETERMINATIVA",
        "url": data.get("source"),
    }]
