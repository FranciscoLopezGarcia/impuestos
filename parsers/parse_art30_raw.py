import json
import re
from pathlib import Path
import pdfplumber

BASE_DIR = Path(__file__).resolve().parents[1]
PDF = BASE_DIR / "outputs" / "pdfs" / "Deducciones-personales-art-30-liq-anual-2025.pdf"
OUT = BASE_DIR / "outputs" / "raw_art30_2025.json"

def norm_key(label: str) -> str:
    s = label.lower().strip()

    if "ganancias no imponibles" in s:
        return "ganancia_no_imponible"
    if "cónyuge" in s or "conyuge" in s:
        return "cargas_familia_conyuge"
    if "hijo incapacitado" in s:
        return "cargas_familia_hijo_incapacitado"
    if re.search(r"\b2\.\s*hijo\b", s) or s.startswith("2. hijo"):
        return "cargas_familia_hijo"

    # deducciones especiales
    if "deducción especial" in s or "deduccion especial" in s:
        if "apartado 1" in s and "nuevos" in s:
            return "deduccion_especial_ap1_nuevos"
        if "apartado 1" in s:
            return "deduccion_especial_ap1"
        if "apartado 2" in s:
            return "deduccion_especial_ap2"
        return "deduccion_especial"

    return ""

def first_money(cell: str) -> str | None:
    if not cell:
        return None
    # captura formatos tipo 4.507.505,52 o 15.776.269,32
    m = re.search(r"(\d{1,3}(?:\.\d{3})*,\d{2})", cell)
    return m.group(1) if m else None

def parse():
    data = {
        "anio": 2025,
        "fuente": "ARCA",
        "items": {}
    }

    with pdfplumber.open(PDF) as pdf:
        page = pdf.pages[0]
        tables = page.extract_tables() or []

        if not tables:
            raise RuntimeError("No se detectaron tablas en el PDF (raro).")

        # En este PDF hay 1 tabla buena
        table = tables[0]

        for row in table:
            if not row or len(row) < 2:
                continue

            label = (row[0] or "").strip()
            value = (row[1] or "").strip()

            # saltar header
            if "CONCEPTO" in label.upper():
                continue

            key = norm_key(label)
            money = first_money(value)

            # Solo guardar si encontramos clave + monto
            if key and money:
                data["items"][key] = money

    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"OK -> {OUT}")

if __name__ == "__main__":
    parse()
