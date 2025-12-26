import json
from pathlib import Path
from codigo.normalizers.utils import to_number

from codigo.paths import OUTPUTS_DIR

RAW = OUTPUTS_DIR / "raw_art30_2024.json"



def normalize_ganancias_deducciones():
    data = json.loads(RAW.read_text(encoding="utf-8"))

    anio = data.get("anio") or data.get("year")
    url = data.get("source") or data.get("url") or None  # si tu raw no trae link, queda None
    items = data.get("items", {})

    if not isinstance(items, dict):
        raise RuntimeError("ART30: se esperaba items como dict")

    out = []
    for k, v in items.items():
        out.append({
            "concepto": f"GAN_DED_{k.upper()}",
            "impuesto": "GANANCIAS",
            "anio": anio,
            "valor_raw": v,
            "valor_num": to_number(v),
            "unidad": "ARS",
            "fuente": data.get("fuente", "ARCA"),
            "origen": "PDF_ART_30",
            "url": url,
        })

    return out
