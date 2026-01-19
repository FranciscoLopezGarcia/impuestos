import json
from pathlib import Path
from utils import  to_number

import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "outputs" / "raw"

RAW = RAW_DIR / "raw_monedas_2024.json"


def _find_dolar(lista):
    for item in lista:
        desc = (item.get("descripcion") or "").upper()
        if "DOLAR" in desc or "DÓLAR" in desc:
            return item
    return None

def normalize_bp_dolar(year_filter=None):

    data = json.loads(RAW.read_text(encoding="utf-8"))
    anio = data.get("anio")
    fuente = data.get("fuente", "ARCA")

    # Aplicar filtro de año si existe
    if year_filter and anio != year_filter:
        return []

    billete = _find_dolar(data.get("billetes", []))
    divisa = _find_dolar(data.get("divisas", []))

    out = []

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