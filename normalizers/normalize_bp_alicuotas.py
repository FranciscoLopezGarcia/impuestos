import json
from pathlib import Path
from normalizers.utils import to_number

RAW = Path(__file__).resolve().parents[1] / "outputs" / "raw_bienes_alicuotas_2024.json"

def _extract_tramos_from_table(rows):
    """
    rows es lista de filas (cada fila = lista de celdas).
    Devuelve lista de dicts con desde/hasta/pagaran/aliquota/excedente.
    """
    tramos = []
    for r in rows:
        if not isinstance(r, list) or len(r) < 4:
            continue

        # buscamos filas tipo: [desde, hasta, pagaran, porcentaje, excedente]
        # en tu raw algunas filas tienen '-' y 'en adelante'
        if len(r) >= 5:
            desde, hasta, pagaran, porc, exced = r[0], r[1], r[2], r[3], r[4]
        else:
            continue

        # descartamos headers
        if "más de" in str(desde).lower() or "valor total" in str(desde).lower():
            continue

        # al menos debe tener porcentaje tipo "0,50%"
        if "%" not in str(porc):
            continue

        tramos.append({
            "desde": desde,
            "hasta": hasta,
            "pagaran": pagaran,
            "porcentaje": porc,
            "excedente_desde": exced,
        })
    return tramos

def normalize_bp_alicuotas():
    data = json.loads(RAW.read_text(encoding="utf-8"))
    anio = data.get("anio")
    tablas = data.get("tablas", [])
    if not tablas:
        return []

    # detectamos tablas "2024" por el primer hasta = 40.107.213,86
    def table_score(tab):
        rows = tab.get("rows", [])
        tramos = _extract_tramos_from_table(rows)
        if not tramos:
            return 0
        first_hasta = str(tramos[0].get("hasta", ""))
        return 10 if "40.107.213,86" in first_hasta else 1

    tablas_sorted = sorted(tablas, key=table_score, reverse=True)

    out = []

    # tabla general (la mejor puntuación)
    general = tablas_sorted[0]
    tramos_general = _extract_tramos_from_table(general.get("rows", []))

    for i, t in enumerate(tramos_general, start=1):
        out.append({
            "concepto": f"BP_ALICUOTA_GENERAL_TRAMO_{i}",
            "impuesto": "BIENES_PERSONALES",
            "anio": anio,
            "desde": to_number(t["desde"]),
            "hasta": to_number(t["hasta"]),
            "monto_fijo": to_number(t["pagaran"]),
            "porcentaje": to_number(t["porcentaje"]),
            "excedente_desde": to_number(t["excedente_desde"]),
            "unidad": "ARS/%",
            "fuente": data.get("fuente", "ARCA"),
            "origen": "HTML_ALICUOTAS",
            "url": None,
        })

    # “Contribuyentes cumplidores” (siempre que exista una 2da tabla con buen score)
    # En tu raw, tabla_index 1 parece "cumplidores 2024" por valores 0,25%, 0,50% etc. :contentReference[oaicite:11]{index=11}
    if len(tablas_sorted) > 1:
        cumpl = tablas_sorted[1]
        tramos_cumpl = _extract_tramos_from_table(cumpl.get("rows", []))
        for i, t in enumerate(tramos_cumpl, start=1):
            out.append({
                "concepto": f"BP_ALICUOTA_CUMPLIDORES_TRAMO_{i}",
                "impuesto": "BIENES_PERSONALES",
                "anio": anio,
                "desde": to_number(t["desde"]),
                "hasta": to_number(t["hasta"]),
                "monto_fijo": to_number(t["pagaran"]),
                "porcentaje": to_number(t["porcentaje"]),
                "excedente_desde": to_number(t["excedente_desde"]),
                "unidad": "ARS/%",
                "fuente": data.get("fuente", "ARCA"),
                "origen": "HTML_ALICUOTAS",
                "url": None,
            })

    return out
