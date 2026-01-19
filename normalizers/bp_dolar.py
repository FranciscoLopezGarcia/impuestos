import json
from pathlib import Path
from utils import to_number

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "outputs" / "raw"


def _find_dolar(lista):
    for item in lista:
        desc = (item.get("descripcion") or "").upper()
        if "DOLAR" in desc or "DÓLAR" in desc:
            return item
    return None


def normalize_bp_dolar(year_filter=None):
    out = []

    # Buscar todos los raw de monedas disponibles
    files = sorted(RAW_DIR.glob("raw_monedas_*.json"))

    for raw_file in files:
        try:
            data = json.loads(raw_file.read_text(encoding="utf-8"))
        except Exception:
            continue

        anio = data.get("anio")
        fuente = data.get("fuente", "ARCA")

        # Respetar filtro de año
        if year_filter and anio != year_filter:
            continue

        billete = _find_dolar(data.get("billetes", []))
        divisa = _find_dolar(data.get("divisas", []))

        if billete:
            out.append({
                "concepto": "BP_DOLAR_BILLETE_COMP_31_12",
                "impuesto": "BIENES_PERSONALES",
                "anio": anio,
                "valor_raw": billete.get("comprador"),
                "valor_num": to_number(billete.get("comprador")),
                "unidad": "ARS",
                "fuente": fuente,
                "origen": "PDF_MONEDA_EXTRANJERA",
                "url": None,
            })
            out.append({
                "concepto": "BP_DOLAR_BILLETE_VEND_31_12",
                "impuesto": "BIENES_PERSONALES",
                "anio": anio,
                "valor_raw": billete.get("vendedor"),
                "valor_num": to_number(billete.get("vendedor")),
                "unidad": "ARS",
                "fuente": fuente,
                "origen": "PDF_MONEDA_EXTRANJERA",
                "url": None,
            })

        if divisa:
            out.append({
                "concepto": "BP_DOLAR_DIVISA_COMP_31_12",
                "impuesto": "BIENES_PERSONALES",
                "anio": anio,
                "valor_raw": divisa.get("comprador"),
                "valor_num": to_number(divisa.get("comprador")),
                "unidad": "ARS",
                "fuente": fuente,
                "origen": "PDF_MONEDA_EXTRANJERA",
                "url": None,
            })
            out.append({
                "concepto": "BP_DOLAR_DIVISA_VEND_31_12",
                "impuesto": "BIENES_PERSONALES",
                "anio": anio,
                "valor_raw": divisa.get("vendedor"),
                "valor_num": to_number(divisa.get("vendedor")),
                "unidad": "ARS",
                "fuente": fuente,
                "origen": "PDF_MONEDA_EXTRANJERA",
                "url": None,
            })

    return out
