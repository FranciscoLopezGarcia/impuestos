import json
from pathlib import Path
from utils import to_number

RAW = Path("../outputs/raw_escalas_2025.json")

def normalize_ganancias_escalas():
    data = json.loads(RAW.read_text(encoding="utf-8"))

    # tu raw es LISTA directa
    if isinstance(data, list):
        tramos = data
        anio = None
        url = None
        fuente = "ARCA"
    else:
        tramos = data.get("tramos", [])
        anio = data.get("anio") or data.get("year")
        url = data.get("source") or data.get("url")
        fuente = data.get("fuente", "ARCA")

    out = []
    for i, t in enumerate(tramos, start=1):
        out.append({
            "concepto": f"GAN_ESCALA_TRAMO_{i}",
            "impuesto": "GANANCIAS",
            "anio": anio,
            "desde": to_number(t.get("desde")),
            "hasta": to_number(t.get("hasta")),
            "monto_fijo": to_number(t.get("monto_fijo")),
            "porcentaje": to_number(t.get("porcentaje")),
            "excedente_desde": to_number(t.get("excedente_desde")),
            "unidad": "ARS/%",
            "fuente": fuente,
            "origen": "PDF_ART_94",
            "url": url,
        })

    return out
