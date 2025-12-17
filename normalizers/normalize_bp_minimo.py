from pathlib import Path
import json
from normalizers.utils import to_number

RAW = Path(__file__).resolve().parents[1] / "outputs" / "raw_bp_determinativa_2024.json"

def normalize_bp_minimo():
    data = json.loads(RAW.read_text(encoding="utf-8"))

    out = []
    for item in data.get("thresholds", []):
        out.append({
            "concepto": "BP_MINIMO_NO_IMPONIBLE",
            "impuesto": "BIENES_PERSONALES",
            "anio": item.get("year"),
            "valor_raw": item.get("amount_raw"),
            "valor_num": to_number(item.get("amount_raw")),
            "unidad": "ARS",
            "fuente": "ARCA",
            "origen": "HTML_DETERMINATIVA",
            "url": None,
        })

    return out
