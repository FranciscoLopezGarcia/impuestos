import json
from pathlib import Path
from codigo.normalizers.utils import to_number, pick_year

YEAR_INPUT = 2025
RAW = Path("../outputs/raw_bp_determinativa.json")

def normalize_bp():
    data = json.loads(RAW.read_text(encoding="utf-8"))
    item = pick_year(data["thresholds"], YEAR_INPUT)

    if not item:
        return []

    return [{
        "concepto": "BP_MINIMO_NO_IMPONIBLE",
        "impuesto": "BIENES_PERSONALES",
        "anio": item["year"],
        "valor_raw": item["amount_raw"],
        "valor_num": to_number(item["amount_raw"]),
        "unidad": "ARS",
        "fuente": "ARCA",
        "origen": "HTML_DETERMINATIVA",
        "url": data["source"]
    }]
